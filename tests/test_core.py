"""Tests for bcla.core"""

import numpy as np
import pytest
import bcla.core as core
from bcla.core import (
    fit_capacity_fade,
    fit_all_models,
    best_model,
    bootstrap_life_projection,
    select_model_by_validation,
    temporal_holdout_scores,
    arrhenius_acceleration_factor,
)


def test_fit_linear_returns_reasonable_rmse():
    x = np.arange(1, 501, dtype=float)
    y = 1.0 - 0.0002 * x
    result = fit_capacity_fade(x, y, model="linear")
    assert result.rmse < 0.01
    assert abs(result.params["Q0"] - 1.0) < 0.05
    assert abs(result.params["k"] - 0.0002) < 0.0001


def test_fit_power_law_on_noisy_lfp():
    """Power law should fit noisy LFP-like data with reasonable RMSE."""
    x = np.arange(1, 1001, dtype=float)
    rng = np.random.default_rng(42)
    y = 1.0 - 0.01 * x ** 0.6 + rng.normal(0, 0.005, size=1000)
    result = fit_capacity_fade(x, y, model="power_law")
    assert result.rmse < 0.02
    assert result.r_squared > 0.95
    assert 0.8 < result.params["Q0"] < 1.2


def test_fit_all_models_returns_three():
    x = np.arange(1, 501, dtype=float)
    y = 1.0 - 0.0002 * x
    results = fit_all_models(x, y)
    assert set(results) == {"linear", "power_law", "logarithmic"}


def test_best_model_picks_lowest_rmse():
    x = np.arange(1, 501, dtype=float)
    y = 1.0 - 0.0002 * x
    results = fit_all_models(x, y)
    name, _ = best_model(results, criterion="rmse")
    # Linear and power-law (β=1) are equivalent for perfect line;
    # just verify RMSE is low for the chosen one
    assert results[name].rmse < 0.01


def test_temporal_holdout_selects_power_law_and_refits_all_data():
    x = np.arange(1, 501, dtype=float)
    y = 1.0 - 0.003 * x ** 0.7

    selection = select_model_by_validation(x[::-1], y[::-1])

    assert selection.model_name == "power_law"
    assert selection.validation_score.validation_size == 100
    assert selection.validation_score.train_size == 400
    assert selection.validation_score.rmse < 1e-6
    assert len(selection.fit.cycles) == len(x)
    assert np.all(np.diff(selection.fit.cycles) >= 0)


def test_temporal_holdout_scores_reject_invalid_split():
    x = np.arange(1, 7, dtype=float)
    y = 1.0 - 0.001 * x

    try:
        temporal_holdout_scores(x, y, validation_fraction=0.5)
    except ValueError as exc:
        assert "training observations" in str(exc)
    else:
        raise AssertionError("expected an invalid temporal split to fail")


def test_temporal_holdout_rejects_negative_cycles():
    x = np.array([-1, 1, 2, 3, 4, 5, 6], dtype=float)
    y = 1.0 - 0.001 * x

    with pytest.raises(ValueError, match="non-negative"):
        temporal_holdout_scores(x, y)


def test_temporal_holdout_requires_distinct_cycle_values():
    x = np.array([1, 1, 2, 3, 4, 5], dtype=float)
    y = 1.0 - 0.001 * x

    with pytest.raises(ValueError, match="distinct cycle values"):
        temporal_holdout_scores(x, y)


def test_temporal_holdout_keeps_duplicate_cycles_on_one_side():
    x = np.array([1, 2, 3, 4, 5, 6, 6, 7], dtype=float)
    y = 1.0 - 0.001 * x

    scores = temporal_holdout_scores(x, y, validation_fraction=0.25)

    assert all(score.train_size == 5 for score in scores.values())
    assert all(score.validation_size == 3 for score in scores.values())
    assert all(score.split_cycle == 6 for score in scores.values())


def test_r_squared_selection_rejects_constant_validation_window():
    x = np.arange(1, 11, dtype=float)
    y = np.concatenate([1.0 - 0.01 * x[:8], np.array([0.9, 0.9])])

    try:
        select_model_by_validation(x, y, criterion="r_squared")
    except ValueError as exc:
        assert "constant validation window" in str(exc)
    else:
        raise AssertionError("expected undefined validation R-squared to fail")


