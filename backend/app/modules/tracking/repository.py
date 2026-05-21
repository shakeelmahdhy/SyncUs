"""
Tracking repository — Supabase data access for `public.applications`.

Layering: this module is the only place that talks to Supabase for the
tracking module. Services call these functions; routers never call
repositories directly.

Authorization rule (Option A): every owner-sensitive function takes
`user_id: UUID` (= verified `sub` from the JWT) and scopes the SQL with
`job_seeker_id = user_id`. The server uses the SECRET key, which bypasses
RLS, so this scoping is the ONLY thing protecting per-user data here.

`select_applications_for_job` is the lone exception — it does not take a
`user_id` because the access rule (typically: "only the employer of the
job") is a business decision and belongs in the service layer. Callers
must authorize before invoking it.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.supabase_client import get_supabase_service_client

from .model import ApplicationRow
from .schema import ApplicationStatus

_TABLE = "applications"


def insert_application(
    user_id: UUID,
    job_id: UUID,
    resume_id: UUID | None,
) -> ApplicationRow:
    """
    Insert a new application owned by `user_id`.

    Sets `job_seeker_id = user_id` server-side; the request body cannot
    override ownership because this function never accepts a job_seeker_id
    parameter.

    Returns the inserted row.

    Raises:
        RuntimeError: if Supabase did not return the inserted row.
    """
    client = get_supabase_service_client()

    payload: dict[str, Any] = {
        "job_id": str(job_id),
        "job_seeker_id": str(user_id),
    }
    if resume_id is not None:
        payload["resume_id"] = str(resume_id)

    response = client.table(_TABLE).insert(payload).execute()
    rows = response.data or []
    if not rows:
        raise RuntimeError("Insert into applications returned no rows")
    return rows[0]  # type: ignore[return-value]


def select_applications_by_user(user_id: UUID) -> list[ApplicationRow]:
    """
    Return all applications where `job_seeker_id = user_id`.

    Empty list (not None) when the user has no applications yet.
    """
    client = get_supabase_service_client()
    response = (
        client.table(_TABLE)
        .select("*")
        .eq("job_seeker_id", str(user_id))
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []  # type: ignore[return-value]


def select_application_for_user(
    application_id: UUID,
    user_id: UUID,
) -> ApplicationRow | None:
    """
    Return the application iff it belongs to `user_id`.

    Returns `None` (no exception) when the row does not exist or the user
    does not own it. The service decides whether `None` becomes 404 or 403.
    """
    client = get_supabase_service_client()
    response = (
        client.table(_TABLE)
        .select("*")
        .eq("id", str(application_id))
        .eq("job_seeker_id", str(user_id))
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None  # type: ignore[return-value]


def select_application_by_id(application_id: UUID) -> ApplicationRow | None:
    """Return one application row by id without applying owner rules."""
    client = get_supabase_service_client()
    response = (
        client.table(_TABLE)
        .select("*")
        .eq("id", str(application_id))
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None  # type: ignore[return-value]


def update_application_status_for_user(
    application_id: UUID,
    user_id: UUID,
    new_status: ApplicationStatus,
) -> ApplicationRow | None:
    """
    Update `status` for the application iff it belongs to `user_id`.

    Workflow rules (e.g. legal status transitions) are NOT enforced here;
    they belong to the service. This function only enforces ownership and
    persistence.

    Returns the updated row, or `None` if no matching row was found.
    """
    client = get_supabase_service_client()
    response = (
        client.table(_TABLE)
        .update({"status": new_status})
        .eq("id", str(application_id))
        .eq("job_seeker_id", str(user_id))
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None  # type: ignore[return-value]


def update_application_status_by_id(
    application_id: UUID,
    new_status: ApplicationStatus,
) -> ApplicationRow | None:
    """Update application status after service-layer authorization."""
    client = get_supabase_service_client()
    response = (
        client.table(_TABLE)
        .update({"status": new_status})
        .eq("id", str(application_id))
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None  # type: ignore[return-value]


def select_job_employer_id(job_id: UUID) -> UUID | None:
    """
    Return ``employer_id`` for a row in ``public.jobs``, or ``None`` if missing.

    Used by the service layer to authorize pipeline reads before calling
    ``select_applications_for_job``.
    """
    client = get_supabase_service_client()
    response = (
        client.table("jobs")
        .select("employer_id")
        .eq("id", str(job_id))
        .limit(1)
        .execute()
    )
    rows = response.data or []
    if not rows or rows[0].get("employer_id") is None:
        return None
    return UUID(rows[0]["employer_id"])


def select_applications_for_job(job_id: UUID) -> list[ApplicationRow]:
    """
    Return all applications for `job_id`.

    NOTE: this function does NOT check the caller's identity. It backs the
    job pipeline endpoint, which must be authorized by the service layer
    (typically: only the employer that owns the job may view the pipeline).
    Do not expose this directly from a router.
    """
    client = get_supabase_service_client()
    response = (
        client.table(_TABLE)
        .select("*")
        .eq("job_id", str(job_id))
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []  # type: ignore[return-value]
