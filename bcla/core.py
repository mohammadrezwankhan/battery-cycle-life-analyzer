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

    def project(self, target_cycles: float) -> float:
        """Return predicted normalised capacity at *target_cycles*."""
        func = _model_func(self.model_name)
        p0 = [self.params[n] for n in _model_pnames(self.model_name)]
        prediction = np.asarray(
            func(np.array([target_cycles], dtype=float), *p0),
            dtype=float,
        )
        return float(prediction.reshape(-1)[0])

    def eol_cycle(self, eol_fraction: float = 0.8) -> Optional[float]:
        """
        Cycle number where capacity drops to *eol_fraction* of initial.

        Returns None if the model never reaches the threshold within
        three times the largest observed cycle.
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


@dataclass(frozen=True)
class ValidationScore:
    """Diagnostics on a chronological validation window."""

    model_name: str
    rmse: float
    r_squared: float
    train_size: int
    validation_size: int
    split_cycle: float


@dataclass
class ModelSelection:
    """A model selected on held-out late-cycle observations."""

    model_name: str
    fit: FitResult
    scores: dict[str, ValidationScore]
    criterion: Literal["rmse", "r_squared"]
    validation_fraction: float

    @property
    def validation_score(self) -> ValidationScore:
        """Return the held-out score for the selected model."""
        return self.scores[self.model_name]


@dataclass(frozen=True)
class LifeProjectionInterval:
    """Residual-bootstrap interval for bounded EOL and RUL projections."""

    model_name: str
    confidence: float
    eol_fraction: float
    current_cycle: float
    eol_estimate: Optional[float]
    eol_lower: Optional[float]
    eol_upper: Optional[float]
    rul_estimate: Optional[float]
    rul_lower: Optional[float]
    rul_upper: Optional[float]
    requested_samples: int
    successful_samples: int
    censored_samples: int
    failed_samples: int


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
    """Return the best in-sample fit (not an extrapolation validation)."""
    if criterion == "rmse":
        key = lambda kv: kv[1].rmse
    elif criterion == "r_squared":
        key = lambda kv: -kv[1].r_squared
    else:
        raise ValueError("criterion must be 'rmse' or 'r_squared'")
    return min(results.items(), key=key)


def _temporal_arrays(cycles: np.ndarray,
                     capacity: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Validate and sort paired observations by cycle for temporal splitting."""
    x = np.asarray(cycles, dtype=float).ravel()
    y = np.asarray(capacity, dtype=float).ravel()
    if x.size != y.size:
        raise ValueError("cycles and capacity must contain the same number of values")
    if x.size < 6:
        raise ValueError("at least six observations are required for temporal validation")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("cycles and capacity must contain only finite values")
    if np.any(x < 0.0):
        raise ValueError("cycles must be non-negative")
    minimum_unique_cycles = max(
        len(_model_pnames(name)) + 1 for name in MODEL_REGISTRY
    ) + 2
    if np.unique(x).size < minimum_unique_cycles:
        raise ValueError(
            f"at least {minimum_unique_cycles} distinct cycle values are required "
            "for temporal validation"
        )
    order = np.argsort(x, kind="stable")
    return x[order], y[order]


