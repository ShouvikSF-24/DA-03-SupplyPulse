
UPDATE analytics.fact_order_items f SET days_for_shipment_scheduled = o.days_for_shipment_scheduled FROM core.orders o WHERE f.order_id = o.order_id AND f.days_for_shipment_scheduled IS DISTINCT FROM o.days_for_shipment_scheduled;
