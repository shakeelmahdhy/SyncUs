"""
Map between ``public.jobs`` rows and jobs API Pydantic models.

The canonical table is ``public.jobs`` (see ``supabase/migrations``). Columns:
id, employer_id, title, description, required_skills, location, work_mode,
experience_required, status, created_at.

API models may include extra fields (salary, company_name on the job DTO, etc.);
those are filled with defaults or loaded from ``employers`` where noted.
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


def job_create_to_row(job_data: JobCreate, employer_id: UUID) -> dict[str, Any]:
    """Build insert payload for ``public.jobs`` from API create body."""
    work_mode = job_data.work_mode
    if isinstance(work_mode, WorkMode):
        work_mode = work_mode.value

    experience = job_data.min_years_experience
    if experience is None:
        experience = 0

    return {
        "employer_id": str(employer_id),
        "title": job_data.title,
        "description": job_data.description,
        "required_skills": job_data.required_skills,
        "location": job_data.location,
        "work_mode": work_mode,
        "experience_required": experience,
        "status": JobStatus.DRAFT.value,
    }


def job_update_to_row(job_data: JobUpdate) -> dict[str, Any]:
    """Build update payload for ``public.jobs`` (only columns that exist)."""
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
        wm = data["work_mode"]
        patch["work_mode"] = wm.value if isinstance(wm, WorkMode) else wm
    if "min_years_experience" in data:
        patch["experience_required"] = data["min_years_experience"]

    return patch


def row_to_job(row: dict[str, Any], *, company_name: str = "Employer") -> Job:
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

    return Job(
        job_id=UUID(row["id"]),
        employer_id=UUID(row["employer_id"]),
        title=row["title"],
        company_name=company_name,
        description=row["description"],
        required_skills=row.get("required_skills") or [],
        location=row.get("location") or "",
        work_mode=work_mode,
        education_level=EducationLevel.ANY,
        experience_level=ExperienceLevel.ANY,
        min_years_experience=row.get("experience_required"),
        max_years_experience=None,
        salary_min=None,
        salary_max=None,
        contact_email="noreply@syncus.local",
        website=None,
        status=status,
        views_count=0,
        applications_count=0,
        created_at=created,
        updated_at=created,
        published_at=published_at,
        closed_at=closed_at,
    )
