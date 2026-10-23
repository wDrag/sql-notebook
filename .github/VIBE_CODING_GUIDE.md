# Working on SQL Notebook

Give coding agents the existing notebook or script path, the actual database
dialect, the relevant schema, and the specific behavior to improve. Never paste
database credentials into a prompt or commit them to a notebook.

Useful requests include:

- Refactor an existing export function while preserving saved outputs and tags.
- Investigate a query using its actual execution plan and table definitions.
- Add an explanatory Markdown cell above an existing complex query.
- Fix environment setup on Windows while retaining the Unix workflow.

For SQL changes, verify schema names and terminal behavior before editing a
notebook. For tooling changes, run `python scripts/setup/manage.py test` after
installing the PDF dependencies. Keep original notebooks, remove temporary
exports, and review `git diff` and `git status` before committing.

See [workspace instructions](instructions/copilot.instructions.md) for conventions
and [README](../README.md) for supported commands.
