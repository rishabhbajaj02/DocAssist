from app.config import settings
from app.database.supabase import create_service_role_client, create_user_client


def test_user_client_uses_anon_key_and_request_token() -> None:
    first = create_user_client("first-user-jwt")
    second = create_user_client("second-user-jwt")

    assert first is not second
    assert first.options.headers["apiKey"] == settings.supabase_anon_key
    assert first.options.headers["Authorization"] == "Bearer first-user-jwt"
    assert second.options.headers["Authorization"] == "Bearer second-user-jwt"
    assert first.options.headers["Authorization"] == "Bearer first-user-jwt"


def test_service_role_client_uses_service_key() -> None:
    client = create_service_role_client()

    assert client.options.headers["apiKey"] == settings.supabase_service_role_key
    assert client.options.headers["Authorization"] == f"Bearer {settings.supabase_service_role_key}"
