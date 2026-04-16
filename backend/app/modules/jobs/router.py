from fastapi import APIRouter
from .service import create_user

router = APIRouter()

@router.post("/")
def register_user():
    return create_user()