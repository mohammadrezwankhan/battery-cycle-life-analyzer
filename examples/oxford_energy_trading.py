"""Analyze one cell from the Oxford energy-trading battery dataset.

The script downloads original ODbL-licensed CSV files from the University of
Oxford Research Archive at runtime. No Oxford data are bundled with bcla.
"""

from __future__ import annotations

import argparse
import csv
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import numpy as np
from numpy.typing import NDArray

from bcla.datasets import equivalent_full_cycles


OXFORD_RECORD_URL = (
    "https://ora.ox.ac.uk/objects/"
    "uuid:9aae61af-2949-49f1-8ad5-6aea448979e5"
)
OXFORD_DOI = "10.5287/bodleian:gJPdDzvP4"
OXFORD_LICENSE = "ODC Open Database License (ODbL) 1.0"
NOMINAL_CAPACITY_AH = 16.0
MAX_DOWNLOAD_BYTES = 32 * 1024 * 1024

_FILE_ROOT = f"{OXFORD_RECORD_URL}/files"
CELL_FILES = {
    "BMP_cell1": ("dcc08hf70v", "d7h149q034"),
    "BMP_cell2": ("dvx021f16r", "dth83kz455"),
    "BMR_cell1": ("d7d278t10b", "dkw52j8142"),
    "BMR_cell2": ("d4b29b6049", "dxp68kg34h"),
    "SPM_cell1": ("d9880vr050", "d2801pg45q"),
    "SPM_cell2": ("dhx11xf35n", "dg732d903f"),
}


@dataclass(frozen=True)
class OxfordCellData:
    """One Oxford cell expressed on a measured discharge-EFC axis."""

    cell_id: str
    efc: NDArray[np.float64]
    capacity_ah: NDArray[np.float64]
    normalized_capacity: NDArray[np.float64]
    profile_rows: int
    canonical_profile_rows: int
    non_increasing_transitions: int
    duplicate_samples: int
    unobserved_tail_s: float


@dataclass(frozen=True)
class _ProfileData:
    time_s: NDArray[np.float64]
    current_a: NDArray[np.float64]
    raw_rows: int
    non_increasing_transitions: int
    duplicate_samples: int


def _download_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "bcla-real-data-example/1.0"})
    with urlopen(request, timeout=90) as response:
        payload = response.read(MAX_DOWNLOAD_BYTES + 1)
    if len(payload) > MAX_DOWNLOAD_BYTES:
        raise ValueError(
            f"Download exceeds the {MAX_DOWNLOAD_BYTES}-byte safety limit: {url}"
        )
    return payload.decode("utf-8-sig")


def _reader(csv_text: str, required: set[str]) -> csv.DictReader:
    reader = csv.DictReader(io.StringIO(csv_text))
    if reader.fieldnames is None:
        raise ValueError("CSV input is missing a header row")
    missing = required - set(reader.fieldnames)
    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing))}. "
            f"Available columns: {', '.join(reader.fieldnames)}"
        )
    return reader


def _profile_arrays(csv_text: str) -> _ProfileData:
    reader = _reader(csv_text, {"time_s", "current_A"})
    times: list[float] = []
    currents: list[float] = []
    trailing_non_finite = False
    for row_number, row in enumerate(reader, start=2):
        try:
            time = float(row["time_s"])
            current = float(row["current_A"])
        except (TypeError, ValueError):
            raise ValueError(
                f"Could not parse profile row {row_number}: "
                f"time_s={row.get('time_s')!r}, current_A={row.get('current_A')!r}"
            ) from None

        if not np.isfinite(time) and not np.isfinite(current):
            trailing_non_finite = True
            continue
        if not np.isfinite(time) or not np.isfinite(current):
            raise ValueError(
                f"Partially non-finite profile row {row_number}: "
                f"time_s={row.get('time_s')!r}, current_A={row.get('current_A')!r}"
            )
        if trailing_non_finite:
            raise ValueError("Non-finite profile rows must be trailing only")
        times.append(time)
        currents.append(current)

    raw_time = np.asarray(times, dtype=float)
    raw_current = np.asarray(currents, dtype=float)
    if raw_time.size < 2:
        raise ValueError("At least two finite profile rows are required")

    non_increasing = int(np.count_nonzero(np.diff(raw_time) <= 0.0))
    order = np.argsort(raw_time, kind="stable")
    sorted_time = raw_time[order]
    sorted_current = raw_current[order]
    unique_time, first_index, counts = np.unique(
        sorted_time,
        return_index=True,
        return_counts=True,
    )
    summed_current = np.add.reduceat(sorted_current, first_index)
    canonical_current = summed_current / counts
    duplicate_samples = int(raw_time.size - unique_time.size)
    return _ProfileData(
        time_s=unique_time,
        current_a=canonical_current,
        raw_rows=int(raw_time.size),
        non_increasing_transitions=non_increasing,
        duplicate_samples=duplicate_samples,
    )


