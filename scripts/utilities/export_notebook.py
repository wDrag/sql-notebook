#!/usr/bin/env python3
"""Export saved notebook content without executing cells or changing the source."""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
import re
import sys
import tempfile


# Strip only a standalone SQL cell magic. Connection/options/capture arguments
# carry meaning, so keep those headers visible instead of silently losing them.
SQL_MAGIC = re.compile(r"\A%%sql[ \t]*(?:\r?\n|\Z)")


def prepare_notebook(notebook):
    """Return a cleaned copy, preserving SQL, outputs, and non-SQL magics."""
    prepared = deepcopy(notebook)
    prepared.cells = [
        cell for cell in prepared.cells
        if "hide_cell" not in cell.get("metadata", {}).get("tags", [])
    ]
    for cell in prepared.cells:
        if cell.cell_type == "code":
            cell.source = SQL_MAGIC.sub("", cell.source, count=1)
    return prepared


def notebook_to_html(notebook, notebook_dir: Path) -> str:
    """Render the saved cells and outputs; never connect to a database."""
    from nbconvert import HTMLExporter

    exporter = HTMLExporter()
    html, _ = exporter.from_notebook_node(
        prepare_notebook(notebook),
        resources={"metadata": {"path": str(notebook_dir)}},
    )
    return html


def render_pdf(html: str, notebook_dir: Path, output_path: Path) -> None:
    """Resolve local images relative to the notebook, regardless of cwd."""
    try:
        from weasyprint import HTML
    except (ImportError, OSError) as exc:
        raise RuntimeError(
            "PDF rendering requires WeasyPrint and its native libraries. "
            "Install requirements-pdf.txt and follow the platform setup in README.md."
        ) from exc

    HTML(string=html, base_url=str(notebook_dir)).write_pdf(str(output_path))


def export_notebook(input_path: str | Path, output_path: str | Path) -> Path:
    """Atomically replace the PDF only after a successful render."""
    source = Path(input_path).expanduser().resolve()
    destination = Path(output_path).expanduser().resolve()
    if source.suffix.lower() != ".ipynb":
        raise ValueError("Input must be an .ipynb notebook.")
    if not source.is_file():
        raise FileNotFoundError(f"Notebook does not exist: {source}")
    if destination.suffix.lower() != ".pdf":
        raise ValueError("Output must have a .pdf extension.")

    import nbformat

    try:
        notebook = nbformat.read(source, as_version=4)
        nbformat.validate(notebook)
    except nbformat.ValidationError as exc:
        raise ValueError(f"Invalid notebook structure: {exc.message}") from exc
    except (AttributeError, KeyError, TypeError) as exc:
        raise ValueError("Invalid notebook structure: expected a notebook JSON object.") from exc
    html = notebook_to_html(notebook, source.parent)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Use the destination filesystem so replace is atomic. Close before handing
    # the path to WeasyPrint: Windows forbids reopening a NamedTemporaryFile.
    with tempfile.NamedTemporaryFile(
        dir=destination.parent, prefix=f".{destination.stem}-", suffix=".pdf",
        delete=False,
    ) as temporary:
        temporary_path = Path(temporary.name)
    try:
        render_pdf(html, source.parent, temporary_path)
        temporary_path.replace(destination)
    finally:
        temporary_path.unlink(missing_ok=True)
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="saved .ipynb notebook")
    parser.add_argument("output", type=Path, help="destination .pdf file")
    args = parser.parse_args(argv)
    try:
        destination = export_notebook(args.input, args.output)
    except ImportError as exc:
        print(
            f"Export failed: missing PDF dependency ({exc}). "
            "Install with: python scripts/setup/manage.py install --pdf",
            file=sys.stderr,
        )
        return 1
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Export failed: {exc}", file=sys.stderr)
        return 1
    print(f"Export complete: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
