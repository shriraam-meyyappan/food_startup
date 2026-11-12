"""Payment evidence, refund requests and deduplicated provider event records."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Record


class Payment(Record, Base):
    __tablename__ = "payments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["order_id", "user_id"],
            ["orders.id", "orders.user_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["subscription_id", "user_id"],
            ["subscriptions.id", "subscriptions.user_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("user_id", "idempotency_key"),
        UniqueConstraint("provider", "provider_payment_id"),
        CheckConstraint(
            "(order_id IS NOT NULL AND subscription_id IS NULL) OR (order_id IS NULL AND subscription_id IS NOT NULL)",
            name="one_target",
        ),
        CheckConstraint(
            "amount_paise > 0 AND currency = 'INR'", name="amount_currency"
        ),
        CheckConstraint("provider = 'razorpay'", name="provider"),
        CheckConstraint(
            "status IN ('created', 'authorized', 'captured', 'failed')", name="status"
        ),
        CheckConstraint(
            "(status = 'captured') = (captured_at IS NOT NULL)", name="capture_instant"
        ),
        CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name="request_identity",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    order_id: Mapped[UUID | None] = mapped_column(index=True)
    subscription_id: Mapped[UUID | None] = mapped_column(index=True)
    amount_paise: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    provider: Mapped[str] = mapped_column(String(20), default="razorpay")
    provider_order_id: Mapped[str | None] = mapped_column(String(100), index=True)
    provider_payment_id: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(16), default="created", index=True)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))


class Refund(Record, Base):
    __tablename__ = "refunds"
    __table_args__ = (
        UniqueConstraint("payment_id", "idempotency_key"),
        UniqueConstraint("provider_refund_id"),
        CheckConstraint("amount_paise > 0", name="amount_positive"),
        CheckConstraint(
            "status IN ('requested', 'processing', 'succeeded', 'failed')",
            name="status",
        ),
        CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name="request_identity",
        ),
    )

    payment_id: Mapped[UUID] = mapped_column(
        ForeignKey("payments.id", ondelete="RESTRICT"), index=True
    )
    amount_paise: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(16), default="requested")
    reason: Mapped[str] = mapped_column(String(300))
    provider_refund_id: Mapped[str | None] = mapped_column(String(100))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))


class PaymentWebhookEvent(Record, Base):
    __tablename__ = "payment_webhook_events"
    __table_args__ = (
        UniqueConstraint("provider", "provider_event_id"),
        CheckConstraint("provider = 'razorpay'", name="provider"),
        CheckConstraint("status IN ('received', 'processed', 'failed')", name="status"),
        CheckConstraint(
            "length(provider_event_id) > 0 AND length(payload_hash) = 64",
            name="event_identity",
        ),
        CheckConstraint(
            "jsonb_typeof(sanitized_payload) = 'object'", name="payload_object"
        ),
    )

    provider: Mapped[str] = mapped_column(String(20), default="razorpay")
    provider_event_id: Mapped[str] = mapped_column(String(150))
    payment_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("payments.id", ondelete="RESTRICT"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(100))
    payload_hash: Mapped[str] = mapped_column(String(64))
    sanitized_payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(16), default="received", index=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
