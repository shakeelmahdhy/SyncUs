"""Unit tests for auth guard helper dependencies."""

from __future__ import annotations

from uuid import UUID

import pytest
from fastapi import HTTPException

from app.core.auth import (
    CurrentUser,
    get_current_candidate,
    get_current_employer,
    get_current_user_id,
)


def test_get_current_user_id_returns_sub() -> None:
    user = CurrentUser(
        sub=UUID("11111111-1111-1111-1111-111111111111"),
        email="candidate@example.com",
        role="job_seeker",
    )

    assert get_current_user_id(user) == user.sub


def test_get_current_employer_allows_employer() -> None:
    user = CurrentUser(
        sub=UUID("22222222-2222-2222-2222-222222222222"),
        email="employer@example.com",
        role="employer",
    )

    assert get_current_employer(user) == user


def test_get_current_employer_rejects_non_employer() -> None:
    user = CurrentUser(
        sub=UUID("33333333-3333-3333-3333-333333333333"),
        email="candidate@example.com",
        role="job_seeker",
    )

    with pytest.raises(HTTPException) as exc:
        get_current_employer(user)

    assert exc.value.status_code == 403
    assert exc.value.detail == "This endpoint is only accessible to employers"


def test_get_current_candidate_allows_job_seeker() -> None:
    user = CurrentUser(
        sub=UUID("44444444-4444-4444-4444-444444444444"),
        email="candidate@example.com",
        role="job_seeker",
    )

    assert get_current_candidate(user) == user


def test_get_current_candidate_rejects_non_job_seeker() -> None:
    user = CurrentUser(
        sub=UUID("55555555-5555-5555-5555-555555555555"),
        email="employer@example.com",
        role="employer",
    )

    with pytest.raises(HTTPException) as exc:
        get_current_candidate(user)

    assert exc.value.status_code == 403
    assert exc.value.detail == "This endpoint is only accessible to job seekers"
