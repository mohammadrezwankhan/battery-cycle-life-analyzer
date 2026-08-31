"""Opt-in integration checks against the official Oxford ORA files."""

import os

import pytest

from examples import oxford_energy_trading as oxford


pytestmark = pytest.mark.skipif(
    os.environ.get("BCLA_RUN_OXFORD_LIVE") != "1",
    reason="set BCLA_RUN_OXFORD_LIVE=1 to download official Oxford data",
)


EXPECTED = {
    "BMP_cell1": (412.37, 0.975258),
    "BMP_cell2": (410.12, 0.975585),
    "BMR_cell1": (1558.15, 0.859662),
    "BMR_cell2": (1557.65, 0.851486),
    "SPM_cell1": (689.23, 0.983522),
    "SPM_cell2": (689.93, 0.982333),
}


@pytest.mark.parametrize(("cell_id", "expected"), EXPECTED.items())
def test_official_oxford_files_reproduce_audited_efc(cell_id, expected):
    expected_efc, expected_retention = expected

    cell = oxford.load_oxford_cell(cell_id)

    assert cell.efc.size == 13
    assert cell.efc[-1] == pytest.approx(expected_efc, abs=0.01)
    assert cell.normalized_capacity[-1] == pytest.approx(
        expected_retention,
        abs=0.000001,
    )
    assert cell.non_increasing_transitions > 0
    assert cell.unobserved_tail_s <= 1800.0
