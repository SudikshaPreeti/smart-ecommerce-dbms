-- =====================================================
-- Smart E-Commerce - Triggers
-- =====================================================
USE smart_ecommerce;

DROP TRIGGER IF EXISTS trg_order_item_insert;
DROP TRIGGER IF EXISTS trg_order_cancelled;
DROP TRIGGER IF EXISTS trg_purchase_interaction;

DELIMITER $$

-- 1. Auto-decrement stock when an order item is inserted
CREATE TRIGGER trg_order_item_insert
AFTER INSERT ON Order_Items
FOR EACH ROW
BEGIN
    UPDATE Product
    SET stock_quantity = GREATEST(stock_quantity - NEW.quantity, 0)
    WHERE product_id = NEW.product_id;
END$$

-- 2. Restore stock when an order is cancelled
CREATE TRIGGER trg_order_cancelled
AFTER UPDATE ON Orders
FOR EACH ROW
BEGIN
    IF NEW.status = 'CANCELLED' AND OLD.status <> 'CANCELLED' THEN
        UPDATE Product p
        JOIN Order_Items oi ON oi.product_id = p.product_id
        SET p.stock_quantity = p.stock_quantity + oi.quantity
        WHERE oi.order_id = NEW.order_id;
    END IF;
END$$

-- 3. Auto-log every purchase into Product_Interactions
CREATE TRIGGER trg_purchase_interaction
AFTER INSERT ON Order_Items
FOR EACH ROW
BEGIN
    DECLARE v_customer INT;
    SELECT customer_id INTO v_customer
    FROM Orders WHERE order_id = NEW.order_id;

    INSERT INTO Product_Interactions
        (customer_id, product_id, interaction_type, interaction_time)
    VALUES
        (v_customer, NEW.product_id, 'purchase', NOW());
END$$

DELIMITER ;