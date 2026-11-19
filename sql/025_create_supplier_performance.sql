
CREATE TABLE IF NOT EXISTS core.supplier_performance (
    performance_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    supplier_id BIGINT NOT NULL REFERENCES core.suppliers(supplier_id),
    purchase_order_code TEXT NOT NULL UNIQUE,
    order_date DATE NOT NULL,
    expected_delivery_date DATE NOT NULL,
    actual_delivery_date DATE NOT NULL,
    ordered_quantity INTEGER NOT NULL CHECK (ordered_quantity > 0),
    received_quantity INTEGER NOT NULL CHECK (received_quantity >= 0),
    accepted_quantity INTEGER NOT NULL CHECK (accepted_quantity >= 0),
    is_simulated BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (received_quantity <= ordered_quantity),
    CHECK (accepted_quantity <= received_quantity)
);
