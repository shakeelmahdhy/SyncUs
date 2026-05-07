from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional


# -------- USER / JOB SEEKER --------
class UserCreateRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    user_id: Optional[UUID] = None


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None


# -------- RESUME --------
class ResumeCreateRequest(BaseModel):
    file_url: str


class ResumeResponse(BaseModel):
    id: UUID
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

