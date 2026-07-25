"""
core — Degradation models and curve fitting for battery cycle‑life data.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Literal, Optional

import numpy as np
from scipy.optimize import curve_fit


# ── Models (curve_fit convention: x first, then parameters) ──────────────


def _linear(cycle: np.ndarray, q0: float, k: float) -> np.ndarray:
    """Q(cycle) = Q0 - k * cycle   (k > 0 → capacity fade)"""
    return q0 - k * cycle


def _power_law(cycle: np.ndarray, q0: float, alpha: float,
               beta: float) -> np.ndarray:
    """Q(cycle) = Q0 - α * cycle^β  (β near 0.5 → diffusion‑limited)"""
    return q0 - alpha * cycle ** beta


def _logarithmic(cycle: np.ndarray, q0: float, a: float,
                 b: float) -> np.ndarray:
    """Q(cycle) = Q0 - a * ln(1 + b * cycle)"""
    return q0 - a * np.log(1.0 + b * cycle)


# Each entry: (callable, parameter_names, bounds_lower_upper)
MODEL_REGISTRY: dict[str, tuple] = {
    "linear":       (_linear,       ["Q0", "k"],       [[0.5, 1.5], [0.0, 1.0]]),
    "power_law":    (_power_law,    ["Q0", "α", "β"],  [[0.5, 1.5], [0.0, 5.0], [0.1, 2.0]]),
    "logarithmic":  (_logarithmic,  ["Q0", "a", "b"],  [[0.5, 1.5], [0.0, 1.0], [0.0, 1e5]]),
}


def _model_func(name: str):
    return MODEL_REGISTRY[name][0]


def _model_pnames(name: str):
    return MODEL_REGISTRY[name][1]


def _model_bounds(name: str):
    return MODEL_REGISTRY[name][2]


@dataclass
class FitResult:
    """Result of fitting a degradation model to cycle‑data."""
    model_name: str
    params: dict[str, float]
    pcov: np.ndarray
    rmse: float
    r_squared: float
    cycles: np.ndarray
    observed: np.ndarray
    predicted: np.ndarray

    def project(self, target_cycles: int) -> float:
        """Return predicted normalised capacity at *target_cycles*."""
        func = _model_func(self.model_name)
        p0 = [self.params[n] for n in _model_pnames(self.model_name)]
        return float(func(np.array([target_cycles]), *p0))

    def eol_cycle(self, eol_fraction: float = 0.8) -> Optional[float]:
        """
        Cycle number where capacity drops to *eol_fraction* of initial.

        Returns None if the model never reaches the threshold within
        a reasonable extrapolation (3× the data range).
        """
        func = _model_func(self.model_name)
        pnames = _model_pnames(self.model_name)
        p0 = [self.params[n] for n in pnames]
        max_cycle = float(self.cycles.max()) * 3.0
        q0 = self.params["Q0"]

        candidates = np.linspace(0, max_cycle, 100_000)
        pred = func(candidates, *p0)
        idx = np.where(pred <= q0 * eol_fraction)[0]
        if len(idx) == 0:
            return None
        return float(candidates[idx[0]])

    def summary(self, *, ascii_only: bool = False) -> str:
        """Return a multi-line summary, optionally safe for legacy terminals."""
        score_label = "R-squared" if ascii_only else "R²"
        parameter_names = {"α": "alpha", "β": "beta"} if ascii_only else {}
        lines = [
            f"Model          : {self.model_name}",
            f"RMSE           : {self.rmse:.5f}",
            f"{score_label:<15}: {self.r_squared:.4f}",
        ]
        for k, v in self.params.items():
            display_name = parameter_names.get(k, k)
            lines.append(f"  {display_name:<15s}: {v:.6f}")
        return "\n".join(lines)


# ── Fitting ─────────────────────────────────────────────────────────────

def fit_capacity_fade(cycles: np.ndarray,
                      capacity: np.ndarray,
                      model: str = "power_law",
                      q0_guess: Optional[float] = None
                      ) -> FitResult:
    """
    Fit a degradation model to cycle‑life data.

    Parameters
    ----------
    cycles : (N,) array of cycle indices.
    capacity : (N,) normalised capacity values (e.g. Q/Q₀).
    model : one of "linear", "power_law", "logarithmic".
    q0_guess : optional initial Q0; defaults to max(capacity).

    Returns
    -------
    FitResult with observed, predicted, and diagnostics.
    """
    if model not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model '{model}'. Choose from {list(MODEL_REGISTRY)}")

    func = _model_func(model)
    pnames = _model_pnames(model)
    bounds_list = _model_bounds(model)

    x = np.asarray(cycles, dtype=float).ravel()
    y = np.asarray(capacity, dtype=float).ravel()

    if q0_guess is None:
        q0_guess = float(y.max())

    # Build initial guesses
    p0_map: dict[str, float] = {"Q0": q0_guess}
    if model == "linear":
        est_k = max(0.0, (y[0] - y[-1]) / (x[-1] - x[0] + 1e-6))
        p0_map["k"] = max(est_k, 1e-8)
    elif model == "power_law":
        p0_map["α"] = 0.01
        p0_map["β"] = 0.6
    elif model == "logarithmic":
        p0_map["a"] = 0.02
        p0_map["b"] = 0.1

    p0 = [p0_map[n] for n in pnames]
    bounds = ([b[0] for b in bounds_list], [b[1] for b in bounds_list])

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        popt, pcov = curve_fit(func, x, y, p0=p0, bounds=bounds, maxfev=50_000)

    predicted = func(x, *popt)
    residuals = y - predicted
    rmse = float(np.sqrt(np.mean(residuals ** 2)))
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_sq = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    params = dict(zip(pnames, popt))
    return FitResult(
        model_name=model,
        params=params,
        pcov=pcov,
        rmse=rmse,
        r_squared=r_sq,
        cycles=x,
        observed=y,
        predicted=predicted,
    )


def fit_all_models(cycles: np.ndarray,
                   capacity: np.ndarray
                   ) -> dict[str, FitResult]:
    """Fit every registered model and return a name→result dict."""
    return {
        name: fit_capacity_fade(cycles, capacity, model=name)
        for name in MODEL_REGISTRY
    }


def best_model(results: dict[str, FitResult],
               criterion: Literal["rmse", "r_squared"] = "rmse"
               ) -> tuple[str, FitResult]:
    """Return (model_name, FitResult) of the best fit."""
    if criterion == "rmse":
        key = lambda kv: kv[1].rmse
    else:
        key = lambda kv: -kv[1].r_squared
    return min(results.items(), key=key)


# ── Temperature compensation (Arrhenius) ────────────────────────────────

def arrhenius_acceleration_factor(temperature_c: float,
                                  reference_c: float = 25.0,
                                  activation_ev: float = 0.5) -> float:
    """
    Relative degradation acceleration factor from Arrhenius kinetics.

    Parameters
    ----------
    temperature_c : operating temperature °C.
    reference_c   : reference temperature °C (default 25).
    activation_ev : activation energy in eV (typical 0.3–0.7 for Li‑ion).

    Returns
    -------
    Acceleration factor ( >1 means faster degradation).
    """
    kB = 8.617333262e-5  # eV / K
    tk = temperature_c + 273.15
    tref = reference_c + 273.15
    return float(np.exp(activation_ev / kB * (1.0 / tref - 1.0 / tk)))
