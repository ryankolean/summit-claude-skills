---
name: cli-duckdb
description: >
  Covers effective use of DuckDB for in-process analytical SQL
  queries directly on CSV, Parquet, JSON, and remote S3/HTTP files without
  importing data. Activates when the user asks about DuckDB, querying files
  with SQL, analytical data processing, or OLAP on local files.
---

# DuckDB — Analytical SQL Engine

**Repo:** https://github.com/duckdb/duckdb

In-process analytical database that queries CSV, Parquet, JSON, and remote
files directly with SQL — no server, no import step. Designed for OLAP
workloads: aggregations, window functions, and large scans run significantly
faster than SQLite or Pandas on the same data.

## When to Activate

**Manual triggers:**
- "How do I use DuckDB?"
- "Query a CSV/Parquet file with SQL"
- "Analytical SQL on local files"
- "Faster than pandas for data analysis"

**Auto-detect triggers:**
- User wants to run SQL directly on CSV or Parquet files without a database
- User wants window functions, PIVOT, or QUALIFY for analytical queries
- User wants to query S3 or HTTP files without downloading them
- User wants to convert between CSV, Parquet, and JSON formats
- User wants approximate aggregations or SUMMARIZE on large datasets

## Key CLI Commands

### Opening DuckDB
```bash
duckdb                       # Temporary in-memory database
duckdb mydb.duckdb           # Open (or create) a persistent database file
duckdb -c "SELECT 42"        # Run a single query and exit
duckdb -json -c "SELECT 1"   # Output as JSON
duckdb -csv  -c "SELECT 1"   # Output as CSV
```

### CLI Dot-Commands
```sql
.mode line/column/csv/json/markdown/box   -- Set output format
.timer on/off                             -- Show query execution time
.tables                                   -- List tables
.schema tablename                         -- Show CREATE statement
.read script.sql                          -- Execute a SQL file
.output results.csv                       -- Redirect output to file
.quit / .exit                             -- Exit DuckDB
.help                                     -- List all commands
```

## Querying Files Directly

```sql
-- CSV (auto-detect schema)
SELECT * FROM 'data.csv' LIMIT 10;
SELECT * FROM read_csv_auto('data.csv');

-- Parquet
SELECT * FROM 'data.parquet' LIMIT 10;
SELECT * FROM read_parquet('data.parquet');

-- JSON
SELECT * FROM read_json_auto('events.json');
SELECT * FROM read_json_auto('logs/*.json');   -- Glob patterns supported

-- Multiple files as one table (union)
SELECT * FROM read_csv_auto('data_*.csv');
SELECT * FROM read_parquet(['jan.parquet', 'feb.parquet', 'mar.parquet']);
```

## COPY TO — Export Results

```sql
-- Export to CSV
COPY (SELECT * FROM 'data.parquet' WHERE year = 2024)
TO 'filtered.csv' (HEADER, DELIMITER ',');

-- Export to Parquet (compressed)
COPY (SELECT * FROM read_csv_auto('raw.csv'))
TO 'output.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);

-- Export to JSON
COPY (SELECT id, name FROM users)
TO 'users.json' (FORMAT JSON, ARRAY true);
```

## Analytical SQL Features

### SUMMARIZE — Instant Data Profile
```sql
SUMMARIZE 'data.csv';
-- Returns: column names, types, min, max, avg, std, null count, etc.
-- No query writing needed — great first step for any new dataset
```

### GROUP BY ALL
```sql
-- GROUP BY ALL groups by all non-aggregate columns automatically
SELECT region, product, SUM(revenue), AVG(discount)
FROM 'sales.csv'
GROUP BY ALL
ORDER BY SUM(revenue) DESC;
```

### Window Functions
```sql
SELECT
  date,
  revenue,
  SUM(revenue) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7d,
  LAG(revenue, 7) OVER (ORDER BY date) AS last_week,
  NTILE(4) OVER (ORDER BY revenue DESC) AS quartile
FROM 'daily_revenue.csv';
```

### CTEs
```sql
WITH base AS (
  SELECT user_id, COUNT(*) AS sessions, SUM(duration) AS total_time
  FROM read_json_auto('events.json')
  WHERE event = 'session_start'
  GROUP BY ALL
),
ranked AS (
  SELECT *, PERCENT_RANK() OVER (ORDER BY total_time) AS pct
  FROM base
)
SELECT * FROM ranked WHERE pct >= 0.95;
```

### PIVOT / UNPIVOT
```sql
-- Pivot: rows → columns
PIVOT (SELECT month, region, revenue FROM 'sales.csv')
ON region
USING SUM(revenue)
GROUP BY month;

-- Unpivot: columns → rows
UNPIVOT wide_table
ON (jan, feb, mar, apr)
INTO NAME month VALUE revenue;
```

