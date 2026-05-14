from typing import Optional
from fastapi import HTTPException, status
from supabase import Client

from .models import (
    JobSearchRequest,
    JobSearchResponse,
    JobSearchResult,
    CandidateFilterRequest,
    CandidateFilterResponse,
    CandidateResult,
    SortOrder,
)


class SearchService:
    """
    Search & Discovery Service
    Handles full-text job search for candidates and skill-based
    candidate filtering for employers.
    """

    def __init__(self, supabase_client: Client):
        self.db = supabase_client

    async def search_jobs(self, request: JobSearchRequest) -> JobSearchResponse:
        """
        Search published job postings using keyword and optional filters.
        Keyword matches against job title and description.
        Skills filter uses PostgreSQL array overlap.
        """
        try:
            query = self.db.table("job_postings").select("*", count="exact")

            # Only return published jobs
            query = query.eq("status", "published")

            # Keyword: match title OR description (case-insensitive)
            if request.keyword:
                kw = request.keyword.strip()
                query = query.or_(
                    f"title.ilike.%{kw}%,description.ilike.%{kw}%"
                )

            # Location filter
            if request.location:
                query = query.ilike("location", f"%{request.location.strip()}%")

            # Work mode filter
            if request.work_mode:
                query = query.eq("work_mode", request.work_mode.lower())

            # Education level filter
            if request.education_level:
                query = query.eq("education_level", request.education_level.lower())

            # Experience level filter
            if request.experience_level:
                query = query.eq("experience_level", request.experience_level.lower())

            # Skills: job must contain at least one of the requested skills
            if request.skills:
                skills_lower = [s.strip().lower() for s in request.skills if s.strip()]
                if skills_lower:
                    # PostgreSQL array overlap: required_skills && ARRAY[...]
                    query = query.filter(
                        "required_skills", "cs", f'{{{",".join(skills_lower)}}}'
                    )

            # Salary range filters
            if request.min_salary is not None:
                query = query.gte("salary_max", request.min_salary)
            if request.max_salary is not None:
                query = query.lte("salary_min", request.max_salary)

            # Sort order
            if request.sort_by == SortOrder.NEWEST:
                query = query.order("published_at", desc=True)
            elif request.sort_by == SortOrder.OLDEST:
                query = query.order("published_at", desc=False)
            else:
                # RELEVANCE: fall back to newest for now
                # TODO: integrate vector similarity ranking via JobBERT-v2
                query = query.order("published_at", desc=True)

            # Pagination
            offset = (request.page - 1) * request.page_size
            query = query.range(offset, offset + request.page_size - 1)

            response = query.execute()

            total = response.count or 0
            total_pages = max(1, (total + request.page_size - 1) // request.page_size)

            results = [
                JobSearchResult(
                    job_id=str(job["job_id"]),
                    title=job["title"],
                    company_name=job["company_name"],
                    location=job["location"],
                    work_mode=job["work_mode"],
                    required_skills=job.get("required_skills", []),
                    education_level=job.get("education_level"),
                    experience_level=job.get("experience_level"),
                    salary_min=job.get("salary_min"),
                    salary_max=job.get("salary_max"),
                    published_at=str(job.get("published_at", "")),
                    views_count=job.get("views_count", 0),
                    applications_count=job.get("applications_count", 0),
                )
                for job in (response.data or [])
            ]

            return JobSearchResponse(
                results=results,
                total=total,
                page=request.page,
                page_size=request.page_size,
                total_pages=total_pages,
                keyword_used=request.keyword,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Job search failed: {str(e)}",
            )

    async def filter_candidates(
        self, request: CandidateFilterRequest
    ) -> CandidateFilterResponse:
        """
        Filter candidate profiles for employers.
        Supports skill tag matching, education, major, GPA, and location.
        Returns only candidates with completed profiles.
        """
        try:
            query = self.db.table("candidate_profiles").select("*", count="exact")

            # Only surface completed profiles to employers
            query = query.gte("profile_completeness", 80)

            filters_applied = []

            # Skill tags: candidate must have at least one matching skill
            if request.skill_tags:
                tags_lower = [s.strip().lower() for s in request.skill_tags if s.strip()]
                if tags_lower:
                    query = query.filter(
                        "skills", "cs", f'{{{",".join(tags_lower)}}}'
                    )
                    filters_applied.append(f"skills: {', '.join(tags_lower)}")

            # Education level
            if request.education_level:
                query = query.eq("education_level", request.education_level.lower())
                filters_applied.append(f"education: {request.education_level}")

            # Major / field of study
            if request.major:
                query = query.ilike("major", f"%{request.major.strip()}%")
                filters_applied.append(f"major: {request.major}")

            # Minimum GPA
            if request.min_gpa is not None:
                query = query.gte("gpa", request.min_gpa)
                filters_applied.append(f"min GPA: {request.min_gpa}")

            # Location
            if request.location:
                query = query.ilike("location", f"%{request.location.strip()}%")
                filters_applied.append(f"location: {request.location}")

            # Availability type (internship / full-time / part-time)
            if request.available_for:
                query = query.eq("available_for", request.available_for.lower())
                filters_applied.append(f"available for: {request.available_for}")

            # Sort order
            if request.sort_by == SortOrder.RELEVANCE:
                query = query.order("profile_completeness", desc=True)
            elif request.sort_by == SortOrder.NEWEST:
                query = query.order("created_at", desc=True)
            else:
                query = query.order("created_at", desc=False)

            # Pagination
            offset = (request.page - 1) * request.page_size
            query = query.range(offset, offset + request.page_size - 1)

            response = query.execute()

            total = response.count or 0
            total_pages = max(1, (total + request.page_size - 1) // request.page_size)

            results = [
                CandidateResult(
                    candidate_id=str(c["id"]),
                    full_name=c.get("full_name", ""),
                    major=c.get("major"),
                    education_level=c.get("education_level"),
                    skills=c.get("skills", []),
                    location=c.get("location"),
                    gpa=c.get("gpa"),
                    profile_completeness=c.get("profile_completeness"),
                    has_github=bool(c.get("github_url")),
                    available_for=c.get("available_for"),
                )
                for c in (response.data or [])
            ]

            return CandidateFilterResponse(
                results=results,
                total=total,
                page=request.page,
                page_size=request.page_size,
                total_pages=total_pages,
                filters_applied=filters_applied,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Candidate filter failed: {str(e)}",
            )
