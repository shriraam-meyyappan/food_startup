"""Load and validate application settings without storing secrets in code."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from sqlalchemy.engine import make_url
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Environment variables override values in the backend's local .env."""

    app_name: str = Field(default="DailyDabba API", min_length=1)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    database_url: SecretStr | None = Field(default=None, repr=False)
    migration_database_url: SecretStr | None = Field(default=None, repr=False)
    test_database_url: SecretStr | None = Field(default=None, repr=False)

    jwt_secret: SecretStr | None = Field(default=None, repr=False)
    jwt_issuer: str = Field(default="dailydabba-api", min_length=1, max_length=120)
    jwt_audience: str = Field(
        default="dailydabba-clients", min_length=1, max_length=120
    )
    access_token_minutes: int = Field(default=15, ge=1, le=60)
    auth_rate_limit_per_minute: int = Field(default=10, ge=1, le=1000)

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, value: SecretStr | None) -> SecretStr | None:
        if value is not None:
            secret = value.get_secret_value()
            if len(secret.encode("utf-8")) < 32 or secret.startswith("replace_"):
                raise ValueError(
                    "JWT_SECRET must be a generated secret of at least 32 bytes"
                )
        return value

    @field_validator("database_url", "migration_database_url", "test_database_url")
    @classmethod
    def validate_postgres_url(cls, value: SecretStr | None) -> SecretStr | None:
        if value is None:
            return None
        try:
            url = make_url(value.get_secret_value())
        except Exception:
            raise ValueError("Use a valid PostgreSQL connection URL") from None
        if (
            url.drivername != "postgresql+psycopg"
            or not url.host
            or not url.database
            or not url.username
            or not url.password
        ):
            raise ValueError(
                "Use postgresql+psycopg with host, database, user and password"
            )
        return value

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="forbid",
        hide_input_in_errors=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Validate settings once per server process."""
    return Settings()
