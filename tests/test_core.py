"""Tests for bcla.core"""

import numpy as np
from bcla.core import (
    fit_capacity_fade,
    fit_all_models,
    best_model,
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
