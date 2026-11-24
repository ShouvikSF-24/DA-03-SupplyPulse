
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "inventory_forecast_analysis_v2.csv"
)
OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "inventory_days_of_inventory.csv"
)


def main():
    print("=" * 65)
    print("SUPPLYPULSE - DAYS OF INVENTORY ANALYSIS")
    print("=" * 65)

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "product_id",
        "product_name_forecast",
        "available_stock",
        "forecast_units",
    ]

    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df[required_columns].isnull().any().any():
        raise ValueError("Missing values in required columns.")

    if (df["available_stock"] < 0).any():
        raise ValueError("Available stock cannot be negative.")

    if (df["forecast_units"] < 0).any():
        raise ValueError("Forecast demand cannot be negative.")

    df["average_daily_demand"] = (
        df["forecast_units"] / 30.0
    )

    df["days_of_inventory"] = (
        df["available_stock"]
        / df["average_daily_demand"].replace(0, pd.NA)
    )

    df["days_of_inventory"] = (
        df["days_of_inventory"].round(2)
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(OUTPUT_FILE, index=False)

    valid_doi = df["days_of_inventory"].dropna()

    print("\n========== ANALYSIS RESULTS ==========")
    print("Products analysed:", len(df))
    print("Products with zero forecast demand:",
          int((df["forecast_units"] == 0).sum()))
    print("Products with zero available stock:",
          int((df["available_stock"] == 0).sum()))

    if not valid_doi.empty:
        print("Average days of inventory:",
              round(valid_doi.mean(), 2))
        print("Median days of inventory:",
              round(valid_doi.median(), 2))
    else:
        print("No valid days of inventory values.")

    print("\nFirst five records:")
    print(
        df[
            [
                "product_id",
                "product_name_forecast",
                "available_stock",
                "forecast_units",
                "average_daily_demand",
                "days_of_inventory",
            ]
        ].head().to_string(index=False)
    )

    print("\nOutput file:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
