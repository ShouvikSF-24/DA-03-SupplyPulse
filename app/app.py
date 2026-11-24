
from pathlib import Path
import sys

import pandas as pd
import streamlit as st
from sqlalchemy import text

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import engine


st.set_page_config(
    page_title="SupplyPulse | Control Tower",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# DATABASE QUERY FUNCTIONS
# --------------------------------------------------

@st.cache_data(ttl=60)
def load_kpi_overview():
    query = """
        SELECT *
        FROM analytics.vw_kpi_overview
    """
    with engine.connect() as connection:
        return pd.read_sql_query(text(query), connection)

@st.cache_data(ttl=60)
def load_control_tower_kpis():
    query = """
        SELECT *
        FROM analytics.vw_control_tower_kpis
    """
    with engine.connect() as connection:
        return pd.read_sql_query(text(query), connection)

@st.cache_data(ttl=60)
def load_inventory_risk():
    query = """
        SELECT
            snapshot_date,
            inventory_status,
            COUNT(*) AS inventory_records,
            COUNT(DISTINCT product_id) AS distinct_products,
            SUM(available_stock) AS total_available_stock,
            SUM(reserved_stock) AS total_reserved_stock
        FROM analytics.vw_inventory_risk
        GROUP BY snapshot_date, inventory_status
        ORDER BY snapshot_date DESC, inventory_status
    """
    with engine.connect() as connection:
        return pd.read_sql_query(text(query), connection)


@st.cache_data(ttl=60)
def load_supplier_performance():
    query = """
        SELECT
            supplier_name,
            supplier_region,
            total_purchase_orders,
            on_time_orders,
            late_orders,
            fulfilment_rate,
            quality_acceptance_rate,
            on_time_delivery_rate,
            average_delivery_delay_days,
            is_simulated
        FROM analytics.vw_supplier_performance
        ORDER BY on_time_delivery_rate ASC
    """
    with engine.connect() as connection:
        return pd.read_sql_query(text(query), connection)


# --------------------------------------------------
# FORECASTING AND SIMULATION DATA LOADERS
# --------------------------------------------------

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


@st.cache_data(ttl=60)
def load_demand_forecasts():
    file_path = PROCESSED_DIR / "demand_forecasts.csv"
    return pd.read_csv(
        file_path,
        parse_dates=["forecast_month"],
    )


@st.cache_data(ttl=60)
def load_forecast_evaluation():
    file_path = PROCESSED_DIR / "forecast_evaluation.csv"
    return pd.read_csv(file_path)


@st.cache_data(ttl=60)
def load_inventory_forecast_analysis():
    file_path = PROCESSED_DIR / "inventory_forecast_analysis_v2.csv"
    return pd.read_csv(
        file_path,
        parse_dates=["forecast_month", "snapshot_date"],
    )


@st.cache_data(ttl=60)
def load_supplier_scenarios():
    file_path = PROCESSED_DIR / "supplier_delay_scenario_comparison.csv"
    return pd.read_csv(file_path)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📦 SupplyPulse")
st.subheader("Retail & Supply Chain Control Tower")

st.caption(
    "Operational visibility | Inventory intelligence | "
    "Supplier performance | Demand forecasting"
)

st.divider()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("SupplyPulse")
    st.caption("Control Tower Navigation")

    
    page = st.radio(
        "Select Dashboard",
        [
            "Executive Overview",
            "Inventory Monitoring",
            "Supplier Performance",
            "Forecasting & Risk Analysis",
        ],
    )


    st.divider()

    if st.button("Refresh Dashboard", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption("Data source: PostgreSQL")
    st.caption("Refresh interval: 60 seconds")


# --------------------------------------------------
# EXECUTIVE OVERVIEW
# --------------------------------------------------

if page == "Executive Overview":

    st.header("Executive Overview")

    try:
        kpi = load_kpi_overview()

        if kpi.empty:
            st.warning("No KPI data available.")
        else:
            data = kpi.iloc[0]

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Total Orders",
                f"{int(data['total_orders']):,}",
            )

            col2.metric(
                "Order Items",
                f"{int(data['total_order_items']):,}",
            )

            col3.metric(
                "Units Sold",
                f"{int(data['total_units_sold']):,}",
            )

            col4.metric(
                "Recorded Sales",
                f"{data['total_recorded_sales']:,.2f}",
            )

            col5, col6, col7, col8 = st.columns(4)

            col5.metric(
                "Net Item Value",
                f"{data['total_net_item_value']:,.2f}",
            )

            col6.metric(
                "Average Order Value",
                f"{data['average_order_value']:,.2f}",
            )

            col7.metric(
                "Total Discounts",
                f"{data['total_discounts']:,.2f}",
            )

            col8.metric(
                "Discount Rate",
                f"{data['discount_rate_pct']:.2f}%",
            )

    except Exception as error:
        st.error(f"Unable to load business KPIs: {error}")

    
    st.divider()

    st.header("Supply Chain & Inventory KPIs")

    try:
        control_kpi = load_control_tower_kpis()

        if control_kpi.empty:
            st.warning("No supply chain KPI data available.")
        else:
            data = control_kpi.iloc[0]

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Stock-out Rate",
                f"{data['stockout_rate_pct']:.2f}%",
                help="Percentage of inventory products with zero available stock.",
            )

            col2.metric(
                "On-time Delivery",
                f"{data['on_time_delivery_pct']:.2f}%",
                help="Percentage of purchase orders delivered on or before the expected date.",
            )

            col3.metric(
                "Average Supplier Lead Time",
                f"{data['average_actual_lead_time_days']:.2f} days",
            )

            col4.metric(
                "Average Days of Inventory",
                f"{data['average_days_of_inventory']:.2f} days",
                help="Estimated using available stock and historical monthly demand.",
            )

            st.caption(
                f"Median Days of Inventory: "
                f"{data['median_days_of_inventory']:.2f} days. "
                "Inventory snapshot and historical demand are from different periods; "
                "these are analytical estimates, not live operational metrics."
            )

    except Exception as error:
        st.error(f"Unable to load supply chain KPIs: {error}")

    st.divider()

    st.header("Inventory Health Summary")

    try:
        inventory = load_inventory_risk()

        if inventory.empty:
            st.info("No inventory records available.")
        else:
            latest_date = inventory["snapshot_date"].max()

            latest_inventory = inventory[
                inventory["snapshot_date"] == latest_date
            ].copy()

            st.caption(f"Latest inventory snapshot: {latest_date}")

            total_records = int(
                latest_inventory["inventory_records"].sum()
            )

            critical = int(
                latest_inventory.loc[
                    latest_inventory["inventory_status"] == "CRITICAL",
                    "inventory_records",
                ].sum()
            )

            low_stock = int(
                latest_inventory.loc[
                    latest_inventory["inventory_status"] == "LOW STOCK",
                    "inventory_records",
                ].sum()
            )

            healthy = int(
                latest_inventory.loc[
                    latest_inventory["inventory_status"] == "HEALTHY",
                    "inventory_records",
                ].sum()
            )

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Inventory Records", f"{total_records:,}")
            col2.metric("Critical", f"{critical:,}")
            col3.metric("Low Stock", f"{low_stock:,}")
            col4.metric("Healthy", f"{healthy:,}")

            chart_data = latest_inventory.set_index(
                "inventory_status"
            )["inventory_records"]

            st.bar_chart(chart_data)

    except Exception as error:
        st.error(f"Unable to load inventory summary: {error}")


