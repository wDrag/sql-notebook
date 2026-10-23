"""Exercise identity switching without real keys, agents, or network access."""

import os
from pathlib import Path
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/utilities/switch_ssh.sh"


@unittest.skipUnless(
    sys.platform != "win32" and shutil.which("bash") and shutil.which("git"),
    "requires native Unix Bash and Git",
)
class IdentitySwitchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="identity switch ")
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.repo = root / "checkout"
        self.repo.mkdir()
        self.home = root / "home"
        self.ssh = self.home / ".ssh"
        self.ssh.mkdir(parents=True)
        self.bin = root / "bin"
        self.bin.mkdir()
        self.runtime = root / "runtime"
        self.runtime.mkdir()
        self.environment = {
            **os.environ, "HOME": str(self.home),
            "XDG_RUNTIME_DIR": str(self.runtime),
            "PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
        }
        for name in ("GIT_SSH_COMMAND", "GIT_SSH_VARIANT", "SSH_AUTH_SOCK"):
            self.environment.pop(name, None)
        self.git("init", "-q")
        self.git("remote", "add", "origin", "https://github.com/wDrag/sql-notebook.git")

    def git(self, *arguments):
        return subprocess.check_output(
            ["git", "-C", str(self.repo), *arguments],
            env=self.environment, text=True, stderr=subprocess.PIPE,
        ).strip()

    def switch(self, *arguments):
        return subprocess.run(
            ["bash", str(SCRIPT), "--repo", str(self.repo), *arguments],
            env=self.environment, text=True, capture_output=True, check=False,
        )

    def fixture_executable(self, name, source):
        target = self.bin / name
        target.write_text("#!/bin/sh\n" + source, encoding="utf-8")
        target.chmod(0o755)

    def fixture_socket(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        listener = socket.socket(socket.AF_UNIX)
        self.addCleanup(listener.close)
        listener.bind(str(path))

    def test_discovers_loaded_key_in_an_agent_outside_shell_environment(self):
        # These files are placeholders consumed by fake executables, not keys.
        (self.ssh / "wdrag").write_text("fixture", encoding="utf-8")
        (self.ssh / "wdrag.pub").write_text("fixture", encoding="utf-8")
        empty = self.runtime / "openssh_agent"
        selected = self.ssh / "agent/s.test.agent.loaded"
        self.fixture_socket(empty)
        self.fixture_socket(selected)
        self.environment["SSH_AUTH_SOCK"] = str(empty)
        self.fixture_executable("ssh-keygen", "printf '256 SHA256:SELECTED fixture (ED25519)\\n'\n")
        self.fixture_executable("ssh-add", """
case "$SSH_AUTH_SOCK" in
    */s.test.agent.loaded) printf '256 SHA256:SELECTED fixture (ED25519)\\n' ;;
    */openssh_agent) exit 1 ;;
    *) exit 2 ;;
esac
""")
        result = self.switch("wdrag")
        self.assertEqual(result.returncode, 0, result.stderr)
        command = shlex.split(self.git("config", "--local", "core.sshCommand"))
        self.assertEqual(command[0], "ssh")
        self.assertIn(f"IdentityAgent={selected}", command)
        self.assertIn(str(self.ssh / "wdrag"), command)
        self.assertIn("IdentitiesOnly=yes", command)
        self.assertEqual(self.git("remote", "get-url", "origin"), "git@github.com:wDrag/sql-notebook.git")

    def test_missing_identity_preserves_remote_and_existing_override(self):
        self.git("config", "--local", "core.sshCommand", "original override")
        result = self.switch("missing")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SSH key not found", result.stderr)
        self.assertEqual(self.git("config", "--local", "core.sshCommand"), "original override")
        self.assertEqual(self.git("remote", "get-url", "origin"), "https://github.com/wDrag/sql-notebook.git")

    def test_https_switch_preserves_project_and_removes_local_overrides(self):
        self.git("remote", "set-url", "origin", "git@github.com:wDrag/sql-notebook.git")
        self.git("config", "--local", "core.sshCommand", "ssh fixture")
        self.git("config", "--local", "ssh.variant", "ssh")
        result = self.switch("--https")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("remote", "get-url", "origin"), "https://github.com/wDrag/sql-notebook.git")
        settings = self.git("config", "--local", "--list")
        self.assertNotIn("core.sshcommand=", settings.lower())
        self.assertNotIn("ssh.variant=", settings.lower())


if __name__ == "__main__":
    unittest.main()
