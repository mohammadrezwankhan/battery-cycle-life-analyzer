import os
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _strict_cp1252_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp1252:strict"
    env["MPLBACKEND"] = "Agg"
    existing_path = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{PROJECT_ROOT}{os.pathsep}{existing_path}"
        if existing_path
        else str(PROJECT_ROOT)
    )
    return env


def test_cli_help_is_cp1252_safe(tmp_path):
    completed = subprocess.run(
        [sys.executable, "-m", "bcla", "--help"],
        cwd=tmp_path,
        env=_strict_cp1252_environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    output = completed.stdout.decode("cp1252", errors="strict")
    assert completed.returncode == 0, output
    assert "Battery Cycle-Life Analyzer" in output


def test_power_law_cli_is_cp1252_safe(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "bcla",
            "--cycles",
            "50",
            "--model",
            "power_law",
        ],
        cwd=tmp_path,
        env=_strict_cp1252_environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    output = completed.stdout.decode("cp1252", errors="strict")
    assert completed.returncode == 0, output
    assert "R-squared" in output
    assert "alpha" in output
    assert "beta" in output
    assert (tmp_path / "bcla_demo.png").is_file()
