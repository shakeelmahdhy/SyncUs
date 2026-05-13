"""Tests for tracking status transition rules."""

import pytest

from app.modules.tracking.schema import ApplicationStatus
from app.modules.tracking.transitions import can_transition

_STATUSES: list[ApplicationStatus] = [
    "applied",
    "shortlisted",
    "interview",
    "offered",
    "rejected",
    "withdrawn",
]


@pytest.mark.parametrize("status", _STATUSES)
def test_same_status_is_always_allowed(status: ApplicationStatus) -> None:
    assert can_transition(status, status) is True


@pytest.mark.parametrize(
    ("from_s", "to_s", "expected"),
    [
        ("applied", "shortlisted", True),
        ("applied", "interview", True),
        ("applied", "rejected", True),
        ("applied", "withdrawn", True),
        ("applied", "offered", False),
        ("shortlisted", "interview", True),
        ("shortlisted", "offered", True),
        ("shortlisted", "applied", False),
        ("interview", "offered", True),
        ("interview", "shortlisted", False),
        ("offered", "rejected", True),
        ("offered", "withdrawn", True),
        ("offered", "interview", False),
        ("rejected", "withdrawn", False),
        ("withdrawn", "applied", False),
    ],
)
def test_directed_transitions(
    from_s: ApplicationStatus, to_s: ApplicationStatus, expected: bool
) -> None:
    assert can_transition(from_s, to_s) is expected
