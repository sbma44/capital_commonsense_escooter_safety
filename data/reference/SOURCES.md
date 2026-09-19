# Reference data sources

Small, hand-collected datasets checked directly into this repo because
they're either static (DDOT stopped publishing updates) or not available
through any API (manually scraped from a JS dashboard). Everything else
(`data/raw/`) is fetched fresh by `fetch_crash_data.py` and by `build.py`'s
live queries against DDOT's own ArcGIS services.

## `ddot_monthly_scooter_ridership.csv`

- **What**: DDOT's own published monthly e-scooter trip counts, Jan 2019-Feb
  2022.
- **Source**: [ddot.dc.gov/page/dockless-api](https://ddot.dc.gov/page/dockless-api),
  linked spreadsheet "Monthly Ride Data for the Shared Fleet Electric Scooter
  Program (2019-2022)":
  `https://ddot.dc.gov/sites/default/files/dc/sites/ddot/page_content/attachments/YOY%20scooter%20ridership_1.xlsx`
- **Fetched**: September 2026. The spreadsheet was not being updated as of
  that date (DDOT appears to have moved to the Ride Report dashboard below
  instead) -- re-check the URL before assuming this file is still current.
- **Caveat**: ridership (trips/month), not fleet size. DDOT does not publish
  a historical device-count series, only point-in-time regulatory fleet caps
  (2018: 2,400; 2019: 6,000; 2020: 20,000 bikes+scooters; Oct 2022: up to
  25,000), which are not the same as vehicles actually deployed.

## `ride_report_quarterly_scooter_stats.csv`

- **What**: Quarterly scooter trip counts and average daily active vehicles
  (real fleet size), Q1 2019-Q2 2026.
- **Source**: [public.ridereport.com/dc](https://public.ridereport.com/dc)
  (DDOT's public dashboard, built by vendor Ride Report), "Scooters" filter.
  There is no public API or stable export URL for this dashboard -- it's a
  JS-rendered page. Each row was collected by navigating to
  `https://public.ridereport.com/dc?vehicle=scooter&time=<YYYY>-Q<N>` for
  each quarter and reading off "Average Vehicles" and "Total Trips".
- **Collected**: September 2026, via browser automation (Claude in Chrome).
  To redo/extend this: open the URL above for each quarter of interest and
  read the same two stats, or use the page's "Download Data" button if it
  exposes a machine-readable export by the time you're reading this.
- **`coverage_reliable` column**: cross-checked against
  `ddot_monthly_scooter_ridership.csv` for the overlapping 2019-2021 period.
  Ride Report's own trip counts covered only ~2% of DDOT's reported total in
  2019-Q1, rising to ~34% by 2021-Q1, ~88% by 2021-Q3, and ~99% by 2021-Q4 --
  a data-coverage ramp-up as operators onboarded to Ride Report's feed, not
  real ~90x ridership growth. `coverage_reliable=True` from 2021-Q4 onward;
  everything earlier is kept for transparency but should not be plotted or
  compared at face value. See `build.py`'s `load_ride_report_quarterly()` and
  `output/DATA_NOTES.md` (generated) for how this is used.
