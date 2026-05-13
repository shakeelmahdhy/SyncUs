from datetime import datetime, UTC
from uuid import UUID, uuid4

from .mapping import application_row_to_response
from .repository import insert_application
from .schema import ApplicationCreateRequest, ApplicationResponse, ApplicationStatus


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
    """Persist a new application for ``user_id`` and return the stored row as API model."""
    row = insert_application(user_id, payload.job_id, payload.resume_id)
    return application_row_to_response(row)


def list_applications() -> dict:
    return {
        "items": [],
        "total": 0,
    }


def get_application(application_id: UUID) -> dict:
    application = _base_application(uuid4())
    application["id"] = application_id
    return application


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
