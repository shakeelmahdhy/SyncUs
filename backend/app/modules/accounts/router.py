from uuid import UUID
from fastapi import APIRouter, UploadFile, File, HTTPException

from .schema import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
    ResumeCreateRequest,
    ResumeResponse,
    ResumeListResponse,
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
    list_user_resumes,
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


@router.get("/profile/{user_id}", response_model=UserResponse)
def get_profile(user_id: UUID):
    """Fetch an existing profile by user_id."""
    result = get_user_profile(user_id)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.get("/profile/{user_id}/parse")
def parse_profile(user_id: UUID):
    """Placeholder for future resume/profile parsing feature."""
    result = parse_profile_data(user_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.patch("/profile/{user_id}", response_model=UserResponse)
def update_profile(user_id: UUID, payload: UserUpdateRequest) -> UserResponse:
    """Update personal information for a user profile."""
    result = update_user_profile(user_id, payload)
    if not result or "error" in result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


# ---------------- RESUME MANAGEMENT ---------------- #

@router.get("/profile/{user_id}/resumes", response_model=ResumeListResponse)
def get_resumes(user_id: UUID) -> ResumeListResponse:
    result = list_user_resumes(user_id)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    items = [ResumeResponse(**row) for row in result]
    return ResumeListResponse(items=items, total=len(items))


@router.post("/profile/{user_id}/resume", response_model=ResumeResponse)
def add_resume_record(user_id: UUID, payload: ResumeCreateRequest) -> ResumeResponse:
    """Add an existing resume record by providing a file URL."""
    result = add_resume(user_id, payload)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/profile/{user_id}/resume/upload")
def upload_resume_file(user_id: UUID, file: UploadFile = File(...)):
    """Upload a resume file to Supabase Storage and save its metadata."""
    result = upload_resume_to_storage(user_id, file)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------- AUTHENTICATION ---------------- #

@router.post("/auth/register")
def register(payload: RegisterRequest):
    """
    Register a new user with Supabase Auth and create an employer or job_seeker profile.
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
