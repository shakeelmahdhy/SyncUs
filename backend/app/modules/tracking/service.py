"""
Tracking business logic.

Orchestrates repository calls, status transition rules, and API model mapping.
Routers stay thin; this module owns workflow and HTTP-oriented errors.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status

from .mapping import application_row_to_response
from .repository import (
    insert_application,
    select_application_by_id,
    select_application_by_job_and_user,
    select_application_for_user,
    select_applications_by_user,
    select_applications_for_job,
    select_job_employer_id,
    update_application_status_by_id,
    update_application_status_for_user,
)
from .schema import (
    ApplicationCreateRequest,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationStatus,
    ApplicationStatusUpdateResponse,
    JobPipelineResponse,
)
from .transitions import can_transition


def create_application(
    user_id: UUID, payload: ApplicationCreateRequest
) -> ApplicationResponse:
    """Create or return the user's existing application for the job."""
    existing = select_application_by_job_and_user(user_id, payload.job_id)
    if existing is not None:
        return application_row_to_response(existing)

    try:
        row = insert_application(user_id, payload.job_id, payload.resume_id)
    except Exception as exc:
        message = str(exc).lower()
        if "duplicate" in message or "23505" in message or "unique" in message:
            existing = select_application_by_job_and_user(user_id, payload.job_id)
            if existing is not None:
                return application_row_to_response(existing)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Application could not be submitted: {exc}",
        ) from exc
    return application_row_to_response(row)


def list_applications(user_id: UUID) -> ApplicationListResponse:
    """Return all applications for ``user_id``, newest ``created_at`` first."""
    rows = select_applications_by_user(user_id)
    items = [application_row_to_response(r) for r in rows]
    return ApplicationListResponse(items=items, total=len(items))


def get_application(user_id: UUID, application_id: UUID) -> ApplicationResponse:
    """
    Return one application when it belongs to ``user_id``.

    Raises:
        HTTPException: 404 when the row does not exist or is not owned by the user.
    """
    row = select_application_for_user(application_id, user_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return application_row_to_response(row)


def update_application_status(
    user_id: UUID,
    application_id: UUID,
    new_status: ApplicationStatus,
) -> ApplicationStatusUpdateResponse:
    """
    Update application status when ``user_id`` is the seeker that owns the
    application or the employer that owns the job.

    Raises:
        HTTPException: 404 when not found; 403 when not authorized; 400 when
        transition is invalid.
    """
    existing = select_application_by_id(application_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    is_seeker_owner = UUID(existing["job_seeker_id"]) == user_id
    employer_id = select_job_employer_id(UUID(existing["job_id"]))
    is_employer_owner = employer_id == user_id

    if not is_seeker_owner and not is_employer_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this application",
        )

    current_status: ApplicationStatus = existing["status"]
    if is_seeker_owner and not is_employer_owner and new_status not in {
        current_status,
        "withdrawn",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Job seekers can only withdraw their own applications",
        )
    if is_employer_owner and not is_seeker_owner and new_status == "withdrawn":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can withdraw applications",
        )

    if not can_transition(current_status, new_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from '{current_status}' to '{new_status}'",
        )

    if is_seeker_owner and not is_employer_owner:
        updated = update_application_status_for_user(
            application_id, user_id, new_status
        )
    else:
        updated = update_application_status_by_id(application_id, new_status)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # `applications` has no `updated_at` column in the current schema.
    return ApplicationStatusUpdateResponse(
        id=UUID(updated["id"]),
        status=updated["status"],
        updated_at=datetime.now(UTC),
    )


def get_job_pipeline(user_id: UUID, job_id: UUID) -> JobPipelineResponse:
    """
    Return all applications for a job when ``user_id`` is the job's employer.

    Raises:
        HTTPException: 404 when the job does not exist; 403 when not the employer.
    """
    employer_id = select_job_employer_id(job_id)
    if employer_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    if employer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this job pipeline",
        )

    rows = select_applications_for_job(job_id)
    applications = [application_row_to_response(r) for r in rows]
    return JobPipelineResponse(job_id=job_id, applications=applications)
