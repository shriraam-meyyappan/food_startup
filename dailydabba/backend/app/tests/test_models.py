"""Check model wiring and PostgreSQL DDL, without claiming database integration."""

from sqlalchemy import DateTime, Float, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.orm import configure_mappers
from sqlalchemy.schema import CreateIndex

import app.models  # noqa: F401
from app.db.base import Base
from app.db.export_schema import render_schema
from app.models.commerce import Order, OrderItem
from app.models.identity import Address
from app.models.subscriptions import CreditTransaction


def test_all_mappings_and_foreign_keys_resolve() -> None:
    configure_mappers()
    assert len(Base.metadata.tables) == 23
    for table in Base.metadata.sorted_tables:
        for foreign_key in table.foreign_keys:
            assert foreign_key.column.table in Base.metadata.tables.values()


def test_schema_compiles_for_postgresql_without_a_driver() -> None:
    ddl = render_schema()
    assert ddl.count("CREATE TABLE ") == 23
    assert "TIMESTAMP WITH TIME ZONE" in ddl
    assert "JSONB" in ddl
    assert "GENERATED ALWAYS AS (unit_price_paise * quantity) STORED" in ddl
    assert "AT TIME ZONE 'Asia/Kolkata'" in ddl


def test_all_money_is_exact_and_all_event_timestamps_are_timezone_aware() -> None:
    for table in Base.metadata.tables.values():
        for column in table.columns:
            assert not isinstance(column.type, Float)
            if isinstance(column.type, DateTime):
                assert column.type.timezone
            if column.name.endswith("_paise"):
                assert column.type.python_type is int


def test_owned_order_address_uses_one_composite_foreign_key() -> None:
    constraints = [
        c for c in Order.__table__.constraints if isinstance(c, ForeignKeyConstraint)
    ]
    ownership = next(
        c for c in constraints if set(c.column_keys) == {"address_id", "user_id"}
    )
    assert [element.target_fullname for element in ownership.elements] == [
        "addresses.id",
        "addresses.user_id",
    ]


def test_default_address_uniqueness_only_applies_to_live_defaults() -> None:
    index = next(
        i
        for i in Address.__table__.indexes
        if i.name == "uq_addresses_one_live_default"
    )
    ddl = str(CreateIndex(index).compile(dialect=dialect()))
    assert "UNIQUE INDEX" in ddl
    assert "WHERE is_default AND deleted_at IS NULL" in ddl


def test_financial_history_has_no_cascading_delete() -> None:
    for table in Base.metadata.tables.values():
        for foreign_key in table.foreign_keys:
            if foreign_key.ondelete == "CASCADE":
                assert table.name == "cart_items"
    assert OrderItem.__table__.c.line_total_paise.computed is not None


def test_credit_retry_and_business_event_both_have_unique_keys() -> None:
    keys = {
        tuple(c.columns.keys())
        for c in CreditTransaction.__table__.constraints
        if isinstance(c, UniqueConstraint)
    }
    assert ("account_id", "event_key") in keys
    assert ("account_id", "order_id", "kind") in keys


def test_renewal_owner_and_purchase_grant_guards_compile() -> None:
    subscription = Base.metadata.tables["subscriptions"]
    constraints = [
        c for c in subscription.constraints if isinstance(c, ForeignKeyConstraint)
    ]
    renewal = next(
        c for c in constraints if set(c.column_keys) == {"renewed_from_id", "user_id"}
    )
    assert [e.target_fullname for e in renewal.elements] == [
        "subscriptions.id",
        "subscriptions.user_id",
    ]
    index = next(
        i
        for i in CreditTransaction.__table__.indexes
        if i.name == "uq_credit_account_purchase_grant"
    )
    ddl = str(CreateIndex(index).compile(dialect=dialect()))
    assert "UNIQUE INDEX" in ddl
    assert "WHERE kind = 'grant'" in ddl
