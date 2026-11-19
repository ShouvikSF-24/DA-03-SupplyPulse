
BEGIN;

-- Step 1: Correct the meaning of the Type column.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'orders'
          AND column_name = 'order_type'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'orders'
          AND column_name = 'payment_type'
    )
    THEN
        ALTER TABLE core.orders
        RENAME COLUMN order_type TO payment_type;
    END IF;
END $$;


-- Step 2: Load unique DataCo customers.
INSERT INTO core.customers_dataco (
    customer_id,
    customer_segment
)
SELECT DISTINCT ON (source_data->>'Customer Id')
    (source_data->>'Customer Id')::BIGINT,
    source_data->>'Customer Segment'
FROM staging.dataco_raw
ORDER BY source_data->>'Customer Id'
ON CONFLICT (customer_id) DO NOTHING;


-- Step 3: Load unique products.
INSERT INTO core.products (
    product_id,
    category_id,
    category_name,
    department_id,
    department_name,
    product_name,
    product_price,
    product_status
)
SELECT DISTINCT ON (source_data->>'Product Card Id')
    (source_data->>'Product Card Id')::INTEGER,
    NULLIF(source_data->>'Category Id', '')::INTEGER,
    source_data->>'Category Name',
    NULLIF(source_data->>'Department Id', '')::INTEGER,
    source_data->>'Department Name',
    source_data->>'Product Name',
    NULLIF(source_data->>'Product Price', '')::NUMERIC(14, 2),
    NULLIF(source_data->>'Product Status', '')::INTEGER
FROM staging.dataco_raw
ORDER BY source_data->>'Product Card Id'
ON CONFLICT (product_id) DO NOTHING;


-- Step 4: Load one record per order.
INSERT INTO core.orders (
    order_id,
    customer_id,
    payment_type,
    order_date,
    shipping_date,
    order_status,
    delivery_status,
    late_delivery_risk,
    shipping_mode,
    days_for_shipping_real,
    days_for_shipment_scheduled,
    market,
    order_city,
    order_state,
    order_country,
    order_region
)
SELECT DISTINCT ON (source_data->>'Order Id')
    (source_data->>'Order Id')::BIGINT,
    (source_data->>'Order Customer Id')::BIGINT,
    source_data->>'Type',
    TO_TIMESTAMP(
        source_data->>'order date (DateOrders)',
        'FMMM/FMDD/YYYY HH24:MI'
    )::TIMESTAMP,
    TO_TIMESTAMP(
        source_data->>'shipping date (DateOrders)',
        'FMMM/FMDD/YYYY HH24:MI'
    )::TIMESTAMP,
    source_data->>'Order Status',
    source_data->>'Delivery Status',
    NULLIF(source_data->>'Late_delivery_risk', '')::SMALLINT,
    source_data->>'Shipping Mode',
    NULLIF(source_data->>'Days for shipping (real)', '')::INTEGER,
    NULLIF(source_data->>'Days for shipment (scheduled)', '')::INTEGER,
    source_data->>'Market',
    source_data->>'Order City',
    source_data->>'Order State',
    source_data->>'Order Country',
    source_data->>'Order Region'
FROM staging.dataco_raw
ORDER BY source_data->>'Order Id'
ON CONFLICT (order_id) DO NOTHING;


-- Step 5: Load individual order items.
INSERT INTO core.order_items (
    order_item_id,
    order_id,
    product_id,
    quantity,
    product_price,
    discount,
    discount_rate,
    profit_ratio,
    sales,
    order_item_total,
    order_profit_per_order,
    benefit_per_order,
    sales_per_customer
)
SELECT
    (source_data->>'Order Item Id')::BIGINT,
    (source_data->>'Order Id')::BIGINT,
    (source_data->>'Order Item Cardprod Id')::INTEGER,
    NULLIF(source_data->>'Order Item Quantity', '')::INTEGER,
    NULLIF(source_data->>'Order Item Product Price', '')::NUMERIC(14, 2),
    NULLIF(source_data->>'Order Item Discount', '')::NUMERIC(14, 2),
    NULLIF(source_data->>'Order Item Discount Rate', '')::NUMERIC(10, 6),
    NULLIF(source_data->>'Order Item Profit Ratio', '')::NUMERIC(12, 6),
    NULLIF(source_data->>'Sales', '')::NUMERIC(16, 2),
    NULLIF(source_data->>'Order Item Total', '')::NUMERIC(16, 2),
    NULLIF(source_data->>'Order Profit Per Order', '')::NUMERIC(16, 2),
    NULLIF(source_data->>'Benefit per order', '')::NUMERIC(16, 2),
    NULLIF(source_data->>'Sales per customer', '')::NUMERIC(16, 2)
FROM staging.dataco_raw
ON CONFLICT (order_item_id) DO NOTHING;

COMMIT;