### QUALIFY (filter window function results)
```sql
-- Keep only the top revenue row per region (no subquery needed)
SELECT region, product, revenue,
       RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS rnk
FROM 'sales.csv'
QUALIFY rnk = 1;
```

### List, Struct, and Map Types
```sql
-- Aggregate into a list
SELECT user_id, LIST(event ORDER BY ts) AS event_sequence
FROM read_json_auto('events.json')
GROUP BY user_id;

-- Struct access
SELECT payload.user.email FROM read_json_auto('logs.json');

-- Unnest a list column
SELECT user_id, UNNEST(tags) AS tag FROM read_json_auto('posts.json');
```

### Regex
```sql
SELECT * FROM 'logs.csv'
WHERE regexp_matches(message, 'ERROR|FATAL');

SELECT regexp_extract(url, 'https?://([^/]+)', 1) AS domain
FROM 'access_log.csv';
```

### Approximate Aggregations
```sql
-- Approximate COUNT DISTINCT (much faster on large data)
SELECT approx_count_distinct(user_id) FROM 'events.parquet';

-- Reservoir sampling
SELECT * FROM 'data.parquet' USING SAMPLE 1%;
SELECT * FROM 'data.parquet' USING SAMPLE 10000 ROWS;
```

## Advanced Patterns

### httpfs — Query S3 and HTTP Files Directly
```sql
INSTALL httpfs;
LOAD httpfs;

-- Query a public Parquet file over HTTP (no download):
SELECT * FROM read_parquet('https://example.com/data.parquet') LIMIT 5;

-- Query S3 (set credentials first):
SET s3_region='us-east-1';
SET s3_access_key_id='...';
SET s3_secret_access_key='...';
SELECT * FROM read_parquet('s3://my-bucket/data/*.parquet');

-- Hive-partitioned S3 dataset:
SELECT * FROM read_parquet('s3://bucket/events/year=*/month=*/*.parquet',
                            hive_partitioning=true)
WHERE year = 2024 AND month = 3;
```

### Cross-Format Joins
```sql
-- Join a CSV with a Parquet file directly:
SELECT c.name, p.revenue
FROM 'customers.csv' c
JOIN 'transactions.parquet' p ON c.id = p.customer_id
WHERE p.amount > 1000;
```

### CTAS — Create Table As Select
```sql
-- Persist query result as a new table:
CREATE TABLE top_customers AS
SELECT customer_id, SUM(amount) AS ltv
FROM 'orders.parquet'
GROUP BY ALL
ORDER BY ltv DESC
LIMIT 1000;
```

### Parquet Export Optimization
```sql
-- Partition output by column (creates directory structure):
COPY (SELECT * FROM 'large.csv')
TO 'partitioned/' (FORMAT PARQUET, PARTITION_BY (year, region), COMPRESSION ZSTD);
```

### Attach SQLite
```sql
INSTALL sqlite;
LOAD sqlite;

ATTACH 'app.db' AS sqlite (TYPE sqlite);
SELECT * FROM sqlite.users LIMIT 10;

-- Join DuckDB data with SQLite:
SELECT d.event, s.name
FROM read_json_auto('events.json') d
JOIN sqlite.users s ON d.user_id = s.id;
```

## Practical Examples

```bash
# Profile a new dataset instantly:
duckdb -c "SUMMARIZE 'data.csv'"

# Count rows in a Parquet file:
duckdb -c "SELECT COUNT(*) FROM 'large.parquet'"

# Convert CSV to Parquet:
duckdb -c "COPY (SELECT * FROM 'data.csv') TO 'data.parquet' (FORMAT PARQUET)"

# Run a SQL file against a dataset:
duckdb -c ".read analysis.sql"

# Output query results as JSON to stdout:
duckdb -json -c "SELECT * FROM 'data.csv' LIMIT 5"

# Quick column stats:
duckdb -c "SELECT * FROM (SUMMARIZE 'data.csv') WHERE column_name = 'revenue'"
```

## Chaining with Other Skills

- **jq:** Pipe DuckDB JSON output to jq for further reshaping; or preprocess nested JSON with jq before querying with `read_json_auto()`
- **SQLite (cli-sqlite):** Use DuckDB for heavy analytical work then export results to SQLite (`ATTACH ... TYPE sqlite`) for lightweight app consumption; share data both ways
- **fd (cli-fd):** Use fd to build file lists for multi-file queries: `fd -e parquet | xargs -I{} duckdb -c "SELECT COUNT(*) FROM '{}'"` or pass a glob to `read_parquet()`
- **bat (cli-bat):** Use `bat -l sql` to view and syntax-highlight SQL scripts before passing them to `duckdb -c ".read script.sql"`
- **Apify / web scraping:** Export scraped data to CSV or JSON, then use DuckDB to analyze without any import step
