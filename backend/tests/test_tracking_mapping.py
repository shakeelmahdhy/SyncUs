"""Tests for ApplicationRow -> ApplicationResponse mapping."""

from datetime import datetime, timezone
from uuid import UUID

import pytest

from app.modules.tracking.mapping import application_row_to_response
from app.modules.tracking.model import ApplicationRow


def test_maps_strings_to_response_with_z_suffix() -> None:
    row: ApplicationRow = {
        "id": "11111111-1111-1111-1111-111111111111",
        "job_id": "22222222-2222-2222-2222-222222222222",
        "job_seeker_id": "33333333-3333-3333-3333-333333333333",
        "resume_id": None,
        "status": "applied",
        "created_at": "2025-01-15T12:30:00Z",
    }
    out = application_row_to_response(row)
    assert out.id == UUID("11111111-1111-1111-1111-111111111111")
    assert out.job_id == UUID("22222222-2222-2222-2222-222222222222")
    assert out.job_seeker_id == UUID("33333333-3333-3333-3333-333333333333")
    assert out.resume_id is None
    assert out.status == "applied"
    assert out.created_at == datetime(2025, 1, 15, 12, 30, tzinfo=timezone.utc)


def test_offset_timestamptz() -> None:
    row: ApplicationRow = {
        "id": "11111111-1111-1111-1111-111111111111",
        "job_id": "22222222-2222-2222-2222-222222222222",
        "job_seeker_id": "33333333-3333-3333-3333-333333333333",
        "resume_id": None,
        "status": "shortlisted",
        "created_at": "2025-06-01T08:00:00+10:00",
    }
    out = application_row_to_response(row)
    assert out.created_at.isoformat() == "2025-06-01T08:00:00+10:00"


def test_resume_id_string() -> None:
    row: ApplicationRow = {
        "id": "11111111-1111-1111-1111-111111111111",
        "job_id": "22222222-2222-2222-2222-222222222222",
        "job_seeker_id": "33333333-3333-3333-3333-333333333333",
        "resume_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "status": "interview",
        "created_at": "2025-01-15T00:00:00+00:00",
    }
    out = application_row_to_response(row)
    assert out.resume_id == UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def test_invalid_uuid_raises() -> None:
    row: ApplicationRow = {
        "id": "not-a-uuid",
        "job_id": "22222222-2222-2222-2222-222222222222",
        "job_seeker_id": "33333333-3333-3333-3333-333333333333",
        "resume_id": None,
        "status": "applied",
        "created_at": "2025-01-15T00:00:00+00:00",
    }
    with pytest.raises(ValueError):
        application_row_to_response(row)
