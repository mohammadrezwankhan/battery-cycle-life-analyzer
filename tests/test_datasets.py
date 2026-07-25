"""Tests for bcla.datasets."""

from pathlib import Path

import numpy as np
import pytest

from bcla import core
from bcla.datasets import (
    LongFormCycleData,
    load_cycle_data,
    load_cycle_data_long_form,
    synthetic_lfp,
)


def test_load_cycle_data_reads_csv_and_normalizes(tmp_path: Path):
    csv_path = tmp_path / "cycles.csv"
    csv_path.write_text("cycle,capacity\n1,1.00\n2,0.98\n3,0.95\n")

    cycles, capacity = load_cycle_data(csv_path)

    assert np.allclose(cycles, np.array([1.0, 2.0, 3.0]))
    assert np.allclose(capacity, np.array([1.0, 0.98, 0.95]))


def test_load_cycle_data_works_without_normalization(tmp_path: Path):
    csv_path = tmp_path / "cycles.tsv"
    csv_path.write_text("t\tq\n1\t1.10\n2\t1.00\n3\t0.85\n")

    cycles, capacity = load_cycle_data(
        csv_path,
        cycle_col="t",
        capacity_col="q",
        normalize=False,
    )

    assert np.allclose(cycles, np.array([1.0, 2.0, 3.0]))
    assert np.allclose(capacity, np.array([1.10, 1.00, 0.85]))


