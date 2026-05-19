"""
Legacy import path for the Supabase client.

Prefer ``app.core.supabase_client`` and ``app.core.auth`` for new code.
"""

from supabase import Client

from app.core.supabase_client import get_supabase_service_client


def get_supabase_client() -> Client:
    """Deprecated: use ``get_supabase_service_client()`` directly."""
    return get_supabase_service_client()
