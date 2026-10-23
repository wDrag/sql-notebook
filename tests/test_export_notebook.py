"""Regression tests use in-memory notebook objects, never project databases."""

from contextlib import redirect_stderr
from copy import deepcopy
from io import StringIO
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import nbformat

from scripts.utilities import export_notebook as exporter


class NotebookPreparationTests(unittest.TestCase):
    def test_removes_hidden_cells_without_mutating_source(self):
        notebook = nbformat.v4.new_notebook(cells=[
            nbformat.v4.new_markdown_cell("private", metadata={"tags": ["hide_cell"]}),
            nbformat.v4.new_code_cell("%%sql\n", metadata={"tags": ["hide_cell"]}),
            nbformat.v4.new_code_cell("%%sql\n\n-- preserved indentation\n", outputs=[
                nbformat.v4.new_output("stream", name="stdout", text="saved output")
            ]),
        ])
        original = deepcopy(notebook)
        prepared = exporter.prepare_notebook(notebook)
        self.assertEqual(notebook, original)
        self.assertEqual(len(prepared.cells), 1)
        self.assertEqual(prepared.cells[0].source, "\n-- preserved indentation\n")
        self.assertEqual(prepared.cells[0].outputs[0].text, "saved output")

    def test_sql_magic_matching_preserves_other_content(self):
        cases = {
            "%%sql\n\n  -- spacing": "\n  -- spacing",
            "%%sql \t\r\n  -- spacing": "  -- spacing",
            "%%sql": "",
            "%%sql --persist result\nbody": "%%sql --persist result\nbody",
            "%%sql connection\nbody": "%%sql connection\nbody",
            "%%sqlite\nbody": "%%sqlite\nbody",
            "%sql body": "%sql body",
            "\n%%sql\nbody": "\n%%sql\nbody",
            "%%python\nbody": "%%python\nbody",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                notebook = nbformat.v4.new_notebook(cells=[
                    nbformat.v4.new_code_cell(source),
                    nbformat.v4.new_markdown_cell(source),
                ])
                prepared = exporter.prepare_notebook(notebook)
                self.assertEqual(prepared.cells[0].source, expected)
                self.assertEqual(prepared.cells[1].source, source)

    def test_html_contains_saved_outputs_and_never_executes_code(self):
        notebook = nbformat.v4.new_notebook(cells=[
            nbformat.v4.new_markdown_cell("HIDDEN_SENTINEL", metadata={"tags": ["hide_cell"]}),
            nbformat.v4.new_markdown_cell("Visible résumé"),
            nbformat.v4.new_code_cell("raise RuntimeError('must never execute')", outputs=[
                nbformat.v4.new_output("stream", name="stdout", text="SAVED_OUTPUT")
            ]),
        ])
        html = exporter.notebook_to_html(notebook, Path.cwd())
        self.assertIn("Visible résumé", html)
        self.assertIn("SAVED_OUTPUT", html)
        self.assertNotIn("HIDDEN_SENTINEL", html)


class ExportTests(unittest.TestCase):
    def test_invalid_paths_fail_before_loading_optional_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "Input"):
                exporter.export_notebook(root / "input.txt", root / "output.pdf")
            with self.assertRaises(FileNotFoundError):
                exporter.export_notebook(root / "missing.ipynb", root / "output.pdf")
            with patch.object(Path, "is_file", return_value=True):
                with self.assertRaisesRegex(ValueError, "Output"):
                    exporter.export_notebook(root / "input.ipynb", root / "input.ipynb")

    def test_success_creates_parent_and_resolves_notebook_asset_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "notebooks with spaces" / "résumé.ipynb"
            destination = root / "exports with spaces" / "résumé.pdf"

            def render(html, base, target):
                self.assertEqual(html, "rendered html")
                self.assertEqual(base, source.parent)
                self.assertNotEqual(target, destination)
                target.write_bytes(b"%PDF-regression")

            with (
                patch.object(Path, "is_file", return_value=True),
                patch("nbformat.read", return_value=nbformat.v4.new_notebook()) as read,
                patch.object(exporter, "notebook_to_html", return_value="rendered html"),
                patch.object(exporter, "render_pdf", side_effect=render),
            ):
                self.assertEqual(exporter.export_notebook(source, destination), destination)
            read.assert_called_once_with(source, as_version=4)
            self.assertEqual(destination.read_bytes(), b"%PDF-regression")
            self.assertEqual(list(destination.parent.iterdir()), [destination])

    def test_failed_render_keeps_existing_pdf_and_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = root / "output.pdf"
            destination.write_bytes(b"previous PDF")

            def fail(html, base, target):
                target.write_bytes(b"partial output")
                raise RuntimeError("render failed")

            with (
                patch.object(Path, "is_file", return_value=True),
                patch("nbformat.read", return_value=nbformat.v4.new_notebook()),
                patch.object(exporter, "notebook_to_html", return_value="html"),
                patch.object(exporter, "render_pdf", side_effect=fail),
                self.assertRaisesRegex(RuntimeError, "render failed"),
            ):
                exporter.export_notebook(root / "input.ipynb", destination)
            self.assertEqual(destination.read_bytes(), b"previous PDF")
            self.assertEqual(list(root.iterdir()), [destination])

    def test_cli_reports_missing_dependency_without_traceback(self):
        stderr = StringIO()
        with (
            patch.object(exporter, "export_notebook", side_effect=ImportError("nbconvert")),
            redirect_stderr(stderr),
        ):
            self.assertEqual(exporter.main(["input.ipynb", "output.pdf"]), 1)
        self.assertIn("install --pdf", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_invalid_notebook_structure_fails_before_rendering(self):
        notebook = nbformat.v4.new_notebook()
        notebook.cells = [nbformat.NotebookNode(id="invalid-cell", cell_type="unknown", metadata={})]
        with (
            patch.object(Path, "is_file", return_value=True),
            patch("nbformat.read", return_value=notebook),
            patch.object(exporter, "notebook_to_html") as render,
            self.assertRaisesRegex(ValueError, "Invalid notebook structure"),
        ):
            exporter.export_notebook("input.ipynb", "output.pdf")
        render.assert_not_called()

    def test_cli_handles_malformed_notebook_reader_errors(self):
        documents = [
            "{}",
            '{"nbformat": 4, "nbformat_minor": 5, "metadata": {}}',
            "[]",
        ]
        for document in documents:
            with self.subTest(document=document):
                stderr = StringIO()

                def read(*args, **kwargs):
                    return nbformat.reads(document, as_version=4)

                with (
                    patch.object(Path, "is_file", return_value=True),
                    patch("nbformat.read", side_effect=read),
                    patch.object(exporter, "notebook_to_html") as render,
                    redirect_stderr(stderr),
                ):
                    self.assertEqual(exporter.main(["input.ipynb", "output.pdf"]), 1)
                self.assertIn("Invalid notebook structure", stderr.getvalue())
                self.assertNotIn("Traceback", stderr.getvalue())
                render.assert_not_called()

    def test_weasyprint_resolves_assets_relative_to_notebook(self):
        from types import SimpleNamespace
        from unittest.mock import Mock

        html = Mock()
        with patch.dict("sys.modules", {"weasyprint": SimpleNamespace(HTML=html)}):
            exporter.render_pdf("html", Path("notebook directory"), Path("output.pdf"))
        html.assert_called_once_with(string="html", base_url="notebook directory")
        html.return_value.write_pdf.assert_called_once_with("output.pdf")

    @unittest.skipUnless(os.environ.get("RUN_PDF_SMOKE") == "1", "requires native WeasyPrint libraries")
    def test_real_pdf_render(self):
        # Test the real renderer without creating notebook files or SQL data.
        notebook = nbformat.v4.new_notebook(cells=[
            nbformat.v4.new_markdown_cell("# PDF renderer regression\nRésumé")
        ])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "output.pdf"
            exporter.render_pdf(exporter.notebook_to_html(notebook, root), root, target)
            self.assertTrue(target.read_bytes().startswith(b"%PDF-"))
            self.assertGreater(target.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
