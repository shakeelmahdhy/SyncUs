"""
Jobs Module Data Models
Pydantic models for job posting validation and serialization
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID


class WorkMode(str, Enum):
    """Work mode options for job postings"""
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"


class JobStatus(str, Enum):
    """Job posting status workflow"""
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"


class EducationLevel(str, Enum):
    """Education level requirements"""
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    ANY = "any"


class ExperienceLevel(str, Enum):
    """Experience level requirements"""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    ANY = "any"


class JobBase(BaseModel):
    """Base job posting model with common fields"""
    title: str = Field(..., min_length=3, max_length=200)
    company_name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=50, max_length=5000)
    required_skills: List[str] = Field(..., min_items=1, max_items=20)
    location: str = Field(..., min_length=2, max_length=200)
    work_mode: WorkMode
    education_level: EducationLevel = EducationLevel.ANY
    experience_level: ExperienceLevel = ExperienceLevel.ANY
    min_years_experience: Optional[int] = Field(None, ge=0, le=50)
    max_years_experience: Optional[int] = Field(None, ge=0, le=50)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    contact_email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    website: Optional[str] = None

    @validator('required_skills')
    def validate_skills(cls, v):
        """Validate and normalize skills"""
        if not v:
            raise ValueError('At least one skill is required')
        # Remove duplicates and empty strings, convert to lowercase
        cleaned = list(set(skill.strip().lower() for skill in v if skill.strip()))
        if not cleaned:
            raise ValueError('At least one valid skill is required')
        return cleaned

    @validator('max_years_experience')
    def validate_experience_range(cls, v, values):
        """Ensure max experience is greater than min"""
        if v is not None and 'min_years_experience' in values:
            min_exp = values['min_years_experience']
            if min_exp is not None and v < min_exp:
                raise ValueError('max_years_experience must be greater than or equal to min_years_experience')
        return v

    @validator('salary_max')
    def validate_salary_range(cls, v, values):
        """Ensure max salary is greater than min"""
        if v is not None and 'salary_min' in values:
            min_sal = values['salary_min']
            if min_sal is not None and v < min_sal:
                raise ValueError('salary_max must be greater than or equal to salary_min')
        return v


class JobCreate(JobBase):
    """Model for creating a new job posting"""
    pass


class JobUpdate(BaseModel):
    """Model for updating an existing job posting"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    company_name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, min_length=50, max_length=5000)
    required_skills: Optional[List[str]] = Field(None, min_items=1, max_items=20)
    location: Optional[str] = Field(None, min_length=2, max_length=200)
    work_mode: Optional[WorkMode] = None
    education_level: Optional[EducationLevel] = None
    experience_level: Optional[ExperienceLevel] = None
    min_years_experience: Optional[int] = Field(None, ge=0, le=50)
    max_years_experience: Optional[int] = Field(None, ge=0, le=50)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    contact_email: Optional[str] = Field(None, regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    website: Optional[str] = None


class Job(JobBase):
    """Complete job posting model with database fields"""
    job_id: UUID
    employer_id: UUID
    status: JobStatus
    views_count: int = 0
    applications_count: int = 0
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class JobSearchFilters(BaseModel):
    """Model for job search and filtering parameters"""
    keyword: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = None
    work_mode: Optional[WorkMode] = None
    education_level: Optional[EducationLevel] = None
    experience_level: Optional[ExperienceLevel] = None
    skills: Optional[List[str]] = None
    min_salary: Optional[int] = Field(None, ge=0)
    max_salary: Optional[int] = Field(None, ge=0)
    status: JobStatus = JobStatus.PUBLISHED
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class JobListResponse(BaseModel):
    """Paginated job listing response"""
    jobs: List[Job]
    total: int
    page: int
    page_size: int
    total_pages: int


class JobPublishResponse(BaseModel):
    """Response after publishing a job"""
    job_id: UUID
    status: JobStatus
    published_at: datetime
    message: str


class JobCloseResponse(BaseModel):
    """Response after closing a job"""
    job_id: UUID
    status: JobStatus
    closed_at: datetime
    message: str
