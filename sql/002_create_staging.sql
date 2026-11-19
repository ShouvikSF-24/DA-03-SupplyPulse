
BEGIN;

CREATE TABLE IF NOT EXISTS staging.dataco_raw (
    source_row_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_data JSONB NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staging.olist_customers_raw (
    source_row_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id TEXT NOT NULL,
    customer_unique_id TEXT NOT NULL,
    customer_zip_code_prefix INTEGER,
    customer_city TEXT,
    customer_state VARCHAR(2),
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dataco_raw_ingested
    ON staging.dataco_raw(ingested_at);

CREATE INDEX IF NOT EXISTS idx_olist_raw_customer
    ON staging.olist_customers_raw(customer_id);

COMMIT;
