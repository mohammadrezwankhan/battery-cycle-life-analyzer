"""Reject unrepresentable projections without changing ordinary model arithmetic."""

from __future__ import annotations

import unittest

import numpy as np

from bcla.core import FitResult, arrhenius_acceleration_factor


def make_fit(model: str, params: dict[str, float], last_cycle: float = 1000.0) -> FitResult:
    values = np.array([0.0, last_cycle], dtype=float)
    capacity = np.array([1.0, 0.9], dtype=float)
    return FitResult(
        model_name=model,
        params=params,
        pcov=np.eye(len(params)),
        rmse=0.0,
        r_squared=1.0,
        cycles=values,
        observed=capacity,
        predicted=capacity.copy(),
    )


class FiniteProjectionTests(unittest.TestCase):
    def test_power_law_projection_overflow_is_rejected(self) -> None:
        result = make_fit("power_law", {"Q0": 1.0, "α": 0.01, "β": 2.0})
        with self.assertRaisesRegex(ValueError, "finite"):
            result.project(1e308)

    def test_logarithmic_projection_overflow_is_rejected(self) -> None:
        result = make_fit("logarithmic", {"Q0": 1.0, "a": 0.01, "b": 1e5})
        with self.assertRaisesRegex(ValueError, "finite"):
            result.project(1e308)

    def test_eol_horizon_overflow_is_rejected(self) -> None:
        result = make_fit("linear", {"Q0": 1.0, "k": 0.0001}, last_cycle=1e308)
        with self.assertRaisesRegex(ValueError, "finite"):
            result.eol_cycle()

    def test_eol_prediction_overflow_is_rejected(self) -> None:
        result = make_fit("power_law", {"Q0": 1.0, "α": 0.01, "β": 2.0}, last_cycle=1e160)
        with self.assertRaisesRegex(ValueError, "finite"):
            result.eol_cycle()

    def test_finite_projection_keeps_negative_capacity(self) -> None:
        result = make_fit("linear", {"Q0": 1.0, "k": 0.0001})
        self.assertEqual(result.project(20000.0), -1.0)


class FiniteArrheniusTests(unittest.TestCase):
    def test_overflow_invalid_and_underflow_are_rejected(self) -> None:
        for temperature in (0.0, 25.0, 50.0):
            with (
                self.subTest(temperature=temperature),
                self.assertRaisesRegex(ValueError, "finite"),
            ):
                arrhenius_acceleration_factor(temperature, activation_ev=1e308)

    def test_absolute_zero_neighbor_underflow_is_rejected(self) -> None:
        temperature = float(np.nextafter(-273.15, np.inf))
        with self.assertRaisesRegex(ValueError, "positive"):
            arrhenius_acceleration_factor(temperature)

    def test_identity_and_reciprocal_for_normal_temperatures(self) -> None:
        for temperature in (0.0, 25.0, 50.0):
            with self.subTest(temperature=temperature):
                self.assertEqual(arrhenius_acceleration_factor(temperature, temperature), 1.0)
                forward = arrhenius_acceleration_factor(temperature)
                reverse = arrhenius_acceleration_factor(25.0, temperature)
                self.assertAlmostEqual(forward * reverse, 1.0, places=14)
