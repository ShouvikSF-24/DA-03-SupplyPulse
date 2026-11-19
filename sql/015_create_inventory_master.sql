
CREATE TABLE IF NOT EXISTS core.inventory_master (
    inventory_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id INTEGER NOT NULL UNIQUE REFERENCES core.products(product_id),
    opening_stock INTEGER NOT NULL CHECK (opening_stock >= 0),
    reorder_level INTEGER NOT NULL CHECK (reorder_level >= 0),
    safety_stock INTEGER NOT NULL CHECK (safety_stock >= 0),
    warehouse_code TEXT NOT NULL,
    is_simulated BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
