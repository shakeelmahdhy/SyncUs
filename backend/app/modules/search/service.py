from typing import Optional

from fastapi import HTTPException, status
from supabase import Client

from .mapping import JOBS_TABLE, row_to_search_result
from .models import (
    CandidateFilterRequest,
    CandidateFilterResponse,
    CandidateResult,
    JobSearchRequest,
    JobSearchResponse,
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

    def _company_name_for(self, employer_id: str) -> str:
        """Load display company name from ``employers`` when available."""
        response = (
            self.db.table("employers")
            .select("company_name")
            .eq("id", employer_id)
            .limit(1)
            .execute()
        )
        if response.data and response.data[0].get("company_name"):
            return response.data[0]["company_name"]
        return "Employer"

    async def search_jobs(self, request: JobSearchRequest) -> JobSearchResponse:
        """
        Search published jobs in ``public.jobs`` using keyword and optional filters.
        Keyword matches title and description. Skills use array overlap.
        """
        try:
            query = self.db.table(JOBS_TABLE).select("*", count="exact")
            query = query.eq("status", "published")

            if request.keyword:
                kw = request.keyword.strip()
                query = query.or_(
                    f"title.ilike.%{kw}%,description.ilike.%{kw}%"
                )

            if request.location:
                query = query.ilike("location", f"%{request.location.strip()}%")

            if request.work_mode:
                query = query.eq("work_mode", request.work_mode.lower())

            # education_level, experience_level, salary: not on public.jobs yet — ignored

            if request.skills:
                skills_lower = [s.strip().lower() for s in request.skills if s.strip()]
                if skills_lower:
                    query = query.filter(
                        "required_skills", "cs", f'{{{",".join(skills_lower)}}}'
                    )

            if request.sort_by == SortOrder.OLDEST:
                query = query.order("created_at", desc=False)
            else:
                # NEWEST and RELEVANCE: sort by created_at until vector ranking exists
                query = query.order("created_at", desc=True)

            offset = (request.page - 1) * request.page_size
            query = query.range(offset, offset + request.page_size - 1)

            response = query.execute()

            total = response.count or 0
            total_pages = max(1, (total + request.page_size - 1) // request.page_size)

            company_cache: dict[str, str] = {}
            results = []
            for row in response.data or []:
                eid = str(row["employer_id"])
                if eid not in company_cache:
                    company_cache[eid] = self._company_name_for(eid)
                results.append(
                    row_to_search_result(row, company_name=company_cache[eid])
                )

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

            query = query.gte("profile_completeness", 80)

            filters_applied = []

            if request.skill_tags:
                tags_lower = [s.strip().lower() for s in request.skill_tags if s.strip()]
                if tags_lower:
                    query = query.filter(
                        "skills", "cs", f'{{{",".join(tags_lower)}}}'
                    )
                    filters_applied.append(f"skills: {', '.join(tags_lower)}")

            if request.education_level:
                query = query.eq("education_level", request.education_level.lower())
                filters_applied.append(f"education: {request.education_level}")

            if request.major:
                query = query.ilike("major", f"%{request.major.strip()}%")
                filters_applied.append(f"major: {request.major}")

            if request.min_gpa is not None:
                query = query.gte("gpa", request.min_gpa)
                filters_applied.append(f"min GPA: {request.min_gpa}")

            if request.location:
                query = query.ilike("location", f"%{request.location.strip()}%")
                filters_applied.append(f"location: {request.location}")

            if request.available_for:
                query = query.eq("available_for", request.available_for.lower())
                filters_applied.append(f"available for: {request.available_for}")

            if request.sort_by == SortOrder.RELEVANCE:
                query = query.order("profile_completeness", desc=True)
            elif request.sort_by == SortOrder.NEWEST:
                query = query.order("created_at", desc=True)
            else:
                query = query.order("created_at", desc=False)

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
