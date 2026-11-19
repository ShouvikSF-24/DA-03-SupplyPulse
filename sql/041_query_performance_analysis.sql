
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT * FROM analytics.vw_kpi_overview;


EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT * FROM analytics.vw_monthly_sales;


EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT * FROM analytics.vw_delivery_performance;


EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT * FROM analytics.vw_inventory_risk;


EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT * FROM analytics.vw_supplier_performance;


-- SUPPLYPULSE QUERY PERFORMANCE BASELINE
-- Date: 2026-11-19
-- Database: PostgreSQL
-- KPI Overview: Execution 902.060 ms; temporary reads 266 blocks; temporary writes 267 blocks.
-- Monthly Sales: Execution 1425.836 ms; external merge sort; approximately 11992 KB disk usage; temporary reads 1499 blocks; temporary writes 1503 blocks.
-- Delivery Performance: Execution 1599.672 ms; parallel sequential scan and parallel aggregation.
-- Inventory Risk: Execution 7.880 ms; hash joins; no temporary disk activity reported.
-- Supplier Performance: Execution 17.382 ms; Memoize cache hits 90; misses 10; supplier primary key index scan.
-- Assessment: Performance baselines established. Further tuning requires controlled testing.
-- CONTROLLED PERFORMANCE EXPERIMENT
-- Original work_mem: 4 MB
-- Test work_mem: 16 MB
-- Scope: Current PostgreSQL session only
-- No permanent configuration changes


-- =====================================================
-- CONTROLLED WORK_MEM EXPERIMENT
-- =====================================================
-- Original work_mem: 4 MB
-- Experimental work_mem: 16 MB
-- Test query: analytics.vw_monthly_sales
-- Original execution time: 1425.836 ms
-- Experimental execution time: 1481.758 ms
-- Original temporary blocks read: 1499
-- Experimental temporary blocks read: 1499
-- Original temporary blocks written: 1503
-- Experimental temporary blocks written: 1500
-- Original sort: External Merge
-- Experimental sort: External Merge
--
-- CONCLUSION:
-- Increasing work_mem to 16 MB did not produce
-- a meaningful performance improvement.
-- Original configuration was restored and verified.
--
-- FINAL PERFORMANCE ASSESSMENT:
-- Five analytical views benchmarked successfully.
-- KPI Overview: 902.060 ms
-- Monthly Sales: 1425.836 ms
-- Delivery Performance: 1599.672 ms
-- Inventory Risk: 7.880 ms
-- Supplier Performance: 17.382 ms
--
-- No additional indexes or permanent PostgreSQL
-- configuration changes were justified by this review.
-- Further optimisation can be considered after
-- Python ETL integration and workload testing.
-- =====================================================
