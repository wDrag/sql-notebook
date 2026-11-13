---
applyTo: "**"
---

# SQL Notebook workspace instructions

- Keep the repository clean and modular. Edit original notebooks; do not leave
  throwaway notebooks, reports, datasets, or snippets. Use `report.local` for
  requested analysis or audit reports.
- Use real project schemas and data. Never invent database tables, columns,
  measurements, or credentials. Ask when required schema information is missing.
- Confirm SQL syntax against the official documentation for the actual dialect.
  Verify queries and connections in the terminal before notebook execution.
  Use EXPLAIN and bounded results where appropriate; be aware that EXPLAIN ANALYZE
  executes the query.
- Use parameterized SQL, explicit joins and column names, explicit transactions
  for related writes, and proper connection/cursor cleanup.
- Keep connection strings in environment variables or ignored `.env` files.
  Never commit sensitive notebook outputs or database credentials.
- Organize notebooks by purpose under `notebooks/`. Add explanatory Markdown cells
  above complex queries, and remove redundant queries when revising an analysis.
- The actual stack is Python 3.11+, IPython SQL magic, SQLAlchemy,
  psycopg2-binary, and PyMySQL; SQLite is in the standard library. PDF export uses
  the optional nbformat/nbconvert/WeasyPrint stack. There is no frontend or Node
  build in this repository.
- Use `python scripts/setup/manage.py init` for setup, `install --pdf` for PDF
  dependencies, and `test` for checks. Preserve `python_modules` as the project
  environment location and support both Windows and Unix interpreter paths.
- Install requirements together with `python -m pip install -r ...`. Never freeze
  an arbitrary local environment over the dependency manifests. Update declared
  dependencies and constraints intentionally.
- Keep export modules safe to import. Export saved content without executing
  notebooks, changing their source, or connecting to databases.
- Tooling tests may use in-memory notebook objects and automatically cleaned
  temporary export files. They must never require a real database or create
  dummy SQL schemas or project notebooks.
- Before committing, run the relevant checks and inspect `git status` for
  leftovers. Keep commit messages concise (at most 20 words).
