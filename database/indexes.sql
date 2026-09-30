-- =====================================================
-- Smart E-Commerce - Indexes for Query Optimization
-- =====================================================
USE smart_ecommerce;

-- Product search & filter indexes
CREATE INDEX idx_product_category   ON Product(category_id);
CREATE INDEX idx_product_price      ON Product(unit_price);
CREATE INDEX idx_product_name       ON Product(product_name);
CREATE INDEX idx_product_stock      ON Product(stock_quantity);

-- Order lookups
CREATE INDEX idx_orders_customer    ON Orders(customer_id);
CREATE INDEX idx_orders_date        ON Orders(order_date);
CREATE INDEX idx_orders_status      ON Orders(status);

-- Order items reverse lookup
CREATE INDEX idx_oi_product         ON Order_Items(product_id);

-- Reviews
CREATE INDEX idx_rev_product        ON Reviews(product_id);
CREATE INDEX idx_rev_rating         ON Reviews(rating);
CREATE INDEX idx_rev_customer       ON Reviews(customer_id);

-- Wishlist
CREATE INDEX idx_wish_customer      ON Wishlist(customer_id);
CREATE INDEX idx_wish_product       ON Wishlist(product_id);

-- Product interactions (heavily queried by recommender)
CREATE INDEX idx_int_customer       ON Product_Interactions(customer_id);
CREATE INDEX idx_int_product        ON Product_Interactions(product_id);
CREATE INDEX idx_int_type           ON Product_Interactions(interaction_type);
CREATE INDEX idx_int_time           ON Product_Interactions(interaction_time);

-- Composite index for recommendation queries (very common pattern)
CREATE INDEX idx_int_cust_type      ON Product_Interactions(customer_id, interaction_type);
CREATE INDEX idx_int_prod_type      ON Product_Interactions(product_id, interaction_type);

-- Full-text search on product names
ALTER TABLE Product ADD FULLTEXT idx_ft_product (product_name);