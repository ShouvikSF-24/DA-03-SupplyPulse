
WITH ranked_products AS (
    SELECT
        inventory_id,
        ROW_NUMBER() OVER (ORDER BY product_id) AS rn
    FROM core.inventory_master
)
UPDATE core.inventory_snapshots s
SET available_stock = CASE
    WHEN rp.rn <= 10 THEN 0
    WHEN rp.rn <= 30 THEN im.safety_stock + 1
    ELSE im.reorder_level + 20
END
FROM ranked_products rp
JOIN core.inventory_master im
    ON rp.inventory_id = im.inventory_id
WHERE s.inventory_id = rp.inventory_id
  AND s.snapshot_date = CURRENT_DATE;
