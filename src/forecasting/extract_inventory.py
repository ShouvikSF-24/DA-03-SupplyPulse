
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.database import engine


OUTPUT_FILE = Path("data/processed/inventory_snapshot.csv")

QUERY = """
SELECT
    s.product_id,
    p.product_name,
    s.snapshot_date,
    s.available_stock,
    s.reserved_stock,
    m.opening_stock,
    m.reorder_level,
    m.safety_stock,
    s.warehouse_code,
    s.is_simulated
FROM core.inventory_snapshots s
JOIN core.inventory_master m
    ON s.inventory_id = m.inventory_id
JOIN core.products p
    ON s.product_id = p.product_id
WHERE s.snapshot_date = '2026-11-18'
ORDER BY s.product_id;
"""


def main():
    print("=" * 65)
    print("SUPPLYPULSE - INVENTORY SNAPSHOT EXTRACTION")
    print("=" * 65)

    try:
        with engine.connect() as connection:
            inventory = pd.read_sql(text(QUERY), connection)

        required_columns = [
            "product_id",
            "product_name",
            "snapshot_date",
            "available_stock",
            "reserved_stock",
            "reorder_level",
            "safety_stock",
        ]

        missing_columns = [
            col for col in required_columns
            if col not in inventory.columns
        ]

        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        if inventory.empty:
            raise ValueError("No inventory records were extracted.")

        if inventory["product_id"].duplicated().any():
            raise ValueError("Duplicate product inventory records found.")

        if inventory[required_columns].isnull().any().any():
            raise ValueError("Missing values found in required columns.")

        if (inventory["available_stock"] < 0).any():
            raise ValueError("Negative available stock found.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        inventory.to_csv(OUTPUT_FILE, index=False)

        print("\n========== EXTRACTION RESULTS ==========")
        print("Total inventory records:", len(inventory))
        print("Distinct products:", inventory["product_id"].nunique())
        print("Snapshot date:", inventory["snapshot_date"].iloc[0])
        print("Simulated records:", int(inventory["is_simulated"].sum()))
        print("Total available stock:", inventory["available_stock"].sum())
        print("Total reserved stock:", inventory["reserved_stock"].sum())
        print("Output file:", OUTPUT_FILE.resolve())

        print("\nFirst five records:")
        print(inventory.head().to_string(index=False))

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
