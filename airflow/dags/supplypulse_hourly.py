from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/project"

with DAG(
    dag_id="supplypulse_hourly_monitoring",
    description="Hourly demand extraction, anomaly detection and alert dispatch",
    start_date=datetime(2026, 11, 1),
    schedule="0 * * * *",
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    tags=["supplypulse", "monitoring"],
) as dag:

    extract_demand = BashOperator(
        task_id="extract_monthly_demand",
        bash_command=f"cd {PROJECT_DIR} && python -m src.forecasting.extract_demand",
    )

    detect_anomalies = BashOperator(
        task_id="detect_anomalies",
        bash_command=f"cd {PROJECT_DIR} && python -m src.anomaly_detection.detection",
    )

    dispatch_alerts = BashOperator(
        task_id="dispatch_alerts",
        bash_command=f"cd {PROJECT_DIR} && python -m src.alerts.notifications",
    )

    extract_demand >> detect_anomalies >> dispatch_alerts
