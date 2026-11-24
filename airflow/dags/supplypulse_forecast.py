
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_DIR = "/opt/airflow/project"

with DAG(
    dag_id="supplypulse_monthly_forecast",
    description="Monthly Prophet demand forecasting and benchmark evaluation",
    start_date=datetime(2026, 11, 1),
    schedule="0 2 1 * *",
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    tags=["supplypulse", "forecasting", "prophet"],
) as dag:

    generate_forecasts = BashOperator(
        task_id="generate_demand_forecasts",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "python -m src.forecasting.train_demand_forecast"
        ),
    )

    generate_forecasts
