from uuid import UUID
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.core.auth import CurrentUserIdDep

from .schema import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
    ResumeCreateRequest,
    ResumeResponse,
    RegisterRequest,
    LoginRequest,
)

from .service import (
    create_user,
    get_user_profile,
    update_user_profile,
    add_resume,
    parse_profile_data,
    upload_resume_to_storage,
    register_user,
    login_user,
)

router = APIRouter()

# ---------------- PROFILE MANAGEMENT ---------------- #

@router.post("/profile", response_model=UserResponse)
def create_profile(payload: UserCreateRequest) -> UserResponse:
    """
    Optional/manual profile creation.
    Normally profile creation is handled during /auth/register.
    """
    result = create_user(payload)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/profile/me", response_model=UserResponse)
def get_profile(current_user_id: CurrentUserIdDep) -> UserResponse:
    """Fetch authenticated user's profile."""

    result = get_user_profile(current_user_id)

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/profile/me/parse")
def parse_profile(current_user_id: CurrentUserIdDep):
    """Placeholder for future resume/profile parsing feature."""

    result = parse_profile_data(current_user_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.patch("/profile/me", response_model=UserResponse)
def update_profile(
    payload: UserUpdateRequest,
    current_user_id: CurrentUserIdDep,
) -> UserResponse:
    """Update authenticated user's profile."""

    result = update_user_profile(current_user_id, payload)

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# ---------------- RESUME MANAGEMENT ---------------- #

@router.post("/profile/me/resume", response_model=ResumeResponse)
def add_resume_record(
    payload: ResumeCreateRequest,
    current_user_id: CurrentUserIdDep,
) -> ResumeResponse:
    """Add resume record for authenticated user."""

    result = add_resume(current_user_id, payload)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/profile/me/resume/upload")
def upload_resume_file(
    current_user_id: CurrentUserIdDep,
    file: UploadFile = File(...),
):
    """Upload resume for authenticated user."""

    result = upload_resume_to_storage(current_user_id, file)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# ---------------- AUTHENTICATION ---------------- #

@router.post("/auth/register")
def register(payload: RegisterRequest):
    """
    Register a new user with Supabase Auth
    and automatically create a role-based profile.
    """
    result = register_user(payload)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/auth/login")
def login(payload: LoginRequest):
    """Authenticate a user and return a Supabase access token."""

    result = login_user(payload)

    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])

    return result