def temporal_holdout_scores(
        cycles: np.ndarray,
        capacity: np.ndarray,
        validation_fraction: float = 0.2,
        ) -> dict[str, ValidationScore]:
    """
    Score every model on the latest chronological observations.

    Models are fitted only to the earlier observations. The validation window
    therefore tests forward prediction rather than randomly mixing early and
    late cycles. At least four distinct training cycle values and two distinct
    held-out cycle values are required. Rows with the same cycle index remain
    on the same side of the split. ``validation_fraction`` is an observation-row
    fraction rather than a fraction of the cycle-number horizon.
    """
    if not 0.0 < validation_fraction < 1.0:
        raise ValueError("validation_fraction must be between 0 and 1")

    x, y = _temporal_arrays(cycles, capacity)
    validation_size = max(2, int(np.ceil(x.size * validation_fraction)))
    split_index = x.size - validation_size
    while split_index > 0 and x[split_index - 1] == x[split_index]:
        split_index -= 1
    while split_index > 0 and np.unique(x[split_index:]).size < 2:
        split_cycle = x[split_index - 1]
        while split_index > 0 and x[split_index - 1] == split_cycle:
            split_index -= 1
    train_size = split_index
    validation_size = x.size - split_index
    minimum_train_size = max(
        len(_model_pnames(name)) + 1 for name in MODEL_REGISTRY
    )
    if train_size < minimum_train_size:
        raise ValueError(
            f"validation_fraction leaves fewer than {minimum_train_size} "
            "training observations"
        )
    if np.unique(x[:split_index]).size < minimum_train_size:
        raise ValueError(
            f"validation_fraction leaves fewer than {minimum_train_size} "
            "distinct training cycle values"
        )

    x_train, y_train = x[:split_index], y[:split_index]
    x_validation, y_validation = x[split_index:], y[split_index:]
    scores: dict[str, ValidationScore] = {}
    for name in MODEL_REGISTRY:
        fitted = fit_capacity_fade(x_train, y_train, model=name)
        func = _model_func(name)
        params = [fitted.params[pname] for pname in _model_pnames(name)]
        predicted = func(x_validation, *params)
        if not np.all(np.isfinite(predicted)):
            raise ValueError(
                f"{name} produced non-finite predictions on the validation window"
            )
        residuals = y_validation - predicted
        rmse = float(np.sqrt(np.mean(residuals ** 2)))
        ss_res = float(np.sum(residuals ** 2))
        ss_tot = float(np.sum((y_validation - np.mean(y_validation)) ** 2))
        r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        if not np.isfinite(rmse):
            raise ValueError(
                f"{name} produced a non-finite RMSE on the validation window"
            )
        scores[name] = ValidationScore(
            model_name=name,
            rmse=rmse,
            r_squared=r_squared,
            train_size=train_size,
            validation_size=validation_size,
            split_cycle=float(x_validation[0]),
        )
    return scores


def select_model_by_validation(
        cycles: np.ndarray,
        capacity: np.ndarray,
        validation_fraction: float = 0.2,
        criterion: Literal["rmse", "r_squared"] = "rmse",
        ) -> ModelSelection:
    """
    Select a model on a late-cycle holdout, then refit it on all observations.

    The returned ``fit`` uses the complete, cycle-sorted dataset only after the
    model family has been selected. ``scores`` retains the held-out diagnostics
    used for that decision.
    """
    if criterion not in {"rmse", "r_squared"}:
        raise ValueError("criterion must be 'rmse' or 'r_squared'")

    x, y = _temporal_arrays(cycles, capacity)
    scores = temporal_holdout_scores(
        x,
        y,
        validation_fraction=validation_fraction,
    )
    if criterion == "rmse":
        model_name = min(scores, key=lambda name: scores[name].rmse)
    else:
        if any(not np.isfinite(score.r_squared) for score in scores.values()):
            raise ValueError(
                "r_squared is undefined for a constant validation window; "
                "use criterion='rmse'"
            )
        model_name = max(scores, key=lambda name: scores[name].r_squared)
    fitted = fit_capacity_fade(x, y, model=model_name)
    return ModelSelection(
        model_name=model_name,
        fit=fitted,
        scores=scores,
        criterion=criterion,
        validation_fraction=validation_fraction,
    )


