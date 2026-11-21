"""Second-pass adversarial regressions from independent audit-package review.

Each case reproduces a previously untested input or scientific reporting
contract; none requires measured Oxford data or network access.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from bcla import core
from bcla.datasets import load_cycle_data_long_form, load_duty_cycle_history


def test_long_form_rejects_incompatible_timestamp_awareness(tmp_path: Path) -> None:
    """A mixed naive/aware series must not raise an unhandled TypeError."""
    path = tmp_path / "mixed-clock.csv"
    path.write_text(
        "cell_id,cycle,capacity,timestamp_iso\n"
        "A,0,1.0,2026-07-01T00:00:00\n"
        "A,1,0.99,2026-07-01T01:00:00+00:00\n"
    )
    with pytest.raises(ValueError, match="timezone"):
        load_cycle_data_long_form(path)


def test_history_rejects_mixed_timestamp_awareness_in_interval(tmp_path: Path) -> None:
    """Interval ordering must have an explicit timezone contract."""
    path = tmp_path / "mixed-interval.csv"
    path.write_text(
        "cell_id,experiment_id,interval_start,interval_end\n"
        "A,experiment,2026-07-01T00:00:00,2026-07-01T01:00:00Z\n"
    )
    with pytest.raises(ValueError, match="timezone"):
        load_duty_cycle_history(path)


def test_history_rejects_mixed_timestamp_awareness_across_rows(tmp_path: Path) -> None:
    """One interval per row is not enough: min/max spans must be comparable."""
    path = tmp_path / "mixed-rows.csv"
    path.write_text(
        "cell_id,experiment_id,interval_start,interval_end\n"
        "A,experiment,2026-07-01T00:00:00,2026-07-01T01:00:00\n"
        "A,experiment,2026-07-01T02:00:00+00:00,2026-07-01T03:00:00+00:00\n"
    )
    with pytest.raises(ValueError, match="timezone"):
        load_duty_cycle_history(path)


def test_long_form_normalization_rejects_overflow(tmp_path: Path) -> None:
    """Finite source numbers can produce infinite normalized retention."""
    path = tmp_path / "overflow.csv"
    path.write_text(
        "cell_id,cycle,capacity\n"
        "A,0,0.000001\n"
        "A,1,1e308\n"
    )
    with pytest.raises(ValueError, match="non-finite"):
        load_cycle_data_long_form(path)


def test_temporal_validation_rejects_negative_future_capacity() -> None:
    """Held-out physically impossible observations cannot be scored."""
    cycles = np.arange(10, dtype=float)
    retention = 1.0 - 0.01 * cycles
    retention[-1] = -0.3
    with pytest.raises(ValueError, match="non-negative"):
        core.temporal_holdout_scores(cycles, retention)


def test_solver_reports_active_q0_and_beta_bounds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A bound-limited fit is not the same as a freely identified exponent."""
    def fitted_at_bounds(
        *_args: object, **_kwargs: object
    ) -> tuple[np.ndarray, np.ndarray]:
        return np.array([1.5, 0.001, 2.0]), np.eye(3)

    monkeypatch.setattr(core, "curve_fit", fitted_at_bounds)
    cycles = np.arange(8, dtype=float)
    retention = 1.0 - 0.001 * cycles
    result = core.fit_capacity_fade(cycles, retention, model="power_law")
    assert "Q0 (upper)" in result.active_bounds
    assert "β (upper)" in result.active_bounds
    assert "Bound-limited parameters" in result.summary()


def test_nonboundary_fit_has_no_bound_limited_diagnostic() -> None:
    x = np.arange(1, 100, dtype=float)
    y = 1.0 - 0.01 * x**0.6
    fit = core.fit_capacity_fade(x, y, model="power_law")
    assert fit.active_bounds == ()


def test_invalid_manual_eol_fit_does_not_claim_no_crossing() -> None:
    """An increasing-capacity manual FitResult violates the fade-model contract."""
    cycles = np.array([0.0, 1.0])
    observed = np.array([1.0, 1.1])
    invalid = core.FitResult(
        model_name="linear", params={"Q0": 1.0, "k": -0.1},
        pcov=np.eye(2), rmse=0.0, r_squared=1.0,
        cycles=cycles, observed=observed, predicted=observed.copy(),
    )
    with pytest.raises(ValueError, match="degradation parameters"):
        invalid.eol_cycle()


def test_lower_fit_bounds_are_reported_without_non_ascii_cli_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fitted_at_lower_bounds(
        *_args: object, **_kwargs: object
    ) -> tuple[np.ndarray, np.ndarray]:
        return np.array([0.5, 0.001, 0.1]), np.eye(3)

    monkeypatch.setattr(core, "curve_fit", fitted_at_lower_bounds)
    cycles = np.arange(8, dtype=float)
    retention = 0.75 - 0.001 * cycles
    result = core.fit_capacity_fade(cycles, retention, model="power_law")
    assert "Q0 (lower)" in result.active_bounds
    assert "β (lower)" in result.active_bounds
    assert "beta (lower)" in result.summary(ascii_only=True)
    assert "β" not in result.summary(ascii_only=True)
