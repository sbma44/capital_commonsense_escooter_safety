"""Sanity checks against the checked-in data/reference/ CSVs. No network."""

from dc_escooter_injuries.build import load_ride_report_quarterly, load_ridership_by_quarter


def test_ddot_ridership_loads_and_sums_to_quarters():
    ridership = load_ridership_by_quarter()
    assert ridership, "expected data/reference/ddot_monthly_scooter_ridership.csv to be non-empty"

    # Jan 2019 = 124833, Feb 2019 = 178720, Mar 2019 = 310192 rides (DDOT's own figures)
    total, n_months = ridership["2019-Q1"]
    assert total == 124833 + 178720 + 310192
    assert n_months == 3

    # the series is documented to end Feb 2022 -- a partial (2-month) quarter
    total_q1_2022, n_months_q1_2022 = ridership["2022-Q1"]
    assert n_months_q1_2022 == 2
    assert "2022-Q2" not in ridership


def test_ride_report_stats_load_and_flag_reliability():
    ride_report = load_ride_report_quarterly()
    assert ride_report, "expected data/reference/ride_report_quarterly_scooter_stats.csv to be non-empty"

    # 2019-Q1 is known-unreliable (covers ~2% of DDOT's own reported trips)
    assert ride_report["2019-Q1"]["coverage_reliable"] is False
    # 2021-Q4 onward is the documented reliability cutoff
    assert ride_report["2021-Q4"]["coverage_reliable"] is True

    for row in ride_report.values():
        assert isinstance(row["total_trips"], int)
        assert row["total_trips"] >= 0
