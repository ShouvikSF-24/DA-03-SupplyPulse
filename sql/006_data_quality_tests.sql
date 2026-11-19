
SELECT
    test_name,
    actual_value,
    expected_value,
    CASE
        WHEN actual_value = expected_value THEN 'PASS'
        ELSE 'FAIL'
    END AS test_status
FROM (
    VALUES
    (
        '01_fact_row_count',
        (SELECT COUNT(*)::NUMERIC FROM analytics.fact_order_items),
        (SELECT COUNT(*)::NUMERIC FROM core.order_items)
    ),
    (
        '02_unique_order_item_ids',
        (SELECT COUNT(DISTINCT order_item_id)::NUMERIC FROM analytics.fact_order_items),
        (SELECT COUNT(*)::NUMERIC FROM analytics.fact_order_items)
    ),
    (
        '03_customer_dimension_count',
        (SELECT COUNT(*)::NUMERIC FROM analytics.dim_customer_dataco),
        (SELECT COUNT(*)::NUMERIC FROM core.customers_dataco)
    ),
    (
        '04_product_dimension_count',
        (SELECT COUNT(*)::NUMERIC FROM analytics.dim_product),
        (SELECT COUNT(*)::NUMERIC FROM core.products)
    ),
    (
        '05_geography_dimension_count',
        (SELECT COUNT(*)::NUMERIC FROM analytics.dim_geography),
        (SELECT COUNT(DISTINCT (market, order_city, order_state, order_country, order_region))::NUMERIC FROM core.orders)
    ),
    (
        '06_missing_dimension_keys',
        (SELECT COUNT(*)::NUMERIC FROM analytics.fact_order_items
         WHERE customer_key IS NULL
         OR product_key IS NULL
         OR order_date_key IS NULL
         OR shipping_date_key IS NULL
         OR geography_key IS NULL),
        0::NUMERIC
    ),
    (
        '07_unique_orders',
        (SELECT COUNT(DISTINCT order_id)::NUMERIC FROM analytics.fact_order_items),
        (SELECT COUNT(*)::NUMERIC FROM core.orders)
    ),
    (
        '08_quantity_reconciliation',
        (SELECT SUM(quantity)::NUMERIC FROM analytics.fact_order_items),
        (SELECT SUM(quantity)::NUMERIC FROM core.order_items)
    ),
    (
        '09_sales_reconciliation',
        (SELECT SUM(sales)::NUMERIC FROM analytics.fact_order_items),
        (SELECT SUM(sales)::NUMERIC FROM core.order_items)
    ),
    (
        '10_discount_reconciliation',
        (SELECT SUM(discount)::NUMERIC FROM analytics.fact_order_items),
        (SELECT SUM(discount)::NUMERIC FROM core.order_items)
    ),
    (
        '11_item_value_reconciliation',
        (SELECT SUM(order_item_total)::NUMERIC FROM analytics.fact_order_items),
        (SELECT SUM(order_item_total)::NUMERIC FROM core.order_items)
    )
) AS checks(test_name, actual_value, expected_value)
ORDER BY test_name;
