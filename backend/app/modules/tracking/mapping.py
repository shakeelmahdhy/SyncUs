"""
Map Supabase `applications` rows to API Pydantic models.

Supabase returns UUIDs and timestamps as strings; this module normalizes them.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from .model import ApplicationRow
from .schema import ApplicationResponse


def _parse_timestamptz(value: str) -> datetime:
    """Parse Postgres `timestamptz` strings returned by the Supabase client."""
    normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def application_row_to_response(row: ApplicationRow) -> ApplicationResponse:
    """Build `ApplicationResponse` from a repository `ApplicationRow`."""
    raw_resume = row.get("resume_id")
    resume_id: UUID | None = (
        None if raw_resume is None or raw_resume == "" else UUID(raw_resume)
    )

    return ApplicationResponse(
        id=UUID(row["id"]),
        job_id=UUID(row["job_id"]),
        job_seeker_id=UUID(row["job_seeker_id"]),
        resume_id=resume_id,
        status=row["status"],
        created_at=_parse_timestamptz(row["created_at"]),
    )
