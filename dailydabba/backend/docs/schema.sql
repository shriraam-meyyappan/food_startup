-- Phase 3 design only. Not an Alembic migration.

-- Generated from SQLAlchemy models. No database connection was used.

-- ORM insert defaults (including UUIDs) are not SQL server defaults.

CREATE TABLE food_categories (
	name VARCHAR(80) NOT NULL,
	is_active BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_food_categories PRIMARY KEY (id),
	CONSTRAINT uq_food_categories_name UNIQUE (name)
);

CREATE TABLE daily_menus (
	business_date DATE NOT NULL,
	meal_type VARCHAR(12) NOT NULL,
	is_active BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_daily_menus PRIMARY KEY (id),
	CONSTRAINT uq_daily_menus_business_date_meal_type UNIQUE (business_date, meal_type),
	CONSTRAINT uq_daily_menus_id_business_date_meal_type UNIQUE (id, business_date, meal_type),
	CONSTRAINT ck_daily_menus_meal_type CHECK (meal_type IN ('breakfast', 'lunch', 'dinner'))
);

CREATE TABLE delivery_slots (
	name VARCHAR(80) NOT NULL,
	meal_type VARCHAR(12) NOT NULL,
	start_local TIME WITHOUT TIME ZONE NOT NULL,
	end_local TIME WITHOUT TIME ZONE NOT NULL,
	is_active BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_delivery_slots PRIMARY KEY (id),
	CONSTRAINT uq_delivery_slots_meal_type_start_local_end_local UNIQUE (meal_type, start_local, end_local),
	CONSTRAINT uq_delivery_slots_id_meal_type UNIQUE (id, meal_type),
	CONSTRAINT ck_delivery_slots_meal_type CHECK (meal_type IN ('breakfast', 'lunch', 'dinner')),
	CONSTRAINT ck_delivery_slots_time_window CHECK (end_local > start_local)
);

