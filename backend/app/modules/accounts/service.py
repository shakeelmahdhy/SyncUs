from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ---------------- USER (job_seekers) ---------------- #

def create_user(payload):
    data = {
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "email": payload.email
    }

    response = supabase.table("job_seekers").insert(data).execute()
    return response.data[0]


def get_user_profile(user_id):
    response = supabase.table("job_seekers").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None


def update_user_profile(user_id, payload):
    update_data = {}

    if payload.first_name:
        update_data["first_name"] = payload.first_name
    if payload.last_name:
        update_data["last_name"] = payload.last_name
    if payload.email:
        update_data["email"] = payload.email

    supabase.table("job_seekers").update(update_data).eq("id", user_id).execute()

    return get_user_profile(user_id)


# ---------------- RESUME ---------------- #

def add_resume(user_id, payload):
    data = {
        "job_seeker_id": user_id,
        "file_url": payload.file_url
    }

    response = supabase.table("resumes").insert(data).execute()
    return response.data[0]

def parse_profile_data(user_id):
    profile = get_user_profile(user_id)

    if not profile:
        return None

    return {
        "user_id": user_id,
        "message": "Profile parsing placeholder (future feature)",
        "profile": profile
    }
#--------Add Supabase auth register and login function--------    
def register_user(payload):
    auth_response = supabase.auth.sign_up({
        "email": payload.email,
        "password": payload.password
    })

    data = {
        "user_id": auth_response.user.id,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "email": payload.email
    }

    response = supabase.table("job_seekers").insert(data).execute()
    return response.data[0]


def login_user(payload):
    response = supabase.auth.sign_in_with_password({
        "email": payload.email,
        "password": payload.password
    })

    return {
        "access_token": response.session.access_token,
        "user": response.user
    }

def upload_resume_to_storage(user_id, file):
    file_path = f"{user_id}/{file.filename}"
    file_content = file.file.read()

    supabase.storage.from_("resumes").upload(
        file_path,
        file_content
    )

    public_url = supabase.storage.from_("resumes").get_public_url(file_path)

    data = {
        "job_seeker_id": str(user_id),
        "resume_name": file.filename,
        "file_url": public_url
    }

    response = supabase.table("resumes").insert(data).execute()
    return response.data[0]
