
SELECT *
FROM (
    VALUES
    ('customer_dimension',
        (SELECT COUNT(*)::BIGINT FROM analytics.dim_customer_dataco)),
    ('customers_dataco',
        (SELECT COUNT(*)::BIGINT FROM core.customers_dataco)),
    ('products',
        (SELECT COUNT(*)::BIGINT FROM core.products)),
    ('orders',
        (SELECT COUNT(*)::BIGINT FROM core.orders)),
    ('core_order_items',
        (SELECT COUNT(*)::BIGINT FROM core.order_items)),
    ('fact_order_items',
        (SELECT COUNT(*)::BIGINT FROM analytics.fact_order_items)),
    ('suppliers',
        (SELECT COUNT(*)::BIGINT FROM core.suppliers)),
    ('product_supplier_mappings',
        (SELECT COUNT(*)::BIGINT FROM core.product_suppliers)),
    ('supplier_purchase_orders',
        (SELECT COUNT(*)::BIGINT FROM core.supplier_performance)),
    ('inventory_records',
        (SELECT COUNT(*)::BIGINT FROM core.inventory_master)),
    ('inventory_snapshots',
        (SELECT COUNT(*)::BIGINT FROM core.inventory_snapshots))
) AS reconciliation(table_name, total_records)
ORDER BY table_name;
