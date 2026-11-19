
INSERT INTO core.supplier_performance (
    supplier_id,
    purchase_order_code,
    order_date,
    expected_delivery_date,
    actual_delivery_date,
    ordered_quantity,
    received_quantity,
    accepted_quantity,
    is_simulated
)
SELECT
    s.supplier_id,
    'PO-' || LPAD(s.supplier_id::TEXT, 3, '0')
        || '-' || LPAD(g.n::TEXT, 3, '0'),
    DATE '2026-01-01' + (g.n * 10),
    DATE '2026-01-01' + (g.n * 10)
        + s.average_lead_time_days,
    DATE '2026-01-01' + (g.n * 10)
        + s.average_lead_time_days
        + CASE
            WHEN (s.supplier_id + g.n) % 4 = 0 THEN 2
            ELSE 0
          END,
    100 + (s.supplier_id * 7 + g.n * 13) % 101,
    100 + (s.supplier_id * 7 + g.n * 13) % 101
        - (g.n % 3),
    100 + (s.supplier_id * 7 + g.n * 13) % 101
        - (g.n % 3)
        - (g.n % 5),
    TRUE
FROM core.suppliers s
CROSS JOIN GENERATE_SERIES(1, 10) AS g(n)
ON CONFLICT (purchase_order_code) DO NOTHING;
