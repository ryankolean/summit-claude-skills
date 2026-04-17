---
name: cli-sqlite
description: >
  Covers effective use of SQLite for serverless SQL databases
  including CLI dot-commands, schema management, CSV import/export, JSON
  functions, FTS5 full-text search, WAL mode, multi-database attach, and
  data analysis workflows. Activates when the user asks about SQLite, sqlite3,
  or embedded SQL databases.
---

# SQLite — Serverless SQL Database

**Repo:** https://github.com/sqlite/sqlite

Self-contained, serverless, zero-configuration SQL database engine. The most
widely deployed database in the world. Great for local data analysis, embedded
apps, prototyping, and file-based data exchange.

## When to Activate

**Manual triggers:**
- "How do I use SQLite?"
- "Query a .db file"
- "Import CSV into a database"
- "Serverless / embedded SQL"

**Auto-detect triggers:**
- User wants to query or transform structured data without a server
- User wants to import CSV files for SQL-based analysis
- User wants a portable, file-based database for an app
- User wants to use full-text search (FTS5)
- User wants to work with JSON data in SQL

## Key CLI Commands (sqlite3)

### Opening a Database
```bash
sqlite3 mydb.db              # Open (or create) a database file
sqlite3 :memory:             # In-memory database (gone when process exits)
sqlite3                      # Open with no file (temporary in-memory)
sqlite3 mydb.db "SELECT 1"   # Run a single query and exit
```

### Dot-Commands (meta-commands)
```sql
.tables                      -- List all tables
.schema                      -- Show CREATE statements for all tables
.schema tablename            -- Show CREATE statement for one table
.mode column                 -- Aligned column output
.mode csv                    -- CSV output
.mode json                   -- JSON output
.mode markdown               -- Markdown table output
.mode box                    -- Box-drawing table output
.headers on                  -- Show column headers
.headers off                 -- Hide column headers
.output results.csv          -- Redirect output to file
.output stdout               -- Reset output to terminal
.import data.csv tablename   -- Import CSV into table
.import --csv data.csv tbl   -- Import with explicit CSV mode
.dump                        -- Dump entire DB as SQL
.dump tablename              -- Dump one table as SQL
.backup backup.db            -- Backup DB to file
.read script.sql             -- Execute a SQL file
.quit / .exit                -- Exit sqlite3
.help                        -- Show all dot-commands
```

### Useful Settings for Analysis
```bash
# Add to ~/.sqliterc for persistent settings:
.mode box
.headers on
.timer on        -- Show query execution time
.changes on      -- Show rows affected
.nullvalue NULL  -- Display NULLs explicitly
```

## SQL Patterns

### DDL & DML
```sql
-- Create table
CREATE TABLE users (
  id    INTEGER PRIMARY KEY AUTOINCREMENT,
  name  TEXT NOT NULL,
  email TEXT UNIQUE,
  ts    TEXT DEFAULT (datetime('now'))
);

-- Insert
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

-- Upsert (INSERT OR REPLACE / ON CONFLICT)
INSERT INTO users (id, name, email)
VALUES (1, 'Alice', 'alice@new.com')
ON CONFLICT(id) DO UPDATE SET email = excluded.email;

-- Update / Delete
UPDATE users SET name = 'Bob' WHERE id = 2;
DELETE FROM users WHERE email IS NULL;
```

### JOINs
```sql
SELECT u.name, o.total
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE o.total > 100
ORDER BY o.total DESC;
```

### CTEs (Common Table Expressions)
```sql
WITH monthly AS (
  SELECT strftime('%Y-%m', ts) AS month, SUM(total) AS revenue
  FROM orders
  GROUP BY 1
),
ranked AS (
  SELECT *, ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rn
  FROM monthly
)
SELECT * FROM ranked WHERE rn <= 3;
```

### Window Functions
```sql
SELECT
  name,
  total,
  SUM(total) OVER (ORDER BY ts) AS running_total,
  AVG(total) OVER (PARTITION BY user_id) AS user_avg,
  RANK() OVER (ORDER BY total DESC) AS rnk
FROM orders;
```

