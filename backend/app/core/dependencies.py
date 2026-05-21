"""
Legacy FastAPI dependencies.

New route handlers should use ``app.core.auth`` for identity and
``app.core.supabase_client`` for Supabase clients. This module remains as a
backwards-compatible adapter for older imports.
"""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client

from app.core.auth import CurrentUser, get_current_user as get_auth_current_user
from app.core.supabase_client import get_supabase_service_client

security = HTTPBearer(auto_error=False)


def get_supabase_client() -> Client:
    """Deprecated: use ``get_supabase_service_client()`` directly."""
    try:
        return get_supabase_service_client()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


def _legacy_role(role: str | None) -> str | None:
    """Map canonical role names to the older dependency contract."""
    if role == "job_seeker":
        return "candidate"
    return role


def _legacy_profile(current_user: CurrentUser) -> dict:
    profile: dict = {}
    table_name = None

    if current_user.role == "employer":
        table_name = "employers"
    elif current_user.role == "job_seeker":
        table_name = "job_seekers"

    if table_name:
        response = (
            get_supabase_client()
            .table(table_name)
            .select("*")
            .eq("id", str(current_user.sub))
            .limit(1)
            .execute()
        )
        if response.data:
            profile = response.data[0]

    return {
        "id": str(current_user.sub),
        "sub": current_user.sub,
        "email": current_user.email,
        "role": _legacy_role(current_user.role),
        "profile": profile,
    }


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Deprecated legacy user dependency.

    Verifies the same Supabase JWT as ``app.core.auth`` and returns the older
    dict payload shape expected by pre-contract routes.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
        )

    current_user = get_auth_current_user(credentials)
    return _legacy_profile(current_user)


async def get_current_employer(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Deprecated: require an authenticated employer."""
    if current_user.get("role") != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to employers",
        )
    return current_user


async def get_current_candidate(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Deprecated: require an authenticated job seeker/candidate."""
    if current_user.get("role") not in {"candidate", "job_seeker"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to job seekers",
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """Deprecated: return the current user when a Bearer token is present."""
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
