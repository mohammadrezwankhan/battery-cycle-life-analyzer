"""Offline tests for the Oxford real-data example's CSV mapping."""

from types import TracebackType
from typing import Literal, Optional

import numpy as np
import pytest

from examples import oxford_energy_trading as example

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
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.requested_bytes: Optional[int] = None

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Literal[False]:
        return False

    def read(self, requested_bytes: int) -> bytes:
        self.requested_bytes = requested_bytes
        return self.payload[:requested_bytes]


def test_download_text_uses_a_bounded_read(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _FakeResponse(b"\xef\xbb\xbftime_s,current_A\n0,0\n")
    monkeypatch.setattr(
        example,
        "urlopen",
        lambda _request, **_kwargs: response,
    )

    text = example._download_text("https://ora.ox.ac.uk/profile.csv")

    assert text.startswith("time_s,current_A")
    assert response.requested_bytes == example.MAX_DOWNLOAD_BYTES + 1


def test_download_text_rejects_payload_over_safety_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _FakeResponse(b"12345")
    monkeypatch.setattr(example, "MAX_DOWNLOAD_BYTES", 4)
    monkeypatch.setattr(
        example,
        "urlopen",
        lambda _request, **_kwargs: response,
    )

    with pytest.raises(ValueError, match="4-byte safety limit"):
        example._download_text("https://ora.ox.ac.uk/oversized.csv")


def test_load_oxford_cell_from_text_maps_official_headers() -> None:
    cell = example.load_oxford_cell_from_text(
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


def test_profile_parser_rejects_data_after_trailing_nan_rows() -> None:
    profile = PROFILE_CSV + "3600,1,3.5\n"

    with pytest.raises(ValueError, match="trailing only"):
        example.load_oxford_cell_from_text("fixture", profile, CAPACITY_CSV)


def test_oxford_mapping_canonicalizes_time_and_records_near_zero_tail() -> None:
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

    cell = example.load_oxford_cell_from_text("fixture", profile, capacity)

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
def test_oxford_mapping_rejects_invalid_inputs(profile: str, capacity: str, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        example.load_oxford_cell_from_text("fixture", profile, capacity)


@pytest.mark.parametrize(
    "url",
    [
        "http://ora.ox.ac.uk/file",
        "file:///etc/passwd",
        "https://evil.test/file",
        "https://ora.ox.ac.uk.evil.test/file",
        "https://user:pass@ora.ox.ac.uk/file",
        "https://ora.ox.ac.uk:444/file",
    ],
)
def test_download_rejects_unapproved_origin_before_opening(
    url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unexpected_open(*_args: object, **_kwargs: object) -> None:
        pytest.fail("an invalid URL reached the network opener")

    monkeypatch.setattr(example, "urlopen", unexpected_open)
    with pytest.raises(ValueError, match="HTTPS"):
        example._download_text(url)


def test_download_redirects_keep_the_approved_https_origin() -> None:
    import io
    from http.client import HTTPMessage
    from urllib.request import Request

    handler = example._ArchiveRedirectHandler()
    request = Request("https://ora.ox.ac.uk/original")
    for url in ("http://ora.ox.ac.uk/file", "https://evil.test/file", "file:///tmp/file"):
        with pytest.raises(ValueError, match="HTTPS"):
            handler.redirect_request(request, io.BytesIO(), 302, "Found", HTTPMessage(), url)
    redirected = handler.redirect_request(
        request, io.BytesIO(), 302, "Found", HTTPMessage(), "https://ora.ox.ac.uk/approved"
    )
    assert redirected is not None
    assert redirected.full_url == "https://ora.ox.ac.uk/approved"
