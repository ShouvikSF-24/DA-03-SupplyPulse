
from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/processed")

FORECAST_FILE = DATA_DIR / "demand_forecasts.csv"
INVENTORY_FILE = DATA_DIR / "inventory_snapshot.csv"

# Preserve the original analysis file.
OUTPUT_FILE = DATA_DIR / "inventory_forecast_analysis_v2.csv"


def classify_inventory(stock, safety_stock, reorder_level):
    if stock <= 0:
        return "OUT_OF_STOCK"
    elif stock <= safety_stock:
        return "BELOW_SAFETY_STOCK"
    elif stock <= reorder_level:
        return "BELOW_REORDER_LEVEL"
    return "HEALTHY"


def main():
    print("=" * 65)
    print("SUPPLYPULSE - INVENTORY REPLENISHMENT ANALYSIS V2")
    print("=" * 65)

    forecasts = pd.read_csv(FORECAST_FILE)
    inventory = pd.read_csv(INVENTORY_FILE)

    if forecasts.empty or inventory.empty:
        raise ValueError("Forecast or inventory input file is empty.")

    if forecasts["product_id"].duplicated().any():
        raise ValueError("Duplicate product IDs in forecast file.")

    if inventory["product_id"].duplicated().any():
        raise ValueError("Duplicate product IDs in inventory file.")

    analysis = forecasts.merge(
        inventory,
        on="product_id",
        how="inner",
        suffixes=("_forecast", "_inventory"),
        validate="one_to_one",
    )

    if len(analysis) != len(forecasts):
        raise ValueError(
            "Some forecast products did not match inventory records."
        )

    required_columns = [
        "available_stock",
        "forecast_units",
        "reorder_level",
        "safety_stock",
    ]

    if analysis[required_columns].isnull().any().any():
        raise ValueError("Missing values found in required columns.")

    if (analysis[required_columns] < 0).any().any():
        raise ValueError("Negative values found in stock or demand fields.")

    # Net stock balance after forecast demand.
    # This may be negative when demand exceeds available stock.
    analysis["net_stock_after_forecast"] = (
        analysis["available_stock"] - analysis["forecast_units"]
    )

    # Physical stock cannot be negative.
    analysis["projected_stock_after_demand"] = (
        analysis["net_stock_after_forecast"].clip(lower=0)
    )

    # 1. Potential demand that cannot be fulfilled.
    analysis["potential_unmet_demand"] = (
        analysis["forecast_units"] - analysis["available_stock"]
    ).clip(lower=0)

    # 2. Replenishment required to restore stock to reorder level.
    analysis["replenishment_to_reorder_level"] = (
        analysis["reorder_level"]
        - analysis["projected_stock_after_demand"]
    ).clip(lower=0)

    # 3. Additional units required to fulfil forecast demand.
    analysis["replenishment_to_cover_forecast"] = (
        analysis["forecast_units"] - analysis["available_stock"]
    ).clip(lower=0)

    # 4. Units required to fulfil forecast demand AND retain safety stock.
    analysis["replenishment_to_maintain_safety_stock"] = (
        analysis["forecast_units"]
        + analysis["safety_stock"]
        - analysis["available_stock"]
    ).clip(lower=0)

    # Projected inventory status after forecast demand.
    analysis["projected_inventory_status"] = analysis.apply(
        lambda row: classify_inventory(
            row["projected_stock_after_demand"],
            row["safety_stock"],
            row["reorder_level"],
        ),
        axis=1,
    )

    # Stock coverage ratio: available stock / forecast demand.
    analysis["stock_coverage_ratio"] = (
        analysis["available_stock"]
        / analysis["forecast_units"].replace(0, pd.NA)
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    analysis.to_csv(OUTPUT_FILE, index=False)

    print("\n========== ANALYSIS RESULTS ==========")
    print("Forecast products:", len(forecasts))
    print("Inventory products:", len(inventory))
    print("Matched products:", len(analysis))

    print(
        "Potential unmet demand:",
        int(analysis["potential_unmet_demand"].sum()),
        "units",
    )

    print(
        "Replenishment to reorder level:",
        int(analysis["replenishment_to_reorder_level"].sum()),
        "units",
    )

    print(
        "Replenishment to cover forecast:",
        int(analysis["replenishment_to_cover_forecast"].sum()),
        "units",
    )

    print(
        "Replenishment to maintain safety stock:",
        int(analysis["replenishment_to_maintain_safety_stock"].sum()),
        "units",
    )

    print("\nProjected inventory status:")
    print(analysis["projected_inventory_status"].value_counts().to_string())

    display_columns = [
        "product_id",
        "product_name_forecast",
        "available_stock",
        "forecast_units",
        "net_stock_after_forecast",
        "potential_unmet_demand",
        "replenishment_to_reorder_level",
        "replenishment_to_cover_forecast",
        "replenishment_to_maintain_safety_stock",
        "projected_inventory_status",
    ]

    print("\nFirst five records:")
    print(analysis[display_columns].head().to_string(index=False))

    print("\nOutput file:", OUTPUT_FILE.resolve())


if __name__ == "__main__":
    main()
