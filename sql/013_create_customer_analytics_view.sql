
CREATE OR REPLACE VIEW analytics.vw_customer_analytics AS
WITH customer_metrics AS (
    SELECT
        customer_key,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(quantity) AS total_quantity,
        SUM(sales) AS gross_sales,
        SUM(discount) AS total_discount,
        SUM(order_item_total) AS net_item_value,
        SUM(benefit_per_order) AS total_benefit
    FROM analytics.fact_order_items
    GROUP BY customer_key
)
SELECT
    c.customer_segment,
    COUNT(*) AS total_customers,
    SUM(COALESCE(m.total_orders, 0)) AS total_orders,
    SUM(COALESCE(m.total_quantity, 0)) AS total_quantity,
    ROUND(SUM(COALESCE(m.gross_sales, 0)), 2) AS gross_sales,
    ROUND(SUM(COALESCE(m.total_discount, 0)), 2) AS total_discount,
    ROUND(SUM(COALESCE(m.net_item_value, 0)), 2) AS net_item_value,
    ROUND(SUM(COALESCE(m.total_benefit, 0)), 2) AS total_benefit,
    ROUND(
        SUM(COALESCE(m.net_item_value, 0))
        / NULLIF(SUM(COALESCE(m.total_orders, 0)), 0), 2
    ) AS average_order_value,
    ROUND(
        AVG(COALESCE(m.total_orders, 0)), 2
    ) AS average_orders_per_customer
FROM analytics.dim_customer_dataco c
LEFT JOIN customer_metrics m
    ON c.customer_key = m.customer_key
GROUP BY c.customer_segment;
