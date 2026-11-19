
"""
SupplyPulse - Olist Customer Dataset Inspection
Purpose: Profile customer data without exporting raw customer records.
"""

from pathlib import Path
import pandas as pd

# 1. Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "olist_customers_dataset.csv"
)

REPORT_DIR = PROJECT_ROOT / "reports"


def inspect_dataset():

    print("=" * 70)
    print("SUPPLYPULSE - OLIST CUSTOMER DATASET INSPECTION")
    print("=" * 70)

    # 2. Verify dataset
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    print(f"\nDataset: {DATA_FILE.name}")
    print(
        f"File size: "
        f"{DATA_FILE.stat().st_size / (1024**2):.2f} MB"
    )

    # 3. Load dataset
    print("\nLoading dataset...")

    df = pd.read_csv(
        DATA_FILE,
        encoding="utf-8",
        low_memory=False
    )

    # 4. Basic information
    print("\n--- DATASET DIMENSIONS ---")
    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")

    print("\n--- COLUMN NAMES ---")
    for column in df.columns:
        print(column)

    print("\n--- DATA TYPES ---")
    print(df.dtypes.to_string())

    # 5. Data quality
    print("\n--- MISSING VALUES ---")

    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(
        ascending=False
    )

    if missing.empty:
        print("No missing values found.")
    else:
        print(missing.to_string())

    print("\n--- DUPLICATE RECORDS ---")
    duplicate_count = df.duplicated().sum()
    print(f"Duplicate rows: {duplicate_count:,}")

    # 6. Unique value analysis
    print("\n--- UNIQUE VALUES ---")

    unique_counts = df.nunique(dropna=True)

    print(unique_counts.to_string())

    # 7. Customer identifier checks
    print("\n--- CUSTOMER IDENTIFIER CHECKS ---")

    for column in ["customer_id", "customer_unique_id"]:

        if column in df.columns:

            print(
                f"{column}: "
                f"{df[column].nunique(dropna=True):,} "
                f"unique values"
            )

            print(
                f"{column} missing: "
                f"{df[column].isnull().sum():,}"
            )

    # 8. Save privacy-safe reports
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    missing.to_csv(
        REPORT_DIR / "olist_missing_values.csv",
        header=["missing_count"]
    )

    unique_counts.to_csv(
        REPORT_DIR / "olist_unique_values.csv",
        header=["unique_count"]
    )

    summary = [
        "SUPPLYPULSE - OLIST INSPECTION REPORT",
        f"Total rows: {df.shape[0]:,}",
        f"Total columns: {df.shape[1]}",
        f"Duplicate rows: {duplicate_count:,}",
        f"Columns with missing values: {len(missing)}",
        "",
        "DATA TYPES:",
        df.dtypes.to_string(),
        "",
        "MISSING VALUES:",
        missing.to_string(),
        "",
        "UNIQUE VALUES:",
        unique_counts.to_string(),
    ]

    (
        REPORT_DIR / "olist_inspection.txt"
    ).write_text(
        "\n".join(summary),
        encoding="utf-8"
    )

    print("\n--- REPORTS SAVED ---")
    print(f"Location: {REPORT_DIR}")

    print("\nOlist inspection completed successfully!")


if __name__ == "__main__":
    inspect_dataset()
