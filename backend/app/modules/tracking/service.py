from datetime import datetime, UTC
from uuid import UUID, uuid4

from .mapping import application_row_to_response
from .repository import (
    insert_application,
    select_application_for_user,
    select_applications_by_user,
)
from .schema import (
    ApplicationCreateRequest,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationStatus,
)


def _base_application(job_id: UUID, status: ApplicationStatus = "applied") -> dict:
    return {
        "id": uuid4(),
        "job_id": job_id,
        "job_seeker_id": uuid4(),
        "resume_id": None,
        "status": status,
        "created_at": datetime.now(UTC),
    }


def create_application(
    user_id: UUID, payload: ApplicationCreateRequest
) -> ApplicationResponse:
    """Create a new application for ``user_id`` and return the persisted row as ``ApplicationResponse``."""
    row = insert_application(user_id, payload.job_id, payload.resume_id)
    return application_row_to_response(row)


def list_applications(user_id: UUID) -> ApplicationListResponse:
    """Return all applications for ``user_id``, newest ``created_at`` first."""
    rows = select_applications_by_user(user_id)
    items = [application_row_to_response(r) for r in rows]
    return ApplicationListResponse(items=items, total=len(items))


def get_application(
    user_id: UUID, application_id: UUID
) -> ApplicationResponse | None:
    """
    Return the application if it exists and ``job_seeker_id == user_id``.

    Returns ``None`` when the row is missing or not owned by ``user_id``;
    the router maps that to an HTTP 404.
    """
    row = select_application_for_user(application_id, user_id)
    if row is None:
        return None
    return application_row_to_response(row)


def update_application_status(
    application_id: UUID, status: ApplicationStatus
) -> dict:
    return {
        "id": application_id,
        "status": status,
        "updated_at": datetime.now(UTC),
    }


def get_job_pipeline(job_id: UUID) -> dict:
    return {
        "job_id": job_id,
        "applications": [],
    }
