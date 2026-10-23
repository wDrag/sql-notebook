# SQL Notebook

A workspace for SQL notebooks, database schemas, and saved notebook PDF exports.
Keep personal notebooks and data under the ignored `.local/` directory.

Requires Python **3.11 or newer**. Use VS Code's Jupyter extension or your existing
Jupyter installation to edit notebooks. A Jupyter server is not installed by this
project.

## Setup

From the repository root, on Windows, macOS, or Linux:

```sh
python scripts/setup/manage.py init
```

Use `python3` if that is your system's Python command. This creates the existing
`python_modules` virtual environment and installs the SQL/notebook dependencies
in one pip invocation. Repeating the command reuses the environment. Activation
is optional; select its interpreter as your notebook kernel:

- Windows: `python_modules/Scripts/python.exe`
- macOS/Linux: `python_modules/bin/python`

Virtual environments are specific to their operating system. Setup rejects an
existing environment created by another OS; use separate checkouts or recreate
the environment when moving between Windows and WSL/Linux.

To install additional packages, quote version constraints as needed:

```sh
python scripts/setup/manage.py install "pandas>=2"
```

Installs never rewrite requirements. Record intentional dependency changes in
`requirements.txt`; the original version pins are retained in `constraints.txt`.
Constraints apply to the declared requirements, rather than forcing every
transitive or optional package to be installed. Custom package installs are
unconstrained unless you pass a requirements file to pip directly.

The default environment includes IPython SQL magic, SQLAlchemy, PostgreSQL
(`psycopg2-binary`) and MySQL (`PyMySQL`) adapters. SQLite comes with Python.
Load the extension with `%load_ext sql`; supply your actual connection string
through an environment variable. Keep credentials and sensitive outputs local.

## PDF exports

Install the optional conversion dependencies:

```sh
python scripts/setup/manage.py install --pdf
```

Or use `init --pdf` when first creating the environment. WeasyPrint also needs
native Pango/GLib libraries; pip alone does not install them. Follow the
[official platform installation instructions](https://doc.courtbouillon.org/weasyprint/v66.0/first_steps.html#installation),
including the Windows MSYS2/Pango setup and `WEASYPRINT_DLL_DIRECTORIES` setting
when needed. Missing native libraries produce an actionable error at export time.

Export an existing, saved notebook:

```sh
python scripts/setup/manage.py dev -- "notebooks/analysis/report.ipynb" "data/exports/report.pdf"
```

With the environment interpreter active, either of these also works:

```sh
python main.py "notebooks/analysis/report.ipynb" "data/exports/report.pdf"
python scripts/utilities/export_notebook.py "notebooks/analysis/report.ipynb" "data/exports/report.pdf"
```

Paths are relative to the calling directory. Parent output directories are created
automatically. Local image paths resolve relative to the notebook directory.
Export uses saved cells and outputs, **never executes cells**, and leaves the
original notebook untouched. Cells tagged `hide_cell` are omitted. A standalone
leading `%%sql` header is removed for presentation; SQL magics with connection,
capture, or option arguments stay visible to preserve their meaning. Existing
PDFs are replaced only after successful rendering; failed renders clean up their
temporary output.

## Make and Bash shortcuts

These wrappers call the same Python tooling. GNU Make and Bash are optional.
Set `PYTHON=python` if `python3` is unavailable.

```sh
make init
make init ARGS=--pdf
make install ARGS=--pdf
make install ARGS='"pandas>=2"'
make dev                              # show the export CLI help
make pdf INPUT="notebooks/analysis/report.ipynb" OUTPUT="data/exports/report.pdf"
make test
bash scripts/setup/init.sh --pdf
bash scripts/utilities/export_notebook.sh "notebooks/analysis/report.ipynb" "data/exports/report.pdf"
```

Use named `INPUT`/`OUTPUT` variables for `make pdf` and `ARGS` for other targets;
the former positional Make syntax is no longer supported. Unknown targets now
fail instead of silently succeeding. There is no production service or `prod`
target in this notebook workspace.

## Switch Git SSH identity in WSL

Run Git and the switch script directly in WSL:

```sh
bash scripts/utilities/switch_ssh.sh wdrag
```

The identity is the key filename under `~/.ssh`. Only this repository's Git
configuration and selected remote transport change; commit author settings stay
unchanged. The script replaces any previous Windows SSH bridge with native SSH.

For a passphrase-protected key, run this in your WSL terminal:

```sh
bash scripts/utilities/switch_ssh.sh wdrag --unlock --check
```

Enter the passphrase at the SSH prompt. The script reuses an existing agent that
holds the selected key, including agents outside the current shell environment.
Otherwise, `--unlock` loads the key into a live agent or starts a persistent one
at `~/.ssh/git-identity-agent.sock` when none is available. The key stays in WSL.
The selected key is forced with `IdentitiesOnly=yes`; SSH config files are
bypassed for this checkout. A new agent starts only with explicit `--unlock`.

Keep the WSL terminal open while Git needs the unlocked key. WSL shutdown clears
agent memory; unlocking is required again after a restart. Ubuntu's systemd agent
socket is normally `/run/user/$(id -u)/openssh_agent`. Login shells should export
that socket as `SSH_AUTH_SOCK`; the switch script can discover it independently.

SSH uses port 22 by default. Use `--port 443` for
[GitHub's alternate SSH endpoint](https://docs.github.com/en/authentication/troubleshooting-ssh/using-ssh-over-the-https-port).
`--check` verifies access with read-only `git ls-remote` without prompting. If
the host is not already trusted, connect once from WSL with
`ssh -T -p 443 git@ssh.github.com` and verify the
[published host fingerprint](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)
before accepting it.

Return to HTTPS with:

```sh
bash scripts/utilities/switch_ssh.sh --https
```

Use `--repo PATH` for another checkout or `--remote NAME` for another remote.
Explicit push URLs are preserved; inspect `git remote -v` if fetch and push
destinations differ.

## Checks

Install PDF dependencies first, then run:

```sh
python scripts/setup/manage.py test
```

Alternatively, in an environment with `nbformat` and `nbconvert` installed:

```sh
python -m unittest discover -s tests -v
```

Tests use in-memory notebooks, temporary export files, and isolated SSH
fixtures. They never connect to an external database or use real SSH keys. Set `RUN_PDF_SMOKE=1` to include an actual
PDF render when native WeasyPrint libraries are installed. CI runs the regression
suite on Windows and Linux with Python 3.11, 3.13, and 3.14, plus real rendering on Linux.

## Layout

```text
notebooks/
  exploratory/      Ad-hoc analysis
  analysis/         Reviewed analysis notebooks
  migrations/       Database migration notebooks
  optimization/     Query optimization work
  documentation/    Schema and query explanations
schema/
  ddl/              Schema definitions
  dml/              Data manipulation scripts
  constraints/      Constraints and indexes
scripts/
  setup/            Cross-platform setup and compatibility wrappers
  etl/              Project ETL scripts
  utilities/        Notebook export
tests/              Tooling regression tests
data/
  sample/           Local data (ignored)
  exports/          Local results (ignored)
```
