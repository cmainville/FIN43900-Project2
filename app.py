"""FIN 43900 Project 2: committee-facing Streamlit portfolio dashboard."""

import math

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from dashboard_analytics import (
    candidate_cloud, concentration, maximum_drawdown,
    monthly_wealth, nondominated_frontier, override_estimates, validate_custom_weights,
)
from portfolio_engine import (
    EQUAL_WEIGHT, LAB15_REFERENCE, RETURN_FLOOR, SIGNAL_END, SNAPSHOT_RETRIEVED,
    STUDENT_PROPOSED,
    TICKERS, WARNING, analyze, analyze_extended, analyze_policy, assess,
    largest_weight_change, load_extended_prices, load_prices, optimize,
    portfolio_metrics, rebalance_costs, stability_trigger,
)


st.set_page_config(
    page_title="FIN 43900 | Portfolio Decision System", layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = {"VTI": "#3B82F6", "VXUS": "#35C3C1", "XLE": "#F08A5D",
          "IWM": "#A78BFA", "IAU": "#F2C94C"}
EXPOSURES = {"VTI": "U.S. total equity", "VXUS": "International equity",
             "XLE": "U.S. energy", "IWM": "U.S. small cap", "IAU": "Gold"}
OPTIONS = (
    "A — Equal Weight", "B — Lab 15 Reference",
    "C — Original Minimum-Volatility Portfolio",
    "D — Student-Proposed Diversified Portfolio",
    "Illustrative Diversification Policy — NOT APPROVED", "Custom Portfolio",
)
WINDOWS = ("Extended 119 returns", "Original 59 returns", "Recent 36 returns")


@st.cache_data(show_spinner=False)
def frozen_results():
    base = analyze()
    extended = analyze_extended(base)
    return base, extended, analyze_policy(extended), load_prices(), load_extended_prices()


def pct(value):
    return f"{value:.2%}"


def weight_text(weights):
    return " / ".join(f"{weights[ticker]:.0%}" for ticker in TICKERS)


def reset_explorer():
    for key in ("portfolio_choice", "compare_choice", *(f"custom_{ticker}" for ticker in TICKERS)):
        st.session_state.pop(key, None)


def reset_optimization():
    for key in list(st.session_state):
        if key in ("opt_window", "opt_floor", "opt_bounds", "opt_gold", "opt_vxus") or key.startswith(("opt_return_", "opt_vol_")):
            del st.session_state[key]


def reset_stress():
    for key in list(st.session_state):
        if key.startswith("stress_"):
            del st.session_state[key]


def window_details(extended, original_prices, extended_prices, name):
    index = WINDOWS.index(name)
    _, estimates, solution = extended["windows"][index]
    prices = extended_prices if index == 0 else original_prices
    if index == 2:
        prices = prices.tail(37)
    return estimates, solution, prices


def portfolio_for_option(option, base, policy):
    if option == OPTIONS[0]:
        return base["portfolios"]["A — Equal Weight"]
    if option == OPTIONS[1]:
        return base["portfolios"]["B — Lab 15 Reference"]
    if option == OPTIONS[2]:
        return base["portfolios"]["C — Constrained Minimum Volatility"]
    if option == OPTIONS[3]:
        return assess(STUDENT_PROPOSED, base["full"])
    if option == OPTIONS[4]:
        return policy["rows"][1]["alternative"]["result"]
    weights = {ticker: st.session_state.get(f"custom_{ticker}", 20.0) / 100 for ticker in TICKERS}
    valid, _ = validate_custom_weights(weights)
    if not valid:
        return None
    return assess(weights, base["full"])


def allocation_chart(weights, height=260):
    frame = pd.DataFrame([
        {"ETF": ticker, "Weight": weights[ticker], "Exposure": EXPOSURES[ticker],
         "Label": f"{ticker} {weights[ticker]:.0%}"}
        for ticker in TICKERS if weights[ticker] > 0
    ])
    chart = (alt.Chart(frame).mark_arc(innerRadius=68, outerRadius=105)
            .encode(theta=alt.Theta("Weight:Q", stack=True),
                    color=alt.Color("ETF:N", scale=alt.Scale(
                        domain=list(TICKERS), range=list(COLORS.values())),
                        legend=alt.Legend(orient="bottom")),
                    tooltip=["ETF:N", "Exposure:N", alt.Tooltip("Weight:Q", format=".1%")])
            .properties(height=height))
    labels = (alt.Chart(frame).mark_text(radius=125, fontSize=11, color="#E7ECF5")
              .encode(theta=alt.Theta("Weight:Q", stack=True), text="Label:N"))
    return chart + labels


def allocation_bars(named_weights, height=200):
    frame = pd.DataFrame([
        {"Portfolio": name, "ETF": ticker, "Weight": weights[ticker] * 100}
        for name, weights in named_weights.items() for ticker in TICKERS
    ])
    return (alt.Chart(frame).mark_bar().encode(
        x=alt.X("Portfolio:N", title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Weight:Q", title="Allocation (%)", stack="zero"),
        color=alt.Color("ETF:N", scale=alt.Scale(domain=list(TICKERS),
                                                 range=list(COLORS.values())),
                        legend=alt.Legend(orient="bottom")),
        tooltip=["Portfolio:N", "ETF:N", alt.Tooltip("Weight:Q", format=".0f")]
    ).properties(height=height))


def growth_chart(prices, named_weights):
    frame = pd.concat([
        monthly_wealth(prices, weights).rename(name)
        for name, weights in named_weights.items()
    ], axis=1).reset_index().rename(columns={"Date": "Date", "index": "Date"})
    long = frame.melt(id_vars="Date", var_name="Portfolio", value_name="Value")
    return (alt.Chart(long).mark_line(strokeWidth=2.5).encode(
        x=alt.X("Date:T", title=None), y=alt.Y("Value:Q", title="Hypothetical value ($)"),
        color=alt.Color("Portfolio:N", legend=alt.Legend(orient="bottom")),
        tooltip=[alt.Tooltip("Date:T", format="%Y-%m"), "Portfolio:N",
                 alt.Tooltip("Value:Q", format=".2f")]
    ).properties(height=240))


def metric_card(label, value, note=None):
    with st.container(border=True):
        st.metric(label, value)
        if note:
            st.caption(note)


def portfolio_kpis(result, benchmark=None):
    ticker, largest = concentration(result["weights"])
    columns = st.columns(3)
    with columns[0]:
        metric_card("Estimated annual arithmetic return", pct(result["return"]))
    with columns[1]:
        metric_card("Estimated annualized volatility", pct(result["volatility"]))
    with columns[2]:
        metric_card("Largest ETF position", f"{ticker} · {largest:.0%}")
    if benchmark is not None:
        st.caption(f"VTI external benchmark on the same estimates: return {pct(benchmark['return'])} · "
                   f"volatility {pct(benchmark['volatility'])}.")


def verdict_line(result, hypothetical=False):
    verdict = result["verdict"]
    label = "Hypothetical allocation · approved mandate checks" if hypothetical else "Modeled mandate"
    st.write(f"**{label}: {'PASS' if verdict['pass'] else 'FAIL'}** · "
             f"Hard construction rules: {'PASS' if verdict['hard_pass'] else 'FAIL'} · "
             f"Provisional 6% return objective: {'PASS' if verdict['objective_pass'] else 'FAIL'}")
    if verdict["reasons"]:
        st.error("Failed rule(s): " + "; ".join(verdict["reasons"]))
    else:
        st.caption("A modeled pass is not an investment suitability determination.")


def show_before_after(before, after, before_label="Approved original", after_label="Hypothetical scenario"):
    columns = st.columns(2)
    for column, label, result in ((columns[0], before_label, before),
                                  (columns[1], after_label, after)):
        with column:
            with st.container(border=True):
                st.markdown(f"**{label}**")
                if result is None:
                    st.error("INFEASIBLE — no allocation meets all stated rules.")
                else:
                    st.write(weight_text(result["weights"]))
                    st.write(f"Return **{pct(result['return'])}** · Volatility **{pct(result['volatility'])}**")
    if before is not None and after is not None:
        ticker, points = largest_weight_change(before["weights"], after["weights"])
        st.caption(f"Largest allocation change: {ticker} {points:.0f} percentage points. "
                   "Both metrics use the displayed scenario assumptions unless noted.")


def scenario_inputs(estimates, scenario, prefix="stress"):
    """One modified input family per workbench run."""
    means = tuple(float(value) for value in estimates["returns"])
    vols = tuple(float(value) for value in np.sqrt(np.diag(estimates["covariance"])))
    bounds_min, bounds_max = {}, {}
    floor = RETURN_FLOOR
    cost_bps = None
    changed_window = None
    if scenario in ("Expected-return shock", "Volatility shock"):
        ticker = st.selectbox("ETF", TICKERS, index=4, key=f"{prefix}_ticker_{scenario}")
        index = TICKERS.index(ticker)
        if scenario == "Expected-return shock":
            delta = st.number_input("Change in annual return estimate (percentage points)",
                                    min_value=-50.0, max_value=50.0, value=-5.0,
                                    step=0.5, key=f"{prefix}_return_delta")
            means = tuple(value + (delta / 100 if i == index else 0) for i, value in enumerate(means))
            description = f"{ticker} annual arithmetic estimate {estimates['returns'][index]:.2%} → {means[index]:.2%}; covariance fixed."
        else:
            change = st.number_input("Change in annualized volatility (%)", min_value=-90.0,
                                     max_value=300.0, value=25.0, step=5.0,
                                     key=f"{prefix}_vol_delta")
            vols = tuple(value * (1 + change / 100) if i == index else value
                         for i, value in enumerate(vols))
            description = f"{ticker} annualized volatility multiplied by {1 + change / 100:.2f}; historical correlations retained."
    elif scenario == "Historical-window sensitivity":
        changed_window = st.selectbox("Comparison window", (WINDOWS[0], WINDOWS[2]),
                                      index=1, key=f"{prefix}_window")
        description = f"Original 59-return window → {changed_window}; each has its own estimates."
    elif scenario == "Return-floor sensitivity":
        floor = st.number_input("Hypothetical minimum annual return (%)", min_value=0.0,
                                max_value=40.0, value=16.0, step=1.0, key=f"{prefix}_floor") / 100
        description = f"Minimum return 6% → {floor:.0%}; original 59-return estimates fixed."
    elif scenario == "Trading-cost sensitivity":
        cost_bps = st.number_input("One-time cost per dollar traded (basis points)",
                                   min_value=0.0, max_value=100.0, value=10.0,
                                   step=5.0, key=f"{prefix}_cost")
        description = f"One-time B → C rebalance at {cost_bps:.0f} bps on both purchases and sales."
    elif scenario == "Illustrative diversification policy":
        cap = st.slider("Hypothetical maximum IAU (%)", 0, 100, 20, 5,
                        key=f"{prefix}_gold")
        minimum = st.slider("Hypothetical minimum VXUS (%)", 0, 100, 15, 5,
                            key=f"{prefix}_vxus")
        bounds_max, bounds_min = {"IAU": cap / 100}, {"VXUS": minimum / 100}
        description = f"No approved concentration limits → IAU ≤{cap}%, VXUS ≥{minimum}%. NOT APPROVED."
    return means, vols, floor, bounds_min, bounds_max, cost_bps, changed_window, description


def main():
    st.sidebar.markdown("### FIN 43900")
    st.sidebar.caption("Portfolio Decision System · educational analysis")
    navigation = st.sidebar.radio("Navigation", ("Overview", "Analytics", "Decision"),
                                  key="navigation")
    st.sidebar.divider()
    st.sidebar.caption("Approved process · frozen sources · no live prices")
    try:
        base, extended, policy, original_prices, extended_prices = frozen_results()
    except (OSError, ValueError) as exc:
        st.error(f"HARD FAILURE — Required data or optimization failed: {exc}")
        return
    st.session_state.setdefault("portfolio_choice", OPTIONS[2])
    st.session_state.setdefault("compare_choice", OPTIONS[1])
    st.title("FIN 43900 | Portfolio Decision System")
    st.caption("Educational use · Historical estimates, not investment advice · "
               "Original snapshot retrieved 2026-10-22; supplementary snapshot retrieved 2026-11-16")
    if navigation == "Overview":
        overview(base, extended, policy, original_prices)
    elif navigation == "Analytics":
        analytics(base, extended, policy, original_prices, extended_prices)
    else:
        decision(base, extended, policy)


def overview(base, extended, policy, original_prices):
    choice = st.session_state.portfolio_choice
    result = portfolio_for_option(choice, base, policy)
    st.subheader("Executive overview")
    st.caption(f"Portfolio in focus: {choice} · Analysis basis: original 59 monthly returns")
    if result is None:
        st.error("Custom weights are invalid. Open Analytics → Portfolio Explorer to correct them.")
        return
    if choice == OPTIONS[3]:
        st.info("Student-approved conditional-pilot proposal; REVIEW HOLD resolution and committee authorization remain pending.")
    elif choice in OPTIONS[4:]:
        st.warning("HYPOTHETICAL — This selected allocation is not an approved mandate amendment or committee decision.")
    portfolio_kpis(result, base["vti_benchmark"])
    columns = st.columns([1.05, 1.5])
    with columns[0]:
        with st.container(border=True):
            st.markdown("**Allocation**")
            st.altair_chart(allocation_chart(result["weights"]), width="stretch")
            st.caption(" · ".join(f"{ticker}: {EXPOSURES[ticker]}" for ticker in TICKERS))
    with columns[1]:
        with st.container(border=True):
            st.markdown("**Hypothetical historical growth · $100 start**")
            st.altair_chart(growth_chart(original_prices, {
                "Selected": result["weights"], "VTI benchmark": base["vti_benchmark"]["weights"]
            }), width="stretch")
            st.caption("Original 2021–2026 snapshot; fixed weights reset monthly. "
                       "Optimized weights are applied to their own estimation period in hindsight. "
                       "This is neither an out-of-sample test nor a forward projection.")
    columns = st.columns(3)
    with columns[0]:
        with st.container(border=True):
            st.markdown("**Mandate compliance**")
            verdict_line(result, choice in OPTIONS[3:])
    with columns[1]:
        with st.container(border=True):
            st.markdown("**Implementation status**")
            st.error(base["process"]["status"])
            st.caption("Official 59-versus-36 allocation change: IAU 25 percentage points; "
                       "strict review trigger is more than 20.")
    with columns[2]:
        with st.container(border=True):
            st.markdown("**Signal snapshot**")
            st.write(" · ".join(f"{row['ticker']} {row['momentum']:.1%}"
                               for row in base["momentum"]))
            st.caption(f"12-month ranking through {SIGNAL_END}; retrieved {SNAPSHOT_RETRIEVED}. "
                       "Descriptive only; predictive accuracy unproven.")
    with st.container(border=True):
        st.markdown("**Committee summary**")
        st.write("The approved minimum-volatility result concentrates 40% in IAU on the original "
                 "window; the supplementary ten-year result holds 50% IAU. The 59-versus-36 "
                 "monitoring breach places implementation on REVIEW HOLD.")
        st.info("Student-approved proposal: conditional pilot of D within proposed ranges; committee authorization and REVIEW HOLD resolution remain pending.")
    with st.expander("Mandate, data, and calculation conventions"):
        st.write("Young wealth-accumulation investor; flexible 15-year horizon. Approved Lab 15 "
                 "objective: minimum estimated annualized volatility with a provisional 6% "
                 "annual nominal arithmetic-return floor, long-only fully invested five-ETF grid "
                 "in five-point steps. No approved gold cap, VXUS minimum, or reserve. VTI is the "
                 "external benchmark. Monthly adjusted prices are frozen; annual estimates use "
                 "mean monthly simple return ×12 and sample monthly covariance ×12.")


def analytics(base, extended, policy, original_prices, extended_prices):
    explorer_tab, optimizer_tab, risk_tab, historical_tab = st.tabs(
        ("Portfolio Explorer", "Optimization", "Risk & Stress Tests", "Historical Analysis")
    )
    with explorer_tab:
        explorer(base, policy, original_prices)
    with optimizer_tab:
        optimization(base, extended)
    with risk_tab:
        risk_and_stress(base, extended, policy, original_prices, extended_prices)
    with historical_tab:
        historical_analysis(base, extended, policy)


def explorer(base, policy, original_prices):
    st.subheader("Portfolio Explorer")
    st.button("Reset to Defaults", on_click=reset_explorer, key="reset_explorer")
    left, right = st.columns(2)
    with left:
        choice = st.selectbox("Portfolio", OPTIONS, key="portfolio_choice")
    with right:
        st.selectbox("Compare with", OPTIONS, key="compare_choice")
    if choice == OPTIONS[5]:
        st.caption("Custom/hypothetical portfolio · enter five weights; no automatic normalization.")
        columns = st.columns(5)
        for column, ticker in zip(columns, TICKERS):
            with column:
                st.number_input(f"{ticker} weight (%)", min_value=0.0, max_value=100.0,
                                value=20.0, step=1.0, key=f"custom_{ticker}")
        weights = {ticker: st.session_state[f"custom_{ticker}"] / 100 for ticker in TICKERS}
        valid, message = validate_custom_weights(weights)
        if not valid:
            st.error(message)
        else:
            st.success(message)
    selected = portfolio_for_option(choice, base, policy)
    comparison = portfolio_for_option(st.session_state.compare_choice, base, policy)
    if selected is None:
        return
    if choice == OPTIONS[3]:
        st.info("Student-proposed fixed allocation · conditional-pilot proposal approved by the student, pending REVIEW HOLD resolution and committee authorization.")
    if choice == OPTIONS[4]:
        st.warning("NOT APPROVED — IAU ≤20%, VXUS ≥15% are illustrative policy bounds.")
    portfolio_kpis(selected, base["vti_benchmark"])
    verdict_line(selected, choice in OPTIONS[3:])
    columns = st.columns(2)
    with columns[0]:
        st.altair_chart(allocation_chart(selected["weights"]), width="stretch")
    with columns[1]:
        st.markdown("**Holdings**")
        st.table([{"ETF": ticker, "Exposure": EXPOSURES[ticker],
                   "Weight": f"{selected['weights'][ticker]:.1%}"} for ticker in TICKERS])
    if comparison is not None:
        st.markdown("**Comparison on the original 59-return estimates**")
        st.altair_chart(allocation_bars({"Selected": selected["weights"],
                                        "Comparison": comparison["weights"]}),
                        width="stretch")
        columns = st.columns(2)
        columns[0].metric("Return difference", f"{(selected['return'] - comparison['return']) * 100:+.2f} pp")
        columns[1].metric("Volatility difference", f"{(selected['volatility'] - comparison['volatility']) * 100:+.2f} pp")
    st.caption("All displayed estimates use the original 59-return frozen snapshot. "
               "Custom allocations do not change the approved A, B, or C portfolios.")


def optimization(base, extended):
    st.subheader("Interactive Optimization")
    st.caption("The approved baseline has a 6% floor, no concentration bounds, and original "
               "59-return estimates. All changes here are hypothetical and do not change Portfolio C.")
    st.button("Reset to Approved Defaults", on_click=reset_optimization, key="reset_optimization")
    first, second = st.columns(2)
    with first:
        window = st.selectbox("Estimation window", WINDOWS, index=1, key="opt_window")
        floor_pct = st.number_input("Minimum expected annual return (%)", min_value=0.0,
                                    max_value=40.0, value=6.0, step=0.5, key="opt_floor")
    with second:
        enabled = st.checkbox("Enable hypothetical concentration bounds · NOT APPROVED",
                              value=False, key="opt_bounds")
        cap = st.slider("Maximum IAU (%)", 0, 100, 20, 5, key="opt_gold", disabled=not enabled)
        minimum = st.slider("Minimum VXUS (%)", 0, 100, 15, 5,
                            key="opt_vxus", disabled=not enabled)
    _, historical, approved = extended["windows"][WINDOWS.index(window)]
    original_means = tuple(float(value) for value in historical["returns"])
    original_vols = tuple(float(value) for value in np.sqrt(np.diag(historical["covariance"])))
    with st.expander("Individual ETF estimates · hypothetical overrides"):
        st.caption("Inputs are annual percentages. Editing volatility scales covariance while "
                   "holding the selected window's historical correlations fixed.")
        mean_inputs, vol_inputs = [], []
        for ticker, mean, vol in zip(TICKERS, original_means, original_vols):
            left, right = st.columns(2)
            mean_inputs.append(left.number_input(
                f"{ticker} arithmetic return (%)", min_value=-100.0, max_value=300.0,
                value=mean * 100, step=0.5, format="%.4f", key=f"opt_return_{window}_{ticker}"))
            vol_inputs.append(right.number_input(
                f"{ticker} annualized volatility (%)", min_value=0.01, max_value=300.0,
                value=vol * 100, step=0.5, format="%.4f", key=f"opt_vol_{window}_{ticker}"))
    means = tuple(value / 100 for value in mean_inputs)
    vols = tuple(value / 100 for value in vol_inputs)
    overridden = (not np.allclose(means, original_means, atol=1e-12, rtol=0)
                  or not np.allclose(vols, original_vols, atol=1e-12, rtol=0))
    try:
        estimates = override_estimates(historical, means, vols) if overridden else historical
        lower = {"VXUS": minimum / 100} if enabled else {}
        upper = {"IAU": cap / 100} if enabled else {}
        solution = optimize(estimates, floor=floor_pct / 100,
                            minimum_weights=lower, maximum_weights=upper)
        cloud = candidate_cloud(estimates, floor=floor_pct / 100,
                                minimum_weights=lower, maximum_weights=upper)
    except ValueError as exc:
        st.error(f"Invalid hypothetical inputs: {exc}")
        return
    st.write(f"**Hypothetical scenario** · {window} · {solution['feasible_count']:,} "
             f"feasible of {solution['candidate_count']:,} grid allocations")
    if not solution["feasible"]:
        st.error("INFEASIBLE — No grid allocation meets all displayed assumptions. "
                 "No constraint was relaxed.")
    else:
        result = solution["result"]
        portfolio_kpis(result)
        st.write(f"Optimized scenario weights (VTI / VXUS / XLE / IWM / IAU): "
                 f"**{weight_text(result['weights'])}**")
        st.caption("The frozen unmodified optimum for this window remains "
                   f"{weight_text(approved['result']['weights'])} under frozen inputs.")
    st.markdown("**Finite-grid efficient frontier**")
    frontier = nondominated_frontier(cloud)
    feasible = cloud.loc[cloud["Feasible"]]
    if feasible.empty:
        st.info("No feasible points to plot under these hypothetical assumptions.")
        return
    sample_step = max(1, math.ceil(len(feasible) / 1200))
    sample = feasible.iloc[::sample_step]
    points = (alt.Chart(sample).mark_circle(size=24, opacity=0.22, color="#6B7F9C")
              .encode(x=alt.X("Volatility:Q", title="Estimated annualized volatility (%)",
                                  scale=alt.Scale(zero=False)),
                      y=alt.Y("Return:Q", title="Estimated annual arithmetic return (%)",
                                  scale=alt.Scale(zero=False)),
                      tooltip=[alt.Tooltip("Volatility:Q", format=".2f"),
                               alt.Tooltip("Return:Q", format=".2f"), "Weights:N", "Feasible:N"]))
    line = (alt.Chart(frontier).mark_line(color="#3B82F6", strokeWidth=2.5)
            .encode(x=alt.X("Volatility:Q", scale=alt.Scale(zero=False)),
                    y=alt.Y("Return:Q", scale=alt.Scale(zero=False)),
                    tooltip=["Weights:N", alt.Tooltip("Volatility:Q", format=".2f"),
                             alt.Tooltip("Return:Q", format=".2f")]))
    markers = []
    for label, weights in (("Equal weight", EQUAL_WEIGHT), ("Lab 15 reference", LAB15_REFERENCE),
                           ("VTI benchmark", base["vti_benchmark"]["weights"]),
                           ("Frozen window optimum", approved["result"]["weights"])):
        metrics = portfolio_metrics(weights, estimates)
        markers.append({"Portfolio": label, "Volatility": metrics["volatility"] * 100,
                        "Return": metrics["return"] * 100, "Weights": weight_text(weights),
                        "Feasible": bool(metrics["return"] >= floor_pct / 100 - 1e-12
                                         and all(weights[t] >= v for t, v in lower.items())
                                         and all(weights[t] <= v for t, v in upper.items()))})
    if solution["feasible"]:
        result = solution["result"]
        markers.append({"Portfolio": "Current scenario optimum", "Volatility": result["volatility"] * 100,
                        "Return": result["return"] * 100, "Weights": weight_text(result["weights"]),
                        "Feasible": True})
    marks = (alt.Chart(pd.DataFrame(markers)).mark_point(filled=True, size=100)
             .encode(x=alt.X("Volatility:Q", scale=alt.Scale(zero=False)),
                     y=alt.Y("Return:Q", scale=alt.Scale(zero=False)),
                     color=alt.Color("Portfolio:N"),
                     tooltip=["Portfolio:N", "Weights:N", "Feasible:N",
                              alt.Tooltip("Volatility:Q", format=".2f"),
                              alt.Tooltip("Return:Q", format=".2f")]))
    st.altair_chart((points + line + marks).properties(height=340), width="stretch")
    st.caption(f"Blue line: nondominated boundary of all {len(feasible):,} feasible grid points; "
               f"gray dots: representative sample of {len(sample):,} points. Fixed baseline "
               "and benchmark markers may be infeasible under hypothetical limits. "
               "This estimated frontier is not a forecast or a maximum-Sharpe result.")


def risk_and_stress(base, extended, policy, original_prices, extended_prices):
    st.subheader("Portfolio Risk Analytics")
    window = st.selectbox("Risk estimation window", WINDOWS, index=1, key="risk_window")
    estimates, _, prices = window_details(extended, original_prices, extended_prices, window)
    choice = st.session_state.portfolio_choice
    result = portfolio_for_option(choice, base, policy)
    if result is None:
        st.error("Correct invalid custom weights in Portfolio Explorer to view risk analytics.")
    else:
        wealth = monthly_wealth(prices, result["weights"])
        benchmark_wealth = monthly_wealth(prices, base["vti_benchmark"]["weights"])
        ticker, biggest = concentration(result["weights"])
        cols = st.columns(3)
        cols[0].metric("Maximum monthly-observed drawdown", pct(maximum_drawdown(wealth)))
        cols[1].metric("Largest ETF position", f"{ticker} {biggest:.0%}")
        cols[2].metric("Annualized volatility on selected window",
                       pct(portfolio_metrics(result["weights"], estimates)["volatility"]))
        st.altair_chart(growth_chart(prices, {"Selected": result["weights"],
                                             "VTI benchmark": base["vti_benchmark"]["weights"]}),
                        width="stretch")
        st.caption("$100 hypothetical start; monthly simple returns and monthly reset to fixed "
                   "weights. Drawdown is peak-to-trough on monthly observations. Optimized weights "
                   "are selected with hindsight on overlapping historical data, not out of sample.")
    with st.expander("ETF correlation matrix · selected estimation window"):
        covariance = estimates["covariance"]
        vols = np.sqrt(np.diag(covariance))
        correlation = covariance / np.outer(vols, vols)
        cells = pd.DataFrame([
            {"ETF": left, "Peer": right, "Correlation": float(correlation[i, j]),
             "Label": f"{correlation[i, j]:.2f}"}
            for i, left in enumerate(TICKERS) for j, right in enumerate(TICKERS)
        ])
        heat = (alt.Chart(cells).mark_rect()
                .encode(x=alt.X("ETF:N", sort=list(TICKERS), title=None),
                        y=alt.Y("Peer:N", sort=list(TICKERS), title=None),
                        color=alt.Color("Correlation:Q", scale=alt.Scale(
                            domain=[-1, 1], scheme="redblue")),
                        tooltip=["ETF:N", "Peer:N",
                                 alt.Tooltip("Correlation:Q", format=".2f")]))
        numbers = (alt.Chart(cells).mark_text(color="#E7ECF5", fontSize=11)
                   .encode(x=alt.X("ETF:N", sort=list(TICKERS)),
                           y=alt.Y("Peer:N", sort=list(TICKERS)), text="Label:N"))
        st.altair_chart((heat + numbers).properties(height=250), width="stretch")
    st.divider()
    stress_workbench(base, extended)
    signal_data_card(base)


def stress_workbench(base, extended):
    st.subheader("Interactive Scenario Workbench")
    st.caption("One hypothetical scenario at a time. The approved REVIEW HOLD and frozen "
               "stress evidence remain unchanged by these controls.")
    st.button("Reset scenario", on_click=reset_stress, key="reset_stress")
    options = ("Expected-return shock", "Volatility shock", "Historical-window sensitivity",
               "Return-floor sensitivity", "Trading-cost sensitivity",
               "Illustrative diversification policy", "Custom Scenario")
    mode = st.selectbox("Scenario", options, key="stress_mode")
    scenario = mode
    if mode == "Custom Scenario":
        scenario = st.selectbox("One custom change", options[:-1], key="stress_custom_type")
    estimates = base["full"]
    before = base["optimized_full"]["result"]
    values = scenario_inputs(estimates, scenario)
    means, vols, floor, lower, upper, cost_bps, changed_window, description = values
    st.write(f"**Assumption change:** {description}")
    if changed_window:
        after = extended["windows"][WINDOWS.index(changed_window)][2]["result"]
        show_before_after(before, after)
        st.caption("Before and after metrics use different estimation windows; compare weights, "
                   "not volatility levels as like-for-like estimates.")
        if after is not None:
            ticker, points = largest_weight_change(before["weights"], after["weights"])
            if changed_window == WINDOWS[2] and stability_trigger(points):
                st.warning(f"Approved monitoring comparison: {ticker} moves {points:.0f} pp; REVIEW HOLD.")
            elif changed_window == WINDOWS[0]:
                st.caption(f"Extended-window comparison: {ticker} moves {points:.0f} pp. "
                           "Supplementary evidence only; the approved 59-vs-36 rule is unchanged.")
    elif cost_bps is not None:
        before = base["portfolios"]["B — Lab 15 Reference"]
        after = base["optimized_full"]["result"]
        show_before_after(before, after, "B — Lab 15 reference", "C — Original approved")
        cost = rebalance_costs(before["weights"], after["weights"], cost_bps)
        st.write(f"One-way turnover **{cost['one_way_turnover']:.1%}** · "
                 f"Total buys + sells **{cost['total_traded']:.1%}** · "
                 f"One-time implementation cost **{cost['cost']:.3%}** of portfolio value")
        st.caption("Costs apply to purchases and sales; excluded from annual expected return. "
                   "Taxes and other frictions are omitted.")
    else:
        try:
            modified = override_estimates(estimates, means, vols)
            solution = optimize(modified, floor=floor, minimum_weights=lower,
                                maximum_weights=upper)
        except ValueError as exc:
            st.error(f"Scenario input failure: {exc}")
            return
        after = solution["result"]
        # Display the original weights on the modified inputs for a like-for-like
        # comparison; the approved frozen result remains identified separately.
        before_same_inputs = assess(before["weights"], modified)
        show_before_after(before_same_inputs, after, "Original weights · scenario estimates",
                          "Scenario optimum")
        st.caption(f"Feasible candidates: {solution['feasible_count']:,}/{solution['candidate_count']:,}. "
                   "Original approved C on frozen 59-return estimates remains "
                   f"{weight_text(before['weights'])}, return {pct(before['return'])}, "
                   f"volatility {pct(before['volatility'])}.")
        if after is None:
            st.error("Scenario HARD FAILURE: no feasible allocation under the hypothetical inputs. "
                     "No constraint was silently relaxed.")
        elif after["verdict"]["reasons"]:
            st.warning("Modeled mandate reasons: " + "; ".join(after["verdict"]["reasons"]))
        if scenario == "Illustrative diversification policy":
            st.warning("NOT APPROVED — these limits are suitability assumptions for review.")
    st.info("Official implementation status: REVIEW HOLD from the approved 59-vs-36 rule. "
            "Scenario-specific results do not authorize implementation.")


def signal_data_card(base):
    with st.expander("Momentum ranking and point-in-time data card"):
        st.table([{"Rank": row["rank"], "ETF": row["ticker"],
                   "Trailing 12-month adjusted-price return": pct(row["momentum"])}
                  for row in base["momentum"]])
        st.write("One cross-sectional signal: ending adjusted close ÷ starting adjusted close − 1 "
                 "for each approved ETF. Observation labels are September 2025 and September 2026; "
                 "September 30, 2026 is the cutoff. The Yahoo adjusted-price snapshot was retrieved "
                 "October 22, 2026, so availability at the September cutoff is not claimed. "
                 "Missing or nonpositive endpoints invalidate the signal. Adjusted histories can "
                 "be revised. No forward returns are used, predictive validity is unproven, and "
                 "the signal does not enter optimization.")


def historical_analysis(base, extended, policy):
    st.subheader("Historical Robustness")
    st.caption("Three overlapping estimation windows · extended Yahoo retrieval 2026-11-16; "
               "original Lab 15 retrieval 2026-10-22. No independent out-of-sample backtest.")
    weights = {name: solution["result"]["weights"]
               for name, _, solution in extended["windows"] if solution["feasible"]}
    st.altair_chart(allocation_bars(weights, height=270), width="stretch")
    st.table([
        {"Window": name, "VTI": f"{solution['result']['weights']['VTI']:.0%}",
         "VXUS": f"{solution['result']['weights']['VXUS']:.0%}",
         "IAU": f"{solution['result']['weights']['IAU']:.0%}",
         "Return": pct(solution["result"]["return"]),
         "Volatility": pct(solution["result"]["volatility"])}
        for name, _, solution in extended["windows"]
    ])
    st.error(WARNING)
    st.caption("Approved monitoring: original 59 vs recent 36 returns; largest move IAU 25 pp. "
               "Extended 119 vs recent 36 differs by IAU 35 pp as supplementary evidence. "
               "Own-window volatility estimates use different covariance inputs; historical "
               "arithmetic returns are not 15-year forecasts.")
    with st.expander("Illustrative diversification policy · NOT APPROVED"):
        st.write("Hypothetical IAU maximum 20%, VXUS minimum 15%; suitability sensitivity, "
                 "not an approved mandate change.")
        st.table([
            {"Window": row["name"], "Case": label,
             "Weights (VTI/VXUS/XLE/IWM/IAU)": weight_text(solution["result"]["weights"]),
             "Feasible candidates": f"{solution['feasible_count']:,}/{solution['candidate_count']:,}",
             "Est. return": pct(solution["result"]["return"]),
             "Est. volatility": pct(solution["result"]["volatility"])}
            for row in policy["rows"]
            for label, solution in (("Approved unconstrained", row["original"]),
                                    ("Illustrative policy", row["alternative"]))
        ])
        st.caption("Illustrative 59-vs-36 largest move is XLE 5 pp, but the approved "
                   "original REVIEW HOLD remains. Each within-window policy comparison uses "
                   "the same covariance matrix; any policy adoption needs student approval.")


def decision(base, extended, policy):
    st.subheader("Investment Committee Decision Framework")
    st.error("REVIEW HOLD · Implementation requires independent review and committee authorization")
    columns = st.columns(2)
    with columns[0]:
        with st.container(border=True):
            st.markdown("**Approved Lab 15 mandate**")
            st.write("Flexible 15-year wealth accumulation; five approved ETFs; long-only, "
                     "fully invested; minimize annualized estimated volatility subject to a "
                     "provisional 6% nominal arithmetic-return floor. VTI is the external benchmark. "
                     "No approved concentration cap or reserve.")
        with st.container(border=True):
            st.markdown("**Original approved C**")
            original = base["optimized_full"]["result"]
            st.write(weight_text(original["weights"]))
            st.write(f"Estimated return **{pct(original['return'])}** · "
                     f"volatility **{pct(original['volatility'])}**")
    with columns[1]:
        with st.container(border=True):
            st.markdown("**Illustrative diversified alternative · NOT APPROVED**")
            proposed = policy["rows"][1]["alternative"]["result"]
            st.write(weight_text(proposed["weights"]))
            st.write(f"Estimated return **{pct(proposed['return'])}** · "
                     f"volatility **{pct(proposed['volatility'])}**")
        with st.container(border=True):
            st.markdown("**D · Student-proposed conditional-pilot candidate**")
            student = assess(STUDENT_PROPOSED, base["full"])
            st.write(weight_text(student["weights"]))
            st.write(f"Estimated return **{pct(student['return'])}** · "
                     f"volatility **{pct(student['volatility'])}** · "
                     f"modeled mandate **{'PASS' if student['verdict']['pass'] else 'FAIL'}**")
            st.caption("Student-selected fixed weights; not optimized or committee-approved. "
                       "Conditional pilot remains subject to REVIEW HOLD resolution and authorization.")
        with st.container(border=True):
            st.markdown("**Evidence and principal risks**")
            st.write("Original C has 40% IAU; the extended-window optimum has 50% IAU. "
                     "The original 59-vs-36 change is 25 IAU points. The illustrative bounds "
                     "reduce concentration but add estimated risk on the longer windows. "
                     "Historical windows overlap; momentum is descriptive, not predictive.")
    with st.container(border=True):
        st.markdown("**Implementation constraints and monitoring**")
        st.write("Invalid required data or infeasible optimization is a HARD FAILURE. "
                 "An ETF weight change greater than 20 percentage points between the approved "
                 "59- and 36-return optimizations is a REVIEW HOLD. The current hold remains; "
                 "implementation requires independent review and committee authorization. "
                 "Reassess the return floor, concentration suitability, data revisions, and "
                 "allocation stability before any implementation decision.")
    st.info("Student-approved proposal: conditional pilot of D within the memo's proposed ranges, "
            "with quarterly monitoring and annual rebalancing consideration. The active REVIEW HOLD "
            "requires written resolution and explicit committee authorization before implementation.")


if __name__ == "__main__":
    main()
