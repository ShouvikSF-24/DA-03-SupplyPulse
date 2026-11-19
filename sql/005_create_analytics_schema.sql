
-- ============================================================
-- SupplyPulse
-- Day 2: Analytics Star Schema
-- Script: 005_create_analytics_schema.sql
-- PostgreSQL 16
--
-- Fact grain: One row per DataCo order item.
-- Existing Core and Staging tables are not modified.
-- ============================================================


-- 1. CUSTOMER DIMENSION

CREATE TABLE IF NOT EXISTS analytics.dim_customer_dataco (
    customer_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL UNIQUE,
    customer_segment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 2. PRODUCT DIMENSION

CREATE TABLE IF NOT EXISTS analytics.dim_product (
    product_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id INTEGER NOT NULL UNIQUE,
    category_id INTEGER,
    category_name TEXT,
    department_id INTEGER,
    department_name TEXT,
    product_name TEXT,
    product_price NUMERIC(18,2),
    product_status INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 3. DATE DIMENSION

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    calendar_year INTEGER NOT NULL,
    calendar_quarter INTEGER NOT NULL,
    month_number INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    is_weekend BOOLEAN NOT NULL
);


-- 4. GEOGRAPHY DIMENSION

CREATE TABLE IF NOT EXISTS analytics.dim_geography (
    geography_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    market TEXT,
    order_city TEXT,
    order_state TEXT,
    order_country TEXT,
    order_region TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Avoid duplicate geography combinations,
-- including combinations containing NULL values.

CREATE UNIQUE INDEX IF NOT EXISTS
    uq_dim_geography_natural_key
ON analytics.dim_geography (
    market,
    order_city,
    order_state,
    order_country,
    order_region
)
NULLS NOT DISTINCT;


-- 5. ORDER ITEM FACT TABLE

CREATE TABLE IF NOT EXISTS analytics.fact_order_items (

    -- Source-level grain
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,

    -- Dimension references
    customer_key BIGINT NOT NULL,
    product_key BIGINT NOT NULL,
    order_date_key INTEGER,
    shipping_date_key INTEGER,
    geography_key BIGINT,

    -- Original timestamps
    order_timestamp TIMESTAMP,
    shipping_timestamp TIMESTAMP,

    -- Order attributes
    payment_type TEXT,
    order_status TEXT,
    delivery_status TEXT,
    shipping_mode TEXT,
    late_delivery_risk SMALLINT,

    -- Shipping performance
    days_for_shipping_real INTEGER,
    days_for_shipment_scheduled INTEGER,

    -- Business measures
    quantity INTEGER,
    sales NUMERIC(18,2),
    discount NUMERIC(18,2),
    discount_rate NUMERIC(18,6),
    order_item_total NUMERIC(18,2),

    -- Preserved source measures.
    -- Benefit aggregation is not yet validated.
    benefit_per_order NUMERIC(18,2),
    profit_ratio NUMERIC(18,6),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Referential integrity
    CONSTRAINT fk_fact_customer
        FOREIGN KEY (customer_key)
        REFERENCES analytics.dim_customer_dataco(customer_key),

    CONSTRAINT fk_fact_product
        FOREIGN KEY (product_key)
        REFERENCES analytics.dim_product(product_key),

    CONSTRAINT fk_fact_order_date
        FOREIGN KEY (order_date_key)
        REFERENCES analytics.dim_date(date_key),

    CONSTRAINT fk_fact_shipping_date
        FOREIGN KEY (shipping_date_key)
        REFERENCES analytics.dim_date(date_key),

    CONSTRAINT fk_fact_geography
        FOREIGN KEY (geography_key)
        REFERENCES analytics.dim_geography(geography_key)
);


-- 6. FACT TABLE INDEXES

CREATE INDEX IF NOT EXISTS idx_fact_order_id
    ON analytics.fact_order_items(order_id);

CREATE INDEX IF NOT EXISTS idx_fact_customer_key
    ON analytics.fact_order_items(customer_key);

CREATE INDEX IF NOT EXISTS idx_fact_product_key
    ON analytics.fact_order_items(product_key);

CREATE INDEX IF NOT EXISTS idx_fact_order_date
    ON analytics.fact_order_items(order_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_shipping_date
    ON analytics.fact_order_items(shipping_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_geography
    ON analytics.fact_order_items(geography_key);


-- ============================================================
-- END OF SCRIPT
-- ============================================================
