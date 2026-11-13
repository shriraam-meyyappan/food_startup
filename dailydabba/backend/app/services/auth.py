"""Account and authentication use cases own their transactions."""

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import (
    InvalidCredentials,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.identity import CustomerProfile
from app.models.operations import AuditLog
from app.repositories import users
from app.schemas.auth import RegisterRequest, TokenResponse, UserResponse


class AccountExists(Exception):
    pass


def create_account(
    session: Session, payload: RegisterRequest, *, role: str = "customer"
) -> UserResponse:
    """Only trusted code supplies role; the public route always calls register()."""
    if role not in {"customer", "admin", "kitchen_staff"}:
        raise ValueError("Unsupported role")
    password_hash = hash_password(payload.password.get_secret_value())
    with session.begin():
        user = users.insert_account(
            session,
            email=str(payload.email).lower(),
            password_hash=password_hash,
            role=role,
        )
        if user is None:
            raise AccountExists()
        user.profile = CustomerProfile(
            user_id=user.id, full_name=payload.full_name, phone=payload.phone
        )
        session.add(
            AuditLog(
                actor_user_id=None,
                action=(
                    "account_registered"
                    if role == "customer"
                    else "staff_account_created"
                ),
                target_type="users",
                target_id=user.id,
                details={"role": role},
            )
        )
        session.flush()
        response = UserResponse.model_validate(user)
    return response


def register(session: Session, payload: RegisterRequest) -> UserResponse:
    return create_account(session, payload, role="customer")


def login(
    session: Session, email: str, password: str, settings: Settings
) -> TokenResponse:
    with session.begin():
        user = users.by_email(session, email.lower())
        valid, upgraded_hash = verify_password(
            password, user.password_hash if user else None
        )
        if (
            not valid
            or user is None
            or not user.is_active
            or user.deactivated_at is not None
        ):
            raise InvalidCredentials()
        if upgraded_hash:
            user.password_hash = upgraded_hash
        token = create_access_token(user.id, settings)
    return TokenResponse(
        access_token=token, expires_in=settings.access_token_minutes * 60
    )
