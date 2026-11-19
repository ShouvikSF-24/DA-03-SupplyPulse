
SELECT
    COUNT(*) AS total_suppliers,
    SUM(total_purchase_orders) AS total_purchase_orders,
    SUM(total_ordered_quantity) AS total_ordered_quantity,
    SUM(total_received_quantity) AS total_received_quantity,
    SUM(total_accepted_quantity) AS total_accepted_quantity,
    SUM(on_time_orders) AS total_on_time_orders,
    SUM(late_orders) AS total_late_orders,
    COUNT(*) FILTER (
        WHERE is_simulated = TRUE
    ) AS simulated_suppliers,
    COUNT(*) FILTER (
        WHERE fulfilment_rate < 0 OR fulfilment_rate > 100
    ) AS invalid_fulfilment_rates,
    COUNT(*) FILTER (
        WHERE quality_acceptance_rate < 0
           OR quality_acceptance_rate > 100
    ) AS invalid_quality_rates,
    COUNT(*) FILTER (
        WHERE on_time_delivery_rate < 0
           OR on_time_delivery_rate > 100
    ) AS invalid_delivery_rates
FROM analytics.vw_supplier_performance;
