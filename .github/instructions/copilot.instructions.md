---
applyTo: "**"
---

# SQL Notebook Workspace - AI Coding Agent Instructions

## Kevin's Code Conduct (CRITICAL - Read First)

1. **No junk files.** Always edit the original notebook file. Never create random or "simple" test notebooks.
2. **Use real data, not dummy data.** Work with actual database schemas and real queries. Remove test data after testing.
3. **Verify with terminal first.** Test SQL commands and database connections in the terminal before executing in notebooks.
4. **Work only with real project data.** Handle real and existing database data within the project. Do not fabricate schemas or create random test tables.
5. **Minimize temp and test files.** Test queries locally before committing. Focus strictly on the user's request.
6. **Keep the repo clean and modular.** Never leave temporary files, junk markdowns, or throwaway snippets. Organize notebooks by topic/domain.
7. **Read official documentation carefully.** Always consult accurate SQL dialect docs (PostgreSQL, MySQL, SQLite, etc.) for proper syntax and functions.
8. **Use `report.local` for all reports.** When generating query analysis, error reports, or documentation summaries, output to `report.local` at the project root. Never create random markdown files for reports.
9. **Always check for leftovers before committing.** Run `git status` to verify no orphaned files remain. Keep commit messages concise (max 20 words).
10. **Be concise and efficient.** Skip pleasantries and confirmations unless asked. Execute tasks directly and give minimal explanations. Save premium request quota.
11. **Verification when generating SQL.**
    - Summarize the reasoning and re-evaluate query logic.
    - Double-check that table names, column names, and functions exist in the schema.
    - If uncertain about schema, ask clarifying questions instead of assuming.
    - Always reference the correct SQL dialect syntax (PostgreSQL, MySQL, SQLite, etc.).
    - Never invent undocumented tables, columns, or SQL functions.
12. **Document complex queries.** Add markdown cells explaining query purpose, logic, and expected results above SQL cells.
13. **Remove unused queries.** Always scan for unused or redundant queries and remove them to maintain clean notebooks.
14. **Test queries before executing.** Validate SQL syntax and use EXPLAIN or LIMIT clauses when testing to avoid performance issues.

## Tech Stack & Architecture

**Environment:** Jupyter Notebook / VS Code Notebooks
**Database Systems:** PostgreSQL, MySQL, SQLite, SQL Server (support multiple dialects)
**Key Tools:**

-   SQL clients: psycopg2 (PostgreSQL), mysql-connector-python (MySQL), sqlite3 (SQLite)
-   Data analysis: pandas, numpy
-   Visualization: matplotlib, seaborn, plotly
-   Notebook: ipykernel, jupyter
-   Query optimization: sqlparse (for formatting), EXPLAIN/ANALYZE

## Project Structure

```
notebooks/
├── exploratory/          # Ad-hoc queries and data exploration
├── analysis/             # Analytical queries and reports
├── migrations/           # Schema changes and data migrations
├── optimization/         # Query performance tuning
└── documentation/        # Schema documentation and examples
scripts/
├── setup/                # Database setup scripts
├── etl/                  # Extract, Transform, Load scripts
└── utilities/            # Helper Python scripts
data/
├── sample/               # Sample datasets (CSV, JSON)
└── exports/              # Query results and exports
schema/
├── ddl/                  # Data Definition Language files
├── dml/                  # Data Manipulation Language examples
└── constraints/          # Foreign keys, indexes, triggers
```

## Critical Patterns & Conventions

### Database Connection Pattern

-   **Connection strings:** Store in environment variables or `.env` files (never commit credentials)
-   **Connection pooling:** Use connection pools for production environments
-   **Transaction management:** Use explicit BEGIN/COMMIT/ROLLBACK for multi-statement transactions
-   **Error handling:** Always wrap database operations in try/except blocks
-   **Close connections:** Properly close connections and cursors after use

### SQL Best Practices

-   **Parameterized queries:** Always use parameterized queries to prevent SQL injection
-   **Explicit column names:** Use explicit column names instead of `SELECT *`
-   **Indexes:** Create indexes on frequently queried columns
-   **JOINs:** Prefer explicit JOIN syntax over implicit joins in WHERE clause
-   **LIMIT clauses:** Use LIMIT when testing queries to avoid large result sets
-   **Comments:** Add SQL comments for complex query logic
-   **Formatting:** Use consistent indentation and line breaks for readability

