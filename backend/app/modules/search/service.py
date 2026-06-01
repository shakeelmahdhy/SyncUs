from __future__ import annotations

import re
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any

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


TOKEN_PATTERN = re.compile(r"[a-z0-9+#.]+")

RELATED_TERMS: dict[str, tuple[str, ...]] = {
    "software": ("developer", "engineer", "programmer", "coder", "coding", "web", "application"),
    "engineer": ("developer", "programmer", "coder", "software", "engineering"),
    "developer": ("engineer", "programmer", "coder", "software"),
    "programmer": ("software", "engineer", "developer", "coder"),
    "coder": ("software", "engineer", "developer", "programmer"),
    "coding": ("software", "engineer", "developer", "programmer"),
    "frontend": ("front", "react", "typescript", "javascript", "web"),
    "front": ("frontend", "react", "typescript", "javascript", "web"),
    "backend": ("back", "api", "python", "fastapi", "node"),
    "analyst": ("analytics", "data", "sql", "reporting", "insights"),
    "analysis": ("analyst", "analytics", "data", "sql", "insights"),
    "remote": ("workfromhome", "wfh", "distributed"),
    "onsite": ("on-site", "office"),
    "hybrid": ("flexible",),
}

PHRASE_ALIASES: dict[str, tuple[str, ...]] = {
    "software engineer": ("software developer", "programmer", "coder", "developer"),
    "data analyst": ("analytics analyst", "business intelligence", "bi analyst", "sql analyst"),
    "entry level": ("entry-level", "entry", "junior", "graduate"),
    "full time": ("full-time", "fulltime", "permanent"),
    "on site": ("on-site", "onsite", "office"),
}

WORK_MODE_ALIASES = {
    "remote": "remote",
    "workfromhome": "remote",
    "wfh": "remote",
    "onsite": "onsite",
    "on-site": "onsite",
    "on site": "onsite",
    "office": "onsite",
    "hybrid": "hybrid",
    "flexible": "hybrid",
}

EXPERIENCE_ALIASES = {
    "entry": "entry",
    "entrylevel": "entry",
    "entry-level": "entry",
    "graduate": "entry",
    "junior": "junior",
    "mid": "mid",
    "midlevel": "mid",
    "mid-level": "mid",
    "senior": "senior",
    "lead": "lead",
    "any": "any",
}

FULL_TIME_TERMS = {"fulltime", "full-time", "full time", "permanent"}


