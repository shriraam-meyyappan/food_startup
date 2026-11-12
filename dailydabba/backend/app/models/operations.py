"""Kitchen work, notifications and minimal audit evidence."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Record


class KitchenOrder(Record, Base):
    __tablename__ = "kitchen_orders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('queued', 'preparing', 'ready', 'completed', 'cancelled')",
            name="status",
        ),
    )

    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="RESTRICT"), unique=True
    )
    status: Mapped[str] = mapped_column(String(16), default="queued", index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Notification(Record, Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint("channel IN ('in_app', 'email', 'sms')", name="channel"),
        CheckConstraint(
            "status IN ('pending', 'sent', 'failed', 'read')", name="status"
        ),
        CheckConstraint("jsonb_typeof(payload) = 'object'", name="payload_object"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    event_key: Mapped[str] = mapped_column(String(150), unique=True)
    channel: Mapped[str] = mapped_column(String(12))
    status: Mapped[str] = mapped_column(String(12), default="pending", index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditLog(Record, Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        CheckConstraint("jsonb_typeof(details) = 'object'", name="details_object"),
    )

    actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    action: Mapped[str] = mapped_column(String(100))
    target_type: Mapped[str] = mapped_column(String(80))
    target_id: Mapped[UUID] = mapped_column(index=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB)
