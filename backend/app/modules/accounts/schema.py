from pydantic import BaseModel
from uuid import UUID
from typing import Optional


# -------- USER / JOB SEEKER --------
class UserCreateRequest(BaseModel):
    first_name: str
    last_name: str
    email: str


class UserResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: Optional[str] = None


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


# -------- RESUME --------
class ResumeCreateRequest(BaseModel):
    file_url: str


class ResumeResponse(BaseModel):
    id: UUID
    job_seeker_id: UUID
    file_url: str

#---------Add Authentication Request schemas ---------

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str
