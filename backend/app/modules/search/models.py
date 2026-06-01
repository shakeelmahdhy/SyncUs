from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class SortOrder(str, Enum):
    NEWEST = "newest"
    OLDEST = "oldest"
    RELEVANCE = "relevance"


class JobSearchRequest(BaseModel):
    """Filters for job search (used by candidates)"""
    keyword: Optional[str] = Field(None, max_length=200, description="Search across jobs, employers, skills, and preferences")
    location: Optional[str] = Field(None, max_length=200)
    work_mode: Optional[str] = Field(None, description="remote | onsite | hybrid")
    employment_type: Optional[str] = Field(None, description="full-time | part-time | casual | contract")
    education_level: Optional[str] = None
    experience_level: Optional[str] = None
    skills: Optional[List[str]] = Field(None, description="List of required skills to match")
    min_salary: Optional[int] = Field(None, ge=0)
    max_salary: Optional[int] = Field(None, ge=0)
    sort_by: SortOrder = SortOrder.NEWEST
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class JobSearchResult(BaseModel):
    """Single job result in search response"""
    job_id: str
    title: str
    company_name: str
    location: str
    work_mode: str
    required_skills: List[str]
    education_level: Optional[str]
    experience_level: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    published_at: Optional[str]
    views_count: int
    applications_count: int


class JobSearchResponse(BaseModel):
    """Paginated job search response"""
    results: List[JobSearchResult]
    total: int
    page: int
    page_size: int
    total_pages: int
    keyword_used: Optional[str] = None


class CandidateFilterRequest(BaseModel):
    """Filters for candidate search (used by employers)"""
    keyword: Optional[str] = Field(None, max_length=200, description="Search candidate profile text")
    skill_tags: Optional[List[str]] = Field(None, description="Skills to filter by (e.g. ['react', 'python'])")
    education_level: Optional[str] = None
    major: Optional[str] = Field(None, description="Field of study")
    min_gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    location: Optional[str] = None
    available_for: Optional[str] = Field(None, description="internship | full-time | part-time")
    sort_by: SortOrder = SortOrder.RELEVANCE
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class CandidateResult(BaseModel):
    """Single candidate result in filter response"""
    candidate_id: str
    full_name: str
    major: Optional[str]
    education_level: Optional[str]
    skills: List[str]
    location: Optional[str]
    gpa: Optional[float]
    profile_completeness: Optional[int]
    has_github: bool
    available_for: Optional[str]


class CandidateFilterResponse(BaseModel):
    """Paginated candidate filter response"""
    results: List[CandidateResult]
    total: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: List[str]
