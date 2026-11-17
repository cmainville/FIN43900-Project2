# Portfolio D — Student-Proposed Diversified Portfolio

**Decision status:** The student selected VTI **40%**, VXUS **25%**, XLE **15%**, IWM **5%**, and IAU **15%** as a preliminary **conditional-pilot candidate**. This fixed allocation is the student's investment judgment, not an optimizer output or an approved mandate amendment. Financial validation and committee authorization remain pending. The original optimizer's **REVIEW HOLD** remains active.

## Inputs and calculation basis

The approved Lab 15 mandate remains a flexible 15-year wealth-accumulation horizon, long-only fully invested positions in the five approved ETFs, and minimum estimated annualized volatility subject to a provisional **6% nominal annual arithmetic-return floor**. No approved concentration cap, reserve, or volatility ceiling exists. VTI is the external benchmark. Portfolio D totals 100% and lies on the existing five-percentage-point grid, though its weights are **never reoptimized** between windows.

The original Yahoo adjusted-close snapshot was retrieved **2026-10-22** (60 monthly prices, October 2021–September 2026; 59 returns). The separate extended Yahoo adjusted-close snapshot was retrieved **2026-11-16** (120 monthly prices, October 2016–September 2026; 119 returns). Both end at the **September 2026 observation cutoff**. The recent 36 returns come from the original snapshot. Source conventions and hashes appear in [the methodology](mandate-and-methodology.md) and [extended provenance](../data/extended-provenance.md). All results below were computed from those frozen files with `portfolio_engine.assess`, `rebalance_costs`, and `dashboard_analytics.monthly_wealth` / `maximum_drawdown` on **2026-11-17**.

Annual arithmetic return is mean monthly simple return ×12. Annual covariance is sample monthly covariance ×12; volatility is the square root of `wᵀΣw`. These are historical estimates, not compound annual growth forecasts. Comparisons within a row use the **same** window's estimates; estimated volatility levels across different rows use different inputs and should not be interpreted as a controlled performance comparison.

## Estimated return, risk, and mandate verdict

| Window | D return | D volatility | D mandate | C return / volatility | Illustrative policy return / volatility | VTI return / volatility |
| --- | ---: | ---: | --- | --- | --- | --- |
| Extended 119 returns | 13.43% | 14.26% | PASS: hard rules and 6% floor | 14.12% / 11.69% | 12.81% / 12.92% | 15.38% / 15.80% |
| Original 59 returns | 13.74% | 13.27% | PASS: hard rules and 6% floor | 15.66% / 12.27% | 14.30% / 12.85% | 12.00% / 15.87% |
| Recent 36 returns | 20.80% | 10.08% | PASS: hard rules and 6% floor | 20.76% / 9.79% | 20.76% / 9.79% | 21.11% / 12.86% |

C is the original approved minimum-volatility result on each window: **50/0/0/0/50**, **50/0/10/0/40**, and **45/20/20/0/15** in VTI/VXUS/XLE/IWM/IAU order. The illustrative, **NOT APPROVED** policy results are **40/40/0/0/20**, **40/25/15/0/20**, and **45/20/20/0/15**. D remains **40/25/15/5/15** in every window by construction. Fixed D weights across windows are not evidence of optimized allocation stability.

D's additional estimated volatility versus C is **2.57**, **1.00**, and **0.29 percentage points** on the extended, original, and recent windows. Versus the illustrative policy it is **1.34**, **0.43**, and **0.29 points**. D's estimated return differs from C by **−0.70**, **−1.92**, and **+0.03 points**, respectively. D has lower estimated volatility than VTI in all three windows, but lower estimated return in the extended and recent windows. These are sample estimates, not evidence that D is superior or suitable.

## Historical risk and growth

For each window, a hypothetical **$100** start is compounded using that window's monthly simple ETF returns with portfolio weights reset **monthly** to the fixed target. Drawdown is the largest peak-to-trough decline observed at **monthly** valuation points. No taxes or implementation costs are included. The optimized C and policy weights are applied to their own estimation histories with hindsight, so these comparisons are **in sample**, not independent out-of-sample backtests.

| Window | D ending hypothetical value | D max drawdown | C ending value / drawdown | Policy ending value / drawdown | VTI ending value / drawdown |
| --- | ---: | ---: | --- | --- | --- |
| Extended 119 | $340.17 | −23.86% | $376.66 / −17.21% | $326.19 / −22.48% | $402.98 / −24.82% |
| Original 59 | $187.70 | −17.21% | $207.28 / −16.06% | $193.35 / −16.95% | $169.33 / −24.82% |
| Recent 36 | $182.98 | −4.34% | $182.94 / −4.08% | $182.94 / −4.08% | $183.06 / −8.40% |

D has **85% equity ETF exposure** and **15% gold exposure**; its largest single ETF weight is **40% VTI**. U.S. equity ETF allocations total **60%** (VTI, XLE, IWM) and VXUS is **25%**. XLE adds a concentrated U.S. energy-sector tilt and overlaps economically with energy companies inside the broad U.S. market fund VTI; exact underlying issuer overlap is not quantified here. The 15% IAU position reduces reliance on gold relative to original C's 40–50% estimates, but it does not eliminate gold-price risk. No approved concentration rule is breached simply because an exposure is large. Whether this equity-heavy mix and its observed drawdowns suit the investor requires independent judgment.

## Hypothetical one-time rebalance costs

One-way turnover is `0.5 × sum(abs(new weight − old weight))`; total buy-plus-sell trading is the full absolute-weight sum. The basis-point rate applies to **both purchases and sales**. Costs are one-time fractions of portfolio value and are **not** deductions from annual expected return. Taxes and some market frictions are excluded.

| Rebalance | One-way turnover | Total traded | Cost at 0 bp | Cost at 10 bp | Cost at 25 bp |
| --- | ---: | ---: | ---: | ---: | ---: |
| B → D | 10% | 20% | 0.000% | 0.020% | 0.050% |
| Original 59-return C → D | 35% | 70% | 0.000% | 0.070% | 0.175% |

The current official **REVIEW HOLD** arises from a **25-percentage-point IAU change** between the original 59-return and recent 36-return **optimized** allocations. D's fixed weights do not remove that finding or authorize implementation. The student must validate the calculations and suitability trade-off, then seek committee authorization for any pilot. A final allocation range, reversal triggers, and committee ask are still open.
