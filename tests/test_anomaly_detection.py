import pandas as pd
import pytest

from src.anomaly_detection.detection import (
    detect_demand_anomalies,
    detect_supplier_delay_anomalies,
)


def test_demand_spike_is_detected():
    data = pd.DataFrame({
        "product_id": [1] * 11,
        "product_name": ["Product A"] * 11,
        "month_start": pd.date_range("2025-01-01", periods=11, freq="MS"),
        "units_sold": [10, 11, 9, 10, 12, 8, 11, 9, 10, 11, 40],
    })

    result = detect_demand_anomalies(data)

    assert result["is_anomaly"].sum() == 1
    assert result.iloc[-1]["is_anomaly"]
    assert result.iloc[-1]["z_score"] > 3


def test_normal_demand_has_no_anomaly():
    data = pd.DataFrame({
        "product_id": [1] * 5,
        "product_name": ["Product A"] * 5,
        "month_start": pd.date_range("2025-01-01", periods=5, freq="MS"),
        "units_sold": [10, 11, 9, 10, 12],
    })

    result = detect_demand_anomalies(data)

    assert result["is_anomaly"].sum() == 0


def test_zero_variance_demand_has_no_anomaly():
    data = pd.DataFrame({
        "product_id": [1] * 4,
        "product_name": ["Product A"] * 4,
        "month_start": pd.date_range("2025-01-01", periods=4, freq="MS"),
        "units_sold": [10, 10, 10, 10],
    })

    result = detect_demand_anomalies(data)

    assert result["is_anomaly"].sum() == 0
    assert (result["z_score"] == 0).all()


def test_supplier_delay_anomaly_is_detected():
    data = pd.DataFrame({
        "supplier_id": [1] * 11,
        "supplier_name": ["Supplier A"] * 11,
        "purchase_order_code": [f"PO-{i}" for i in range(11)],
        "expected_delivery_date": pd.to_datetime(
            ["2025-01-01"] * 11
        ),
        "actual_delivery_date": pd.to_datetime(
            ["2025-01-01"] * 10 + ["2025-01-20"]
        ),
        "is_simulated": [True] * 11,
    })

    result = detect_supplier_delay_anomalies(data)

    assert result["is_anomaly"].sum() == 1
    assert result.iloc[-1]["is_anomaly"]
    assert result.iloc[-1]["z_score"] > 3


def test_supplier_zero_variance_has_no_anomaly():
    data = pd.DataFrame({
        "supplier_id": [1] * 4,
        "supplier_name": ["Supplier A"] * 4,
        "purchase_order_code": [f"PO-{i}" for i in range(4)],
        "expected_delivery_date": pd.to_datetime(
            ["2025-01-01"] * 4
        ),
        "actual_delivery_date": pd.to_datetime(
            ["2025-01-01", "2025-01-01",
             "2025-01-03", "2025-01-03"]
        ),
        "is_simulated": [True] * 4,
    })

    result = detect_supplier_delay_anomalies(data)

    assert result["is_anomaly"].sum() == 0


def test_invalid_threshold_is_rejected():
    data = pd.DataFrame({
        "product_id": [1],
        "product_name": ["Product A"],
        "month_start": ["2025-01-01"],
        "units_sold": [10],
    })

    with pytest.raises(ValueError):
        detect_demand_anomalies(data, threshold=0)
