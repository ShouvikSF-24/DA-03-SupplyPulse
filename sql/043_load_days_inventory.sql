CREATE TABLE IF NOT EXISTS analytics.inventory_days_of_inventory (
    product_id INTEGER PRIMARY KEY,
    days_of_inventory NUMERIC(12, 2)
);

TRUNCATE TABLE analytics.inventory_days_of_inventory;