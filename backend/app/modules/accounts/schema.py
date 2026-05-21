from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Literal, Optional


# -------- USER / JOB SEEKER --------
class UserCreateRequest(BaseModel):
    user_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    location: str
    bio: str


class UserResponse(BaseModel):
    id: Optional[UUID] = None        
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
    account_type: Literal["job_seeker", "employer"] = "job_seeker"
    company_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
