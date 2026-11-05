"""Numerical domains, chronology and physically interpretable degradation cases."""

from __future__ import annotations

from dataclasses import replace
from typing import Literal, cast

import numpy as np
import pytest

from bcla import core


def _linear_fit() -> core.FitResult:
    x = np.arange(10, dtype=float) * 100.0
    return core.fit_capacity_fade(x, 1.0 - 0.0003 * x, model="linear", q0_guess=1.0)


def test_linear_physical_projection_and_model_diagnostics() -> None:
    fitted = _linear_fit()
    assert fitted.project(1000.0) == pytest.approx(0.7, abs=1e-8)
    assert fitted.eol_cycle() == pytest.approx(0.2 / 0.0003, abs=0.03)
    assert "Model" in fitted.summary()
    assert "R-squared" in fitted.summary(ascii_only=True)
    result = core.best_model({"linear": fitted}, criterion="r_squared")
    assert result[0] == "linear"
    with pytest.raises(ValueError, match="criterion"):
        core.best_model({"linear": fitted}, cast(Literal["rmse", "r_squared"], "invalid"))
    with pytest.raises(ValueError, match="Unknown model"):
        core.fit_capacity_fade([0, 1, 2], [1.0, 0.9, 0.8], model="unknown")


@pytest.mark.parametrize(
    ("cycles", "capacity", "message"),
    [
        ([0, 1, 2], [1, 1], "same number"),
        ([0, 1, 2], [1, 1, 1], "at least six"),
        ([0, 1, 2, 3, 4, np.inf], [1] * 6, "finite"),
        ([-1, 0, 1, 2, 3, 4], [1] * 6, "non-negative"),
        ([0, 0, 1, 1, 2, 2], [1] * 6, "distinct cycle"),
    ],
)
def test_temporal_domain_checks(cycles: list[float], capacity: list[float], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        core.temporal_holdout_scores(cycles, capacity)


@pytest.mark.parametrize("fraction", [0.0, 1.0, np.nan, 0.99])
def test_temporal_invalid_or_insufficient_training_fraction(fraction: float) -> None:
    with pytest.raises(ValueError, match="validation_fraction"):
        core.temporal_holdout_scores(np.arange(10), np.linspace(1.0, 0.9, 10), fraction)


def test_temporal_split_keeps_repeated_cycle_groups_and_distinct_windows() -> None:
    x = np.array([0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5], dtype=float)
    y = 1.0 - 0.01 * x
    scores = core.temporal_holdout_scores(x, y)
    for score in scores.values():
        assert score.train_size == 4
        assert score.validation_size == 8
        assert score.split_cycle == 4.0
    x = np.array([0, 0, 0, 0, 1, 2, 3, 4, 5], dtype=float)
    with pytest.raises(ValueError, match="distinct training"):
        core.temporal_holdout_scores(x, 1.0 - 0.01 * x, validation_fraction=0.4)


def test_r_squared_selection_and_invalid_criterion() -> None:
    x = np.arange(10, dtype=float) * 100.0
    y = 1.0 - 0.0003 * x
    selected = core.select_model_by_validation(x, y, criterion="r_squared")
    assert selected.validation_score.r_squared > 0.999
    with pytest.raises(ValueError, match="criterion"):
        core.select_model_by_validation(x, y, criterion=cast(Literal["rmse", "r_squared"], "bad"))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("eol_fraction", 0.0, "eol_fraction"),
        ("confidence", 0.0, "confidence"),
        ("samples", 19, "samples"),
        ("current_cycle", np.nan, "finite"),
        ("current_cycle", -1.0, "non-negative"),
    ],
)
def test_bootstrap_argument_domains(field: str, value: float, message: str) -> None:
    fitted = _linear_fit()
    if field == "eol_fraction":

        def call() -> core.LifeProjectionInterval:
            return core.bootstrap_life_projection(fitted, eol_fraction=value, samples=20)
    elif field == "confidence":

        def call() -> core.LifeProjectionInterval:
            return core.bootstrap_life_projection(fitted, confidence=value, samples=20)
    elif field == "samples":

        def call() -> core.LifeProjectionInterval:
            return core.bootstrap_life_projection(fitted, samples=int(value))
    else:

        def call() -> core.LifeProjectionInterval:
            return core.bootstrap_life_projection(fitted, current_cycle=value, samples=20)

    with pytest.raises(ValueError, match=message):
        call()


def test_bootstrap_rejects_malformed_fit_results() -> None:
    fitted = _linear_fit()
    malformed = [
        (replace(fitted, model_name="unknown"), "Unknown"),
        (replace(fitted, cycles=np.array([])), "aligned"),
        (replace(fitted, observed=np.full(10, np.nan)), "finite"),
        (replace(fitted, cycles=-np.arange(10)), "non-negative"),
        (replace(fitted, cycles=np.zeros(10)), "distinct observations"),
    ]
    for result, message in malformed:
        with pytest.raises(ValueError, match=message):
            core.bootstrap_life_projection(result, samples=20)


def test_arrhenius_reference_and_temperature_ordering() -> None:
    assert core.arrhenius_acceleration_factor(25.0) == 1.0
    assert core.arrhenius_acceleration_factor(0.0) < 1.0
    assert core.arrhenius_acceleration_factor(50.0) > 1.0
    assert core.arrhenius_acceleration_factor(50.0, activation_ev=0.0) == 1.0
