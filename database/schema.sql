-- =====================================================
-- Smart E-Commerce DBMS - Schema
-- =====================================================
DROP DATABASE IF EXISTS smart_ecommerce;
CREATE DATABASE smart_ecommerce CHARACTER SET utf8mb4;
USE smart_ecommerce;

-- ---------- CUSTOMER ----------
CREATE TABLE Customer (
    customer_id     INT PRIMARY KEY AUTO_INCREMENT,
    full_name       VARCHAR(120) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    country         VARCHAR(60),
    signup_date     DATE NOT NULL DEFAULT (CURRENT_DATE)
);

-- ---------- CATEGORY ----------
CREATE TABLE Category (
    category_id     INT PRIMARY KEY AUTO_INCREMENT,
    category_name   VARCHAR(80) NOT NULL UNIQUE,
    description     VARCHAR(255)
);

-- ---------- PRODUCT ----------
CREATE TABLE Product (
    product_id      INT PRIMARY KEY AUTO_INCREMENT,
    stock_code      VARCHAR(30) NOT NULL UNIQUE,
    product_name    VARCHAR(200) NOT NULL,
    category_id     INT NOT NULL,
    unit_price      DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    stock_quantity  INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id) REFERENCES Category(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------- ORDERS ----------
CREATE TABLE Orders (
    order_id        INT PRIMARY KEY AUTO_INCREMENT,
    customer_id     INT NOT NULL,
    order_date      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status          ENUM('PENDING','PAID','SHIPPED','DELIVERED','CANCELLED')
                    NOT NULL DEFAULT 'PENDING',
    total_amount    DECIMAL(12,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- ---------- ORDER_ITEMS ----------
CREATE TABLE Order_Items (
    order_id        INT NOT NULL,
    product_id      INT NOT NULL,
    quantity        INT NOT NULL CHECK (quantity > 0),
    unit_price      DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, product_id),
    CONSTRAINT fk_oi_order   FOREIGN KEY (order_id)
        REFERENCES Orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_oi_product FOREIGN KEY (product_id)
        REFERENCES Product(product_id) ON DELETE RESTRICT
);

-- ---------- PAYMENT ----------
CREATE TABLE Payment (
    payment_id      INT PRIMARY KEY AUTO_INCREMENT,
    order_id        INT NOT NULL UNIQUE,
    method          ENUM('CARD','UPI','NETBANKING','COD') NOT NULL,
    amount          DECIMAL(12,2) NOT NULL,
    paid_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    status          ENUM('SUCCESS','FAILED','REFUNDED') NOT NULL DEFAULT 'SUCCESS',
    CONSTRAINT fk_payment_order FOREIGN KEY (order_id)
        REFERENCES Orders(order_id) ON DELETE CASCADE
);

-- ---------- REVIEWS ----------
CREATE TABLE Reviews (
    review_id       INT PRIMARY KEY AUTO_INCREMENT,
    customer_id     INT NOT NULL,
    product_id      INT NOT NULL,
    rating          TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment         VARCHAR(500),
    review_date     DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_review (customer_id, product_id),
    CONSTRAINT fk_rev_customer FOREIGN KEY (customer_id)
        REFERENCES Customer(customer_id) ON DELETE CASCADE,
    CONSTRAINT fk_rev_product  FOREIGN KEY (product_id)
        REFERENCES Product(product_id) ON DELETE CASCADE
);

-- ---------- WISHLIST ----------
CREATE TABLE Wishlist (
    wishlist_id     INT PRIMARY KEY AUTO_INCREMENT,
    customer_id     INT NOT NULL,
    product_id      INT NOT NULL,
    added_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_wish (customer_id, product_id),
    CONSTRAINT fk_wish_customer FOREIGN KEY (customer_id)
        REFERENCES Customer(customer_id) ON DELETE CASCADE,
    CONSTRAINT fk_wish_product  FOREIGN KEY (product_id)
        REFERENCES Product(product_id) ON DELETE CASCADE
);

-- ---------- PRODUCT_INTERACTIONS ----------
CREATE TABLE Product_Interactions (
    interaction_id   BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id      INT NOT NULL,
    product_id       INT NOT NULL,
    interaction_type ENUM('view','wishlist','addtocart','purchase') NOT NULL,
    interaction_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_int_customer FOREIGN KEY (customer_id)
        REFERENCES Customer(customer_id) ON DELETE CASCADE,
    CONSTRAINT fk_int_product  FOREIGN KEY (product_id)
        REFERENCES Product(product_id) ON DELETE CASCADE
);