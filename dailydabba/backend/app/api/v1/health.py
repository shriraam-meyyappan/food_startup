"""Process health endpoint; database readiness is a later phase."""

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return HTTP 200 when this application can serve requests."""
    return HealthResponse(status="ok")
