"""Backend environment settings."""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str = Field(min_length=1)
    supabase_anon_key: str = Field(min_length=1)
    supabase_service_role_key: str = Field(min_length=1)
    database_url: str = Field(min_length=1)
    openai_api_key: str = Field(min_length=1)
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = 1536
    allowed_origins: str

    @field_validator("allowed_origins")
    @classmethod
    def validate_origins(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("ALLOWED_ORIGINS must contain at least one origin")
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()
