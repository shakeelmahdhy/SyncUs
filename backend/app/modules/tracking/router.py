from uuid import UUID

from fastapi import APIRouter

from app.core.auth import CandidateUserDep, CurrentUserDep, EmployerUserDep

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
    current_candidate: CandidateUserDep,
) -> ApplicationResponse:
    return create_application(current_candidate.sub, payload)


@router.get("/applications", response_model=ApplicationListResponse)
def get_my_applications(current_candidate: CandidateUserDep) -> ApplicationListResponse:
    return list_applications(current_candidate.sub)


@router.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application_detail(
    application_id: UUID,
    current_candidate: CandidateUserDep,
) -> ApplicationResponse:
    return get_application(current_candidate.sub, application_id)


@router.patch(
    "/applications/{application_id}/status",
    response_model=ApplicationStatusUpdateResponse,
)
def transition_application_status(
    application_id: UUID,
    payload: ApplicationStatusUpdateRequest,
    current_user: CurrentUserDep,
) -> ApplicationStatusUpdateResponse:
    return update_application_status(current_user.sub, application_id, payload.status)


@router.get("/jobs/{job_id}/pipeline", response_model=JobPipelineResponse)
def get_pipeline(job_id: UUID, current_employer: EmployerUserDep) -> JobPipelineResponse:
    return get_job_pipeline(current_employer.sub, job_id)
