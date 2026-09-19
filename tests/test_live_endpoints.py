"""Smoke tests against DDOT's real ArcGIS endpoints.

Excluded from the default `pytest` run (see the `live` marker in
pyproject.toml) -- these hit real public infrastructure, so they're opt-in:

    uv run pytest -m live

Each test fetches at most a handful of rows. None of them page through the
full dataset -- that's what `uv run fetch-crash-data` is for, not a test.
"""

import urllib.request

import pytest

from dc_escooter_injuries import fetch_crash_data
from dc_escooter_injuries.build import FEATURE_SERVER_QUERY_URL, fetch_crash_dates

pytestmark = pytest.mark.live


def test_crash_details_endpoint_is_reachable_and_has_rows():
    """MapServer/25 (fetch_crash_data.py's source) responds and is non-trivially sized."""
    total = fetch_crash_data._total_count()
    # sanity floor, not an exact match -- this is a live, growing dataset
    assert total > 800_000


def test_crash_details_endpoint_schema_matches_expected_fields():
    """A single tiny page has exactly the fields fetch_crash_data.py expects."""
    page = fetch_crash_data._fetch_page(offset=0)
    assert page, "expected at least one row back from a live query"

    first_row = page[0]
    assert set(first_row.keys()) == set(fetch_crash_data.FIELDS)


def test_crashes_in_dc_join_endpoint_resolves_a_real_crimeid():
    """The date/ward join endpoint (MapServer/24, used by build.py) round-trips
    a real CRIMEID pulled live from the Crash Details table."""
    sample_crimeid = fetch_crash_data._fetch_page(offset=0)[0]["CRIMEID"]

    result = fetch_crash_dates([sample_crimeid])

    # Not every CRIMEID resolves (some crashes have no geocoded location, see
    # README caveat 2) -- but the query itself must succeed and, when it does
    # resolve, come back shaped the way build.py expects.
    if sample_crimeid in result:
        info = result[sample_crimeid]
        assert set(info.keys()) == {"year", "year_month", "ward"}


def test_crashes_in_dc_query_url_is_reachable():
    """Confirms the URL build.py hardcodes still resolves to a live ArcGIS service."""
    req = urllib.request.Request(
        FEATURE_SERVER_QUERY_URL,
        data=b"where=1%3D1&returnCountOnly=true&f=json",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        assert resp.status == 200
