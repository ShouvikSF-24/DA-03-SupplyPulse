
import argparse
import csv
import json
from pathlib import Path

from sqlalchemy import text

from src.database import engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "raw" / "DataCoSupplyChainDataset.csv"

BATCH_SIZE = 500

ALLOWED_COLUMNS = [
    "Type",
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Benefit per order",
    "Sales per customer",
    "Delivery Status",
    "Late_delivery_risk",
    "Category Id",
    "Category Name",
    "Customer Id",
    "Customer Segment",
    "Department Id",
    "Department Name",
    "Market",
    "Order City",
    "Order Country",
    "Order Customer Id",
    "order date (DateOrders)",
    "Order Id",
    "Order Item Cardprod Id",
    "Order Item Discount",
    "Order Item Discount Rate",
    "Order Item Id",
    "Order Item Product Price",
    "Order Item Profit Ratio",
    "Order Item Quantity",
    "Sales",
    "Order Item Total",
    "Order Profit Per Order",
    "Order Region",
    "Order State",
    "Order Status",
    "Product Card Id",
    "Product Category Id",
    "Product Name",
    "Product Price",
    "Product Status",
    "shipping date (DateOrders)",
    "Shipping Mode",
]

INTEGER_COLUMNS = {
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Late_delivery_risk",
    "Category Id",
    "Customer Id",
    "Department Id",
    "Order Customer Id",
    "Order Id",
    "Order Item Cardprod Id",
    "Order Item Id",
    "Order Item Quantity",
    "Product Card Id",
    "Product Category Id",
    "Product Status",
}

FLOAT_COLUMNS = {
    "Benefit per order",
    "Sales per customer",
    "Order Item Discount",
    "Order Item Discount Rate",
    "Order Item Product Price",
    "Order Item Profit Ratio",
    "Sales",
    "Order Item Total",
    "Order Profit Per Order",
    "Product Price",
}


INSERT_SQL = text("""
    INSERT INTO staging.dataco_raw (source_data)
    VALUES (CAST(:source_data AS JSONB))
    ON CONFLICT ((source_data->>'Order Item Id')) DO NOTHING
""")


def parse_value(column, value):
    value = value.strip()

    if value == "":
        return None

    if column in INTEGER_COLUMNS:
        return int(value)

    if column in FLOAT_COLUMNS:
        return float(value)

    return value


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stream DataCo CSV records into PostgreSQL staging."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum source records to process.",
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear existing DataCo staging rows before loading.",
    )

    return parser.parse_args()


def load_dataco(limit=None, reset=False):

    if not DATA_FILE.exists():
        raise FileNotFoundError(f"DataCo file not found: {DATA_FILE}")

    if limit is not None and limit <= 0:
        raise ValueError("--limit must be positive.")

    if reset:
        print("Resetting DataCo staging table...")

        with engine.begin() as connection:
            connection.execute(
                text(
                    "TRUNCATE TABLE staging.dataco_raw "
                    "RESTART IDENTITY"
                )
            )

        print("Staging table cleared.")

    total_processed = 0
    total_inserted = 0
    total_skipped = 0

    batch = []

    print("=" * 60)
    print("SUPPLYPULSE - DATACO STREAMING INGESTION")
    print("=" * 60)
    print(f"Source: {DATA_FILE}")
    print(f"Batch size: {BATCH_SIZE}")
    print("Parser: Python built-in CSV")
    print("Encoding: cp1250")

    def insert_batch(records):
        nonlocal total_inserted, total_skipped

        if not records:
            return

        payload = [
            {"source_data": json.dumps(record, ensure_ascii=False)}
            for record in records
        ]

        with engine.begin() as connection:
            result = connection.execute(INSERT_SQL, payload)
            inserted = result.rowcount or 0

        total_inserted += inserted
        total_skipped += len(records) - inserted

    with open(
        DATA_FILE,
        mode="r",
        encoding="cp1250",
        newline="",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError("CSV file has no header.")

        missing_columns = set(ALLOWED_COLUMNS) - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                f"Missing expected columns: {sorted(missing_columns)}"
            )

        for row in reader:

            record = {
                column: parse_value(column, row[column] or "")
                for column in ALLOWED_COLUMNS
            }

            batch.append(record)
            total_processed += 1

            if len(batch) >= BATCH_SIZE:
                insert_batch(batch)
                batch.clear()

                print(
                    f"Processed: {total_processed:,} | "
                    f"Inserted: {total_inserted:,} | "
                    f"Skipped: {total_skipped:,}"
                )

            if limit is not None and total_processed >= limit:
                break

        # Insert the final incomplete batch.
        if batch:
            insert_batch(batch)

    print("\nINGESTION SUMMARY")
    print("-" * 60)
    print(f"Source rows processed: {total_processed:,}")
    print(f"New rows inserted: {total_inserted:,}")
    print(f"Duplicate rows skipped: {total_skipped:,}")
    print("Completed batches committed individually.")

    return total_inserted


if __name__ == "__main__":
    args = parse_arguments()

    try:
        load_dataco(
            limit=args.limit,
            reset=args.reset,
        )
    finally:
        engine.dispose()