def _capacity_arrays(csv_text: str) -> tuple[NDArray[np.float64],
                                              NDArray[np.float64]]:
    reader = _reader(csv_text, {"profile_time_s", "capacity_Ah"})
    times: list[float] = []
    capacities: list[float] = []
    for row_number, row in enumerate(reader, start=2):
        try:
            time = float(row["profile_time_s"])
            capacity = float(row["capacity_Ah"])
        except (TypeError, ValueError):
            raise ValueError(
                f"Could not parse capacity row {row_number}: "
                f"profile_time_s={row.get('profile_time_s')!r}, "
                f"capacity_Ah={row.get('capacity_Ah')!r}"
            ) from None
        if not np.isfinite(time) or not np.isfinite(capacity):
            raise ValueError(f"Capacity row {row_number} must contain finite values")
        if capacity <= 0.0:
            raise ValueError(f"Capacity row {row_number} must be positive")
        times.append(time)
        capacities.append(capacity)

    time_array = np.asarray(times, dtype=float)
    capacity_array = np.asarray(capacities, dtype=float)
    if time_array.size < 2:
        raise ValueError("At least two capacity checks are required")
    if np.any(np.diff(time_array) <= 0.0):
        raise ValueError("profile_time_s must be strictly increasing")
    return time_array, capacity_array


def load_oxford_cell_from_text(
    cell_id: str,
    profile_csv: str,
    capacity_csv: str,
    nominal_capacity_ah: float = NOMINAL_CAPACITY_AH,
) -> OxfordCellData:
    """Convert official Oxford CSV text to capacity versus measured EFC."""
    profile = _profile_arrays(profile_csv)
    check_time, capacity = _capacity_arrays(capacity_csv)
    trailing_checks = check_time > profile.time_s[-1]
    trailing_count = int(np.count_nonzero(trailing_checks))
    unobserved_tail_s = max(0.0, float(check_time[-1] - profile.time_s[-1]))
    if trailing_count:
        if trailing_count != 1:
            raise ValueError(
                "Only the final capacity check may extend beyond the measured "
                "current profile"
            )
        if unobserved_tail_s > 1800.0 or abs(profile.current_a[-1]) > 1e-3:
            raise ValueError(
                "Capacity checks extend beyond the measured current profile "
                "without a supported near-zero-current tail"
            )
        check_time = check_time.copy()
        check_time[-1] = profile.time_s[-1]
    efc = equivalent_full_cycles(
        profile.time_s,
        profile.current_a,
        nominal_capacity_ah,
        query_time_s=check_time,
    )
    return OxfordCellData(
        cell_id=cell_id,
        efc=efc,
        capacity_ah=capacity,
        normalized_capacity=capacity / capacity[0],
        profile_rows=profile.raw_rows,
        canonical_profile_rows=int(profile.time_s.size),
        non_increasing_transitions=profile.non_increasing_transitions,
        duplicate_samples=profile.duplicate_samples,
        unobserved_tail_s=unobserved_tail_s,
    )


def load_oxford_cell(cell_id: str) -> OxfordCellData:
    """Download and convert one supported Oxford cell."""
    if cell_id not in CELL_FILES:
        raise ValueError(
            f"Unknown cell_id={cell_id!r}; choose from {', '.join(CELL_FILES)}"
        )
    profile_file, capacity_file = CELL_FILES[cell_id]
    profile_csv = _download_text(f"{_FILE_ROOT}/{profile_file}")
    capacity_csv = _download_text(f"{_FILE_ROOT}/{capacity_file}")
    return load_oxford_cell_from_text(cell_id, profile_csv, capacity_csv)


def _decorate_efc_figure(figure: Any, results: dict[str, Any], cell_id: str) -> None:
    """Expose the observed window and bounded extrapolation on an EFC axis."""
    fitted = list(results.values())
    threshold = min(result.params["Q0"] * 0.8 for result in fitted)
    observed_min = min(float(np.min(result.observed)) for result in fitted)
    observed_max = max(float(np.max(result.observed)) for result in fitted)
    q0_max = max(result.params["Q0"] for result in fitted)

    for axis, result in zip(figure.axes, fitted):
        display_model_name = result.model_name.replace("_", " ").title()
        axis.lines[0].set_label(display_model_name)
        last_observed_efc = float(np.max(result.cycles))
        eol = result.eol_cycle(0.8)
        projection_end = (
            max(last_observed_efc, eol)
            if eol is not None
            else last_observed_efc * 3.0
        )
        if projection_end > last_observed_efc:
            projection_efc = np.linspace(last_observed_efc, projection_end, 300)
            projected_capacity = np.asarray(
                [result.project(value) for value in projection_efc],
                dtype=float,
            )
            axis.plot(
                projection_efc,
                projected_capacity,
                color="#d62728",
                linestyle="--",
                linewidth=1.5,
                label="Bounded projection",
            )
        axis.set_xlabel("Measured Discharge EFC")
        axis.set_xlim(left=0.0, right=max(1.0, projection_end * 1.03))
        axis.set_title(display_model_name)
        metrics_text = axis.texts[-1]
        metrics_text.set_position((0.03, 0.05))
        metrics_text.set_horizontalalignment("left")
        axis.legend(loc="upper right", fontsize=8)

    figure.axes[0].set_ylim(
        bottom=min(threshold - 0.06, observed_min - 0.05),
        top=max(q0_max + 0.03, observed_max + 0.03),
    )
    display_cell_id = cell_id.replace("_cell", " cell ")
    figure.suptitle(
        f"{display_cell_id}: Model Comparison on Measured Discharge EFC",
        fontsize=14,
        y=1.04,
    )


