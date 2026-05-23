"""
JWT authentication for SyncUs (Option A).

Verifies Supabase Auth access tokens sent as:
  Authorization: Bearer <access_jwt>

The canonical user id is JWT claim ``sub`` (UUID), matching ``auth.users.id``.
Role is inferred from ``public.employers`` / ``public.job_seekers``.

Supabase signing:
  - **ES256** (current default): asymmetric — verify with the public key from JWKS.
  - **HS256** (legacy): symmetric — verify with ``SUPABASE_JWT_SECRET`` from the dashboard.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Annotated, Literal
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.core.supabase_client import get_supabase_service_client

UserRole = Literal["employer", "job_seeker"]

_bearer = HTTPBearer(auto_error=True)
_bearer_optional = HTTPBearer(auto_error=False)

_jwks_client_instance: PyJWKClient | None = None


@dataclass(frozen=True, slots=True)
class CurrentUser:
    """Authenticated caller: verified JWT ``sub`` plus optional app role."""

    sub: UUID
    email: str | None = None
    role: UserRole | None = None


def _jwt_secret() -> str | None:
    """Legacy HS256 secret from the dashboard (optional when using ES256 + JWKS)."""
    secret = os.environ.get("SUPABASE_JWT_SECRET", "").strip()
    return secret or None


def _get_jwks_client() -> PyJWKClient:
    """Lazy JWKS client for ES256 (and other asymmetric) Supabase access tokens."""
    global _jwks_client_instance
    if _jwks_client_instance is None:
        base = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
        if not base:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SUPABASE_URL is not configured",
            )
        jwks_url = f"{base}/auth/v1/.well-known/jwks.json"
        _jwks_client_instance = PyJWKClient(jwks_url)
    return _jwks_client_instance


def _verify_and_decode(token: str) -> dict:
    """
    Verify signature and return JWT claims.

    Picks verification method from the token header ``alg``:
    - HS256 → symmetric secret
    - ES256 / RS256 → public key from Supabase JWKS (matched by ``kid``)
    """
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    alg = header.get("alg")
    decode_options = {"verify_aud": True}

    try:
        if alg == "HS256":
            secret = _jwt_secret()
            if not secret:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="SUPABASE_JWT_SECRET is not configured for HS256 tokens",
                )
            return jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                audience="authenticated",
                options=decode_options,
            )

        if alg in ("ES256", "RS256"):
            signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=[alg],
                audience="authenticated",
                options=decode_options,
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def _decode_sub_and_email(token: str) -> tuple[UUID, str | None]:
    """Verify access JWT and return ``(sub, email)``."""
    payload = _verify_and_decode(token)

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
