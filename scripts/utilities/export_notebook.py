#!/usr/bin/env python3
import sys
import nbformat
from nbconvert import HTMLExporter
from weasyprint import HTML
from traitlets.config import Config
import re

if len(sys.argv) < 3:
    print("Usage: python export_notebook.py input.ipynb output.pdf")
    sys.exit(1)

input_path = sys.argv[1]
output_path = sys.argv[2]

print(f"Exporting notebook {input_path} to PDF {output_path}...")

# Load notebook
nb = nbformat.read(input_path, as_version=4)

# Remove hide_cell + strip magic lines
c = Config()
c.TagRemovePreprocessor.enabled = True
c.TagRemovePreprocessor.remove_cell_tags = ["hide_cell"]

html_exporter = HTMLExporter(config=c)

# BEFORE exporting → remove %%sql from source
for cell in nb.cells:
    if cell.get("cell_type") == "code":
        # strip "%%sql" only if it's the first line
        cell["source"] = re.sub(r"^%%sql\s*\n", "", cell["source"])

html_str, _ = html_exporter.from_notebook_node(nb)

HTML(string=html_str).write_pdf(output_path)

print(f"Export complete → {output_path}")
