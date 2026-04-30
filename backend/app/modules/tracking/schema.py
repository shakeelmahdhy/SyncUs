from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field



ApplicationStatus = Literal[
    "applied",
    "shortlisted",
    "interview",
    "offered",
    "rejected",
    "withdrawn",
]


# POST /tracking/applications
class ApplicationCreateRequest(BaseModel):
    job_id: UUID
    resume_id: UUID | None = None


# Generic application payload from DB
class ApplicationResponse(BaseModel):
    id: UUID
    job_id: UUID
    job_seeker_id: UUID
    resume_id: UUID | None = None
    status: ApplicationStatus
    created_at: datetime


# GET /tracking/applications
class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
    total: int


# PATCH /tracking/applications/{application_id}/status
class ApplicationStatusUpdateRequest(BaseModel):
    status: ApplicationStatus = Field(...)


class ApplicationStatusUpdateResponse(BaseModel):
    id: UUID
    status: ApplicationStatus
    updated_at: datetime


# GET /tracking/jobs/{job_id}/pipeline
class JobPipelineResponse(BaseModel):
    job_id: UUID
    applications: list[ApplicationResponse]