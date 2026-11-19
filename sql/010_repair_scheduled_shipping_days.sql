
UPDATE core.orders o SET days_for_shipment_scheduled = src.scheduled_days FROM (SELECT (source_data->>'Order Id')::BIGINT AS order_id, MIN(NULLIF(BTRIM(source_data->>'Days for shipment (scheduled)'), '')::INTEGER) AS scheduled_days FROM staging.dataco_raw GROUP BY (source_data->>'Order Id')::BIGINT HAVING COUNT(DISTINCT NULLIF(BTRIM(source_data->>'Days for shipment (scheduled)'), '')::INTEGER) = 1) src WHERE o.order_id = src.order_id AND o.days_for_shipment_scheduled IS DISTINCT FROM src.scheduled_days;

