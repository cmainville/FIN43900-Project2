"""Fixed-snapshot, five-ETF portfolio calculations for FIN 43900 Project 2."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

import numpy as np
import pandas as pd


TICKERS = ("VTI", "VXUS", "XLE", "IWM", "IAU")
DATA_PATH = Path(__file__).parent / "data" / "prices_growth.csv"
RETURN_FLOOR = 0.06
GRID_UNITS = 20  # One unit is five percentage points.
MONITORING_THRESHOLD_POINTS = 20.0
EQUAL_WEIGHT = dict.fromkeys(TICKERS, 0.20)
LAB15_REFERENCE = dict(zip(TICKERS, (0.45, 0.25, 0.10, 0.10, 0.10)))
WARNING = (
    "REVIEW REQUIRED — Allocation instability exceeds the "
    "20-percentage-point monitoring threshold."
)


def load_prices(path: Path = DATA_PATH) -> pd.DataFrame:
    """Read the frozen Yahoo snapshot and enforce its exact schema and window."""
    frame = pd.read_csv(path)
    if tuple(frame.columns) != ("Date", *TICKERS):
        raise ValueError("Expected exactly Date,VTI,VXUS,XLE,IWM,IAU columns.")
    dates = pd.to_datetime(frame["Date"], format="%Y-%m-%d", errors="raise")
    expected_dates = pd.date_range("2021-10-31", "2026-09-30", freq="ME")
    if len(frame) != 60 or not dates.equals(pd.Series(expected_dates, name="Date")):
        raise ValueError("Expected 60 unique, ordered calendar month-end labels, 2021-10 through 2026-09.")
    try:
        prices = frame.loc[:, TICKERS].apply(pd.to_numeric, errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("Prices must be numeric.") from exc
    values = prices.to_numpy(dtype=float)
    if not np.isfinite(values).all() or not (values > 0).all():
        raise ValueError("Prices must be finite, positive, and complete.")
    prices.index = pd.DatetimeIndex(dates)
    return prices


def estimate_from_returns(monthly: pd.DataFrame) -> dict:
    """Estimate annual moments from aligned monthly simple returns."""
    if tuple(monthly.columns) != TICKERS or len(monthly) < 2:
        raise ValueError("Need at least two aligned return rows for the approved ETFs.")
    if not np.isfinite(monthly.to_numpy(dtype=float)).all():
        raise ValueError("Monthly returns must be finite.")
    expected_returns = monthly.mean().to_numpy(dtype=float) * 12
    covariance = monthly.cov().to_numpy(dtype=float) * 12
    if not np.isfinite(expected_returns).all() or not np.isfinite(covariance).all():
        raise ValueError("Nonfinite return or covariance estimate.")
    if not np.allclose(covariance, covariance.T, atol=1e-12):
        raise ValueError("Covariance matrix is not symmetric.")
    return {
        "returns": expected_returns,
        "covariance": covariance,
        "observations": len(monthly),
        "start": monthly.index[0].date().isoformat(),
        "end": monthly.index[-1].date().isoformat(),
    }


def estimate(prices: pd.DataFrame, last_36: bool = False) -> dict:
    """Estimate moments for the approved full or recent frozen window."""
    if tuple(prices.columns) != TICKERS:
        raise ValueError("Price columns do not match the approved ETF universe.")
    monthly = prices.pct_change(fill_method=None).iloc[1:]
    if last_36:
        monthly = monthly.tail(36)
    if len(monthly) != (36 if last_36 else 59):
        raise ValueError("Wrong number of aligned monthly returns.")
    return estimate_from_returns(monthly)


def weights_array(weights: dict[str, float]) -> np.ndarray:
    if set(weights) != set(TICKERS):
        raise ValueError("Weights must use exactly the five approved ETFs.")
    values = np.array([weights[ticker] for ticker in TICKERS], dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Weights must be finite.")
    return values


def portfolio_metrics(weights: dict[str, float], estimates: dict) -> dict:
    w = weights_array(weights)
    expected_return = float(w @ estimates["returns"])
    variance = float(w @ estimates["covariance"] @ w)
    if variance < -1e-12:
        raise ValueError("Portfolio variance is materially negative.")
    return {
        "return": expected_return,
        "variance": max(variance, 0.0),
        "volatility": math.sqrt(max(variance, 0.0)),
    }


def mandate_verdict(weights: dict[str, float], expected_return: float) -> dict:
    """Report construction checks and the separate provisional return objective."""
    reasons = []
    if set(weights) != set(TICKERS):
        reasons.append("unapproved or missing ETF")
        return {"hard_pass": False, "objective_pass": False, "pass": False, "reasons": reasons}
    w = weights_array(weights)
    if not math.isclose(float(w.sum()), 1.0, abs_tol=1e-10):
        reasons.append("weights do not total 100%")
    if (w < -1e-12).any():
        reasons.append("negative weight violates long-only/no-shorting rule")
    # The approved five ETFs are unlevered positions; no borrowing or derivatives
    # are introduced by these nonnegative, fully invested ETF weights.
    hard_pass = not reasons
    objective_pass = expected_return >= RETURN_FLOOR - 1e-12
    if not objective_pass:
        reasons.append("estimated annual nominal return is below the provisional 6% floor")
    return {
        "hard_pass": hard_pass,
        "objective_pass": objective_pass,
        "pass": hard_pass and objective_pass,
        "reasons": reasons,
    }


def assess(weights: dict[str, float], estimates: dict) -> dict:
    metrics = portfolio_metrics(weights, estimates)
    return {
        "weights": weights,
        **metrics,
        "verdict": mandate_verdict(weights, metrics["return"]),
    }


def allocation_units(remaining: int = GRID_UNITS, assets: int = len(TICKERS)):
    """Enumerate every nonnegative, fully invested five-point allocation once."""
    if assets == 1:
        yield (remaining,)
    else:
        for first in range(remaining + 1):
            for rest in allocation_units(remaining - first, assets - 1):
                yield (first, *rest)


def optimize(estimates: dict) -> dict:
    """Choose minimum variance among grid allocations meeting the 6% floor."""
    best = None
    feasible_count = 0
    candidate_count = 0
    for units in allocation_units():
        candidate_count += 1
        weights = dict(zip(TICKERS, (unit / GRID_UNITS for unit in units)))
        expected_return = float(weights_array(weights) @ estimates["returns"])
        if expected_return < RETURN_FLOOR - 1e-12:
            continue
        feasible_count += 1
        candidate = assess(weights, estimates)
        # First enumerated allocation wins a tie within numerical tolerance.
        if best is None or candidate["variance"] < best["variance"] - 1e-12:
            best = candidate
    return {
        "feasible": best is not None,
        "result": best,
        "candidate_count": candidate_count,
        "feasible_count": feasible_count,
    }


def largest_weight_change(first: dict, second: dict) -> tuple[str, float]:
    """Return first ticker with the largest absolute weight change, in points."""
    a, b = weights_array(first), weights_array(second)
    changes = np.abs(a - b) * 100
    index = int(np.argmax(changes))
    return TICKERS[index], float(changes[index])


def stability_trigger(points: float) -> bool:
    return points > MONITORING_THRESHOLD_POINTS + 1e-9


def analyze(path: Path = DATA_PATH) -> dict:
    prices = load_prices(path)
    full = estimate(prices)
    recent = estimate(prices, last_36=True)
    optimized_full = optimize(full)
    optimized_recent = optimize(recent)
    if not optimized_full["feasible"] or not optimized_recent["feasible"]:
        change = None
        triggered = None
    else:
        change = largest_weight_change(
            optimized_full["result"]["weights"], optimized_recent["result"]["weights"]
        )
        triggered = stability_trigger(change[1])
    return {
        "source_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "full": full,
        "recent": recent,
        "portfolios": {
            "A — Equal Weight": assess(EQUAL_WEIGHT, full),
            "B — Lab 15 Reference": assess(LAB15_REFERENCE, full),
            "C — Constrained Minimum Volatility": optimized_full["result"],
        },
        "optimized_full": optimized_full,
        "optimized_recent": optimized_recent,
        "vti_benchmark": assess(dict(zip(TICKERS, (1.0, 0.0, 0.0, 0.0, 0.0))), full),
        "largest_change": change,
        "stability_triggered": triggered,
    }


def report_markdown(analysis: dict) -> str:
    """Format actual engine results for the repository's visible output artifact."""
    def weights_text(result: dict) -> str:
        return " / ".join(f"{result['weights'][ticker]:.0%}" for ticker in TICKERS)

    lines = [
        "# Executed Portfolio Output — Milestone 2",
        "",
        "Generated by `python3 -m portfolio_engine` from the frozen dataset; no values were entered by hand.",
        "",
        f"- Dataset: `data/prices_growth.csv` (SHA-256 `{analysis['source_sha256']}`)",
        "- Source: Yahoo Finance daily `Adj Close`, retrieved 2026-10-22 in Lab 15; last available trading day per completed month, labeled calendar month-end.",
        f"- Price labels: 2021-10-31 through 2026-09-30; full returns: {analysis['full']['observations']} ({analysis['full']['start']} to {analysis['full']['end']}); recent returns: {analysis['recent']['observations']} ({analysis['recent']['start']} to {analysis['recent']['end']}).",
        "- Mandate: 15-year flexible horizon; five approved ETFs; fully invested, long-only, no leverage/shorts/derivatives; minimize estimated annualized volatility subject to provisional ≥6% annual nominal arithmetic expected return; no reserve, sector, or asset cap.",
        "- Weight order in tables: VTI / VXUS / XLE / IWM / IAU.",
        "",
        "## Three portfolios — full historical window",
        "",
        "| Portfolio | Weights | Estimated annual return | Estimated annual volatility | Hard rules | 6% objective | Mandate verdict / failed rule |",
        "| --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for name, result in analysis["portfolios"].items():
        if result is None:
            lines.append(f"| {name} | — | — | — | — | — | Infeasible |")
            continue
        verdict = result["verdict"]
        detail = "PASS" if verdict["pass"] else "FAIL: " + "; ".join(verdict["reasons"])
        lines.append(
            f"| {name} | {weights_text(result)} | {result['return']:.2%} | "
            f"{result['volatility']:.2%} | {'PASS' if verdict['hard_pass'] else 'FAIL'} | "
            f"{'PASS' if verdict['objective_pass'] else 'FAIL'} | {detail} |"
        )
    benchmark = analysis["vti_benchmark"]
    lines += [
        "",
        f"External market benchmark: **VTI** (100% VTI), estimated return **{benchmark['return']:.2%}**, estimated volatility **{benchmark['volatility']:.2%}** on the same full window. It is not one of the two required baseline portfolios.",
        "",
        "## Window stability",
        "",
        "| Estimation window | Optimized weights | Estimated annual return | Estimated annual volatility | Feasible grid candidates |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for label, key in (("Full: 59 returns", "optimized_full"), ("Recent: 36 returns", "optimized_recent")):
        solution = analysis[key]
        result = solution["result"]
        if result is None:
            lines.append(f"| {label} | Infeasible | — | — | {solution['feasible_count']}/{solution['candidate_count']} |")
        else:
            lines.append(
                f"| {label} | {weights_text(result)} | {result['return']:.2%} | "
                f"{result['volatility']:.2%} | {solution['feasible_count']}/{solution['candidate_count']} |"
            )
    if analysis["largest_change"] is None:
        lines.append("\nLargest change: unavailable because at least one window is infeasible.")
    else:
        ticker, points = analysis["largest_change"]
        lines.append(f"\nLargest absolute ETF weight change: **{ticker}, {points:.0f} percentage points**.")
        if analysis["stability_triggered"]:
            lines.append(f"\n{WARNING}")
        else:
            lines.append("\nMonitoring threshold not breached (trigger is strictly more than 20 points).")
    lines += [
        "",
        "## Limits",
        "",
        "Annual arithmetic returns and covariance are historical estimates, not compound growth forecasts or guarantees. The five-point grid is approximate. The window comparison is a monitoring test, not a hard feasibility rule. This output does not assess costs, taxes, future drawdowns, signal quality, or investment suitability and is not a recommendation.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(report_markdown(analyze()), end="")
