"""Tests for tracking ``create_application`` (B1)."""

from unittest.mock import patch
from uuid import UUID

from app.modules.tracking.model import ApplicationRow
from app.modules.tracking.schema import ApplicationCreateRequest
from app.modules.tracking.service import create_application


def test_create_application_uses_insert_and_mapping() -> None:
    user_id = UUID("11111111-1111-1111-1111-111111111111")
    job_id = UUID("22222222-2222-2222-2222-222222222222")
    payload = ApplicationCreateRequest(job_id=job_id, resume_id=None)

    row: ApplicationRow = {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "job_id": str(job_id),
        "job_seeker_id": str(user_id),
        "resume_id": None,
        "status": "applied",
        "created_at": "2025-03-01T10:00:00+00:00",
    }

    with patch(
        "app.modules.tracking.service.insert_application",
        return_value=row,
    ) as mock_insert:
        out = create_application(user_id, payload)

    mock_insert.assert_called_once_with(user_id, job_id, None)
    assert out.id == UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    assert out.job_id == job_id
    assert out.job_seeker_id == user_id
    assert out.resume_id is None
    assert out.status == "applied"
