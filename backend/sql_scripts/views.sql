-- Sales by category view
CREATE OR REPLACE VIEW v_category_sales AS
SELECT
    c.id AS category_id,
    c.name AS category_name,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.subtotal) AS total_revenue
FROM catalog_category c
JOIN catalog_product p ON p.category_id = c.id
JOIN orders_orderitem oi ON oi.product_id = p.id
JOIN orders_order o ON o.id = oi.order_id AND o.status != 'cancelled'
GROUP BY c.id, c.name;

-- Active cart summary per user
CREATE OR REPLACE VIEW v_cart_summary AS
SELECT
    u.id AS user_id,
    u.username,
    COUNT(ci.id) AS line_items,
    SUM(ci.quantity) AS total_units,
    SUM(ci.quantity * p.price) AS cart_value
FROM auth_user u
JOIN cart_cart cart ON cart.user_id = u.id
JOIN cart_cartitem ci ON ci.cart_id = cart.id
JOIN catalog_product p ON p.id = ci.product_id
GROUP BY u.id, u.username;

-- Order tracking overview
CREATE OR REPLACE VIEW v_order_tracking AS
SELECT
    o.id AS order_id,
    o.status AS current_status,
    o.total_amount,
    u.username,
    p.status AS payment_status,
    COUNT(t.id) AS tracking_events,
    MAX(t.recorded_at) AS last_update
FROM orders_order o
JOIN auth_user u ON u.id = o.user_id
LEFT JOIN orders_payment p ON p.order_id = o.id
LEFT JOIN orders_ordertracking t ON t.order_id = o.id
GROUP BY o.id, o.status, o.total_amount, u.username, p.status;
