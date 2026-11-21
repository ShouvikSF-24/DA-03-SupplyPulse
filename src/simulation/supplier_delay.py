
import pandas as pd
from sqlalchemy import text

from src.database import engine


SUPPLIER_QUERY = """
SELECT
    ps.product_id,
    ps.supplier_id,
    ps.unit_cost,
    s.supplier_code,
    s.supplier_name,
    s.supplier_region,
    s.average_lead_time_days,
    ps.is_simulated AS mapping_is_simulated,
    s.is_simulated AS supplier_is_simulated
FROM core.product_suppliers AS ps
INNER JOIN core.suppliers AS s
    ON ps.supplier_id = s.supplier_id
WHERE ps.is_primary_supplier = TRUE
ORDER BY ps.product_id;
"""


def load_supplier_data():
    """Load primary supplier mappings and lead times from PostgreSQL."""

    with engine.connect() as connection:
        supplier_data = pd.read_sql(
            text(SUPPLIER_QUERY),
            connection
        )

    if supplier_data.empty:
        raise ValueError("No supplier mapping records found.")

    if supplier_data["product_id"].duplicated().any():
        raise ValueError("Duplicate primary supplier mappings found.")

    return supplier_data


def load_inventory_forecast_data():
    """Load and combine inventory snapshots with demand forecasts."""

    inventory = pd.read_csv(
        "data/processed/inventory_snapshot.csv"
    )

    forecasts = pd.read_csv(
        "data/processed/demand_forecasts.csv"
    )

    inventory["product_id"] = inventory["product_id"].astype(int)
    forecasts["product_id"] = forecasts["product_id"].astype(int)

    if inventory["product_id"].duplicated().any():
        raise ValueError("Duplicate products found in inventory data.")

    if forecasts["product_id"].duplicated().any():
        raise ValueError("Duplicate products found in forecast data.")

    combined = forecasts.merge(
        inventory,
        on="product_id",
        how="inner",
        suffixes=("_forecast", "_inventory"),
        validate="one_to_one"
    )

    if combined.empty:
        raise ValueError("No matching inventory and forecast records found.")

    return combined


def load_simulation_inputs():
    """Combine supplier, inventory, and forecast data."""

    inventory_forecast = load_inventory_forecast_data()
    suppliers = load_supplier_data()

    simulation_data = inventory_forecast.merge(
        suppliers,
        on="product_id",
        how="inner",
        validate="one_to_one"
    )

    if simulation_data.empty:
        raise ValueError("No matching simulation input records found.")

    if simulation_data["average_lead_time_days"].isna().any():
        raise ValueError("Missing supplier lead times found.")

    return simulation_data


def simulate_supplier_delay(additional_delay_days: int):
    """Estimate inventory exposure under an additional supplier delay."""

    if not isinstance(additional_delay_days, int) or additional_delay_days < 0:
        raise ValueError("Additional delay must be a non-negative integer.")

    data = load_simulation_inputs().copy()

    data["forecast_month"] = pd.to_datetime(
        data["forecast_month"],
        errors="raise"
    )

    data["days_in_forecast_month"] = (
        data["forecast_month"].dt.days_in_month
    )

    data["daily_forecast_demand"] = (
        data["forecast_units"] / data["days_in_forecast_month"]
    )

    data["baseline_lead_time_days"] = (
        data["average_lead_time_days"]
    )

    data["delayed_lead_time_days"] = (
        data["baseline_lead_time_days"] + additional_delay_days
    )

    data["baseline_demand_exposure"] = (
        data["daily_forecast_demand"]
        * data["baseline_lead_time_days"]
    )

    data["delayed_demand_exposure"] = (
        data["daily_forecast_demand"]
        * data["delayed_lead_time_days"]
    )

    data["baseline_projected_shortfall"] = (
        data["baseline_demand_exposure"]
        - data["available_stock"]
    ).clip(lower=0)

    data["delayed_projected_shortfall"] = (
        data["delayed_demand_exposure"]
        - data["available_stock"]
    ).clip(lower=0)

    data["incremental_shortfall_due_to_delay"] = (
        data["delayed_projected_shortfall"]
        - data["baseline_projected_shortfall"]
    ).clip(lower=0)

    data["additional_delay_days"] = additional_delay_days

    return data


def save_simulation_results(additional_delay_days: int):
    """Save supplier delay scenario results to a new CSV file."""

    results = simulate_supplier_delay(additional_delay_days).copy()

    results["is_scenario_simulation"] = True
    results["scenario_description"] = (
        f"Additional supplier delay of {additional_delay_days} days"
    )

    output_path = (
        f"data/processed/supplier_delay_simulation_"
        f"{additional_delay_days}day.csv"
    )

    results.to_csv(output_path, index=False)

    return output_path


def compare_delay_scenarios(delay_days=(0, 3, 5, 7)):
    """Compare inventory exposure across multiple delay scenarios."""

    if not delay_days:
        raise ValueError("At least one delay scenario is required.")

    summary = []

    for days in delay_days:
        results = simulate_supplier_delay(days)

        summary.append({
            "additional_delay_days": days,
            "products_analysed": len(results),
            "total_demand_exposure": results[
                "delayed_demand_exposure"
            ].sum(),
            "projected_shortfall": results[
                "delayed_projected_shortfall"
            ].sum(),
            "incremental_shortfall": results[
                "incremental_shortfall_due_to_delay"
            ].sum(),
            "products_with_incremental_shortfall": (
                results["incremental_shortfall_due_to_delay"] > 0
            ).sum()
        })

    return pd.DataFrame(summary)


def save_delay_scenario_comparison():
    """Save the multi-scenario comparison report."""

    comparison = compare_delay_scenarios()

    output_path = (
        "data/processed/supplier_delay_scenario_comparison.csv"
    )

    comparison.to_csv(output_path, index=False)

    return output_path
