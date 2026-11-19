
CREATE TABLE IF NOT EXISTS core.product_suppliers (
    product_supplier_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES core.products(product_id),
    supplier_id BIGINT NOT NULL REFERENCES core.suppliers(supplier_id),
    is_primary_supplier BOOLEAN NOT NULL DEFAULT TRUE,
    unit_cost NUMERIC(12,2) NOT NULL CHECK (unit_cost >= 0),
    is_simulated BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (product_id, supplier_id)
);
