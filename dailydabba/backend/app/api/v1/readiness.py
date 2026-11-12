"""Database readiness is separate from process liveness."""

import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.db.check import DatabaseNotReady, check_database
from app.db.database import DbSession
from app.schemas.health import ReadinessResponse

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


@router.get("/ready", response_model=ReadinessResponse)
def readiness(session: DbSession) -> ReadinessResponse:
    """Require a reachable, UTC-configured database at the current migration head."""
    try:
        check_database(session)
    except (SQLAlchemyError, DatabaseNotReady):
        logger.warning("Database readiness check failed")
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    return ReadinessResponse(status="ready")
