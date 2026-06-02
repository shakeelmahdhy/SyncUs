"""
Supabase client factories for the SyncUs backend.

This module is the SINGLE place that builds Supabase clients on the server.
Other modules must call these functions instead of calling
`supabase.create_client(...)` themselves.

Two clients are exposed:

- `get_supabase_service_client()` — uses SUPABASE_SECRET_KEY (server-only).
  Required for Option A: bypasses RLS, so callers MUST scope every query
  by the authenticated user (`sub`) in code.

- `get_supabase_publishable_client()` — uses SUPABASE_PUBLISHABLE_KEY.

Both clients are created lazily and cached as module-level singletons.
"""

from __future__ import annotations

import os
import sys
from typing import Optional


_service_client: Optional["object"] = None
_publishable_client: Optional["object"] = None


def _import_supabase_create_client():
    """Import supabase.create_client without the local supabase/ CLI folder shadowing it."""
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
    removed = False
    if repo_root in sys.path:
        sys.path.remove(repo_root)
        removed = True
    try:
        from supabase import create_client

        return create_client
    finally:
        if removed:
            sys.path.insert(0, repo_root)


def _require_env(name: str) -> str:
    """Return the env var or raise a clear RuntimeError if missing/empty."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Set it in backend/.env (see backend/.env.example)."
        )
    return value


def _publishable_key() -> str:
    """Resolve the canonical publishable API key."""
    key = (os.environ.get("SUPABASE_PUBLISHABLE_KEY") or "").strip()
    if key:
        return key
    raise RuntimeError(
        "Missing Supabase publishable key: set SUPABASE_PUBLISHABLE_KEY "
        "in backend/.env (see backend/.env.example)."
    )


def get_supabase_service_client():
    """Return a process-wide Supabase client built with the SECRET key (bypasses RLS)."""
    global _service_client
    if _service_client is None:
        url = _require_env("SUPABASE_URL")
        key = _require_env("SUPABASE_SECRET_KEY")
        create_client = _import_supabase_create_client()
        try:
            from supabase.lib.client_options import ClientOptions
            from supabase_auth import AuthFlowType

            options = ClientOptions(
                auto_refresh_token=False,
                persist_session=False,
                flow_type=AuthFlowType.IMPLICIT,
            )
            _service_client = create_client(url, key, options)
        except Exception:
            _service_client = create_client(url, key)
    return _service_client


def create_supabase_service_client():
    """Return a fresh Supabase client using the SECRET key.

    Use this for Auth operations that may attach a user session to the client.
    Data-access code should keep using the cached service client above.
    """
    url = _require_env("SUPABASE_URL")
    key = _require_env("SUPABASE_SECRET_KEY")
    create_client = _import_supabase_create_client()
    try:
        from supabase.lib.client_options import ClientOptions
        from supabase_auth import AuthFlowType

        options = ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
            flow_type=AuthFlowType.IMPLICIT,
        )
        return create_client(url, key, options)
    except Exception:
        return create_client(url, key)


def reset_supabase_service_client() -> None:
    """Drop the cached service client (e.g. after accidental user sign-in on it)."""
    global _service_client
    _service_client = None


def get_supabase_publishable_client():
    """Return a process-wide Supabase client built with the publishable key."""
    global _publishable_client
    if _publishable_client is None:
        url = _require_env("SUPABASE_URL")
        key = _publishable_key()
        create_client = _import_supabase_create_client()
        _publishable_client = create_client(url, key)
    return _publishable_client


def get_supabase_anon_client():
    """Backwards-compatible alias for the publishable/anon client."""
    return get_supabase_publishable_client()
