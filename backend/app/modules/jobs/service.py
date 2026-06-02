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
)


class JobService:
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

    async def create_job(
        self,
        job_data: JobCreate,
        employer_id: UUID,
        *,
        publish: bool = False,
    ) -> Job:
        """Create a new job posting (DRAFT, or PUBLISHED when ``publish=True``)."""
        try:
            payload = job_create_to_row(job_data, employer_id, publish=publish)
            response = self.db.table(JOBS_TABLE).insert(payload).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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

            response = query.execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job posting not found",
                )

            row = response.data[0]

            # Increment view count if job is published and not viewed by owner.
            # Some deployed Supabase projects do not have this optional RPC yet;
            # analytics should never prevent a job detail response.
            if row["status"] == JobStatus.PUBLISHED.value and str(employer_id) != row["employer_id"]:
                try:
                    self.db.rpc('increment_job_views', {'job_id': str(job_id)}).execute()
                    row["views_count"] = row.get("views_count", 0) + 1
                except Exception:
                    pass

            emp_id = UUID(row["employer_id"])
            return self._row_to_job(row, company_name=self._company_name_for(emp_id))

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update job posting",
                )

            return self._row_to_job(
                response.data[0], company_name=self._company_name_for(employer_id)
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating job: {str(e)}",
            )

    async def publish_job(
        self, job_id: UUID, employer_id: UUID
    ) -> JobPublishResponse:
        """Publish a job (status draft → published)."""
        try:
            existing_job = await self.get_job_by_id(job_id, employer_id)

            if existing_job.status == JobStatus.PUBLISHED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Job posting is already published",
                )

            if existing_job.status == JobStatus.CLOSED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
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

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to publish job posting",
                )

            return JobPublishResponse(
                job_id=job_id,
                status=JobStatus.PUBLISHED,
                published_at=published_at,
                message="Job posting published successfully",
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error publishing job: {str(e)}",
            )

    async def close_job(self, job_id: UUID, employer_id: UUID) -> JobCloseResponse:
        """Close a job (status → closed)."""
        try:
            existing_job = await self.get_job_by_id(job_id, employer_id)

            if existing_job.status == JobStatus.CLOSED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
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

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to close job posting",
                )

            return JobCloseResponse(
                job_id=job_id,
                status=JobStatus.CLOSED,
                closed_at=closed_at,
                message="Job posting closed successfully",
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
                offset, offset + filters.page_size - 1
            )

            response = query.execute()

            total = response.count if response.count else 0
            total_pages = (total + filters.page_size - 1) // filters.page_size

            jobs: List[Job] = []
            for row in response.data or []:
                emp_id = UUID(row["employer_id"])
                jobs.append(self._row_to_job(row, company_name=self._company_name_for(emp_id)))

            return JobListResponse(
                jobs=jobs,
                total=total,
                page=filters.page,
                page_size=filters.page_size,
                total_pages=total_pages,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error searching jobs: {str(e)}",
            )

    async def get_employer_jobs(
        self,
        employer_id: UUID,
        status_filter: Optional[JobStatus] = None,
        page: int = 1,
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
                offset, offset + page_size - 1
            )

            response = query.execute()

            total = response.count if response.count else 0
            total_pages = (total + page_size - 1) // page_size
            company = self._company_name_for(employer_id)

            jobs = [self._row_to_job(row, company_name=company) for row in (response.data or [])]

            return JobListResponse(
                jobs=jobs,
                total=total,
                page=page,
                page_size=page_size,
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

            return {"message": "Job posting deleted successfully", "job_id": str(job_id)}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting job: {str(e)}",
            )
