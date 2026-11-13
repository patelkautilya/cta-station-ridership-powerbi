# CTA 'L' Station Entries | 2024–2025

An analyst case study of daily station entries reported by the Chicago Transit Authority (CTA). The package includes a reproducible Python extract, a compact Power BI input table, validation evidence, findings, and a two-page report export.

## Question

How did reported 'L' station entries vary across 2024–2025 by month, station, and CTA day type?

## Source and scope

- Official [CTA daily station entries dataset](https://data.cityofchicago.org/Transportation/CTA-Ridership-L-Station-Entries-Daily-Totals/5neh-572f) on the City of Chicago Data Portal; [Socrata API](https://data.cityofchicago.org/resource/5neh-572f.json).
- Fixed service-date window: **2024-01-01 through 2025-12-31**, inclusive. Extracted 2026-11-13 UTC; source update timestamp and SHA-256 hashes are in [`validation_summary.json`](validation_summary.json).
- Grain: one reported **station × service date** record. `rides` counts entries through station turnstiles, combined across entrances. CTA day-type labels are W (weekday), A (Saturday), and U (Sunday/holiday), as documented on the dataset page.
- [`build_dataset.py`](build_dataset.py) downloads the source, rejects duplicate station-date keys, unexpected day types and negative entries, and reconciles extracted totals with independent Socrata aggregation queries. Run `python build_dataset.py` with Python 3.10+ and internet access.
- [`cta_station_month_daytype_2024_2025.csv`](cta_station_month_daytype_2024_2025.csv) is the compact Power BI table: 10,350 **station × month × day type** rows with summed entries and observed station-days. The 105,082-row daily extract is reproducible locally and excluded from this repository to keep the public package small.

## Validated headline metrics

| Metric | Value |
|---|---:|
| Reported station entries, 2024–2025 | 225,706,465 |
| 2024 entries | 108,217,182 |
| 2025 entries | 117,489,283 |
| Service dates covered | 731 of 731 |
| Distinct station IDs | 144 |
| Station-date records | 105,082 |

The 2025 total is **8.57% higher** than the 2024 total in this extract. Calendar-day averages are 321,888 in 2025 and 295,675 in leap-year 2024, an **8.87% difference**. These are descriptive counts, not a causal estimate of demand growth. See [`FINDINGS.md`](FINDINGS.md) for station coverage and interpretation.

## Power BI report

- [Open the interactive Power BI report](https://app.powerbi.com/groups/e6426da3-9b36-4519-acf1-2434daa552ae/reports/b00d9eed-9986-450c-9bd9-ef1127adc1b2/04fe2fbf008da1de0a2d?experience=power-bi) (Microsoft sign-in or workspace access may be required).
- [View the two-page PDF export](CTA_Station_Ridership_Report.pdf) and page previews: [network overview](cta-report-preview-1.png) · [station detail](cta-report-preview-2.png).
- **Network overview:** total entries and observed station-days, monthly trend, day-type mix, and year and station filters.
- **Station detail:** station ranking, monthly trend, year and day-type filters. Selecting a station bar cross-filters the trend; the Lake/State selection was checked in the saved report and then cleared before export.

The PDF was exported with default values and both pages were visually checked. The model uses summed `rides` and `station_days` from the compact table; it does not contain the optional DAX measures in [`POWER_BI_BUILD.md`](POWER_BI_BUILD.md).

## Limits

Entries are not unique people or complete trips. Station entries do not reveal line boardings at multi-line stations. The extract includes zero-entry station-days and one station ID with only 549 of 731 dates; station availability and service changes affect comparisons. Monthly totals also reflect differing month lengths and CTA day-type composition. The data support descriptive patterns, not exposure-adjusted station performance or an explanation for why ridership changed.

