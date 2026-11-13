"""Argon2 password hashing and strictly verified short-lived JWT access tokens."""

import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from app.core.config import Settings

_password_hash = PasswordHash.recommended()
_dummy_hash = _password_hash.hash(secrets.token_urlsafe(32))


class InvalidCredentials(Exception):
    pass


class AuthNotConfigured(Exception):
    pass


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, stored_hash: str | None) -> tuple[bool, str | None]:
    """Unknown emails still incur a real Argon2 check; malformed hashes fail closed."""
    try:
        valid, updated = _password_hash.verify_and_update(
            password, stored_hash or _dummy_hash
        )
    except (UnknownHashError, ValueError):
        _password_hash.verify(password, _dummy_hash)
        return False, None
    return valid and bool(stored_hash), updated


def require_signing_key(settings: Settings) -> str:
    if settings.jwt_secret is None:
        raise AuthNotConfigured()
    return settings.jwt_secret.get_secret_value()


def create_access_token(user_id: UUID, settings: Settings) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id),
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=settings.access_token_minutes),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "jti": str(uuid4()),
            "token_type": "access",
        },
        require_signing_key(settings),
        algorithm="HS256",
    )


def decode_access_token(token: str, settings: Settings) -> UUID:
    key = require_signing_key(settings)
    try:
        if len(token) > 4096:
            raise InvalidCredentials()
        payload = jwt.decode(
            token,
            key,
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={
                "require": [
                    "sub",
                    "iat",
                    "nbf",
                    "exp",
                    "iss",
                    "aud",
                    "jti",
                    "token_type",
                ]
            },
        )
        if payload["token_type"] != "access":
            raise InvalidCredentials()
        UUID(payload["jti"])
        return UUID(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError):
        raise InvalidCredentials() from None
