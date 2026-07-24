"""Tests for bcla.datasets."""

from pathlib import Path

import numpy as np
import pytest

from bcla.datasets import load_cycle_data


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
