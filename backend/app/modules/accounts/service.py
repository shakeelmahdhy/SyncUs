from app.core.supabase_client import get_supabase_service_client
from app.core.supabase_client import get_supabase_anon_client
from fastapi import UploadFile
from uuid import UUID
import uuid


def _anon_supabase():
    """Return the anon/publishable client; lazy so importing this module does not touch env."""
    return get_supabase_anon_client()


# ---------------- USER (job_seekers) ---------------- #

def create_user(payload):
    """Create a new profile record in job_seekers."""
    try:
        user_uuid = str(payload.user_id)

        data = {
            "id": user_uuid,
            "first_name": payload.first_name,
            "last_name": payload.last_name,
            "phone": payload.phone,
        }

        response = get_supabase_service_client().table("job_seekers").insert(data).execute()
        return response.data[0]

    except Exception as e:
        return {"error": f"Profile creation failed: {str(e)}"}


def get_user_profile(user_id: UUID):
    """Fetch a user's profile from job_seekers."""
    try:
        service = get_supabase_service_client()
        response = (
            service
            .table("job_seekers")
            .select("*")
            .eq("id", str(user_id))
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        profile = response.data[0]
        skill_links = (
            service.table("job_seeker_skills")
            .select("skill_id")
            .eq("job_seeker_id", str(user_id))
            .execute()
        )
        skill_ids = [row["skill_id"] for row in (skill_links.data or []) if row.get("skill_id")]
        skills: list[str] = []
        if skill_ids:
            skill_rows = service.table("skills").select("name").in_("id", skill_ids).execute()
            skills = [row["name"] for row in (skill_rows.data or []) if row.get("name")]

        years = profile.get("years_of_experience")
        education = profile.get("education") or ""
        major = profile.get("major") or ""
        return {
            **profile,
            "first_name": profile.get("first_name") or "",
            "last_name": profile.get("last_name") or "",
            "email": profile.get("email"),
            "user_id": profile.get("id"),
            "phone": profile.get("phone") or "",
            "location": profile.get("location") or "",
            "title": major,
            "experience": "" if years is None else str(years),
            "bio": profile.get("bio") or "",
            "linkedin": profile.get("linkedin") or "",
            "portfolio": profile.get("portfolio") or "",
            "education": education,
            "company": profile.get("company") or "",
            "skills": skills,
            "major": major,
            "years_of_experience": years,
            "academic_units": profile.get("academic_units") or [],
        }

    except Exception as e:
        return {"error": f"Unable to fetch profile: {str(e)}"}


def update_user_profile(user_id: UUID, payload):
    """Update existing job_seeker profile."""
    try:
        raw = payload.model_dump(exclude_none=True)
        update_data = {}

        for key in ("first_name", "last_name", "phone", "education", "major", "academic_units"):
            if key in raw:
                update_data[key] = raw[key]

        if "title" in raw and "major" not in update_data:
            update_data["major"] = raw["title"]

        if "experience" in raw and "years_of_experience" not in raw:
            digits = "".join(ch for ch in str(raw["experience"]) if ch.isdigit())
            if digits:
                update_data["years_of_experience"] = int(digits)
        elif "years_of_experience" in raw:
            update_data["years_of_experience"] = raw["years_of_experience"]

        if update_data:
            get_supabase_service_client().table("job_seekers").update(update_data).eq("id", str(user_id)).execute()
        return get_user_profile(user_id)

    except Exception as e:
        return {"error": f"Update failed: {str(e)}"}


# ---------------- RESUME ---------------- #

def add_resume(user_id: UUID, payload):
    """Add an existing resume record by URL."""
    try:
        data = {
            "job_seeker_id": str(user_id),
            "resume_name": payload.resume_name,
            "file_url": payload.file_url,
        }

        response = _anon_supabase().table("resumes").insert(data).execute()
        return response.data[0]

    except Exception as e:
        return {"error": f"Resume insert failed: {str(e)}"}


def upload_resume_to_storage(user_id: UUID, file: UploadFile):
    """Upload resume file to Supabase Storage and register metadata."""
    service = get_supabase_service_client()

    try:
        unique_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = f"{user_id}/{unique_name}"
        file_bytes = file.file.read()

        service.storage.from_("resumes").upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )

        public_url = service.storage.from_("resumes").get_public_url(file_path)

        data = {
            "job_seeker_id": str(user_id),
            "resume_name": file.filename,
            "file_url": public_url,
        }

        db_response = service.table("resumes").insert(data).execute()
        return db_response.data[0]

    except Exception as e:
        return {"error": f"Resume upload failed: {str(e)}"}


# ---------------- PROFILE DATA PARSING PLACEHOLDER ---------------- #

def parse_profile_data(user_id: UUID):
    """Placeholder for future NLP-based parsing/inference."""
    profile = get_user_profile(user_id)

    if not profile:
        return {"error": "User not found"}

    return {
        "user_id": str(user_id),
        "message": "Profile parsing placeholder (future NLP integration)",
        "profile": profile,
    }


# ---------------- AUTH ---------------- #

def register_user(payload):
    """Registers a user with Supabase Auth and inserts a profile."""
    try:
        sb = _anon_supabase()
        try:
            auth_response = sb.auth.sign_up(
                email=payload.email,
                password=payload.password
            )
        except TypeError:
            auth_response = sb.auth.sign_up({
                "email": payload.email,
                "password": payload.password
            })

        user = getattr(auth_response, "user", None)

        if not user:
            return {"error": "Supabase user creation failed"}

        user_id = getattr(user, "id", None)

        if not user_id:
            return {"error": "Supabase signup returned no user ID"}

        service = get_supabase_service_client()
        if payload.account_type == "employer":
            data = {
                "id": str(user_id),
                "company_name": payload.company_name or f"{payload.first_name} {payload.last_name}",
            }
            table_name = "employers"
        else:
            data = {
                "id": str(user_id),
                "first_name": payload.first_name,
                "last_name": payload.last_name,
            }
            table_name = "job_seekers"

        response = service.table(table_name).insert(data).execute()
        profile = response.data[0] if response.data else data
        session = getattr(auth_response, "session", None)

        return {
            "access_token": getattr(session, "access_token", None) if session else None,
            "user": {
                "id": str(user_id),
                "email": payload.email,
                "account_type": payload.account_type,
            },
            "profile": profile,
        }

    except Exception as e:
        return {"error": f"Auth registration failed: {str(e)}"}


def login_user(payload):
    """Authenticates a user and retrieves a valid access token."""
    try:
        sb = _anon_supabase()
        try:
            response = sb.auth.sign_in_with_password(
                email=payload.email,
                password=payload.password
            )
        except TypeError:
            response = sb.auth.sign_in_with_password({
                "email": payload.email,
                "password": payload.password
            })

        access_token = getattr(response.session, "access_token", None)

        if not access_token:
            return {"error": "Invalid credentials"}

        return {
            "access_token": access_token,
            "user": {
                "id": str(response.user.id),
                "email": response.user.email,
            },
        }

    except Exception as e:
        return {"error": f"Login failed: {str(e)}"}
