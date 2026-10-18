"""Regression checks for invalid inputs at the public modeling boundary."""

import numpy as np
import pytest

from bcla.core import arrhenius_acceleration_factor, fit_capacity_fade


@pytest.mark.parametrize(
    ("cycles", "capacity", "message"),
    [
        ([0, 1, 2], [1], "same number"),
        ([0], [1, 0.9, 0.8], "same number"),
        ([], [], "non-empty"),
        ([[0, 1, 2]], [[1, 0.9, 0.8]], "one-dimensional"),
        ([-2, -1, 0], [1, 0.9, 0.8], "non-negative"),
        ([0, 1, np.inf], [1, 0.9, 0.8], "finite"),
        ([0, 1, 2], [1, np.nan, 0.8], "finite"),
    ],
)
def test_fit_rejects_invalid_observation_arrays(cycles, capacity, message):
    with pytest.raises(ValueError, match=message):
        fit_capacity_fade(cycles, capacity, model="linear")


@pytest.mark.parametrize("target", [-1, np.nan, np.inf, -np.inf])
def test_projection_rejects_invalid_cycle_coordinate(target):
    fitted = fit_capacity_fade([0, 100, 200], [1, 0.95, 0.9], model="linear")
    with pytest.raises(ValueError, match="finite and non-negative"):
        fitted.project(target)


@pytest.mark.parametrize("fraction", [0, 1, -0.2, 2, np.nan, np.inf])
def test_eol_rejects_invalid_fraction(fraction):
    fitted = fit_capacity_fade([0, 100, 200], [1, 0.95, 0.9], model="linear")
    with pytest.raises(ValueError, match="between 0 and 1"):
        fitted.eol_cycle(fraction)


@pytest.mark.parametrize("field", ["temperature_c", "reference_c", "activation_ev"])
@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_arrhenius_rejects_non_finite_inputs(field, value):
    arguments = {"temperature_c": 25.0, field: value}
    with pytest.raises(ValueError, match="finite"):
        arrhenius_acceleration_factor(**arguments)


@pytest.mark.parametrize("field", ["temperature_c", "reference_c"])
@pytest.mark.parametrize("value", [-273.15, -274.0])
def test_arrhenius_rejects_non_positive_kelvin_temperature(field, value):
    arguments = {"temperature_c": 25.0, field: value}
    with pytest.raises(ValueError, match="above absolute zero"):
        arrhenius_acceleration_factor(**arguments)
