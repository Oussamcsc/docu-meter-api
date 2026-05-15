from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Docu Meter API"
    database_url: str = "sqlite:///./docu_meter.db"
    api_key_prefix: str = "dm_live"
    api_key_pepper: SecretStr
    admin_api_token: SecretStr | None = None
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    max_document_characters: int = 50_000
    openai_api_key: SecretStr
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: float = 60.0

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_api_key(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("OPENAI_API_KEY must be configured")
        return value

    @property
    def sqlite_path(self) -> Path | None:
        if not self.database_url.startswith("sqlite:///"):
            return None
        return Path(self.database_url.removeprefix("sqlite:///"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
