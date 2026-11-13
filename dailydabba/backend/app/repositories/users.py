"""User persistence; no HTTP decisions and no independent commits."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, selectinload

from app.models.identity import User


def by_email(session: Session, email: str) -> User | None:
    return session.scalar(
        select(User).where(User.email == email).options(selectinload(User.profile))
    )


def by_id(session: Session, user_id: UUID) -> User | None:
    return session.scalar(
        select(User).where(User.id == user_id).options(selectinload(User.profile))
    )


def insert_account(
    session: Session, *, email: str, password_hash: str, role: str
) -> User | None:
    """Unique email handles concurrent registration without a pre-check race."""
    return session.scalar(
        insert(User)
        .values(
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
        )
        .on_conflict_do_nothing(index_elements=[User.email])
        .returning(User)
    )
