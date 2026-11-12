"""initial database schema

Revision ID: 0001_initial
Revises: none
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Reviewed initial schema and explicit runtime grants.
    op.create_table(
        "daily_menus",
        sa.Column("business_date", sa.Date(), nullable=False),
        sa.Column("meal_type", sa.String(length=12), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "meal_type IN ('breakfast', 'lunch', 'dinner')",
            name=op.f("ck_daily_menus_meal_type"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_menus")),
        sa.UniqueConstraint(
            "business_date",
            "meal_type",
            name=op.f("uq_daily_menus_business_date_meal_type"),
        ),
        sa.UniqueConstraint(
            "id",
            "business_date",
            "meal_type",
            name=op.f("uq_daily_menus_id_business_date_meal_type"),
        ),
    )
    op.create_table(
        "delivery_slots",
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("meal_type", sa.String(length=12), nullable=False),
        sa.Column("start_local", sa.Time(), nullable=False),
        sa.Column("end_local", sa.Time(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "meal_type IN ('breakfast', 'lunch', 'dinner')",
            name=op.f("ck_delivery_slots_meal_type"),
        ),
        sa.CheckConstraint(
            "end_local > start_local", name=op.f("ck_delivery_slots_time_window")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_delivery_slots")),
        sa.UniqueConstraint(
            "id", "meal_type", name=op.f("uq_delivery_slots_id_meal_type")
        ),
        sa.UniqueConstraint(
            "meal_type",
            "start_local",
            "end_local",
            name=op.f("uq_delivery_slots_meal_type_start_local_end_local"),
        ),
    )
    op.create_table(
        "food_categories",
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_food_categories")),
        sa.UniqueConstraint("name", name=op.f("uq_food_categories_name")),
    )
    op.create_table(
        "subscription_plans",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("period", sa.String(length=12), nullable=False),
        sa.Column("meal_type", sa.String(length=12), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("included_credits", sa.Integer(), nullable=False),
        sa.Column("price_paise", sa.BigInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "meal_type IN ('breakfast', 'lunch', 'dinner')",
            name=op.f("ck_subscription_plans_meal_type"),
        ),
        sa.CheckConstraint(
            "period IN ('weekly', 'monthly')", name=op.f("ck_subscription_plans_period")
        ),
        sa.CheckConstraint(
            "duration_days > 0 AND included_credits > 0 AND price_paise >= 0",
            name=op.f("ck_subscription_plans_terms_positive"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscription_plans")),
        sa.UniqueConstraint("code", name=op.f("uq_subscription_plans_code")),
    )
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "role IN ('customer', 'admin', 'kitchen_staff')", name=op.f("ck_users_role")
        ),
        sa.CheckConstraint(
            "email = lower(email) AND length(email) > 3",
            name=op.f("ck_users_email_normalized"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_table(
        "addresses",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("label", sa.String(length=50), nullable=False),
        sa.Column("recipient_name", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("line1", sa.String(length=200), nullable=False),
        sa.Column("line2", sa.String(length=200), nullable=True),
        sa.Column("locality", sa.String(length=120), nullable=False),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("state", sa.String(length=80), nullable=False),
        sa.Column("postal_code", sa.String(length=6), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "NOT is_default OR deleted_at IS NULL",
            name=op.f("ck_addresses_default_not_deleted"),
        ),
        sa.CheckConstraint(
            "length(postal_code) = 6", name=op.f("ck_addresses_postal_code_length")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_addresses_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_addresses")),
        sa.UniqueConstraint("id", "user_id", name=op.f("uq_addresses_id_user_id")),
    )
    op.create_index(
        op.f("ix_addresses_user_id"), "addresses", ["user_id"], unique=False
    )
    op.create_index(
        "uq_addresses_one_live_default",
        "addresses",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_default AND deleted_at IS NULL"),
    )
    op.create_table(
        "audit_logs",
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "jsonb_typeof(details) = 'object'",
            name=op.f("ck_audit_logs_details_object"),
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name=op.f("fk_audit_logs_actor_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )
    op.create_index(
        op.f("ix_audit_logs_actor_user_id"),
        "audit_logs",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_logs_target_id"), "audit_logs", ["target_id"], unique=False
    )
    op.create_table(
        "carts",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("menu_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["menu_id"],
            ["daily_menus.id"],
            name=op.f("fk_carts_menu_id_daily_menus"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_carts_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_carts")),
        sa.UniqueConstraint("id", "menu_id", name=op.f("uq_carts_id_menu_id")),
        sa.UniqueConstraint("user_id", name=op.f("uq_carts_user_id")),
    )
    op.create_index(op.f("ix_carts_menu_id"), "carts", ["menu_id"], unique=False)
    op.create_table(
        "customer_profiles",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_customer_profiles_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_customer_profiles")),
        sa.UniqueConstraint("user_id", name=op.f("uq_customer_profiles_user_id")),
    )
    op.create_table(
        "food_items",
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price_paise", sa.BigInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "price_paise >= 0", name=op.f("ck_food_items_price_nonnegative")
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["food_categories.id"],
            name=op.f("fk_food_items_category_id_food_categories"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_food_items")),
    )
    op.create_index(
        op.f("ix_food_items_category_id"), "food_items", ["category_id"], unique=False
    )
    op.create_table(
        "notifications",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("event_key", sa.String(length=150), nullable=False),
        sa.Column("channel", sa.String(length=12), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "channel IN ('in_app', 'email', 'sms')",
            name=op.f("ck_notifications_channel"),
        ),
        sa.CheckConstraint(
            "jsonb_typeof(payload) = 'object'",
            name=op.f("ck_notifications_payload_object"),
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'sent', 'failed', 'read')",
            name=op.f("ck_notifications_status"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_notifications_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
        sa.UniqueConstraint("event_key", name=op.f("uq_notifications_event_key")),
    )
    op.create_index(
        op.f("ix_notifications_status"), "notifications", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False
    )
    op.create_table(
        "subscriptions",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("renewed_from_id", sa.Uuid(), nullable=True),
        sa.Column("plan_name", sa.String(length=120), nullable=False),
        sa.Column("meal_type", sa.String(length=12), nullable=False),
        sa.Column("purchased_credits", sa.Integer(), nullable=False),
        sa.Column("price_paise", sa.BigInteger(), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("expires_on", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "policy_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "jsonb_typeof(policy_snapshot) = 'object'",
            name=op.f("ck_subscriptions_policy_object"),
        ),
        sa.CheckConstraint(
            "meal_type IN ('breakfast', 'lunch', 'dinner')",
            name=op.f("ck_subscriptions_meal_type"),
        ),
        sa.CheckConstraint(
            "status IN ('pending_payment', 'active', 'paused', 'expired', 'cancelled')",
            name=op.f("ck_subscriptions_status"),
        ),
        sa.CheckConstraint(
            "expires_on > starts_on", name=op.f("ck_subscriptions_date_window")
        ),
        sa.CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name=op.f("ck_subscriptions_request_identity"),
        ),
        sa.CheckConstraint(
            "purchased_credits > 0 AND price_paise >= 0",
            name=op.f("ck_subscriptions_purchased_terms"),
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["subscription_plans.id"],
            name=op.f("fk_subscriptions_plan_id_subscription_plans"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["renewed_from_id", "user_id"],
            ["subscriptions.id", "subscriptions.user_id"],
            name=op.f("fk_subscriptions_renewed_from_id_user_id_subscriptions"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_subscriptions_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscriptions")),
        sa.UniqueConstraint("id", "user_id", name=op.f("uq_subscriptions_id_user_id")),
        sa.UniqueConstraint(
            "user_id",
            "idempotency_key",
            name=op.f("uq_subscriptions_user_id_idempotency_key"),
        ),
    )
    op.create_index(
        op.f("ix_subscriptions_plan_id"), "subscriptions", ["plan_id"], unique=False
    )
    op.create_index(
        op.f("ix_subscriptions_renewed_from_id"),
        "subscriptions",
        ["renewed_from_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscriptions_status"), "subscriptions", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_subscriptions_user_id"), "subscriptions", ["user_id"], unique=False
    )
    op.create_table(
        "menu_items",
        sa.Column("menu_id", sa.Uuid(), nullable=False),
        sa.Column("food_item_id", sa.Uuid(), nullable=False),
        sa.Column("price_paise", sa.BigInteger(), nullable=False),
        sa.Column("portions_remaining", sa.Integer(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "portions_remaining >= 0", name=op.f("ck_menu_items_stock_nonnegative")
        ),
        sa.CheckConstraint(
            "price_paise >= 0", name=op.f("ck_menu_items_price_nonnegative")
        ),
        sa.ForeignKeyConstraint(
            ["food_item_id"],
            ["food_items.id"],
            name=op.f("fk_menu_items_food_item_id_food_items"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["menu_id"],
            ["daily_menus.id"],
            name=op.f("fk_menu_items_menu_id_daily_menus"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_menu_items")),
        sa.UniqueConstraint("id", "menu_id", name=op.f("uq_menu_items_id_menu_id")),
        sa.UniqueConstraint(
            "menu_id", "food_item_id", name=op.f("uq_menu_items_menu_id_food_item_id")
        ),
    )
    op.create_index(
        op.f("ix_menu_items_food_item_id"), "menu_items", ["food_item_id"], unique=False
    )
    op.create_index(
        op.f("ix_menu_items_menu_id"), "menu_items", ["menu_id"], unique=False
    )
    op.create_table(
        "orders",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("address_id", sa.Uuid(), nullable=False),
        sa.Column(
            "address_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("menu_id", sa.Uuid(), nullable=False),
        sa.Column("business_date", sa.Date(), nullable=False),
        sa.Column("meal_type", sa.String(length=12), nullable=False),
        sa.Column("delivery_slot_id", sa.Uuid(), nullable=False),
        sa.Column("delivery_start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivery_end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("subtotal_paise", sa.BigInteger(), nullable=False),
        sa.Column("delivery_fee_paise", sa.BigInteger(), nullable=False),
        sa.Column("tax_paise", sa.BigInteger(), nullable=False),
        sa.Column("discount_paise", sa.BigInteger(), nullable=False),
        sa.Column("total_paise", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "business_date = (delivery_start_at AT TIME ZONE 'Asia/Kolkata')::date AND business_date = (delivery_end_at AT TIME ZONE 'Asia/Kolkata')::date",
            name=op.f("ck_orders_business_date_local"),
        ),
        sa.CheckConstraint(
            "jsonb_typeof(address_snapshot) = 'object'",
            name=op.f("ck_orders_address_object"),
        ),
        sa.CheckConstraint(
            "status IN ('pending_payment', 'placed', 'confirmed', 'preparing', 'ready', 'out_for_delivery', 'delivered', 'cancelled')",
            name=op.f("ck_orders_status"),
        ),
        sa.CheckConstraint(
            "delivery_end_at > delivery_start_at",
            name=op.f("ck_orders_delivery_window"),
        ),
        sa.CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name=op.f("ck_orders_request_identity"),
        ),
        sa.CheckConstraint(
            "subtotal_paise >= 0 AND delivery_fee_paise >= 0 AND tax_paise >= 0 AND discount_paise >= 0 AND total_paise >= 0",
            name=op.f("ck_orders_amounts_nonnegative"),
        ),
        sa.CheckConstraint(
            "total_paise = subtotal_paise + delivery_fee_paise + tax_paise - discount_paise",
            name=op.f("ck_orders_total_equation"),
        ),
        sa.ForeignKeyConstraint(
            ["address_id", "user_id"],
            ["addresses.id", "addresses.user_id"],
            name=op.f("fk_orders_address_id_user_id_addresses"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["delivery_slot_id", "meal_type"],
            ["delivery_slots.id", "delivery_slots.meal_type"],
            name=op.f("fk_orders_delivery_slot_id_meal_type_delivery_slots"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["menu_id", "business_date", "meal_type"],
            ["daily_menus.id", "daily_menus.business_date", "daily_menus.meal_type"],
            name=op.f("fk_orders_menu_id_business_date_meal_type_daily_menus"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_orders_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orders")),
        sa.UniqueConstraint("id", "menu_id", name=op.f("uq_orders_id_menu_id")),
        sa.UniqueConstraint("id", "user_id", name=op.f("uq_orders_id_user_id")),
        sa.UniqueConstraint(
            "user_id", "idempotency_key", name=op.f("uq_orders_user_id_idempotency_key")
        ),
    )
    op.create_index(
        op.f("ix_orders_address_id"), "orders", ["address_id"], unique=False
    )
    op.create_index(
        op.f("ix_orders_business_date"), "orders", ["business_date"], unique=False
    )
    op.create_index(
        op.f("ix_orders_delivery_slot_id"), "orders", ["delivery_slot_id"], unique=False
    )
    op.create_index(op.f("ix_orders_menu_id"), "orders", ["menu_id"], unique=False)
    op.create_index(op.f("ix_orders_status"), "orders", ["status"], unique=False)
    op.create_index(op.f("ix_orders_user_id"), "orders", ["user_id"], unique=False)
    op.create_table(
        "subscription_credits",
        sa.Column("subscription_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("balance", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "balance >= 0", name=op.f("ck_subscription_credits_balance_nonnegative")
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id", "user_id"],
            ["subscriptions.id", "subscriptions.user_id"],
            name=op.f("fk_subscription_credits_subscription_id_user_id_subscriptions"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscription_credits")),
        sa.UniqueConstraint(
            "id", "user_id", name=op.f("uq_subscription_credits_id_user_id")
        ),
        sa.UniqueConstraint(
            "subscription_id", name=op.f("uq_subscription_credits_subscription_id")
        ),
    )
    op.create_index(
        op.f("ix_subscription_credits_user_id"),
        "subscription_credits",
        ["user_id"],
        unique=False,
    )
    op.create_table(
        "subscription_events",
        sa.Column("subscription_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=16), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("event_key", sa.String(length=128), nullable=False),
        sa.Column("reason", sa.String(length=300), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "event_type IN ('activate', 'pause', 'resume', 'skip', 'renew', 'expire', 'cancel')",
            name=op.f("ck_subscription_events_event_type"),
        ),
        sa.CheckConstraint(
            "length(event_key) > 0", name=op.f("ck_subscription_events_event_key")
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name=op.f("fk_subscription_events_actor_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id"],
            ["subscriptions.id"],
            name=op.f("fk_subscription_events_subscription_id_subscriptions"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscription_events")),
        sa.UniqueConstraint(
            "subscription_id",
            "event_key",
            name=op.f("uq_subscription_events_subscription_id_event_key"),
        ),
    )
    op.create_index(
        op.f("ix_subscription_events_actor_user_id"),
        "subscription_events",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscription_events_subscription_id"),
        "subscription_events",
        ["subscription_id"],
        unique=False,
    )
    op.create_index(
        "uq_subscription_skip_date",
        "subscription_events",
        ["subscription_id", "effective_date"],
        unique=True,
        postgresql_where=sa.text("event_type = 'skip'"),
    )
    op.create_table(
        "cart_items",
        sa.Column("cart_id", sa.Uuid(), nullable=False),
        sa.Column("menu_id", sa.Uuid(), nullable=False),
        sa.Column("menu_item_id", sa.Uuid(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity > 0", name=op.f("ck_cart_items_quantity_positive")
        ),
        sa.ForeignKeyConstraint(
            ["cart_id", "menu_id"],
            ["carts.id", "carts.menu_id"],
            name=op.f("fk_cart_items_cart_id_menu_id_carts"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["menu_item_id", "menu_id"],
            ["menu_items.id", "menu_items.menu_id"],
            name=op.f("fk_cart_items_menu_item_id_menu_id_menu_items"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cart_items")),
        sa.UniqueConstraint(
            "cart_id", "menu_item_id", name=op.f("uq_cart_items_cart_id_menu_item_id")
        ),
    )
    op.create_index(
        op.f("ix_cart_items_cart_id"), "cart_items", ["cart_id"], unique=False
    )
    op.create_index(
        op.f("ix_cart_items_menu_id"), "cart_items", ["menu_id"], unique=False
    )
    op.create_index(
        op.f("ix_cart_items_menu_item_id"), "cart_items", ["menu_item_id"], unique=False
    )
    op.create_table(
        "credit_transactions",
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=True),
        sa.Column("kind", sa.String(length=12), nullable=False),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("event_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.String(length=300), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(kind IN ('grant', 'restore') AND delta > 0) OR (kind IN ('debit', 'expire') AND delta < 0) OR kind = 'adjust'",
            name=op.f("ck_credit_transactions_delta_direction"),
        ),
        sa.CheckConstraint(
            "kind IN ('grant', 'debit', 'restore', 'expire', 'adjust')",
            name=op.f("ck_credit_transactions_kind"),
        ),
        sa.CheckConstraint(
            "kind NOT IN ('debit', 'restore') OR order_id IS NOT NULL",
            name=op.f("ck_credit_transactions_order_required"),
        ),
        sa.CheckConstraint(
            "delta <> 0", name=op.f("ck_credit_transactions_delta_nonzero")
        ),
        sa.CheckConstraint(
            "length(event_key) > 0 AND length(request_hash) = 64 AND length(reason) > 0",
            name=op.f("ck_credit_transactions_event_identity"),
        ),
        sa.ForeignKeyConstraint(
            ["account_id", "user_id"],
            ["subscription_credits.id", "subscription_credits.user_id"],
            name=op.f("fk_credit_transactions_account_id_user_id_subscription_credits"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name=op.f("fk_credit_transactions_actor_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["order_id", "user_id"],
            ["orders.id", "orders.user_id"],
            name=op.f("fk_credit_transactions_order_id_user_id_orders"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_credit_transactions")),
        sa.UniqueConstraint(
            "account_id",
            "event_key",
            name=op.f("uq_credit_transactions_account_id_event_key"),
        ),
        sa.UniqueConstraint(
            "account_id",
            "order_id",
            "kind",
            name=op.f("uq_credit_transactions_account_id_order_id_kind"),
        ),
    )
    op.create_index(
        op.f("ix_credit_transactions_account_id"),
        "credit_transactions",
        ["account_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_credit_transactions_actor_user_id"),
        "credit_transactions",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_credit_transactions_order_id"),
        "credit_transactions",
        ["order_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_credit_transactions_user_id"),
        "credit_transactions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "uq_credit_account_purchase_grant",
        "credit_transactions",
        ["account_id"],
        unique=True,
        postgresql_where=sa.text("kind = 'grant'"),
    )
    op.create_table(
        "kitchen_orders",
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ready_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'preparing', 'ready', 'completed', 'cancelled')",
            name=op.f("ck_kitchen_orders_status"),
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            name=op.f("fk_kitchen_orders_order_id_orders"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_kitchen_orders")),
        sa.UniqueConstraint("order_id", name=op.f("uq_kitchen_orders_order_id")),
    )
    op.create_index(
        op.f("ix_kitchen_orders_status"), "kitchen_orders", ["status"], unique=False
    )
    op.create_table(
        "order_items",
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("menu_id", sa.Uuid(), nullable=False),
        sa.Column("menu_item_id", sa.Uuid(), nullable=False),
        sa.Column("food_name", sa.String(length=120), nullable=False),
        sa.Column("unit_price_paise", sa.BigInteger(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column(
            "line_total_paise",
            sa.BigInteger(),
            sa.Computed("unit_price_paise * quantity", persisted=True),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity > 0 AND unit_price_paise >= 0",
            name=op.f("ck_order_items_item_amount"),
        ),
        sa.ForeignKeyConstraint(
            ["menu_item_id", "menu_id"],
            ["menu_items.id", "menu_items.menu_id"],
            name=op.f("fk_order_items_menu_item_id_menu_id_menu_items"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["order_id", "menu_id"],
            ["orders.id", "orders.menu_id"],
            name=op.f("fk_order_items_order_id_menu_id_orders"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_items")),
        sa.UniqueConstraint(
            "order_id",
            "menu_item_id",
            name=op.f("uq_order_items_order_id_menu_item_id"),
        ),
    )
    op.create_index(
        op.f("ix_order_items_menu_id"), "order_items", ["menu_id"], unique=False
    )
    op.create_index(
        op.f("ix_order_items_menu_item_id"),
        "order_items",
        ["menu_item_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_order_items_order_id"), "order_items", ["order_id"], unique=False
    )
    op.create_table(
        "payments",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=True),
        sa.Column("subscription_id", sa.Uuid(), nullable=True),
        sa.Column("amount_paise", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("provider_order_id", sa.String(length=100), nullable=True),
        sa.Column("provider_payment_id", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(status = 'captured') = (captured_at IS NOT NULL)",
            name=op.f("ck_payments_capture_instant"),
        ),
        sa.CheckConstraint(
            "amount_paise > 0 AND currency = 'INR'",
            name=op.f("ck_payments_amount_currency"),
        ),
        sa.CheckConstraint("provider = 'razorpay'", name=op.f("ck_payments_provider")),
        sa.CheckConstraint(
            "status IN ('created', 'authorized', 'captured', 'failed')",
            name=op.f("ck_payments_status"),
        ),
        sa.CheckConstraint(
            "(order_id IS NOT NULL AND subscription_id IS NULL) OR (order_id IS NULL AND subscription_id IS NOT NULL)",
            name=op.f("ck_payments_one_target"),
        ),
        sa.CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name=op.f("ck_payments_request_identity"),
        ),
        sa.ForeignKeyConstraint(
            ["order_id", "user_id"],
            ["orders.id", "orders.user_id"],
            name=op.f("fk_payments_order_id_user_id_orders"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id", "user_id"],
            ["subscriptions.id", "subscriptions.user_id"],
            name=op.f("fk_payments_subscription_id_user_id_subscriptions"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_payments_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_payments")),
        sa.UniqueConstraint(
            "provider",
            "provider_payment_id",
            name=op.f("uq_payments_provider_provider_payment_id"),
        ),
        sa.UniqueConstraint(
            "user_id",
            "idempotency_key",
            name=op.f("uq_payments_user_id_idempotency_key"),
        ),
    )
    op.create_index(
        op.f("ix_payments_order_id"), "payments", ["order_id"], unique=False
    )
    op.create_index(
        op.f("ix_payments_provider_order_id"),
        "payments",
        ["provider_order_id"],
        unique=False,
    )
    op.create_index(op.f("ix_payments_status"), "payments", ["status"], unique=False)
    op.create_index(
        op.f("ix_payments_subscription_id"),
        "payments",
        ["subscription_id"],
        unique=False,
    )
    op.create_index(op.f("ix_payments_user_id"), "payments", ["user_id"], unique=False)
    op.create_table(
        "payment_webhook_events",
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("provider_event_id", sa.String(length=150), nullable=False),
        sa.Column("payment_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "sanitized_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "jsonb_typeof(sanitized_payload) = 'object'",
            name=op.f("ck_payment_webhook_events_payload_object"),
        ),
        sa.CheckConstraint(
            "provider = 'razorpay'", name=op.f("ck_payment_webhook_events_provider")
        ),
        sa.CheckConstraint(
            "status IN ('received', 'processed', 'failed')",
            name=op.f("ck_payment_webhook_events_status"),
        ),
        sa.CheckConstraint(
            "length(provider_event_id) > 0 AND length(payload_hash) = 64",
            name=op.f("ck_payment_webhook_events_event_identity"),
        ),
        sa.ForeignKeyConstraint(
            ["payment_id"],
            ["payments.id"],
            name=op.f("fk_payment_webhook_events_payment_id_payments"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_payment_webhook_events")),
        sa.UniqueConstraint(
            "provider",
            "provider_event_id",
            name=op.f("uq_payment_webhook_events_provider_provider_event_id"),
        ),
    )
    op.create_index(
        op.f("ix_payment_webhook_events_payment_id"),
        "payment_webhook_events",
        ["payment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_payment_webhook_events_status"),
        "payment_webhook_events",
        ["status"],
        unique=False,
    )
    op.create_table(
        "refunds",
        sa.Column("payment_id", sa.Uuid(), nullable=False),
        sa.Column("amount_paise", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("reason", sa.String(length=300), nullable=False),
        sa.Column("provider_refund_id", sa.String(length=100), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('requested', 'processing', 'succeeded', 'failed')",
            name=op.f("ck_refunds_status"),
        ),
        sa.CheckConstraint("amount_paise > 0", name=op.f("ck_refunds_amount_positive")),
        sa.CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name=op.f("ck_refunds_request_identity"),
        ),
        sa.ForeignKeyConstraint(
            ["payment_id"],
            ["payments.id"],
            name=op.f("fk_refunds_payment_id_payments"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refunds")),
        sa.UniqueConstraint(
            "payment_id",
            "idempotency_key",
            name=op.f("uq_refunds_payment_id_idempotency_key"),
        ),
        sa.UniqueConstraint(
            "provider_refund_id", name=op.f("uq_refunds_provider_refund_id")
        ),
    )
    op.create_index(
        op.f("ix_refunds_payment_id"), "refunds", ["payment_id"], unique=False
    )
    # Explicit runtime grants: history/snapshots cannot be updated or deleted.
    op.execute("GRANT SELECT, INSERT ON TABLE public.users TO dailydabba_app")
    op.execute(
        "GRANT SELECT, INSERT ON TABLE public.customer_profiles TO dailydabba_app"
    )
    op.execute("GRANT SELECT, INSERT ON TABLE public.addresses TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.food_categories TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.food_items TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.daily_menus TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.menu_items TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.delivery_slots TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.carts TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.cart_items TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.orders TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.order_items TO dailydabba_app")
    op.execute(
        "GRANT SELECT, INSERT ON TABLE public.subscription_plans TO dailydabba_app"
    )
    op.execute("GRANT SELECT, INSERT ON TABLE public.subscriptions TO dailydabba_app")
    op.execute(
        "GRANT SELECT, INSERT ON TABLE public.subscription_events TO dailydabba_app"
    )
    op.execute(
        "GRANT SELECT, INSERT ON TABLE public.subscription_credits TO dailydabba_app"
    )
    op.execute(
        "GRANT SELECT, INSERT ON TABLE public.credit_transactions TO dailydabba_app"
    )
    op.execute("GRANT SELECT, INSERT ON TABLE public.payments TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.refunds TO dailydabba_app")
    op.execute(
        "GRANT SELECT, INSERT ON TABLE public.payment_webhook_events TO dailydabba_app"
    )
    op.execute("GRANT SELECT, INSERT ON TABLE public.kitchen_orders TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.notifications TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.audit_logs TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.users TO dailydabba_app")
    op.execute(
        "GRANT UPDATE, DELETE ON TABLE public.customer_profiles TO dailydabba_app"
    )
    op.execute("GRANT UPDATE, DELETE ON TABLE public.addresses TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.food_categories TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.food_items TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.daily_menus TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.menu_items TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.delivery_slots TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.carts TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.cart_items TO dailydabba_app")
    op.execute(
        "GRANT UPDATE, DELETE ON TABLE public.subscription_plans TO dailydabba_app"
    )
    op.execute("GRANT UPDATE, DELETE ON TABLE public.notifications TO dailydabba_app")
    op.execute("GRANT UPDATE (status) ON TABLE public.orders TO dailydabba_app")
    op.execute(
        "GRANT UPDATE (status, expires_on) ON TABLE public.subscriptions TO dailydabba_app"
    )
    op.execute(
        "GRANT UPDATE (balance) ON TABLE public.subscription_credits TO dailydabba_app"
    )
    op.execute(
        "GRANT UPDATE (status, captured_at, provider_order_id, provider_payment_id) ON TABLE public.payments TO dailydabba_app"
    )
    op.execute(
        "GRANT UPDATE (status, provider_refund_id) ON TABLE public.refunds TO dailydabba_app"
    )
    op.execute(
        "GRANT UPDATE (status, payment_id, processed_at) ON TABLE public.payment_webhook_events TO dailydabba_app"
    )
    op.execute(
        "GRANT UPDATE (status, started_at, ready_at) ON TABLE public.kitchen_orders TO dailydabba_app"
    )
    op.execute("REVOKE ALL ON TABLE public.alembic_version FROM dailydabba_app")
    op.execute("GRANT SELECT ON TABLE public.alembic_version TO dailydabba_app")
    # ### end Alembic commands ###


def downgrade() -> None:
    # Reviewed initial schema and explicit runtime grants.
    op.drop_index(op.f("ix_refunds_payment_id"), table_name="refunds")
    op.drop_table("refunds")
    op.drop_index(
        op.f("ix_payment_webhook_events_status"), table_name="payment_webhook_events"
    )
    op.drop_index(
        op.f("ix_payment_webhook_events_payment_id"),
        table_name="payment_webhook_events",
    )
    op.drop_table("payment_webhook_events")
    op.drop_index(op.f("ix_payments_user_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_subscription_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_status"), table_name="payments")
    op.drop_index(op.f("ix_payments_provider_order_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_order_id"), table_name="payments")
    op.drop_table("payments")
    op.drop_index(op.f("ix_order_items_order_id"), table_name="order_items")
    op.drop_index(op.f("ix_order_items_menu_item_id"), table_name="order_items")
    op.drop_index(op.f("ix_order_items_menu_id"), table_name="order_items")
    op.drop_table("order_items")
    op.drop_index(op.f("ix_kitchen_orders_status"), table_name="kitchen_orders")
    op.drop_table("kitchen_orders")
    op.drop_index(
        "uq_credit_account_purchase_grant",
        table_name="credit_transactions",
        postgresql_where=sa.text("kind = 'grant'"),
    )
    op.drop_index(
        op.f("ix_credit_transactions_user_id"), table_name="credit_transactions"
    )
    op.drop_index(
        op.f("ix_credit_transactions_order_id"), table_name="credit_transactions"
    )
    op.drop_index(
        op.f("ix_credit_transactions_actor_user_id"), table_name="credit_transactions"
    )
    op.drop_index(
        op.f("ix_credit_transactions_account_id"), table_name="credit_transactions"
    )
    op.drop_table("credit_transactions")
    op.drop_index(op.f("ix_cart_items_menu_item_id"), table_name="cart_items")
    op.drop_index(op.f("ix_cart_items_menu_id"), table_name="cart_items")
    op.drop_index(op.f("ix_cart_items_cart_id"), table_name="cart_items")
    op.drop_table("cart_items")
    op.drop_index(
        "uq_subscription_skip_date",
        table_name="subscription_events",
        postgresql_where=sa.text("event_type = 'skip'"),
    )
    op.drop_index(
        op.f("ix_subscription_events_subscription_id"), table_name="subscription_events"
    )
    op.drop_index(
        op.f("ix_subscription_events_actor_user_id"), table_name="subscription_events"
    )
    op.drop_table("subscription_events")
    op.drop_index(
        op.f("ix_subscription_credits_user_id"), table_name="subscription_credits"
    )
    op.drop_table("subscription_credits")
    op.drop_index(op.f("ix_orders_user_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_status"), table_name="orders")
    op.drop_index(op.f("ix_orders_menu_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_delivery_slot_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_business_date"), table_name="orders")
    op.drop_index(op.f("ix_orders_address_id"), table_name="orders")
    op.drop_table("orders")
    op.drop_index(op.f("ix_menu_items_menu_id"), table_name="menu_items")
    op.drop_index(op.f("ix_menu_items_food_item_id"), table_name="menu_items")
    op.drop_table("menu_items")
    op.drop_index(op.f("ix_subscriptions_user_id"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_status"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_renewed_from_id"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_plan_id"), table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_status"), table_name="notifications")
    op.drop_table("notifications")
    op.drop_index(op.f("ix_food_items_category_id"), table_name="food_items")
    op.drop_table("food_items")
    op.drop_table("customer_profiles")
    op.drop_index(op.f("ix_carts_menu_id"), table_name="carts")
    op.drop_table("carts")
    op.drop_index(op.f("ix_audit_logs_target_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_actor_user_id"), table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index(
        "uq_addresses_one_live_default",
        table_name="addresses",
        postgresql_where=sa.text("is_default AND deleted_at IS NULL"),
    )
    op.drop_index(op.f("ix_addresses_user_id"), table_name="addresses")
    op.drop_table("addresses")
    op.drop_table("users")
    op.drop_table("subscription_plans")
    op.drop_table("food_categories")
    op.drop_table("delivery_slots")
    op.drop_table("daily_menus")
    # ### end Alembic commands ###
