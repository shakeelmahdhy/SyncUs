"""
Actor identity for tracking routes.

Intended to be swapped for a JWT-based dependency when authorization lands.
Until then: send ``X-User-Id`` (UUID) on requests, or set ``SYNCUS_DEV_USER_ID``.
"""

from __future__ import annotations

import os
from typing import Annotated
from uuid import UUID

from fastapi import Header, HTTPException


def get_actor_user_id(
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
) -> UUID:
    """Resolve the authenticated user's id for tracking write/read scope."""
    raw = (x_user_id or os.environ.get("SYNCUS_DEV_USER_ID") or "").strip()
    if not raw:
        raise HTTPException(
            status_code=503,
            detail="Actor id required: send X-User-Id header or set SYNCUS_DEV_USER_ID until JWT auth is configured.",
        )
    try:
        return UUID(raw)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Actor id must be a valid UUID.",
        ) from exc
