
"""
SupplyPulse - DataCo Relationship Validation
Validates candidate identifiers and relationships.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = ROOT / "data" / "raw" / "DataCoSupplyChainDataset.csv"


def main():

    print("=" * 65)
    print("SUPPLYPULSE - RELATIONSHIP VALIDATION")
    print("=" * 65)

    df = pd.read_csv(
        DATA_FILE,
        encoding="latin-1",
        low_memory=False
    )

    # 1. Check matching identifier columns
    print("\n--- IDENTIFIER CONSISTENCY ---")

    comparisons = [
        ("Customer Id", "Order Customer Id"),
        ("Product Card Id", "Order Item Cardprod Id"),
        ("Category Id", "Product Category Id"),
    ]

    for left, right in comparisons:

        mismatches = (df[left] != df[right]).sum()

        print(f"\n{left} vs {right}")
        print(f"Mismatched records: {mismatches:,}")

    # 2. Check order-level consistency
    print("\n--- ORDER-LEVEL CONSISTENCY ---")

    order_columns = [
        "Customer Id",
        "order date (DateOrders)",
        "shipping date (DateOrders)",
        "Order Status",
        "Market",
        "Order City",
        "Order Country",
        "Order Region",
        "Shipping Mode",
    ]

    for column in order_columns:

        counts = df.groupby("Order Id")[column].nunique(
            dropna=False
        )

        inconsistent = (counts > 1).sum()

        print(
            f"{column}: "
            f"{inconsistent:,} orders with inconsistent values"
        )

    # 3. Product mapping consistency
    print("\n--- PRODUCT MAPPING CONSISTENCY ---")

    product_columns = [
        "Product Name",
        "Product Category Id",
        "Product Price",
    ]

    for column in product_columns:

        counts = df.groupby("Product Card Id")[column].nunique(
            dropna=False
        )

        print(
            f"{column}: "
            f"{(counts > 1).sum():,} product IDs with multiple values"
        )

    # 4. Customer relationship summary
    print("\n--- CUSTOMER RELATIONSHIP ---")

    customer_counts = df.groupby("Customer Id")[
        "Order Id"
    ].nunique()

    print(f"Unique customers: {customer_counts.size:,}")
    print(
        "Customers with multiple orders:",
        f"{(customer_counts > 1).sum():,}"
    )

    print("\nRELATIONSHIP VALIDATION COMPLETED.")


if __name__ == "__main__":
    main()
