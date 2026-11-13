"""Build a reproducible 2024–2025 CTA station-entry extract and BI aggregate.

Source: https://data.cityofchicago.org/Transportation/CTA-Ridership-L-Station-Entries-Daily-Totals/5neh-572f
Run: python build_dataset.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import time
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
API = "https://data.cityofchicago.org/resource/5neh-572f.json"
META = "https://data.cityofchicago.org/api/views/5neh-572f.json"
START = date(2024, 1, 1)
END = date(2025, 12, 31)
PAGE_SIZE = 20000
RAW = ROOT / "cta_station_daily_2024_2025.csv"
AGG = ROOT / "cta_station_month_daytype_2024_2025.csv"
VALIDATION = ROOT / "validation_summary.json"


def fetch_json(url: str) -> object:
    for attempt in range(6):
        try:
            request = Request(url, headers={"User-Agent": "analyst-portfolio-reproducible-study/1.0"})
            with urlopen(request, timeout=90) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 5:
                raise
            time.sleep(min(60, 2 ** attempt * 2))
        except (TimeoutError, URLError):
            if attempt == 5:
                raise
            time.sleep(min(60, 2 ** attempt * 2))
    raise RuntimeError("Unable to fetch source")


def query(params: dict[str, str | int]) -> object:
    return fetch_json(f"{API}?{urlencode(params)}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    metadata = fetch_json(META)
    assert isinstance(metadata, dict)
    where = "date >= '2024-01-01T00:00:00' and date < '2026-01-01T00:00:00'"
    source_summary = query({
        "$where": where,
        "$select": "count(*) as rows, sum(rides) as rides, count(distinct station_id) as stations, count(distinct date) as dates, min(date) as first_date, max(date) as last_date",
    })
    assert isinstance(source_summary, list) and len(source_summary) == 1
    source_summary = source_summary[0]

    daily: list[tuple[str, str, str, str, int]] = []
    offset = 0
    while True:
        page = query({
            "$select": "station_id,stationname,date,daytype,rides",
            "$where": where,
            "$order": "date,station_id",
            "$limit": PAGE_SIZE,
            "$offset": offset,
        })
        assert isinstance(page, list)
        for item in page:
            service_date = date.fromisoformat(item["date"][:10])
            if not START <= service_date <= END:
                raise ValueError(f"Out-of-window date: {service_date}")
            rides = int(item["rides"])
            if rides < 0:
                raise ValueError(f"Negative rides: {item}")
            daytype = item["daytype"]
            if daytype not in {"W", "A", "U"}:
                raise ValueError(f"Unexpected day type: {daytype}")
            daily.append((str(item["station_id"]), item["stationname"], service_date.isoformat(), daytype, rides))
        offset += len(page)
        print(f"Fetched {offset:,} rows")
        if len(page) < PAGE_SIZE:
            break

    keys = [(row[0], row[2]) for row in daily]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate station-date rows")
    names: dict[str, set[str]] = defaultdict(set)
    days: dict[str, set[str]] = defaultdict(set)
    totals = Counter()
    years = Counter()
    daytypes = Counter()
    aggregate: dict[tuple[str, str, str, str], list[int]] = defaultdict(lambda: [0, 0])
    for station_id, station_name, service_date, daytype, rides in daily:
        names[station_id].add(station_name)
        days[service_date].add(station_id)
        totals["rides"] += rides
        years[service_date[:4]] += rides
        daytypes[daytype] += rides
        key = (service_date[:7], station_id, station_name, daytype)
        aggregate[key][0] += rides
        aggregate[key][1] += 1

    if len(daily) != int(source_summary["rows"]):
        raise ValueError("Row count differs from independent Socrata aggregate")
    if totals["rides"] != int(source_summary["rides"]):
        raise ValueError("Ride total differs from independent Socrata aggregate")
    if len(names) != int(source_summary["stations"]):
        raise ValueError("Station count differs from independent Socrata aggregate")
    if len(days) != 731 or len(days) != int(source_summary["dates"]):
        raise ValueError("Not all 731 service dates are covered")
    if min(days) != START.isoformat() or max(days) != END.isoformat():
        raise ValueError("Unexpected date range")
    source_years = {}
    for year in (2024, 2025):
        result = query({
            "$where": f"date >= '{year}-01-01T00:00:00' and date < '{year + 1}-01-01T00:00:00'",
            "$select": "count(*) as rows, sum(rides) as rides, count(distinct date) as dates",
        })
        assert isinstance(result, list) and len(result) == 1
        source_years[str(year)] = result[0]
        if years[str(year)] != int(result[0]["rides"]):
            raise ValueError(f"{year} total differs from independent Socrata aggregate")
        if int(result[0]["dates"]) != (366 if year == 2024 else 365):
            raise ValueError(f"Incomplete {year} date coverage")
    metadata_after = fetch_json(META)
    assert isinstance(metadata_after, dict)
    if metadata_after.get("rowsUpdatedAt") != metadata.get("rowsUpdatedAt"):
        raise RuntimeError("Source dataset updated during extraction; rerun for a consistent snapshot")

    with RAW.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["station_id", "station_name", "service_date", "day_type", "rides"])
        writer.writerows(daily)
    with AGG.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["month", "year", "station_id", "station_name", "day_type", "rides", "station_days"])
        for (month, station_id, station_name, daytype), (rides, station_days) in sorted(aggregate.items()):
            writer.writerow([month, month[:4], station_id, station_name, daytype, rides, station_days])

    validation = {
        "source": META,
        "dataset_page": "https://data.cityofchicago.org/Transportation/CTA-Ridership-L-Station-Entries-Daily-Totals/5neh-572f",
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_rows_updated_at_unix": metadata.get("rowsUpdatedAt"),
        "window": {"start": START.isoformat(), "end": END.isoformat()},
        "daily_rows": len(daily),
        "distinct_stations": len(names),
        "distinct_dates": len(days),
        "total_entries": totals["rides"],
        "entries_by_year": dict(sorted(years.items())),
        "entries_by_day_type": dict(sorted(daytypes.items())),
        "station_name_variants": {station_id: sorted(values) for station_id, values in names.items() if len(values) > 1},
        "stations_per_date_min": min(map(len, days.values())),
        "stations_per_date_max": max(map(len, days.values())),
        "stations_per_date_mean": round(sum(map(len, days.values())) / len(days), 3),
        "aggregate_rows": len(aggregate),
        "aggregate_entries": sum(value[0] for value in aggregate.values()),
        "aggregate_station_days": sum(value[1] for value in aggregate.values()),
        "zero_entry_station_days": sum(row[4] == 0 for row in daily),
        "source_query_years": source_years,
        "source_query_summary": source_summary,
        "files": {
            RAW.name: {"bytes": RAW.stat().st_size, "sha256": sha256(RAW)},
            AGG.name: {"bytes": AGG.stat().st_size, "sha256": sha256(AGG)},
        },
    }
    if validation["aggregate_entries"] != totals["rides"] or validation["aggregate_station_days"] != len(daily):
        raise ValueError("Aggregate reconciliation failed")
    VALIDATION.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: validation[key] for key in ("daily_rows", "distinct_stations", "distinct_dates", "total_entries", "entries_by_year", "aggregate_rows")}, indent=2))


if __name__ == "__main__":
    main()
