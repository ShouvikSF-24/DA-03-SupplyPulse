"""Statistical anomaly detection for demand and supplier delivery delays."""

from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEMAND_FILE = PROJECT_ROOT / "data" / "processed" / "demand_monthly.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "anomaly_detection_results.csv"

Z_SCORE_THRESHOLD = 3.0

SUPPLIER_QUERY = """
SELECT
    sp.supplier_id,
    s.supplier_name,
    sp.purchase_order_code,
    sp.expected_delivery_date,
    sp.actual_delivery_date,
    sp.is_simulated
FROM core.supplier_performance sp
JOIN core.suppliers s
    ON sp.supplier_id = s.supplier_id
ORDER BY sp.supplier_id, sp.order_date;
"""


def detect_demand_anomalies(data, threshold=Z_SCORE_THRESHOLD):
    required = {
        "product_id", "product_name", "month_start", "units_sold"
    }
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing demand columns: {sorted(missing)}")
    if threshold <= 0:
        raise ValueError("Threshold must be positive.")

    df = data.copy()
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="raise")
    df["month_start"] = pd.to_datetime(df["month_start"], errors="raise")

    if (df["units_sold"] < 0).any():
        raise ValueError("Demand cannot contain negative units.")

    grouped = df.groupby("product_id")["units_sold"]
    df["baseline_mean"] = grouped.transform("mean")
    df["baseline_std"] = grouped.transform(
        lambda values: values.std(ddof=0)
    )

    df["z_score"] = np.where(
        df["baseline_std"] > 0,
        (df["units_sold"] - df["baseline_mean"])
        / df["baseline_std"].replace(0, np.nan),
        0.0,
    )

    df["is_anomaly"] = df["z_score"] > threshold

    return pd.DataFrame({
        "anomaly_type": "DEMAND_SPIKE",
        "entity_id": df["product_id"],
        "entity_name": df["product_name"],
        "event_date": df["month_start"].dt.strftime("%Y-%m-%d"),
        "observed_value": df["units_sold"],
        "baseline_mean": df["baseline_mean"],
        "baseline_std": df["baseline_std"],
        "z_score": df["z_score"],
        "is_anomaly": df["is_anomaly"],
        "severity": np.where(df["is_anomaly"], "HIGH", "NORMAL"),
        "detection_reason": np.where(
            df["is_anomaly"],
            "Demand exceeded historical mean by more than 3 standard deviations.",
            "No demand spike above the configured Z-score threshold.",
        ),
        "is_simulated": False,
    })


def load_supplier_delivery_data():
    from src.database import engine

    with engine.connect() as connection:
        return pd.read_sql(text(SUPPLIER_QUERY), connection)


def detect_supplier_delay_anomalies(data, threshold=Z_SCORE_THRESHOLD):
    required = {
        "supplier_id",
        "supplier_name",
        "purchase_order_code",
        "expected_delivery_date",
        "actual_delivery_date",
        "is_simulated",
    }
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing supplier columns: {sorted(missing)}")
    if threshold <= 0:
        raise ValueError("Threshold must be positive.")

    df = data.copy()
    df["expected_delivery_date"] = pd.to_datetime(
        df["expected_delivery_date"], errors="raise"
    )
    df["actual_delivery_date"] = pd.to_datetime(
        df["actual_delivery_date"], errors="raise"
    )
    df["delay_days"] = (
        df["actual_delivery_date"] - df["expected_delivery_date"]
    ).dt.days

    grouped = df.groupby("supplier_id")["delay_days"]
    df["baseline_mean"] = grouped.transform("mean")
    df["baseline_std"] = grouped.transform(
        lambda values: values.std(ddof=0)
    )

    df["z_score"] = np.where(
        df["baseline_std"] > 0,
        (df["delay_days"] - df["baseline_mean"])
        / df["baseline_std"].replace(0, np.nan),
        0.0,
    )

    df["is_anomaly"] = (
        (df["delay_days"] > 0) & (df["z_score"] > threshold)
    )

    return pd.DataFrame({
        "anomaly_type": "SUPPLIER_DELIVERY_DELAY",
        "entity_id": df["supplier_id"],
        "entity_name": df["supplier_name"],
        "event_date": df["actual_delivery_date"].dt.strftime("%Y-%m-%d"),
        "observed_value": df["delay_days"],
        "baseline_mean": df["baseline_mean"],
        "baseline_std": df["baseline_std"],
        "z_score": df["z_score"],
        "is_anomaly": df["is_anomaly"],
        "severity": np.where(df["is_anomaly"], "HIGH", "NORMAL"),
        "detection_reason": np.where(
            df["is_anomaly"],
            "Delivery delay exceeded supplier-specific mean by more than 3 standard deviations.",
            "No unusual supplier delay above the configured Z-score threshold.",
        ),
        "is_simulated": df["is_simulated"].astype(bool),
    })


def run_anomaly_detection():
    demand = pd.read_csv(DEMAND_FILE)
    suppliers = load_supplier_delivery_data()

    demand_results = detect_demand_anomalies(demand)
    supplier_results = detect_supplier_delay_anomalies(suppliers)

    results = pd.concat(
        [demand_results, supplier_results],
        ignore_index=True,
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT_FILE, index=False)

    print("\n========== SUPPLYPULSE ANOMALY DETECTION ==========")
    print("Demand records analysed:", len(demand_results))
    print(
        "Demand spikes detected:",
        int(demand_results["is_anomaly"].sum()),
    )
    print("Supplier orders analysed:", len(supplier_results))
    print(
        "Supplier delay anomalies detected:",
        int(supplier_results["is_anomaly"].sum()),
    )
    print("Total records:", len(results))
    print("Output file:", OUTPUT_FILE)

    return results


if __name__ == "__main__":
    run_anomaly_detection()
