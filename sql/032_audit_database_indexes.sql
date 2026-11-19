
SELECT
    schemaname AS table_schema,
    tablename AS table_name,
    indexname AS index_name,
    indexdef AS index_definition
FROM pg_indexes
WHERE schemaname IN ('core', 'analytics')
ORDER BY
    schemaname,
    tablename,
    indexname;
