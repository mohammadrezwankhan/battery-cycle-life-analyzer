"""
datasets — Built‑in example cycling data and synthetic generators.
"""

from __future__ import annotations

import csv
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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

    # Two‑phase degradation: mild power‑law fade + soft knee + late acceleration.
    q0 = 1.0
    alpha = 0.0006
    beta = 0.65
    capacity = q0 - alpha * x ** beta

    # Add a knee plateau around cycle 800–1000
    knee_onset = 800
    knee_mag = 0.03 * (1 + np.tanh((x - knee_onset - 100) / 50)) / 2
    capacity -= knee_mag

    # Non‑linear end‑of‑life acceleration
    eol_accel = 0.00005 * np.maximum(0, x - 1100) ** 1.1
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


LONG_FORM_REQUIRED_COLUMNS = ("cell_id", "cycle", "capacity")
LONG_FORM_OPTIONAL_COLUMNS = (
    "chemistry",
    "timestamp_iso",
    "temperature_c",
    "c_rate",
    "rest_time_h",
    "cycles_per_day",
    "depth_of_discharge",
    "energy_throughput_wh",
    "protocol",
    "source",
)


@dataclass(frozen=True)
class LongFormCycleData:
    """Loaded long‑form cycle dataset with provenance fields preserved."""

    rows: list[dict[str, Any]]
    schema_version: str
    validation_envelopes: dict[str, dict[str, Any]]

    @property
    def cell_ids(self) -> tuple[str, ...]:
        """Cell identifiers in order of first appearance."""
        ids: list[str] = []
        for row in self.rows:
            cell_id = str(row["cell_id"])
            if cell_id not in ids:
                ids.append(cell_id)
        return tuple(ids)

    @property
    def cycles(self) -> NDArray[np.float64]:
        """
        Backwards-compatible access for single-cell inputs.

        If the payload contains multiple cells, users should call
        ``for_cell(cell_id)``.
        """
        if len(self.cell_ids) != 1:
            raise ValueError(
                "Long-form payload contains multiple cells; use for_cell(cell_id)."
            )
        cycles, _ = self.for_cell(self.cell_ids[0])
        return cycles

    @property
    def capacity(self) -> NDArray[np.float64]:
        """
        Backwards-compatible access for single-cell inputs.

        If the payload contains multiple cells, users should call
        ``for_cell(cell_id)``.
        """
        if len(self.cell_ids) != 1:
            raise ValueError(
                "Long-form payload contains multiple cells; use for_cell(cell_id)."
            )
        _, capacity = self.for_cell(self.cell_ids[0])
        return capacity

    def for_cell(self, cell_id: str) -> tuple[NDArray[np.float64],
                                             NDArray[np.float64]]:
        """Return cycle and capacity vectors for one `cell_id`."""
        matching = [row for row in self.rows if row["cell_id"] == cell_id]
        if not matching:
            raise KeyError(f"No observations found for cell_id='{cell_id}'.")

        matching = sorted(matching, key=lambda row: row["cycle"])
        cycles = np.asarray([row["cycle"] for row in matching], dtype=float)
        capacity = np.asarray([row["capacity"] for row in matching], dtype=float)
        return cycles, capacity


def _parse_required_string(row_num: int, field: str, value: Any) -> str:
    text = str(value).strip() if value is not None else ""
    if not text:
        raise ValueError(
            f"Missing required field in row {row_num}: {field}={value!r}"
        )
    return text


def _parse_required_float(
    row_num: int,
    field: str,
    value: Any,
    *,
    non_negative: bool = False,
) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"Could not parse row {row_num}: {field}={value!r}"
        ) from None

    if not np.isfinite(parsed):
        raise ValueError(
            f"Non-finite required value in row {row_num}: {field}={value!r}"
        )

    if non_negative and parsed < 0.0:
        raise ValueError(
            f"Negative required value in row {row_num}: {field}={value!r}"
        )
    return parsed


