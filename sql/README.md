# SupplyPulse – SQL Layer

## 1. Overview

This directory contains the SQL implementation of the SupplyPulse Retail and Supply Chain Control Tower.

The SQL layer is responsible for database creation, source data transformation, operational data management, analytical modelling, data quality validation and query optimisation.

The database runs on PostgreSQL using Docker.

## 2. Database Architecture

The database is organised into three schemas:

- **staging:** Stores raw source datasets.
- **core:** Contains transformed operational data, fact tables and dimension tables.
- **analytics:** Contains analytical views and business intelligence queries.

## 3. SQL Script Execution Order

Scripts are organised sequentially from 001 to 034.

### 001–006: Database Foundation

Establishes the database structure and prepares source datasets.

- Schema creation
- Staging table creation
- DataCo source transformation
- Olist source transformation
- Analytics schema creation
- Initial data quality checks

### 007–014: Analytics and Data Preparation

Creates the initial analytical layer and prepares data for reporting.

- Business KPI views
- Monthly sales analysis
- Geography performance analysis
- Scheduled shipping days repair
- Fact table scheduled shipping data repair
- Delivery performance view
- Customer analytics view
- Product performance view

### 015–020: Inventory Management

Implements inventory management and stock risk analysis.

- Inventory master creation
- Inventory snapshot creation
- Inventory snapshot loading
- Inventory risk analytical view
- Inventory risk simulation
- Inventory layer validation

### 021–028: Supplier Management

Implements supplier master data and supplier performance analytics.

- Supplier master creation
- Supplier data loading
- Product-supplier mapping creation
- Product-supplier mapping loading
- Supplier performance table creation
- Supplier performance data loading
- Supplier performance analytical view
- Supplier performance validation

### 029–034: Database Auditing and Optimisation

Performs final database verification and optimisation.

- Database reconciliation
- Analytical views verification
- Database constraint audit
- Database index audit
- Missing foreign key index identification
- Missing foreign key index creation

## 4. Analytical Views

The following eight analytical views are implemented:

1. vw_customer_analytics
2. vw_delivery_performance
3. vw_geography_performance
4. vw_inventory_risk
5. vw_kpi_overview
6. vw_monthly_sales
7. vw_product_performance
8. vw_supplier_performance

These views support customer, sales, geography, delivery, product, inventory and supplier performance analysis.

## 5. Data Quality and Integrity

Database validation includes:

- Source and transformed table reconciliation
- Primary key and foreign key verification
- Unique constraint auditing
- Referential integrity checks
- Foreign key index verification
- Inventory validation
- Supplier performance validation
- Analytical view verification

## 6. Important Notes

- Original source datasets are preserved in the staging layer.
- Inventory and supplier operational records include simulated data.
- Analytical views are implemented using PostgreSQL.
- Indexes support important joins and filtering operations.
- Validation and audit scripts are maintained separately from transformation scripts.
- Existing source and operational records must be preserved during subsequent development.

## 7. Current Development Status

| Component | Status |
|---|---|
| Database schemas | Completed |
| Staging and source transformations | Completed |
| Core database tables | Completed |
| Fact and dimension tables | Completed |
| Analytical views | Created |
| Inventory management | Created |
| Supplier management | Created |
| Database reconciliation | Completed |
| Constraint audit | Completed |
| Index audit | Completed |
| Missing foreign key indexes | Created and verified |
| Final data quality validation | Pending |
| Query performance analysis | Pending |
| SQL final sign-off | Pending |

## 8. Next Development Phase

After SQL finalisation, the project will proceed to Python ETL integration.

The Python layer will connect to PostgreSQL, automate data ingestion and transformation, execute validation checks and support the overall SupplyPulse analytical pipeline.