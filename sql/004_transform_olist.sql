
BEGIN;

INSERT INTO core.olist_customers (
    customer_id,
    customer_unique_id,
    zip_code_prefix,
    customer_city,
    customer_state
)
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM staging.olist_customers_raw
ON CONFLICT (customer_id) DO NOTHING;

COMMIT;
