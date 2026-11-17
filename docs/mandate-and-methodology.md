# Project 2 Mandate and Portfolio Methodology

**Status:** Milestone 4A supplementary historical analysis implemented and tested, 2026-11-16. Calculated results appear in [visible-executed-output.md](visible-executed-output.md). They are historical estimates, not an investment recommendation.

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

The fixed dataset contains 60 month-end labels, October 2021 through September 2026; **September 2026 is the observation cutoff**, while **October 22, 2026 is the documented snapshot retrieval/availability date**. The full sample has 59 aligned monthly simple returns (November 2021–September 2026). The recent sample has the last 36 returns (October 2023–September 2026). The app does not download live prices. The loader requires exact columns/order, all 60 unique ordered monthly labels, and finite positive prices with no missing values.

For each ETF and month, simple return is `P_t/P_(t-1) - 1`. Annual arithmetic return estimate is sample mean monthly return ×12. Annual covariance is sample monthly covariance (`ddof=1`) ×12. Portfolio expected return is `wᵀμ`; variance is `wᵀΣw`; annualized volatility is `√variance`. Arithmetic return estimates are **not** compound annual growth forecasts. No external prices or unrecorded inputs are needed to reproduce the fixed output.

## Stability and interpretation

The engine independently re-estimates return and covariance on the 59-return and last-36-return windows, then resolves the constrained grid on each. It reports each allocation and estimated metrics, plus the largest individual absolute weight change. The actual 25-point IAU change breaches the approved strict **>20-point** trigger, so the app displays the required **REVIEW REQUIRED** warning. This is a reason for further evaluation, not an automatic adopt/reject verdict. Historical minimum volatility cannot establish future stability.

The 6% floor is slack for every grid allocation in this historical sample. Thus the selected portfolios largely reflect estimated covariance rather than a binding return threshold. This is a sample result, not a basis for assuming future returns will clear 6%.

## Supplementary ten-year robustness and IAU concentration

A separate [Yahoo adjusted-close snapshot](../data/extended-provenance.md), retrieved **2026-11-16**, supplies 120 aligned monthly prices from October 2016 through September 2026 and **119 monthly simple returns**. Its raw responses and CSV are frozen with SHA-256 hashes and an offline replay script. The older Lab 15 CSV remains unchanged for the original **59** and recent **36** returns; the two downloads are not spliced. Their overlapping rows differ slightly, with the cause not independently established. Calendar month-end is the observation label, not the retrieval date or a claim of historical point-in-time archiving.

The same arithmetic-return, sample-covariance, and 5-point grid methodology selects **50% VTI / 50% IAU** on 119 returns, versus **50% VTI / 10% XLE / 40% IAU** on 59 returns and **45% VTI / 20% VXUS / 20% XLE / 15% IAU** on 36 returns. All **10,626** grid allocations clear the provisional 6% floor in each sample, so the floor does not drive these choices. The new window increases IAU concentration and leaves VXUS at zero. It therefore challenges the idea that a longer history alone will produce a larger international-equity core.

On the extended sample, IAU's standalone annualized volatility is **15.47%**. Its sample correlations with VTI, VXUS, XLE, and IWM are **0.118, 0.347, −0.013, and 0.010**. Low covariance with VTI lets a 50/50 mix have estimated volatility **11.69%**, below either standalone ETF. This explains the grid optimizer's choice under the approved objective; it does not establish that 50% gold is suitable for a 15-year wealth-accumulation client. A gold cap or equity minimum would be a new policy choice for the student and committee, not an error correction or a rule implemented here.

The extended-vs-original largest change is **10 points in XLE**; extended-vs-recent is **35 points in IAU**. These are supplementary comparisons. The approved implementation monitoring rule still uses only the original **59-vs-36** comparison, which breaches at **25 IAU points** and remains a **REVIEW HOLD**. Each window's reported volatility uses different estimates. For an additional like-for-like risk comparison, the three selected portfolios are evaluated on the common extended covariance matrix in the visible output. These overlapping windows are **not** an independent out-of-sample backtest, and ten years still falls short of the 15-year planning horizon.