### Notebook Cell Organization

-   **Markdown cells:** Use for explanations, query purpose, and results interpretation
-   **SQL cells:** One logical query per cell (split complex operations)
-   **Python cells:** For data processing, visualization, and database connections
-   **Cell execution order:** Maintain logical order; mark dependencies clearly
-   **Output management:** Clear outputs before committing if they contain sensitive data

### Query Optimization

-   **EXPLAIN:** Use EXPLAIN or EXPLAIN ANALYZE to understand query execution plans
-   **Indexing:** Check if queries benefit from indexes
-   **Query rewriting:** Optimize subqueries, CTEs, and joins for performance
-   **Statistics:** Keep table statistics up to date with ANALYZE (PostgreSQL)
-   **Avoiding pitfalls:** Watch for N+1 queries, full table scans, and implicit conversions

## Development Workflow

### Commands (use pnpm)

```bash
pnpm dev              # Dev server with Turbo (localhost:3000)
pnpm build            # Production build
pnpm build:prod       # Build + remove source maps
pnpm start            # Start production server
pnpm lint             # ESLint
pnpm format           # Prettier (auto-formats on pre-commit)
```

### Code Quality

-   **Pre-commit hooks:** Husky + lint-staged
    -   Runs ESLint + Prettier on staged `.ts`, `.tsx` files
-   **ESLint config:** `eslint.config.mjs` (Flat config format)
    -   Plugins: `@next/eslint-plugin-next`, `react-hooks`, `tailwindcss`, `prettier`
    -   Import sorting: `eslint-plugin-sort-export-all`

## Development Workflow

### Common Commands

```bash
# Database connections
psql -h localhost -U username -d database     # PostgreSQL
mysql -h localhost -u username -p database    # MySQL
sqlite3 database.db                           # SQLite

# Python environment
pip install -r requirements.txt               # Install dependencies
pip install psycopg2-binary                   # PostgreSQL adapter
pip install mysql-connector-python            # MySQL adapter
pip install pandas sqlalchemy                 # Data analysis tools

# Jupyter
jupyter notebook                              # Start Jupyter server
jupyter lab                                   # Start JupyterLab
```

### Notebook Workflow

1. **Setup cell:** Import libraries and establish database connection
2. **Schema exploration:** Query information_schema or system catalogs
3. **Query development:** Build queries incrementally, test with LIMIT
4. **Data analysis:** Load results into pandas DataFrames for analysis
5. **Visualization:** Create charts with matplotlib/seaborn/plotly
6. **Documentation:** Add markdown cells explaining findings
7. **Cleanup:** Close connections, clear sensitive outputs

### Code Quality

-   **SQL formatting:** Use sqlparse or online formatters for consistent style
-   **Code review:** Check queries for performance issues before running on production
-   **Version control:** Commit notebooks with clear outputs (or cleared if sensitive)
-   **Documentation:** Maintain README with database connection instructions

## Common Tasks

### Creating a new analysis notebook

1. Create notebook in appropriate subfolder (`notebooks/exploratory/`, `notebooks/analysis/`)
2. Start with markdown cell describing the analysis goal
3. Add setup cell: imports and database connection
4. Document each query with markdown cells
5. Include visualizations for key findings

### Exploring a new database schema

1. Query `information_schema.tables` to list all tables
2. Query `information_schema.columns` for table structures
3. Check foreign key relationships
4. Document findings in markdown cells
5. Create reusable connection code for future notebooks

### Optimizing a slow query

1. Use EXPLAIN or EXPLAIN ANALYZE to see execution plan
2. Check for missing indexes on JOIN and WHERE columns
3. Rewrite subqueries as JOINs or CTEs if more efficient
4. Test with LIMIT to verify correctness before full run
5. Document optimization steps and performance gains

### Exporting query results

1. Load results into pandas DataFrame
2. Use `.to_csv()`, `.to_excel()`, or `.to_json()` methods
3. Save to `data/exports/` directory
4. Document export purpose and timestamp

## Critical Reminders

-   **Never commit database credentials** - use environment variables or `.env` files
-   **Never create test/dummy databases** - work with real schemas
-   **Test queries with LIMIT** before running on full datasets
-   **Use parameterized queries** to prevent SQL injection
-   **Verify in terminal** before executing database-altering statements

-   **Keep repo clean** - no junk markdown files, no temporary code
