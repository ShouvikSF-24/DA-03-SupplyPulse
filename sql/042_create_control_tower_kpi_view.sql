
CREATE OR REPLACE VIEW analytics.vw_control_tower_kpis AS
WITH inventory_metrics AS (
    SELECT
        COUNT(*) AS total_inventory_products,
        COUNT(*) FILTER (WHERE available_stock = 0) AS stockout_products,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE available_stock = 0)
            / NULLIF(COUNT(*), 0), 2
        ) AS stockout_rate_pct
    FROM analytics.vw_inventory_risk
),
supplier_metrics AS (
    SELECT
        ROUND(
            100.0 * SUM(on_time_orders)
            / NULLIF(SUM(total_purchase_orders), 0), 2
        ) AS on_time_delivery_pct,
        ROUND(
            SUM(average_actual_lead_time_days * total_purchase_orders)
            / NULLIF(SUM(total_purchase_orders), 0), 2
        ) AS average_actual_lead_time_days
    FROM analytics.vw_supplier_performance
),
doi_metrics AS (
    SELECT
        ROUND(AVG(days_of_inventory)::numeric, 2)
            AS average_days_of_inventory,
        ROUND(
            PERCENTILE_CONT(0.5)
            WITHIN GROUP (ORDER BY days_of_inventory)::numeric,
            2
        ) AS median_days_of_inventory
    FROM analytics.inventory_days_of_inventory
)
SELECT
    i.total_inventory_products,
    i.stockout_products,
    i.stockout_rate_pct,
    s.on_time_delivery_pct,
    s.average_actual_lead_time_days,
    d.average_days_of_inventory,
    d.median_days_of_inventory
FROM inventory_metrics i
CROSS JOIN supplier_metrics s
CROSS JOIN doi_metrics d;
