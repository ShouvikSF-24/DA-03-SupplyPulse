
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import PROJECT_ROOT


INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "demand_monthly.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

FORECAST_FILE = OUTPUT_DIR / "demand_forecasts.csv"
EVALUATION_FILE = OUTPUT_DIR / "forecast_evaluation.csv"

MIN_ACTIVE_MONTHS = 24
TEST_MONTHS = 3


def load_demand():
    """Load and validate extracted monthly demand."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Demand file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        parse_dates=["month_start"],
    )

    required = {
        "product_id",
        "product_name",
        "month_start",
        "units_sold",
        "order_count",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    if df.duplicated(
        ["product_id", "month_start"]
    ).any():
        raise ValueError("Duplicate product-month records found.")

    return df


def prepare_product_series(product_data):
    """Create a continuous monthly series within observed history."""

    product_data = product_data.sort_values("month_start")

    product_data = product_data.set_index("month_start")

    monthly = product_data["units_sold"].asfreq(
        "MS",
        fill_value=0,
    )

    return monthly.astype(float)


def calculate_wape(actual, predicted):
    """Calculate weighted absolute percentage error."""

    denominator = np.sum(np.abs(actual))

    if denominator == 0:
        return np.nan

    return (
        np.sum(np.abs(actual - predicted))
        / denominator
    ) * 100


def main():
    print("=" * 65)
    print("SUPPLYPULSE - DEMAND FORECASTING")
    print("=" * 65)

    df = load_demand()

    forecasts = []
    evaluations = []

    eligible_products = 0
    skipped_products = 0

    for product_id, product_data in df.groupby("product_id"):

        active_months = product_data["month_start"].nunique()

        if active_months < MIN_ACTIVE_MONTHS:
            skipped_products += 1
            continue

        series = prepare_product_series(product_data)

        if len(series) <= TEST_MONTHS + 12:
            skipped_products += 1
            continue

        eligible_products += 1

        train = series.iloc[:-TEST_MONTHS]
        actual = series.iloc[-TEST_MONTHS:]

        moving_average_predictions = []
        seasonal_predictions = []

        for position in range(len(train), len(series)):
            previous_three = series.iloc[position - 3:position]

            moving_average_predictions.append(
                previous_three.mean()
            )

            seasonal_position = position - 12

            seasonal_predictions.append(
                series.iloc[seasonal_position]
            )

        actual_values = actual.to_numpy(dtype=float)

        moving_values = np.array(
            moving_average_predictions,
            dtype=float,
        )

        seasonal_values = np.array(
            seasonal_predictions,
            dtype=float,
        )

        moving_wape = calculate_wape(
            actual_values,
            moving_values,
        )

        seasonal_wape = calculate_wape(
            actual_values,
            seasonal_values,
        )

        evaluations.append({
            "product_id": int(product_id),
            "product_name": product_data["product_name"].iloc[0],
            "test_months": TEST_MONTHS,
            "actual_units": float(actual_values.sum()),
            "moving_average_wape": moving_wape,
            "seasonal_naive_wape": seasonal_wape,
        })

    evaluation_df = pd.DataFrame(evaluations)

    if evaluation_df.empty:
        raise ValueError(
            "No products qualified for forecasting evaluation."
        )

    total_actual = evaluation_df["actual_units"].sum()

    moving_predictions = []
    seasonal_predictions = []

    # Reconstruct the held-out predictions for aggregate evaluation.
    for product_id, product_data in df.groupby("product_id"):

        if product_data["month_start"].nunique() < MIN_ACTIVE_MONTHS:
            continue

        series = prepare_product_series(product_data)

        if len(series) <= TEST_MONTHS + 12:
            continue

        for position in range(len(series) - TEST_MONTHS, len(series)):

            moving_predictions.append(
                series.iloc[position - 3:position].mean()
            )

            seasonal_predictions.append(
                series.iloc[position - 12]
            )

    actual_by_product = []

    for product_id, product_data in df.groupby("product_id"):

        if product_data["month_start"].nunique() < MIN_ACTIVE_MONTHS:
            continue

        series = prepare_product_series(product_data)

        if len(series) <= TEST_MONTHS + 12:
            continue

        actual_by_product.extend(
            series.iloc[-TEST_MONTHS:].to_list()
        )

    actual_all = np.array(actual_by_product, dtype=float)

    moving_wape = calculate_wape(
        actual_all,
        np.array(moving_predictions),
    )

    seasonal_wape = calculate_wape(
        actual_all,
        np.array(seasonal_predictions),
    )

    if moving_wape <= seasonal_wape:
        selected_method = "THREE_MONTH_MOVING_AVERAGE"
    else:
        selected_method = "SEASONAL_NAIVE"

    print("\n========== BACKTEST RESULTS ==========")
    print(f"Eligible products: {eligible_products}")
    print(f"Skipped products: {skipped_products}")
    print(f"Holdout months per product: {TEST_MONTHS}")
    print(f"Moving average WAPE: {moving_wape:.2f}%")
    print(f"Seasonal naive WAPE: {seasonal_wape:.2f}%")
    print(f"Selected method: {selected_method}")

    # Generate next-month forecasts using the selected method.
    for product_id, product_data in df.groupby("product_id"):

        if product_data["month_start"].nunique() < MIN_ACTIVE_MONTHS:
            continue

        series = prepare_product_series(product_data)

        if len(series) <= TEST_MONTHS + 12:
            continue

        if selected_method == "THREE_MONTH_MOVING_AVERAGE":
            predicted_demand = series.iloc[-3:].mean()
        else:
            predicted_demand = series.iloc[-12]

        next_month = (
            series.index[-1] + pd.offsets.MonthBegin(1)
        )

        forecasts.append({
            "product_id": int(product_id),
            "product_name": product_data["product_name"].iloc[0],
            "forecast_month": next_month,
            "forecast_units": max(
                0,
                int(round(predicted_demand)),
            ),
            "forecast_method": selected_method,
            "historical_active_months": int(
                product_data["month_start"].nunique()
            ),
        })

    forecast_df = pd.DataFrame(forecasts)

    evaluation_df["selected_method"] = selected_method
    evaluation_df["aggregate_moving_average_wape"] = moving_wape
    evaluation_df["aggregate_seasonal_naive_wape"] = seasonal_wape

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    forecast_df.to_csv(
        FORECAST_FILE,
        index=False,
    )

    evaluation_df.to_csv(
        EVALUATION_FILE,
        index=False,
    )

    print("\n========== FORECAST OUTPUT ==========")
    print(f"Forecast records: {len(forecast_df)}")
    print(f"Forecast file: {FORECAST_FILE}")
    print(f"Evaluation file: {EVALUATION_FILE}")

    print("\nFirst five forecasts:")
    print(
        forecast_df.head().to_string(index=False)
    )


if __name__ == "__main__":
    main()
