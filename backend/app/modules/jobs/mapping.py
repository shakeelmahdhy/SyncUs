"""
Map between ``public.jobs`` rows and jobs API Pydantic models.

The canonical table is ``public.jobs`` (see ``supabase/migrations``).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from .models import (
    EducationLevel,
    ExperienceLevel,
    Job,
    JobCreate,
    JobStatus,
    JobUpdate,
    WorkMode,
)

JOBS_TABLE = "jobs"


def _parse_ts(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _parse_education(raw: Any) -> EducationLevel:
    try:
        return EducationLevel(raw or EducationLevel.ANY.value)
    except ValueError:
        return EducationLevel.ANY


def _parse_experience_level(raw: Any) -> ExperienceLevel:
    try:
        return ExperienceLevel(raw or ExperienceLevel.ANY.value)
    except ValueError:
        return ExperienceLevel.ANY


def job_create_to_row(job_data: JobCreate, employer_id: UUID) -> dict[str, Any]:
    """Build insert payload for ``public.jobs`` from API create body."""
    work_mode = _enum_value(job_data.work_mode)
    experience = job_data.min_years_experience
    if experience is None:
        experience = 0

    row: dict[str, Any] = {
        "employer_id": str(employer_id),
        "title": job_data.title,
        "description": job_data.description,
        "required_skills": job_data.required_skills,
        "location": job_data.location,
        "work_mode": work_mode,
        "experience_required": experience,
        "education_level": _enum_value(job_data.education_level),
        "experience_level": _enum_value(job_data.experience_level),
        "max_years_experience": job_data.max_years_experience,
        "salary_min": job_data.salary_min,
        "salary_max": job_data.salary_max,
        "contact_email": job_data.contact_email,
        "website": job_data.website,
        "status": JobStatus.DRAFT.value,
    }
    return row


def job_update_to_row(job_data: JobUpdate) -> dict[str, Any]:
    """Build update payload for ``public.jobs``."""
    data = job_data.dict(exclude_none=True)
    patch: dict[str, Any] = {}

    if "title" in data:
        patch["title"] = data["title"]
    if "description" in data:
        patch["description"] = data["description"]
    if "required_skills" in data:
        patch["required_skills"] = data["required_skills"]
    if "location" in data:
        patch["location"] = data["location"]
    if "work_mode" in data:
        patch["work_mode"] = _enum_value(data["work_mode"])
    if "min_years_experience" in data:
        patch["experience_required"] = data["min_years_experience"]
    if "max_years_experience" in data:
        patch["max_years_experience"] = data["max_years_experience"]
    if "education_level" in data:
        patch["education_level"] = _enum_value(data["education_level"])
    if "experience_level" in data:
        patch["experience_level"] = _enum_value(data["experience_level"])
    if "salary_min" in data:
        patch["salary_min"] = data["salary_min"]
    if "salary_max" in data:
        patch["salary_max"] = data["salary_max"]
    if "contact_email" in data:
        patch["contact_email"] = data["contact_email"]
    if "website" in data:
        patch["website"] = data["website"]

    return patch


def row_to_job(
    row: dict[str, Any],
    *,
    company_name: str = "Employer",
    applications_count: int | None = None,
) -> Job:
    """Build API ``Job`` from a ``public.jobs`` row."""
    created = _parse_ts(row.get("created_at"))
    status_raw = row.get("status") or JobStatus.DRAFT.value
    status = JobStatus(status_raw)

    work_mode_raw = row.get("work_mode") or WorkMode.REMOTE.value
    try:
        work_mode = WorkMode(work_mode_raw)
    except ValueError:
        work_mode = WorkMode.REMOTE

    published_at = created if status == JobStatus.PUBLISHED else None
    closed_at = created if status == JobStatus.CLOSED else None

    min_years = row.get("experience_required")
    if min_years is None and row.get("min_years_experience") is not None:
        min_years = row.get("min_years_experience")

    return Job(
        job_id=UUID(row["id"]),
        employer_id=UUID(row["employer_id"]),
        title=row["title"],
        company_name=company_name,
        description=row["description"],
        required_skills=row.get("required_skills") or [],
        location=row.get("location") or "",
        work_mode=work_mode,
        education_level=_parse_education(row.get("education_level")),
        experience_level=_parse_experience_level(row.get("experience_level")),
        min_years_experience=min_years,
        max_years_experience=row.get("max_years_experience"),
        salary_min=row.get("salary_min"),
        salary_max=row.get("salary_max"),
        contact_email=row.get("contact_email") or "noreply@syncus.local",
        website=row.get("website"),
        status=status,
        views_count=int(row.get("views_count") or 0),
        applications_count=(
            applications_count
            if applications_count is not None
            else int(row.get("applications_count") or 0)
        ),
        created_at=created,
        updated_at=_parse_ts(row.get("updated_at")) if row.get("updated_at") else created,
        published_at=published_at,
        closed_at=closed_at,
    )