class SearchService:
    """
    Search & Discovery Service
    Handles full-text job search for candidates and skill-based
    candidate filtering for employers.
    """

    def __init__(self, supabase_client: Client):
        self.db = supabase_client

    def _employer_profile_for(self, employer_id: str) -> dict[str, str]:
        """Load employer search/display fields from ``employers`` when available."""
        response = (
            self.db.table("employers")
            .select("company_name, company_description, industry")
            .eq("id", employer_id)
            .limit(1)
            .execute()
        )
        row = response.data[0] if response.data else {}
        return {
            "company_name": row.get("company_name") or "Employer",
            "company_description": row.get("company_description") or "",
            "industry": row.get("industry") or "",
        }

    def _company_name_for(self, employer_id: str) -> str:
        """Load display company name from ``employers`` when available."""
        return self._employer_profile_for(employer_id)["company_name"]

    def _safe_list(self, value: Any) -> list[str]:
        if not value:
            return []
        if isinstance(value, (list, tuple, set)):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
            return [item.strip().strip('"') for item in value[1:-1].split(",") if item.strip()]
        return [str(value).strip()]

    def _normalise_text(self, value: Any) -> str:
        text = str(value or "").casefold()
        return " ".join(TOKEN_PATTERN.findall(text.replace("-", " ")))

    def _tokens(self, value: Any) -> set[str]:
        return set(TOKEN_PATTERN.findall(self._normalise_text(value)))

    def _normalise_filter(self, value: str | None) -> str | None:
        if not value:
            return None
        return self._normalise_text(value).replace(" ", "")

    def _normalise_work_mode(self, value: str | None) -> str | None:
        if not value:
            return None
        compact = self._normalise_filter(value)
        spaced = self._normalise_text(value)
        return WORK_MODE_ALIASES.get(compact or "") or WORK_MODE_ALIASES.get(spaced)

    def _normalise_experience(self, value: str | None) -> str | None:
        if not value:
            return None
        compact = self._normalise_filter(value)
        spaced = self._normalise_text(value)
        return EXPERIENCE_ALIASES.get(compact or "") or EXPERIENCE_ALIASES.get(spaced) or compact

    def _expanded_query_terms(self, keyword: str | None) -> set[str]:
        if not keyword:
            return set()

        normalised = self._normalise_text(keyword)
        terms = self._tokens(normalised)

        for phrase, aliases in PHRASE_ALIASES.items():
            if phrase in normalised or SequenceMatcher(None, normalised, phrase).ratio() >= 0.78:
                terms.update(self._tokens(phrase))
                for alias in aliases:
                    terms.update(self._tokens(alias))

        for token in list(terms):
            terms.update(RELATED_TERMS.get(token, ()))

        return terms

    def _job_search_parts(self, row: dict[str, Any], employer: dict[str, str]) -> list[str]:
        skills = self._safe_list(row.get("required_skills"))
        min_years = row.get("experience_required") or row.get("min_years_experience")
        max_years = row.get("max_years_experience")
        experience_parts = [
            str(row.get("experience_level") or ""),
            f"{min_years} years" if min_years is not None else "",
            f"{min_years}-{max_years} years" if min_years is not None and max_years is not None else "",
        ]
        return [
            row.get("title") or "",
            row.get("description") or "",
            " ".join(skills),
            row.get("location") or "",
            row.get("work_mode") or "",
            row.get("education_level") or "",
            *experience_parts,
            employer.get("company_name") or "",
            employer.get("company_description") or "",
            employer.get("industry") or "",
            "full time full-time permanent",
        ]

    def _passes_job_filters(
        self,
        row: dict[str, Any],
        employer: dict[str, str],
        request: JobSearchRequest,
    ) -> bool:
        if request.location:
            location_query = self._normalise_text(request.location)
            location_text = self._normalise_text(row.get("location"))
            if location_query not in location_text:
                return False

        expected_work_mode = self._normalise_work_mode(request.work_mode)
        if expected_work_mode and self._normalise_work_mode(row.get("work_mode")) != expected_work_mode:
            return False

        employment_type = self._normalise_filter(request.employment_type)
        if employment_type and employment_type not in {term.replace(" ", "") for term in FULL_TIME_TERMS}:
            row_type = self._normalise_filter(row.get("employment_type") or row.get("job_type"))
            if row_type != employment_type:
                return False

        expected_experience = self._normalise_experience(request.experience_level)
        if expected_experience and expected_experience != "any":
            row_experience = self._normalise_experience(row.get("experience_level"))
            if row_experience != expected_experience:
                return False

        if request.education_level:
            expected_education = self._normalise_filter(request.education_level)
            row_education = self._normalise_filter(row.get("education_level"))
            if expected_education and row_education not in {expected_education, "any"}:
                return False

        if request.min_salary is not None:
            salary_max = row.get("salary_max")
            salary_min = row.get("salary_min")
            if salary_max is not None and int(salary_max) < request.min_salary:
                return False
            if salary_max is None and salary_min is not None and int(salary_min) < request.min_salary:
                return False

        if request.max_salary is not None:
            salary_min = row.get("salary_min")
            if salary_min is not None and int(salary_min) > request.max_salary:
                return False

        if request.skills:
            required = {self._normalise_filter(skill) for skill in self._safe_list(row.get("required_skills"))}
            requested = {self._normalise_filter(skill) for skill in request.skills if skill.strip()}
            if requested and not (required & requested):
                return False

        return True

    def _created_at(self, row: dict[str, Any]) -> datetime:
        raw = row.get("created_at")
        if not raw:
            return datetime.min.replace(tzinfo=timezone.utc)
        try:
            normalized = str(raw).replace("Z", "+00:00")
            parsed = datetime.fromisoformat(normalized)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return datetime.min.replace(tzinfo=timezone.utc)

    def _keyword_score(self, row: dict[str, Any], employer: dict[str, str], keyword: str | None) -> float:
        if not keyword or not keyword.strip():
            return 0.0

        normalised_query = self._normalise_text(keyword)
        query_terms = self._expanded_query_terms(keyword)
        parts = self._job_search_parts(row, employer)
        haystack = self._normalise_text(" ".join(parts))
        title = self._normalise_text(row.get("title"))
        description = self._normalise_text(row.get("description"))
        skills = self._normalise_text(" ".join(self._safe_list(row.get("required_skills"))))
        employer_text = self._normalise_text(
            " ".join([employer.get("company_name", ""), employer.get("company_description", ""), employer.get("industry", "")])
        )
        haystack_terms = self._tokens(haystack)

        score = 0.0
        if normalised_query and normalised_query in title:
            score += 120
        if normalised_query and normalised_query in skills:
            score += 90
        if normalised_query and normalised_query in description:
            score += 70
        if normalised_query and normalised_query in employer_text:
            score += 35
        if query_terms and query_terms <= haystack_terms:
            score += 45

        overlap = query_terms & haystack_terms
        if query_terms:
            score += (len(overlap) / len(query_terms)) * 60

        title_ratio = SequenceMatcher(None, normalised_query, title).ratio() if title else 0.0
        best_part_ratio = max((SequenceMatcher(None, normalised_query, self._normalise_text(part)).ratio() for part in parts if part), default=0.0)
        best_token_ratio = max(
            (
                SequenceMatcher(None, term, candidate).ratio()
                for term in query_terms
                for candidate in haystack_terms
            ),
            default=0.0,
        )

        if title_ratio >= 0.72:
            score += title_ratio * 95
        if best_part_ratio >= 0.78:
            score += best_part_ratio * 70
        if best_token_ratio >= 0.82:
            score += best_token_ratio * 35

        return round(score, 4)

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
            candidate.get("location"),
            candidate.get("work_mode") or candidate.get("preferred_working_mode"),
            skills,
        ]
        completed = sum(1 for value in fields if value not in (None, "", [], {}))
        return round((completed / len(fields)) * 100)

    def _candidate_search_parts(self, candidate: dict[str, Any], skills: list[str]) -> list[str]:
        return [
            candidate.get("first_name") or "",
            candidate.get("last_name") or "",
            candidate.get("education") or "",
            candidate.get("major") or "",
            str(candidate.get("years_of_experience") or ""),
            " ".join(self._safe_list(candidate.get("academic_units"))),
            candidate.get("location") or "",
            candidate.get("work_mode") or candidate.get("preferred_working_mode") or "",
            candidate.get("available_for") or "",
            candidate.get("bio") or "",
            candidate.get("title") or "",
            " ".join(skills),
        ]

    def _candidate_keyword_score(self, candidate: dict[str, Any], skills: list[str], keyword: str | None) -> float:
        if not keyword or not keyword.strip():
            return 0.0

        normalised_query = self._normalise_text(keyword)
        query_terms = self._expanded_query_terms(keyword)
        parts = self._candidate_search_parts(candidate, skills)
        haystack = self._normalise_text(" ".join(parts))
        haystack_terms = self._tokens(haystack)
        full_name = self._normalise_text(
            f"{candidate.get('first_name') or ''} {candidate.get('last_name') or ''}"
        )

        score = 0.0
        if normalised_query and normalised_query in full_name:
            score += 90
        if normalised_query and normalised_query in haystack:
            score += 50

        overlap = query_terms & haystack_terms
        if query_terms:
            score += (len(overlap) / len(query_terms)) * 55

        best_part_ratio = max(
            (SequenceMatcher(None, normalised_query, self._normalise_text(part)).ratio() for part in parts if part),
            default=0.0,
        )
        best_token_ratio = max(
            (
                SequenceMatcher(None, term, candidate_term).ratio()
                for term in query_terms
                for candidate_term in haystack_terms
            ),
            default=0.0,
        )
        if best_part_ratio >= 0.78:
            score += best_part_ratio * 60
        if best_token_ratio >= 0.82:
            score += best_token_ratio * 30

        return round(score, 4)

    async def search_jobs(self, request: JobSearchRequest) -> JobSearchResponse:
        """
        Search published jobs with keyword, filter, combined, and fuzzy relevance.
        """
        try:
            query = self.db.table(JOBS_TABLE).select("*", count="exact")
            query = query.eq("status", "published")

            if request.work_mode:
                work_mode = self._normalise_work_mode(request.work_mode)
                if work_mode:
                    query = query.eq("work_mode", work_mode)

            response = query.execute()

            company_cache: dict[str, dict[str, str]] = {}
            scored_rows: list[tuple[float, datetime, dict[str, Any], dict[str, str]]] = []
            for row in response.data or []:
                eid = str(row["employer_id"])
                if eid not in company_cache:
                    company_cache[eid] = self._employer_profile_for(eid)
                employer = company_cache[eid]
                if not self._passes_job_filters(row, employer, request):
                    continue

                score = self._keyword_score(row, employer, request.keyword)
                if request.keyword and score <= 0:
                    continue
                scored_rows.append((score, self._created_at(row), row, employer))

            should_rank_by_relevance = request.sort_by == SortOrder.RELEVANCE or bool(request.keyword)
            if should_rank_by_relevance:
                scored_rows.sort(key=lambda item: (item[0], item[1]), reverse=True)
            elif request.sort_by == SortOrder.OLDEST:
                scored_rows.sort(key=lambda item: item[1])
            else:
                scored_rows.sort(key=lambda item: item[1], reverse=True)

            total = len(scored_rows)
            total_pages = max(1, (total + request.page_size - 1) // request.page_size)
            offset = (request.page - 1) * request.page_size
            paged_rows = scored_rows[offset : offset + request.page_size]

            results = []
            for _score, _created, row, employer in paged_rows:
                results.append(
                    row_to_search_result(row, company_name=employer["company_name"])
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
            query = self.db.table("job_seekers").select("*", count="exact")

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
                filters_applied.append(f"location: {request.location}")

            if request.available_for:
                filters_applied.append(f"availability: {request.available_for}")

            if request.sort_by == SortOrder.NEWEST:
                query = query.order("created_at", desc=True)
            elif request.sort_by == SortOrder.OLDEST:
                query = query.order("created_at", desc=False)

            response = query.execute()

            tag_filters = [s.strip().lower() for s in (request.skill_tags or []) if s.strip()]
            if tag_filters:
                filters_applied.append(f"skills: {', '.join(tag_filters)}")

            scored_candidates: list[tuple[float, CandidateResult]] = []
            for candidate in response.data or []:
                skills = self._candidate_skills(str(candidate["id"]))
                skill_text = {skill.lower() for skill in skills}
                if tag_filters and not any(tag in skill_text for tag in tag_filters):
                    continue

                if request.location:
                    location = self._normalise_text(candidate.get("location"))
                    if self._normalise_text(request.location) not in location:
                        continue

                if request.available_for:
                    requested = self._normalise_filter(request.available_for)
                    availability = self._normalise_filter(
                        candidate.get("available_for")
                        or candidate.get("work_mode")
                        or candidate.get("preferred_working_mode")
                    )
                    if requested and requested != availability:
                        continue

                keyword_score = self._candidate_keyword_score(candidate, skills, request.keyword)
                if request.keyword and keyword_score <= 0:
                    continue

                completeness = self._profile_completeness(candidate, skills)
                result = CandidateResult(
                    candidate_id=str(candidate["id"]),
                    full_name=(
                        f"{candidate.get('first_name') or ''} {candidate.get('last_name') or ''}"
                    ).strip(),
                    major=candidate.get("major") or candidate.get("title"),
                    education_level=candidate.get("education"),
                    skills=skills,
                    location=candidate.get("location"),
                    gpa=candidate.get("gpa"),
                    profile_completeness=completeness,
                    has_github=bool(candidate.get("github") or candidate.get("github_url")),
                    available_for=(
                        candidate.get("available_for")
                        or candidate.get("work_mode")
                        or candidate.get("preferred_working_mode")
                    ),
                )
                scored_candidates.append((keyword_score, result))

            if request.sort_by == SortOrder.RELEVANCE:
                scored_candidates.sort(
                    key=lambda item: (item[0], item[1].profile_completeness or 0),
                    reverse=True,
                )
            candidates = [candidate for _score, candidate in scored_candidates]

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
