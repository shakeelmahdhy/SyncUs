<<<<<<< HEAD
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
  Optional, intended for tooling/scripts that should remain low-privilege.
  Most FastAPI route handlers should NOT use this.

Both clients are created lazily and cached as module-level singletons so
that:
  1. Importing this module never crashes on missing env (which previously
     broke `fastapi dev` discovery).
  2. The first request that needs Supabase initializes one client and
     reuses it for the rest of the process.
"""

from __future__ import annotations

import os
import sys
from typing import Optional


_service_client: Optional["object"] = None
_publishable_client: Optional["object"] = None


def _import_supabase_create_client():
    """
    Import `supabase.create_client` while temporarily removing the repo root
    from `sys.path`.

    Why: this repository contains a top-level `supabase/` directory used by
    the Supabase CLI. When Python resolves `import supabase`, that local
    folder can shadow the installed `supabase-py` PyPI package and break
    `create_client`.

    We remove the repo root just for the duration of this import, then
    restore it.
    """
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
    removed = False
    if repo_root in sys.path:
        sys.path.remove(repo_root)
        removed = True
    try:
        from supabase import create_client  # imported here to avoid shadowing
        return create_client
=======
import os
import sys

from dotenv import load_dotenv


def get_supabase_anon_client():
    """
    Stateless Supabase client using the public anon key.

    This client is intended for RLS-driven access patterns where auth context
    will be derived from the request (next steps).
    """

    # Load environment variables from `backend/.env` (if present).
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))

    supabase_url = os.environ.get("SUPABASE_URL")
    anon_key = os.environ.get("SUPABASE_ANON_KEY")

    if not supabase_url:
        raise RuntimeError("Missing env var SUPABASE_URL")

    if not anon_key:
        raise RuntimeError("Missing env var SUPABASE_ANON_KEY")

    # Important:
    # This repo contains a `supabase/` folder for Supabase CLI.
    # That folder can shadow the installed `supabase-py` package.
    # To avoid that, temporarily remove this repo root from sys.path during import.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

    removed = False

    if repo_root in sys.path:
        sys.path.remove(repo_root)
        removed = True

    try:
        from supabase import create_client  # imported here to avoid shadowing

        # Create a stateless anon client.
        # Note: we intentionally avoid ClientOptions here because your current
        # supabase-py version raises an error related to missing attributes.
        return create_client(supabase_url, anon_key)

>>>>>>> dev
    finally:
        if removed:
            sys.path.insert(0, repo_root)


<<<<<<< HEAD
def _require_env(name: str) -> str:
    """Return the env var or raise a clear RuntimeError if missing/empty."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Set it in backend/.env (see backend/.env.example)."
        )
    return value


def get_supabase_service_client():
    """
    Return a process-wide Supabase client built with the SECRET key.

    This client BYPASSES Row Level Security. It is intended for FastAPI
    backend code that has already verified the caller's identity (Option A:
    JWT verified -> `sub`). Every repository call MUST still filter by the
    authenticated user explicitly.

    Reads from env on first call:
      - SUPABASE_URL
      - SUPABASE_SECRET_KEY  (format: sb_secret_...; replaces legacy
        service_role)

    Raises:
        RuntimeError: if either env var is missing/empty.
    """
    global _service_client
    if _service_client is None:
        url = _require_env("SUPABASE_URL")
        key = _require_env("SUPABASE_SECRET_KEY")
        create_client = _import_supabase_create_client()
        _service_client = create_client(url, key)
    return _service_client


def get_supabase_publishable_client():
    """
    Return a process-wide Supabase client built with the PUBLISHABLE key.

    This client honours Row Level Security and the built-in `anon` role.
    Use it only for tooling/scripts where elevated access is not required.
    Route handlers that need user-scoped data on the backend should prefer
    `get_supabase_service_client()` plus explicit `sub` scoping in code.

    Reads from env on first call:
      - SUPABASE_URL
      - SUPABASE_PUBLISHABLE_KEY  (format: sb_publishable_...; replaces
        legacy anon)

    Raises:
        RuntimeError: if either env var is missing/empty.
    """
    global _publishable_client
    if _publishable_client is None:
        url = _require_env("SUPABASE_URL")
        key = _require_env("SUPABASE_PUBLISHABLE_KEY")
        create_client = _import_supabase_create_client()
        _publishable_client = create_client(url, key)
    return _publishable_client
=======
def get_supabase_service_client():
    """
    Supabase client using the service role key.
    Used only for trusted backend operations like storage uploads.
    """

    # Load environment variables from `backend/.env` (if present).
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))

    supabase_url = os.environ.get("SUPABASE_URL")
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url:
        raise RuntimeError("Missing env var SUPABASE_URL")

    if not service_role_key:
        raise RuntimeError("Missing env var SUPABASE_SERVICE_ROLE_KEY")

    # Prevent local supabase/ folder shadowing installed package.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

    removed = False

    if repo_root in sys.path:
        sys.path.remove(repo_root)
        removed = True

    try:
        from supabase import create_client

        return create_client(supabase_url, service_role_key)

    finally:
        if removed:
            sys.path.insert(0, repo_root)
>>>>>>> dev
