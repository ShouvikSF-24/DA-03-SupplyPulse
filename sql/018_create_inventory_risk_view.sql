
CREATE OR REPLACE VIEW analytics.vw_inventory_risk AS
SELECT
    im.product_id,
    p.product_name,
    p.category_name,
    im.warehouse_code,
    s.snapshot_date,
    im.opening_stock,
    s.available_stock,
    s.reserved_stock,
    im.reorder_level,
    im.safety_stock,
    CASE
        WHEN s.available_stock <= im.safety_stock
            THEN 'CRITICAL'
        WHEN s.available_stock <= im.reorder_level
            THEN 'LOW STOCK'
        ELSE 'HEALTHY'
    END AS inventory_status,
    im.is_simulated
FROM core.inventory_master im
JOIN core.products p
    ON im.product_id = p.product_id
JOIN core.inventory_snapshots s
    ON im.inventory_id = s.inventory_id;
