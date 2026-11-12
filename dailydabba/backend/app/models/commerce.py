"""Carts and order snapshots; no checkout or status-transition services yet."""

from datetime import date, datetime, time
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Computed,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, Record
from app.models.catalog import MEAL_CHECK


class DeliverySlot(Record, Base):
    __tablename__ = "delivery_slots"
    __table_args__ = (
        UniqueConstraint("meal_type", "start_local", "end_local"),
        UniqueConstraint("id", "meal_type"),
        CheckConstraint(MEAL_CHECK, name="meal_type"),
        CheckConstraint("end_local > start_local", name="time_window"),
    )

    name: Mapped[str] = mapped_column(String(80))
    meal_type: Mapped[str] = mapped_column(String(12))
    start_local: Mapped[time] = mapped_column(Time(timezone=False))
    end_local: Mapped[time] = mapped_column(Time(timezone=False))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Cart(Record, Base):
    __tablename__ = "carts"
    __table_args__ = (UniqueConstraint("id", "menu_id"),)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), unique=True
    )
    menu_id: Mapped[UUID] = mapped_column(
        ForeignKey("daily_menus.id", ondelete="RESTRICT"), index=True
    )
    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart", passive_deletes="all"
    )


class CartItem(Record, Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        ForeignKeyConstraint(
            ["cart_id", "menu_id"], ["carts.id", "carts.menu_id"], ondelete="CASCADE"
        ),
        ForeignKeyConstraint(
            ["menu_item_id", "menu_id"],
            ["menu_items.id", "menu_items.menu_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("cart_id", "menu_item_id"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
    )

    cart_id: Mapped[UUID] = mapped_column(index=True)
    menu_id: Mapped[UUID] = mapped_column(index=True)
    menu_item_id: Mapped[UUID] = mapped_column(index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    cart: Mapped[Cart] = relationship(back_populates="items")


class Order(Record, Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        UniqueConstraint("id", "menu_id"),
        UniqueConstraint("user_id", "idempotency_key"),
        ForeignKeyConstraint(
            ["address_id", "user_id"],
            ["addresses.id", "addresses.user_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["menu_id", "business_date", "meal_type"],
            ["daily_menus.id", "daily_menus.business_date", "daily_menus.meal_type"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["delivery_slot_id", "meal_type"],
            ["delivery_slots.id", "delivery_slots.meal_type"],
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "subtotal_paise >= 0 AND delivery_fee_paise >= 0 AND tax_paise >= 0 AND discount_paise >= 0 AND total_paise >= 0",
            name="amounts_nonnegative",
        ),
        CheckConstraint(
            "total_paise = subtotal_paise + delivery_fee_paise + tax_paise - discount_paise",
            name="total_equation",
        ),
        CheckConstraint("delivery_end_at > delivery_start_at", name="delivery_window"),
        CheckConstraint(
            "business_date = (delivery_start_at AT TIME ZONE 'Asia/Kolkata')::date AND business_date = (delivery_end_at AT TIME ZONE 'Asia/Kolkata')::date",
            name="business_date_local",
        ),
        CheckConstraint(
            "jsonb_typeof(address_snapshot) = 'object'", name="address_object"
        ),
        CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name="request_identity",
        ),
        CheckConstraint(
            "status IN ('pending_payment', 'placed', 'confirmed', 'preparing', 'ready', 'out_for_delivery', 'delivered', 'cancelled')",
            name="status",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    address_id: Mapped[UUID] = mapped_column(index=True)
    address_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB)
    menu_id: Mapped[UUID] = mapped_column(index=True)
    business_date: Mapped[date] = mapped_column(Date, index=True)
    meal_type: Mapped[str] = mapped_column(String(12))
    delivery_slot_id: Mapped[UUID] = mapped_column(index=True)
    delivery_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    delivery_end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    subtotal_paise: Mapped[int] = mapped_column(BigInteger)
    delivery_fee_paise: Mapped[int] = mapped_column(BigInteger)
    tax_paise: Mapped[int] = mapped_column(BigInteger)
    discount_paise: Mapped[int] = mapped_column(BigInteger)
    total_paise: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(
        String(24), default="pending_payment", index=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", passive_deletes="all"
    )


class OrderItem(Record, Base):
    __tablename__ = "order_items"
    __table_args__ = (
        ForeignKeyConstraint(
            ["order_id", "menu_id"],
            ["orders.id", "orders.menu_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["menu_item_id", "menu_id"],
            ["menu_items.id", "menu_items.menu_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("order_id", "menu_item_id"),
        CheckConstraint("quantity > 0 AND unit_price_paise >= 0", name="item_amount"),
    )

    order_id: Mapped[UUID] = mapped_column(index=True)
    menu_id: Mapped[UUID] = mapped_column(index=True)
    menu_item_id: Mapped[UUID] = mapped_column(index=True)
    food_name: Mapped[str] = mapped_column(String(120))
    unit_price_paise: Mapped[int] = mapped_column(BigInteger)
    quantity: Mapped[int] = mapped_column(Integer)
    line_total_paise: Mapped[int] = mapped_column(
        BigInteger, Computed("unit_price_paise * quantity", persisted=True)
    )
    order: Mapped[Order] = relationship(back_populates="items")
