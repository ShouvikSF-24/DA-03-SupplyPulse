
INSERT INTO core.suppliers (
    supplier_code,
    supplier_name,
    supplier_region,
    contact_email,
    average_lead_time_days,
    is_simulated
)
VALUES
('SUP001', 'Apex Global Supplies', 'North America', 'contact@apex.example.com', 5, TRUE),
('SUP002', 'Pacific Trade Partners', 'Asia Pacific', 'contact@pacific.example.com', 7, TRUE),
('SUP003', 'EuroSource Logistics', 'Europe', 'contact@eurosource.example.com', 6, TRUE),
('SUP004', 'LatAm Distribution Co', 'Latin America', 'contact@latam.example.com', 8, TRUE),
('SUP005', 'Metro Wholesale Group', 'North America', 'contact@metro.example.com', 4, TRUE),
('SUP006', 'Eastern Commerce Ltd', 'Asia Pacific', 'contact@eastern.example.com', 9, TRUE),
('SUP007', 'Continental Supply Hub', 'Europe', 'contact@continental.example.com', 5, TRUE),
('SUP008', 'Global Retail Sources', 'North America', 'contact@globalretail.example.com', 6, TRUE),
('SUP009', 'Pacific Industrial Supply', 'Asia Pacific', 'contact@pacificindustrial.example.com', 10, TRUE),
('SUP010', 'Central Trade Network', 'Latin America', 'contact@centraltrade.example.com', 7, TRUE)
ON CONFLICT (supplier_code) DO NOTHING;
