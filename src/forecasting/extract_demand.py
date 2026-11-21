
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.config import PROJECT_ROOT
from src.database import engine


OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "demand_monthly.csv"


DEMAND_QUERY = text("""
    SELECT
        oi.product_id,
        p.product_name,
        DATE_TRUNC('month', o.order_date)::date AS month_start,
        SUM(oi.quantity)::integer AS units_sold,
        COUNT(DISTINCT o.order_id)::integer AS order_count
    FROM core.order_items oi
    JOIN core.orders o
        ON oi.order_id = o.order_id
    JOIN core.products p
        ON oi.product_id = p.product_id
    GROUP BY
        oi.product_id,
        p.product_name,
        DATE_TRUNC('month', o.order_date)::date
    ORDER BY
        oi.product_id,
        month_start
""")


def extract_monthly_demand(connection):
    """Extract actual monthly product demand from PostgreSQL."""

    demand = pd.read_sql_query(
        DEMAND_QUERY,
        connection,
    )

    if demand.empty:
        raise ValueError("No demand records were returned.")

    required_columns = {
        "product_id",
        "product_name",
        "month_start",
        "units_sold",
        "order_count",
    }

    missing_columns = required_columns - set(demand.columns)

    if missing_columns:
        raise ValueError(
            f"Missing expected columns: {sorted(missing_columns)}"
        )

    if demand[list(required_columns)].isnull().any().any():
        raise ValueError("Demand data contains missing values.")

    if (demand["units_sold"] < 0).any():
        raise ValueError("Demand data contains negative quantities.")

    if demand.duplicated(
        subset=["product_id", "month_start"]
    ).any():
        raise ValueError("Duplicate product-month records detected.")

    demand["month_start"] = pd.to_datetime(
        demand["month_start"]
    )

    return demand


def main():
    print("=" * 60)
    print("SUPPLYPULSE - MONTHLY DEMAND EXTRACTION")
    print("=" * 60)

    try:
        with engine.connect() as connection:
            demand = extract_monthly_demand(connection)

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        demand.to_csv(
            OUTPUT_FILE,
            index=False,
        )

        print("\nExtraction successful!")
        print(f"Total product-month records: {len(demand):,}")
        print(
            "Distinct products: "
            f"{demand['product_id'].nunique():,}"
        )
        print(
            "First month: "
            f"{demand['month_start'].min().date()}"
        )
        print(
            "Latest month: "
            f"{demand['month_start'].max().date()}"
        )
        print(
            "Total units sold: "
            f"{demand['units_sold'].sum():,}"
        )
        print(f"\nOutput file: {OUTPUT_FILE}")

        print("\nFirst five records:")
        print(demand.head().to_string(index=False))

    except Exception as error:
        print("\nDemand extraction failed!")
        print(f"Error: {error}")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
