"""CSV contracts and physically bounded inputs exercised through public loaders."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, cast

import numpy as np
import pytest

from bcla import datasets


@pytest.mark.parametrize(
    "loader",
    [
        datasets.load_cycle_data,
        datasets.load_cycle_data_long_form,
        datasets.load_duty_cycle_history,
    ],
)
def test_csv_loaders_reject_missing_file_and_invalid_header(
    loader: Callable[..., object],
    tmp_path: Path,
) -> None:
    path = tmp_path / "data.csv"
    with pytest.raises(FileNotFoundError):
        loader(path)
    for text, message in (("", "header"), ("unrelated\n1\n", "required columns")):
        path.write_text(text)
        with pytest.raises(ValueError, match=message):
            loader(path)
    path.write_text("unused\n")
    with pytest.raises(ValueError, match="Separator"):
        loader(path, sep="::")


@pytest.mark.parametrize(
    "text", ["cycle,capacity\n", "cycle,capacity\n0,bad\n", "cycle,capacity\n0,0\n1,1\n"]
)
def test_simple_csv_empty_malformed_and_zero_initial_capacity(text: str, tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_text(text)
    with pytest.raises(ValueError):
        datasets.load_cycle_data(path)


@pytest.mark.parametrize(
    "text",
    [
        "cell_id,cycle,capacity\n",
        "cell_id,cycle,capacity\nA,0,0\n",
        "cell_id,cycle,capacity\nA,invalid,1\n",
        "cell_id,cycle,capacity\nA,-1,1\n",
        "cell_id,cycle,capacity\nA,inf,1\n",
        "cell_id,cycle,capacity,c_rate\nA,0,1,invalid\n",
        "cell_id,cycle,capacity,c_rate\nA,0,1,-1\n",
        "cell_id,cycle,capacity,depth_of_discharge\nA,0,1,1.1\n",
    ],
)
def test_long_form_rejects_empty_or_invalid_physical_values(text: str, tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_text(text)
    with pytest.raises(ValueError):
        datasets.load_cycle_data_long_form(path)


def test_long_form_single_cell_compatibility_sorted_selection_and_optional_empty_values(
    tmp_path: Path,
) -> None:
    path = tmp_path / "data.tsv"
    path.write_text(
        "cell_id\tcycle\tcapacity\tchemistry\ttimestamp_iso\tc_rate\n"
        "A\t10\t1.8\t \t \t \nA\t0\t2.0\tLFP\t\t\n"
    )
    data = datasets.load_cycle_data_long_form(path, sep=r"\t", normalize=False)
    assert data.cell_ids == ("A",)
    assert np.array_equal(data.cycles, [0.0, 10.0])
    assert np.array_equal(data.capacity, [2.0, 1.8])
    assert data.rows[0]["chemistry"] is None
    assert data.rows[0]["timestamp_iso"] is None
    with pytest.raises(KeyError, match="No observations"):
        data.for_cell("missing")
    multi = datasets.LongFormCycleData(
        [
            {"cell_id": "A", "cycle": 0, "capacity": 1},
            {"cell_id": "B", "cycle": 0, "capacity": 1},
        ],
        "1",
        {},
    )
    with pytest.raises(ValueError, match="multiple cells"):
        _ = multi.cycles
    with pytest.raises(ValueError, match="multiple cells"):
        _ = multi.capacity


def test_history_loader_accepts_explicit_tab_and_rejects_empty_table(tmp_path: Path) -> None:
    path = tmp_path / "history.tsv"
    header = "cell_id\texperiment_id\tinterval_start\tinterval_end\n"
    path.write_text(header)
    with pytest.raises(ValueError, match="no data"):
        datasets.load_duty_cycle_history(path)
    path.write_text(header + "A\tE\t2026-01-01T00:00:00Z\t2026-01-01T01:00:00Z\n")
    rows, envelopes, schema = datasets.load_duty_cycle_history(path, sep=r"\t")
    assert len(rows) == 1
    assert envelopes["A|E"]["duration_hours"] == (1.0, 1.0)
    assert schema == "2"


def test_efc_last_query_and_non_numeric_nameplate_capacity() -> None:
    result = datasets.equivalent_full_cycles([0.0, 3600.0], [1.0, 1.0], 1.0, query_time_s=[3600.0])
    assert np.array_equal(result, [1.0])
    # Exercise the external parser with a value outside the static float contract.
    with pytest.raises(ValueError, match="positive finite"):
        datasets.equivalent_full_cycles([0.0, 1.0], [1.0, 1.0], cast(float, "invalid"))
