"""
Jobs Service Layer
Business logic for job posting management
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from supabase import Client

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


class JobService:
    """Service class for job posting operations"""

    def __init__(self, supabase_client: Client):
        """Initialize with Supabase client"""
        self.db = supabase_client

    async def create_job(self, job_data: JobCreate, employer_id: UUID) -> Job:
        """
        Create a new job posting (initially in DRAFT status)

        Args:
            job_data: Job creation data
            employer_id: UUID of the employer creating the job

        Returns:
            Created job posting

        Raises:
            HTTPException: If creation fails
        """
        try:
            job_dict = job_data.dict()
            job_dict['employer_id'] = str(employer_id)
            job_dict['status'] = JobStatus.DRAFT.value
            job_dict['views_count'] = 0
            job_dict['applications_count'] = 0
            job_dict['created_at'] = datetime.utcnow().isoformat()
            job_dict['updated_at'] = datetime.utcnow().isoformat()

            response = self.db.table('job_postings').insert(job_dict).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create job posting"
                )

            return Job(**response.data[0])

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating job: {str(e)}"
            )

    async def get_job_by_id(self, job_id: UUID, employer_id: Optional[UUID] = None) -> Job:
        """
        Get a job posting by ID

        Args:
            job_id: UUID of the job
            employer_id: Optional employer ID for ownership verification

        Returns:
            Job posting

        Raises:
            HTTPException: If job not found or unauthorized
        """
        try:
            query = self.db.table('job_postings').select('*').eq('job_id', str(job_id))

            # If employer_id provided, verify ownership
            if employer_id:
                query = query.eq('employer_id', str(employer_id))

            response = query.execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job posting not found"
                )

            # Increment view count (only for published jobs viewed by non-owners)
            if not employer_id:
                job = response.data[0]
                if job['status'] == JobStatus.PUBLISHED.value:
                    self.db.table('job_postings').update({
                        'views_count': job['views_count'] + 1
                    }).eq('job_id', str(job_id)).execute()

            return Job(**response.data[0])

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving job: {str(e)}"
            )

    async def update_job(self, job_id: UUID, job_data: JobUpdate, employer_id: UUID) -> Job:
        """
        Update an existing job posting

        Args:
            job_id: UUID of the job to update
            job_data: Updated job data
            employer_id: UUID of the employer (for ownership verification)

        Returns:
            Updated job posting

        Raises:
            HTTPException: If job not found, unauthorized, or update fails
        """
        try:
            # Verify ownership
            existing_job = await self.get_job_by_id(job_id, employer_id)

            # Don't allow updates to closed jobs
            if existing_job.status == JobStatus.CLOSED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot update a closed job posting"
                )

            # Prepare update data (exclude None values)
            update_dict = {k: v for k, v in job_data.dict().items() if v is not None}

            if not update_dict:
                return existing_job

            update_dict['updated_at'] = datetime.utcnow().isoformat()

            response = self.db.table('job_postings').update(update_dict).eq(
                'job_id', str(job_id)
            ).eq('employer_id', str(employer_id)).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update job posting"
                )

            return Job(**response.data[0])

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating job: {str(e)}"
            )

    async def publish_job(self, job_id: UUID, employer_id: UUID) -> JobPublishResponse:
        """
        Publish a job posting (change status from DRAFT to PUBLISHED)

        Args:
            job_id: UUID of the job to publish
            employer_id: UUID of the employer (for ownership verification)

        Returns:
            Publish response with status and timestamp

        Raises:
            HTTPException: If job not found, unauthorized, or already published
        """
        try:
            # Verify ownership and current status
            existing_job = await self.get_job_by_id(job_id, employer_id)

            if existing_job.status == JobStatus.PUBLISHED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Job posting is already published"
                )

            if existing_job.status == JobStatus.CLOSED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot publish a closed job posting"
                )

            published_at = datetime.utcnow()

            response = self.db.table('job_postings').update({
                'status': JobStatus.PUBLISHED.value,
                'published_at': published_at.isoformat(),
                'updated_at': published_at.isoformat()
            }).eq('job_id', str(job_id)).eq('employer_id', str(employer_id)).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to publish job posting"
                )

            return JobPublishResponse(
                job_id=job_id,
                status=JobStatus.PUBLISHED,
                published_at=published_at,
                message="Job posting published successfully"
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error publishing job: {str(e)}"
            )

    async def close_job(self, job_id: UUID, employer_id: UUID) -> JobCloseResponse:
        """
        Close a job posting

        Args:
            job_id: UUID of the job to close
            employer_id: UUID of the employer (for ownership verification)

        Returns:
            Close response with status and timestamp

        Raises:
            HTTPException: If job not found, unauthorized, or already closed
        """
        try:
            # Verify ownership
            existing_job = await self.get_job_by_id(job_id, employer_id)

            if existing_job.status == JobStatus.CLOSED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Job posting is already closed"
                )

            closed_at = datetime.utcnow()

            response = self.db.table('job_postings').update({
                'status': JobStatus.CLOSED.value,
                'closed_at': closed_at.isoformat(),
                'updated_at': closed_at.isoformat()
            }).eq('job_id', str(job_id)).eq('employer_id', str(employer_id)).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to close job posting"
                )

            return JobCloseResponse(
                job_id=job_id,
                status=JobStatus.CLOSED,
                closed_at=closed_at,
                message="Job posting closed successfully"
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error closing job: {str(e)}"
            )

    async def search_jobs(self, filters: JobSearchFilters) -> JobListResponse:
        """
        Search and filter job postings

        Args:
            filters: Search and filter parameters

        Returns:
            Paginated list of job postings

        Raises:
            HTTPException: If search fails
        """
        try:
            # Start with base query
            query = self.db.table('job_postings').select('*', count='exact')

            # Apply status filter (default to PUBLISHED only)
            query = query.eq('status', filters.status.value)

            # Apply keyword search on title and description
            if filters.keyword:
                keyword = filters.keyword.strip().lower()
                # Note: Supabase uses ilike for case-insensitive matching
                query = query.or_(
                    f'title.ilike.%{keyword}%,description.ilike.%{keyword}%'
                )

            # Apply location filter
            if filters.location:
                query = query.ilike('location', f'%{filters.location}%')

            # Apply work mode filter
            if filters.work_mode:
                query = query.eq('work_mode', filters.work_mode.value)

            # Apply education level filter
            if filters.education_level:
                query = query.eq('education_level', filters.education_level.value)

            # Apply experience level filter
            if filters.experience_level:
                query = query.eq('experience_level', filters.experience_level.value)

            # Apply skills filter (job must have at least one matching skill)
            if filters.skills:
                skills_lower = [s.lower() for s in filters.skills]
                # PostgreSQL array overlap operator
                query = query.filter('required_skills', 'cs', f'{{{",".join(skills_lower)}}}')

            # Apply salary filters
            if filters.min_salary is not None:
                query = query.gte('salary_max', filters.min_salary)

            if filters.max_salary is not None:
                query = query.lte('salary_min', filters.max_salary)

            # Calculate pagination
            offset = (filters.page - 1) * filters.page_size

            # Execute query with pagination
            query = query.order('created_at', desc=True).range(
                offset, offset + filters.page_size - 1
            )

            response = query.execute()

            # Get total count from response
            total = response.count if response.count else 0
            total_pages = (total + filters.page_size - 1) // filters.page_size

            jobs = [Job(**job) for job in response.data] if response.data else []

            return JobListResponse(
                jobs=jobs,
                total=total,
                page=filters.page,
                page_size=filters.page_size,
                total_pages=total_pages
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error searching jobs: {str(e)}"
            )

    async def get_employer_jobs(
        self,
        employer_id: UUID,
        status_filter: Optional[JobStatus] = None,
        page: int = 1,
        page_size: int = 10
    ) -> JobListResponse:
        """
        Get all jobs posted by a specific employer

        Args:
            employer_id: UUID of the employer
            status_filter: Optional status filter
            page: Page number
            page_size: Items per page

        Returns:
            Paginated list of employer's job postings
        """
        try:
            query = self.db.table('job_postings').select('*', count='exact').eq(
                'employer_id', str(employer_id)
            )

            if status_filter:
                query = query.eq('status', status_filter.value)

            # Calculate pagination
            offset = (page - 1) * page_size

            query = query.order('created_at', desc=True).range(
                offset, offset + page_size - 1
            )

            response = query.execute()

            total = response.count if response.count else 0
            total_pages = (total + page_size - 1) // page_size

            jobs = [Job(**job) for job in response.data] if response.data else []

            return JobListResponse(
                jobs=jobs,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving employer jobs: {str(e)}"
            )

    async def delete_job(self, job_id: UUID, employer_id: UUID) -> dict:
        """
        Delete a job posting (only allowed for DRAFT jobs)

        Args:
            job_id: UUID of the job to delete
            employer_id: UUID of the employer (for ownership verification)

        Returns:
            Success message

        Raises:
            HTTPException: If job not found, unauthorized, or cannot be deleted
        """
        try:
            # Verify ownership and status
            existing_job = await self.get_job_by_id(job_id, employer_id)

            # Only allow deletion of DRAFT jobs
            if existing_job.status != JobStatus.DRAFT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only draft job postings can be deleted. Published or closed jobs should be closed instead."
                )

            response = self.db.table('job_postings').delete().eq(
                'job_id', str(job_id)
            ).eq('employer_id', str(employer_id)).execute()

            return {"message": "Job posting deleted successfully", "job_id": str(job_id)}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting job: {str(e)}"
            )
