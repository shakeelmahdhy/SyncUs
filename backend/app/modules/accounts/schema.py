from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional, List


# -------- USER / JOB SEEKER --------

class UserCreateRequest(BaseModel):
    user_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None

    # New requirement fields
    work_experience: Optional[str] = None
    skills: Optional[List[str]] = None
    preferred_working_mode: Optional[str] = None
    preferred_location: Optional[str] = None

    # Membership feature
    membership: bool = False


class UserResponse(BaseModel):
    id: Optional[UUID] = None
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    user_id: Optional[UUID] = None

    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None

    work_experience: Optional[str] = None
    skills: Optional[List[str]] = None
    preferred_working_mode: Optional[str] = None
    preferred_location: Optional[str] = None

    membership: Optional[bool] = False


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None

    work_experience: Optional[str] = None
    skills: Optional[List[str]] = None
    preferred_working_mode: Optional[str] = None
    preferred_location: Optional[str] = None

    membership: Optional[bool] = None


# -------- RESUME --------

class ResumeCreateRequest(BaseModel):
    resume_name: str
    file_url: str


class ResumeResponse(BaseModel):
    id: Optional[UUID] = None
    job_seeker_id: UUID
    resume_name: Optional[str] = None
    file_url: str


# -------- AUTH --------

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str



