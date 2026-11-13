from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from scripts.setup import manage


class SetupTests(unittest.TestCase):
    def test_environment_paths_on_windows_and_unix(self):
        for platform, expected in [("win32", "Scripts/python.exe"), ("linux", "bin/python")]:
            with self.subTest(platform=platform), patch.object(manage.sys, "platform", platform):
                self.assertEqual(manage.environment_python(Path("env")), Path("env") / expected)

    def test_default_install_is_one_pip_call_and_never_freezes(self):
        python = Path("env/python")
        with patch.object(manage, "run") as run:
            manage.install(python, [], pdf=True)
        run.assert_called_once_with([
            str(python), "-m", "pip", "install",
            "-r", str(manage.ROOT / "requirements.txt"),
            "-r", str(manage.ROOT / "requirements-pdf.txt"),
        ])

    def test_custom_packages_are_preserved_as_individual_arguments(self):
        with patch.object(manage, "run") as run:
            manage.install(Path("python"), ["some-package>=1", "package[extra]"])
        run.assert_called_once_with([
            "python", "-m", "pip", "install", "some-package>=1", "package[extra]",
        ])

    def test_init_creates_environment_and_installs_once(self):
        with (
            patch.object(Path, "is_file", return_value=False),
            patch.object(manage.venv, "EnvBuilder") as builder,
            patch.object(manage, "install") as install,
        ):
            self.assertEqual(manage.main(["init", "--pdf"]), 0)
        builder.assert_called_once_with(with_pip=True)
        builder.return_value.create.assert_called_once_with(manage.ENVIRONMENT)
        install.assert_called_once_with(manage.environment_python(), [], pdf=True)

    def test_repeated_init_reuses_existing_environment(self):
        with (
            patch.object(Path, "is_file", return_value=True),
            patch.object(manage.venv, "EnvBuilder") as builder,
            patch.object(manage, "install"),
        ):
            self.assertEqual(manage.main(["init"]), 0)
        builder.assert_not_called()

    def test_init_rejects_environment_from_another_operating_system(self):
        stderr = StringIO()
        with (
            patch.object(Path, "is_file", side_effect=[False, True]),
            patch.object(manage.venv, "EnvBuilder") as builder,
            patch.object(manage, "install") as install,
            redirect_stderr(stderr),
            self.assertRaises(SystemExit) as error,
        ):
            manage.main(["init"])
        self.assertEqual(error.exception.code, 2)
        self.assertIn("another operating system", stderr.getvalue())
        builder.assert_not_called()
        install.assert_not_called()

    def test_missing_environment_has_actionable_error(self):
        stderr = StringIO()
        with (
            patch.object(Path, "is_file", return_value=False),
            redirect_stderr(stderr),
            self.assertRaises(SystemExit) as error,
        ):
            manage.main(["install"])
        self.assertEqual(error.exception.code, 2)
        self.assertIn("manage.py init", stderr.getvalue())

    def test_dev_preserves_arguments_and_callers_directory(self):
        with (
            patch.object(Path, "is_file", return_value=True),
            patch.object(manage, "run") as run,
        ):
            self.assertEqual(manage.main(["dev", "--", "input space.ipynb", "output.pdf"]), 0)
        run.assert_called_once_with([
            str(manage.environment_python()), str(manage.ROOT / "main.py"),
            "input space.ipynb", "output.pdf",
        ], cwd=Path.cwd())

    def test_subprocess_failure_propagates_exit_code(self):
        with (
            patch.object(Path, "is_file", return_value=True),
            patch.object(manage, "run", side_effect=subprocess.CalledProcessError(7, ["python"])),
        ):
            self.assertEqual(manage.main(["dev", "--", "--help"]), 7)

    def test_dev_without_arguments_shows_help(self):
        with (
            patch.object(Path, "is_file", return_value=True),
            patch.object(manage, "run") as run,
        ):
            self.assertEqual(manage.main(["dev"]), 0)
        self.assertEqual(run.call_args.args[0][-1], "--help")

    def test_test_command_uses_project_environment_and_repository_directory(self):
        with (
            patch.object(Path, "is_file", return_value=True),
            patch.object(manage, "run") as run,
        ):
            self.assertEqual(manage.main(["test"]), 0)
        run.assert_called_once_with([
            str(manage.environment_python()), "-m", "unittest", "discover", "-s", "tests", "-v",
        ])


if __name__ == "__main__":
    unittest.main()
