from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EmbedLead"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    api_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+asyncpg://embedlead:embedlead@localhost:5432/embedlead",
    )

    redis_url: str = "redis://localhost:6379/0"

    cors_allowed_origins: str = "http://localhost:3000"

    rate_limit_per_minute: int = 60

    geo_primary_url: str = "https://ipapi.co"
    geo_fallback_url: str = "https://ipwho.is"

    widget_cache_ttl_seconds: int = 300

    max_submission_payload_bytes: int = 16384

    secret_key: str = Field(
        default="development-only-change-me",
        min_length=16,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
