"""Frontend-independent JSON registration and password login endpoints."""

from fastapi import APIRouter, Depends

from app.api.dependencies import RequestSettings, throttle_auth
from app.core.security import require_signing_key
from app.db.database import DbSession
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services import auth

router = APIRouter(
    prefix="/auth", tags=["Authentication"], dependencies=[Depends(throttle_auth)]
)


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, session: DbSession) -> UserResponse:
    return auth.register(session, payload)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest, settings: RequestSettings, session: DbSession
) -> TokenResponse:
    require_signing_key(settings)
    return auth.login(
        session, str(payload.email), payload.password.get_secret_value(), settings
    )
