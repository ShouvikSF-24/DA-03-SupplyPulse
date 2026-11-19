
INSERT INTO core.product_suppliers (
    product_id,
    supplier_id,
    is_primary_supplier,
    unit_cost,
    is_simulated
)
SELECT
    p.product_id,
    s.supplier_id,
    TRUE,
    ROUND((p.product_price * 0.70)::NUMERIC, 2),
    TRUE
FROM core.products p
JOIN core.suppliers s
    ON s.supplier_code =
       'SUP' || LPAD((1 + (p.product_id % 10))::TEXT, 3, '0')
ON CONFLICT (product_id, supplier_id) DO NOTHING;