def bootstrap_life_projection(
        result: FitResult,
        eol_fraction: float = 0.8,
        current_cycle: Optional[float] = None,
        confidence: float = 0.95,
        samples: int = 500,
        random_state: Optional[int] = None,
        ) -> LifeProjectionInterval:
    """
    Estimate bounded EOL/RUL intervals with a residual bootstrap.

    Each replicate resamples centered fit residuals, refits the selected model,
    and applies the same three-times-largest-observed-cycle projection bound as
    :meth:`FitResult.eol_cycle`. Replicates whose EOL is outside that bound are
    reported as censored. Interval bounds are withheld whenever any replicate
    is right-censored or fails to fit. This prevents apparently finite bounds
    from being calculated after discarding unknown or longest-running
    projections.

    This interval quantifies residual/refit variation conditional on the chosen
    empirical model. It does not cover model-form, protocol, or unrecorded
    measurement uncertainty.
    """
    if not 0.0 < eol_fraction < 1.0:
        raise ValueError("eol_fraction must be between 0 and 1")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be between 0 and 1")
    if not isinstance(samples, (int, np.integer)) or samples < 20:
        raise ValueError("samples must be an integer of at least 20")
    if result.model_name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model '{result.model_name}'")

    cycles = np.asarray(result.cycles, dtype=float).ravel()
    observed = np.asarray(result.observed, dtype=float).ravel()
    predicted = np.asarray(result.predicted, dtype=float).ravel()
    if cycles.size == 0 or cycles.size != observed.size or cycles.size != predicted.size:
        raise ValueError("result must contain aligned, non-empty fit observations")
    if not all(np.all(np.isfinite(values)) for values in (cycles, observed, predicted)):
        raise ValueError("result observations and predictions must be finite")
    if np.any(cycles < 0.0):
        raise ValueError("result cycles must be non-negative")
    parameter_count = len(_model_pnames(result.model_name))
    if cycles.size <= parameter_count or np.unique(cycles).size <= parameter_count:
        raise ValueError(
            "bootstrap projection requires more distinct observations than "
            "fitted parameters"
        )

    if current_cycle is None:
        current_cycle = float(np.max(cycles))
    if not np.isfinite(current_cycle):
        raise ValueError("current_cycle must be finite")
    if current_cycle < 0.0:
        raise ValueError("current_cycle must be non-negative")

    residuals = observed - predicted
    centered_residuals = residuals - np.mean(residuals)
    residual_scale = float(np.std(centered_residuals, ddof=1))
    numerical_scale = max(1.0, float(np.max(np.abs(observed))))
    if residual_scale <= np.finfo(float).eps * numerical_scale:
        raise ValueError(
            "bootstrap projection requires positive residual variance"
        )
    rng = np.random.default_rng(random_state)
    eol_samples: list[float] = []
    censored_samples = 0
    failed_samples = 0

    for _ in range(int(samples)):
        synthetic_capacity = predicted + rng.choice(
            centered_residuals,
            size=centered_residuals.size,
            replace=True,
        )
        try:
            bootstrap_fit = fit_capacity_fade(
                cycles,
                synthetic_capacity,
                model=result.model_name,
                q0_guess=result.params.get("Q0"),
            )
            bootstrap_eol = bootstrap_fit.eol_cycle(eol_fraction)
        except (
            RuntimeError,
            ValueError,
            FloatingPointError,
            np.linalg.LinAlgError,
            OverflowError,
        ):
            failed_samples += 1
            continue
        if bootstrap_eol is None or not np.isfinite(bootstrap_eol):
            censored_samples += 1
            continue
        eol_samples.append(float(bootstrap_eol))

    successful_samples = len(eol_samples)
    eol_lower: Optional[float] = None
    eol_upper: Optional[float] = None
    rul_lower: Optional[float] = None
    rul_upper: Optional[float] = None
    if (
        censored_samples == 0
        and failed_samples == 0
        and successful_samples == samples
    ):
        alpha = (1.0 - confidence) / 2.0
        eol_array = np.asarray(eol_samples)
        eol_lower, eol_upper = (
            float(value) for value in np.quantile(eol_array, [alpha, 1.0 - alpha])
        )
        rul_array = np.maximum(0.0, eol_array - current_cycle)
        rul_lower, rul_upper = (
            float(value) for value in np.quantile(rul_array, [alpha, 1.0 - alpha])
        )

    eol_estimate = result.eol_cycle(eol_fraction)
    rul_estimate = (
        None
        if eol_estimate is None
        else max(0.0, float(eol_estimate) - current_cycle)
    )
    return LifeProjectionInterval(
        model_name=result.model_name,
        confidence=confidence,
        eol_fraction=eol_fraction,
        current_cycle=current_cycle,
        eol_estimate=eol_estimate,
        eol_lower=eol_lower,
        eol_upper=eol_upper,
        rul_estimate=rul_estimate,
        rul_lower=rul_lower,
        rul_upper=rul_upper,
        requested_samples=int(samples),
        successful_samples=successful_samples,
        censored_samples=censored_samples,
        failed_samples=failed_samples,
    )


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