### JSON Functions
```sql
-- Extract a JSON field
SELECT json_extract(payload, '$.user.email') AS email FROM events;

-- Expand a JSON array into rows
SELECT value FROM events, json_each(json_extract(payload, '$.tags'));

-- Build JSON from columns
SELECT json_object('id', id, 'name', name) FROM users;

-- Check if JSON key exists
SELECT * FROM events WHERE json_extract(payload, '$.error') IS NOT NULL;
```

### Full-Text Search (FTS5)
```sql
-- Create FTS5 virtual table
CREATE VIRTUAL TABLE docs_fts USING fts5(title, body, content=docs);

-- Populate
INSERT INTO docs_fts SELECT title, body FROM docs;

-- Search
SELECT * FROM docs_fts WHERE docs_fts MATCH 'sqlite performance';

-- Ranked search
SELECT *, rank FROM docs_fts WHERE docs_fts MATCH 'error handling' ORDER BY rank;

-- Highlight matching terms
SELECT highlight(docs_fts, 1, '<b>', '</b>') FROM docs_fts WHERE docs_fts MATCH 'query';
```

## Advanced Patterns

### CSV Import for Data Analysis
```bash
# Import CSV (auto-creates table from headers)
sqlite3 analysis.db <<'EOF'
.mode csv
.import data.csv sales
.headers on
.mode box
SELECT region, SUM(amount) AS total FROM sales GROUP BY region ORDER BY total DESC;
EOF

# One-liner: import and query
sqlite3 -csv -header analysis.db ".import data.csv t" "SELECT * FROM t LIMIT 5"
```

### WAL Mode (Write-Ahead Logging)
```sql
-- Enable WAL for concurrent reads + writes (recommended for apps)
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;   -- Faster writes, safe with WAL
PRAGMA cache_size=-64000;    -- 64MB page cache
PRAGMA temp_store=MEMORY;    -- Temp tables in memory
```

### In-Memory Database
```bash
# Full analysis workflow in memory (discarded on exit):
sqlite3 :memory: <<'EOF'
CREATE TABLE t (a, b, c);
.mode csv
.import /dev/stdin t
SELECT SUM(c) FROM t GROUP BY a;
EOF
```

### Multi-Database ATTACH
```sql
-- Attach a second database and query across both
ATTACH DATABASE 'archive.db' AS arch;

SELECT m.name, a.legacy_id
FROM main.users m
JOIN arch.users a ON m.email = a.email;

-- Copy a table from one DB to another
CREATE TABLE archive_users AS SELECT * FROM arch.users;
DETACH DATABASE arch;
```

### Virtual Tables
```sql
-- CSV virtual table (no import needed — query CSV directly)
CREATE VIRTUAL TABLE temp.csv_data USING csv(filename='data.csv', header=YES);
SELECT * FROM temp.csv_data WHERE amount > 1000;

-- Generate series
SELECT value FROM generate_series(1, 100) WHERE value % 7 = 0;
```

### Indexes and Query Planning
```sql
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_ts   ON orders(ts DESC);

-- Inspect query plan
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE user_id = 5 ORDER BY ts DESC;
```

## Practical Examples

```bash
# Quick schema dump of an existing DB:
sqlite3 app.db ".schema"

# Count rows in every table:
sqlite3 app.db "SELECT name, (SELECT COUNT(*) FROM pragma_table_info(name)) cols FROM sqlite_master WHERE type='table'"

# Export a table to CSV:
sqlite3 -csv -header app.db "SELECT * FROM users" > users.csv

# Run a SQL file:
sqlite3 app.db < migrations/001_add_index.sql

# Diff two databases (schema):
diff <(sqlite3 db1.db .schema) <(sqlite3 db2.db .schema)
```

## Chaining with Other Skills

- **jq:** Export JSON from SQLite with `json_object()`/`json_group_array()`, pipe to jq for further transformation; or preprocess JSON with jq then import to SQLite
- **duckdb (cli-duckdb):** Use DuckDB for heavy analytical queries on Parquet/CSV, export results to SQLite for app consumption; or attach SQLite files in DuckDB with `ATTACH 'app.db' AS sqlite (TYPE sqlite)`
- **fd (cli-fd):** Use fd to find all `.db` files in a directory tree before running batch schema inspections or migrations
- **bat (cli-bat):** Use `bat -l sql` to view SQL migration files with syntax highlighting before running them
