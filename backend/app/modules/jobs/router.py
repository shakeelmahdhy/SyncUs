from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse

from .models import (
    Job,
    JobCreate,
    JobUpdate,
    JobStatus,
    JobSearchFilters,
    JobListResponse,
    JobPublishResponse,
    JobCloseResponse
)
from .service import JobService
from app.core.auth import EmployerUserDep, OptionalUserDep
from app.core.supabase_client import get_supabase_service_client


router = APIRouter()


def get_job_service() -> JobService:
    """Build JobService with the shared server-side Supabase client (Option A)."""
    return JobService(get_supabase_service_client())


@router.post(
    "",
    response_model=Job,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job posting",
    description="Create a new job posting in DRAFT status. Only employers can create jobs."
)
async def create_job(
    job_data: JobCreate,
    current_employer: EmployerUserDep,
    job_service: JobService = Depends(get_job_service)
) -> Job:
    """
    Create a new job posting.

    - **title**: Job title (required)
    - **company_name**: Company name (required)
    - **description**: Job description (required, min 50 chars)
    - **required_skills**: List of required skills (required)
    - **location**: Job location (required)
    - **work_mode**: remote/onsite/hybrid (required)
    - **education_level**: Minimum education required
    - **experience_level**: Experience level required
    - **min_years_experience**: Minimum years of experience
    - **max_years_experience**: Maximum years of experience
    - **salary_min**: Minimum salary
    - **salary_max**: Maximum salary
    - **contact_email**: Contact email (required)
    - **website**: Company website URL
    """
    employer_id = current_employer.sub
    return await job_service.create_job(job_data, employer_id)


@router.get(
    "/{job_id}",
    response_model=Job,
    summary="Get job posting details",
    description="Retrieve a specific job posting by ID. Increments view count for published jobs."
)
async def get_job(
    job_id: UUID,
    current_user: OptionalUserDep,
    job_service: JobService = Depends(get_job_service)
) -> Job:
    """
    Get a job posting by ID.

    - **job_id**: UUID of the job posting
    """
    # If user is an employer, verify ownership to see draft jobs
    employer_id = None
    if current_user and current_user.role == "employer":
        employer_id = current_user.sub

    return await job_service.get_job_by_id(job_id, employer_id)


@router.patch(
    "/{job_id}",
    response_model=Job,
    summary="Update a job posting",
    description="Update an existing job posting. Only the posting employer can update their jobs."
)
async def update_job(
    job_id: UUID,
    job_data: JobUpdate,
    current_employer: EmployerUserDep,
    job_service: JobService = Depends(get_job_service)
) -> Job:
    employer_id = current_employer.sub
    return await job_service.update_job(job_id, job_data, employer_id)


@router.post(
    "/{job_id}/publish",
    response_model=JobPublishResponse,
    summary="Publish a job posting",
    description="Change job status from DRAFT to PUBLISHED. Only the posting employer can publish their jobs."
)
async def publish_job(
    job_id: UUID,
    current_employer: EmployerUserDep,
    job_service: JobService = Depends(get_job_service)
) -> JobPublishResponse:
    employer_id = current_employer.sub
    return await job_service.publish_job(job_id, employer_id)


@router.post(
    "/{job_id}/close",
    response_model=JobCloseResponse,
    summary="Close a job posting",
    description="Close a job posting. Only the posting employer can close their jobs."
)
async def close_job(
    job_id: UUID,
    current_employer: EmployerUserDep,
    job_service: JobService = Depends(get_job_service)
) -> JobCloseResponse:
    employer_id = current_employer.sub
    return await job_service.close_job(job_id, employer_id)


@router.get(
    "",
    response_model=JobListResponse,
    summary="Search and filter job postings",
    description="Search for job postings with various filters. Returns paginated results."
)
async def search_jobs(
    keyword: Optional[str] = Query(None, description="Search keyword for title and description"),
    location: Optional[str] = Query(None, description="Filter by location"),
    work_mode: Optional[str] = Query(None, description="Filter by work mode (remote/onsite/hybrid)"),
    education_level: Optional[str] = Query(None, description="Filter by education level"),
    experience_level: Optional[str] = Query(None, description="Filter by experience level"),
    skills: Optional[str] = Query(None, description="Comma-separated list of skills"),
    min_salary: Optional[int] = Query(None, ge=0, description="Minimum salary"),
    max_salary: Optional[int] = Query(None, ge=0, description="Maximum salary"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    job_service: JobService = Depends(get_job_service)
) -> JobListResponse:
    """
    Search for job postings with filters.

    - **keyword**: Search in title and description
    - **location**: Filter by location
    - **work_mode**: Filter by work mode (remote/onsite/hybrid)
    - **education_level**: Filter by minimum education level
    - **experience_level**: Filter by experience level
    - **skills**: Comma-separated skills (e.g., "react,python,fastapi")
    - **min_salary**: Minimum salary threshold
    - **max_salary**: Maximum salary threshold
    - **page**: Page number for pagination
    - **page_size**: Number of results per page (max 100)
    """
    # Parse skills from comma-separated string
    skills_list = None
    if skills:
        skills_list = [s.strip() for s in skills.split(',') if s.strip()]

    filters = JobSearchFilters(
        keyword=keyword,
        location=location,
        work_mode=work_mode,
        education_level=education_level,
        experience_level=experience_level,
        skills=skills_list,
        min_salary=min_salary,
        max_salary=max_salary,
        page=page,
        page_size=page_size
    )

    return await job_service.search_jobs(filters)


@router.get(
    "/employer/my-jobs",
    response_model=JobListResponse,
    summary="Get employer's job postings",
    description="Get all job postings created by the current employer."
)
async def get_my_jobs(
    current_employer: EmployerUserDep,
    status_filter: Optional[JobStatus] = Query(None, description="Filter by job status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    job_service: JobService = Depends(get_job_service),
) -> JobListResponse:
    employer_id = current_employer.sub
    return await job_service.get_employer_jobs(
        employer_id=employer_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size
    )


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a job posting",
    description="Delete a DRAFT job posting. Only the posting employer can delete their jobs."
)
async def delete_job(
    job_id: UUID,
    current_employer: EmployerUserDep,
    job_service: JobService = Depends(get_job_service)
) -> dict:
    employer_id = current_employer.sub
    return await job_service.delete_job(job_id, employer_id)


@router.get(
    "/stats/overview",
    summary="Get job posting statistics",
    description="Get overview statistics for the current employer's job postings."
)
async def get_job_stats(
    current_employer: EmployerUserDep,
    job_service: JobService = Depends(get_job_service)
) -> dict:
    employer_id = current_employer.sub

    # Get all jobs for this employer
    all_jobs = await job_service.get_employer_jobs(
        employer_id=employer_id,
        page=1,
        page_size=1000  # Get all jobs for stats
    )

    # Calculate statistics
    stats = {
        'total_jobs': all_jobs.total,
        'draft_count': sum(1 for job in all_jobs.jobs if job.status == JobStatus.DRAFT),
        'published_count': sum(1 for job in all_jobs.jobs if job.status == JobStatus.PUBLISHED),
        'closed_count': sum(1 for job in all_jobs.jobs if job.status == JobStatus.CLOSED),
        'total_views': sum(job.views_count for job in all_jobs.jobs),
        'total_applications': sum(job.applications_count for job in all_jobs.jobs)
    }

    return stats
