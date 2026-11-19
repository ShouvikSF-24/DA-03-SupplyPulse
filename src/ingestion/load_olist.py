
import argparse
import csv
from pathlib import Path

from sqlalchemy import text

from src.database import engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "raw" / "olist_customers_dataset.csv"

BATCH_SIZE = 500

EXPECTED_COLUMNS = [
    "customer_id",
    "customer_unique_id",
    "customer_zip_code_prefix",
    "customer_city",
    "customer_state",
]

INSERT_SQL = text("""
    INSERT INTO staging.olist_customers_raw (
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state
    )
    VALUES (
        :customer_id,
        :customer_unique_id,
        :customer_zip_code_prefix,
        :customer_city,
        :customer_state
    )
    ON CONFLICT (customer_id) DO NOTHING
""")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stream Olist customer records into PostgreSQL staging."
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
        help="Clear existing Olist staging rows before loading.",
    )

    return parser.parse_args()


def insert_batch(records):
    if not records:
        return 0

    with engine.begin() as connection:
        result = connection.execute(INSERT_SQL, records)
        return result.rowcount or 0


def load_olist(limit=None, reset=False):
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Olist file not found: {DATA_FILE}")

    if limit is not None and limit <= 0:
        raise ValueError("--limit must be positive.")

    if reset:
        print("Resetting Olist staging table...")

        with engine.begin() as connection:
            connection.execute(
                text("TRUNCATE TABLE staging.olist_customers_raw RESTART IDENTITY")
            )

        print("Staging table cleared.")

    total_processed = 0
    total_inserted = 0
    total_skipped = 0
    batch = []

    print("=" * 60)
    print("SUPPLYPULSE - OLIST CUSTOMER INGESTION")
    print("=" * 60)
    print(f"Source: {DATA_FILE}")
    print(f"Batch size: {BATCH_SIZE}")
    print("Parser: Python built-in CSV")
    print("Encoding: utf-8-sig")

    with open(DATA_FILE, mode="r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError("CSV file has no header.")

        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError(
                f"Unexpected CSV columns. Found: {reader.fieldnames}"
            )

        for row in reader:
            customer_id = (row["customer_id"] or "").strip()
            customer_unique_id = (row["customer_unique_id"] or "").strip()
            zip_prefix = (row["customer_zip_code_prefix"] or "").strip()

            if not customer_id or not customer_unique_id:
                raise ValueError(
                    f"Missing customer identifier near source row "
                    f"{total_processed + 2}."
                )

            record = {
                "customer_id": customer_id,
                "customer_unique_id": customer_unique_id,
                "customer_zip_code_prefix": int(zip_prefix) if zip_prefix else None,
                "customer_city": (row["customer_city"] or "").strip() or None,
                "customer_state": (row["customer_state"] or "").strip() or None,
            }

            batch.append(record)
            total_processed += 1

            if len(batch) >= BATCH_SIZE:
                inserted = insert_batch(batch)
                total_inserted += inserted
                total_skipped += len(batch) - inserted
                batch.clear()

                print(
                    f"Processed: {total_processed:,} | "
                    f"Inserted: {total_inserted:,} | "
                    f"Skipped: {total_skipped:,}"
                )

            if limit is not None and total_processed >= limit:
                break

        if batch:
            inserted = insert_batch(batch)
            total_inserted += inserted
            total_skipped += len(batch) - inserted

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
        load_olist(limit=args.limit, reset=args.reset)
    finally:
        engine.dispose()