The existing 12-month momentum ranking puts XLE first and IAU last, while the extended minimum-variance solution holds zero XLE and 50% IAU. The difference is not a calculation error: momentum ranks backward-looking adjusted-price change, whereas the optimizer minimizes estimated covariance risk. This single signal has not demonstrated predictive accuracy and does not alter the optimizer.

## Point-in-time signal data card

| Field | Definition |
| --- | --- |
| Name and meaning | **Cross-sectional 12-month adjusted-price momentum:** ranks recent adjusted-price performance across the five approved ETFs; it is one signal with five ETF observations |
| Exact inputs/source | September 2025 and September 2026 rows of the frozen Yahoo Finance daily `Adj Close` snapshot, for VTI, VXUS, XLE, IWM, and IAU |
| Observation cutoff | **2026-09-30** calendar month-end label; no October or later prices or forward returns |
| Documented retrieval/availability | **2026-10-22**; do not claim the October snapshot was available on September 30 |
| Lookback and formula | Twelve completed months, from **2025-09-30** to **2026-09-30**; `P_end / P_start − 1` per ETF, ranked high to low with ticker order resolving a tie |
| Transformations | Use the already adjusted prices as stored; no second adjustment, winsorization, annualization, or optimizer input |
| Missing-data rule | Missing, nonfinite, or nonpositive endpoint makes the signal unavailable; do not substitute a different month or fabricate a value |
| Decision role | Supporting evidence for independent review only; it does not change minimum-variance weights or automatically trigger an allocation |
| Limitations | Adjusted histories can be revised after an observation date. This single snapshot is reproducible as retrieved but is **not** a separately archived historical point-in-time series. Momentum is backward-looking and is no forecast of future return. |

## Stress tests and process rule

All scenarios rerun the same 5-point optimizer and keep the approved mandate unchanged. The estimation tests are hypothetical: cut IAU's annual return estimate by **5 percentage points** with other inputs fixed; then, separately, multiply IAU's annualized volatility by **1.25**, hold correlations fixed, and rebuild its covariance row and column. The first scenario leaves weights unchanged because the 6% floor remains slack, which is not evidence of robust expected returns. The second changes the allocation. Exact results are in [visible executed output](visible-executed-output.md).

The historical-window comparison remains the full **59** returns versus the last **36** returns. The one-time B → C cost exercise uses **0, 10, and 25 basis points per dollar traded** on buys and sells. One-way turnover is half the sum of absolute weight changes; total traded volume is the full sum; cost is total volume times the basis-point rate. Costs are shown as a one-time fraction of portfolio value and are not subtracted from annual expected returns. Taxes and other frictions are omitted.

The return-floor sensitivity reruns the original full-window estimates at **6%**, illustrative **16%**, and illustrative **25%**. An infeasible scenario is labeled and never silently relaxed. These floors are scenarios, not client-policy changes.

**Process stop rule:** invalid required input data or no mandate-feasible allocation is a **HARD FAILURE**; implementation pauses. A feasible process with an individual ETF weight move **greater than 20 percentage points** between full and recent optimized windows is a **REVIEW HOLD**; implementation requires further independent review and committee authorization. A hold is not a permanent suitability judgment. Current data and optimizations pass, but IAU moves **25 points**, so the current status is **REVIEW HOLD**.

## Validation and remaining scope

[`test_portfolio_engine.py`](../test_portfolio_engine.py) uses independent monthly-return and covariance fixtures and checks the prior portfolio results against [Lab 15's known answers](https://github.com/cmainville/FIN43900/blob/main/lab15/lab15-notes.md). [`test_milestone3.py`](../test_milestone3.py) covers the signal's boundaries and ranking, isolated estimate changes, correlation-preserving volatility stress, buy-plus-sell costs, feasible/infeasible floors, and process-status precedence. [`test_extended.py`](../test_extended.py) checks the 120-price source, offline raw-response replay, independently calculated return/covariance/risk quantities, and preservation of original allocations and monitoring. Results and Streamlit checks are recorded in [validation-and-ai-use.md](validation-and-ai-use.md). Student review of data provenance, calculations, and investment suitability remains pending.

Independent investment suitability review, the committee recommendation, allocation range, and committee ask remain pending. The Locked Changed-Input Record remains empty until the student personally authors and commits the AI-off prediction before its separate designated run.
