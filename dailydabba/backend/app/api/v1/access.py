"""Role-guard demonstrations only; operational APIs remain Phase 12 work."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import require_roles
from app.models.identity import User
from app.schemas.auth import AccessResponse

router = APIRouter(tags=["Role access checks"])


@router.get("/admin/access-check", response_model=AccessResponse)
def admin_access(
    user: Annotated[User, Depends(require_roles("admin"))],
) -> AccessResponse:
    return AccessResponse(role=user.role)


@router.get("/kitchen/access-check", response_model=AccessResponse)
def kitchen_access(
    user: Annotated[User, Depends(require_roles("admin", "kitchen_staff"))],
) -> AccessResponse:
    return AccessResponse(role=user.role)
