"""Supabase clients for user-scoped and privileged database access."""

from supabase import AsyncClient, AsyncClientOptions

from app.config import settings


def create_user_client(access_token: str) -> AsyncClient:
    """Create an async client whose requests carry one user's JWT."""
    options = AsyncClientOptions(
        headers={"Authorization": f"Bearer {access_token}"},
        auto_refresh_token=False,
        persist_session=False,
    )
    return AsyncClient(settings.supabase_url, settings.supabase_anon_key, options)


def create_service_role_client() -> AsyncClient:
    """Create an async client for backend-only privileged operations."""
    options = AsyncClientOptions(
        headers={"Authorization": f"Bearer {settings.supabase_service_role_key}"},
        auto_refresh_token=False,
        persist_session=False,
    )
    return AsyncClient(settings.supabase_url, settings.supabase_service_role_key, options)
