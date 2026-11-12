"""Assemble the version 1 API independently of the application entry point."""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.readiness import router as readiness_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)

api_router.include_router(readiness_router)
