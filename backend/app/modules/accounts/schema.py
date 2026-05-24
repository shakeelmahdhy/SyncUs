from app.core.supabase_client import get_supabase_anon_client
from app.core.supabase_client import get_supabase_service_client
from fastapi import UploadFile
import uuid

supabase = get_supabase_anon_client()


def _to_str_id(user_id) -> str:
    return str(user_id)


# ---------------- USER / PROFILE ---------------- #

def create_user(payload):
    """Create a new manual job_seeker profile."""
    try:
        user_uuid = _to_str_id(payload.user_id)
        service_supabase = get_supabase_service_client()

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
        }

        response = service_supabase.table("job_seekers").insert(data).execute()

        if not response.data:
            return {"error": "Profile creation failed: no data returned"}

        return response.data[0]

    except Exception as e:
        return {"error": f"Profile creation failed: {str(e)}"}


def get_user_profile(user_id):
    """Fetch authenticated user's profile from job_seekers or employers."""
    try:
        user_uuid = _to_str_id(user_id)
        service_supabase = get_supabase_service_client()

        job_seeker_response = (
            service_supabase.table("job_seekers")
            .select("*")
            .eq("user_id", user_uuid)
            .execute()
        )

        if job_seeker_response.data:
            profile = job_seeker_response.data[0]
            profile["role"] = "job_seeker"
            return profile

        employer_response = (
            service_supabase.table("employers")
            .select("*")
            .eq("id", user_uuid)
            .execute()
        )

        if employer_response.data:
            employer = employer_response.data[0]

            return {
                "id": employer.get("id"),
                "user_id": employer.get("id"),
                "first_name": employer.get("first_name"),
                "last_name": employer.get("last_name"),
                "email": employer.get("email"),
                "phone": None,
                "location": None,
                "bio": employer.get("company_description"),
                "work_experience": employer.get("industry"),
                "skills": None,
                "preferred_working_mode": None,
                "preferred_location": None,
                "role": "employer",
                "company_name": employer.get("company_name"),
                "company_description": employer.get("company_description"),
                "industry": employer.get("industry"),
                "is_verified": employer.get("is_verified"),
            }

        return None

    except Exception as e:
        return {"error": f"Unable to fetch profile: {str(e)}"}


def update_user_profile(user_id, payload):
    """Update authenticated user's job_seeker or employer profile."""
    try:
        user_uuid = _to_str_id(user_id)
        service_supabase = get_supabase_service_client()

        update_data = {
            key: value
            for key, value in payload.model_dump(exclude_none=True).items()
        }

        if not update_data:
            return {"error": "No update data provided"}

        job_seeker_check = (
            service_supabase.table("job_seekers")
            .select("id")
            .eq("user_id", user_uuid)
            .execute()
        )

        if job_seeker_check.data:
            allowed_job_seeker_fields = {
                "first_name",
                "last_name",
                "phone",
                "location",
                "bio",
                "work_experience",
                "skills",
                "preferred_working_mode",
                "preferred_location",
            }

            job_seeker_update = {
                key: value
                for key, value in update_data.items()
                if key in allowed_job_seeker_fields
            }

            if not job_seeker_update:
                return {"error": "No valid job seeker update fields provided"}

            service_supabase.table("job_seekers").update(job_seeker_update).eq(
                "user_id", user_uuid
            ).execute()

            return get_user_profile(user_uuid)

        employer_check = (
            service_supabase.table("employers")
            .select("id")
            .eq("id", user_uuid)
            .execute()
        )

        if employer_check.data:
            allowed_employer_fields = {
                "first_name",
                "last_name",
                "company_name",
                "company_description",
                "industry",
            }

            employer_update = {
                key: value
                for key, value in update_data.items()
                if key in allowed_employer_fields
            }

            if not employer_update:
                return {"error": "No valid employer update fields provided"}

            service_supabase.table("employers").update(employer_update).eq(
                "id", user_uuid
            ).execute()

            return get_user_profile(user_uuid)

        return {"error": "User not found"}

    except Exception as e:
        return {"error": f"Update failed: {str(e)}"}


# ---------------- RESUME ---------------- #

def add_resume(user_id, payload):
    """Add an existing resume record by URL."""
    try:
        user_uuid = _to_str_id(user_id)
        service_supabase = get_supabase_service_client()

        data = {
            "job_seeker_id": user_uuid,
            "resume_name": payload.resume_name,
            "file_url": payload.file_url,
        }

        response = service_supabase.table("resumes").insert(data).execute()

        if not response.data:
            return {"error": "Resume insert failed: no data returned"}

        return response.data[0]

    except Exception as e:
        return {"error": f"Resume insert failed: {str(e)}"}


def upload_resume_to_storage(user_id, file: UploadFile):
    """Upload resume file to Supabase Storage and register metadata."""
    try:
        service_supabase = get_supabase_service_client()
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
    """Register a user with Supabase Auth and create auto-confirmed role-based profile."""
    try:
        service_supabase = get_supabase_service_client()

        auth_response = service_supabase.auth.admin.create_user({
            "email": payload.email,
            "password": payload.password,
            "email_confirm": True,
        })

        user = getattr(auth_response, "user", None)

        if not user:
            return {"error": "Supabase user creation failed"}

        user_id = getattr(user, "id", None)

        if not user_id:
            return {"error": "Supabase signup returned no user ID"}

        user_uuid = _to_str_id(user_id)

        if payload.role == "job_seeker":
            data = {
                "id": user_uuid,
                "user_id": user_uuid,
                "first_name": payload.first_name,
                "last_name": payload.last_name,
                "email": payload.email,
            }

            response = service_supabase.table("job_seekers").insert(data).execute()

        elif payload.role == "employer":
            if not payload.company_name:
                return {"error": "Company name is required for employer registration"}

            data = {
                "id": user_uuid,
                "email": payload.email,
                "first_name": payload.first_name,
                "last_name": payload.last_name,
                "company_name": payload.company_name,
                "company_description": payload.company_description,
                "industry": payload.industry,
                "is_verified": False,
            }

            response = service_supabase.table("employers").insert(data).execute()

        else:
            return {"error": "Invalid role"}

        if not response.data:
            return {"error": "Profile creation after registration failed"}

        result = response.data[0]
        result["role"] = payload.role

        return result

    except Exception as e:
        return {"error": f"Auth registration failed: {str(e)}"}


def login_user(payload):
    """Authenticate a user and retrieve a valid access token with role."""
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

        user_id = str(response.user.id)
        role = None

        service_supabase = get_supabase_service_client()

        job_seeker_response = (
            service_supabase.table("job_seekers")
            .select("id")
            .eq("user_id", user_id)
            .execute()
        )

        if job_seeker_response.data:
            role = "job_seeker"
        else:
            employer_response = (
                service_supabase.table("employers")
                .select("id")
                .eq("id", user_id)
                .execute()
            )

            if employer_response.data:
                role = "employer"

        return {
            "access_token": access_token,
            "user": {
                "id": user_id,
                "email": response.user.email,
                "role": role,
            },
        }

    except Exception as e:
        return {"error": f"Login failed: {str(e)}"}
