# Data directory

- **`raw/`** -- gitignored. Populated by `uv run fetch-crash-data`, which
  pulls DC MPD's full "Crash Details" table live from DDOT's public ArcGIS
  API. Not checked in: it's ~85MB and growing (the dataset is live), so
  there's no fixed version to commit -- run the fetch script instead of
  looking for a file here.
- **`reference/`** -- small, checked-in datasets that either can't be fetched
  programmatically (hand-scraped from a JS dashboard) or are frozen
  historical publications no longer being updated. See `reference/SOURCES.md`
  for exactly where each one came from and how to refresh or extend it.
