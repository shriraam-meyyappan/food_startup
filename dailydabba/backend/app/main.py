"""FastAPI application entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.db.database import Database

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build one application; tests may supply isolated settings."""
    settings = settings if settings is not None else get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        configure_logging(settings.log_level)
        application.state.database = (
            Database.from_url(settings.database_url) if settings.database_url else None
        )
        logger.info("DailyDabba backend started")
        try:
            yield
        finally:
            if application.state.database is not None:
                application.state.database.dispose()
            logger.info("DailyDabba backend stopped")

    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        debug=False,
    )
    application.include_router(api_router)
    return application


app = create_app()
