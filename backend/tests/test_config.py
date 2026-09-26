import pytest
from pydantic import ValidationError

from app.config import Settings


REQUIRED = {
    "SUPABASE_URL": "https://example.supabase.co",
    "SUPABASE_ANON_KEY": "anon",
    "SUPABASE_SERVICE_ROLE_KEY": "service",
    "DATABASE_URL": "postgresql://postgres:password@db.example.supabase.co:5432/postgres",
    "OPENAI_API_KEY": "sk-test",
    "ALLOWED_ORIGINS": "http://localhost:5173, https://app.example.com",
}


def test_settings_load_required_values_and_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for name, value in REQUIRED.items():
        monkeypatch.setenv(name, value)

    settings = Settings(_env_file=None)

    assert settings.database_url == REQUIRED["DATABASE_URL"]
    assert settings.openai_embedding_model == "text-embedding-3-small"
    assert settings.openai_embedding_dimensions == 1536
    assert settings.cors_origins == ["http://localhost:5173", "https://app.example.com"]


def test_settings_fail_when_required_value_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    for name, value in REQUIRED.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY")

    with pytest.raises(ValidationError, match="supabase_service_role_key"):
        Settings(_env_file=None)
