# Locked Changed-Input Record

## Part A — Prediction (Before Execution)

**Date and Time:** 
Tuesday November 17th, 3:34pm

**Input Being Changed:**
I am testing how increasing the allocation to IWM (Russell 2000 small-cap equities) affects the estimated return and volatility of my proposed Portfolio D.

**Original Portfolio Allocation:**

| ETF | Original Weight |
|---|---:|
| VTI | 40% |
| VXUS | 25% |
| XLE | 15% |
| IWM | 5% |
| IAU | 15% |
| **Total** | **100%** |

**Original Estimated Results (59 Monthly Returns):**
- Annualized arithmetic return: 13.74%
- Annualized volatility: 13.27%

**New Allocation:**

IWM will increase from 5% to 15%.

To keep the portfolio fully invested at 100%, I will reduce XLE from 15% to 5%.

All remaining ETF weights will stay unchanged.

**Expected Direction of Financial Output:**

By increasing my IWM allocation from 5% to 15% and reducing XLE from 15% to 5%, I expect my portfolio's estimated annual return to decrease and annualized volatility to increase. Although this reduces my concentration in the energy sector, I believe the increased exposure to small-cap equities will introduce additional risk.

**Expected Effect on Investment Decision:**

I expect this change to weaken my original conditional-pilot recommendation. While increasing small-cap exposure could improve diversification across industries, I don't believe that benefit would justify a lower estimated return and higher volatility. If my prediction is correct, I would prefer to maintain my original Portfolio D allocation, assuming it continues to satisfy the investment mandate.

**Financial Reasoning Behind Prediction:**

XLE benefited from strong energy-sector performance during much of the historical period, particularly when energy prices increased. I believe reducing that exposure in favor of IWM will lower the portfolio's estimated return. I also expect volatility to increase because smaller companies can be more sensitive to economic conditions, financing costs, and interest rates. Although IWM provides broader industry exposure than XLE, it also overlaps with my existing VTI allocation. For these reasons, I expect the revised portfolio to have a less favorable historical risk-return profile.
---

## Part B — Actual Results (After Execution)

**Pre-Test Git Commit SHA:** 3c05cd3be7bbe6e9edba57bd9995f08da1ae0e4c

**Execution Date and Time:** Tuesday Novemeber 17th, 4:27pm

**Original Output:**

My original Portfolio D allocation had an estimated annual arithmetic return of 13.74% and annualized volatility of 13.27%. The portfolio satisfied the investment mandate.

**Changed Output:**

After increasing IWM from 5% to 15% and reducing XLE from 15% to 5%, the estimated annual return decreased to 12.24%, while annualized volatility increased to 13.87%.

This represents a 1.50 percentage-point reduction in estimated return and a 0.60 percentage-point increase in volatility. The revised portfolio continued to satisfy the mandate.

**Actual Effect on Investment Decision:**

The results weakened the case for changing my original Portfolio D allocation. Although increasing IWM reduced my direct concentration in the energy sector, the revised portfolio produced a less favorable historical risk-return combination. I would maintain my original Portfolio D recommendation rather than adopt the revised allocation. The original REVIEW HOLD remains in effect.

**Did the Results Match My Prediction?**

Yes. I predicted that increasing IWM and reducing XLE would decrease estimated return and increase volatility. Both changes occurred in the expected direction.

**Explanation of Results or Discrepancies:**

The results were consistent with my expectation that reducing XLE exposure would lower historical estimated returns over the selected period. Replacing part of that allocation with IWM also increased portfolio volatility, suggesting that the revised combination of asset weights and historical covariances was less effective at reducing risk.

This test demonstrates how sensitive portfolio outcomes can be to allocation decisions. However, these results are based on historical estimates and do not establish that XLE will outperform IWM in the future.

**Supporting Evidence:**

- [Before Screenshot](evidence/locked-before.png)
- [After Screenshot](evidence/locked-after.png)
- Pre-test prediction commit:(https://github.com/cmainville/FIN43900-Project2/commit/3c05cd3be7bbe6e9edba57bd9995f08da1ae0e4c)
