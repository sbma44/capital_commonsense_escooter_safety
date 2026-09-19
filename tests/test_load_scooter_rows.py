"""Tests for load_scooter_rows against a small synthetic CSV. No network, no real data file."""

import csv

from dc_escooter_injuries.build import load_scooter_rows

FIELDNAMES = [
    "CRIMEID", "CCN", "PERSONID", "PERSONTYPE", "AGE", "FATAL", "MAJORINJURY",
    "MINORINJURY", "VEHICLEID", "INVEHICLETYPE", "TICKETISSUED",
    "LICENSEPLATESTATE", "IMPAIRED", "SPEEDING", "OBJECTID",
]

SAMPLE_ROWS = [
    # a scooter rider with a minor injury
    dict(
        CRIMEID="1", CCN="19100001", PERSONID="p1", PERSONTYPE="Driver", AGE="29",
        FATAL="N", MAJORINJURY="N", MINORINJURY="Y", VEHICLEID="v1",
        INVEHICLETYPE="Moped/scooter", TICKETISSUED="N", LICENSEPLATESTATE="None",
        IMPAIRED="N", SPEEDING="N", OBJECTID="1",
    ),
    # the post-2023 scooter code, uninjured
    dict(
        CRIMEID="2", CCN="23100002", PERSONID="p2", PERSONTYPE="Driver", AGE="",
        FATAL="N", MAJORINJURY="N", MINORINJURY="N", VEHICLEID="v2",
        INVEHICLETYPE="Moped or motorized bicycle", TICKETISSUED="Y",
        LICENSEPLATESTATE="Unknown", IMPAIRED="N", SPEEDING="Y", OBJECTID="2",
    ),
    # not a scooter at all -- must be filtered out
    dict(
        CRIMEID="3", CCN="19100003", PERSONID="p3", PERSONTYPE="Driver", AGE="40",
        FATAL="N", MAJORINJURY="N", MINORINJURY="N", VEHICLEID="v3",
        INVEHICLETYPE="Passenger Car/automobile", TICKETISSUED="N",
        LICENSEPLATESTATE="DC", IMPAIRED="N", SPEEDING="N", OBJECTID="3",
    ),
]


def _write_sample_csv(path):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(SAMPLE_ROWS)


def test_filters_to_scooter_rows_only(tmp_path):
    csv_path = tmp_path / "crash_details_table.csv"
    _write_sample_csv(csv_path)

    rows = load_scooter_rows(csv_path)

    assert {r["CRIMEID"] for r in rows} == {"1", "2"}


def test_derives_severity_match_source_and_year(tmp_path):
    csv_path = tmp_path / "crash_details_table.csv"
    _write_sample_csv(csv_path)

    rows = {r["CRIMEID"]: r for r in load_scooter_rows(csv_path)}

    assert rows["1"]["severity"] == "Minor"
    assert rows["1"]["match_source"] == "moped_scooter"
    assert rows["1"]["year_ccn"] == 2019
    assert rows["1"]["age_band"] == "25-34"

    assert rows["2"]["severity"] == "None"
    assert rows["2"]["match_source"] == "moped_or_motorized_bicycle"
    assert rows["2"]["year_ccn"] == 2023
    assert rows["2"]["age_band"] == "Unknown"


def test_missing_file_raises(tmp_path):
    missing = tmp_path / "does_not_exist.csv"
    try:
        load_scooter_rows(missing)
    except SystemExit as e:
        assert "fetch-crash-data" in str(e)
    else:
        raise AssertionError("expected SystemExit for a missing source file")
