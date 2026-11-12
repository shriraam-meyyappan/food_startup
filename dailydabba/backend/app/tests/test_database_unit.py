"""Configuration secrecy and liveness behavior without a configured database."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.main import create_app


def test_database_secrets_are_not_in_settings_representation():
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://app:private_password@localhost/db",
    )
    assert "private_password" not in repr(settings)
    assert "private_password" not in settings.model_dump_json()


def test_invalid_database_url_does_not_expose_input():
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None, database_url="sqlite://secret_password")
    assert "secret_password" not in str(error.value)


def test_liveness_is_independent_of_database_configuration():
    with TestClient(create_app(Settings(_env_file=None))) as client:
        assert client.get("/api/v1/health").json() == {"status": "ok"}
        response = client.get("/api/v1/ready")
        assert response.status_code == 503
        assert response.json() == {"detail": "Database unavailable"}


def test_readiness_database_errors_are_sanitized():
    from unittest.mock import Mock
    from sqlalchemy.exc import SQLAlchemyError
    from app.db.database import get_session

    fake_session = Mock()
    fake_session.execute.side_effect = SQLAlchemyError(
        "private_password must not appear"
    )
    application = create_app(Settings(_env_file=None))
    application.dependency_overrides[get_session] = lambda: fake_session
    with TestClient(application) as client:
        response = client.get("/api/v1/ready")
        assert response.status_code == 503
        assert response.json() == {"detail": "Database unavailable"}
        assert "private_password" not in response.text
