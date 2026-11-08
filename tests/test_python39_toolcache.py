"""Exercise the Python 3.9 tool-cache fallback without trusting bad downloads."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


@unittest.skipUnless(os.name == "posix", "The hosted Python fallback runs on Linux")
class Python39FallbackTests(unittest.TestCase):
    """A cache hit is preserved and unverified bytes are never extracted."""

    def test_existing_cache_needs_no_download(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "tools/Python/3.9.25/x64.complete"
            marker.parent.mkdir(parents=True)
            marker.write_text("")
            result = self.run_fallback(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(marker.exists())
            self.assertFalse((root / "called").exists())

    def test_corrupt_download_is_rejected_before_install(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.run_fallback(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((root / "called").exists())
            self.assertFalse((root / "tools/Python/3.9.25/x64.complete").exists())
            self.assertFalse(list(root.glob("python39.*/extracted")))

    def test_unsupported_platforms_need_no_download(self) -> None:
        for platform in (
            ("Darwin", "x86_64", "missing"),
            ("Darwin", "x86_64", "ubuntu 24.04"),
            ("Linux", "aarch64", "ubuntu 24.04"),
            ("Linux", "x86_64", "ubuntu 22.04"),
            ("Linux", "x86_64", "debian 12"),
            ("Linux", "x86_64", "missing"),
            ("Linux", "x86_64", "incomplete"),
        ):
            with self.subTest(platform=platform), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                result = self.run_fallback(root, *platform)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse((root / "called").exists())
                self.assertFalse((root / "tools").exists())

    @staticmethod
    def run_fallback(
        root: Path,
        system: str = "Linux",
        machine: str = "x86_64",
        release: str = "ubuntu 24.04",
    ) -> subprocess.CompletedProcess[str]:
        bindir = root / "bin"
        bindir.mkdir()
        gh = bindir / "gh"
        gh.write_text('#!/bin/sh\ntouch "${RUNNER_TEMP}/called"\nprintf corrupt\n')
        gh.chmod(0o755)
        curl = bindir / "curl"
        curl.write_text("#!/bin/sh\nexit 1\n")
        curl.chmod(0o755)
        env = dict(os.environ, RUNNER_TEMP=str(root), RUNNER_TOOL_CACHE=str(root / "tools"))
        env.update(
            FIXTURE_SYSTEM=system,
            FIXTURE_MACHINE=machine,
            FIXTURE_RELEASE=release,
            FIXTURE_PYTHON=sys.executable,
        )
        env["PATH"] = f"{bindir}:{env['PATH']}"
        script = Path(__file__).resolve().parents[1] / "scripts/bootstrap-python39.sh"
        # Mock only host metadata and GNU command adapters. The real bootstrap
        # still chooses whether to download, checks the digest, and extracts.
        harness = r'''
uname() {
  case "$1" in
    -s) printf '%s\n' "$FIXTURE_SYSTEM" ;;
    -m) printf '%s\n' "$FIXTURE_MACHINE" ;;
    *) return 1 ;;
  esac
}
function .() {
  [[ "$1" == /etc/os-release ]] || return 1
  unset ID VERSION_ID
  case "$FIXTURE_RELEASE" in
    missing) return 1 ;;
    incomplete) ID=ubuntu ;;
    *) read -r ID VERSION_ID <<< "$FIXTURE_RELEASE" ;;
  esac
}
timeout() { [[ "$1" == 120s ]] || return 1; shift; "$@"; }
sha256sum() {
  [[ "$1" == --check ]] || return 1
  "$FIXTURE_PYTHON" -c 'import hashlib, pathlib, sys
expected, filename = sys.stdin.readline().strip().split("  ", 1)
sys.exit(hashlib.sha256(pathlib.Path(filename).read_bytes()).hexdigest() != expected)'
}
builtin source "$1"
'''
        return subprocess.run(  # noqa: S603 -- fixed shell and repository script
            ["/bin/bash", "-c", harness, "--", str(script)],
            env=env, capture_output=True, text=True, check=False
        )


if __name__ == "__main__":
    unittest.main()
