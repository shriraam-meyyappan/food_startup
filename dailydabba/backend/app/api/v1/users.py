"""Self-service profile access, never arbitrary user-ID updates."""

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.db.database import DbSession
from app.schemas.auth import ProfileUpdate, UserResponse
from app.services.profiles import update_profile

router = APIRouter(prefix="/users", tags=["Current user"])


@router.get("/me", response_model=UserResponse)
def me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)


@router.patch("/me/profile", response_model=UserResponse)
def patch_profile(
    payload: ProfileUpdate, user: CurrentUser, session: DbSession
) -> UserResponse:
    return update_profile(session, user, payload)
