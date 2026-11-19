
CREATE TABLE IF NOT EXISTS core.inventory_snapshots (
    snapshot_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    inventory_id BIGINT NOT NULL REFERENCES core.inventory_master(inventory_id),
    product_id INTEGER NOT NULL REFERENCES core.products(product_id),
    snapshot_date DATE NOT NULL,
    available_stock INTEGER NOT NULL CHECK (available_stock >= 0),
    reserved_stock INTEGER NOT NULL CHECK (reserved_stock >= 0),
    reorder_level INTEGER NOT NULL,
    warehouse_code TEXT NOT NULL,
    is_simulated BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (inventory_id, snapshot_date)
);
