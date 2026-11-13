# Findings and caveats

## Validation

The fixed 2024–2025 source snapshot contains **105,082 unique station-date records**, **144 station IDs**, and all **731 service dates**. The total is **225,706,465 entries**. Independent Socrata count/sum queries matched the full extract and each year: 52,522 rows and 108,217,182 entries in 2024; 52,560 rows and 117,489,283 entries in 2025. The curated month/station/day-type table reconciles to the same entries and station-days. Exact source update time, files, and SHA-256 hashes are recorded in [`validation_summary.json`](validation_summary.json).

## Observations

1. **Reported entries rose across the two annual totals.** The 2025 count exceeds 2024 by 9,272,101, or **8.57%**. Since 2024 had 366 dates and 2025 had 365, the calendar-day average moved from about 295,675 to 321,888 entries (**8.87%**). This adjustment only accounts for number of dates, not station availability or service changes.
2. **October was the largest month in each year.** October 2024 had 10,748,721 entries; October 2025 had 11,593,208. Month comparisons should consider the number and mix of W/A/U days.
3. **Coverage varies by station.** There are 143 station records on 182 dates and 144 on 549 dates. Station ID 41710 (Damen-Lake) appears on 549 dates, beginning 2024-07-01. The dataset also contains **1,156 zero-entry station-days**, including 562 each for Berwyn and Lawrence. A count of station IDs therefore should not be read as the count of stations with positive entries on every date.

## Interpretation limits

- CTA defines these as combined station turnstile entries, not unique riders, complete trips, or route-level boardings. A rider can enter more than once. No fare, population, or service-exposure denominator is provided.
- W means weekday, A means Saturday, and U means Sunday/holiday in this dataset. Holiday treatment means day types are not identical to weekdays derived from the calendar.
- The source can be revised after extraction. Re-run the script and compare hashes and the source update timestamp before using this as a current operational report.
- Station availability, temporary closures, route/service changes, weather, events, and other factors could influence the observed pattern. This case does not attribute causality.

Source: [CTA daily station entries](https://data.cityofchicago.org/Transportation/CTA-Ridership-L-Station-Entries-Daily-Totals/5neh-572f), City of Chicago Data Portal, dataset ID `5neh-572f`.
