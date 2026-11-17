# Locked Changed-Input Record — Test 2

## Part A — Prediction Before Execution

**Date and Time:** 11/17/26 @ 5:08pm

**Input Being Changed:**

I am testing how increasing IWM from 5% to 25% affects the estimated return and volatility of Portfolio D. I will fund the increase by reducing VTI from 40% to 30% and XLE from 15% to 5%.

**Original Portfolio Allocation:**

| ETF | Original | Revised |
|---|---:|---:|
| VTI | 40% | 30% |
| VXUS | 25% | 25% |
| XLE | 15% | 5% |
| IWM | 5% | 25% |
| IAU | 15% | 15% |
| Total | 100% | 100% |

**Original Estimated Results (59 Monthly Returns):**

- Annualized arithmetic return: 13.74%
- Annualized volatility: 13.27%
- Mandate verdict: PASS

**Expected Direction of Financial Output:**

I expect the portfolio's estimated annual return to decrease and annualized volatility to increase. Increasing IWM to 25% creates a much larger small-cap allocation, while reducing exposure to VTI and XLE. I expect the additional small-cap risk to outweigh the diversification benefit over the historical estimation period.

**Expected Effect on Investment Decision:**

I expect this change to weaken my case for adopting the revised portfolio. Although IWM provides exposure to a broad range of smaller U.S. companies, I do not believe the additional allocation will improve the historical risk-return trade-off enough to justify replacing my original Portfolio D. If my prediction is correct, I would retain the original allocation and continue the conditional review process.

**Financial Reasoning Behind Prediction:**

XLE benefited from strong energy-sector returns during portions of the historical period, while smaller companies faced challenges associated with economic uncertainty and elevated borrowing costs. Reducing XLE and VTI to increase IWM may therefore lower the estimated portfolio return. I also expect greater volatility because small-cap stocks tend to be sensitive to economic conditions, and IWM overlaps with the broad U.S. equity exposure already represented by VTI. The actual volatility effect will depend on historical correlations between all five ETFs.

---

## Part B — Actual Results After Execution

**Part A Commit SHA:** 4171e014c3b871993bce416523d46a65888f16c6

**Execution Date and Time:** 11/17/26 @ 5:14pm

**Original Output:**

My original Portfolio D had an estimated annual arithmetic return of 13.74% and annualized volatility of 13.27%. The portfolio passed the investment mandate.

**Changed Output:**

After increasing IWM from 5% to 25%, reducing VTI from 40% to 30%, and reducing XLE from 15% to 5%, my portfolio's estimated annual return decreased to 11.79%, while annualized volatility increased to 14.27%.

This represents a 1.96 percentage-point decrease in estimated return and a 1.00 percentage-point increase in volatility. The revised portfolio still passed the investment mandate's 6% return requirement.

**Actual Effect on Investment Decision:**

The results weakened my case for increasing the IWM allocation. Although the revised portfolio provided greater small-cap exposure and reduced energy concentration, it produced a lower estimated return and higher volatility. I would maintain my original Portfolio D allocation rather than adopt this alternative. The existing REVIEW HOLD remains in effect.

**Did the Results Match My Prediction?**

Yes. I predicted that increasing small-cap exposure while reducing VTI and XLE would decrease estimated annual return and increase volatility. Both changes occurred in the expected direction.

**Explanation of Results:**

The results support my initial expectation that shifting additional weight toward IWM would produce a less favorable historical risk-return profile. Reducing exposure to XLE, which performed strongly during portions of the estimation period, contributed to the lower estimated return.

The increase in volatility also suggests that the revised weights and historical relationships between the ETFs did not provide enough diversification benefit to offset the additional risk. These findings apply to the historical estimation window and do not guarantee similar future performance.

**Supporting Evidence:**

- [Before Screenshot](evidence/locked-v2-before.png)
- [After Screenshot](evidence/locked-v2-after.png)
- [Part A Prediction Commit](https://github.com/cmainville/FIN43900-Project2/commit/4171e014c3b871993bce416523d46a65888f16c6)

