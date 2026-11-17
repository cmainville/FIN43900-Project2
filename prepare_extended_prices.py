"""Build the frozen 2016-10 through 2026-09 ETF CSV from five Yahoo chart JSONs.

This is an offline preparation tool. The Streamlit app never downloads data.
Pass one saved Yahoo daily chart response per ticker with explicit adjclose data.
"""

import argparse
import calendar
import csv
import json
import math
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


TICKERS = ("VTI", "VXUS", "XLE", "IWM", "IAU")
FIRST = (2016, 10)
LAST = (2026, 9)
NEW_YORK = ZoneInfo("America/New_York")


def months():
    year, month = FIRST
    while (year, month) <= LAST:
        yield year, month
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)


MONTHS = tuple(months())


def month_end(year, month):
    return date(year, month, calendar.monthrange(year, month)[1])


def read_monthly_adjusted(raw_path, ticker):
    """Use the last dated daily Adj Close in every completed calendar month."""
    payload = json.loads(Path(raw_path).read_text(encoding="utf-8"))
    if payload["chart"]["error"] is not None:
        raise ValueError(f"{ticker}: Yahoo chart error")
    result, = payload["chart"]["result"]
    metadata = result["meta"]
    if metadata.get("symbol") != ticker or metadata.get("currency") != "USD":
        raise ValueError(f"{ticker}: wrong Yahoo symbol or currency")
    timestamps = result["timestamp"]
    adjusted = result["indicators"]["adjclose"][0]["adjclose"]
    if len(timestamps) != len(adjusted) or not timestamps:
        raise ValueError(f"{ticker}: incomplete adjusted-close response")
    selected = {}
    seen_dates = set()
    for timestamp, price in zip(timestamps, adjusted):
        observed = datetime.fromtimestamp(timestamp, NEW_YORK).date()
        if observed in seen_dates:
            raise ValueError(f"{ticker}: duplicate daily observation {observed}")
        seen_dates.add(observed)
        key = (observed.year, observed.month)
        if key not in MONTHS:
            continue
        if key not in selected or observed > selected[key][0]:
            selected[key] = (observed, price)
    if set(selected) != set(MONTHS):
        missing = sorted(set(MONTHS) - set(selected))
        raise ValueError(f"{ticker}: missing months {missing}")
    for (year, month), (observed, price) in selected.items():
        if price is None or not math.isfinite(price) or price <= 0:
            raise ValueError(f"{ticker}: missing or invalid final adjusted price in {year}-{month:02d}")
        if (month_end(year, month) - observed).days > 4:
            raise ValueError(f"{ticker}: final observation too early in {year}-{month:02d}")
    return selected


def build_snapshot(raw_files, output):
    series = {ticker: read_monthly_adjusted(raw_files[ticker], ticker) for ticker in TICKERS}
    rows = [
        [month_end(year, month).isoformat()]
        + [format(series[ticker][(year, month)][1], ".12g") for ticker in TICKERS]
        for year, month in MONTHS
    ]
    with Path(output).open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(("Date", *TICKERS))
        writer.writerows(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for ticker in TICKERS:
        parser.add_argument(f"--{ticker.lower()}", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    files = {ticker: getattr(args, ticker.lower()) for ticker in TICKERS}
    rows = build_snapshot(files, args.output)
    print(f"Wrote {len(rows)} aligned monthly prices, {rows[0][0]} through {rows[-1][0]}")


if __name__ == "__main__":
    main()
