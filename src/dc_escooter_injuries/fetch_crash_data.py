"""Fetch DC's "Crash Details" table into data/raw/.

This is the person-level crash detail extract the whole analysis is built on:
one row per person-per-vehicle involved in an MPD-reported crash. DDOT
publishes it as a live ArcGIS table (companion to the "Crashes in DC" point
layer that build.py queries directly for REPORTDATE/WARD):

    https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Public_Safety_WebMercator/MapServer/25

It's a live, growing dataset -- MPD adds crashes continuously -- so re-running
this will pull more rows than whatever count is cited in this repo's output.

Usage:
    uv run fetch-crash-data
"""

import csv
import json
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = REPO_ROOT / "data" / "raw" / "crash_details_table.csv"

QUERY_URL = (
    "https://maps2.dcgis.dc.gov/dcgis/rest/services/"
    "DCGIS_DATA/Public_Safety_WebMercator/MapServer/25/query"
)
FIELDS = [
    "CRIMEID", "CCN", "PERSONID", "PERSONTYPE", "AGE", "FATAL", "MAJORINJURY",
    "MINORINJURY", "VEHICLEID", "INVEHICLETYPE", "TICKETISSUED",
    "LICENSEPLATESTATE", "IMPAIRED", "SPEEDING", "OBJECTID",
]
PAGE_SIZE = 1000  # server-enforced maxRecordCount
MAX_WORKERS = 8   # polite parallelism against a public government endpoint


def _query(params: dict) -> dict:
    encoded = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(QUERY_URL, data=encoded)
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read())
    if "error" in payload:
        raise RuntimeError(f"ArcGIS query error: {payload['error']}")
    return payload


def _total_count() -> int:
    payload = _query({"where": "1=1", "returnCountOnly": "true", "f": "json"})
    return payload["count"]


def _fetch_page(offset: int) -> list[dict]:
    payload = _query({
        "where": "1=1",
        "outFields": ",".join(FIELDS),
        "orderByFields": "OBJECTID",
        "resultOffset": offset,
        "resultRecordCount": PAGE_SIZE,
        "f": "json",
    })
    return [feat["attributes"] for feat in payload["features"]]


def fetch_all() -> list[dict]:
    total = _total_count()
    offsets = list(range(0, total, PAGE_SIZE))
    print(f"{total} rows to fetch in {len(offsets)} pages of {PAGE_SIZE}...")

    pages: dict[int, list[dict]] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for offset, page in zip(offsets, pool.map(_fetch_page, offsets)):
            pages[offset] = page
            if len(pages) % 20 == 0 or len(pages) == len(offsets):
                print(f"  fetched {len(pages)}/{len(offsets)} pages")

    rows = []
    for offset in offsets:
        rows.extend(pages[offset])
    return rows


def main() -> None:
    print(f"Fetching DC's Crash Details table from {QUERY_URL} ...")
    rows = fetch_all()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
