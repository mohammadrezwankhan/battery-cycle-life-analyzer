"""Tests for discharge equivalent-full-cycle integration."""

import numpy as np
import pytest

from bcla.datasets import equivalent_full_cycles


def test_equivalent_full_cycles_uses_clipped_trapezoidal_integration():
    time_s = np.array([0.0, 900.0, 1800.0, 2700.0])
    current_a = np.array([8.0, -8.0, 16.0, 0.0])

    efc = equivalent_full_cycles(time_s, current_a, 16.0)

    assert np.allclose(efc, np.array([0.0, 0.0625, 0.1875, 0.3125]))


def test_equivalent_full_cycles_handles_partial_interval_queries():
    efc = equivalent_full_cycles(
        [0.0, 900.0],
        [8.0, -8.0],
        16.0,
        query_time_s=[0.0, 450.0, 900.0],
    )

    assert np.allclose(efc, np.array([0.0, 0.046875, 0.0625]))


def test_equivalent_full_cycles_excludes_charging_current():
    efc = equivalent_full_cycles([0.0, 900.0], [-8.0, -4.0], 16.0)

    assert np.array_equal(efc, np.zeros(2))


def test_equivalent_full_cycles_accepts_scalar_query():
    efc = equivalent_full_cycles(
        [0.0, 900.0],
        [16.0, 16.0],
        16.0,
        query_time_s=450.0,
    )

    assert efc.shape == (1,)
    assert efc[0] == pytest.approx(0.125)


@pytest.mark.parametrize(
    ("time_s", "current_a", "nominal_capacity_ah", "match"),
    [
        ([[0.0, 1.0]], [1.0, 1.0], 1.0, "one-dimensional"),
        ([0.0, 1.0], [[1.0, 1.0]], 1.0, "one-dimensional"),
        ([0.0], [1.0], 1.0, "at least two"),
        ([0.0, 1.0], [1.0], 1.0, "same length"),
        ([0.0, np.nan], [1.0, 1.0], 1.0, "finite"),
        ([0.0, 1.0], [1.0, np.inf], 1.0, "finite"),
        ([-1.0, 0.0], [1.0, 1.0], 1.0, "non-negative"),
        ([0.0, 0.0], [1.0, 1.0], 1.0, "strictly increasing"),
        ([1.0, 0.0], [1.0, 1.0], 1.0, "strictly increasing"),
        ([0.0, 1.0], [1.0, 1.0], 0.0, "positive finite"),
        ([0.0, 1.0], [1.0, 1.0], np.inf, "positive finite"),
    ],
)
def test_equivalent_full_cycles_rejects_invalid_measurements(
    time_s, current_a, nominal_capacity_ah, match
):
    with pytest.raises(ValueError, match=match):
        equivalent_full_cycles(time_s, current_a, nominal_capacity_ah)


@pytest.mark.parametrize(
    "query_time_s",
    [[-1.0], [901.0], [np.nan], [[0.0, 1.0]]],
)
def test_equivalent_full_cycles_rejects_invalid_queries(query_time_s):
    with pytest.raises(ValueError):
        equivalent_full_cycles(
            [0.0, 900.0],
            [8.0, 0.0],
            16.0,
            query_time_s=query_time_s,
        )


def test_equivalent_full_cycles_allows_empty_query():
    efc = equivalent_full_cycles(
        [0.0, 900.0],
        [8.0, 0.0],
        16.0,
        query_time_s=[],
    )

    assert efc.size == 0


def test_equivalent_full_cycles_rejects_numerical_overflow():
    with pytest.raises(ValueError, match="non-finite"):
        equivalent_full_cycles(
            [0.0, 1e308],
            [1e308, 1e308],
            1.0,
        )
