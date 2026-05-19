"""
JWT authentication for SyncUs (Option A).

Verifies Supabase Auth access tokens sent as:
  Authorization: Bearer <access_jwt>

The canonical user id is JWT claim ``sub`` (UUID), matching ``auth.users.id``.
Role is inferred from ``public.employers`` / ``public.job_seekers`` (not ``user_profiles``).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Annotated, Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from uuid import UUID

from app.core.supabase_client import get_supabase_service_client

UserRole = Literal["employer", "job_seeker"]

_bearer = HTTPBearer(auto_error=True)
_bearer_optional = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class CurrentUser:
    """Authenticated caller: verified JWT ``sub`` plus optional app role."""

    sub: UUID
    email: str | None = None
    role: UserRole | None = None


def _jwt_secret() -> str:
    secret = os.environ.get("SUPABASE_JWT_SECRET", "").strip()
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_JWT_SECRET is not configured",
        )
    return secret


def _decode_sub_and_email(token: str) -> tuple[UUID, str | None]:
    """Verify access JWT and return ``(sub, email)``."""
    try:
        payload = jwt.decode(
            token,
            _jwt_secret(),
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    raw_sub = payload.get("sub")
    if not raw_sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(str(raw_sub))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    raw_email = payload.get("email")
    email = raw_email if isinstance(raw_email, str) else None
    return user_id, email


def _load_role(user_id: UUID) -> UserRole | None:
    """
    Resolve role from SyncUs profile tables.

    Employers take precedence if a row exists in both tables (should not happen).
    """
    client = get_supabase_service_client()
    uid = str(user_id)

    employer = (
        client.table("employers").select("id").eq("id", uid).limit(1).execute()
    )
    if employer.data:
        return "employer"

    seeker = (
        client.table("job_seekers").select("id").eq("id", uid).limit(1).execute()
    )
    if seeker.data:
        return "job_seeker"

    return None


def _current_user_from_token(token: str) -> CurrentUser:
    """Verify JWT and attach role from ``employers`` / ``job_seekers``."""
    sub, email = _decode_sub_and_email(token)
    return CurrentUser(sub=sub, email=email, role=_load_role(sub))


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> CurrentUser:
    """Require a valid Bearer token; return user with optional role."""
    return _current_user_from_token(credentials.credentials)


def get_current_user_id(
    current_user: CurrentUser = Depends(get_current_user),
) -> UUID:
    """Return ``sub`` for routes that only need the user id."""
    return current_user.sub


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_optional),
) -> CurrentUser | None:
    """Return authenticated user when Bearer token is present; else ``None``."""
    if credentials is None:
        return None
    try:
        return _current_user_from_token(credentials.credentials)
    except HTTPException:
        return None


def get_current_employer(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Require authenticated user with an ``employers`` profile row."""
    if current_user.role != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to employers",
        )
    return current_user


def get_current_candidate(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Require authenticated user with a ``job_seekers`` profile row."""
    if current_user.role != "job_seeker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to job seekers",
        )
    return current_user


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
CurrentUserIdDep = Annotated[UUID, Depends(get_current_user_id)]
OptionalUserDep = Annotated[CurrentUser | None, Depends(get_optional_user)]
EmployerUserDep = Annotated[CurrentUser, Depends(get_current_employer)]
CandidateUserDep = Annotated[CurrentUser, Depends(get_current_candidate)]
