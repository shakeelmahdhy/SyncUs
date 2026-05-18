"""
Legacy dev identity helper (superseded by ``app.core.auth``).

Tracking routes now use ``Authorization: Bearer <supabase_access_jwt>`` via
``CurrentUserIdDep`` in ``router.py``. This module is kept only for local
scripts or temporary debugging; do not use in new route handlers.
"""

from __future__ import annotations

import os
from uuid import UUID

from fastapi import Header, HTTPException


def get_actor_user_id(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> UUID:
    """
    Dev-only actor resolution from ``X-User-Id`` or ``SYNCUS_DEV_USER_ID``.

    Not used by production tracking routes after Phase C2.
    """
    raw = (x_user_id or os.environ.get("SYNCUS_DEV_USER_ID") or "").strip()
    if not raw:
        raise HTTPException(
            status_code=503,
            detail="Send X-User-Id or set SYNCUS_DEV_USER_ID (dev helper only).",
        )
    try:
        return UUID(raw)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Actor id must be a valid UUID.",
        ) from exc
