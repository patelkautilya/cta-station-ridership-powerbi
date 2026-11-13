# Power BI report plan and acceptance checks

## Model

Import the public raw URL for `cta_station_month_daytype_2024_2025.csv` after the repository is created. Keep `station_id` as text, `year` as a whole number, `month` as a sortable month date or a text YYYY-MM field sorted chronologically, `rides` and `station_days` as whole numbers, and `day_type` as text. No daily date drill is available in this aggregate; drill from year to month and from station rank to station detail.

Suggested DAX:

```DAX
Entries = SUM('CTA'[rides])
Station-Days = SUM('CTA'[station_days])
Entries per Station-Day = DIVIDE([Entries], [Station-Days])
Active Stations = COUNTROWS(FILTER(VALUES('CTA'[station_id]), CALCULATE([Entries]) > 0))
```

`Entries per Station-Day` is a weighted station-day average. Do not average precomputed ratios by row. `Active Stations` is the count of station IDs with positive entries in the current filter context; it does not mean a station was open throughout the selected window.

## Page 1: system overview

- KPI cards: Entries, Active Stations, Entries per Station-Day.
- Year selector (2024–2025) and CTA day-type selector (W/A/U).
- Monthly entry trend, chronologically ordered.
- Top stations by entries with ranking and clear count units.
- Source/window and interpretation note on the page.

## Page 2: station detail

- Station selector or drill-through from the ranking chart.
- Monthly entries for selected station and day-type mix.
- Sortable station table with entries, station-days, and weighted entries per station-day.
- Show full-window baseline when no station filter is active. Verify that exporting from a drill-through test does not leave the page inadvertently filtered.

## Checks before publication

- Full window: 225,706,465 entries; 2024: 108,217,182; 2025: 117,489,283.
- All-day-type entries: W 176,007,221; A 27,045,939; U 22,653,305.
- Year/day-type/station filters change all dependent visuals consistently. Confirm at least one drill interaction and reset filters before export.
- Export two pages, inspect each visually, publish PDF and PNG previews with working public links, and add truthful report links to README/profile/site. Power BI service access may require sign-in.