def _parse_optional_float(
    row_num: int,
    field: str,
    value: Any,
    *,
    non_negative: bool = False,
) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        parsed = float(text)
    except (TypeError, ValueError):
        raise ValueError(
            f"Could not parse optional numeric field in row {row_num}: "
            f"{field}={value!r}"
        ) from None

    if not np.isfinite(parsed):
        raise ValueError(
            f"Non-finite optional value in row {row_num}: "
            f"{field}={value!r}"
        )
    if non_negative and parsed < 0.0:
        raise ValueError(
            f"Negative optional value in row {row_num}: "
            f"{field}={value!r}"
        )
    return parsed


def _parse_optional_fraction(
    row_num: int,
    field: str,
    value: Any,
    *,
    allow_endpoint: bool = True,
) -> float | None:
    parsed = _parse_optional_float(
        row_num,
        field,
        value,
        non_negative=True,
    )
    if parsed is None:
        return None

    upper = 1.0 if allow_endpoint else (1.0 - np.finfo(float).eps)
    if parsed > upper:
        raise ValueError(
            f"{field} in row {row_num} must be between 0 and "
            f"{1.0 if allow_endpoint else 'just under 1'}."
        )
    return parsed


def _parse_optional_str(row_num: int, field: str, value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return text


def _parse_optional_timestamp(row_num: int, field: str, value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None

    normalized = text
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(normalized)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Could not parse optional timestamp field in row {row_num}: "
            f"{field}={value!r}"
        ) from exc

    return dt.isoformat()


def _build_validation_envelope(
    rows: list[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    by_cell: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_cell.setdefault(str(row["cell_id"]), []).append(row)

    envelopes: dict[str, dict[str, Any]] = {}
    for cell_id, observations in by_cell.items():
        cycles = [float(row["cycle"]) for row in observations]
        timestamps = [
            datetime.fromisoformat(row["_timestamp_parsed"].replace("Z", "+00:00"))
            for row in observations
            if row["_timestamp_parsed"] is not None
        ]
        temperature_c = [
            float(row["temperature_c"]) for row in observations
            if row["temperature_c"] is not None
        ]
        c_rates = [
            float(row["c_rate"]) for row in observations
            if row["c_rate"] is not None
        ]
        rest_time = [
            float(row["rest_time_h"]) for row in observations
            if row["rest_time_h"] is not None
        ]
        cycles_per_day = [
            float(row["cycles_per_day"]) for row in observations
            if row["cycles_per_day"] is not None
        ]
        dod = [
            float(row["depth_of_discharge"]) for row in observations
            if row["depth_of_discharge"] is not None
        ]
        throughput = [
            float(row["energy_throughput_wh"]) for row in observations
            if row["energy_throughput_wh"] is not None
        ]

        envelopes[cell_id] = {
            "cycle_range": (min(cycles), max(cycles)),
            "cycle_count": len(cycles),
            "timestamp_range": (
                min(timestamps).isoformat(),
                max(timestamps).isoformat(),
            ) if timestamps else (None, None),
            "timestamp_span_days": (
                (max(timestamps) - min(timestamps)).total_seconds() / 86400.0
            ) if timestamps else None,
            "temperature_c": (
                min(temperature_c), max(temperature_c)
            ) if temperature_c else (None, None),
            "c_rate": (min(c_rates), max(c_rates)) if c_rates else (None, None),
            "rest_time_h": (min(rest_time), max(rest_time))
            if rest_time else (None, None),
            "cycles_per_day": (
                min(cycles_per_day), max(cycles_per_day)
            ) if cycles_per_day else (None, None),
            "depth_of_discharge": (
                min(dod), max(dod)
            ) if dod else (None, None),
            "energy_throughput_wh": (
                min(throughput), max(throughput)
            ) if throughput else (None, None),
        }

    return envelopes


def _ensure_optional_columns(
    rows: list[dict[str, Any]],
    optional_columns: list[str],
) -> None:
    for row in rows:
        for field in optional_columns:
            row.setdefault(field, None)


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


def load_cycle_data_long_form(
    csv_path: str | Path,
    sep: str | None = None,
    normalize: bool = True,
    schema_version: str = "1",
) -> LongFormCycleData:
    """
    Load long-form cycle-capacity data with optional metadata columns preserved.

    Parameters
    ----------
    csv_path : str | Path
        Input file path.
    sep : str | None
        Separator character. If None, infer tab for `.tsv`/`.tab` files and comma
        otherwise. The escaped value ``"\\t"`` is accepted as a tab.
    normalize : bool
        If True, divide capacities by the first observed capacity per `cell_id`.
    schema_version : str
        Optional schema tag returned in the result.
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
        missing = set(LONG_FORM_REQUIRED_COLUMNS) - header
        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(sorted(missing))}. "
                f"Available columns: {', '.join(reader.fieldnames)}"
            )

        rows: list[dict[str, Any]] = []
        for row_i, raw_row in enumerate(reader, start=2):
            row = {
                "cell_id": _parse_required_string(row_i, "cell_id", raw_row["cell_id"]),
                "cycle": _parse_required_float(
                    row_i,
                    "cycle",
                    raw_row["cycle"],
                    non_negative=True,
                ),
                "capacity": _parse_required_float(
                    row_i,
                    "capacity",
                    raw_row["capacity"],
                ),
                "chemistry": _parse_optional_str(
                    row_i,
                    "chemistry",
                    raw_row.get("chemistry"),
                ),
                "timestamp_iso": _parse_optional_str(
                    row_i,
                    "timestamp_iso",
                    raw_row.get("timestamp_iso"),
                ),
                "_timestamp_parsed": _parse_optional_timestamp(
                    row_i,
                    "timestamp_iso",
                    raw_row.get("timestamp_iso"),
                ),
                "temperature_c": _parse_optional_float(
                    row_i,
                    "temperature_c",
                    raw_row.get("temperature_c"),
                    non_negative=False,
                ),
                "c_rate": _parse_optional_float(
                    row_i,
                    "c_rate",
                    raw_row.get("c_rate"),
                    non_negative=True,
                ),
                "rest_time_h": _parse_optional_float(
                    row_i,
                    "rest_time_h",
                    raw_row.get("rest_time_h"),
                    non_negative=True,
                ),
                "cycles_per_day": _parse_optional_float(
                    row_i,
                    "cycles_per_day",
                    raw_row.get("cycles_per_day"),
                    non_negative=True,
                ),
                "depth_of_discharge": _parse_optional_fraction(
                    row_i,
                    "depth_of_discharge",
                    raw_row.get("depth_of_discharge"),
                ),
                "energy_throughput_wh": _parse_optional_float(
                    row_i,
                    "energy_throughput_wh",
                    raw_row.get("energy_throughput_wh"),
                    non_negative=True,
                ),
                "protocol": _parse_optional_str(
                    row_i,
                    "protocol",
                    raw_row.get("protocol"),
                ),
                "source": _parse_optional_str(
                    row_i,
                    "source",
                    raw_row.get("source"),
                ),
            }
            rows.append(row)

    if not rows:
        raise ValueError("Input file contains no data rows.")

    _ensure_optional_columns(rows, list(LONG_FORM_OPTIONAL_COLUMNS))

    if normalize:
        cells: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            cell_id = str(row["cell_id"])
            cells.setdefault(cell_id, []).append(row)

        for cell_id, group in cells.items():
            # Normalize against earliest observed cycle in the grouped payload.
            sorted_group = sorted(group, key=lambda row: row["cycle"])
            base_capacity = float(sorted_group[0]["capacity"])
            if np.isclose(base_capacity, 0.0):
                raise ValueError(
                    f"Cannot normalize because first capacity for cell_id='{cell_id}' "
                    "is zero."
                )
            for row in group:
                row["capacity"] = float(row["capacity"]) / base_capacity

    envelopes = _build_validation_envelope(rows)
    return LongFormCycleData(
        rows=rows,
        schema_version=schema_version,
        validation_envelopes=envelopes,
    )
