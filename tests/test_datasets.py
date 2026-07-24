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
        sep="\t",
        normalize=False,
    )

    assert np.allclose(cycles, np.array([1.0, 2.0, 3.0]))
    assert np.allclose(capacity, np.array([1.10, 1.00, 0.85]))


def test_load_cycle_data_raises_for_missing_columns(tmp_path: Path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("a,b\n1,2\n")

    with pytest.raises(ValueError, match="Missing required columns"):
        load_cycle_data(csv_path)

