from uuid import UUID
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.core.auth import CurrentUser, get_current_user

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
    (Deprecated/Optional)
    Profile creation is handled during /auth/register.
    Use this endpoint only if user_id is already created 
    and you need to manually insert a record.
    """
    result = create_user(payload)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/profile/me", response_model=UserResponse)
def get_profile(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Fetch authenticated user's profile."""
    
    result = get_user_profile(current_user.id)

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    return result


@router.get("/profile/me/parse")
def parse_profile(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Placeholder for future resume/profile parsing feature."""

    result = parse_profile_data(current_user.id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.patch("/profile/me", response_model=UserResponse)
def update_profile(
    payload: UserUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> UserResponse:
    """Update authenticated user's profile."""

    result = update_user_profile(current_user.id, payload)

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

# ---------------- RESUME MANAGEMENT ---------------- #

@router.post("/profile/me/resume", response_model=ResumeResponse)
def add_resume_record(
    payload: ResumeCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ResumeResponse:
    """Add resume record for authenticated user."""

    result = add_resume(current_user.id, payload)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/profile/me/resume/upload")
def upload_resume_file(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Upload resume for authenticated user."""

    result = upload_resume_to_storage(current_user.id, file)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# ---------------- AUTHENTICATION ---------------- #

@router.post("/auth/register")
def register(payload: RegisterRequest):
    """
    Register a new user with Supabase Auth 
    and automatically create a job_seeker profile.
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
