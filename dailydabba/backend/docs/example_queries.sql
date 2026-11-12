-- Phase 3 read-only examples; Phase 4 has now migrated the development database.
-- :parameters are SQLAlchemy text() bind names, not literal psql substitutions.
-- Use only after migrations and suitable test-data setup, with server-validated IDs.

-- 1. Public menu: all publication/availability flags and stock must permit sale.
SELECT m.business_date, m.meal_type, mi.id AS menu_item_id,
       f.name, f.description, mi.price_paise, mi.portions_remaining
FROM daily_menus AS m
JOIN menu_items AS mi ON mi.menu_id = m.id
JOIN food_items AS f ON f.id = mi.food_item_id
JOIN food_categories AS c ON c.id = f.category_id
WHERE m.business_date = :business_date AND m.meal_type = :meal_type
  AND m.is_active AND mi.is_available AND mi.portions_remaining > 0
  AND f.is_active AND f.is_available AND c.is_active
ORDER BY f.name;

-- 2. Customer order history uses stored totals, not today's catalog prices.
SELECT id, business_date, meal_type, status, total_paise,
       delivery_start_at, delivery_end_at
FROM orders
WHERE user_id = :customer_id
ORDER BY created_at DESC
LIMIT :page_size;

-- 3. Check snapshot subtotal, as a diagnostic (not an authorization bypass).
SELECT o.id, o.subtotal_paise, COALESCE(SUM(i.line_total_paise), 0) AS computed_subtotal
FROM orders AS o
LEFT JOIN order_items AS i ON i.order_id = o.id
WHERE o.id = :order_id AND o.user_id = :customer_id
GROUP BY o.id
HAVING o.subtotal_paise <> COALESCE(SUM(i.line_total_paise), 0)
    OR COUNT(i.id) = 0;

-- 4. Reconcile ledger sum against cache. A healthy account has no result here.
SELECT a.id, a.balance, COALESCE(SUM(t.delta), 0) AS ledger_balance
FROM subscription_credits AS a
LEFT JOIN credit_transactions AS t ON t.account_id = a.id
WHERE a.id = :account_id AND a.user_id = :customer_id
GROUP BY a.id
HAVING a.balance <> COALESCE(SUM(t.delta), 0);

-- 5. Kitchen quantities use committed order snapshots, excluding unpaid/cancelled.
-- Group by menu offering too: identical display names need not identify one dish.
SELECT i.menu_item_id, i.food_name, SUM(i.quantity) AS portions
FROM orders AS o
JOIN order_items AS i ON i.order_id = o.id
WHERE o.business_date = :business_date AND o.meal_type = :meal_type
  AND o.status IN ('confirmed', 'preparing', 'ready')
GROUP BY i.menu_item_id, i.food_name
ORDER BY i.food_name;

-- 6. Business-date expiry candidates; execution of expiry is a later transaction.
SELECT id, user_id, expires_on
FROM subscriptions
WHERE status IN ('active', 'paused')
  AND expires_on <= (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')::date;

-- 7. Read refundable-capacity evidence; a service must lock the payment first
-- when acting on this value, and verify capture/status/provider state.
SELECT p.id, p.amount_paise,
       p.amount_paise - COALESCE(SUM(r.amount_paise)
         FILTER (WHERE r.status IN ('requested', 'processing', 'succeeded')), 0)
         AS unreserved_paise
FROM payments AS p
LEFT JOIN refunds AS r ON r.payment_id = p.id
WHERE p.id = :payment_id AND p.user_id = :customer_id AND p.status = 'captured'
GROUP BY p.id;