def test_load_cycle_data_raises_for_missing_columns(tmp_path: Path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("a,b\n1,2\n")

    with pytest.raises(ValueError, match="Missing required columns"):
        load_cycle_data(csv_path)


def test_load_cycle_data_reads_utf8_bom_header(tmp_path: Path):
    csv_path = tmp_path / "excel.csv"
    csv_path.write_bytes(
        b"\xef\xbb\xbfcycle,capacity\n1,1.00\n2,0.98\n3,0.95\n"
    )

    cycles, capacity = load_cycle_data(csv_path)

    assert np.allclose(cycles, np.array([1.0, 2.0, 3.0]))
    assert np.allclose(capacity, np.array([1.0, 0.98, 0.95]))


def test_load_cycle_data_accepts_escaped_tab_separator(tmp_path: Path):
    csv_path = tmp_path / "cycles.txt"
    csv_path.write_text("cycle\tcapacity\n1\t1.00\n2\t0.95\n")

    cycles, capacity = load_cycle_data(csv_path, sep=r"\t")

    assert np.allclose(cycles, np.array([1.0, 2.0]))
    assert np.allclose(capacity, np.array([1.0, 0.95]))


@pytest.mark.parametrize("bad_value", ["nan", "inf", "-inf"])
def test_load_cycle_data_rejects_non_finite_values(
    tmp_path: Path, bad_value: str
):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text(
        f"cycle,capacity\n1,1.00\n2,{bad_value}\n"
    )

    with pytest.raises(ValueError, match="Non-finite value in row 3"):
        load_cycle_data(csv_path)


def test_load_cycle_data_rejects_multi_character_separator(tmp_path: Path):
    csv_path = tmp_path / "cycles.csv"
    csv_path.write_text("cycle,capacity\n1,1.00\n")

    with pytest.raises(ValueError, match="Separator must be one character"):
        load_cycle_data(csv_path, sep="||")


def test_load_cycle_data_long_form_multi_cell_with_metadata_and_envelope(tmp_path: Path):
    csv_path = tmp_path / "long_form.csv"
    csv_path.write_text(
        "cell_id,cycle,capacity,chemistry,temperature_c,c_rate,cycles_per_day,"
        "timestamp_iso,depth_of_discharge,energy_throughput_wh,protocol,source\n"
        "LFP-A,2,0.997,LFP,25,0.5,1,2026-07-01T00:00:00Z,0.8,1200,CC,lab\n"
        "LFP-A,1,1.00,LFP,23,0.5,1,2026-07-01T00:01:00Z,0.8,1000,CC,lab\n"
        "NMC-B,1,1.01,NMC,35,1.0,2,2026-07-01T00:02:00Z,0.9,1500,CC,test\n"
        "NMC-B,3,0.99,NMC,36,1.1,2,2026-07-01T00:03:00Z,0.9,1510,CC,test\n"
    )

    result = load_cycle_data_long_form(csv_path)

    assert isinstance(result, LongFormCycleData)
    assert result.cell_ids == ("LFP-A", "NMC-B")

    a_cycles, a_capacity = result.for_cell("LFP-A")
    assert np.allclose(a_cycles, np.array([1.0, 2.0]))
    assert np.allclose(a_capacity, np.array([1.0, 0.997]))

    envelope_a = result.validation_envelopes["LFP-A"]
    assert envelope_a["cycle_range"] == (1.0, 2.0)
    assert envelope_a["temperature_c"] == (23.0, 25.0)
    assert envelope_a["c_rate"] == (0.5, 0.5)
    assert envelope_a["timestamp_range"][0] == "2026-07-01T00:00:00+00:00"
    assert envelope_a["timestamp_range"][1] == "2026-07-01T00:01:00+00:00"
    assert abs(envelope_a["timestamp_span_days"] - 0.0006944444444444445) < 1e-12

    envelope_b = result.validation_envelopes["NMC-B"]
    assert envelope_b["cycle_range"] == (1.0, 3.0)
    assert envelope_b["cycles_per_day"] == (2.0, 2.0)
    assert envelope_b["depth_of_discharge"] == (0.9, 0.9)
    assert all(row["timestamp_iso"] is not None for row in result.rows)
    assert result.rows[0]["timestamp_iso"] == "2026-07-01T00:00:00Z"


def test_load_cycle_data_long_form_marks_optional_fields_explicitly(tmp_path: Path):
    csv_path = tmp_path / "minimal_long_form.csv"
    csv_path.write_text("cell_id,cycle,capacity\nC01,1,1.00\nC01,2,0.95\n")

    result = load_cycle_data_long_form(csv_path)
    assert len(result.rows) == 2
    assert all(row["cell_id"] == "C01" for row in result.rows)
    assert all(row["chemistry"] is None for row in result.rows)
    assert all(row["temperature_c"] is None for row in result.rows)
    assert all(row["protocol"] is None for row in result.rows)
    assert all(row["timestamp_iso"] is None for row in result.rows)
    assert result.cell_ids == ("C01",)
    assert np.allclose(result.cycles, np.array([1.0, 2.0]))
    assert np.allclose(result.capacity, np.array([1.0, 0.95]))


@pytest.mark.parametrize(
    "bad_value", ["nan", "inf", "-inf"]
)
def test_load_cycle_data_long_form_rejects_invalid_optional_numeric(
    tmp_path: Path,
    bad_value: str,
):
    csv_path = tmp_path / "bad_optional.csv"
    csv_path.write_text(
        "cell_id,cycle,capacity,temperature_c,c_rate\n"
        f"C1,1,1.00,{bad_value},1.0\n"
    )

    with pytest.raises(ValueError, match="Non-finite optional value in row 2"):
        load_cycle_data_long_form(csv_path)


def test_load_cycle_data_long_form_rejects_missing_cell_id(tmp_path: Path):
    csv_path = tmp_path / "missing_cell.csv"
    csv_path.write_text("cell_id,cycle,capacity\n,1,1.00\n")

    with pytest.raises(ValueError, match="Missing required field in row 2"):
        load_cycle_data_long_form(csv_path)


def test_load_cycle_data_long_form_rejects_negative_cycle(tmp_path: Path):
    csv_path = tmp_path / "bad_cycle.csv"
    csv_path.write_text("cell_id,cycle,capacity\nC,-1,1.00\n")

    with pytest.raises(ValueError, match="Negative required value in row 2"):
        load_cycle_data_long_form(csv_path)


def test_load_cycle_data_long_form_rejects_negative_optional(tmp_path: Path):
    csv_path = tmp_path / "bad_optional.csv"
    csv_path.write_text("cell_id,cycle,capacity,c_rate\nC,1,1.00,-0.5\n")

    with pytest.raises(ValueError, match="Negative optional value in row 2"):
        load_cycle_data_long_form(csv_path)


def test_load_cycle_data_long_form_rejects_depth_of_discharge_over_one(tmp_path: Path):
    csv_path = tmp_path / "bad_dod.csv"
    csv_path.write_text(
        "cell_id,cycle,capacity,depth_of_discharge\nC,1,1.00,1.5\n"
    )

    with pytest.raises(
        ValueError,
        match="depth_of_discharge in row 2 must be between 0 and 1",
    ):
        load_cycle_data_long_form(csv_path)


def test_load_cycle_data_long_form_rejects_invalid_timestamp(tmp_path: Path):
    bad = "2026/07/01 00:00"
    csv_path = tmp_path / "bad_timestamp.csv"
    csv_path.write_text(
        "cell_id,cycle,capacity,timestamp_iso\nC,1,1.00,"
        f"{bad}\n"
    )

    with pytest.raises(ValueError, match="Could not parse optional timestamp field in row 2"):
        load_cycle_data_long_form(csv_path)


def test_synthetic_lfp_is_gradual_without_premature_clipping():
    cycles, capacity = synthetic_lfp(cycles=1500, seed=42, noise_std=0.0)

    assert cycles[0] == 1.0
    assert cycles[-1] == 1500.0
    assert capacity.shape == (1500,)
    assert np.all(np.diff(capacity) <= 1e-12)
    assert capacity[0] > 0.99
    assert capacity[-1] > 0.82
    assert capacity.min() > 0.84


def test_synthetic_lfp_best_fit_is_good_and_produces_reasonable_eol():
    cycles, capacity = synthetic_lfp(cycles=1500, seed=42, noise_std=0.0)
    results = core.fit_all_models(cycles, capacity)
    _, best = core.best_model(results, criterion="rmse")

    assert best.r_squared > 0.95

    eol = best.eol_cycle(eol_fraction=0.8)
    assert eol is not None
    assert eol > cycles[-1]
    assert eol < 3000
