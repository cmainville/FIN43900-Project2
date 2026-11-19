AI use: OpenAI Codex (GPT-6) assisted with the application, supplementary Portfolio D downside scenarios, and this memo on 2026-11-15 through 2026-11-19. Material contributions, checks, and the student's nine ACCEPT dispositions are in [validation-and-ai-use.md](validation-and-ai-use.md).

Ownership and educational purpose: I selected Portfolio D, independently checked its original-window return and volatility in Excel, and approved this conditional-pilot proposal. I own the investment judgment. This analysis is for education, not investment advice.

# Investment Committee Decision Memo

**Decision requested — conditional pilot of Portfolio D.** I recommend that the committee consider the fixed **40% VTI / 25% VXUS / 15% XLE / 5% IWM / 15% IAU** allocation within the proposed ranges below. I approve this recommendation and monitoring framework for committee consideration. **No trade or pilot starts now:** the approved optimizer is on **REVIEW HOLD** because IAU moves 25 percentage points between the original 59-return and recent 36-return optimized portfolios. Implementation requires a documented resolution of that hold and suitability trade-off, followed by explicit committee authorization. No committee approval is claimed.

## Mandate and proposed allocation policy

The client is a young wealth accumulator with a flexible 15-year horizon. The governing Lab 15 amendment to the earlier Lab 13 mandate uses the five ETFs above, a long-only fully invested five-point grid, and **minimum estimated annualized volatility subject to a provisional 6% nominal annual arithmetic-return floor**. VTI is the external benchmark. There is no approved gold cap, VXUS minimum, cash reserve, or maximum-volatility ceiling. Portfolio D is my fixed allocation judgment; it is **not** Portfolio C's optimization output. Its modeled mandate verdict passes on all three historical windows, but compliance alone does not establish suitability.

| ETF | D target | Proposed committee range | Purpose and judgment |
| --- | ---: | ---: | --- |
| VTI | 40% | 35–45% | Broad U.S. equity core; avoids making the single U.S. fund the entire growth exposure |
| VXUS | 25% | 20–30% | Maintains material international equity exposure absent from the longer-window C optimizers |
| XLE | 15% | 10–15% | Retains energy tilt while limiting further direct sector concentration; energy also overlaps economically with VTI |
| IWM | 5% | 5–10% | Modest small-cap exposure; the student's [locked changed-input test](locked-changed-input-record-v2.md) found a larger IWM tilt worsened the original-window estimated return and volatility |
| IAU | 15% | 10–20% | Diversifier without allowing gold to dominate the growth allocation |

These **proposed** ranges are committee guardrails, not amendments to the active mandate or optimizer. On the existing 5-point grid, **26** fully invested allocations satisfy all five ranges, including D; all 26 clear the historical 6% estimate on each of the three frozen windows. This confirms mechanical feasibility under these samples, not future return or suitability. The ranges permit drift and considered rebalancing but do not authorize automatic trades. I approve the bounds as a proposal; committee approval remains outstanding.

## Evidence and trade-off

All figures below are **historical annual arithmetic return estimates / annualized sample volatility**. Within a row, portfolios use the same frozen covariance and return estimates. The original Yahoo adjusted-close snapshot was retrieved **2026-10-22** and ends at the **2026-09-30 observation cutoff**; the separate extended snapshot was retrieved **2026-11-16**. The windows overlap and are not an independent out-of-sample test.

| Portfolio | Original 59-return estimate | Allocation or role | Modeled verdict |
| --- | --- | --- | --- |
| A — equal weight | 14.02% / 13.66% | 20% in each ETF | PASS |
| B — Lab 15 reference | 12.67% / 13.88% | 45/25/10/10/10% | PASS |
| C — original minimum-volatility output | 15.66% / 12.27% | 50/0/10/0/40% | PASS; official optimizer remains on REVIEW HOLD |
| D — student selected | 13.74% / 13.27% | 40/25/15/5/15% | PASS; pilot not authorized |
| VTI market benchmark | 12.00% / 15.87% | 100% VTI; not a baseline | Context only |

| Window | D return / volatility | C return / volatility | Unapproved policy return / volatility | VTI return / volatility |
| --- | --- | --- | --- | --- |
| Extended 119 returns | 13.43% / 14.26% | 14.12% / 11.69% | 12.81% / 12.92% | 15.38% / 15.80% |
| Original 59 returns | 13.74% / 13.27% | 15.66% / 12.27% | 14.30% / 12.85% | 12.00% / 15.87% |
| Recent 36 returns | 20.80% / 10.08% | 20.76% / 9.79% | 20.76% / 9.79% | 21.11% / 12.86% |

