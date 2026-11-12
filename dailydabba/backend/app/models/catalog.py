"""Catalog prices and dated, meal-specific kitchen offerings."""

from datetime import date
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, Record

MEAL_CHECK = "meal_type IN ('breakfast', 'lunch', 'dinner')"


class FoodCategory(Record, Base):
    __tablename__ = "food_categories"

    name: Mapped[str] = mapped_column(String(80), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    items: Mapped[list["FoodItem"]] = relationship(
        back_populates="category", passive_deletes="all"
    )


class FoodItem(Record, Base):
    __tablename__ = "food_items"
    __table_args__ = (CheckConstraint("price_paise >= 0", name="price_nonnegative"),)

    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("food_categories.id", ondelete="RESTRICT"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    price_paise: Mapped[int] = mapped_column(BigInteger)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=False)
    category: Mapped[FoodCategory] = relationship(back_populates="items")


class DailyMenu(Record, Base):
    __tablename__ = "daily_menus"
    __table_args__ = (
        UniqueConstraint("business_date", "meal_type"),
        UniqueConstraint("id", "business_date", "meal_type"),
        CheckConstraint(MEAL_CHECK, name="meal_type"),
    )

    business_date: Mapped[date] = mapped_column(Date)
    meal_type: Mapped[str] = mapped_column(String(12))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    items: Mapped[list["MenuItem"]] = relationship(
        back_populates="menu", passive_deletes="all"
    )


class MenuItem(Record, Base):
    __tablename__ = "menu_items"
    __table_args__ = (
        UniqueConstraint("menu_id", "food_item_id"),
        UniqueConstraint("id", "menu_id"),
        CheckConstraint("price_paise >= 0", name="price_nonnegative"),
        CheckConstraint("portions_remaining >= 0", name="stock_nonnegative"),
    )

    menu_id: Mapped[UUID] = mapped_column(
        ForeignKey("daily_menus.id", ondelete="RESTRICT"), index=True
    )
    food_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("food_items.id", ondelete="RESTRICT"), index=True
    )
    price_paise: Mapped[int] = mapped_column(BigInteger)
    portions_remaining: Mapped[int] = mapped_column(Integer, default=0)
    is_available: Mapped[bool] = mapped_column(Boolean, default=False)
    menu: Mapped[DailyMenu] = relationship(back_populates="items")
    food_item: Mapped[FoodItem] = relationship()
