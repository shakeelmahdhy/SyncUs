"""
Compatibility import path for Supabase client factories.

Use ``app.core.supabase_client`` in new code.
"""

from app.core.supabase_client import (
    get_supabase_anon_client,
    get_supabase_publishable_client,
    get_supabase_service_client,
)

__all__ = [
    "get_supabase_anon_client",
    "get_supabase_publishable_client",
    "get_supabase_service_client",
]
