"""Exercise real CLI behavior in-process so numerical coverage includes entrypoints."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pytest

from bcla.__main__ import main


@pytest.mark.parametrize(
    "arguments",
    [
        ["--model", "linear"],
        ["--model", "all", "--selection", "in-sample"],
        ["--model", "all"],
        ["--model", "linear", "--bootstrap-samples", "20"],
    ],
)
def test_real_cli_synthetic_modes(
    arguments: list[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bcla", "--cycles", "50", *arguments])
    try:
        main()
        output = capsys.readouterr().out
        assert "Model" in output
        assert "Saved bcla_demo.png" in output
        assert (tmp_path / "bcla_demo.png").is_file()
    finally:
        plt.close("all")


@pytest.mark.parametrize(
    "arguments",
    [
        ["--bootstrap-samples", "1"],
        ["--validation-fraction", "0"],
        ["--cycles", "2", "--model", "all"],
    ],
)
def test_cli_rejects_unsupported_requests(
    arguments: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "argv", ["bcla", *arguments])
    with pytest.raises(SystemExit) as exception:
        main()
    assert exception.value.code == 2


def test_cli_csv_and_bootstrap_reports_censoring(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "cell.csv"
    path.write_text(
        "cycle,capacity\n"
        + "".join(
            f"{i * 100},{1.0 - i * 0.001 + (0.0002 if i % 2 else -0.0002)}\n" for i in range(10)
        )
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "bcla",
            "--model",
            "linear",
            "--csv",
            str(path),
            "--no-normalize",
            "--bootstrap-samples",
            "20",
        ],
    )
    try:
        main()
        assert "bounds withheld" in capsys.readouterr().out
    finally:
        plt.close("all")


def test_cli_bootstrap_rejects_constant_fit_residuals(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "cell.csv"
    path.write_text(
        "cycle,capacity\n" + "".join(f"{i * 100},{1.0 - i * 0.03}\n" for i in range(10))
    )
    monkeypatch.setattr(
        sys, "argv", ["bcla", "--model", "linear", "--csv", str(path), "--bootstrap-samples", "20"]
    )
    with pytest.raises(SystemExit) as exception:
        main()
    assert exception.value.code == 2


def test_module_entrypoint_help(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["bcla", "--help"])
    monkeypatch.delitem(sys.modules, "bcla.__main__", raising=False)
    with pytest.raises(SystemExit) as exception:
        runpy.run_module("bcla", run_name="__main__")
    assert exception.value.code == 0
