"""FIN 43900 Project 2 portfolio decision application."""

import streamlit as st

from portfolio_engine import (
    SIGNAL_END,
    SIGNAL_START,
    SNAPSHOT_RETRIEVED,
    TICKERS,
    WARNING,
    analyze,
)


st.set_page_config(page_title="FIN 43900 | Portfolio Decision System", layout="wide")


@st.cache_data
def results():
    return analyze()


def weight_table(result):
    return [{"ETF": ticker, "Weight": f"{result['weights'][ticker]:.0%}"} for ticker in TICKERS]


def weights_text(result):
    return " / ".join(f"{result['weights'][ticker]:.0%}" for ticker in TICKERS)


def scenario_rows(scenarios):
    rows = []
    for scenario in scenarios:
        solution = scenario["solution"]
        result = solution["result"]
        change = scenario["change"]
        movement = (
            "—" if change is None else
            "0 pp" if change[1] < 1e-9 else
            f"{change[0]} {change[1]:.0f} pp"
        )
        rows.append({
            "Scenario": scenario["label"],
            "Feasible": "YES" if solution["feasible"] else "NO",
            "Weights (VTI / VXUS / XLE / IWM / IAU)": weights_text(result) if result else "—",
            "Estimated return": f"{result['return']:.2%}" if result else "—",
            "Estimated volatility": f"{result['volatility']:.2%}" if result else "—",
            "Feasible candidates": f"{solution['feasible_count']:,}/{solution['candidate_count']:,}",
            "Largest change vs 6% base": movement,
        })
    return rows


def show_portfolio(name, result):
    st.subheader(name)
    if result is None:
        st.error("No feasible portfolio meets the provisional 6% expected-return floor.")
        return
    st.table(weight_table(result))
    left, right = st.columns(2)
    left.metric("Estimated annual arithmetic return", f"{result['return']:.2%}")
    right.metric("Estimated annualized volatility", f"{result['volatility']:.2%}")
    verdict = result["verdict"]
    st.write(
        f"Hard rules: **{'PASS' if verdict['hard_pass'] else 'FAIL'}** · "
        f"Provisional 6% return objective: **{'PASS' if verdict['objective_pass'] else 'FAIL'}** · "
        f"Mandate verdict: **{'PASS' if verdict['pass'] else 'FAIL'}**"
    )
    if verdict["reasons"]:
        st.error("Failed rule(s): " + "; ".join(verdict["reasons"]))
    else:
        st.caption("Passes modeled mandate checks; this is not an investment suitability verdict.")


st.title("FIN 43900 | Portfolio Decision System")
st.caption("Fixed historical snapshot · Estimated results, not a recommendation")
try:
    data = results()
except (OSError, ValueError) as exc:
    st.error(f"HARD FAILURE — Required input data or optimization failed: {exc}")
    st.stop()

mandate_tab, portfolio_tab, signal_tab, decision_tab = st.tabs(
    ["Mandate & Data", "Portfolio Analysis", "Signal & Stress Tests", "Committee Decision"]
)

with mandate_tab:
    st.header("Mandate & Data")
    st.write(
        "Client: a young investor accumulating wealth over a **15-year horizon**, "
        "with flexibility to remain invested longer. The horizon is planning context."
    )
    st.write(
        "Objective: minimize estimated annualized volatility while targeting at least "
        "**6% expected annual nominal return**. The return floor is provisional, not guaranteed."
    )
    st.write(
        "Hard rules: weights total 100%; long-only; no leverage, short selling, or derivatives; "
        "only VTI, VXUS, XLE, IWM, and IAU. No required cash/Treasury reserve, sector or asset cap, "
        "or maximum-volatility ceiling."
    )
    st.table(
        [
            {"ETF": "VTI", "Role": "U.S. total equity market"},
            {"ETF": "VXUS", "Role": "International equities"},
            {"ETF": "XLE", "Role": "U.S. energy sector"},
            {"ETF": "IWM", "Role": "Russell 2000 small-cap equities"},
            {"ETF": "IAU", "Role": "Gold exposure"},
        ]
    )
    st.write(
        "Data: frozen Yahoo Finance daily adjusted closing prices from Lab 15, retrieved "
        "2026-10-22. Each completed month's final available trading-day price is labeled "
        "by calendar month-end. Price labels: October 2021–September 2026; "
        "full estimation uses 59 monthly simple returns."
    )
    st.caption(f"Local snapshot: data/prices_growth.csv · SHA-256 {data['source_sha256']}")
    st.caption(
        "Annual return estimates are monthly arithmetic mean ×12; annual covariance is "
        "sample monthly covariance ×12. Historical estimates are not growth forecasts."
    )