def test_bootstrap_life_projection_returns_reproducible_eol_rul_interval():
    x = np.arange(1, 501, dtype=float)
    rng = np.random.default_rng(7)
    y = 1.0 - 0.0004 * x + rng.normal(0.0, 0.002, size=x.size)
    fitted = fit_capacity_fade(x, y, model="linear")

    interval = bootstrap_life_projection(
        fitted,
        current_cycle=400.0,
        confidence=0.9,
        samples=60,
        random_state=42,
    )

    assert interval.successful_samples == 60
    assert interval.censored_samples == 0
    assert interval.failed_samples == 0
    assert interval.eol_estimate is not None
    assert interval.eol_lower is not None
    assert interval.eol_upper is not None
    assert interval.eol_lower <= interval.eol_estimate <= interval.eol_upper
    assert interval.rul_estimate is not None
    assert interval.rul_lower is not None
    assert interval.rul_upper is not None
    assert interval.rul_lower <= interval.rul_estimate <= interval.rul_upper


def test_bootstrap_withholds_interval_when_projection_is_censored():
    x = np.arange(1, 101, dtype=float)
    rng = np.random.default_rng(4)
    y = 1.0 + rng.normal(0.0, 0.001, size=x.size)
    fitted = fit_capacity_fade(x, y, model="linear")

    interval = bootstrap_life_projection(
        fitted,
        samples=20,
        random_state=1,
    )

    assert interval.eol_estimate is None
    assert interval.successful_samples == 0
    assert interval.censored_samples == 20
    assert interval.eol_lower is None
    assert interval.eol_upper is None
    assert interval.rul_lower is None
    assert interval.rul_upper is None


def test_bootstrap_withholds_interval_after_partial_right_censoring():
    x = np.arange(1, 501, dtype=float)
    rng = np.random.default_rng(0)
    y = 1.0 - 0.00014 * x + rng.normal(0.0, 0.03, size=x.size)
    fitted = fit_capacity_fade(x, y, model="linear")

    interval = bootstrap_life_projection(
        fitted,
        samples=100,
        random_state=0,
    )

    assert interval.successful_samples > 0
    assert interval.censored_samples > 0
    assert interval.failed_samples == 0
    assert (
        interval.successful_samples
        + interval.censored_samples
        + interval.failed_samples
        == interval.requested_samples
    )
    assert interval.eol_lower is None
    assert interval.eol_upper is None
    assert interval.rul_lower is None
    assert interval.rul_upper is None


def test_bootstrap_rejects_zero_residual_variance():
    x = np.arange(1, 101, dtype=float)
    y = 1.0 - 0.001 * x
    fitted = fit_capacity_fade(x, y, model="linear")

    with pytest.raises(ValueError, match="positive residual variance"):
        bootstrap_life_projection(fitted, samples=20, random_state=1)


def test_bootstrap_withholds_interval_after_any_fit_failure(monkeypatch):
    x = np.arange(1, 501, dtype=float)
    rng = np.random.default_rng(7)
    y = 1.0 - 0.0004 * x + rng.normal(0.0, 0.002, size=x.size)
    fitted = fit_capacity_fade(x, y, model="linear")
    original_fit = core.fit_capacity_fade
    calls = 0

    def flaky_fit(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("simulated numerical fit failure")
        return original_fit(*args, **kwargs)

    monkeypatch.setattr(core, "fit_capacity_fade", flaky_fit)
    interval = bootstrap_life_projection(
        fitted,
        samples=20,
        random_state=42,
    )

    assert interval.failed_samples == 1
    assert (
        interval.successful_samples
        + interval.censored_samples
        + interval.failed_samples
        == interval.requested_samples
    )
    assert interval.eol_lower is None
    assert interval.eol_upper is None
    assert interval.rul_lower is None
    assert interval.rul_upper is None


def test_eol_cycle_returns_sensible():
    x = np.arange(1, 1001, dtype=float)
    y = 1.0 - 0.0002 * x  # reaches 0.8 at exactly cycle 1000
    result = fit_capacity_fade(x, y, model="linear")
    assert result.r_squared > 0.99
    eol = result.eol_cycle(0.8)
    assert eol is not None
    assert 900 <= eol <= 1100  # should be near 1000


def test_eol_linear_reaches_threshold():
    """Cycles beyond data: linear model should hit EOL ≈ 1000."""
    x = np.arange(1, 801, dtype=float)
    y = 1.0 - 0.0002 * x
    result = fit_capacity_fade(x, y, model="linear")
    eol = result.eol_cycle(0.8)
    assert eol is not None
    assert 900 <= eol <= 1200


def test_arrhenius_acceleration():
    af_25 = arrhenius_acceleration_factor(25.0)
    af_45 = arrhenius_acceleration_factor(45.0)
    assert abs(af_25 - 1.0) < 1e-6
    assert af_45 > 1.5