CREATE TABLE users (
	email VARCHAR(254) NOT NULL,
	password_hash VARCHAR(512) NOT NULL,
	role VARCHAR(20) NOT NULL,
	is_active BOOLEAN NOT NULL,
	deactivated_at TIMESTAMP WITH TIME ZONE,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_users PRIMARY KEY (id),
	CONSTRAINT ck_users_email_normalized CHECK (email = lower(email) AND length(email) > 3),
	CONSTRAINT ck_users_role CHECK (role IN ('customer', 'admin', 'kitchen_staff')),
	CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE TABLE subscription_plans (
	code VARCHAR(50) NOT NULL,
	name VARCHAR(120) NOT NULL,
	period VARCHAR(12) NOT NULL,
	meal_type VARCHAR(12) NOT NULL,
	duration_days INTEGER NOT NULL,
	included_credits INTEGER NOT NULL,
	price_paise BIGINT NOT NULL,
	is_active BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_subscription_plans PRIMARY KEY (id),
	CONSTRAINT ck_subscription_plans_period CHECK (period IN ('weekly', 'monthly')),
	CONSTRAINT ck_subscription_plans_meal_type CHECK (meal_type IN ('breakfast', 'lunch', 'dinner')),
	CONSTRAINT ck_subscription_plans_terms_positive CHECK (duration_days > 0 AND included_credits > 0 AND price_paise >= 0),
	CONSTRAINT uq_subscription_plans_code UNIQUE (code)
);

CREATE TABLE food_items (
	category_id UUID NOT NULL,
	name VARCHAR(120) NOT NULL,
	description TEXT NOT NULL,
	price_paise BIGINT NOT NULL,
	is_active BOOLEAN NOT NULL,
	is_available BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_food_items PRIMARY KEY (id),
	CONSTRAINT ck_food_items_price_nonnegative CHECK (price_paise >= 0),
	CONSTRAINT fk_food_items_category_id_food_categories FOREIGN KEY(category_id) REFERENCES food_categories (id) ON DELETE RESTRICT
);

CREATE INDEX ix_food_items_category_id ON food_items (category_id);

CREATE TABLE carts (
	user_id UUID NOT NULL,
	menu_id UUID NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_carts PRIMARY KEY (id),
	CONSTRAINT uq_carts_id_menu_id UNIQUE (id, menu_id),
	CONSTRAINT uq_carts_user_id UNIQUE (user_id),
	CONSTRAINT fk_carts_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT fk_carts_menu_id_daily_menus FOREIGN KEY(menu_id) REFERENCES daily_menus (id) ON DELETE RESTRICT
);

CREATE INDEX ix_carts_menu_id ON carts (menu_id);

CREATE TABLE customer_profiles (
	user_id UUID NOT NULL,
	full_name VARCHAR(120) NOT NULL,
	phone VARCHAR(20),
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_customer_profiles PRIMARY KEY (id),
	CONSTRAINT uq_customer_profiles_user_id UNIQUE (user_id),
	CONSTRAINT fk_customer_profiles_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT
);

CREATE TABLE addresses (
	user_id UUID NOT NULL,
	label VARCHAR(50) NOT NULL,
	recipient_name VARCHAR(120) NOT NULL,
	phone VARCHAR(20) NOT NULL,
	line1 VARCHAR(200) NOT NULL,
	line2 VARCHAR(200),
	locality VARCHAR(120) NOT NULL,
	city VARCHAR(80) NOT NULL,
	state VARCHAR(80) NOT NULL,
	postal_code VARCHAR(6) NOT NULL,
	is_default BOOLEAN NOT NULL,
	deleted_at TIMESTAMP WITH TIME ZONE,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_addresses PRIMARY KEY (id),
	CONSTRAINT uq_addresses_id_user_id UNIQUE (id, user_id),
	CONSTRAINT ck_addresses_postal_code_length CHECK (length(postal_code) = 6),
	CONSTRAINT ck_addresses_default_not_deleted CHECK (NOT is_default OR deleted_at IS NULL),
	CONSTRAINT fk_addresses_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT
);

CREATE INDEX ix_addresses_user_id ON addresses (user_id);

CREATE UNIQUE INDEX uq_addresses_one_live_default ON addresses (user_id) WHERE is_default AND deleted_at IS NULL;

CREATE TABLE notifications (
	user_id UUID NOT NULL,
	event_key VARCHAR(150) NOT NULL,
	channel VARCHAR(12) NOT NULL,
	status VARCHAR(12) NOT NULL,
	payload JSONB NOT NULL,
	sent_at TIMESTAMP WITH TIME ZONE,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_notifications PRIMARY KEY (id),
	CONSTRAINT ck_notifications_channel CHECK (channel IN ('in_app', 'email', 'sms')),
	CONSTRAINT ck_notifications_status CHECK (status IN ('pending', 'sent', 'failed', 'read')),
	CONSTRAINT ck_notifications_payload_object CHECK (jsonb_typeof(payload) = 'object'),
	CONSTRAINT fk_notifications_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT uq_notifications_event_key UNIQUE (event_key)
);

CREATE INDEX ix_notifications_status ON notifications (status);

CREATE INDEX ix_notifications_user_id ON notifications (user_id);

CREATE TABLE audit_logs (
	actor_user_id UUID,
	action VARCHAR(100) NOT NULL,
	target_type VARCHAR(80) NOT NULL,
	target_id UUID NOT NULL,
	details JSONB NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_audit_logs PRIMARY KEY (id),
	CONSTRAINT ck_audit_logs_details_object CHECK (jsonb_typeof(details) = 'object'),
	CONSTRAINT fk_audit_logs_actor_user_id_users FOREIGN KEY(actor_user_id) REFERENCES users (id) ON DELETE RESTRICT
);

CREATE INDEX ix_audit_logs_target_id ON audit_logs (target_id);

CREATE INDEX ix_audit_logs_actor_user_id ON audit_logs (actor_user_id);

CREATE TABLE subscriptions (
	user_id UUID NOT NULL,
	plan_id UUID NOT NULL,
	renewed_from_id UUID,
	plan_name VARCHAR(120) NOT NULL,
	meal_type VARCHAR(12) NOT NULL,
	purchased_credits INTEGER NOT NULL,
	price_paise BIGINT NOT NULL,
	starts_on DATE NOT NULL,
	expires_on DATE NOT NULL,
	status VARCHAR(20) NOT NULL,
	policy_snapshot JSONB NOT NULL,
	idempotency_key VARCHAR(128) NOT NULL,
	request_hash VARCHAR(64) NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_subscriptions PRIMARY KEY (id),
	CONSTRAINT uq_subscriptions_id_user_id UNIQUE (id, user_id),
	CONSTRAINT fk_subscriptions_renewed_from_id_user_id_subscriptions FOREIGN KEY(renewed_from_id, user_id) REFERENCES subscriptions (id, user_id) ON DELETE RESTRICT,
	CONSTRAINT uq_subscriptions_user_id_idempotency_key UNIQUE (user_id, idempotency_key),
	CONSTRAINT ck_subscriptions_date_window CHECK (expires_on > starts_on),
	CONSTRAINT ck_subscriptions_purchased_terms CHECK (purchased_credits > 0 AND price_paise >= 0),
	CONSTRAINT ck_subscriptions_meal_type CHECK (meal_type IN ('breakfast', 'lunch', 'dinner')),
	CONSTRAINT ck_subscriptions_status CHECK (status IN ('pending_payment', 'active', 'paused', 'expired', 'cancelled')),
	CONSTRAINT ck_subscriptions_policy_object CHECK (jsonb_typeof(policy_snapshot) = 'object'),
	CONSTRAINT ck_subscriptions_request_identity CHECK (length(idempotency_key) > 0 AND length(request_hash) = 64),
	CONSTRAINT fk_subscriptions_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT fk_subscriptions_plan_id_subscription_plans FOREIGN KEY(plan_id) REFERENCES subscription_plans (id) ON DELETE RESTRICT
);

CREATE INDEX ix_subscriptions_status ON subscriptions (status);

CREATE INDEX ix_subscriptions_plan_id ON subscriptions (plan_id);

CREATE INDEX ix_subscriptions_renewed_from_id ON subscriptions (renewed_from_id);

CREATE INDEX ix_subscriptions_user_id ON subscriptions (user_id);

CREATE TABLE menu_items (
	menu_id UUID NOT NULL,
	food_item_id UUID NOT NULL,
	price_paise BIGINT NOT NULL,
	portions_remaining INTEGER NOT NULL,
	is_available BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_menu_items PRIMARY KEY (id),
	CONSTRAINT uq_menu_items_menu_id_food_item_id UNIQUE (menu_id, food_item_id),
	CONSTRAINT uq_menu_items_id_menu_id UNIQUE (id, menu_id),
	CONSTRAINT ck_menu_items_price_nonnegative CHECK (price_paise >= 0),
	CONSTRAINT ck_menu_items_stock_nonnegative CHECK (portions_remaining >= 0),
	CONSTRAINT fk_menu_items_menu_id_daily_menus FOREIGN KEY(menu_id) REFERENCES daily_menus (id) ON DELETE RESTRICT,
	CONSTRAINT fk_menu_items_food_item_id_food_items FOREIGN KEY(food_item_id) REFERENCES food_items (id) ON DELETE RESTRICT
);

CREATE INDEX ix_menu_items_menu_id ON menu_items (menu_id);

CREATE INDEX ix_menu_items_food_item_id ON menu_items (food_item_id);

CREATE TABLE orders (
	user_id UUID NOT NULL,
	address_id UUID NOT NULL,
	address_snapshot JSONB NOT NULL,
	menu_id UUID NOT NULL,
	business_date DATE NOT NULL,
	meal_type VARCHAR(12) NOT NULL,
	delivery_slot_id UUID NOT NULL,
	delivery_start_at TIMESTAMP WITH TIME ZONE NOT NULL,
	delivery_end_at TIMESTAMP WITH TIME ZONE NOT NULL,
	subtotal_paise BIGINT NOT NULL,
	delivery_fee_paise BIGINT NOT NULL,
	tax_paise BIGINT NOT NULL,
	discount_paise BIGINT NOT NULL,
	total_paise BIGINT NOT NULL,
	status VARCHAR(24) NOT NULL,
	idempotency_key VARCHAR(128) NOT NULL,
	request_hash VARCHAR(64) NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_orders PRIMARY KEY (id),
	CONSTRAINT uq_orders_id_user_id UNIQUE (id, user_id),
	CONSTRAINT uq_orders_id_menu_id UNIQUE (id, menu_id),
	CONSTRAINT uq_orders_user_id_idempotency_key UNIQUE (user_id, idempotency_key),
	CONSTRAINT fk_orders_address_id_user_id_addresses FOREIGN KEY(address_id, user_id) REFERENCES addresses (id, user_id) ON DELETE RESTRICT,
	CONSTRAINT fk_orders_menu_id_business_date_meal_type_daily_menus FOREIGN KEY(menu_id, business_date, meal_type) REFERENCES daily_menus (id, business_date, meal_type) ON DELETE RESTRICT,
	CONSTRAINT fk_orders_delivery_slot_id_meal_type_delivery_slots FOREIGN KEY(delivery_slot_id, meal_type) REFERENCES delivery_slots (id, meal_type) ON DELETE RESTRICT,
	CONSTRAINT ck_orders_amounts_nonnegative CHECK (subtotal_paise >= 0 AND delivery_fee_paise >= 0 AND tax_paise >= 0 AND discount_paise >= 0 AND total_paise >= 0),
	CONSTRAINT ck_orders_total_equation CHECK (total_paise = subtotal_paise + delivery_fee_paise + tax_paise - discount_paise),
	CONSTRAINT ck_orders_delivery_window CHECK (delivery_end_at > delivery_start_at),
	CONSTRAINT ck_orders_business_date_local CHECK (business_date = (delivery_start_at AT TIME ZONE 'Asia/Kolkata')::date AND business_date = (delivery_end_at AT TIME ZONE 'Asia/Kolkata')::date),
	CONSTRAINT ck_orders_address_object CHECK (jsonb_typeof(address_snapshot) = 'object'),
	CONSTRAINT ck_orders_request_identity CHECK (length(idempotency_key) > 0 AND length(request_hash) = 64),
	CONSTRAINT ck_orders_status CHECK (status IN ('pending_payment', 'placed', 'confirmed', 'preparing', 'ready', 'out_for_delivery', 'delivered', 'cancelled')),
	CONSTRAINT fk_orders_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT
);

CREATE INDEX ix_orders_address_id ON orders (address_id);

CREATE INDEX ix_orders_status ON orders (status);

CREATE INDEX ix_orders_user_id ON orders (user_id);

CREATE INDEX ix_orders_business_date ON orders (business_date);

CREATE INDEX ix_orders_menu_id ON orders (menu_id);

CREATE INDEX ix_orders_delivery_slot_id ON orders (delivery_slot_id);

CREATE TABLE subscription_events (
	subscription_id UUID NOT NULL,
	event_type VARCHAR(16) NOT NULL,
	effective_date DATE NOT NULL,
	event_key VARCHAR(128) NOT NULL,
	reason VARCHAR(300) NOT NULL,
	actor_user_id UUID,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_subscription_events PRIMARY KEY (id),
	CONSTRAINT uq_subscription_events_subscription_id_event_key UNIQUE (subscription_id, event_key),
	CONSTRAINT ck_subscription_events_event_type CHECK (event_type IN ('activate', 'pause', 'resume', 'skip', 'renew', 'expire', 'cancel')),
	CONSTRAINT ck_subscription_events_event_key CHECK (length(event_key) > 0),
	CONSTRAINT fk_subscription_events_subscription_id_subscriptions FOREIGN KEY(subscription_id) REFERENCES subscriptions (id) ON DELETE RESTRICT,
	CONSTRAINT fk_subscription_events_actor_user_id_users FOREIGN KEY(actor_user_id) REFERENCES users (id) ON DELETE RESTRICT
);

CREATE INDEX ix_subscription_events_subscription_id ON subscription_events (subscription_id);

CREATE INDEX ix_subscription_events_actor_user_id ON subscription_events (actor_user_id);

CREATE UNIQUE INDEX uq_subscription_skip_date ON subscription_events (subscription_id, effective_date) WHERE event_type = 'skip';

CREATE TABLE subscription_credits (
	subscription_id UUID NOT NULL,
	user_id UUID NOT NULL,
	balance INTEGER NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_subscription_credits PRIMARY KEY (id),
	CONSTRAINT fk_subscription_credits_subscription_id_user_id_subscriptions FOREIGN KEY(subscription_id, user_id) REFERENCES subscriptions (id, user_id) ON DELETE RESTRICT,
	CONSTRAINT uq_subscription_credits_id_user_id UNIQUE (id, user_id),
	CONSTRAINT ck_subscription_credits_balance_nonnegative CHECK (balance >= 0),
	CONSTRAINT uq_subscription_credits_subscription_id UNIQUE (subscription_id)
);

CREATE INDEX ix_subscription_credits_user_id ON subscription_credits (user_id);

CREATE TABLE cart_items (
	cart_id UUID NOT NULL,
	menu_id UUID NOT NULL,
	menu_item_id UUID NOT NULL,
	quantity INTEGER NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_cart_items PRIMARY KEY (id),
	CONSTRAINT fk_cart_items_cart_id_menu_id_carts FOREIGN KEY(cart_id, menu_id) REFERENCES carts (id, menu_id) ON DELETE CASCADE,
	CONSTRAINT fk_cart_items_menu_item_id_menu_id_menu_items FOREIGN KEY(menu_item_id, menu_id) REFERENCES menu_items (id, menu_id) ON DELETE RESTRICT,
	CONSTRAINT uq_cart_items_cart_id_menu_item_id UNIQUE (cart_id, menu_item_id),
	CONSTRAINT ck_cart_items_quantity_positive CHECK (quantity > 0)
);

CREATE INDEX ix_cart_items_menu_id ON cart_items (menu_id);

CREATE INDEX ix_cart_items_menu_item_id ON cart_items (menu_item_id);

CREATE INDEX ix_cart_items_cart_id ON cart_items (cart_id);

CREATE TABLE order_items (
	order_id UUID NOT NULL,
	menu_id UUID NOT NULL,
	menu_item_id UUID NOT NULL,
	food_name VARCHAR(120) NOT NULL,
	unit_price_paise BIGINT NOT NULL,
	quantity INTEGER NOT NULL,
	line_total_paise BIGINT GENERATED ALWAYS AS (unit_price_paise * quantity) STORED NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_order_items PRIMARY KEY (id),
	CONSTRAINT fk_order_items_order_id_menu_id_orders FOREIGN KEY(order_id, menu_id) REFERENCES orders (id, menu_id) ON DELETE RESTRICT,
	CONSTRAINT fk_order_items_menu_item_id_menu_id_menu_items FOREIGN KEY(menu_item_id, menu_id) REFERENCES menu_items (id, menu_id) ON DELETE RESTRICT,
	CONSTRAINT uq_order_items_order_id_menu_item_id UNIQUE (order_id, menu_item_id),
	CONSTRAINT ck_order_items_item_amount CHECK (quantity > 0 AND unit_price_paise >= 0)
);

CREATE INDEX ix_order_items_menu_item_id ON order_items (menu_item_id);

CREATE INDEX ix_order_items_order_id ON order_items (order_id);

CREATE INDEX ix_order_items_menu_id ON order_items (menu_id);

CREATE TABLE kitchen_orders (
	order_id UUID NOT NULL,
	status VARCHAR(16) NOT NULL,
	started_at TIMESTAMP WITH TIME ZONE,
	ready_at TIMESTAMP WITH TIME ZONE,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_kitchen_orders PRIMARY KEY (id),
	CONSTRAINT ck_kitchen_orders_status CHECK (status IN ('queued', 'preparing', 'ready', 'completed', 'cancelled')),
	CONSTRAINT uq_kitchen_orders_order_id UNIQUE (order_id),
	CONSTRAINT fk_kitchen_orders_order_id_orders FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE RESTRICT
);

CREATE INDEX ix_kitchen_orders_status ON kitchen_orders (status);

CREATE TABLE payments (
	user_id UUID NOT NULL,
	order_id UUID,
	subscription_id UUID,
	amount_paise BIGINT NOT NULL,
	currency VARCHAR(3) NOT NULL,
	provider VARCHAR(20) NOT NULL,
	provider_order_id VARCHAR(100),
	provider_payment_id VARCHAR(100),
	status VARCHAR(16) NOT NULL,
	captured_at TIMESTAMP WITH TIME ZONE,
	idempotency_key VARCHAR(128) NOT NULL,
	request_hash VARCHAR(64) NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_payments PRIMARY KEY (id),
	CONSTRAINT fk_payments_order_id_user_id_orders FOREIGN KEY(order_id, user_id) REFERENCES orders (id, user_id) ON DELETE RESTRICT,
	CONSTRAINT fk_payments_subscription_id_user_id_subscriptions FOREIGN KEY(subscription_id, user_id) REFERENCES subscriptions (id, user_id) ON DELETE RESTRICT,
	CONSTRAINT uq_payments_user_id_idempotency_key UNIQUE (user_id, idempotency_key),
	CONSTRAINT uq_payments_provider_provider_payment_id UNIQUE (provider, provider_payment_id),
	CONSTRAINT ck_payments_one_target CHECK ((order_id IS NOT NULL AND subscription_id IS NULL) OR (order_id IS NULL AND subscription_id IS NOT NULL)),
	CONSTRAINT ck_payments_amount_currency CHECK (amount_paise > 0 AND currency = 'INR'),
	CONSTRAINT ck_payments_provider CHECK (provider = 'razorpay'),
	CONSTRAINT ck_payments_status CHECK (status IN ('created', 'authorized', 'captured', 'failed')),
	CONSTRAINT ck_payments_capture_instant CHECK ((status = 'captured') = (captured_at IS NOT NULL)),
	CONSTRAINT ck_payments_request_identity CHECK (length(idempotency_key) > 0 AND length(request_hash) = 64),
	CONSTRAINT fk_payments_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT
);

CREATE INDEX ix_payments_user_id ON payments (user_id);

CREATE INDEX ix_payments_provider_order_id ON payments (provider_order_id);

CREATE INDEX ix_payments_order_id ON payments (order_id);

CREATE INDEX ix_payments_status ON payments (status);

CREATE INDEX ix_payments_subscription_id ON payments (subscription_id);

CREATE TABLE credit_transactions (
	account_id UUID NOT NULL,
	user_id UUID NOT NULL,
	order_id UUID,
	kind VARCHAR(12) NOT NULL,
	delta INTEGER NOT NULL,
	event_key VARCHAR(128) NOT NULL,
	request_hash VARCHAR(64) NOT NULL,
	reason VARCHAR(300) NOT NULL,
	actor_user_id UUID,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_credit_transactions PRIMARY KEY (id),
	CONSTRAINT fk_credit_transactions_account_id_user_id_subscription_credits FOREIGN KEY(account_id, user_id) REFERENCES subscription_credits (id, user_id) ON DELETE RESTRICT,
	CONSTRAINT fk_credit_transactions_order_id_user_id_orders FOREIGN KEY(order_id, user_id) REFERENCES orders (id, user_id) ON DELETE RESTRICT,
	CONSTRAINT uq_credit_transactions_account_id_event_key UNIQUE (account_id, event_key),
	CONSTRAINT uq_credit_transactions_account_id_order_id_kind UNIQUE (account_id, order_id, kind),
	CONSTRAINT ck_credit_transactions_delta_nonzero CHECK (delta <> 0),
	CONSTRAINT ck_credit_transactions_kind CHECK (kind IN ('grant', 'debit', 'restore', 'expire', 'adjust')),
	CONSTRAINT ck_credit_transactions_delta_direction CHECK ((kind IN ('grant', 'restore') AND delta > 0) OR (kind IN ('debit', 'expire') AND delta < 0) OR kind = 'adjust'),
	CONSTRAINT ck_credit_transactions_order_required CHECK (kind NOT IN ('debit', 'restore') OR order_id IS NOT NULL),
	CONSTRAINT ck_credit_transactions_event_identity CHECK (length(event_key) > 0 AND length(request_hash) = 64 AND length(reason) > 0),
	CONSTRAINT fk_credit_transactions_actor_user_id_users FOREIGN KEY(actor_user_id) REFERENCES users (id) ON DELETE RESTRICT
);

CREATE INDEX ix_credit_transactions_account_id ON credit_transactions (account_id);

CREATE INDEX ix_credit_transactions_order_id ON credit_transactions (order_id);

CREATE INDEX ix_credit_transactions_user_id ON credit_transactions (user_id);

CREATE INDEX ix_credit_transactions_actor_user_id ON credit_transactions (actor_user_id);

CREATE UNIQUE INDEX uq_credit_account_purchase_grant ON credit_transactions (account_id) WHERE kind = 'grant';

CREATE TABLE refunds (
	payment_id UUID NOT NULL,
	amount_paise BIGINT NOT NULL,
	status VARCHAR(16) NOT NULL,
	reason VARCHAR(300) NOT NULL,
	provider_refund_id VARCHAR(100),
	idempotency_key VARCHAR(128) NOT NULL,
	request_hash VARCHAR(64) NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_refunds PRIMARY KEY (id),
	CONSTRAINT uq_refunds_payment_id_idempotency_key UNIQUE (payment_id, idempotency_key),
	CONSTRAINT uq_refunds_provider_refund_id UNIQUE (provider_refund_id),
	CONSTRAINT ck_refunds_amount_positive CHECK (amount_paise > 0),
	CONSTRAINT ck_refunds_status CHECK (status IN ('requested', 'processing', 'succeeded', 'failed')),
	CONSTRAINT ck_refunds_request_identity CHECK (length(idempotency_key) > 0 AND length(request_hash) = 64),
	CONSTRAINT fk_refunds_payment_id_payments FOREIGN KEY(payment_id) REFERENCES payments (id) ON DELETE RESTRICT
);

CREATE INDEX ix_refunds_payment_id ON refunds (payment_id);

CREATE TABLE payment_webhook_events (
	provider VARCHAR(20) NOT NULL,
	provider_event_id VARCHAR(150) NOT NULL,
	payment_id UUID,
	event_type VARCHAR(100) NOT NULL,
	payload_hash VARCHAR(64) NOT NULL,
	sanitized_payload JSONB NOT NULL,
	status VARCHAR(16) NOT NULL,
	processed_at TIMESTAMP WITH TIME ZONE,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_payment_webhook_events PRIMARY KEY (id),
	CONSTRAINT uq_payment_webhook_events_provider_provider_event_id UNIQUE (provider, provider_event_id),
	CONSTRAINT ck_payment_webhook_events_provider CHECK (provider = 'razorpay'),
	CONSTRAINT ck_payment_webhook_events_status CHECK (status IN ('received', 'processed', 'failed')),
	CONSTRAINT ck_payment_webhook_events_event_identity CHECK (length(provider_event_id) > 0 AND length(payload_hash) = 64),
	CONSTRAINT ck_payment_webhook_events_payload_object CHECK (jsonb_typeof(sanitized_payload) = 'object'),
	CONSTRAINT fk_payment_webhook_events_payment_id_payments FOREIGN KEY(payment_id) REFERENCES payments (id) ON DELETE RESTRICT
);

CREATE INDEX ix_payment_webhook_events_status ON payment_webhook_events (status);

CREATE INDEX ix_payment_webhook_events_payment_id ON payment_webhook_events (payment_id);
