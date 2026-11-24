# SupplyPulse Architecture

## Project Overview
SupplyPulse is a Retail and Supply Chain Control Tower for sales analytics, inventory monitoring, supplier performance, demand forecasting and anomaly alerts.

## System Architecture

`mermaid
flowchart TD
    A[Retail Source Data] --> B[Python ETL Pipeline]
    B --> C[(PostgreSQL Database)]
    C --> D[Analytics Schema and SQL Views]
    C --> E[Demand Extraction]
    E --> F[Prophet Forecasting]
    F --> G[Forecast CSV Outputs]
    C --> H[Inventory Risk Analysis]
    C --> I[Supplier Performance Analysis]
    H --> J[Anomaly Detection]
    I --> J
    J --> K[Slack and Email Alert Module]
    C --> L[Streamlit Dashboard]
    D --> M[Apache Superset Dashboard]
    E --> N[Apache Airflow Scheduling]
    J --> N
    F --> N
`",
",

- Python and Pandas
- PostgreSQL
- SQL analytics views
- Prophet
- Apache Airflow
- Streamlit
- Apache Superset
- Docker and Docker Compose
- Pytest

## Main Components
1. Python ETL pipeline
2. PostgreSQL staging, core and analytics layers
3. SQL sales, inventory and supplier analytics
4. Prophet demand forecasting and benchmark evaluation
5. Inventory risk and supplier delay analysis
6. Anomaly detection and notification modules
7. Airflow scheduling
8. Streamlit and Superset dashboards

## Verification
Latest automated test run: 44 tests passed.
