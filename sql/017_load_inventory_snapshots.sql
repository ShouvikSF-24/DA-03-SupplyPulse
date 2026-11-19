
INSERT INTO core.inventory_snapshots (
    inventory_id,
    product_id,
    snapshot_date,
    available_stock,
    reserved_stock,
    reorder_level,
    warehouse_code,
    is_simulated
)
SELECT
    inventory_id,
    product_id,
    CURRENT_DATE,
    opening_stock - (product_id % 21),
    product_id % 21,
    reorder_level,
    warehouse_code,
    TRUE
FROM core.inventory_master
ON CONFLICT (inventory_id, snapshot_date) DO NOTHING;
