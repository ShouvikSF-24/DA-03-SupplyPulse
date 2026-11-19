
SELECT
    ns.nspname AS table_schema,
    tbl.relname AS table_name,
    con.conname AS foreign_key_name,
    att.attname AS foreign_key_column
FROM pg_constraint con
JOIN pg_class tbl
    ON tbl.oid = con.conrelid
JOIN pg_namespace ns
    ON ns.oid = tbl.relnamespace
CROSS JOIN LATERAL
    unnest(con.conkey) AS fk(attnum)
JOIN pg_attribute att
    ON att.attrelid = tbl.oid
    AND att.attnum = fk.attnum
WHERE con.contype = 'f'
  AND ns.nspname IN ('core', 'analytics')
  AND array_length(con.conkey, 1) = 1
  AND NOT EXISTS (
      SELECT 1
      FROM pg_index idx
      WHERE idx.indrelid = con.conrelid
        AND idx.indisvalid
        AND idx.indisready
        AND idx.indkey[0] = fk.attnum
  )
ORDER BY
    ns.nspname,
    tbl.relname,
    att.attname;
