"""Accounts, private profile data and soft-deletable address book entries."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, Record


class User(Record, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "email = lower(email) AND length(email) > 3", name="email_normalized"
        ),
        CheckConstraint("role IN ('customer', 'admin', 'kitchen_staff')", name="role"),
    )

    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    role: Mapped[str] = mapped_column(String(20), default="customer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    profile: Mapped["CustomerProfile | None"] = relationship(back_populates="user")
    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user", passive_deletes="all"
    )


class CustomerProfile(Record, Base):
    __tablename__ = "customer_profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), unique=True
    )
    full_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str | None] = mapped_column(String(20))
    user: Mapped[User] = relationship(back_populates="profile")


class Address(Record, Base):
    __tablename__ = "addresses"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        CheckConstraint("length(postal_code) = 6", name="postal_code_length"),
        CheckConstraint(
            "NOT is_default OR deleted_at IS NULL", name="default_not_deleted"
        ),
        Index(
            "uq_addresses_one_live_default",
            "user_id",
            unique=True,
            postgresql_where=text("is_default AND deleted_at IS NULL"),
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    label: Mapped[str] = mapped_column(String(50))
    recipient_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(20))
    line1: Mapped[str] = mapped_column(String(200))
    line2: Mapped[str | None] = mapped_column(String(200))
    locality: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(80))
    state: Mapped[str] = mapped_column(String(80))
    postal_code: Mapped[str] = mapped_column(String(6))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user: Mapped[User] = relationship(back_populates="addresses")
