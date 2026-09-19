"""Unit tests for build.py's pure row-level transform functions. No I/O, no network."""

import pytest

from dc_escooter_injuries.build import age_band_of, match_source, quarter_of, severity_of


@pytest.mark.parametrize(
    "invehicletype,expected",
    [
        ("Moped/scooter", "moped_scooter"),
        ("Moped/Scooter", "moped_scooter"),  # inconsistent casing in the real data
        ("moped/scooter", "moped_scooter"),
        ("Moped or motorized bicycle", "moped_or_motorized_bicycle"),
        ("  Moped or motorized bicycle  ", "moped_or_motorized_bicycle"),  # stray whitespace
        ("MOPED OR MOTORIZED BICYCLE", "moped_or_motorized_bicycle"),
        ("Passenger Car/automobile", None),
        ("Motor Cycle", None),
        ("Low Speed Vehicle", None),
        ("", None),
        (None, None),
    ],
)
def test_match_source(invehicletype, expected):
    assert match_source(invehicletype) == expected


@pytest.mark.parametrize(
    "fatal,major,minor,expected",
    [
        ("Y", "Y", "Y", "Fatal"),  # fatal wins even if other flags also set
        ("Y", "N", "N", "Fatal"),
        ("N", "Y", "Y", "Major"),  # major wins over minor
        ("N", "Y", "N", "Major"),
        ("N", "N", "Y", "Minor"),
        ("N", "N", "N", "None"),
    ],
)
def test_severity_of_hierarchy(fatal, major, minor, expected):
    assert severity_of(fatal, major, minor) == expected


@pytest.mark.parametrize(
    "year_month,expected",
    [
        ("2019-01", "2019-Q1"),
        ("2019-03", "2019-Q1"),
        ("2019-04", "2019-Q2"),
        ("2019-06", "2019-Q2"),
        ("2019-07", "2019-Q3"),
        ("2019-09", "2019-Q3"),
        ("2019-10", "2019-Q4"),
        ("2019-12", "2019-Q4"),
    ],
)
def test_quarter_of(year_month, expected):
    assert quarter_of(year_month) == expected


@pytest.mark.parametrize(
    "age,expected",
    [
        ("15", "<16"),
        ("0", "<16"),
        ("16", "16-24"),
        ("24", "16-24"),
        ("25", "25-34"),
        ("64", "55-64"),
        ("65", "65+"),
        ("120", "65+"),
        ("", "Unknown"),
        (None, "Unknown"),
        ("not a number", "Unknown"),
    ],
)
def test_age_band_of(age, expected):
    assert age_band_of(age) == expected
