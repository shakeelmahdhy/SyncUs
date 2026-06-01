from typing import Optional, List
from fastapi import APIRouter, Depends, Query

from .models import (
    JobSearchRequest,
    JobSearchResponse,
    CandidateFilterRequest,
    CandidateFilterResponse,
)
from .service import SearchService
from app.core.auth import EmployerUserDep
from app.core.supabase_client import get_supabase_service_client

router = APIRouter()


def get_search_service() -> SearchService:
    """Build SearchService with the shared server-side Supabase client (Option A)."""
    return SearchService(get_supabase_service_client())


@router.get(
    "/jobs",
    response_model=JobSearchResponse,
    summary="Search job postings",
    description=(
        "Enhanced search across published job postings. "
        "Keyword search considers titles, descriptions, employers, skills, experience, locations, and work preferences. "
        "Fuzzy matching handles common typos and related terms."
    ),
)
async def search_jobs(
    keyword: Optional[str] = Query(None, description="Search keyword, including fuzzy or related terms"),
    location: Optional[str] = Query(None, description="Filter by location"),
    work_mode: Optional[str] = Query(None, description="remote | onsite | hybrid"),
    employment_type: Optional[str] = Query(None, description="full-time | part-time | casual | contract"),
    education_level: Optional[str] = Query(None, description="any | bachelor | master | phd"),
    experience_level: Optional[str] = Query(None, description="entry | junior | mid | senior"),
    skills: Optional[str] = Query(None, description="Comma-separated skills, e.g. react,python"),
    min_salary: Optional[int] = Query(None, ge=0),
    max_salary: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query("newest", description="newest | oldest | relevance"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search_service: SearchService = Depends(get_search_service),
) -> JobSearchResponse:
    """
    Search for published job postings.

    - **keyword**: Searches job, employer, skill, experience, location, and work preference text
    - **skills**: Comma-separated, e.g. `react,python,fastapi`
    - **sort_by**: `newest` (default), `oldest`, or `relevance`
    """
    skills_list = None
    if skills:
        skills_list = [s.strip() for s in skills.split(",") if s.strip()]

    request = JobSearchRequest(
        keyword=keyword,
        location=location,
        work_mode=work_mode,
        employment_type=employment_type,
        education_level=education_level,
        experience_level=experience_level,
        skills=skills_list,
        min_salary=min_salary,
        max_salary=max_salary,
        sort_by=sort_by or "newest",
        page=page,
        page_size=page_size,
    )

    return await search_service.search_jobs(request)


@router.get(
    "/candidates",
    response_model=CandidateFilterResponse,
    summary="Filter candidates by skills and profile",
    description=(
        "Allows employers to search the candidate pool by skill tags, "
        "education level, major, GPA, and availability. "
        "Only returns candidates with ≥80% profile completeness."
    ),
)
async def filter_candidates(
    current_employer: EmployerUserDep,
    keyword: Optional[str] = Query(None, description="Search candidate names, skills, education, experience, and preferences"),
    skills: Optional[str] = Query(None, description="Comma-separated skill tags, e.g. react,python"),
    education_level: Optional[str] = Query(None, description="any | bachelor | master | phd"),
    major: Optional[str] = Query(None, description="Field of study, e.g. Computer Science"),
    min_gpa: Optional[float] = Query(None, ge=0.0, le=4.0, description="Minimum GPA (0.0–4.0)"),
    location: Optional[str] = Query(None),
    available_for: Optional[str] = Query(None, description="internship | full-time | part-time"),
    sort_by: Optional[str] = Query("relevance", description="relevance | newest | oldest"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search_service: SearchService = Depends(get_search_service),
) -> CandidateFilterResponse:
    """
    Filter candidates for employer talent sourcing.

    - **skills**: Comma-separated skill tags (e.g. `react,typescript,postgresql`)
    - **min_gpa**: Minimum GPA threshold (0.0–4.0 scale)
    - **available_for**: Filter by availability type
    - **sort_by**: `relevance` sorts by profile completeness (default)
    """
    skills_list = None
    if skills:
        skills_list = [s.strip() for s in skills.split(",") if s.strip()]

    request = CandidateFilterRequest(
        keyword=keyword,
        skill_tags=skills_list,
        education_level=education_level,
        major=major,
        min_gpa=min_gpa,
        location=location,
        available_for=available_for,
        sort_by=sort_by or "relevance",
        page=page,
        page_size=page_size,
    )

    return await search_service.filter_candidates(request)
