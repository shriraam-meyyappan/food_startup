"""Subscription terms, lifecycle history and an auditable credit ledger."""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Record
from app.models.catalog import MEAL_CHECK


class SubscriptionPlan(Record, Base):
    __tablename__ = "subscription_plans"
    __table_args__ = (
        CheckConstraint("period IN ('weekly', 'monthly')", name="period"),
        CheckConstraint(MEAL_CHECK, name="meal_type"),
        CheckConstraint(
            "duration_days > 0 AND included_credits > 0 AND price_paise >= 0",
            name="terms_positive",
        ),
    )

    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    period: Mapped[str] = mapped_column(String(12))
    meal_type: Mapped[str] = mapped_column(String(12))
    duration_days: Mapped[int] = mapped_column(Integer)
    included_credits: Mapped[int] = mapped_column(Integer)
    price_paise: Mapped[int] = mapped_column(BigInteger)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)


class Subscription(Record, Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        ForeignKeyConstraint(
            ["renewed_from_id", "user_id"],
            ["subscriptions.id", "subscriptions.user_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("user_id", "idempotency_key"),
        CheckConstraint("expires_on > starts_on", name="date_window"),
        CheckConstraint(
            "purchased_credits > 0 AND price_paise >= 0", name="purchased_terms"
        ),
        CheckConstraint(MEAL_CHECK, name="meal_type"),
        CheckConstraint(
            "status IN ('pending_payment', 'active', 'paused', 'expired', 'cancelled')",
            name="status",
        ),
        CheckConstraint(
            "jsonb_typeof(policy_snapshot) = 'object'", name="policy_object"
        ),
        CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name="request_identity",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("subscription_plans.id", ondelete="RESTRICT"), index=True
    )
    renewed_from_id: Mapped[UUID | None] = mapped_column(index=True)
    plan_name: Mapped[str] = mapped_column(String(120))
    meal_type: Mapped[str] = mapped_column(String(12))
    purchased_credits: Mapped[int] = mapped_column(Integer)
    price_paise: Mapped[int] = mapped_column(BigInteger)
    starts_on: Mapped[date] = mapped_column(Date)
    expires_on: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(20), default="pending_payment", index=True
    )
    policy_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB)
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))


class SubscriptionEvent(Record, Base):
    __tablename__ = "subscription_events"
    __table_args__ = (
        UniqueConstraint("subscription_id", "event_key"),
        CheckConstraint(
            "event_type IN ('activate', 'pause', 'resume', 'skip', 'renew', 'expire', 'cancel')",
            name="event_type",
        ),
        CheckConstraint("length(event_key) > 0", name="event_key"),
        Index(
            "uq_subscription_skip_date",
            "subscription_id",
            "effective_date",
            unique=True,
            postgresql_where=text("event_type = 'skip'"),
        ),
    )

    subscription_id: Mapped[UUID] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="RESTRICT"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(16))
    effective_date: Mapped[date] = mapped_column(Date)
    event_key: Mapped[str] = mapped_column(String(128))
    reason: Mapped[str] = mapped_column(String(300))
    actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )


class CreditAccount(Record, Base):
    __tablename__ = "subscription_credits"
    __table_args__ = (
        ForeignKeyConstraint(
            ["subscription_id", "user_id"],
            ["subscriptions.id", "subscriptions.user_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "user_id"),
        CheckConstraint("balance >= 0", name="balance_nonnegative"),
    )

    subscription_id: Mapped[UUID] = mapped_column(unique=True)
    user_id: Mapped[UUID] = mapped_column(index=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)


class CreditTransaction(Record, Base):
    __tablename__ = "credit_transactions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["account_id", "user_id"],
            ["subscription_credits.id", "subscription_credits.user_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["order_id", "user_id"],
            ["orders.id", "orders.user_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("account_id", "event_key"),
        Index(
            "uq_credit_account_purchase_grant",
            "account_id",
            unique=True,
            postgresql_where=text("kind = 'grant'"),
        ),
        UniqueConstraint("account_id", "order_id", "kind"),
        CheckConstraint("delta <> 0", name="delta_nonzero"),
        CheckConstraint(
            "kind IN ('grant', 'debit', 'restore', 'expire', 'adjust')", name="kind"
        ),
        CheckConstraint(
            "(kind IN ('grant', 'restore') AND delta > 0) OR (kind IN ('debit', 'expire') AND delta < 0) OR kind = 'adjust'",
            name="delta_direction",
        ),
        CheckConstraint(
            "kind NOT IN ('debit', 'restore') OR order_id IS NOT NULL",
            name="order_required",
        ),
        CheckConstraint(
            "length(event_key) > 0 AND length(request_hash) = 64 AND length(reason) > 0",
            name="event_identity",
        ),
    )

    account_id: Mapped[UUID] = mapped_column(index=True)
    user_id: Mapped[UUID] = mapped_column(index=True)
    order_id: Mapped[UUID | None] = mapped_column(index=True)
    kind: Mapped[str] = mapped_column(String(12))
    delta: Mapped[int] = mapped_column(Integer)
    event_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))
    reason: Mapped[str] = mapped_column(String(300))
    actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
