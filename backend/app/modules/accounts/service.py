from app.core.supabase_client import get_supabase_anon_client
from app.core.supabase_client import get_supabase_service_client
from fastapi import UploadFile
from uuid import UUID
import uuid

supabase = get_supabase_anon_client()


def _to_str_id(user_id) -> str:
    """Convert UUID/string user id to string for Supabase queries."""
    return str(user_id)


# ---------------- USER (job_seekers) ---------------- #

def create_user(payload):
    """Create a new profile record in job_seekers."""
    try:
        user_uuid = _to_str_id(payload.user_id)

        data = {
            "id": user_uuid,
            "user_id": user_uuid,
            "first_name": payload.first_name,
            "last_name": payload.last_name,
            "email": payload.email,
            "phone": payload.phone,
            "location": payload.location,
            "bio": payload.bio,
            "work_experience": payload.work_experience,
            "skills": payload.skills,
            "preferred_working_mode": payload.preferred_working_mode,
            "preferred_location": payload.preferred_location,
            "membership": payload.membership,
        }

        response = supabase.table("job_seekers").insert(data).execute()

        if not response.data:
            return {"error": "Profile creation failed: no data returned"}

        return response.data[0]

    except Exception as e:
        return {"error": f"Profile creation failed: {str(e)}"}


def get_user_profile(user_id):
    """Fetch a user's profile from job_seekers."""
    try:
        user_uuid = _to_str_id(user_id)

        response = (
            supabase.table("job_seekers")
            .select("*")
            .eq("id", user_uuid)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    except Exception as e:
        return {"error": f"Unable to fetch profile: {str(e)}"}


def update_user_profile(user_id, payload):
    """Update existing job_seeker profile."""
    try:
        user_uuid = _to_str_id(user_id)

        update_data = {
            key: value
            for key, value in payload.model_dump(exclude_none=True).items()
        }

        if not update_data:
            return {"error": "No update data provided"}

        supabase.table("job_seekers").update(update_data).eq("id", user_uuid).execute()

        return get_user_profile(user_uuid)

    except Exception as e:
        return {"error": f"Update failed: {str(e)}"}


# ---------------- RESUME ---------------- #

def add_resume(user_id, payload):
    """Add an existing resume record by URL."""
    try:
        user_uuid = _to_str_id(user_id)

        data = {
            "job_seeker_id": user_uuid,
            "resume_name": payload.resume_name,
            "file_url": payload.file_url,
        }

        response = supabase.table("resumes").insert(data).execute()

        if not response.data:
            return {"error": "Resume insert failed: no data returned"}

        return response.data[0]

    except Exception as e:
        return {"error": f"Resume insert failed: {str(e)}"}


def upload_resume_to_storage(user_id, file: UploadFile):
    """Upload resume file to Supabase Storage and register metadata."""
    service_supabase = get_supabase_service_client()

    try:
        user_uuid = _to_str_id(user_id)

        unique_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = f"{user_uuid}/{unique_name}"
        file_bytes = file.file.read()

        service_supabase.storage.from_("resumes").upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": file.content_type},
        )

        public_url = service_supabase.storage.from_("resumes").get_public_url(file_path)

        data = {
            "job_seeker_id": user_uuid,
            "resume_name": file.filename,
            "file_url": public_url,
        }

        db_response = service_supabase.table("resumes").insert(data).execute()

        if not db_response.data:
            return {"error": "Resume upload failed: no database record returned"}

        return db_response.data[0]

    except Exception as e:
        return {"error": f"Resume upload failed: {str(e)}"}


# ---------------- PROFILE DATA PARSING PLACEHOLDER ---------------- #

def parse_profile_data(user_id):
    """Placeholder for future NLP-based parsing/inference."""
    user_uuid = _to_str_id(user_id)

    profile = get_user_profile(user_uuid)

    if not profile:
        return {"error": "User not found"}

    if "error" in profile:
        return profile

    return {
        "user_id": user_uuid,
        "message": "Profile parsing placeholder (future NLP integration)",
        "profile": profile,
    }


# ---------------- AUTH ---------------- #

def register_user(payload):
    """Register a user with Supabase Auth and insert a profile."""
    try:
        try:
            auth_response = supabase.auth.sign_up(
                email=payload.email,
                password=payload.password,
            )
        except TypeError:
            auth_response = supabase.auth.sign_up({
                "email": payload.email,
                "password": payload.password,
            })

        user = getattr(auth_response, "user", None)

        if not user:
            return {"error": "Supabase user creation failed"}

        user_id = getattr(user, "id", None)

        if not user_id:
            return {"error": "Supabase signup returned no user ID"}

        user_uuid = _to_str_id(user_id)

        data = {
            "id": user_uuid,
            "user_id": user_uuid,
            "first_name": payload.first_name,
            "last_name": payload.last_name,
            "email": payload.email,
        }

        response = supabase.table("job_seekers").insert(data).execute()

        if not response.data:
            return {"error": "Profile creation after registration failed"}

        return response.data[0]

    except Exception as e:
        return {"error": f"Auth registration failed: {str(e)}"}


def login_user(payload):
    """Authenticate a user and retrieve a valid access token."""
    try:
        try:
            response = supabase.auth.sign_in_with_password(
                email=payload.email,
                password=payload.password,
            )
        except TypeError:
            response = supabase.auth.sign_in_with_password({
                "email": payload.email,
                "password": payload.password,
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
