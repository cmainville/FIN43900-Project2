AI use: OpenAI Codex (GPT-6) assisted with the application, supplementary Portfolio D downside scenarios, and this memo on 2026-11-15 through 2026-11-19. Material contributions, checks, and the student's ten ACCEPT dispositions are in [validation-and-ai-use.md](validation-and-ai-use.md).

Ownership and educational purpose: I selected Portfolio D, independently checked its original-window return and volatility in Excel, and approved this conditional-pilot proposal. I own the investment judgment. This analysis is for education, not investment advice.

# Investment Committee Decision Memo

**Decision requested:** Consider a conditional pilot of my fixed Portfolio D allocation: **40% VTI / 25% VXUS / 15% XLE / 5% IWM / 15% IAU**. **No trade is authorized.** The optimizer remains on **REVIEW HOLD**: IAU shifts 25 percentage points between its 59-return and 36-return solutions, exceeding the more-than-20-point threshold. Implementation requires documented hold resolution and separate committee authorization.

## Mandate and proposed ranges

The client is a young investor with a flexible 15-year wealth-accumulation horizon. The governing Lab 15 amendment uses these five ETFs, long-only fully invested weights on a five-point grid, and **minimum estimated annualized volatility subject to a provisional 6% nominal annual arithmetic-return floor**. VTI is the benchmark. No gold cap, international-equity minimum, reserve, or volatility ceiling is approved. C is optimized; D is my fixed strategic judgment.

| ETF | D target | Proposed range | Portfolio role |
| --- | ---: | ---: | --- |
| VTI | 40% | 35–45% | Broad U.S. equity core |
| VXUS | 25% | 20–30% | International equity exposure |
| XLE | 15% | 10–15% | Limited direct energy tilt |
| IWM | 5% | 5–10% | Modest small-cap exposure |
| IAU | 15% | 10–20% | Gold diversifier |

These ranges are **proposed guardrails**, not active constraints or trading instructions. Their frozen-data feasibility is documented in [Portfolio D analysis](proposed-allocation-analysis.md); adoption requires committee approval.

## Historical evidence and investment judgment

Figures are annual arithmetic return estimates / annualized sample volatility from frozen adjusted prices. The original snapshot was retrieved **2026-10-22** with a **2026-09-30 observation cutoff**; the extended snapshot was retrieved **2026-11-16**. Windows overlap and use different estimates; this is **not** an independent out-of-sample test.

| Original 59-return comparison | Return | Volatility | Allocation or role |
| --- | ---: | ---: | --- |
| A — equal weight | 14.02% | 13.66% | 20% in each ETF |
| B — Lab 15 reference | 12.67% | 13.88% | 45/25/10/10/10% |
| C — minimum volatility | **15.66%** | **12.27%** | 50/0/10/0/40% |
| D — student proposal | **13.74%** | **13.27%** | 40/25/15/5/15% |

All four portfolios pass the modeled construction rules and 6% estimate on this window. **C is mathematically superior to D on both original-sample estimates:** D has **1.92 percentage points less estimated return** and **1.00 point more estimated volatility**. I accept that modeled volatility cost as a proposed suitability trade-off, not as evidence that D improves the optimization result.

| Estimation window | D return / volatility | C return / volatility | VTI benchmark return / volatility |
| --- | --- | --- | --- |
| Extended 119 returns | 13.43% / 14.26% | 14.12% / 11.69% | 15.38% / 15.80% |
| Original 59 returns | 13.74% / 13.27% | 15.66% / 12.27% | 12.00% / 15.87% |
| Recent 36 returns | 20.80% / 10.08% | 20.76% / 9.79% | 21.11% / 12.86% |

The minimum-volatility solution holds **40% IAU / 0% VXUS** originally and **50% IAU / 0% VXUS** on the extended window. Gold's estimated covariance explains these valid optimizer choices without settling long-horizon suitability. D deliberately holds **25% VXUS / 15% IAU**, reducing gold reliance but accepting greater equity risk and an XLE tilt overlapping broad-market funds. D passes the modeled mandate on all three windows; fixed weights do **not** resolve optimizer instability. The separate [diversification-policy sensitivity](proposed-allocation-analysis.md) remains **unapproved**.

## Downside risk and implementation decision

D's monthly-observed maximum drawdown is **−17.21%** originally and **−23.86%** on the extended window. These monthly-rebalanced, in-sample reconstructions omit taxes and costs. Even the extended history is shorter than the 15-year horizon; adjusted prices may be revised, and estimated returns and correlations may not persist.

Fixed-D hypothetical stresses expose consequential risks. Cutting each equity ETF's annual return estimate by **10 percentage points** lowers D's estimate from **13.74% to 5.24%**, below the provisional 6% floor. Raising IAU's correlations with the equity ETFs by **0.20** raises estimated volatility from **13.27% to 13.85%**; raising all four equity ETF volatilities by **25%** raises it to **16.31%**. The latter two remain modeled passes because the mandate has no volatility ceiling. These are sensitivity assumptions, not forecasts or changed approved inputs; [inputs and calculations](portfolio-d-sensitivity-output.md) are reproducible. [Existing optimizer and cost stresses](visible-executed-output.md) provide additional context.

Four gates govern any pilot:

1. **Hard rules:** Validate data, weights, and the 6% floor; invalid inputs or infeasible approved optimization stop implementation. The hypothetical equity shock is a warning, not today's base-case failure.
2. **REVIEW HOLD and suitability:** Document the 25-point instability; review D's windows, drawdowns, concentration, costs, and sensitivities. The committee must accept additional modeled volatility, equity/energy risk, and estimation uncertainty. Fixed D does not clear the hold.
3. **Authorization:** The committee must record hold resolution and separately authorize a pilot, target, ranges, and controls. An exception does not erase the app's historical REVIEW HOLD diagnostic; this memo authorizes no trade.
4. **Monitoring and suspension:** If authorized, review data, return-floor compliance, optimizer stability, ranges, concentration, and costs **quarterly**. Consider rebalancing **annually** after current cost, tax, and mandate checks. Hard failure stops trading; renewed instability, a range breach, or material risk/return/cost changes suspend pilot trades for committee review. Reversal requires another committee decision.

**Committee ask:** Review the documented hold resolution and D's strategic diversification trade-off, then decide whether to authorize a limited conditional pilot under the proposed ranges and controls or defer implementation. The [methodology](mandate-and-methodology.md), [Portfolio D analysis](proposed-allocation-analysis.md), and [validation and AI-use record](validation-and-ai-use.md) provide the supporting evidence.
