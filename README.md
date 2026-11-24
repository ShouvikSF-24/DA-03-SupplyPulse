# SupplyPulse
### DA-03 – Retail and Supply Chain Control Tower

SupplyPulse is a data analytics project designed to monitor retail sales, inventory health, supplier performance, demand forecasts and operational anomalies through a centralized control tower.

## Key Features
- Python-based data extraction and transformation
- PostgreSQL staging, core and analytics layers
- SQL analytics views for sales, inventory, customers and suppliers
- Business KPI reporting and monthly sales analysis
- Prophet-based demand forecasting and benchmark evaluation
- Inventory replenishment and stock-risk analysis
- Supplier delivery and performance analysis
- Demand and supplier anomaly detection
- Slack and email alert integration (requires valid credentials)
- Streamlit dashboard
- Apache Superset dashboard
- Apache Airflow scheduling

## Technology Stack
| Area | Technology |
|---|---|
| Programming | Python |
| Data processing | Pandas, NumPy |
| Database | PostgreSQL |
| Forecasting | Prophet |
| Orchestration | Apache Airflow |
| Dashboards | Streamlit, Apache Superset |
| Containerization | Docker, Docker Compose |
| Testing | Pytest |

## Project Structure
- `airflow/` – Airflow DAGs
- `app/` – Dashboard application
- `docs/` – Project documentation
- `sql/` – Database schemas, transformations and analytics views
- `src/` – ETL, forecasting, risk analysis and alert modules
- `tests/` – Automated tests
- `docker-compose.yml` – Container configuration

## Setup
1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a local `.env` using `.env.example` as a template. Configure credentials locally.
5. Start PostgreSQL and Airflow:

```bash
docker compose up -d db airflow
```

6. Run tests:

```bash
python -m pytest -q
```

## Airflow Workflows
- `supplypulse_hourly_monitoring` – Demand extraction, anomaly detection and alert dispatch.
- `supplypulse_monthly_forecast` – Prophet demand forecasting and benchmark evaluation.

Airflow UI: `http://localhost:8080`

## Superset Dashboard
Dashboard: **SupplyPulse – Retail & Supply Chain Control Tower**

Superset UI: `http://localhost:8088`

The dashboard uses PostgreSQL analytics datasets for KPI, monthly sales, inventory risk and supplier performance reporting.

## Forecast Outputs
The forecasting workflow generates:
- `data/processed/demand_forecasts.csv`
- `data/processed/forecast_evaluation.csv`

Generated data and local secrets should remain excluded from version control.

## Testing
Latest verified test run: **44 tests passed**.

```bash
python -m pytest -q
```

## Architecture
See [docs/architecture.md](docs/architecture.md).

## Security
- Never commit `.env` or database credentials.
- Use `.env.example` as a configuration template.
- Keep local datasets, logs and generated artifacts out of Git where configured.

---
**Project:** DA-03 – SupplyPulse  
**Category:** Data Analytics
