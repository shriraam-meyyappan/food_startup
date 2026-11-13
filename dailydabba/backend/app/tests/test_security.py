"""Password, JWT, configuration and bounded rate-limiter behavior without a DB."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError

from app.core.config import Settings
from app.core.rate_limit import AuthRateLimiter
from app.core.security import (
    AuthNotConfigured,
    InvalidCredentials,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.db.database import get_session
from app.main import create_app


@pytest.fixture
def settings():
    return Settings(
        _env_file=None,
        jwt_secret=SecretStr("unit-test-signing-key-with-at-least-32-bytes"),
    )


def claims(settings):
    now = datetime.now(timezone.utc)
    return {
        "sub": str(uuid4()),
        "jti": str(uuid4()),
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=15),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "token_type": "access",
    }


def test_argon2_is_salted_and_verification_fails_closed():
    password = "test-only long password"
    one, two = hash_password(password), hash_password(password)
    assert one.startswith("$argon2id$") and one != two
    assert password not in one
    assert verify_password(password, one)[0]
    assert not verify_password("wrong password", one)[0]
    assert not verify_password(password, None)[0]
    assert not verify_password(password, "invalid hash")[0]
    assert not verify_password(password, "$argon2id$invalid")[0]


def test_signed_access_token_roundtrip(settings):
    subject = uuid4()
    token = create_access_token(subject, settings)
    assert decode_access_token(token, settings) == subject


@pytest.mark.parametrize(
    "fault",
    [
        "expired",
        "missing_exp",
        "missing_iat",
        "missing_nbf",
        "missing_jti",
        "missing_sub",
        "wrong_issuer",
        "wrong_audience",
        "wrong_key",
        "wrong_algorithm",
        "wrong_type",
        "invalid_sub",
        "invalid_jti",
        "future_nbf",
        "future_iat",
        "unsigned",
    ],
)
def test_jwt_invalid_claims_or_signatures_are_rejected(settings, fault):
    payload = claims(settings)
    key = settings.jwt_secret.get_secret_value()
    algorithm = "HS256"
    if fault == "expired":
        payload["exp"] = datetime.now(timezone.utc) - timedelta(seconds=10)
    elif fault.startswith("missing_"):
        del payload[fault.removeprefix("missing_")]
    elif fault == "wrong_issuer":
        payload["iss"] = "another-api"
    elif fault == "wrong_audience":
        payload["aud"] = "another-client"
    elif fault == "wrong_key":
        key = "another-signing-key-with-at-least-32-bytes"
    elif fault == "wrong_algorithm":
        algorithm = "HS384"
        key = key * 2
    elif fault == "wrong_type":
        payload["token_type"] = "refresh"
    elif fault == "invalid_sub":
        payload["sub"] = "not-a-uuid"
    elif fault == "invalid_jti":
        payload["jti"] = "not-a-uuid"
    elif fault == "future_nbf":
        payload["nbf"] = datetime.now(timezone.utc) + timedelta(minutes=5)
    elif fault == "future_iat":
        payload["iat"] = datetime.now(timezone.utc) + timedelta(minutes=5)
    elif fault == "unsigned":
        algorithm, key = "none", ""
    token = jwt.encode(payload, key, algorithm=algorithm)
    with pytest.raises(InvalidCredentials):
        decode_access_token(token, settings)


def test_missing_key_disables_auth_without_guessing_defaults():
    with pytest.raises(AuthNotConfigured):
        create_access_token(uuid4(), Settings(_env_file=None))
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None, jwt_secret="too-short-secret")
    assert "too-short-secret" not in str(error.value)


def test_rate_limit_is_atomic_and_expires():
    clock = [0.0]
    limiter = AuthRateLimiter(2, clock=lambda: clock[0])
    with ThreadPoolExecutor(max_workers=8) as pool:
        outcomes = list(
            pool.map(lambda _: limiter.retry_after("same-client"), range(20))
        )
    assert outcomes.count(None) == 2
    assert limiter.retry_after("another-client") is None
    clock[0] = 60.1
    assert limiter.retry_after("same-client") is None


def test_rate_limiter_storage_is_bounded():
    limiter = AuthRateLimiter(1, clock=lambda: 0)
    for index in range(4096):
        assert limiter.retry_after(str(index)) is None
    assert limiter.retry_after("new-client") == 60


def test_validation_does_not_echo_passwords_and_auth_is_throttled(settings):
    settings.auth_rate_limit_per_minute = 2
    application = create_app(settings)
    application.dependency_overrides[get_session] = lambda: object()
    with TestClient(application) as client:
        for _ in range(2):
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "p4X!q",
                    "full_name": "Test",
                },
            )
            assert response.status_code == 422
            assert "p4X!q" not in response.text
            assert "input" not in response.text
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "p4X!q",
                "full_name": "Test",
            },
        )
        assert response.status_code == 429
        assert int(response.headers["retry-after"]) > 0
        assert response.headers["cache-control"] == "no-store"


def test_missing_or_invalid_bearer_token_is_401_without_database(settings):
    with TestClient(create_app(settings)) as client:
        for headers in [
            {},
            {"Authorization": "Bearer invalid"},
            {"Authorization": "Basic invalid"},
        ]:
            response = client.get("/api/v1/users/me", headers=headers)
            assert response.status_code == 401
            assert response.headers["www-authenticate"] == "Bearer"
