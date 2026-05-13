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

    finally:
        if removed:
            sys.path.insert(0, repo_root)


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
