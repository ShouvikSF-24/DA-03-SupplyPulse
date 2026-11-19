
CREATE OR REPLACE VIEW analytics.vw_supplier_performance AS
SELECT
    s.supplier_id,
    s.supplier_code,
    s.supplier_name,
    s.supplier_region,
    s.average_lead_time_days AS expected_lead_time_days,

    COUNT(sp.performance_id) AS total_purchase_orders,

    SUM(sp.ordered_quantity) AS total_ordered_quantity,
    SUM(sp.received_quantity) AS total_received_quantity,
    SUM(sp.accepted_quantity) AS total_accepted_quantity,

    COUNT(*) FILTER (
        WHERE sp.actual_delivery_date <= sp.expected_delivery_date
    ) AS on_time_orders,

    COUNT(*) FILTER (
        WHERE sp.actual_delivery_date > sp.expected_delivery_date
    ) AS late_orders,

    ROUND(
        100.0 * SUM(sp.received_quantity)
        / NULLIF(SUM(sp.ordered_quantity), 0), 2
    ) AS fulfilment_rate,

    ROUND(
        100.0 * SUM(sp.accepted_quantity)
        / NULLIF(SUM(sp.received_quantity), 0), 2
    ) AS quality_acceptance_rate,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE sp.actual_delivery_date <= sp.expected_delivery_date
        )
        / NULLIF(COUNT(*), 0), 2
    ) AS on_time_delivery_rate,

    ROUND(
        AVG(
            sp.actual_delivery_date - sp.expected_delivery_date
        ), 2
    ) AS average_delivery_delay_days,

    ROUND(
        AVG(sp.actual_delivery_date - sp.order_date), 2
    ) AS average_actual_lead_time_days,

    BOOL_AND(sp.is_simulated) AS is_simulated

FROM core.suppliers s
JOIN core.supplier_performance sp
    ON s.supplier_id = sp.supplier_id

GROUP BY
    s.supplier_id,
    s.supplier_code,
    s.supplier_name,
    s.supplier_region,
    s.average_lead_time_days;