with portfolio_tab:
    st.header("Portfolio Analysis")
    st.caption(
        "All three portfolios use full-window estimates. The two baselines are kept "
        "unchanged even if a mandate rule fails."
    )
    for name, result in data["portfolios"].items():
        show_portfolio(name, result)
    st.subheader("External market benchmark")
    benchmark = data["vti_benchmark"]
    st.write(
        f"VTI (100% VTI): estimated annual return **{benchmark['return']:.2%}**; "
        f"estimated annualized volatility **{benchmark['volatility']:.2%}** "
        "on the same full window. VTI is not one of the two required baselines."
    )

with signal_tab:
    st.header("Signal & Stress Tests")
    st.subheader("One cross-sectional momentum signal")
    st.write(
        f"Trailing 12-month adjusted-price return, {SIGNAL_START} to {SIGNAL_END}; "
        f"frozen snapshot retrieved {SNAPSHOT_RETRIEVED}. Ranking is evidence only, "
        "not an optimizer input or automatic allocation instruction."
    )
    st.table([
        {"Rank": row["rank"], "ETF": row["ticker"],
         "12-month adjusted-price momentum": f"{row['momentum']:.2%}"}
        for row in data["momentum"]
    ])
    with st.expander("Signal data card"):
        st.write(
            "Source: Yahoo Finance daily Adj Close in the frozen Lab 15 CSV. "
            "Formula: September 2026 adjusted price ÷ September 2025 adjusted price − 1. "
            "The observation cutoff is September 30, 2026; the documented retrieval "
            "and availability boundary is October 22, 2026. No later prices or forward returns are used. "
            "A missing or nonpositive endpoint makes the signal unavailable. Adjusted histories "
            "can be revised, and this later snapshot is not proof of what was archived on September 30."
        )
    st.subheader("Estimation-window stability")
    for label, key in (("Full history · 59 monthly returns", "optimized_full"),
                       ("Recent history · last 36 monthly returns", "optimized_recent")):
        solution = data[key]
        result = solution["result"]
        st.write(f"**{label}** — {solution['feasible_count']:,} feasible of "
                 f"{solution['candidate_count']:,} grid allocations")
        if result is None:
            st.error("No mix meets the provisional 6% expected-return floor.")
        else:
            st.table(weight_table(result))
            st.write(
                f"Estimated annual return: **{result['return']:.2%}** · "
                f"Estimated annualized volatility: **{result['volatility']:.2%}**"
            )
    if data["largest_change"] is None:
        st.warning("Allocation change is unavailable because a window is infeasible.")
    else:
        ticker, points = data["largest_change"]
        st.write(f"Largest absolute allocation change: **{ticker}, {points:.0f} percentage points**.")
        if data["stability_triggered"]:
            st.error(WARNING)
        else:
            st.success("Allocation instability monitoring threshold not breached.")
    st.caption(
        "The threshold is a monitoring trigger only; historical minimum volatility "
        "does not guarantee future stability."
    )
    st.subheader("Estimation sensitivity")
    st.table(scenario_rows(data["estimation_scenarios"]))
    st.caption(
        "The IAU return cut leaves weights unchanged because the 6% floor remains slack; "
        "zero movement does not prove return estimates are reliable. The volatility shock "
        "keeps correlations fixed and rebuilds covariance."
    )
    st.subheader("One-time B → C execution costs")
    st.table([
        {"Cost per dollar traded": f"{row['basis_points']:.0f} bps",
         "One-way turnover": f"{row['one_way_turnover']:.1%}",
         "Total buys + sells": f"{row['total_traded']:.1%}",
         "One-time cost / portfolio": f"{row['cost']:.3%}"}
        for row in data["cost_scenarios"]
    ])
    st.caption(
        "Costs apply to both buys and sells; they are not subtracted from annual "
        "expected returns. These illustrative amounts exclude taxes and may omit other frictions."
    )
    st.subheader("Return-floor sensitivity")
    st.table(scenario_rows(data["constraint_scenarios"]))
    st.caption("The 16% and 25% floors are hypothetical scenarios, not mandate changes.")

with decision_tab:
    st.header("Committee Decision")
    full_solution = data["optimized_full"]
    if full_solution["feasible"]:
        result = full_solution["result"]
        st.write(
            f"The full-window grid found a mandate-feasible minimum-volatility mix with "
            f"estimated annual return **{result['return']:.2%}** and annualized "
            f"volatility **{result['volatility']:.2%}**."
        )
    else:
        st.error("No full-window grid allocation meets the provisional return objective.")
    process = data["process"]
    st.subheader(f"Implementation process status: {process['status']}")
    for reason in process["reasons"]:
        st.write(f"- {reason}")
    if process["status"] == "REVIEW HOLD":
        st.error(WARNING)
        st.write("Implementation requires further independent review and committee authorization.")
    elif process["status"] == "HARD FAILURE":
        st.error("Implementation must pause until data integrity and feasibility are restored.")
    st.write(
        "These are historical estimates. Hard-rule compliance is separate from "
        "investment suitability, and the window change requires independent review."
    )
    st.info("Final recommendation, allocation range, monitoring plan, and committee ask: pending student review.")
