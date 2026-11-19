
-- =========================================================
-- SUPPLYPULSE
-- Initial PostgreSQL database architecture
-- =========================================================

BEGIN;

-- 1. Create schemas
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;


-- 2. DataCo customer dimension
CREATE TABLE IF NOT EXISTS core.customers_dataco (
    customer_id BIGINT PRIMARY KEY,
    customer_segment TEXT
);


-- 3. Product dimension
CREATE TABLE IF NOT EXISTS core.products (
    product_id INTEGER PRIMARY KEY,
    category_id INTEGER,
    category_name TEXT,
    department_id INTEGER,
    department_name TEXT,
    product_name TEXT,
    product_price NUMERIC(14, 2),
    product_status INTEGER
);


-- 4. Olist customer dimension
CREATE TABLE IF NOT EXISTS core.olist_customers (
    customer_id TEXT PRIMARY KEY,
    customer_unique_id TEXT NOT NULL,
    zip_code_prefix INTEGER,
    customer_city TEXT,
    customer_state VARCHAR(2)
);


-- 5. Orders table
CREATE TABLE IF NOT EXISTS core.orders (
    order_id BIGINT PRIMARY KEY,

    customer_id BIGINT NOT NULL
        REFERENCES core.customers_dataco(customer_id),

    order_type TEXT,
    order_date TIMESTAMP,
    shipping_date TIMESTAMP,

    order_status TEXT,
    delivery_status TEXT,
    late_delivery_risk SMALLINT,

    shipping_mode TEXT,

    days_for_shipping_real INTEGER,
    days_for_shipment_scheduled INTEGER,

    market TEXT,
    order_city TEXT,
    order_state TEXT,
    order_country TEXT,
    order_region TEXT
);


-- 6. Order items fact table
CREATE TABLE IF NOT EXISTS core.order_items (
    order_item_id BIGINT PRIMARY KEY,

    order_id BIGINT NOT NULL
        REFERENCES core.orders(order_id),

    product_id INTEGER NOT NULL
        REFERENCES core.products(product_id),

    quantity INTEGER,

    product_price NUMERIC(14, 2),
    discount NUMERIC(14, 2),
    discount_rate NUMERIC(10, 6),

    profit_ratio NUMERIC(12, 6),

    sales NUMERIC(16, 2),
    order_item_total NUMERIC(16, 2),

    order_profit_per_order NUMERIC(16, 2),
    benefit_per_order NUMERIC(16, 2),
    sales_per_customer NUMERIC(16, 2)
);


-- 7. Useful indexes
CREATE INDEX IF NOT EXISTS idx_orders_customer
    ON core.orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_orders_date
    ON core.orders(order_date);

CREATE INDEX IF NOT EXISTS idx_orders_status
    ON core.orders(order_status);

CREATE INDEX IF NOT EXISTS idx_order_items_order
    ON core.order_items(order_id);

CREATE INDEX IF NOT EXISTS idx_order_items_product
    ON core.order_items(product_id);

CREATE INDEX IF NOT EXISTS idx_olist_unique_customer
    ON core.olist_customers(customer_unique_id);

COMMIT;
