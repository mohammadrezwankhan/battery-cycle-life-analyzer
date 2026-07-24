"""
datasets — Built‑in example cycling data and synthetic generators.
"""

from __future__ import annotations

import csv
from pathlib import Path

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


def load_cycle_data(csv_path: str | Path,
                    cycle_col: str = "cycle",
                    capacity_col: str = "capacity",
                    sep: str | None = None,
                    normalize: bool = True
                    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Load cycle-capacity data from a CSV/TSV-like table.

    Parameters
    ----------
    csv_path : str | Path
        Input file path.
    cycle_col : str
        Column name for cycle index.
    capacity_col : str
        Column name for normalized or raw capacity.
    sep : str | None
        Separator character. If None, infer tab for `.tsv`/`.tab` files and
        comma otherwise. The escaped value ``"\\t"`` is accepted as a tab.
    normalize : bool
        If True, divide capacities by the first capacity value.

    Returns
    -------
    (cycle, capacity) arrays.

    Raises
    ------
    FileNotFoundError
        If `csv_path` does not exist.
    ValueError
        If expected columns are missing or rows are malformed.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Could not find dataset file: {path}")

    if sep is None:
        delimiter = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","
    else:
        delimiter = "\t" if sep == r"\t" else sep
        if len(delimiter) != 1:
            raise ValueError(
                "Separator must be one character or the escaped tab value '\\t'."
            )

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError("Input file is missing a header row.")
        header = set(reader.fieldnames)
        required = {cycle_col, capacity_col}
        missing = required - header
        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(sorted(missing))}. "
                f"Available columns: {', '.join(reader.fieldnames)}"
            )

        cycles: list[float] = []
        capacity: list[float] = []
        for row_i, row in enumerate(reader, start=2):
            try:
                cycle = float(row[cycle_col])
                q = float(row[capacity_col])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Could not parse row {row_i}: {cycle_col}={row.get(cycle_col)!r}, "
                    f"{capacity_col}={row.get(capacity_col)!r}"
                ) from exc
            if not np.isfinite(cycle) or not np.isfinite(q):
                raise ValueError(
                    f"Non-finite value in row {row_i}: "
                    f"{cycle_col}={row.get(cycle_col)!r}, "
                    f"{capacity_col}={row.get(capacity_col)!r}"
                )
            cycles.append(cycle)
            capacity.append(q)

    if len(cycles) == 0:
        raise ValueError("Input file contains no data rows.")

    cycles_arr = np.asarray(cycles, dtype=float)
    capacity_arr = np.asarray(capacity, dtype=float)

    if normalize:
        if capacity_arr.size == 0 or np.isclose(capacity_arr[0], 0.0):
            raise ValueError("Cannot normalize because first capacity is zero.")
        capacity_arr = capacity_arr / capacity_arr[0]

    return cycles_arr, capacity_arr
