"""Tests for tracking ``list_applications`` (B2)."""

from datetime import datetime, timezone
from unittest.mock import patch
from uuid import UUID

from app.modules.tracking.model import ApplicationRow
from app.modules.tracking.service import list_applications

USER_A = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_B = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
JOB = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")


def _row(
    app_id: str,
    seeker_id: UUID,
    created_at: str,
    status: str = "applied",
) -> ApplicationRow:
    return {
        "id": app_id,
        "job_id": str(JOB),
        "job_seeker_id": str(seeker_id),
        "resume_id": None,
        "status": status,  # type: ignore[assignment]
        "created_at": created_at,
    }


def test_list_applications_user_a_two_rows_newest_first() -> None:
    """Repository returns ``created_at`` desc (newest first); service preserves order."""
    older = _row(
        "11111111-1111-1111-1111-111111111111",
        USER_A,
        "2025-01-01T10:00:00+00:00",
    )
    newer = _row(
        "22222222-2222-2222-2222-222222222222",
        USER_A,
        "2025-06-01T12:00:00+00:00",
    )
    with patch(
        "app.modules.tracking.service.select_applications_by_user",
        return_value=[newer, older],
    ) as mock_select:
        out = list_applications(USER_A)

    mock_select.assert_called_once_with(USER_A)
    assert out.total == 2
    assert len(out.items) == 2
    assert out.items[0].id == UUID("22222222-2222-2222-2222-222222222222")
    assert out.items[1].id == UUID("11111111-1111-1111-1111-111111111111")
    assert out.items[0].created_at > out.items[1].created_at


def test_list_applications_user_b_one_row() -> None:
    only = _row(
        "33333333-3333-3333-3333-333333333333",
        USER_B,
        "2025-03-15T08:00:00+00:00",
    )
    with patch(
        "app.modules.tracking.service.select_applications_by_user",
        return_value=[only],
    ) as mock_select:
        out = list_applications(USER_B)

    mock_select.assert_called_once_with(USER_B)
    assert out.total == 1
    assert len(out.items) == 1
    assert out.items[0].job_seeker_id == USER_B
    assert out.items[0].created_at == datetime(
        2025, 3, 15, 8, 0, tzinfo=timezone.utc
    )


def test_list_applications_empty() -> None:
    with patch(
        "app.modules.tracking.service.select_applications_by_user",
        return_value=[],
    ):
        out = list_applications(USER_A)
    assert out.total == 0
    assert out.items == []
