from pydantic import BaseModel
from uuid import UUID


# -------- USER --------
class UserCreateRequest(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str


class UserUpdateRequest(BaseModel):
    name: Optional[str] | None = None
    email: Optional[str] | None = None


# -------- RESUME --------
class ResumeCreateRequest(BaseModel):
    file_url: str


class ResumeResponse(BaseModel):
    id: UUID
    file_url: str
    user_id: UUID
