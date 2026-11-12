"""Reject invalid configuration and verify environment-variable precedence."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_environment_overrides_dotenv(monkeypatch, tmp_path) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text("APP_NAME=From file\nLOG_LEVEL=INFO\n", encoding="utf-8")
    monkeypatch.setenv("APP_NAME", "From environment")
    assert Settings(_env_file=dotenv).app_name == "From environment"


def test_invalid_log_level_fails_validation() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, log_level="INVALID")