def run_analysis(
    cell_id: str,
    *,
    validation_fraction: float,
    bootstrap_samples: int,
    output: Path | None,
) -> None:
    """Download one cell, run the released workflow, and print diagnostics."""
    from bcla import core, viz

    cell = load_oxford_cell(cell_id)
    selection = core.select_model_by_validation(
        cell.efc,
        cell.normalized_capacity,
        validation_fraction=validation_fraction,
    )

    print(f"Source: {OXFORD_RECORD_URL}")
    print(f"DOI: {OXFORD_DOI}")
    print(f"Data license: {OXFORD_LICENSE}")
    print(
        f"{cell.cell_id}: {cell.efc.size} capacity checks, "
        f"{cell.profile_rows} measured-profile rows "
        f"({cell.canonical_profile_rows} canonical)"
    )
    print(
        "Profile diagnostics: "
        f"non-increasing transitions={cell.non_increasing_transitions}, "
        f"duplicate samples={cell.duplicate_samples}, "
        f"unobserved near-zero-current tail={cell.unobserved_tail_s:.1f} s"
    )
    print(f"Final measured discharge EFC: {cell.efc[-1]:.2f}")
    print(f"Final normalized capacity: {cell.normalized_capacity[-1]:.4f}")
    validation_score = selection.validation_score
    print(
        "Chronological holdout: "
        f"training checks={validation_score.train_size}, "
        f"late validation checks={validation_score.validation_size}, "
        f"split={validation_score.split_cycle:.2f} measured discharge EFC"
    )
    for name, score in selection.scores.items():
        print(
            f"{name:11s} holdout RMSE={score.rmse:.6f} "
            f"R^2={score.r_squared:.4f}"
        )
    print(f"Selected model: {selection.model_name}")

    eol = selection.fit.eol_cycle(0.8)
    if eol is None:
        print("80% EOL is outside the supported three-times-observed EFC horizon")
    else:
        print(f"Bounded 80% EOL: {eol:.2f} measured discharge EFC")
        print(
            "Point-estimate RUL at the final observation: "
            f"{max(0.0, eol - cell.efc[-1]):.2f} measured discharge EFC"
        )

    if bootstrap_samples:
        if bootstrap_samples < 20:
            raise ValueError("bootstrap_samples must be 0 or at least 20")
        interval = core.bootstrap_life_projection(
            selection.fit,
            current_cycle=float(cell.efc[-1]),
            samples=bootstrap_samples,
            random_state=42,
        )
        print(
            "Bootstrap diagnostics: "
            f"requested={interval.requested_samples}, "
            f"successful={interval.successful_samples}, "
            f"censored={interval.censored_samples}, "
            f"failed={interval.failed_samples}"
        )
        if interval.eol_lower is None:
            print("Bootstrap EOL/RUL bounds unavailable")
        else:
            print(
                f"95% EOL interval: {interval.eol_lower:.2f}-"
                f"{interval.eol_upper:.2f} measured discharge EFC"
            )
            print(
                f"95% RUL interval: {interval.rul_lower:.2f}-"
                f"{interval.rul_upper:.2f} measured discharge EFC"
            )

    if output is not None:
        results = core.fit_all_models(cell.efc, cell.normalized_capacity)
        figure = viz.model_comparison(results)
        _decorate_efc_figure(figure, results, cell.cell_id)
        figure.savefig(output, dpi=180, bbox_inches="tight")
        print(f"Saved figure: {output}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run bcla on an official Oxford grid-battery cell"
    )
    parser.add_argument("--cell", choices=tuple(CELL_FILES), default="BMR_cell1")
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument(
        "--bootstrap-samples",
        type=int,
        default=200,
        help="Residual-bootstrap replicates; use 0 to disable",
    )
    parser.add_argument("--output", type=Path, help="Optional output PNG path")
    args = parser.parse_args()
    run_analysis(
        args.cell,
        validation_fraction=args.validation_fraction,
        bootstrap_samples=args.bootstrap_samples,
        output=args.output,
    )


if __name__ == "__main__":
    main()
