
import pandas as pd
import pytest

from src.simulation import supplier_delay


@pytest.fixture
def sample_simulation_data():
    return pd.DataFrame({
        "product_id": [1],
        "forecast_month": ["2026-01-01"],
        "forecast_units": [310],
        "available_stock": [0],
        "average_lead_time_days": [2]
    })


def test_zero_delay_produces_zero_incremental_shortfall(
    monkeypatch, sample_simulation_data
):
    monkeypatch.setattr(
        supplier_delay,
        "load_simulation_inputs",
        lambda: sample_simulation_data.copy()
    )

    result = supplier_delay.simulate_supplier_delay(0)

    assert result["incremental_shortfall_due_to_delay"].sum() == 0
    assert (
        result["baseline_projected_shortfall"].equals(
            result["delayed_projected_shortfall"]
        )
    )


def test_positive_delay_increases_demand_exposure(
    monkeypatch, sample_simulation_data
):
    monkeypatch.setattr(
        supplier_delay,
        "load_simulation_inputs",
        lambda: sample_simulation_data.copy()
    )

    result = supplier_delay.simulate_supplier_delay(3)

    assert (
        result["delayed_demand_exposure"].iloc[0]
        > result["baseline_demand_exposure"].iloc[0]
    )

    assert result["incremental_shortfall_due_to_delay"].iloc[0] > 0


def test_negative_delay_is_rejected():
    with pytest.raises(ValueError):
        supplier_delay.simulate_supplier_delay(-1)


def test_non_integer_delay_is_rejected():
    with pytest.raises(ValueError):
        supplier_delay.simulate_supplier_delay(1.5)


def test_delay_scenario_comparison_returns_expected_scenarios(
    monkeypatch, sample_simulation_data
):
    monkeypatch.setattr(
        supplier_delay,
        "load_simulation_inputs",
        lambda: sample_simulation_data.copy()
    )

    result = supplier_delay.compare_delay_scenarios()

    assert result["additional_delay_days"].tolist() == [0, 3, 5, 7]
    assert (result["products_analysed"] == 1).all()
    assert result["incremental_shortfall"].iloc[0] == 0


def test_shortfall_increases_with_supplier_delay(
    monkeypatch, sample_simulation_data
):
    monkeypatch.setattr(
        supplier_delay,
        "load_simulation_inputs",
        lambda: sample_simulation_data.copy()
    )

    result = supplier_delay.compare_delay_scenarios()

    shortfalls = result["projected_shortfall"].tolist()

    assert shortfalls == sorted(shortfalls)
    assert len(set(shortfalls)) == 4
