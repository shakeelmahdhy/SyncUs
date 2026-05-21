"""
JWT authentication for SyncUs using Supabase JWKS / ES256 tokens.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer(auto_error=True)


@dataclass(frozen=True, slots=True)
class CurrentUser:
    sub: UUID
    email: str | None = None


def _supabase_url() -> str:
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    if not url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_URL is not configured",
        )
    return url


def _jwks_url() -> str:
    return f"{_supabase_url()}/auth/v1/.well-known/jwks.json"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> CurrentUser:
    token = credentials.credentials

    try:
        jwk_client = PyJWKClient(_jwks_url())
        signing_key = jwk_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
        )

    except jwt.PyJWTError as e:
        print("JWT ERROR:", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    raw_sub = payload.get("sub")

    if not raw_sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(str(raw_sub))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    raw_email = payload.get("email")
    email = raw_email if isinstance(raw_email, str) else None

    return CurrentUser(sub=user_id, email=email)


def get_current_user_id(
    current_user: CurrentUser = Depends(get_current_user),
) -> UUID:
    return current_user.sub


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
CurrentUserIdDep = Annotated[UUID, Depends(get_current_user_id)]
