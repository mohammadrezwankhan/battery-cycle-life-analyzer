"""Exercise the Python 3.9 tool-cache fallback without trusting bad downloads."""

from __future__ import annotations

import os
import subprocess
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

    @staticmethod
    def run_fallback(root: Path) -> subprocess.CompletedProcess[str]:
        bindir = root / "bin"
        bindir.mkdir()
        gh = bindir / "gh"
        gh.write_text('#!/bin/sh\ntouch "${RUNNER_TEMP}/called"\nprintf corrupt\n')
        gh.chmod(0o755)
        curl = bindir / "curl"
        curl.write_text("#!/bin/sh\nexit 1\n")
        curl.chmod(0o755)
        env = dict(os.environ, RUNNER_TEMP=str(root), RUNNER_TOOL_CACHE=str(root / "tools"))
        env["PATH"] = f"{bindir}:{env['PATH']}"
        script = Path(__file__).resolve().parents[1] / "scripts/bootstrap-python39.sh"
        return subprocess.run(  # noqa: S603 -- fixed shell and repository script
            ["/bin/bash", str(script)], env=env, capture_output=True, text=True, check=False
        )


if __name__ == "__main__":
    unittest.main()
