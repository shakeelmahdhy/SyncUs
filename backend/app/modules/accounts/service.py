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
