# Project 2 Mandate and Portfolio Methodology

**Status:** Milestone 2 implemented and tested, 2026-11-15. Calculated results appear in [visible-executed-output.md](visible-executed-output.md). They are historical estimates, not an investment recommendation.

## Mandate transition and approved mandate

[Lab 13 §13](https://github.com/cmainville/FIN43900/blob/main/lab13-defense.md) described a five-year home-purchase client, a provisional 4% nominal expected-return floor, and a 30% cash/short-term Treasury reserve. [Lab 15 §3](https://github.com/cmainville/FIN43900/blob/main/lab15/lab15-notes.md) explicitly amended that personal mandate to a 15-year growth investor with a provisional 6% floor and **no** reserve. For Project 2, the student has now intentionally chosen the **Lab 15 amendment** as the governing mandate. The old 4% and 30% terms, and the separate Meridian Foundation training case, are not active Project 2 rules.

| Item | Approved Project 2 policy |
| --- | --- |
| Client | Young investor accumulating wealth over 15 years, with flexibility to remain invested longer |
| Construction objective | Minimize estimated annualized volatility subject to expected annual **nominal arithmetic** return of at least 6%; the floor is provisional, not guaranteed |
| Eligible universe | VTI (U.S. total equity), VXUS (international equity), XLE (U.S. energy), IWM (Russell 2000 small cap), IAU (gold exposure) |
| Hard construction rules | Weights total 100%; nonnegative, long-only ETF positions; no leverage, short sales, or derivatives; only the five listed ETFs |
| Explicitly absent rules | No mandatory cash/Treasury reserve, sector or asset weight cap, or maximum-volatility ceiling |
| Planning context | Fifteen-year horizon is not a numerical optimizer constraint |
| Market benchmark | VTI alone; it is **not** one of the two required baseline portfolios |
| Monitoring trigger | Review if any ETF weight moves **more than** 20 percentage points between full and 36-return optimized allocations; this is not a hard feasibility rule |

The mandate verdict checks construction rules and the provisional return objective separately. A passing verdict does not establish investment suitability. No cost, tax, drawdown, issuer look-through, or future-return guarantee is embedded in that verdict.

## Portfolio methodology and baselines

The [prior Lab 15 engine](https://github.com/cmainville/FIN43900/blob/main/lab15/portfolio.py) established a 5-percentage-point exhaustive grid. [`portfolio_engine.py`](../portfolio_engine.py) enumerates all **10,626** fully invested, long-only five-ETF grid allocations, filters those with estimated return below 6%, and selects the feasible allocation with the smallest estimated variance. Enumeration order determines ties within numerical tolerance. If none are feasible, the engine reports infeasibility instead of relaxing the mandate. The grid is transparent but approximate; a continuous optimum could differ.

- **A — Equal Weight:** 20% in each approved ETF.
- **B — Existing Lab 15 Reference:** VTI 45%, VXUS 25%, XLE 10%, IWM 10%, IAU 10%.
- **C — Constrained Minimum Volatility:** optimized on the approved grid using full-window estimates.

The app shows all three portfolios' weights, estimated annual arithmetic return, estimated annualized volatility, hard-rule status, 6% objective status, and failed-rule reasons. VTI's own full-window return and volatility appear separately as market context. Baselines remain fixed even if an assumption change causes a failed objective.

## Data and calculations

The local [`data/prices_growth.csv`](../data/prices_growth.csv) is byte-for-byte identical to the [Lab 15 snapshot](https://github.com/cmainville/FIN43900/blob/main/lab15/prices_growth.csv) (Git blob SHA `55604a3c2b34cbe041c99fb4ae828495cb0b1f1b`; SHA-256 `9b8d269bddae60e67548ae9f68f71429a4eab001b67cb7efb03e14082cd2609d`). [Lab 15 source notes](https://github.com/cmainville/FIN43900/blob/main/lab15/lab15-notes.md) record retrieval on **2026-10-22** from Yahoo Finance daily **Adj Close**, with `auto_adjust=False`; the final available trading-day adjusted close of each completed month was stored at 12 significant digits under a calendar month-end label. All five series used Yahoo; no fallback was used for this snapshot. Calendar labels are not claims about actual trading dates. Vendor revisions to adjusted histories remain possible.

The fixed dataset contains 60 month-end labels, October 2021 through September 2026; **September 2026 is the as-of boundary**. The full sample has 59 aligned monthly simple returns (November 2021–September 2026). The recent sample has the last 36 returns (October 2023–September 2026). The app does not download live prices. The loader requires exact columns/order, all 60 unique ordered monthly labels, and finite positive prices with no missing values.

For each ETF and month, simple return is `P_t/P_(t-1) - 1`. Annual arithmetic return estimate is sample mean monthly return ×12. Annual covariance is sample monthly covariance (`ddof=1`) ×12. Portfolio expected return is `wᵀμ`; variance is `wᵀΣw`; annualized volatility is `√variance`. Arithmetic return estimates are **not** compound annual growth forecasts. No external prices or unrecorded inputs are needed to reproduce the fixed output.

## Stability and interpretation

The engine independently re-estimates return and covariance on the 59-return and last-36-return windows, then resolves the constrained grid on each. It reports each allocation and estimated metrics, plus the largest individual absolute weight change. The actual 25-point IAU change breaches the approved strict **>20-point** trigger, so the app displays the required **REVIEW REQUIRED** warning. This is a reason for further evaluation, not an automatic adopt/reject verdict. Historical minimum volatility cannot establish future stability.

The 6% floor is slack for every grid allocation in this historical sample. Thus the selected portfolios largely reflect estimated covariance rather than a binding return threshold. This is a sample result, not a basis for assuming future returns will clear 6%.

## Validation and remaining scope

[`test_portfolio_engine.py`](../test_portfolio_engine.py) uses independently specified monthly-return and covariance fixtures; tests weight rules, the 6% floor, complete grid enumeration, deterministic ties, infeasibility, malformed data, largest-weight movement, and strict 20-point threshold behavior. It also checks displayed results against [Lab 15's documented known answers](https://github.com/cmainville/FIN43900/blob/main/lab15/lab15-notes.md). Results and Streamlit checks are recorded in [validation-and-ai-use.md](validation-and-ai-use.md).

Milestone 3 remains responsible for one point-in-time signal with a data card, stress scenarios for estimates, costs, and constraints, a finance-grounded process stop condition, and student-led suitability review. The committee recommendation and allocation range remain pending. The Locked Changed-Input Record remains empty until the student personally authors and commits the AI-off prediction before its separate designated run.
