"""Offline tests for the Oxford real-data example's CSV mapping."""

import numpy as np
import pytest

from examples import oxford_energy_trading as EXAMPLE


PROFILE_CSV = """time_s,current_A,voltage_V
0,8,3.7
900,-8,3.8
1800,16,3.6
2700,0,3.7
NaN,NaN,NaN
"""

CAPACITY_CSV = """time_s,profile_time_s,capacity_Ah
0,0,16
1,900,15.84
2,1800,15.36
3,2700,14.4
"""


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.requested_bytes = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self, requested_bytes):
        self.requested_bytes = requested_bytes
        return self.payload[:requested_bytes]


def test_download_text_uses_a_bounded_read(monkeypatch):
    response = _FakeResponse(b"\xef\xbb\xbftime_s,current_A\n0,0\n")
    monkeypatch.setattr(
        EXAMPLE,
        "urlopen",
        lambda request, timeout: response,
    )

    text = EXAMPLE._download_text("https://example.test/profile.csv")

    assert text.startswith("time_s,current_A")
    assert response.requested_bytes == EXAMPLE.MAX_DOWNLOAD_BYTES + 1


def test_download_text_rejects_payload_over_safety_limit(monkeypatch):
    response = _FakeResponse(b"12345")
    monkeypatch.setattr(EXAMPLE, "MAX_DOWNLOAD_BYTES", 4)
    monkeypatch.setattr(
        EXAMPLE,
        "urlopen",
        lambda request, timeout: response,
    )

    with pytest.raises(ValueError, match="4-byte safety limit"):
        EXAMPLE._download_text("https://example.test/oversized.csv")


def test_load_oxford_cell_from_text_maps_official_headers():
    cell = EXAMPLE.load_oxford_cell_from_text(
        "fixture_cell",
        PROFILE_CSV,
        CAPACITY_CSV,
        nominal_capacity_ah=16.0,
    )

    assert cell.cell_id == "fixture_cell"
    assert cell.profile_rows == 4
    assert cell.canonical_profile_rows == 4
    assert cell.non_increasing_transitions == 0
    assert cell.duplicate_samples == 0
    assert cell.unobserved_tail_s == 0.0
    assert np.allclose(cell.efc, [0.0, 0.0625, 0.1875, 0.3125])
    assert np.allclose(cell.normalized_capacity, [1.0, 0.99, 0.96, 0.9])


def test_profile_parser_rejects_data_after_trailing_nan_rows():
    profile = PROFILE_CSV + "3600,1,3.5\n"

    with pytest.raises(ValueError, match="trailing only"):
        EXAMPLE.load_oxford_cell_from_text("fixture", profile, CAPACITY_CSV)


def test_oxford_mapping_canonicalizes_time_and_records_near_zero_tail():
    profile = """time_s,current_A
0,8
900,-8
900,-4
1800,16
1700,8
2700,0
"""
    capacity = """profile_time_s,capacity_Ah
0,16
900,15.9
1800,15.5
3000,15.0
"""

    cell = EXAMPLE.load_oxford_cell_from_text("fixture", profile, capacity)

    assert cell.non_increasing_transitions == 2
    assert cell.duplicate_samples == 1
    assert cell.canonical_profile_rows == 5
    assert cell.unobserved_tail_s == pytest.approx(300.0)
    assert np.all(np.diff(cell.efc) >= 0.0)


@pytest.mark.parametrize(
    ("profile", "capacity", "match"),
    [
        ("time_s,voltage_V\n0,3.7\n", CAPACITY_CSV, "current_A"),
        (PROFILE_CSV, "profile_time_s\n0\n", "capacity_Ah"),
        (PROFILE_CSV, "profile_time_s,capacity_Ah\n0,16\n", "At least two"),
        (
            PROFILE_CSV,
            "profile_time_s,capacity_Ah\n0,16\n0,15\n",
            "strictly increasing",
        ),
        (
            PROFILE_CSV,
            "profile_time_s,capacity_Ah\n0,16\n5001,15\n",
            "near-zero-current tail",
        ),
        (
            "time_s,current_A\n0,8\n2700,2\n",
            "profile_time_s,capacity_Ah\n0,16\n3000,15\n",
            "near-zero-current tail",
        ),
        (
            "time_s,current_A\n0,8\n2700,0\n",
            "profile_time_s,capacity_Ah\n0,16\n2800,15.5\n3000,15\n",
            "Only the final capacity check",
        ),
    ],
)
def test_oxford_mapping_rejects_invalid_inputs(profile, capacity, match):
    with pytest.raises(ValueError, match=match):
        EXAMPLE.load_oxford_cell_from_text("fixture", profile, capacity)
