-- =====================================================
-- Smart E-Commerce - Views for Reporting
-- =====================================================
USE smart_ecommerce;

-- 1. Product Sales Report
DROP VIEW IF EXISTS vw_product_sales;
CREATE VIEW vw_product_sales AS
SELECT
    p.product_id,
    p.product_name,
    c.category_name,
    SUM(oi.quantity)                    AS units_sold,
    SUM(oi.quantity * oi.unit_price)    AS revenue
FROM Order_Items oi
JOIN Product  p ON p.product_id  = oi.product_id
JOIN Category c ON c.category_id = p.category_id
JOIN Orders   o ON o.order_id    = oi.order_id
WHERE o.status IN ('PAID','SHIPPED','DELIVERED')
GROUP BY p.product_id, p.product_name, c.category_name;

-- 2. Customer Lifetime Value
DROP VIEW IF EXISTS vw_customer_ltv;
CREATE VIEW vw_customer_ltv AS
SELECT
    cu.customer_id,
    cu.full_name,
    cu.country,
    COUNT(DISTINCT o.order_id)          AS total_orders,
    COALESCE(SUM(o.total_amount), 0)    AS lifetime_value,
    MAX(o.order_date)                   AS last_order_date
FROM Customer cu
LEFT JOIN Orders o ON o.customer_id = cu.customer_id
GROUP BY cu.customer_id, cu.full_name, cu.country;

-- 3. Top Rated Products
DROP VIEW IF EXISTS vw_top_rated;
CREATE VIEW vw_top_rated AS
SELECT
    p.product_id,
    p.product_name,
    ROUND(AVG(r.rating), 2)     AS avg_rating,
    COUNT(r.review_id)          AS review_count
FROM Product p
JOIN Reviews r ON r.product_id = p.product_id
GROUP BY p.product_id, p.product_name
HAVING review_count >= 1
ORDER BY avg_rating DESC, review_count DESC;

-- 4. Category Sales Summary
DROP VIEW IF EXISTS vw_category_summary;
CREATE VIEW vw_category_summary AS
SELECT
    c.category_id,
    c.category_name,
    COUNT(DISTINCT p.product_id)            AS product_count,
    COALESCE(SUM(oi.quantity), 0)           AS total_units_sold,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue
FROM Category c
LEFT JOIN Product p     ON p.category_id = c.category_id
LEFT JOIN Order_Items oi ON oi.product_id = p.product_id
GROUP BY c.category_id, c.category_name;