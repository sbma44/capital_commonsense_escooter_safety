"""Tests for the pure aggregate_* functions in build.py. No I/O, no network."""

from dc_escooter_injuries.build import (
    aggregate_breakdown_age,
    aggregate_breakdown_flags,
    aggregate_breakdown_match_source,
    aggregate_breakdown_ward,
    aggregate_timeseries_month,
    aggregate_timeseries_quarter,
    aggregate_timeseries_year,
)

# A small hand-built set of already-enriched rows (i.e. as they'd look after
# load_scooter_rows + enrich_with_dates), covering two quarters and a mix of
# severities so every aggregation has something real to count.
ROWS = [
    {
        "year": 2022, "year_month": "2022-01", "severity": "Minor",
        "age_band": "16-24", "IMPAIRED": "N", "SPEEDING": "N", "TICKETISSUED": "N",
        "ward": "Ward 1", "match_source": "moped_scooter",
    },
    {
        "year": 2022, "year_month": "2022-01", "severity": "None",
        "age_band": "16-24", "IMPAIRED": "N", "SPEEDING": "N", "TICKETISSUED": "N",
        "ward": "Ward 1", "match_source": "moped_scooter",
    },
    {
        "year": 2022, "year_month": "2022-04", "severity": "Major",
        "age_band": "25-34", "IMPAIRED": "Y", "SPEEDING": "Y", "TICKETISSUED": "Y",
        "ward": "Ward 2", "match_source": "moped_scooter",
    },
    {
        # no resolved REPORTDATE -- year-only fallback, excluded from month/quarter series
        "year": 2022, "year_month": None, "severity": "Fatal",
        "age_band": "Unknown", "IMPAIRED": "N", "SPEEDING": "N", "TICKETISSUED": "N",
        "ward": None, "match_source": "moped_or_motorized_bicycle",
    },
]


def test_aggregate_timeseries_month_excludes_unresolved_dates():
    out = aggregate_timeseries_month(ROWS)
    assert {"year_month": "2022-01", "severity": "Minor", "count": 1} in out
    assert {"year_month": "2022-01", "severity": "None", "count": 1} in out
    assert {"year_month": "2022-04", "severity": "Major", "count": 1} in out
    # the Fatal row has no year_month and must not show up anywhere
    assert sum(r["count"] for r in out) == 3


def test_aggregate_timeseries_quarter_groups_months_into_quarters():
    out = aggregate_timeseries_quarter(ROWS)
    assert {"year_quarter": "2022-Q1", "severity": "Minor", "count": 1} in out
    assert {"year_quarter": "2022-Q1", "severity": "None", "count": 1} in out
    assert {"year_quarter": "2022-Q2", "severity": "Major", "count": 1} in out
    assert sum(r["count"] for r in out) == 3


def test_aggregate_timeseries_year_includes_fallback_rows():
    out = aggregate_timeseries_year(ROWS)
    # unlike month/quarter, year uses the CCN-fallback year, so the Fatal row
    # with no year_month is still counted here
    assert sum(r["count"] for r in out) == 4
    assert {"year": 2022, "severity": "Fatal", "count": 1} in out


def test_aggregate_breakdown_age():
    out = aggregate_breakdown_age(ROWS)
    counts = {(r["age_band"], r["severity"]): r["count"] for r in out}
    assert counts[("16-24", "Minor")] == 1
    assert counts[("16-24", "None")] == 1
    assert counts[("25-34", "Major")] == 1
    assert counts[("Unknown", "Fatal")] == 1


def test_aggregate_breakdown_flags_covers_all_three_flag_types():
    out = aggregate_breakdown_flags(ROWS)
    flag_types = {r["flag_type"] for r in out}
    assert flag_types == {"impaired", "speeding", "ticket_issued"}
    impaired_yes = [r for r in out if r["flag_type"] == "impaired" and r["flag_value"] == "Y"]
    assert impaired_yes == [{"flag_type": "impaired", "flag_value": "Y", "severity": "Major", "count": 1}]


def test_aggregate_breakdown_ward_labels_missing_ward():
    out = aggregate_breakdown_ward(ROWS)
    counts = {(r["ward"], r["severity"]): r["count"] for r in out}
    assert counts[("Ward 1", "Minor")] == 1
    assert counts[("Unknown/unmatched", "Fatal")] == 1


def test_aggregate_breakdown_match_source():
    out = aggregate_breakdown_match_source(ROWS)
    counts = {(r["match_source"], r["year"]): r["count"] for r in out}
    assert counts[("moped_scooter", 2022)] == 3
    assert counts[("moped_or_motorized_bicycle", 2022)] == 1
