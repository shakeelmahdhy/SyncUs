<<<<<<< HEAD
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
=======
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import os


# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# HTTP Bearer token authentication
security = HTTPBearer()


def get_supabase_client() -> Client:
    """
    Get Supabase client instance

    Returns:
        Supabase client

    Raises:
        HTTPException: If Supabase credentials are not configured
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase configuration missing"
        )

    return create_client(SUPABASE_URL, SUPABASE_KEY)
>>>>>>> 28d9068 (Clean matching module branch for push)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
<<<<<<< HEAD
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
=======
    supabase: Client = Depends(get_supabase_client)
) -> dict:

    try:
        token = credentials.credentials

        # Verify JWT token with Supabase
        user_response = supabase.auth.get_user(token)

        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        user = user_response.user

        # Get user profile with role information
        profile_response = supabase.table('user_profiles').select('*').eq(
            'id', user.id
        ).execute()

        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        profile = profile_response.data[0]

        return {
            'id': user.id,
            'email': user.email,
            'role': profile.get('role'),
            'profile': profile
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


async def get_current_employer(
    current_user: dict = Depends(get_current_user)
) -> dict:
    if current_user.get('role') != 'employer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to employers"
        )

>>>>>>> 28d9068 (Clean matching module branch for push)
    return current_user


async def get_current_candidate(
<<<<<<< HEAD
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Deprecated: require an authenticated job seeker/candidate."""
    if current_user.get("role") not in {"candidate", "job_seeker"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to job seekers",
        )
=======
    current_user: dict = Depends(get_current_user)
) -> dict:
    if current_user.get('role') != 'candidate':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to job seekers"
        )

>>>>>>> 28d9068 (Clean matching module branch for push)
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
<<<<<<< HEAD
) -> Optional[dict]:
    """Deprecated: return the current user when a Bearer token is present."""
=======
    supabase: Client = Depends(get_supabase_client)
) -> Optional[dict]:

>>>>>>> 28d9068 (Clean matching module branch for push)
    if not credentials:
        return None

    try:
<<<<<<< HEAD
        return await get_current_user(credentials)
=======
        return await get_current_user(credentials, supabase)
>>>>>>> 28d9068 (Clean matching module branch for push)
    except HTTPException:
        return None
