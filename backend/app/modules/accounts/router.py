from uuid import UUID
from fastapi import APIRouter
from fastapi import UploadFile, File

from .schema import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
    ResumeCreateRequest,
    ResumeResponse
)

from .service import (
    create_user,
    get_user_profile,
    update_user_profile,
    add_resume
    parse_profile_data
    upload_resume_to_storage
)

router = APIRouter()


# Create user profile (after Supabase signup)
@router.post("/profile", response_model=UserResponse)
def register_user(payload: UserCreateRequest) -> UserResponse:
    return create_user(payload)


# Get profile
@router.get("/profile/{user_id}/parse")
def parse_profile(user_id: UUID):
    return parse_profile_data(user_id)


# Update profile
@router.patch("/profile/{user_id}", response_model=UserResponse)
def update_profile(user_id: UUID, payload: UserUpdateRequest) -> UserResponse:
    return update_user_profile(user_id, payload)


# Add resume
@router.post("/profile/{user_id}/resume", response_model=ResumeResponse)
def upload_resume(user_id: UUID, payload: ResumeCreateRequest) -> ResumeResponse:
    return add_resume(user_id, payload)

@router.post("/profile/{user_id}/resume/upload")
def upload_resume_file(user_id: UUID, file: UploadFile = File(...)):
    return upload_resume_to_storage(user_id, file)
