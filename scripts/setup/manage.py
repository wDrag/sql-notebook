#!/usr/bin/env python3
"""Cross-platform environment management, requiring only Python 3.11+."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import venv


ROOT = Path(__file__).resolve().parents[2]
ENVIRONMENT = ROOT / "python_modules"


def environment_python(environment: Path = ENVIRONMENT) -> Path:
    """Use the same existing environment location on Unix and Windows."""
    directory = "Scripts" if sys.platform == "win32" else "bin"
    executable = "python.exe" if sys.platform == "win32" else "python"
    return environment / directory / executable


def run(arguments: list[str], *, cwd: Path = ROOT) -> None:
    subprocess.run(arguments, cwd=cwd, check=True)


def install(python: Path, packages: list[str], *, pdf: bool = False) -> None:
    arguments = [str(python), "-m", "pip", "install"]
    if packages:
        arguments.extend(packages)
    else:
        arguments.extend(["-r", str(ROOT / "requirements.txt")])
    if pdf:
        arguments.extend(["-r", str(ROOT / "requirements-pdf.txt")])
    run(arguments)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser("init", help="create environment and install dependencies")
    initialize.add_argument("--pdf", action="store_true", help="also install PDF dependencies")
    dependencies = commands.add_parser("install", help="install dependencies without rewriting them")
    dependencies.add_argument("--pdf", action="store_true")
    dependencies.add_argument("packages", nargs="*", help="optional additional package specifiers")
    development = commands.add_parser("dev", help="run the PDF CLI in the project environment")
    development.add_argument("arguments", nargs=argparse.REMAINDER)
    commands.add_parser("test", help="run tooling regression tests in the project environment")
    args = parser.parse_args(argv)
    python = environment_python()
    try:
        if args.command == "init":
            if not python.is_file():
                other_platform = ENVIRONMENT / (
                    "bin/python" if sys.platform == "win32" else "Scripts/python.exe"
                )
                if other_platform.is_file():
                    parser.error(
                        "python_modules belongs to another operating system. "
                        "Use a separate checkout or remove and recreate that environment."
                    )
                venv.EnvBuilder(with_pip=True).create(ENVIRONMENT)
            install(python, [], pdf=args.pdf)
        elif not python.is_file():
            parser.error("Project environment is missing; run: python scripts/setup/manage.py init")
        elif args.command == "install":
            install(python, args.packages, pdf=args.pdf)
        elif args.command == "test":
            run([str(python), "-m", "unittest", "discover", "-s", "tests", "-v"])
        else:
            arguments = args.arguments
            if arguments[:1] == ["--"]:
                arguments = arguments[1:]
            if not arguments:
                arguments = ["--help"]
            # Export paths are relative to the caller, even from outside the repo.
            run([str(python), str(ROOT / "main.py"), *arguments], cwd=Path.cwd())
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    except OSError as exc:
        print(f"Setup failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
