"""
JWT authentication for SyncUs (Option A).

Verifies Supabase Auth access tokens sent as:
  Authorization: Bearer <access_jwt>

The canonical user id is JWT claim ``sub`` (UUID), matching ``auth.users.id``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer(auto_error=True)


@dataclass(frozen=True, slots=True)
class CurrentUser:
    """Authenticated caller derived from a verified Supabase access JWT."""

    sub: UUID
    email: str | None = None


def _jwt_secret() -> str:
    secret = os.environ.get("SUPABASE_JWT_SECRET", "").strip()
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_JWT_SECRET is not configured",
        )
    return secret


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> CurrentUser:
    """
    Verify Bearer token and return the authenticated user.

    Raises:
        HTTPException: 401 for missing/invalid/expired tokens.
    """
    token = credentials.credentials
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
    return CurrentUser(sub=user_id, email=email)


def get_current_user_id(
    current_user: CurrentUser = Depends(get_current_user),
) -> UUID:
    """Return ``sub`` for routes that only need the user id."""
    return current_user.sub


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
CurrentUserIdDep = Annotated[UUID, Depends(get_current_user_id)]
