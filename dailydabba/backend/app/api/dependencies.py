"""Verified bearer identities and live database-backed role authorization."""

from typing import Annotated, Callable
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings
from app.core.security import decode_access_token
from app.db.database import DbSession
from app.models.identity import User
from app.repositories import users

bearer = HTTPBearer(auto_error=False)


def request_settings(request: Request) -> Settings:
    return request.app.state.settings


RequestSettings = Annotated[Settings, Depends(request_settings)]


def unauthenticated() -> HTTPException:
    return HTTPException(
        401, "Invalid or expired credentials", headers={"WWW-Authenticate": "Bearer"}
    )


def token_subject(
    settings: RequestSettings,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> UUID:
    if credentials is None:
        raise unauthenticated()
    return decode_access_token(credentials.credentials, settings)


def current_user(
    subject: Annotated[UUID, Depends(token_subject)], session: DbSession
) -> User:
    user = users.by_id(session, subject)
    if user is None or not user.is_active or user.deactivated_at is not None:
        raise unauthenticated()
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def require_roles(*roles: str) -> Callable:
    def authorize(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(403, "Insufficient permissions")
        return user

    return authorize


def throttle_auth(request: Request) -> None:
    host = request.client.host if request.client else "unknown"
    retry = request.app.state.auth_limiter.retry_after(host + ":" + request.url.path)
    if retry is not None:
        raise HTTPException(
            429, "Too many authentication requests", headers={"Retry-After": str(retry)}
        )
