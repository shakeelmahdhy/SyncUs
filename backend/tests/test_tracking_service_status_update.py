"""Tests for tracking application status updates."""

from unittest.mock import patch
from uuid import UUID

from fastapi import HTTPException
import pytest

from app.modules.tracking.model import ApplicationRow
from app.modules.tracking.service import update_application_status

APPLICATION_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
JOB_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
SEEKER_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
EMPLOYER_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
OTHER_USER_ID = UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")


def _row(status: str = "applied") -> ApplicationRow:
    return {
        "id": str(APPLICATION_ID),
        "job_id": str(JOB_ID),
        "job_seeker_id": str(SEEKER_ID),
        "resume_id": None,
        "status": status,  # type: ignore[assignment]
        "created_at": "2025-03-01T10:00:00+00:00",
    }


def test_employer_can_update_status_for_owned_job_application() -> None:
    updated = _row("shortlisted")

    with (
        patch("app.modules.tracking.service.select_application_by_id", return_value=_row()) as mock_select,
        patch("app.modules.tracking.service.select_job_employer_id", return_value=EMPLOYER_ID) as mock_employer,
        patch("app.modules.tracking.service.update_application_status_by_id", return_value=updated) as mock_update,
        patch("app.modules.tracking.service.update_application_status_for_user") as mock_user_update,
    ):
        out = update_application_status(EMPLOYER_ID, APPLICATION_ID, "shortlisted")

    mock_select.assert_called_once_with(APPLICATION_ID)
    mock_employer.assert_called_once_with(JOB_ID)
    mock_update.assert_called_once_with(APPLICATION_ID, "shortlisted")
    mock_user_update.assert_not_called()
    assert out.id == APPLICATION_ID
    assert out.status == "shortlisted"


def test_job_seeker_can_withdraw_own_application() -> None:
    updated = _row("withdrawn")

    with (
        patch("app.modules.tracking.service.select_application_by_id", return_value=_row()) as mock_select,
        patch("app.modules.tracking.service.select_job_employer_id", return_value=EMPLOYER_ID),
        patch("app.modules.tracking.service.update_application_status_for_user", return_value=updated) as mock_update,
        patch("app.modules.tracking.service.update_application_status_by_id") as mock_employer_update,
    ):
        out = update_application_status(SEEKER_ID, APPLICATION_ID, "withdrawn")

    mock_select.assert_called_once_with(APPLICATION_ID)
    mock_update.assert_called_once_with(APPLICATION_ID, SEEKER_ID, "withdrawn")
    mock_employer_update.assert_not_called()
    assert out.status == "withdrawn"


def test_job_seeker_cannot_self_shortlist() -> None:
    with (
        patch("app.modules.tracking.service.select_application_by_id", return_value=_row()),
        patch("app.modules.tracking.service.select_job_employer_id", return_value=EMPLOYER_ID),
    ):
        with pytest.raises(HTTPException) as exc:
            update_application_status(SEEKER_ID, APPLICATION_ID, "shortlisted")

    assert exc.value.status_code == 403


def test_employer_cannot_withdraw_candidate_application() -> None:
    with (
        patch("app.modules.tracking.service.select_application_by_id", return_value=_row()),
        patch("app.modules.tracking.service.select_job_employer_id", return_value=EMPLOYER_ID),
    ):
        with pytest.raises(HTTPException) as exc:
            update_application_status(EMPLOYER_ID, APPLICATION_ID, "withdrawn")

    assert exc.value.status_code == 403


def test_unrelated_user_cannot_update_application_status() -> None:
    with (
        patch("app.modules.tracking.service.select_application_by_id", return_value=_row()),
        patch("app.modules.tracking.service.select_job_employer_id", return_value=EMPLOYER_ID),
    ):
        with pytest.raises(HTTPException) as exc:
            update_application_status(OTHER_USER_ID, APPLICATION_ID, "shortlisted")

    assert exc.value.status_code == 403
