from app.core.supabase_client import get_supabase_service_client
from app.core.supabase_client import get_supabase_anon_client
from fastapi import UploadFile
from uuid import UUID
import uuid


def _anon_supabase():
    """Return the anon/publishable client; lazy so importing this module does not touch env."""
    return get_supabase_anon_client()


def _service_supabase():
    return get_supabase_service_client()


def _lookup_user_email(user_id: UUID) -> str | None:
    try:
        response = _service_supabase().auth.admin.get_user_by_id(str(user_id))
        user = getattr(response, "user", None)
        return getattr(user, "email", None) if user else None
    except Exception:
        return None


def _resolve_account_type(user_id: UUID) -> str | None:
    service = _service_supabase()
    user_key = str(user_id)
    employer = service.table("employers").select("id").eq("id", user_key).limit(1).execute()
    if employer.data:
        return "employer"
    seeker = service.table("job_seekers").select("id").eq("id", user_key).limit(1).execute()
    if seeker.data:
        return "job_seeker"
    return None


def _sync_job_seeker_skills(service, user_id: str, skill_names: list[str]) -> None:
    service.table("job_seeker_skills").delete().eq("job_seeker_id", user_id).execute()

    for raw_name in skill_names:
        name = raw_name.strip()
        if not name:
            continue

        existing = service.table("skills").select("id").eq("name", name).limit(1).execute()
        if existing.data:
            skill_id = existing.data[0]["id"]
        else:
            inserted = service.table("skills").insert({"name": name}).execute()
            if not inserted.data:
                continue
            skill_id = inserted.data[0]["id"]

        service.table("job_seeker_skills").insert(
            {"job_seeker_id": user_id, "skill_id": skill_id}
        ).execute()


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


def _provision_job_seeker_if_missing(user_id: UUID) -> bool:
    """
    Create a minimal job_seekers row when auth exists but profile was never inserted
    (e.g. partial registration). Skips users who only have an employers profile.
    """
    service = _service_supabase()
    user_key = str(user_id)

    employer = service.table("employers").select("id").eq("id", user_key).limit(1).execute()
    if employer.data:
        return False

    existing = service.table("job_seekers").select("id").eq("id", user_key).limit(1).execute()
    if existing.data:
        return True

    first_name = ""
    last_name = ""
    try:
        auth_response = service.auth.admin.get_user_by_id(user_key)
        user = getattr(auth_response, "user", None)
        meta = getattr(user, "user_metadata", None) or {}
        if isinstance(meta, dict):
            first_name = str(meta.get("first_name") or "")
            last_name = str(meta.get("last_name") or "")
    except Exception:
        pass

    data = {"id": user_key, "first_name": first_name, "last_name": last_name}
    try:
        service.table("job_seekers").insert(data).execute()
        return True
    except Exception as exc:
        message = str(exc).lower()
        if "duplicate" in message or "already exists" in message or "23505" in message:
            return True
        return False


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
            if not _provision_job_seeker_if_missing(user_id):
                return None
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
        email = profile.get("email") or _lookup_user_email(user_id)
        return {
            **profile,
            "first_name": profile.get("first_name") or "",
            "last_name": profile.get("last_name") or "",
            "email": email or "",
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

        # Only persist columns that exist on `public.job_seekers` in the current schema.
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

        service = _service_supabase()
        user_key = str(user_id)

        if update_data:
            service.table("job_seekers").update(update_data).eq("id", user_key).execute()

        if "skills" in raw and raw["skills"] is not None:
            _sync_job_seeker_skills(service, user_key, raw["skills"])

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

        response = _service_supabase().table("resumes").insert(data).execute()
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

def list_user_resumes(user_id: UUID):
    try:
        response = (
            _service_supabase()
            .table("resumes")
            .select("id, job_seeker_id, resume_name, file_url, is_primary, created_at")
            .eq("job_seeker_id", str(user_id))
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []
    except Exception as e:
        return {"error": f"Unable to list resumes: {str(e)}"}


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

def _auth_credentials(email: str, password: str) -> dict[str, str]:
    return {"email": email, "password": password}


def _sign_in(service, email: str, password: str):
    """Sign in via Supabase Auth using the service-role client (BFF pattern)."""
    credentials = _auth_credentials(email, password)
    try:
        return service.auth.sign_in_with_password(credentials)
    except TypeError:
        return service.auth.sign_in_with_password(email=email, password=password)


def _ensure_profile_row(service, user_id: str, payload) -> tuple[str, dict, dict | None]:
    """Insert employer/job_seeker profile if missing; return table name, row data, and optional error."""
    if payload.account_type == "employer":
        table_name = "employers"
        data = {
            "id": user_id,
            "company_name": payload.company_name or f"{payload.first_name} {payload.last_name}",
        }
    else:
        table_name = "job_seekers"
        data = {
            "id": user_id,
            "first_name": payload.first_name,
            "last_name": payload.last_name,
        }

    existing = service.table(table_name).select("id").eq("id", user_id).limit(1).execute()
    if existing.data:
        row = service.table(table_name).select("*").eq("id", user_id).limit(1).execute()
        return table_name, (row.data[0] if row.data else data), None

    try:
        response = service.table(table_name).insert(data).execute()
        profile = response.data[0] if response.data else data
        return table_name, profile, None
    except Exception as exc:
        message = str(exc).lower()
        if "duplicate" in message or "already exists" in message or "23505" in message:
            row = service.table(table_name).select("*").eq("id", user_id).limit(1).execute()
            return table_name, (row.data[0] if row.data else data), None
        return table_name, data, {"error": f"Profile creation failed: {exc}"}


def register_user(payload):
    """Registers a user with Supabase Auth and inserts a profile."""
    try:
        service = _service_supabase()

        try:
            auth_response = service.auth.admin.create_user(
                {
                    "email": payload.email,
                    "password": payload.password,
                    "email_confirm": True,
                }
            )
        except Exception as exc:
            message = str(exc).lower()
            if any(token in message for token in ("already", "registered", "exists", "duplicate")):
                return {"error": "An account with this email already exists."}
            return {"error": f"Auth registration failed: {exc}"}

        user = getattr(auth_response, "user", None)
        if not user:
            return {"error": "Supabase user creation failed"}

        user_id = getattr(user, "id", None)
        if not user_id:
            return {"error": "Supabase signup returned no user ID"}

        user_key = str(user_id)
        _, profile, profile_error = _ensure_profile_row(service, user_key, payload)
        if profile_error:
            try:
                service.auth.admin.delete_user(user_key)
            except Exception:
                pass
            return profile_error

        session_response = _sign_in(service, payload.email, payload.password)
        session = getattr(session_response, "session", None)
        access_token = getattr(session, "access_token", None) if session else None

        return {
            "access_token": access_token,
            "user": {
                "id": user_key,
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
        service = _service_supabase()
        response = _sign_in(service, payload.email, payload.password)

        access_token = getattr(response.session, "access_token", None)
        if not access_token:
            return {"error": "Invalid credentials"}

        user_id = UUID(str(response.user.id))
        account_type = _resolve_account_type(user_id)
        if not account_type:
            return {
                "error": (
                    "Account setup is incomplete. "
                    "Please register again or use the correct login page for your account type."
                )
            }

        return {
            "access_token": access_token,
            "user": {
                "id": str(response.user.id),
                "email": response.user.email,
                "account_type": account_type,
            },
        }

    except Exception as e:
        message = str(e).lower()
        if "invalid" in message and ("credential" in message or "login" in message):
            return {"error": "Invalid email or password."}
        return {"error": f"Login failed: {str(e)}"}
