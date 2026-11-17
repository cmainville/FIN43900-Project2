"""Fixed-snapshot, five-ETF portfolio calculations for FIN 43900 Project 2."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

import numpy as np
import pandas as pd


TICKERS = ("VTI", "VXUS", "XLE", "IWM", "IAU")
DATA_PATH = Path(__file__).parent / "data" / "prices_growth.csv"
EXTENDED_DATA_PATH = Path(__file__).parent / "data" / "prices_growth_extended.csv"
EXTENDED_RAW_PATH = Path(__file__).parent / "data" / "yahoo_raw_extended_2026-11-16.zip"
RETURN_FLOOR = 0.06
GRID_UNITS = 20  # One unit is five percentage points.
MONITORING_THRESHOLD_POINTS = 20.0
SIGNAL_START = "2025-09-30"
SIGNAL_END = "2026-09-30"
SNAPSHOT_RETRIEVED = "2026-10-22"
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


def load_extended_prices(path: Path = EXTENDED_DATA_PATH) -> pd.DataFrame:
    """Read the separate 120-month Yahoo snapshot without altering the Lab 15 data."""
    frame = pd.read_csv(path)
    if tuple(frame.columns) != ("Date", *TICKERS):
        raise ValueError("Extended data needs exactly Date,VTI,VXUS,XLE,IWM,IAU columns.")
    dates = pd.to_datetime(frame["Date"], format="%Y-%m-%d", errors="raise")
    expected_dates = pd.date_range("2016-10-31", "2026-09-30", freq="ME")
    if len(frame) != 120 or not dates.equals(pd.Series(expected_dates, name="Date")):
        raise ValueError("Expected 120 unique, ordered month-end labels, 2016-10 through 2026-09.")
    try:
        prices = frame.loc[:, TICKERS].apply(pd.to_numeric, errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("Extended prices must be numeric.") from exc
    values = prices.to_numpy(dtype=float)
    if not np.isfinite(values).all() or not (values > 0).all():
        raise ValueError("Extended prices must be finite, positive, and complete.")
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


def estimate_extended(prices: pd.DataFrame) -> dict:
    """Use all 119 aligned returns in the supplementary ten-year snapshot."""
    if tuple(prices.columns) != TICKERS or len(prices) != 120:
        raise ValueError("Extended estimates require the five-ETF 120-price snapshot.")
    return estimate_from_returns(prices.pct_change(fill_method=None).iloc[1:])


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


def optimize(estimates: dict, floor: float = RETURN_FLOOR) -> dict:
    """Choose minimum variance among grid allocations meeting the stated floor."""
    if not math.isfinite(floor):
        raise ValueError("Return floor must be finite.")
    best = None
    feasible_count = 0
    candidate_count = 0
    for units in allocation_units():
        candidate_count += 1
        weights = dict(zip(TICKERS, (unit / GRID_UNITS for unit in units)))
        expected_return = float(weights_array(weights) @ estimates["returns"])
        if expected_return < floor - 1e-12:
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


def momentum_signal(prices: pd.DataFrame) -> list[dict]:
    """One cross-sectional trailing 12-month signal, using no post-cutoff price."""
    if tuple(prices.columns) != TICKERS:
        raise ValueError("Signal needs exactly the approved ETF columns.")
    start, end = pd.Timestamp(SIGNAL_START), pd.Timestamp(SIGNAL_END)
    if start not in prices.index or end not in prices.index:
        raise ValueError("Signal requires September 2025 and September 2026 observations.")
    if (end.year - start.year) * 12 + end.month - start.month != 12:
        raise ValueError("Signal observations must be 12 months apart.")
    starting = prices.loc[start, list(TICKERS)].to_numpy(dtype=float)
    ending = prices.loc[end, list(TICKERS)].to_numpy(dtype=float)
    if not np.isfinite(starting).all() or not np.isfinite(ending).all():
        raise ValueError("Signal prices must be finite.")
    if (starting <= 0).any() or (ending <= 0).any():
        raise ValueError("Signal prices must be positive.")
    values = ending / starting - 1
    ranked = sorted(zip(TICKERS, values), key=lambda pair: -pair[1])
    return [
        {"rank": rank, "ticker": ticker, "momentum": float(value)}
        for rank, (ticker, value) in enumerate(ranked, start=1)
    ]


def stressed_return(estimates: dict, ticker: str, delta: float) -> dict:
    """Change one annual arithmetic return estimate, leaving covariance fixed."""
    if ticker not in TICKERS or not math.isfinite(delta):
        raise ValueError("Invalid return stress input.")
    returns = estimates["returns"].copy()
    returns[TICKERS.index(ticker)] += delta
    return {**estimates, "returns": returns}


def stressed_volatility(estimates: dict, ticker: str, multiplier: float) -> dict:
    """Scale one volatility and its covariance row/column; correlations stay fixed."""
    if ticker not in TICKERS or not math.isfinite(multiplier) or multiplier <= 0:
        raise ValueError("Invalid volatility stress input.")
    covariance = estimates["covariance"]
    scale = np.ones(len(TICKERS))
    scale[TICKERS.index(ticker)] = multiplier
    stressed = covariance * np.outer(scale, scale)
    return {**estimates, "covariance": stressed}


def rebalance_costs(from_weights: dict, to_weights: dict, basis_points: float) -> dict:
    """One-time costs on total sales plus purchases, in portfolio fractions."""
    if not math.isfinite(basis_points) or basis_points < 0:
        raise ValueError("Execution cost must be nonnegative basis points.")
    traded = float(np.abs(weights_array(to_weights) - weights_array(from_weights)).sum())
    return {
        "one_way_turnover": traded / 2,
        "total_traded": traded,
        "cost": traded * basis_points / 10_000,
        "basis_points": basis_points,
    }


def process_status(data_valid: bool, full_solution: dict | None,
                   recent_solution: dict | None, unstable: bool | None) -> dict:
    """Hard failure outranks the monitoring review hold."""
    reasons = []
    if not data_valid:
        reasons.append("Required input data failed integrity checks.")
    if full_solution is None or not full_solution["feasible"]:
        reasons.append("No mandate-feasible full-window allocation.")
    if recent_solution is None or not recent_solution["feasible"]:
        reasons.append("No mandate-feasible recent-window allocation.")
    if reasons:
        return {"status": "HARD FAILURE", "reasons": reasons}
    if unstable:
        return {
            "status": "REVIEW HOLD",
            "reasons": ["An ETF weight changed by more than 20 percentage points between estimation windows."],
        }
    return {
        "status": "NO AUTOMATIC HOLD",
        "reasons": ["Required data and optimization checks pass; committee judgment is still pending."],
    }


def scenario_result(label: str, solution: dict, base_solution: dict) -> dict:
    """Package one rerun with its largest weight change from the base allocation."""
    change = None
    if solution["feasible"] and base_solution["feasible"]:
        change = largest_weight_change(
            base_solution["result"]["weights"], solution["result"]["weights"]
        )
    return {"label": label, "solution": solution, "change": change}


def analyze(path: Path = DATA_PATH) -> dict:
    prices = load_prices(path)
    full = estimate(prices)
    recent = estimate(prices, last_36=True)
    optimized_full = optimize(full)
    optimized_recent = optimize(recent)
    estimation_scenarios = [
        scenario_result(
            "IAU annual return estimate −5 percentage points",
            optimize(stressed_return(full, "IAU", -0.05)),
            optimized_full,
        ),
        scenario_result(
            "IAU annualized volatility ×1.25; correlations fixed",
            optimize(stressed_volatility(full, "IAU", 1.25)),
            optimized_full,
        ),
    ]
    constraint_scenarios = [
        scenario_result(
            f"Illustrative return floor {floor:.0%}" if floor != RETURN_FLOOR
            else "Approved return floor 6%",
            optimized_full if floor == RETURN_FLOOR else optimize(full, floor=floor),
            optimized_full,
        )
        for floor in (0.06, 0.16, 0.25)
    ]
    cost_scenarios = (
        [rebalance_costs(LAB15_REFERENCE, optimized_full["result"]["weights"], bps)
         for bps in (0, 10, 25)]
        if optimized_full["feasible"] else []
    )
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
        "momentum": momentum_signal(prices),
        "estimation_scenarios": estimation_scenarios,
        "constraint_scenarios": constraint_scenarios,
        "cost_scenarios": cost_scenarios,
        "process": process_status(True, optimized_full, optimized_recent, triggered),
    }


def analyze_extended(base_analysis: dict, path: Path = EXTENDED_DATA_PATH) -> dict:
    """Supplementary robustness evidence; original 59/36 results stay frozen."""
    prices = load_extended_prices(path)
    estimates = estimate_extended(prices)
    solution = optimize(estimates)
    windows = [
        ("Extended 119 returns", estimates, solution),
        ("Original 59 returns", base_analysis["full"], base_analysis["optimized_full"]),
        ("Recent 36 returns", base_analysis["recent"], base_analysis["optimized_recent"]),
    ]
    comparisons = []
    for left_index, right_index in ((0, 1), (0, 2), (1, 2)):
        left_name, _, left_solution = windows[left_index]
        right_name, _, right_solution = windows[right_index]
        change = None
        if left_solution["feasible"] and right_solution["feasible"]:
            change = largest_weight_change(
                left_solution["result"]["weights"], right_solution["result"]["weights"]
            )
        comparisons.append({
            "left": left_name,
            "right": right_name,
            "largest_change": change,
            "supplementary_threshold_breach": (
                stability_trigger(change[1]) if change is not None and left_index == 0 else None
            ),
        })
    volatilities = np.sqrt(np.diag(estimates["covariance"]))
    correlations = estimates["covariance"] / np.outer(volatilities, volatilities)
    common_risks = {
        name: portfolio_metrics(window_solution["result"]["weights"], estimates)["volatility"]
        if window_solution["feasible"] else None
        for name, _, window_solution in windows
    }
    return {
        "source_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "raw_archive_sha256": hashlib.sha256(EXTENDED_RAW_PATH.read_bytes()).hexdigest(),
        "windows": windows,
        "comparisons": comparisons,
        "volatilities": volatilities,
        "correlations": correlations,
        "common_covariance_risks": common_risks,
    }


def report_markdown(analysis: dict, extended: dict | None = None) -> str:
    """Format actual engine results for the repository's visible output artifact."""
    def weights_text(result: dict) -> str:
        return " / ".join(f"{result['weights'][ticker]:.0%}" for ticker in TICKERS)

    lines = [
        "# Executed Portfolio Output — Milestone 4A",
        "",
        "Generated by `python3 -m portfolio_engine` from the frozen datasets; no values were entered by hand.",
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
        "## One cross-sectional momentum signal",
        "",
        f"Starting adjusted-price observation: **{SIGNAL_START}**; ending observation/cutoff: **{SIGNAL_END}**; frozen snapshot retrieved **{SNAPSHOT_RETRIEVED}**. The snapshot's availability is documented at retrieval, not claimed at the September cutoff. Formula for each ETF: ending adjusted price / starting adjusted price − 1. Ranking is descriptive and is not an optimizer input.",
        "",
        "| Rank | ETF | Trailing 12-month adjusted-price return |",
        "| ---: | --- | ---: |",
    ]
    for row in analysis["momentum"]:
        lines.append(f"| {row['rank']} | {row['ticker']} | {row['momentum']:.2%} |")
    lines += [
        "",
        "## Estimation sensitivity — full-window base inputs",
        "",
        "| Hypothetical scenario | Feasible | Weights | Estimated return | Estimated volatility | Feasible candidates | Largest change vs base |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    def scenario_row(scenario):
        solution = scenario["solution"]
        result = solution["result"]
        change = scenario["change"]
        movement = "—" if change is None else (
            "0 points" if change[1] < 1e-9 else f"{change[0]} {change[1]:.0f} points"
        )
        return_text = f"{result['return']:.2%}" if result else "—"
        volatility_text = f"{result['volatility']:.2%}" if result else "—"
        return (
            f"| {scenario['label']} | {'YES' if solution['feasible'] else 'NO'} | "
            f"{weights_text(result) if result else '—'} | "
            f"{return_text} | {volatility_text} | "
            f"{solution['feasible_count']:,}/{solution['candidate_count']:,} | {movement} |"
        )
    for scenario in analysis["estimation_scenarios"]:
        lines.append(scenario_row(scenario))
    lines += [
        "",
        "The IAU return cut changes only that annual estimate by −5 percentage points; covariance and other returns stay fixed. The 6% floor remains slack, so zero weight movement does **not** establish robustness to return estimation error. The IAU volatility shock multiplies IAU's annualized volatility by 1.25, holds correlations fixed, and scales its covariance row/column consistently.",
        "",
        "## One-time B → C execution cost",
        "",
        "Cost is applied per dollar traded to both sales and purchases. One-way turnover = 0.5 × sum of absolute weight changes; total traded fraction = the full sum. This is a one-time implementation estimate, not an annual-return deduction.",
        "",
        "| Cost assumption | One-way turnover | Total buy + sell volume | One-time cost / portfolio |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for row in analysis["cost_scenarios"]:
        lines.append(
            f"| {row['basis_points']:.0f} bps | {row['one_way_turnover']:.1%} | "
            f"{row['total_traded']:.1%} | {row['cost']:.3%} |"
        )
    lines += [
        "",
        "## Return-floor sensitivity — unchanged full-window estimates",
        "",
        "The 16% and 25% floors are illustrative scenarios, not approved mandate changes.",
        "",
        "| Return floor | Feasible | Weights | Estimated return | Estimated volatility | Feasible candidates | Largest change vs 6% base |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for scenario in analysis["constraint_scenarios"]:
        lines.append(scenario_row(scenario))
    lines += [
        "",
        "## Process stop rule",
        "",
        "HARD FAILURE pauses implementation for invalid required data or no feasible optimized allocation. REVIEW HOLD pauses implementation when an otherwise feasible allocation moves by more than 20 percentage points between the full and recent windows; further independent review and committee authorization are required. A hold is not a permanent suitability judgment.",
        "",
        f"**Current status: {analysis['process']['status']}** — "
        + " ".join(analysis["process"]["reasons"]),
    ]
    if extended is not None:
        lines += [
            "",
            "## Supplementary ten-year historical robustness",
            "",
            f"New Yahoo Finance daily Adj Close snapshot retrieved **2026-11-16**, labeled 2016-10-31 through 2026-09-30. It contains 120 aligned prices and 119 returns. CSV SHA-256: `{extended['source_sha256']}`; archived raw responses SHA-256: `{extended['raw_archive_sha256']}`. The original Lab 15 CSV remains unchanged for its 59- and 36-return windows; the two downloads are not spliced. See [source and replay notes](../data/extended-provenance.md).",
            "",
            "| Window and source | Optimized weights | Est. annual return | Est. annual volatility | Feasible candidates | 6% floor |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
        for name, estimates, solution in extended["windows"]:
            result = solution["result"]
            floor_state = (
                "Slack for all grid candidates"
                if solution["feasible_count"] == solution["candidate_count"]
                else "Binding at selected allocation"
                if result is not None and abs(result["return"] - RETURN_FLOOR) < 1e-10
                else "Slack at selected allocation"
            )
            return_text = f"{result['return']:.2%}" if result else "—"
            volatility_text = f"{result['volatility']:.2%}" if result else "—"
            lines.append(
                f"| {name} | {weights_text(result) if result else 'Infeasible'} | "
                f"{return_text} | {volatility_text} | "
                f"{solution['feasible_count']:,}/{solution['candidate_count']:,} | {floor_state} |"
            )
        lines += [
            "",
            "ETF arithmetic annual return and sample annualized volatility estimates (each window uses its own frozen source):",
            "",
            "| Window | ETF | Return estimate | Volatility estimate |",
            "| --- | --- | ---: | ---: |",
        ]
        for name, estimates, _ in extended["windows"]:
            for index, ticker in enumerate(TICKERS):
                lines.append(
                    f"| {name} | {ticker} | {estimates['returns'][index]:.2%} | "
                    f"{math.sqrt(estimates['covariance'][index, index]):.2%} |"
                )
        lines += [
            "",
            "Largest individual allocation moves:",
            "",
            "| Windows compared | Largest move | Threshold interpretation |",
            "| --- | --- | --- |",
        ]
        for comparison in extended["comparisons"]:
            ticker, points = comparison["largest_change"] or ("—", float("nan"))
            interpretation = (
                "Supplementary >20-point breach"
                if comparison["supplementary_threshold_breach"] is True
                else "Supplementary ≤20 points"
                if comparison["supplementary_threshold_breach"] is False
                else "Approved 59-vs-36 monitoring rule"
            )
            lines.append(
                f"| {comparison['left']} vs {comparison['right']} | "
                f"{ticker} {points:.0f} percentage points | {interpretation} |"
            )
        base = analysis["optimized_full"]["result"]["weights"]
        recent = analysis["optimized_recent"]["result"]["weights"]
        long = extended["windows"][0][2]["result"]["weights"]
        lines += [
            "",
            f"Concentration by window, extended / original / recent: **IAU {long['IAU']:.0%} / {base['IAU']:.0%} / {recent['IAU']:.0%}**; **VTI {long['VTI']:.0%} / {base['VTI']:.0%} / {recent['VTI']:.0%}**; **VXUS {long['VXUS']:.0%} / {base['VXUS']:.0%} / {recent['VXUS']:.0%}**. The ten-year evidence retains and increases gold concentration; it does not make VXUS a core weight under the approved minimum-variance objective.",
            "",
            "### IAU covariance and diversification",
            "",
            f"On the extended window, IAU standalone volatility is **{extended['volatilities'][-1]:.2%}**. Its correlations with VTI / VXUS / XLE / IWM are "
            + " / ".join(f"{value:.3f}" for value in extended["correlations"][-1, :-1])
            + ". Low IAU correlation with VTI helps the 50/50 mix reduce estimated portfolio volatility below either standalone ETF. This is a covariance result, not proof that a 50% gold holding suits a 15-year investor.",
            "",
            "Supplementary risk comparison: evaluate each window's optimized weights on the **same extended-window covariance matrix** (these are not the optimization-window volatility figures):",
            "",
            "| Portfolio chosen from | Volatility on common extended covariance |",
            "| --- | ---: |",
        ]
        for name, risk in extended["common_covariance_risks"].items():
            lines.append(f"| {name} | {risk:.2%} |")
        lines += [
            "",
            "The historical momentum ranking puts XLE first and IAU last, while the extended minimum-variance mix holds 0% XLE and 50% IAU. That disagreement is expected when one measure ranks backward-looking returns and the optimizer minimizes estimated covariance risk. Momentum has not been validated as a forecast and does not enter the optimizer.",
            "",
            "The windows overlap and use different sample estimates. Their own estimated volatilities are not directly like-for-like, and this exercise is **not** an independent out-of-sample backtest. The approved implementation status remains the original 59-vs-36 **REVIEW HOLD**; the extended comparisons are separately labeled supplemental evidence.",
        ]
    lines += [
        "",
        "## Limits",
        "",
        "Annual arithmetic returns and covariance are historical estimates, not compound growth forecasts or guarantees. The five-point grid is approximate. Revised adjusted-price histories can change a reconstructed signal; the original October snapshot is not a September point-in-time archive, and the new November snapshot is not a contemporaneous archive. Cost figures are hypothetical, exclude taxes, and may omit other implementation frictions. The signal and scenarios do not establish future performance or investment suitability. No final recommendation or allocation range is made.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    base_analysis = analyze()
    print(report_markdown(base_analysis, analyze_extended(base_analysis)), end="")
