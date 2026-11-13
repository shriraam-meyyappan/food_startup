"""Real PostgreSQL migration, constraint, permissions and session tests.

Run with --run-db. This resets dailydabba_test and never development data.
"""

import os
from datetime import date, datetime, time, timezone
from unittest.mock import patch
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import delete, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

import app.models as models
from app.core.config import BACKEND_ROOT, Settings, get_settings
from app.db.base import Base
from app.db.check import check_database
from app.db.database import Database, DbSession
from app.main import create_app

pytestmark = pytest.mark.database


@pytest.fixture
def session(databases):
    database, _, _ = databases
    with database.engine.connect() as connection:
        transaction = connection.begin()
        with Session(
            bind=connection, join_transaction_mode="create_savepoint"
        ) as session:
            try:
                yield session
            finally:
                session.close()
                transaction.rollback()


@pytest.fixture
def records(session):
    user = models.User(email="one@example.test", password_hash="test-only-hash")
    other = models.User(email="two@example.test", password_hash="test-only-hash")
    category = models.FoodCategory(name="test meals")
    menu = models.DailyMenu(business_date=date(2026, 11, 12), meal_type="lunch")
    slot = models.DeliverySlot(
        name="test slot", meal_type="lunch", start_local=time(12), end_local=time(13)
    )
    plan = models.SubscriptionPlan(
        code="TEST",
        name="test plan",
        period="weekly",
        meal_type="lunch",
        duration_days=7,
        included_credits=5,
        price_paise=25000,
    )
    session.add_all([user, other, category, menu, slot, plan])
    session.flush()
    address = models.Address(
        user_id=user.id,
        label="test",
        recipient_name="test",
        phone="0000000000",
        line1="test street",
        locality="test",
        city="Chennai",
        state="Tamil Nadu",
        postal_code="600001",
        is_default=True,
    )
    other_address = models.Address(
        user_id=other.id,
        label="test",
        recipient_name="test",
        phone="0000000000",
        line1="other street",
        locality="test",
        city="Chennai",
        state="Tamil Nadu",
        postal_code="600002",
    )
    food = models.FoodItem(
        category_id=category.id, name="test food", description="test", price_paise=5000
    )
    subscription = models.Subscription(
        user_id=user.id,
        plan_id=plan.id,
        plan_name=plan.name,
        meal_type="lunch",
        purchased_credits=5,
        price_paise=25000,
        starts_on=date(2026, 11, 12),
        expires_on=date(2026, 11, 19),
        policy_snapshot={"test": True},
        idempotency_key="sub-one",
        request_hash="a" * 64,
    )
    session.add_all([address, other_address, food, subscription])
    session.flush()
    item = models.MenuItem(
        menu_id=menu.id, food_item_id=food.id, price_paise=5000, portions_remaining=10
    )
    account = models.CreditAccount(
        subscription_id=subscription.id, user_id=user.id, balance=5
    )
    session.add_all([item, account])
    session.flush()
    order = models.Order(
        user_id=user.id,
        address_id=address.id,
        address_snapshot={"line1": address.line1},
        menu_id=menu.id,
        business_date=menu.business_date,
        meal_type="lunch",
        delivery_slot_id=slot.id,
        delivery_start_at=datetime(2026, 11, 12, 6, 30, tzinfo=timezone.utc),
        delivery_end_at=datetime(2026, 11, 12, 7, 30, tzinfo=timezone.utc),
        subtotal_paise=10000,
        delivery_fee_paise=0,
        tax_paise=0,
        discount_paise=0,
        total_paise=10000,
        idempotency_key="order-one",
        request_hash="b" * 64,
    )
    session.add(order)
    session.flush()
    line = models.OrderItem(
        order_id=order.id,
        menu_id=menu.id,
        menu_item_id=item.id,
        food_name=food.name,
        unit_price_paise=5000,
        quantity=2,
    )
    grant = models.CreditTransaction(
        account_id=account.id,
        user_id=user.id,
        kind="grant",
        delta=5,
        event_key="purchase",
        request_hash="c" * 64,
        reason="test purchase",
    )
    session.add_all([line, grant])
    session.flush()
    return dict(
        subscription=subscription,
        user=user,
        other=other,
        address=address,
        other_address=other_address,
        food=food,
        menu=menu,
        item=item,
        account=account,
        order=order,
        line=line,
    )


def test_migration_roundtrip_schema_and_no_model_drift(databases):
    database, runtime, migrate = databases
    assert set(inspect(database.engine).get_table_names()) == set(
        Base.metadata.tables
    ) | {"alembic_version"}
    migrate("check")
    with runtime.sessions() as session:
        assert check_database(session)["status"] == "ready"
        assert (
            session.execute(text("SELECT current_user")).scalar_one()
            == "dailydabba_app"
        )


