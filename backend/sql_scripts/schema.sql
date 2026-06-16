-- E-Commerce DBMS Schema (MySQL 8)
-- Run on cloud MySQL before Django migrate (optional reference)

CREATE DATABASE IF NOT EXISTS ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecommerce_db;

-- Django auth tables are created by migrate; below are business tables reference

-- CATEGORY
CREATE TABLE IF NOT EXISTS catalog_category (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(120) NOT NULL UNIQUE,
    description LONGTEXT NOT NULL
);

-- PRODUCT
CREATE TABLE IF NOT EXISTS catalog_product (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    category_id BIGINT NOT NULL,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(220) NOT NULL UNIQUE,
    description LONGTEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    stock_quantity INT UNSIGNED NOT NULL DEFAULT 0,
    image_url VARCHAR(500) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL,
    CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES catalog_category(id) ON DELETE RESTRICT,
    INDEX idx_product_category (category_id, is_active),
    INDEX idx_product_slug (slug)
);

-- CART (1 user = 1 cart)
CREATE TABLE IF NOT EXISTS cart_cart (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    updated_at DATETIME(6) NOT NULL,
    CONSTRAINT fk_cart_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- CART_ITEM (cart values / line items)
CREATE TABLE IF NOT EXISTS cart_cartitem (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cart_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT UNSIGNED NOT NULL CHECK (quantity >= 1),
    CONSTRAINT fk_cartitem_cart FOREIGN KEY (cart_id) REFERENCES cart_cart(id) ON DELETE CASCADE,
    CONSTRAINT fk_cartitem_product FOREIGN KEY (product_id) REFERENCES catalog_product(id) ON DELETE CASCADE,
    CONSTRAINT uq_cart_product UNIQUE (cart_id, product_id),
    INDEX idx_cartitem_cart (cart_id, product_id)
);

-- ADDRESS
CREATE TABLE IF NOT EXISTS orders_address (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    line1 VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    is_default TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME(6) NOT NULL,
    CONSTRAINT fk_address_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- ORDER
CREATE TABLE IF NOT EXISTS orders_order (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    address_id BIGINT NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    order_date DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    CONSTRAINT fk_order_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE RESTRICT,
    CONSTRAINT fk_order_address FOREIGN KEY (address_id) REFERENCES orders_address(id) ON DELETE RESTRICT,
    INDEX idx_order_user_status (user_id, status)
);

-- ORDER_ITEM
CREATE TABLE IF NOT EXISTS orders_orderitem (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT UNSIGNED NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_orderitem_order FOREIGN KEY (order_id) REFERENCES orders_order(id) ON DELETE CASCADE,
    CONSTRAINT fk_orderitem_product FOREIGN KEY (product_id) REFERENCES catalog_product(id) ON DELETE RESTRICT,
    INDEX idx_orderitem_order (order_id, product_id)
);

-- PAYMENT (1:1 with ORDER)
CREATE TABLE IF NOT EXISTS orders_payment (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE,
    payment_method VARCHAR(20) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    transaction_id VARCHAR(100) NOT NULL,
    paid_at DATETIME(6) NULL,
    CONSTRAINT fk_payment_order FOREIGN KEY (order_id) REFERENCES orders_order(id) ON DELETE CASCADE
);

-- ORDER_TRACKING (track order timeline)
CREATE TABLE IF NOT EXISTS orders_ordertracking (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL,
    message VARCHAR(255) NOT NULL,
    location VARCHAR(120) NOT NULL,
    recorded_at DATETIME(6) NOT NULL,
    CONSTRAINT fk_tracking_order FOREIGN KEY (order_id) REFERENCES orders_order(id) ON DELETE CASCADE,
    INDEX idx_tracking_order (order_id, recorded_at)
);
