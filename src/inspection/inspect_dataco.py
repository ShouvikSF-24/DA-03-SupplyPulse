
"""
SupplyPulse - DataCo Dataset Inspection
Purpose: Profile the raw DataCo supply chain dataset.
"""

from pathlib import Path
import pandas as pd

# 1. Define project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "DataCoSupplyChainDataset.csv"
)

REPORT_DIR = PROJECT_ROOT / "reports"


def inspect_dataset():

    print("=" * 70)
    print("SUPPLYPULSE - DATACO DATASET INSPECTION")
    print("=" * 70)

    # 2. Verify dataset exists
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    print(f"\nDataset: {DATA_FILE.name}")
    print(f"File size: {DATA_FILE.stat().st_size / (1024**2):.2f} MB")

    # 3. Load dataset
    print("\nLoading dataset...")

    df = pd.read_csv(
        DATA_FILE,
        encoding="latin-1",
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

    print("\n--- FIRST 5 RECORDS ---")
    print(df.head().to_string())

    # 5. Data quality checks
    print("\n--- MISSING VALUES ---")

    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if missing.empty:
        print("No missing values found.")
    else:
        print(missing.to_string())

    print("\n--- DUPLICATE RECORDS ---")
    duplicate_count = df.duplicated().sum()
    print(f"Duplicate rows: {duplicate_count:,}")

    # 6. Numerical statistics
    print("\n--- NUMERICAL SUMMARY ---")
    print(df.describe().to_string())

    # 7. Save inspection reports
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    missing.to_csv(
        REPORT_DIR / "dataco_missing_values.csv",
        header=["missing_count"]
    )

    df.head(20).to_csv(
        REPORT_DIR / "dataco_sample.csv",
        index=False
    )

    summary = [
        "SUPPLYPULSE - DATACO INSPECTION REPORT",
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
    ]

    (REPORT_DIR / "dataco_inspection.txt").write_text(
        "\n".join(summary),
        encoding="utf-8"
    )

    print("\n--- REPORTS SAVED ---")
    print(f"Location: {REPORT_DIR}")

    print("\nDataCo inspection completed successfully!")


if __name__ == "__main__":
    inspect_dataset()
