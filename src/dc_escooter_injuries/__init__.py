"""DC scooter-rider crash injury analysis.

Two entry points, meant to run in order:

    uv run fetch-crash-data   # populates data/raw/crash_details_table.csv
    uv run build-analysis     # reads data/raw + data/reference -> output/
"""

from dc_escooter_injuries import build, fetch_crash_data


def fetch_crash_data_main() -> None:
    fetch_crash_data.main()


def build_main() -> None:
    build.main()
