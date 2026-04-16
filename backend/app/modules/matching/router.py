from fastapi import APIRouter
from .service import match_jobs_for_user

router = APIRouter()

@router.get("/{user_id}")
def get_matches(user_id: int):
    return match_jobs_for_user(user_id)