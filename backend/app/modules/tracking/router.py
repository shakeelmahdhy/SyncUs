from uuid import UUID

from fastapi import APIRouter

from app.core.auth import CurrentUserIdDep

from .schema import (
    ApplicationCreateRequest,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationStatusUpdateRequest,
    ApplicationStatusUpdateResponse,
    JobPipelineResponse,
)
from .service import (
    create_application,
    get_application,
    get_job_pipeline,
    list_applications,
    update_application_status,
)

router = APIRouter()


@router.post("/applications", response_model=ApplicationResponse)
def apply_to_job(
    payload: ApplicationCreateRequest,
    user_id: CurrentUserIdDep,
) -> ApplicationResponse:
    return create_application(user_id, payload)


@router.get("/applications", response_model=ApplicationListResponse)
def get_my_applications(user_id: CurrentUserIdDep) -> ApplicationListResponse:
    return list_applications(user_id)


@router.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application_detail(
    application_id: UUID,
    user_id: CurrentUserIdDep,
) -> ApplicationResponse:
    return get_application(user_id, application_id)


@router.patch(
    "/applications/{application_id}/status",
    response_model=ApplicationStatusUpdateResponse,
)
def transition_application_status(
    application_id: UUID,
    payload: ApplicationStatusUpdateRequest,
    user_id: CurrentUserIdDep,
) -> ApplicationStatusUpdateResponse:
    return update_application_status(user_id, application_id, payload.status)


@router.get("/jobs/{job_id}/pipeline", response_model=JobPipelineResponse)
def get_pipeline(job_id: UUID, user_id: CurrentUserIdDep) -> JobPipelineResponse:
    return get_job_pipeline(user_id, job_id)
