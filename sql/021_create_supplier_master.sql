
CREATE TABLE IF NOT EXISTS core.suppliers (
    supplier_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    supplier_code TEXT NOT NULL UNIQUE,
    supplier_name TEXT NOT NULL,
    supplier_region TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    average_lead_time_days INTEGER NOT NULL CHECK (average_lead_time_days > 0),
    is_simulated BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
