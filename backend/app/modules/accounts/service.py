from app.core.supabase_client import get_supabase_anon_client
from app.core.supabase_client import get_supabase_service_client
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
        response = (
            _anon_supabase()
            .table("job_seekers")
            .select("*")
            .eq("id", str(user_id))
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    except Exception as e:
        return {"error": f"Unable to fetch profile: {str(e)}"}


def update_user_profile(user_id: UUID, payload):
    """Update existing job_seeker profile."""
    try:
        update_data = {
            key: value
            for key, value in payload.model_dump(exclude_none=True).items()
        }

        _anon_supabase().table("job_seekers").update(update_data).eq("id", str(user_id)).execute()
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