def test_exact_prices_and_historical_snapshots(session, records):
    line = records["line"]
    assert line.line_total_paise == 10000
    records["item"].price_paise = 9999
    session.flush()
    session.refresh(line)
    assert (line.unit_price_paise, line.line_total_paise) == (5000, 10000)
    with pytest.raises(IntegrityError), session.begin_nested():
        records["food"].price_paise = -1
        session.flush()


def test_order_rejects_another_users_address(session, records):
    with pytest.raises(IntegrityError), session.begin_nested():
        records["order"].address_id = records["other_address"].id
        session.flush()


def test_only_one_live_default_address(session, records):
    address = records["address"]
    with pytest.raises(IntegrityError), session.begin_nested():
        session.add(
            models.Address(
                user_id=address.user_id,
                label="duplicate",
                recipient_name="test",
                phone="0000000000",
                line1="test",
                locality="test",
                city="Chennai",
                state="Tamil Nadu",
                postal_code="600003",
                is_default=True,
            )
        )
        session.flush()


def test_nonnegative_credit_balance_and_duplicate_purchase_grant(session, records):
    account = records["account"]
    with pytest.raises(IntegrityError), session.begin_nested():
        account.balance = -1
        session.flush()
    with pytest.raises(IntegrityError), session.begin_nested():
        session.add(
            models.CreditTransaction(
                account_id=account.id,
                user_id=records["user"].id,
                kind="grant",
                delta=5,
                event_key="changed-retry-key",
                request_hash="d" * 64,
                reason="duplicate purchase",
            )
        )
        session.flush()


def test_duplicate_order_idempotency_and_totals_rejected(session, records):
    with pytest.raises(IntegrityError), session.begin_nested():
        records["order"].total_paise = 1
        session.flush()
    with pytest.raises(IntegrityError), session.begin_nested():
        records["order"].delivery_end_at = datetime(
            2026, 11, 13, 7, 30, tzinfo=timezone.utc
        )
        session.flush()
    values = {
        c.name: getattr(records["order"], c.name)
        for c in models.Order.__table__.columns
        if c.name not in {"id", "created_at"}
    }
    with pytest.raises(IntegrityError), session.begin_nested():
        session.add(models.Order(**values))
        session.flush()


def test_order_history_cannot_be_deleted_with_items(session, records):
    with pytest.raises(IntegrityError), session.begin_nested():
        session.execute(
            delete(models.Order).where(models.Order.id == records["order"].id)
        )


@pytest.mark.parametrize(
    "statement",
    [
        "CREATE TABLE public.runtime_must_not_create (id int)",
        "UPDATE public.orders SET subtotal_paise = 0 WHERE false",
        "DELETE FROM public.credit_transactions WHERE false",
        "UPDATE public.audit_logs SET action = 'changed' WHERE false",
        "DELETE FROM public.alembic_version WHERE false",
    ],
)
def test_runtime_role_cannot_change_schema_or_immutable_history(databases, statement):
    _, runtime, _ = databases
    with pytest.raises(DBAPIError) as error:
        with runtime.engine.begin() as connection:
            connection.execute(text(statement))
    assert error.value.orig.sqlstate == "42501"


def test_request_sessions_rollback_uncommitted_work_and_readiness_is_live(databases):
    _, runtime, _ = databases
    url = SecretStr(runtime.engine.url.render_as_string(hide_password=False))
    application = create_app(Settings(_env_file=None, database_url=url))
    unique_name = "rollback-" + str(uuid4())

    @application.post("/test-rollback")
    def write_then_fail(session: DbSession):
        session.add(models.FoodCategory(name=unique_name))
        session.flush()
        raise HTTPException(409, "Deliberate test rollback")

    with TestClient(application) as client:
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/ready").json() == {"status": "ready"}
        assert client.post("/test-rollback").status_code == 409
    with runtime.sessions() as session:
        assert (
            session.execute(
                text("SELECT count(*) FROM food_categories WHERE name = :name"),
                {"name": unique_name},
            ).scalar_one()
            == 0
        )


def test_payment_targets_provider_uniqueness_and_refund_amounts(session, records):
    payment = models.Payment(
        user_id=records["user"].id,
        order_id=records["order"].id,
        amount_paise=10000,
        provider_payment_id="test-provider-id",
        idempotency_key="attempt-one",
        request_hash="e" * 64,
    )
    session.add(payment)
    session.flush()
    with pytest.raises(IntegrityError), session.begin_nested():
        payment.subscription_id = records["subscription"].id
        session.flush()
    with pytest.raises(IntegrityError), session.begin_nested():
        session.add(
            models.Payment(
                user_id=records["user"].id,
                order_id=records["order"].id,
                amount_paise=10000,
                provider_payment_id="test-provider-id",
                idempotency_key="different-request",
                request_hash="f" * 64,
            )
        )
        session.flush()
    with pytest.raises(IntegrityError), session.begin_nested():
        session.add(
            models.Refund(
                payment_id=payment.id,
                amount_paise=-1,
                reason="invalid amount",
                idempotency_key="refund-one",
                request_hash="a" * 64,
            )
        )
        session.flush()
