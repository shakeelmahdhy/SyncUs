"""
Internal row types for the tracking module.

These types describe rows from `public.applications` as returned by the
Supabase Python client. They are intentionally not Pydantic models — the
repository should not depend on API schemas. Pydantic conversion happens
at the service/router boundary using `ApplicationResponse(**row)`.
"""

from __future__ import annotations

from typing import TypedDict

from .schema import ApplicationStatus


class ApplicationRow(TypedDict):
    """A row from `public.applications` (UUIDs and timestamps as strings)."""

    id: str
    job_id: str
    job_seeker_id: str
    resume_id: str | None
    status: ApplicationStatus
    created_at: str
