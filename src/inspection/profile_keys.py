
"""
SupplyPulse - Primary Key and Relationship Profiling

Checks candidate identifiers, uniqueness, missing keys,
order granularity and date ranges.

Does not print or export personal customer information.
"""

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATACO_FILE = PROJECT_ROOT / "data/raw/DataCoSupplyChainDataset.csv"
OLIST_FILE = PROJECT_ROOT / "data/raw/olist_customers_dataset.csv"


def profile_key(df, column, label):

    print(f"\n{label}: {column}")

    if column not in df.columns:
        print("Column not found.")
        return

    total = len(df)
    unique = df[column].nunique(dropna=True)
    missing = df[column].isna().sum()

    print(f"Total records: {total:,}")
    print(f"Unique values: {unique:,}")
    print(f"Missing values: {missing:,}")
    print(f"Duplicate non-null values: {total - missing - unique:,}")


def main():

    print("=" * 65)
    print("SUPPLYPULSE - KEY PROFILING")
    print("=" * 65)

    # Load DataCo
    print("\nLoading DataCo...")
    dataco = pd.read_csv(
        DATACO_FILE,
        encoding="latin-1",
        low_memory=False
    )

    # Candidate DataCo identifiers
    print("\n--- DATACO IDENTIFIERS ---")

    dataco_keys = [
        "Order Id",
        "Order Item Id",
        "Customer Id",
        "Order Customer Id",
        "Product Card Id",
        "Category Id",
    ]

    for column in dataco_keys:
        profile_key(dataco, column, "DataCo")

    # Check date ranges
    print("\n--- DATACO DATE RANGES ---")

    for column in [
        "order date (DateOrders)",
        "shipping date (DateOrders)",
    ]:

        dates = pd.to_datetime(
            dataco[column],
            errors="coerce"
        )

        print(f"\n{column}")
        print(f"Earliest: {dates.min()}")
        print(f"Latest: {dates.max()}")
        print(f"Unparseable dates: {dates.isna().sum():,}")

    # Check order item relationship
    print("\n--- ORDER ITEM RELATIONSHIP ---")

    order_counts = dataco.groupby("Order Id")[
        "Order Item Id"
    ].nunique()

    print(f"Unique orders: {order_counts.size:,}")
    print(
        "Orders containing multiple items:",
        f"{(order_counts > 1).sum():,}"
    )
    print(
        "Maximum items per order:",
        order_counts.max()
    )

    # Load Olist
    print("\nLoading Olist...")
    olist = pd.read_csv(
        OLIST_FILE,
        encoding="utf-8",
        low_memory=False
    )

    # Candidate Olist identifiers
    print("\n--- OLIST IDENTIFIERS ---")

    for column in [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
    ]:
        profile_key(olist, column, "Olist")

    print("\n--- OLIST CUSTOMER RELATIONSHIP ---")

    customers_per_unique_id = olist.groupby(
        "customer_unique_id"
    )["customer_id"].nunique()

    print(
        "Unique underlying customers:",
        customers_per_unique_id.size
    )

    print(
        "Underlying customers with multiple records:",
        (customers_per_unique_id > 1).sum()
    )

    print("\nKEY PROFILING COMPLETED.")


if __name__ == "__main__":
    main()
