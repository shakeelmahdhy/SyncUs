"""
Map ``public.jobs`` (+ ``employers``) rows to search API results.
"""

from __future__ import annotations

from typing import Any

from app.modules.jobs.mapping import JOBS_TABLE

from .models import JobSearchResult

__all__ = ["JOBS_TABLE", "row_to_search_result"]


def row_to_search_result(
    row: dict[str, Any], *, company_name: str = "Employer"
) -> JobSearchResult:
    """Build ``JobSearchResult`` from a ``public.jobs`` row."""
    created = row.get("created_at")
    published_at = str(created) if row.get("status") == "published" and created else None

    return JobSearchResult(
        job_id=str(row["id"]),
        title=row["title"],
        company_name=company_name,
        location=row.get("location") or "",
        work_mode=row.get("work_mode") or "",
        required_skills=row.get("required_skills") or [],
        education_level=None,
        experience_level=None,
        salary_min=None,
        salary_max=None,
        published_at=published_at,
        views_count=0,
        applications_count=0,
    )
