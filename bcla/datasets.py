"""
datasets — Built‑in example cycling data and synthetic generators.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def synthetic_lfp(cycles: int = 1500,
                  seed: int = 42,
                  noise_std: float = 0.005) -> tuple[NDArray[np.float64],
                                                     NDArray[np.float64]]:
    """
    Synthetic capacity‑fade data resembling an LFP cell at 1C / 25 °C.

    Parameters
    ----------
    cycles    : number of cycles to simulate.
    seed      : random seed for reproducibility.
    noise_std : standard deviation of additive Gaussian noise.

    Returns
    -------
    (cycle_array, capacity_array) each shape (N,).
    """
    rng = np.random.default_rng(seed)
    x = np.arange(1, cycles + 1, dtype=float)

    # Two‑phase degradation: power‑law fade + sudden onset (knee)
    q0 = 1.0
    alpha = 0.012
    beta = 0.65
    capacity = q0 - alpha * x ** beta

    # Add a knee plateau around cycle 800–1000
    knee_onset = 800
    knee_mag = 0.03 * (1 + np.tanh((x - knee_onset - 100) / 50)) / 2
    capacity -= knee_mag

    # Non‑linear end‑of‑life acceleration
    eol_accel = 0.0004 * np.maximum(0, x - 1100) ** 1.1
    capacity -= eol_accel

    capacity += rng.normal(0, noise_std, size=cycles)
    capacity = np.clip(capacity, 0.7, 1.01)
    return x, capacity


def synthetic_nmc(cycles: int = 1000,
                  seed: int = 7,
                  noise_std: float = 0.004) -> tuple[NDArray[np.float64],
                                                     NDArray[np.float64]]:
    """
    Synthetic capacity‑fade resembling an NMC cell at 1C / 25 °C.

    NMC degrades faster than LFP with a more linear trajectory.
    """
    rng = np.random.default_rng(seed)
    x = np.arange(1, cycles + 1, dtype=float)
    q0 = 1.0
    k = 0.00018  # steeper linear fade vs LFP power‑law
    capacity = q0 - k * x - 0.008 * (x / 1000) ** 2
    capacity += rng.normal(0, noise_std, size=cycles)
    capacity = np.clip(capacity, 0.7, 1.01)
    return x, capacity
