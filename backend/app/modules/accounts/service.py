from app.core.supabase_client import get_supabase_anon_client
from fastapi import UploadFile

supabase = get_supabase_anon_client()

# ---------------- USER (job_seekers) ---------------- #

def create_user(payload):
    try:
        data = {
            "first_name": payload.first_name,
            "last_name": payload.last_name,
            "email": payload.email,
        }
        response = supabase.table("job_seekers").insert(data).execute()
        return response.data[0]
    except Exception as e:
        return {"error": str(e)}


def get_user_profile(user_id):
    try:
        response = supabase.table("job_seekers").select("*").eq("id", str(user_id)).execute()
        if not response.data:
            return None
        return response.data[0]
    except Exception as e:
        return {"error": f"Unable to fetch profile: {str(e)}"}


def update_user_profile(user_id, payload):
    try:
        update_data = {
            key: value for key, value in payload.dict().items() if value is not None
        }
        supabase.table("job_seekers").update(update_data).eq("id", str(user_id)).execute()
        return get_user_profile(user_id)
    except Exception as e:
        return {"error": f"Update failed: {str(e)}"}


# ---------------- RESUME ---------------- #

def add_resume(user_id, payload):
    try:
        data = {
            "job_seeker_id": str(user_id),
            "file_url": payload.file_url,
        }
        response = supabase.table("resumes").insert(data).execute()
        return response.data[0]
    except Exception as e:
        return {"error": f"Resume insert failed: {str(e)}"}


def upload_resume_to_storage(user_id, file: UploadFile):
    try:
        file_path = f"{user_id}/{file.filename}"
        file_bytes = file.file.read()

        # Upload to Supabase Storage
        upload_response = supabase.storage.from_("resumes").upload(file_path, file_bytes)
        if hasattr(upload_response, "error") and upload_response.error:
            return {"error": upload_response.error.message}

        public_url = supabase.storage.from_("resumes").get_public_url(file_path)

        # Store metadata
        data = {
            "job_seeker_id": str(user_id),
            "resume_name": file.filename,
            "file_url": public_url,
        }

        db_response = supabase.table("resumes").insert(data).execute()
        return db_response.data[0]
    except Exception as e:
        return {"error": f"Resume upload failed: {str(e)}"}


# ---------------- PROFILE DATA PARSING (placeholder) ---------------- #

def parse_profile_data(user_id):
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
        # Try both possible calling conventions (version-safe)
        try:
            auth_response = supabase.auth.sign_up(email=payload.email, password=payload.password)
        except TypeError:
            auth_response = supabase.auth.sign_up({
                "email": payload.email,
                "password": payload.password
            })

        # Extract user ID safely
        user_id = getattr(auth_response.user, "id", None)
        if not user_id:
            return {"error": "Supabase user creation failed"}

        data = {
            "user_id": str(user_id),
            "first_name": payload.first_name,
            "last_name": payload.last_name,
            "email": payload.email,
        }

        response = supabase.table("job_seekers").insert(data).execute()
        return response.data[0]
    except Exception as e:
        return {"error": f"Auth registration failed: {str(e)}"}


def login_user(payload):
    """Authenticates a user and retrieves token if valid."""
    try:
        # Try both calling patterns for SDK compatibility
        try:
            response = supabase.auth.sign_in_with_password(email=payload.email, password=payload.password)
        except TypeError:
            response = supabase.auth.sign_in_with_password({
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

