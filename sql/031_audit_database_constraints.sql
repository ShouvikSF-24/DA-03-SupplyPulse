
SELECT
    n.nspname AS table_schema,
    t.relname AS table_name,
    c.conname AS constraint_name,
    CASE c.contype
        WHEN 'p' THEN 'PRIMARY KEY'
        WHEN 'f' THEN 'FOREIGN KEY'
        WHEN 'u' THEN 'UNIQUE'
    END AS constraint_type,
    ARRAY(
        SELECT a.attname
        FROM unnest(c.conkey) WITH ORDINALITY AS k(attnum, ord)
        JOIN pg_attribute a
          ON a.attrelid = c.conrelid
         AND a.attnum = k.attnum
        ORDER BY k.ord
    ) AS columns,
    rn.nspname AS referenced_schema,
    rt.relname AS referenced_table,
    ARRAY(
        SELECT ra.attname
        FROM unnest(c.confkey) WITH ORDINALITY AS k(attnum, ord)
        JOIN pg_attribute ra
          ON ra.attrelid = c.confrelid
         AND ra.attnum = k.attnum
        ORDER BY k.ord
    ) AS referenced_columns
FROM pg_constraint c
JOIN pg_class t
    ON t.oid = c.conrelid
JOIN pg_namespace n
    ON n.oid = t.relnamespace
LEFT JOIN pg_class rt
    ON rt.oid = c.confrelid
LEFT JOIN pg_namespace rn
    ON rn.oid = rt.relnamespace
WHERE c.contype IN ('p', 'f', 'u')
  AND n.nspname IN ('core', 'analytics')
ORDER BY
    n.nspname,
    t.relname,
    c.contype,
    c.conname;
