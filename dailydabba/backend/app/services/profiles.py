"""Update only the authenticated user's permitted profile fields."""

from sqlalchemy.orm import Session

from app.models.identity import CustomerProfile, User
from app.models.operations import AuditLog
from app.schemas.auth import ProfileUpdate, UserResponse


class ProfileNameRequired(Exception):
    pass


def update_profile(
    session: Session, user: User, payload: ProfileUpdate
) -> UserResponse:
    if user.profile is None:
        if payload.full_name is None:
            raise ProfileNameRequired()
        user.profile = CustomerProfile(user_id=user.id, full_name=payload.full_name)
    for field in payload.model_fields_set:
        setattr(user.profile, field, getattr(payload, field))
    session.add(
        AuditLog(
            actor_user_id=user.id,
            action="profile_updated",
            target_type="users",
            target_id=user.id,
            details={"fields": sorted(payload.model_fields_set)},
        )
    )
    # The current-user lookup already started this request's transaction.
    session.flush()
    response = UserResponse.model_validate(user)
    session.commit()
    return response