# --------------------------------------------------
# INVENTORY MONITORING
# --------------------------------------------------

elif page == "Inventory Monitoring":

    st.header("Inventory Risk Monitoring")

    try:
        inventory = load_inventory_risk()

        if inventory.empty:
            st.warning("No inventory records found.")
        else:
            latest_date = inventory["snapshot_date"].max()

            st.info(f"Latest available snapshot: {latest_date}")

            latest_inventory = inventory[
                inventory["snapshot_date"] == latest_date
            ]

            st.dataframe(
                latest_inventory,
                use_container_width=True,
                hide_index=True,
            )

            st.subheader("Inventory Risk by Status")

            st.bar_chart(
                latest_inventory.set_index("inventory_status")[
                    "inventory_records"
                ]
            )

            st.subheader("Historical Inventory Snapshots")

            st.dataframe(
                inventory,
                use_container_width=True,
                hide_index=True,
            )

    except Exception as error:
        st.error(f"Unable to load inventory data: {error}")


# --------------------------------------------------
# SUPPLIER PERFORMANCE
# --------------------------------------------------

elif page == "Supplier Performance":

    st.header("Supplier Performance Monitoring")

    try:
        suppliers = load_supplier_performance()

        if suppliers.empty:
            st.warning("No supplier performance records found.")
        else:
            simulated_count = int(
                suppliers["is_simulated"].fillna(False).sum()
            )

            st.warning(
                f"Simulation disclosure: "
                f"{simulated_count} of {len(suppliers)} "
                "supplier records are marked as simulated."
            )

            total_orders = int(
                suppliers["total_purchase_orders"].sum()
            )

            on_time = int(suppliers["on_time_orders"].sum())
            late = int(suppliers["late_orders"].sum())

            overall_rate = (
                100 * on_time / total_orders
                if total_orders else 0
            )

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Suppliers", len(suppliers))
            col2.metric("Purchase Orders", f"{total_orders:,}")
            col3.metric("On-time Orders", f"{on_time:,}")
            col4.metric("Late Orders", f"{late:,}")

            st.metric(
                "Weighted On-time Delivery Rate",
                f"{overall_rate:.2f}%",
            )

            st.subheader("Supplier Performance Details")

            st.dataframe(
                suppliers,
                use_container_width=True,
                hide_index=True,
            )

            st.subheader("On-time Delivery Rate by Supplier")

            st.bar_chart(
                suppliers.set_index("supplier_name")[
                    "on_time_delivery_rate"
                ]
            )

    except Exception as error:
        st.error(f"Unable to load supplier data: {error}")


