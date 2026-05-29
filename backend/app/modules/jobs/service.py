<<<<<<< HEAD
"""
Jobs Service Layer
Business logic for job posting management (``public.jobs``).
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from .mapping import (
    JOBS_TABLE,
    job_create_to_row,
    job_update_to_row,
    row_to_job,
)
from .models import (
    Job,
    JobCreate,
    JobCloseResponse,
    JobListResponse,
    JobPublishResponse,
    JobSearchFilters,
    JobStatus,
    JobUpdate,
=======
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
>>>>>>> 28d9068 (Clean matching module branch for push)
)


class JobService:
<<<<<<< HEAD
    """Service class for job posting operations against ``public.jobs``."""

    def __init__(self, supabase_client: Client):
        self.db = supabase_client

    def _company_name_for(self, employer_id: UUID) -> str:
        """Load display company name from ``employers`` when available."""
        response = (
            self.db.table("employers")
            .select("company_name")
            .eq("id", str(employer_id))
            .limit(1)
            .execute()
        )
        if response.data and response.data[0].get("company_name"):
            return response.data[0]["company_name"]
        return "Employer"

    def _applications_count_for(self, job_id: UUID | str) -> int:
        """Count tracking applications for a job."""
        response = (
            self.db.table("applications")
            .select("id", count="exact")
            .eq("job_id", str(job_id))
            .execute()
        )
        return int(response.count or 0)

    def _row_to_job(self, row: dict, *, company_name: str = "Employer") -> Job:
        return row_to_job(
            row,
            company_name=company_name,
            applications_count=self._applications_count_for(row["id"]),
        )

    async def create_job(self, job_data: JobCreate, employer_id: UUID) -> Job:
        """Create a new job posting (DRAFT)."""
        try:
            payload = job_create_to_row(job_data, employer_id)
            response = self.db.table(JOBS_TABLE).insert(payload).execute()
=======
    """Service class for job posting operations"""

    def __init__(self, supabase_client: Client):
        """Initialize with Supabase client"""
        self.db = supabase_client

    async def create_job(self, job_data: JobCreate, employer_id: UUID) -> Job:

        try:
            job_dict = job_data.dict()
            job_dict['employer_id'] = str(employer_id)
            job_dict['status'] = JobStatus.DRAFT.value
            job_dict['views_count'] = 0
            job_dict['applications_count'] = 0
            job_dict['created_at'] = datetime.utcnow().isoformat()
            job_dict['updated_at'] = datetime.utcnow().isoformat()

            response = self.db.table('job_postings').insert(job_dict).execute()
>>>>>>> 28d9068 (Clean matching module branch for push)

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
                    detail="Failed to create job posting",
                )

            row = response.data[0]
            return self._row_to_job(row, company_name=self._company_name_for(employer_id))

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating job: {str(e)}",
            )

    async def get_job_by_id(
        self, job_id: UUID, employer_id: Optional[UUID] = None
    ) -> Job:
        """Get a job by ``jobs.id``; optional employer scope for ownership."""
        try:
            query = self.db.table(JOBS_TABLE).select("*").eq("id", str(job_id))

            if employer_id:
                query = query.eq("employer_id", str(employer_id))
=======
                    detail="Failed to create job posting"
                )

            return Job(**response.data[0])

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating job: {str(e)}"
            )

    async def get_job_by_id(self, job_id: UUID, employer_id: Optional[UUID] = None) -> Job:
        try:
            query = self.db.table('job_postings').select('*').eq('job_id', str(job_id))

            # If employer_id provided, verify ownership
            if employer_id:
                query = query.eq('employer_id', str(employer_id))
>>>>>>> 28d9068 (Clean matching module branch for push)

            response = query.execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
<<<<<<< HEAD
                    detail="Job posting not found",
                )

            row = response.data[0]

            # Increment view count if job is published and not viewed by owner
            if row["status"] == JobStatus.PUBLISHED.value and str(employer_id) != row["employer_id"]:
                self.db.rpc('increment_job_views', {'job_id': str(job_id)}).execute()
                # Update the local row object so the returned Job model has the incremented count
                row["views_count"] = row.get("views_count", 0) + 1

            emp_id = UUID(row["employer_id"])
            return self._row_to_job(row, company_name=self._company_name_for(emp_id))
=======
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
>>>>>>> 28d9068 (Clean matching module branch for push)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
                detail=f"Error retrieving job: {str(e)}",
            )

    async def update_job(
        self, job_id: UUID, job_data: JobUpdate, employer_id: UUID
    ) -> Job:
        """Update an existing job (owner only)."""
        try:
            existing_job = await self.get_job_by_id(job_id, employer_id)

            if existing_job.status == JobStatus.CLOSED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot update a closed job posting",
                )

            patch = job_update_to_row(job_data)
            if not patch:
                return existing_job

            response = (
                self.db.table(JOBS_TABLE)
                .update(patch)
                .eq("id", str(job_id))
                .eq("employer_id", str(employer_id))
                .execute()
            )
=======
                detail=f"Error retrieving job: {str(e)}"
            )

    async def update_job(self, job_id: UUID, job_data: JobUpdate, employer_id: UUID) -> Job:

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
>>>>>>> 28d9068 (Clean matching module branch for push)

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
                    detail="Failed to update job posting",
                )

            return self._row_to_job(
                response.data[0], company_name=self._company_name_for(employer_id)
            )
=======
                    detail="Failed to update job posting"
                )

            return Job(**response.data[0])
>>>>>>> 28d9068 (Clean matching module branch for push)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
                detail=f"Error updating job: {str(e)}",
            )

    async def publish_job(
        self, job_id: UUID, employer_id: UUID
    ) -> JobPublishResponse:
        """Publish a job (status draft → published)."""
        try:
=======
                detail=f"Error updating job: {str(e)}"
            )

    async def publish_job(self, job_id: UUID, employer_id: UUID) -> JobPublishResponse:

        try:
            # Verify ownership and current status
>>>>>>> 28d9068 (Clean matching module branch for push)
            existing_job = await self.get_job_by_id(job_id, employer_id)

            if existing_job.status == JobStatus.PUBLISHED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
<<<<<<< HEAD
                    detail="Job posting is already published",
=======
                    detail="Job posting is already published"
>>>>>>> 28d9068 (Clean matching module branch for push)
                )

            if existing_job.status == JobStatus.CLOSED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
<<<<<<< HEAD
                    detail="Cannot publish a closed job posting",
                )

            published_at = datetime.now(timezone.utc)

            response = (
                self.db.table(JOBS_TABLE)
                .update({"status": JobStatus.PUBLISHED.value})
                .eq("id", str(job_id))
                .eq("employer_id", str(employer_id))
                .execute()
            )
=======
                    detail="Cannot publish a closed job posting"
                )

            published_at = datetime.utcnow()

            response = self.db.table('job_postings').update({
                'status': JobStatus.PUBLISHED.value,
                'published_at': published_at.isoformat(),
                'updated_at': published_at.isoformat()
            }).eq('job_id', str(job_id)).eq('employer_id', str(employer_id)).execute()
>>>>>>> 28d9068 (Clean matching module branch for push)

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
                    detail="Failed to publish job posting",
=======
                    detail="Failed to publish job posting"
>>>>>>> 28d9068 (Clean matching module branch for push)
                )

            return JobPublishResponse(
                job_id=job_id,
                status=JobStatus.PUBLISHED,
                published_at=published_at,
<<<<<<< HEAD
                message="Job posting published successfully",
=======
                message="Job posting published successfully"
>>>>>>> 28d9068 (Clean matching module branch for push)
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
                detail=f"Error publishing job: {str(e)}",
            )

    async def close_job(self, job_id: UUID, employer_id: UUID) -> JobCloseResponse:
        """Close a job (status → closed)."""
        try:
=======
                detail=f"Error publishing job: {str(e)}"
            )

    async def close_job(self, job_id: UUID, employer_id: UUID) -> JobCloseResponse:
        try:
            # Verify ownership
>>>>>>> 28d9068 (Clean matching module branch for push)
            existing_job = await self.get_job_by_id(job_id, employer_id)

            if existing_job.status == JobStatus.CLOSED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
<<<<<<< HEAD
                    detail="Job posting is already closed",
                )

            closed_at = datetime.now(timezone.utc)

            response = (
                self.db.table(JOBS_TABLE)
                .update({"status": JobStatus.CLOSED.value})
                .eq("id", str(job_id))
                .eq("employer_id", str(employer_id))
                .execute()
            )
=======
                    detail="Job posting is already closed"
                )

            closed_at = datetime.utcnow()

            response = self.db.table('job_postings').update({
                'status': JobStatus.CLOSED.value,
                'closed_at': closed_at.isoformat(),
                'updated_at': closed_at.isoformat()
            }).eq('job_id', str(job_id)).eq('employer_id', str(employer_id)).execute()
>>>>>>> 28d9068 (Clean matching module branch for push)

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
                    detail="Failed to close job posting",
=======
                    detail="Failed to close job posting"
>>>>>>> 28d9068 (Clean matching module branch for push)
                )

            return JobCloseResponse(
                job_id=job_id,
                status=JobStatus.CLOSED,
                closed_at=closed_at,
<<<<<<< HEAD
                message="Job posting closed successfully",
=======
                message="Job posting closed successfully"
>>>>>>> 28d9068 (Clean matching module branch for push)
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
                detail=f"Error closing job: {str(e)}",
            )

    async def search_jobs(self, filters: JobSearchFilters) -> JobListResponse:
        """Search published (or filtered) jobs in ``public.jobs``."""
        try:
            query = self.db.table(JOBS_TABLE).select("*", count="exact")
            query = query.eq("status", filters.status.value)

            if filters.keyword:
                keyword = filters.keyword.strip()
                query = query.or_(
                    f"title.ilike.%{keyword}%,description.ilike.%{keyword}%"
                )

            if filters.location:
                query = query.ilike("location", f"%{filters.location}%")

            if filters.work_mode:
                query = query.eq("work_mode", filters.work_mode.value)

            if filters.skills:
                skills_lower = [s.lower() for s in filters.skills]
                query = query.filter(
                    "required_skills", "cs", f'{{{",".join(skills_lower)}}}'
                )

            offset = (filters.page - 1) * filters.page_size
            query = query.order("created_at", desc=True).range(
=======
                detail=f"Error closing job: {str(e)}"
            )

    async def search_jobs(self, filters: JobSearchFilters) -> JobListResponse:
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
>>>>>>> 28d9068 (Clean matching module branch for push)
                offset, offset + filters.page_size - 1
            )

            response = query.execute()

<<<<<<< HEAD
            total = response.count if response.count else 0
            total_pages = (total + filters.page_size - 1) // filters.page_size

            jobs: List[Job] = []
            for row in response.data or []:
                emp_id = UUID(row["employer_id"])
                jobs.append(self._row_to_job(row, company_name=self._company_name_for(emp_id)))
=======
            # Get total count from response
            total = response.count if response.count else 0
            total_pages = (total + filters.page_size - 1) // filters.page_size

            jobs = [Job(**job) for job in response.data] if response.data else []
>>>>>>> 28d9068 (Clean matching module branch for push)

            return JobListResponse(
                jobs=jobs,
                total=total,
                page=filters.page,
                page_size=filters.page_size,
<<<<<<< HEAD
                total_pages=total_pages,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error searching jobs: {str(e)}",
=======
                total_pages=total_pages
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error searching jobs: {str(e)}"
>>>>>>> 28d9068 (Clean matching module branch for push)
            )

    async def get_employer_jobs(
        self,
        employer_id: UUID,
        status_filter: Optional[JobStatus] = None,
        page: int = 1,
<<<<<<< HEAD
        page_size: int = 10,
    ) -> JobListResponse:
        """List jobs for one employer."""
        try:
            query = (
                self.db.table(JOBS_TABLE)
                .select("*", count="exact")
                .eq("employer_id", str(employer_id))
            )

            if status_filter:
                query = query.eq("status", status_filter.value)

            offset = (page - 1) * page_size
            query = query.order("created_at", desc=True).range(
=======
        page_size: int = 10
    ) -> JobListResponse:
        try:
            query = self.db.table('job_postings').select('*', count='exact').eq(
                'employer_id', str(employer_id)
            )

            if status_filter:
                query = query.eq('status', status_filter.value)

            # Calculate pagination
            offset = (page - 1) * page_size

            query = query.order('created_at', desc=True).range(
>>>>>>> 28d9068 (Clean matching module branch for push)
                offset, offset + page_size - 1
            )

            response = query.execute()

            total = response.count if response.count else 0
            total_pages = (total + page_size - 1) // page_size
<<<<<<< HEAD
            company = self._company_name_for(employer_id)

            jobs = [self._row_to_job(row, company_name=company) for row in (response.data or [])]
=======

            jobs = [Job(**job) for job in response.data] if response.data else []
>>>>>>> 28d9068 (Clean matching module branch for push)

            return JobListResponse(
                jobs=jobs,
                total=total,
                page=page,
                page_size=page_size,
<<<<<<< HEAD
                total_pages=total_pages,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving employer jobs: {str(e)}",
            )

    async def delete_job(self, job_id: UUID, employer_id: UUID) -> dict:
        """Delete a DRAFT job only."""
        try:
            existing_job = await self.get_job_by_id(job_id, employer_id)

            if existing_job.status != JobStatus.DRAFT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Only draft job postings can be deleted. "
                        "Published or closed jobs should be closed instead."
                    ),
                )

            self.db.table(JOBS_TABLE).delete().eq("id", str(job_id)).eq(
                "employer_id", str(employer_id)
            ).execute()
=======
                total_pages=total_pages
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving employer jobs: {str(e)}"
            )

    async def delete_job(self, job_id: UUID, employer_id: UUID) -> dict:
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
>>>>>>> 28d9068 (Clean matching module branch for push)

            return {"message": "Job posting deleted successfully", "job_id": str(job_id)}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
                detail=f"Error deleting job: {str(e)}",
=======
                detail=f"Error deleting job: {str(e)}"
>>>>>>> 28d9068 (Clean matching module branch for push)
            )