**Why consider D:** Historical minimum variance produces **40% IAU and 0% VXUS** on the original window and **50% IAU and 0% VXUS** on the extended window. Low estimated IAU covariance helps explain C mathematically, but that concentration and lack of strategic international equity raise a long-horizon suitability question. D holds **85% in equity ETFs**, including **25% VXUS**, and **15% IAU**. I accept a measured *estimated* volatility cost for that construction choice: D exceeds C by **2.57**, **1.00**, and **0.29 percentage points** on the extended, original, and recent windows. On the original window D's estimated return is **1.92 points lower** than C. D is therefore **not** mathematically superior to C. The separate IAU ≤20% / VXUS ≥15% policy sensitivity is **not approved**; it shows another diversification trade-off, not a replacement for C or D.

## Risks, stress, and implementation controls

D's observed monthly peak-to-trough drawdown is **−23.86%**, **−17.21%**, and **−4.34%** across the extended, original, and recent samples. These monthly-rebalanced, monthly-observed wealth paths omit costs and taxes and cannot predict a 15-year outcome. The energy tilt adds sector and broad-market overlap; equity, gold, and estimated-correlation risk remain. The 119-return history is still shorter than the 15-year planning horizon. The 12-month momentum signal ranks XLE first and IAU last at the September 2026 cutoff, but its October 22 retrieval boundary and revised adjusted histories prevent treating it as a validated forecast or optimizer input.

The approved **59-vs-36** optimizer comparison moves IAU **25 points**, exceeding the **strictly greater than 20-point** review threshold. The extended comparison is supplementary and does not redefine that rule. D's constant weights across windows are fixed by construction and do **not** resolve the optimized-process instability. Existing estimate, cost, and return-floor scenarios remain in the [generated output](visible-executed-output.md); the student's separate [changed-input record](locked-changed-input-record-v2.md) is reproduced in [validation](validation-and-ai-use.md).

**D-specific downside evidence:** On the original 59-return estimates, a hypothetical **10-percentage-point cut to each equity ETF's annual return estimate** lowers fixed D's estimated return from **13.74% to 5.24%**, below the provisional 6% floor. Raising IAU's correlations with all four equity ETFs by **0.20** raises D's estimated volatility from **13.27% to 13.85%**; increasing all four equity ETF volatilities by **25%** raises it to **16.31%**. The latter scenarios still pass the modeled mandate because there is no volatility ceiling, yet they demand explicit risk acceptance. These separate, internally checked assumptions are **hypothetical**, so the first result does not itself change today's base-case PASS. Detailed inputs, percentage-point changes, and limits are in [Portfolio D analysis](proposed-allocation-analysis.md).

One-time illustrative costs are **0.020–0.050%** of portfolio value to rebalance B→D and **0.070–0.175%** for original C→D at 10–25 basis points per dollar traded on buys and sells. These are not annual return deductions; taxes and other frictions are excluded. A current holding account was not provided, so neither route is an actual trade plan.

**Decision and implementation gates:**

1. **Hard mandate failure:** Invalid required data, no mandate-feasible optimized allocation, invalid D weights, or a validated D estimate below the 6% floor prevents a pilot. The hypothetical downside result above is a warning, not a changed approved input.
2. **Monitoring hold and suitability review:** The existing 25-point IAU change keeps implementation paused. Before any pilot, document why D's fixed equity and international exposure is preferable for this investor despite C's lower modeled volatility, and review D's three-window results, drawdowns, concentration, costs, and downside sensitivities. The committee must explicitly accept the additional modeled volatility, equity/energy exposure, reliance on estimated correlations, and remaining historical uncertainty. Selecting D alone does not clear the numerical trigger.
3. **Authorization:** The committee must record a written resolution of the active hold and separately authorize any conditional pilot, target, ranges, and controls. An authorized exception would not erase the app's historical REVIEW HOLD diagnostic; no trade follows from this memo alone.
4. **After authorization:** Review data integrity, the return floor, C's 59-vs-36 stability, D's weights and proposed ranges, concentration, and costs **quarterly**. Consider rebalancing to D **annually**, only after a current cost/tax and mandate check; do not trade automatically. A hard failure stops implementation. A renewed monitoring breach, range breach, or material change in risk, return, or costs suspends further pilot trading for committee review. Reversal or replacement requires a new committee decision, not an automatic switch to C.

**Committee ask:** Review the documented hold resolution and D's downside trade-off, then decide whether to authorize a limited conditional pilot under the proposed ranges and controls or to defer it. The [methodology](mandate-and-methodology.md) and [validation and named AI-use record](validation-and-ai-use.md) support this decision.