# --------------------------------------------------
# FORECASTING & RISK ANALYSIS
# --------------------------------------------------

elif page == "Forecasting & Risk Analysis":

    st.header("Demand Forecasting & Risk Intelligence")

    st.warning(
        "Data context: Demand forecasts are based on historical "
        "2015–2018 order data. Inventory and supplier scenarios "
        "are simulated. These are not live 2026 demand forecasts."
    )

    try:
        forecasts = load_demand_forecasts()
        evaluation = load_forecast_evaluation()
        inventory_analysis = load_inventory_forecast_analysis()
        scenarios = load_supplier_scenarios()

        if any(
            frame.empty
            for frame in [
                forecasts,
                evaluation,
                inventory_analysis,
                scenarios,
            ]
        ):
            st.warning("One or more forecasting datasets are empty.")

        else:
            # ------------------------------------------
            # DEMAND FORECAST OVERVIEW
            # ------------------------------------------

            st.subheader("Historical Demand Forecasts")

            forecast_start = forecasts["forecast_month"].min()
            forecast_end = forecasts["forecast_month"].max()

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Forecast Products",
                f"{forecasts['product_id'].nunique():,}",
            )

            col2.metric(
                "Total Forecast Units",
                f"{forecasts['forecast_units'].sum():,.0f}",
            )

            col3.metric(
                "Selected Method",
                str(forecasts["forecast_method"].iloc[0]),
            )

            st.caption(
                f"Forecast periods: {forecast_start:%B %Y} "
                f"to {forecast_end:%B %Y}"
            )

            st.bar_chart(
                forecasts.groupby("forecast_month")[
                    "forecast_units"
                ].sum()
            )

            st.subheader("Product-wise Forecast")

            st.dataframe(
                forecasts,
                use_container_width=True,
                hide_index=True,
            )

            st.divider()

            # ------------------------------------------
            # MODEL EVALUATION
            # ------------------------------------------

            st.subheader("Forecast Model Evaluation")

            evaluation_summary = evaluation.iloc[0]

            moving_wape = float(
                evaluation_summary[
                    "aggregate_moving_average_wape"
                ]
            )

            seasonal_wape = float(
                evaluation_summary[
                    "aggregate_seasonal_naive_wape"
                ]
            )

            selected_method = evaluation_summary["selected_method"]

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Moving Average WAPE",
                f"{moving_wape:.2f}%",
            )

            col2.metric(
                "Seasonal Naive WAPE",
                f"{seasonal_wape:.2f}%",
            )

            col3.metric(
                "Selected Method",
                str(selected_method),
            )

            st.caption(
                "Lower WAPE indicates lower weighted forecast error. "
                "Method selection is based on aggregate holdout evaluation."
            )

            st.subheader("Product-level Evaluation")

            st.dataframe(
                evaluation,
                use_container_width=True,
                hide_index=True,
            )

            st.divider()

            # ------------------------------------------
            # INVENTORY REPLENISHMENT ANALYSIS
            # ------------------------------------------

            st.subheader("Inventory Replenishment Analysis")

            snapshot_date = (
                inventory_analysis["snapshot_date"].max()
            )

            st.info(
                f"Inventory snapshot: {snapshot_date:%d %B %Y}. "
                "Inventory records are simulated."
            )

            total_unmet = int(
                inventory_analysis["potential_unmet_demand"].sum()
            )

            total_replenishment = int(
                inventory_analysis[
                    "replenishment_to_maintain_safety_stock"
                ].sum()
            )

            out_of_stock = int(
                (
                    inventory_analysis["projected_inventory_status"]
                    == "OUT_OF_STOCK"
                ).sum()
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Potential Unmet Demand",
                f"{total_unmet:,} units",
            )

            col2.metric(
                "Replenishment for Safety Stock",
                f"{total_replenishment:,} units",
            )

            col3.metric(
                "Projected Out-of-Stock Products",
                f"{out_of_stock:,}",
            )

            st.subheader("Projected Inventory Status")

            status_counts = (
                inventory_analysis[
                    "projected_inventory_status"
                ]
                .value_counts()
            )

            st.bar_chart(status_counts)

            st.subheader("Product Replenishment Details")

            display_columns = [
                "product_id",
                "product_name_forecast",
                "available_stock",
                "forecast_units",
                "potential_unmet_demand",
                "replenishment_to_reorder_level",
                "replenishment_to_maintain_safety_stock",
                "projected_inventory_status",
                "stock_coverage_ratio",
            ]

            st.dataframe(
                inventory_analysis[display_columns],
                use_container_width=True,
                hide_index=True,
            )

            st.divider()

            # ------------------------------------------
            # SUPPLIER DELAY SIMULATION
            # ------------------------------------------

            st.subheader("Supplier Delay Scenario Analysis")

            st.warning(
                "What-if simulation: results estimate inventory "
                "exposure under additional supplier delays. "
                "They are not observed shortages."
            )

            st.bar_chart(
                scenarios.set_index("additional_delay_days")[
                    [
                        "projected_shortfall",
                        "incremental_shortfall",
                    ]
                ]
            )

            st.subheader("Scenario Comparison")

            st.dataframe(
                scenarios,
                use_container_width=True,
                hide_index=True,
            )

            st.success(
                "Forecasting, inventory analysis and supplier "
                "scenario datasets loaded successfully."
            )

    except FileNotFoundError as error:
        st.error(f"Required analytics output not found: {error}")

    except Exception as error:
        st.error(
            f"Unable to load forecasting and risk analytics: {error}"
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "SupplyPulse | Retail & Supply Chain Control Tower | "
    "Powered by Python, PostgreSQL and Streamlit"
)
