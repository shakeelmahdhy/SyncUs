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

    def _candidate_skills(self, candidate_id: str) -> list[str]:
        joins = (
            self.db.table("job_seeker_skills")
            .select("skill_id")
            .eq("job_seeker_id", candidate_id)
            .execute()
        )
        skill_ids = [row["skill_id"] for row in (joins.data or []) if row.get("skill_id")]
        if not skill_ids:
            return []

        skills = self.db.table("skills").select("name").in_("id", skill_ids).execute()
        return [row["name"] for row in (skills.data or []) if row.get("name")]

    def _profile_completeness(self, candidate: dict, skills: list[str]) -> int:
        fields = [
            candidate.get("first_name"),
            candidate.get("last_name"),
            candidate.get("education"),
            candidate.get("major"),
            candidate.get("years_of_experience"),
            candidate.get("academic_units"),
            skills,
        ]
        completed = sum(1 for value in fields if value not in (None, "", [], {}))
        return round((completed / len(fields)) * 100)

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
        Filter candidate profiles for employers using contract tables:
        ``job_seekers``, ``job_seeker_skills``, and ``skills``.
        """
        try:
            query = self.db.table("job_seekers").select(
                "id, first_name, last_name, education, major, years_of_experience, academic_units, is_active, created_at",
                count="exact",
            )

            filters_applied = []

            if request.education_level:
                query = query.ilike("education", f"%{request.education_level.strip()}%")
                filters_applied.append(f"education: {request.education_level}")

            if request.major:
                query = query.ilike("major", f"%{request.major.strip()}%")
                filters_applied.append(f"major: {request.major}")

            if request.min_gpa is not None:
                filters_applied.append("min GPA ignored: no GPA column in job_seekers")

            if request.location:
                filters_applied.append("location ignored: no location column in job_seekers")

            if request.available_for:
                filters_applied.append("availability ignored: no availability column in job_seekers")

            if request.sort_by == SortOrder.NEWEST:
                query = query.order("created_at", desc=True)
            elif request.sort_by == SortOrder.OLDEST:
                query = query.order("created_at", desc=False)

            response = query.execute()

            tag_filters = [s.strip().lower() for s in (request.skill_tags or []) if s.strip()]
            if tag_filters:
                filters_applied.append(f"skills: {', '.join(tag_filters)}")

            candidates: list[CandidateResult] = []
            for candidate in response.data or []:
                skills = self._candidate_skills(str(candidate["id"]))
                skill_text = {skill.lower() for skill in skills}
                if tag_filters and not any(tag in skill_text for tag in tag_filters):
                    continue

                completeness = self._profile_completeness(candidate, skills)
                candidates.append(
                    CandidateResult(
                        candidate_id=str(candidate["id"]),
                        full_name=(
                            f"{candidate.get('first_name') or ''} {candidate.get('last_name') or ''}"
                        ).strip(),
                        major=candidate.get("major"),
                        education_level=candidate.get("education"),
                        skills=skills,
                        location=None,
                        gpa=None,
                        profile_completeness=completeness,
                        has_github=False,
                        available_for=None,
                    )
                )

            if request.sort_by == SortOrder.RELEVANCE:
                candidates.sort(key=lambda item: item.profile_completeness or 0, reverse=True)

            total = len(candidates)
            total_pages = max(1, (total + request.page_size - 1) // request.page_size)
            offset = (request.page - 1) * request.page_size
            results = candidates[offset : offset + request.page_size]

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
