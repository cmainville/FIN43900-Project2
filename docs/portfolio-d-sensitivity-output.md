# Portfolio D — Supplementary Downside Sensitivity Output

Input: `data/prices_growth.csv`; SHA-256 `9b8d269bddae60e67548ae9f68f71429a4eab001b67cb7efb03e14082cd2609d`.
Observation cutoff: **2026-09-30**; snapshot retrieval/availability: **2026-10-22**; original **59 monthly returns**.
Weights held fixed: **VTI 40% / VXUS 25% / XLE 15% / IWM 5% / IAU 15%**. Each shock is separate and hypothetical; Portfolio D is not reoptimized.
Annual arithmetic return = mean monthly simple return ×12; annual sample covariance = monthly sample covariance ×12; volatility = √(wᵀΣw).

| Scenario | Exact hypothetical input | Base return | Stressed return | Change | Base volatility | Stressed volatility | Change | Modeled mandate |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Equity return −10 pp | All four equity ETF annual arithmetic return estimates −10 percentage points; covariance fixed. | 13.74% | 5.24% | -8.50 pp | 13.27% | 13.27% | +0.00 pp | FAIL: estimated annual nominal return is below the provisional 6% floor |
| Gold correlation +0.20 | IAU correlation with each equity ETF +0.20; standalone volatilities and annual returns fixed. | 13.74% | 13.74% | +0.00 pp | 13.27% | 13.85% | +0.58 pp | PASS |
| Equity volatility ×1.25 | Each equity ETF annualized volatility ×1.25; correlations and annual returns fixed. | 13.74% | 13.74% | +0.00 pp | 13.27% | 16.31% | +3.04 pp | PASS |

The return shock tests equity-estimate dependence; its covariance is unchanged. The gold shock tests reduced diversification: correlations rise together, standalone risk stays fixed, and the resulting covariance is checked for positive semidefiniteness. The volatility shock tests a broad equity-risk increase: covariance is rebuilt by scaling both axes, so historical correlations are preserved.
The approved original 59-versus-36 process status remains **REVIEW HOLD**. A hypothetical failure does not itself change the approved base-case mandate verdict; a comparable validated input change would require review before implementation. No scenario is a forecast, independent backtest, or part of the student-owned Locked Changed-Input Record.
