-- MySQL triggers for DBMS viva documentation ONLY.
-- Production: Django ORM already handles stock + tracking in orders/services.py.
-- Do NOT deploy trg_orderitem_reduce_stock — it would double-decrement stock.
-- If previously deployed, run the DROP statements below.

DROP TRIGGER IF EXISTS trg_orderitem_reduce_stock;
DROP TRIGGER IF EXISTS trg_order_status_track;

-- Optional read-only audit trigger (safe — does not modify stock):
-- DELIMITER //
-- CREATE TRIGGER IF NOT EXISTS trg_order_status_audit
-- AFTER UPDATE ON orders_order
-- FOR EACH ROW
-- BEGIN
--     IF OLD.status != NEW.status THEN
--         INSERT INTO orders_ordertracking (order_id, status, message, location, recorded_at)
--         VALUES (NEW.id, NEW.status, CONCAT('Audit: status -> ', NEW.status), 'DB Trigger', NOW(6));
--     END IF;
-- END//
-- DELIMITER ;
