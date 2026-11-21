"""Adversarial regressions for scientific and input-contract hardening.

Tests are deterministic, offline, and designed to fail against the v0.3.0
baseline where the corresponding defect was observed by source inspection.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from bcla import core
from bcla.__main__ import main
from bcla.datasets import load_cycle_data, load_cycle_data_long_form


def test_eol_linear_root_is_not_limited_by_a_discrete_grid() -> None:
    cycles = np.array([0.0, 1.0])
    capacity = 1.0 - 0.17 * cycles
    fitted = core.FitResult(
        model_name="linear",
        params={"Q0": 1.0, "k": 0.17},
        pcov=np.eye(2),
        rmse=0.0,
        r_squared=1.0,
        cycles=cycles,
        observed=capacity,
        predicted=capacity.copy(),
    )
    assert fitted.eol_cycle(0.8) == pytest.approx(0.2 / 0.17, abs=1e-10)


def test_eol_stays_censored_beyond_three_times_observed_cycles() -> None:
    cycles = np.array([0.0, 1.0])
    capacity = 1.0 - 0.01 * cycles
    fitted = core.FitResult(
        model_name="linear",
        params={"Q0": 1.0, "k": 0.01},
        pcov=np.eye(2),
        rmse=0.0,
        r_squared=1.0,
        cycles=cycles,
        observed=capacity,
        predicted=capacity.copy(),
    )
    assert fitted.eol_cycle(0.8) is None


def test_logarithmic_model_uses_stable_near_zero_logarithm() -> None:
    actual = core._logarithmic(np.array([1.0]), 0.0, 1.0, 1e-16)
    assert actual[0] == pytest.approx(-1e-16, abs=1e-25)


def test_raw_ampere_hours_outside_normalised_bounds_get_actionable_error() -> None:
    x = np.arange(10, dtype=float) * 100.0
    raw_ah = 3.1 - 0.0002 * x
    with pytest.raises(ValueError, match="normalis"):
        core.fit_capacity_fade(x, raw_ah, model="linear")


def test_temporal_holdout_rejects_multidimensional_trajectories() -> None:
    cycles = np.arange(10, dtype=float).reshape(2, 5)
    capacity = 1.0 - 0.001 * cycles
    with pytest.raises(ValueError, match="one-dimensional"):
        core.temporal_holdout_scores(cycles, capacity)


def test_solver_rejects_insufficient_distinct_cycles() -> None:
    with pytest.raises(ValueError, match="distinct cycle"):
        core.fit_capacity_fade([0, 0, 0, 1, 1], [1, 1, 1, 0.98, 0.98], model="power_law")


def test_solver_rejects_unrepresentable_covariance(monkeypatch: pytest.MonkeyPatch) -> None:
    def invalid_covariance(*args: object, **kwargs: object) -> tuple[np.ndarray, np.ndarray]:
        return np.array([1.0, 0.001]), np.full((2, 2), np.inf)

    monkeypatch.setattr(core, "curve_fit", invalid_covariance)
    with pytest.raises(ValueError, match="covariance"):
        core.fit_capacity_fade(np.arange(6), 1.0 - 0.001 * np.arange(6), model="linear")


def test_solver_rejects_nonfinite_estimates(monkeypatch: pytest.MonkeyPatch) -> None:
    def invalid_estimate(*args: object, **kwargs: object) -> tuple[np.ndarray, np.ndarray]:
        return np.array([np.nan, 0.001]), np.eye(2)

    monkeypatch.setattr(core, "curve_fit", invalid_estimate)
    with pytest.raises(ValueError, match="non-finite"):
        core.fit_capacity_fade(np.arange(6), 1.0 - 0.001 * np.arange(6), model="linear")


def test_simple_csv_rejects_negative_physical_measurements(tmp_path: Path) -> None:
    path = tmp_path / "negative.csv"
    path.write_text("cycle,capacity\n0,1.0\n1,-0.1\n")
    with pytest.raises(ValueError, match="Negative capacity"):
        load_cycle_data(path, normalize=False)
    path.write_text("cycle,capacity\n-1,1.0\n1,0.9\n")
    with pytest.raises(ValueError, match="Negative cycle"):
        load_cycle_data(path)


def test_long_form_csv_rejects_negative_capacity_without_normalization(tmp_path: Path) -> None:
    path = tmp_path / "negative.csv"
    path.write_text("cell_id,cycle,capacity\ncell-a,0,-1.0\n")
    with pytest.raises(ValueError, match="Negative required value"):
        load_cycle_data_long_form(path, normalize=False)


def test_cli_invalid_csv_raises_usage_error_without_traceback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing = tmp_path / "does-not-exist.csv"
    monkeypatch.setattr(sys, "argv", ["bcla", "--csv", str(missing), "--model", "linear"])
    with pytest.raises(SystemExit) as err:
        main()
    assert err.value.code == 2
