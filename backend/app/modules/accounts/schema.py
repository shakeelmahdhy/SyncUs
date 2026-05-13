from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str
    email: str


class AccountProfile(BaseModel):
    id: int
    first_name: str = ""
    last_name: str = ""
    email: str
    phone: str = ""
    location: str = ""
    title: str = ""
    experience: str = ""
    bio: str = ""
    linkedin: str = ""
    portfolio: str = ""
    education: str = ""
    company: str = ""
    skills: list[str] = Field(default_factory=list)


class AccountProfileUpdate(BaseModel):
    first_name: str = ""
    last_name: str = ""
    email: str
    phone: str = ""
    location: str = ""
    title: str = ""
    experience: str = ""
    bio: str = ""
    linkedin: str = ""
    portfolio: str = ""
    education: str = ""
    company: str = ""
    skills: list[str] = Field(default_factory=list)
