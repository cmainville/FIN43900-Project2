# Supplementary ten-year price snapshot provenance

**Retrieved:** 2026-11-16. **Source:** Yahoo Finance chart API, one USD-listed ETF response each for VTI, VXUS, XLE, IWM, and IAU. [Yahoo's adjusted-close explanation](https://in.help.yahoo.com/kb/adjusted-close-sln28256.html) describes split and dividend adjustments. The public responses were downloaded with a standard browser user agent after initial HTTP 429 responses without it. This is a new download and is separate from the Lab 15 five-year snapshot.

The request for each ticker was:

```text
https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}?period1=1475280000&period2=1790812800&interval=1d&events=history&includeAdjustedClose=true
```

The explicit interval is daily; the requested UTC bounds are 2016-10-01 through 2026-10-01 (exclusive). Every saved response identified its expected ticker and USD currency and contained `indicators.adjclose[0].adjclose`. The [raw responses](yahoo_raw_extended_2026-11-16.zip) are archived in the repository, so later vendor revisions cannot silently change this analysis.

| Frozen artifact | SHA-256 |
| --- | --- |
| `prices_growth_extended.csv` | `d011f64fddc6c3d68ce6301a655375563875fc7272b3e28f76f37d9092b93c34` |
| `yahoo_raw_extended_2026-11-16.zip` | `de32e16737f9d003af9b13dc18bb8032e36eb9833c73c0d7efcad8aeea9d296f` |

Raw response entry hashes, in ETF order:

| Entry | SHA-256 |
| --- | --- |
| `VTI.json` | `3322945192d6301acab8e00bd80892df5100d4e99f24d21a88276b9cc0f648ab` |
| `VXUS.json` | `a6b23bdd332b2f04321ad0358e0f4e80046800ae6d1658db3bd68194b86198b5` |
| `XLE.json` | `c4d9749b4029772ab49231536b59a60f2d03071f36969c4860e5de80945a2793` |
| `IWM.json` | `2a479850b93d5ff5cb5db1ef34a7019e15c9098fc3f377a0953b06140b58e3` |
| `IAU.json` | `87d3fabbc900da6be8acc6569309960d38f79061f0e9b3c65c69ac3b20f18b6c` |

[`prepare_extended_prices.py`](../prepare_extended_prices.py) converts each UTC timestamp to the New York trading date, takes the final dated daily **adjusted** close in each completed calendar month, and labels the stored row by calendar month-end. It uses the same `Adj Close` field for all ETFs and stores 12 significant digits. It rejects a wrong symbol/currency, absent or invalid month-end adjusted price, duplicate daily date, missing month, or an implausibly early final observation. The resulting CSV has **120 aligned month labels, 2016-10-31 through 2026-09-30**, and therefore **119 monthly simple returns**. The application reads only the frozen CSV and makes no live request.

To reproduce the snapshot offline, extract the ZIP and run the preparation script with `--vti VTI.json --vxus VXUS.json --xle XLE.json --iwm IWM.json --iau IAU.json --output rebuilt.csv`. This was run on 2026-11-16 and `cmp` confirmed the rebuilt file is byte-for-byte identical to `prices_growth_extended.csv`.

**Overlap with the original Lab 15 snapshot:** The newer and older five-year rows have the same labels but are not byte-for-byte identical. Of 300 overlapping ETF-month prices, **151 are exactly equal**; the largest absolute displayed-price difference is **0.000061035 for VTI**. The differences are small and consistent with vendor precision/history revisions, but their cause was not independently established. The Project 2 app keeps the original 59- and 36-return calculations on the unchanged Lab 15 CSV. It uses the new ten-year CSV only for supplementary robustness analysis and never splices the two sources.

These historical adjusted prices were downloaded on 2026-11-16; this document does **not** claim they were archived at their original observation dates or that a future Yahoo download will match.
