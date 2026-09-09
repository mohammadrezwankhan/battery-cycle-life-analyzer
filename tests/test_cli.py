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


def test_all_models_cli_uses_temporal_validation_by_default(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "bcla",
            "--cycles",
            "50",
            "--model",
            "all",
        ],
        cwd=tmp_path,
        env=_strict_cp1252_environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    output = completed.stdout.decode("cp1252", errors="strict")
    assert completed.returncode == 0, output
    assert "Selected model:" in output
    assert "held-out RMSE=" in output
    assert "validation points=10" in output
    assert (tmp_path / "bcla_demo.png").is_file()


def test_all_models_cli_reports_invalid_validation_before_fit_output(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "bcla",
            "--cycles",
            "5",
            "--model",
            "all",
        ],
        cwd=tmp_path,
        env=_strict_cp1252_environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    output = completed.stdout.decode("cp1252", errors="strict")
    assert completed.returncode == 2
    assert "cannot select a model" in output
    assert "at least six observations" in output
    assert "Model          :" not in output


def test_cli_reports_all_bootstrap_outcome_counts(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "bcla",
            "--cycles",
            "50",
            "--model",
            "linear",
            "--bootstrap-samples",
            "20",
        ],
        cwd=tmp_path,
        env=_strict_cp1252_environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    output = completed.stdout.decode("cp1252", errors="strict")
    assert completed.returncode == 0, output
    assert "Bootstrap replicates:" in output
    assert "successful=" in output
    assert "censored=" in output
    assert "failed=" in output
    assert "requested=20" in output


def test_bundled_quickstart_csv_produces_a_result(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "bcla",
            "--csv",
            str(PROJECT_ROOT / "data" / "quickstart.csv"),
            "--model",
            "all",
            "--bootstrap-samples",
            "20",
        ],
        cwd=tmp_path,
        env=_strict_cp1252_environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    output = completed.stdout.decode("cp1252", errors="strict")
    assert completed.returncode == 0, output
    assert "Selected model:" in output
    assert "held-out RMSE=" in output
    assert "requested=20" in output
    assert "Saved bcla_demo.png" in output
    image_path = tmp_path / "bcla_demo.png"
    assert image_path.is_file()
    assert image_path.stat().st_size > 1000
    assert image_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
