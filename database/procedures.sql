-- =====================================================
-- Smart E-Commerce - Stored Procedures (v2)
-- =====================================================
USE smart_ecommerce;

DROP PROCEDURE IF EXISTS sp_place_order;
DROP PROCEDURE IF EXISTS sp_customer_summary;

DELIMITER $$

CREATE PROCEDURE sp_place_order (
    IN  p_customer_id INT,
    IN  p_items_json  JSON,
    OUT p_order_id    INT
)
BEGIN
    DECLARE v_i       INT DEFAULT 0;
    DECLARE v_n       INT DEFAULT 0;
    DECLARE v_pid     INT;
    DECLARE v_qty     INT;
    DECLARE v_price   DECIMAL(10,2);
    DECLARE v_total   DECIMAL(12,2) DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- 1. Create empty order
    INSERT INTO Orders (customer_id, status, total_amount)
    VALUES (p_customer_id, 'PENDING', 0);
    SET p_order_id = LAST_INSERT_ID();

    -- 2. Count items in JSON
    SELECT JSON_LENGTH(p_items_json) INTO v_n;

    -- 3. Loop over items, inserting one at a time
    WHILE v_i < v_n DO
        SET v_pid = JSON_UNQUOTE(JSON_EXTRACT(p_items_json, CONCAT('$[', v_i, '].product_id')));
        SET v_qty = JSON_UNQUOTE(JSON_EXTRACT(p_items_json, CONCAT('$[', v_i, '].qty')));

        -- Fetch price (SELECT INTO avoids holding a lock during trigger)
        SELECT unit_price INTO v_price
        FROM Product WHERE product_id = v_pid;

        IF v_price IS NOT NULL THEN
            -- This INSERT fires trg_order_item_insert (stock) and
            -- trg_purchase_interaction (log purchase). Safe now because
            -- we're not inside a SELECT...FROM Product anymore.
            INSERT INTO Order_Items (order_id, product_id, quantity, unit_price)
            VALUES (p_order_id, v_pid, v_qty, v_price);

            SET v_total = v_total + (v_qty * v_price);
        END IF;

        SET v_i = v_i + 1;
    END WHILE;

    -- 4. Update order total
    UPDATE Orders SET total_amount = v_total WHERE order_id = p_order_id;

    COMMIT;
END$$

CREATE PROCEDURE sp_customer_summary (IN p_customer_id INT)
BEGIN
    SELECT
        cu.customer_id,
        cu.full_name,
        cu.country,
        COUNT(DISTINCT o.order_id)         AS orders,
        COALESCE(SUM(o.total_amount), 0)   AS spend,
        (SELECT COUNT(*) FROM Reviews  r WHERE r.customer_id = cu.customer_id) AS review_count,
        (SELECT COUNT(*) FROM Wishlist w WHERE w.customer_id = cu.customer_id) AS wishlist_count
    FROM Customer cu
    LEFT JOIN Orders o ON o.customer_id = cu.customer_id
    WHERE cu.customer_id = p_customer_id
    GROUP BY cu.customer_id, cu.full_name, cu.country;
END$$

DELIMITER ;