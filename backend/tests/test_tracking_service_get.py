"""Tests for tracking ``get_application`` (B3)."""

from unittest.mock import patch
from uuid import UUID

from app.modules.tracking.model import ApplicationRow
from app.modules.tracking.service import get_application

USER = UUID("11111111-1111-1111-1111-111111111111")
APP_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
JOB_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def test_get_application_returns_mapped_row() -> None:
    row: ApplicationRow = {
        "id": str(APP_ID),
        "job_id": str(JOB_ID),
        "job_seeker_id": str(USER),
        "resume_id": None,
        "status": "applied",
        "created_at": "2025-04-01T15:00:00+00:00",
    }
    with patch(
        "app.modules.tracking.service.select_application_for_user",
        return_value=row,
    ) as mock_sel:
        out = get_application(USER, APP_ID)

    mock_sel.assert_called_once_with(APP_ID, USER)
    assert out is not None
    assert out.id == APP_ID
    assert out.job_seeker_id == USER


def test_get_application_returns_none_when_not_found_or_unowned() -> None:
    with patch(
        "app.modules.tracking.service.select_application_for_user",
        return_value=None,
    ) as mock_sel:
        out = get_application(USER, APP_ID)

    mock_sel.assert_called_once_with(APP_ID, USER)
    assert out is None
