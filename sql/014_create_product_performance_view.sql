
CREATE OR REPLACE VIEW analytics.vw_product_performance AS
WITH product_metrics AS (
    SELECT
        product_key,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(quantity) AS units_sold,
        SUM(sales) AS gross_sales,
        SUM(discount) AS total_discount,
        SUM(order_item_total) AS net_item_value,
        SUM(benefit_per_order) AS total_benefit,
        AVG(profit_ratio) AS avg_profit_ratio
    FROM analytics.fact_order_items
    GROUP BY product_key
)
SELECT
    p.product_key,
    p.product_id,
    p.product_name,
    p.category_name,
    p.department_name,
    p.product_price,
    p.product_status,
    COALESCE(m.total_orders, 0) AS total_orders,
    COALESCE(m.units_sold, 0) AS units_sold,
    ROUND(COALESCE(m.gross_sales, 0), 2) AS gross_sales,
    ROUND(COALESCE(m.total_discount, 0), 2) AS total_discount,
    ROUND(COALESCE(m.net_item_value, 0), 2) AS net_item_value,
    ROUND(COALESCE(m.total_benefit, 0), 2) AS total_benefit,
    ROUND(
        m.gross_sales / NULLIF(m.units_sold, 0), 2
    ) AS average_selling_price,
    ROUND(m.avg_profit_ratio, 4) AS avg_profit_ratio
FROM analytics.dim_product p
LEFT JOIN product_metrics m
    ON p.product_key = m.product_key;
