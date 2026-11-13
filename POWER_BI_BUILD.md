# Power BI report implementation and acceptance checks

## Model

The saved semantic model **CTA Station Ridership | 2024-2025** imports `cta_station_month_daytype_2024_2025.csv`. The report **CTA Station Ridership | Station & Day-Type Review** has two pages. It uses implicit SUM aggregation for `rides` and `station_days`. `year` and `month` support chronological review; the compact grain has no daily date drill.

Optional DAX enhancements, **not implemented in the saved report**:

```DAX
Entries = SUM('CTA'[rides])
Station-Days = SUM('CTA'[station_days])
Entries per Station-Day = DIVIDE([Entries], [Station-Days])
Active Stations = COUNTROWS(FILTER(VALUES('CTA'[station_id]), CALCULATE([Entries]) > 0))
```

`Entries per Station-Day` is a weighted station-day average. Do not average precomputed ratios by row. `Active Stations` is the count of station IDs with positive entries in the current filter context; it does not mean a station was open throughout the selected window.

## Page 1: Network overview

- KPI cards: summed entries and observed station-days.
- Year range and station-name slicers.
- Monthly entry trend, chronologically ordered.
- Donut chart of summed entries by CTA day type (W/A/U).

## Page 2: Station detail

- Station ranking bar chart and monthly entry trend.
- Year range and day-type slicers.
- Click a station bar to cross-filter the trend. This interaction was checked with Lake/State: the monthly chart rescaled to that station's series, then returned to the full-window baseline after clearing the selection.

## Checks before publication

- Full window: 225,706,465 entries; 2024: 108,217,182; 2025: 117,489,283.
- All-day-type entries: W 176,007,221; A 27,045,939; U 22,653,305.
- Year/day-type/station filters change all dependent visuals consistently. Confirm at least one drill interaction and reset filters before export.
- Export two pages, inspect each visually, publish PDF and PNG previews with working public links, and add truthful report links to README/profile/site. Power BI service access may require sign-in.

