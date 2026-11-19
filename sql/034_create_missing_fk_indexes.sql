
CREATE INDEX IF NOT EXISTS idx_inventory_snapshots_product_id
ON core.inventory_snapshots (product_id);

CREATE INDEX IF NOT EXISTS idx_product_suppliers_supplier_id
ON core.product_suppliers (supplier_id);

CREATE INDEX IF NOT EXISTS idx_supplier_performance_supplier_id
ON core.supplier_performance (supplier_id);
