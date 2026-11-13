"""Safe API error responses; never echo validation inputs or SQL parameters."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import AuthNotConfigured, InvalidCredentials
from app.services.auth import AccountExists
from app.services.profiles import ProfileNameRequired

logger = logging.getLogger(__name__)


def install_error_handlers(application: FastAPI) -> None:
    @application.exception_handler(RequestValidationError)
    async def invalid_input(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": [
                    {"loc": list(item["loc"]), "type": item["type"], "msg": item["msg"]}
                    for item in error.errors()
                ]
            },
        )

    @application.exception_handler(InvalidCredentials)
    async def invalid_credentials(
        request: Request, error: InvalidCredentials
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or expired credentials"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @application.exception_handler(AuthNotConfigured)
    async def unavailable_auth(
        request: Request, error: AuthNotConfigured
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503, content={"detail": "Authentication unavailable"}
        )

    @application.exception_handler(AccountExists)
    async def duplicate_account(request: Request, error: AccountExists) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": "An account already exists for this email"},
        )

    @application.exception_handler(ProfileNameRequired)
    async def profile_name_required(
        request: Request, error: ProfileNameRequired
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": "full_name is required to create a profile"},
        )

    @application.exception_handler(SQLAlchemyError)
    async def database_error(request: Request, error: SQLAlchemyError) -> JSONResponse:
        logger.error("Database request failed")
        return JSONResponse(status_code=503, content={"detail": "Database unavailable"})
