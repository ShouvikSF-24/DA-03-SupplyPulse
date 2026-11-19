
CREATE OR REPLACE VIEW analytics.vw_delivery_performance AS
SELECT
    shipping_mode,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE delivery_status = 'Late delivery'
    ) AS late_orders,
    COUNT(*) FILTER (
        WHERE delivery_status = 'Advance shipping'
    ) AS advance_orders,
    COUNT(*) FILTER (
        WHERE delivery_status = 'Shipping on time'
    ) AS on_time_orders,
    COUNT(*) FILTER (
        WHERE delivery_status = 'Shipping canceled'
    ) AS canceled_orders,
    COUNT(*) FILTER (
        WHERE delivery_status <> 'Shipping canceled'
    ) AS non_canceled_orders,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE delivery_status = 'Late delivery'
        ) / NULLIF(
            COUNT(*) FILTER (
                WHERE delivery_status <> 'Shipping canceled'
            ), 0
        ), 2
    ) AS late_delivery_percentage,
    ROUND(
        AVG(days_for_shipping_real) FILTER (
            WHERE delivery_status <> 'Shipping canceled'
        ), 2
    ) AS avg_actual_shipping_days,
    ROUND(
        AVG(days_for_shipment_scheduled) FILTER (
            WHERE delivery_status <> 'Shipping canceled'
        ), 2
    ) AS avg_scheduled_shipping_days,
    ROUND(
        AVG(
            days_for_shipping_real - days_for_shipment_scheduled
        ) FILTER (
            WHERE delivery_status <> 'Shipping canceled'
        ), 2
    ) AS avg_shipping_delay_days
FROM core.orders
GROUP BY shipping_mode;
