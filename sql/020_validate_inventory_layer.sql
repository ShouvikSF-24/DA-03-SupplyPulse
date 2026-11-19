
SELECT
    (SELECT COUNT(*) FROM core.inventory_master) AS inventory_master_records,
    (SELECT COUNT(*) FROM core.inventory_snapshots) AS snapshot_records,
    (SELECT COUNT(DISTINCT product_id) FROM core.inventory_snapshots) AS unique_snapshot_products,
    (SELECT COUNT(*) FROM analytics.vw_inventory_risk) AS risk_view_records,
    (SELECT COUNT(*) FROM analytics.vw_inventory_risk WHERE inventory_status = 'CRITICAL') AS critical_products,
    (SELECT COUNT(*) FROM analytics.vw_inventory_risk WHERE inventory_status = 'LOW STOCK') AS low_stock_products,
    (SELECT COUNT(*) FROM analytics.vw_inventory_risk WHERE inventory_status = 'HEALTHY') AS healthy_products,
    (SELECT COUNT(*) FROM core.inventory_snapshots WHERE available_stock < 0 OR reserved_stock < 0) AS invalid_stock_records,
    (SELECT COUNT(*) FROM core.inventory_snapshots WHERE is_simulated = TRUE) AS simulated_records;
