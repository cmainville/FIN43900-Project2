AI use: OpenAI Codex (GPT-6) assisted with the application, portfolio engine, signal, stress tests, supplementary historical and illustrative policy analysis, dashboard redesign, Portfolio D calculations and downside scenarios, automated tests, committee memo, and submission documentation on 2026-11-15 through 2026-11-19. Material contributions, checks, and the student's nine ACCEPT dispositions are tracked in [docs/validation-and-ai-use.md](docs/validation-and-ai-use.md).

Ownership and educational purpose: I selected Portfolio D, independently checked its original-window return and volatility in Excel, and approved the conditional-pilot proposal. I own the investment judgment. This project is for education, not investment advice.

# FIN 43900 | Portfolio Decision System

This Streamlit application helps an investment committee evaluate a five-ETF portfolio process for a young investor with a flexible 15-year horizon. It compares two baselines with a constrained minimum-volatility portfolio, reports mandate verdicts, ranks one trailing-momentum signal, and shows four stress dimensions, a supplementary ten-year historical comparison, an illustrative diversification-policy sensitivity, and an implementation process status. The student selected fixed [Portfolio D](docs/proposed-allocation-analysis.md) and approved a **conditional-pilot recommendation** for committee consideration. The [committee memo](docs/decision-memo.md) explains the proposed allocation ranges and trade-off. The approved optimizer's **REVIEW HOLD** remains active; no pilot is authorized. The governing mandate is the student's intentional Lab 15 amendment to the earlier Lab 13 home-purchase mandate; see [mandate and methodology](docs/mandate-and-methodology.md).

## Install and launch

Use Python 3.14; the 2026-11-19 clean-environment audit used Python 3.14.7. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. The persistent sidebar opens on **Overview** and offers **Analytics** and **Decision**. Analytics contains Portfolio Explorer, Optimization, Risk & Stress Tests, and Historical Analysis. No credentials or live market download are required. To check the preserved financial output and run validation:

```bash
python -m portfolio_engine | cmp - docs/visible-executed-output.md
python -m portfolio_d_sensitivity | cmp - docs/portfolio-d-sensitivity-output.md
python -m unittest -v test_portfolio_engine.py test_milestone3.py test_extended.py test_policy.py test_dashboard.py test_proposed_portfolio.py test_portfolio_d_sensitivity.py
```

The first two commands compare fresh engine and Portfolio D downside output with frozen artifacts without replacing them. Interactive scenarios use local frozen inputs and session state; they never overwrite official output. For a student-owned launch and control check, use the [manual cold-run checklist](docs/manual-cold-run-checklist.md).

## Repository map

| Path | Purpose |
| --- | --- |
| `app.py` | Single Streamlit dashboard with sidebar navigation and four Analytics tabs |
| `dashboard_analytics.py` | Interactive scenario estimates, finite-grid frontier, custom-weight validation, growth, and drawdown |
| `.streamlit/config.toml` | Native dark theme and institutional color palette |
| `portfolio_engine.py` | Data validation, estimates, baselines, grid optimizer, mandate checks, and output generation |
| `portfolio_d_sensitivity.py` | Separate fixed-weight D assumption shocks and reproducible output |
| `test_portfolio_engine.py` | Independent numerical fixtures and regression tests |
| `test_milestone3.py` | Signal, stress, cost, and process-rule fixtures |
| `test_extended.py` | Extended-data integrity, offline replay, arithmetic checks, and window regressions |
| `test_policy.py` | Independent grid fixture, policy bounds, preserved results, and app table checks |
| `test_dashboard.py` | Dashboard math fixtures and Streamlit interaction checks |
| `test_portfolio_d_sensitivity.py` | Independent numerical fixtures for D return, correlation, and volatility shocks |
| `data/prices_growth.csv` | Frozen five-ETF adjusted-price snapshot |
| `data/prices_growth_extended.csv` | Separate frozen ten-year Yahoo adjusted-price snapshot |
| `data/yahoo_raw_extended_2026-11-16.zip` | Raw Yahoo responses for offline replay |
| `data/extended-provenance.md` | Extended-source dates, hashes, and overlap comparison |
| `prepare_extended_prices.py` | Offline raw-response to month-end CSV preparation |
| `requirements.txt` | Pinned application dependencies |
| `requirements/` | Governing Project 2 brief, architecture, checklist, and AI boundary card |
| `docs/mandate-and-methodology.md` | Approved mandate and calculation conventions |
| `docs/visible-executed-output.md` | Actual generated finance results visible without running code |
| `docs/portfolio-d-sensitivity-output.md` | Generated, fixed-weight Portfolio D downside scenarios |
| `docs/proposed-allocation-analysis.md` | Student-selected Portfolio D results and conditional-pilot evidence |
| `docs/requirements-tracker.md` | Requirement-to-evidence work plan |
| `docs/decision-memo.md` | Student-approved conditional-pilot proposal and committee ask; implementation requires committee authorization |
| `docs/validation-and-ai-use.md` | Source, test, AI-use, and completed changed-input evidence record |
| `docs/locked-changed-input-record-v2.md` | Preserved Test 2 prediction and result, with linked screenshots |
| `docs/submission-manifest.md` | Twelve-row submission index and pending video fields |
| `docs/video-production-guide.md` | Recording plan and evidence checklist; transcripts follow actual recordings |
| `docs/final-rubric-audit.md` | Six-category evidence audit and final action checklist |
| `docs/manual-cold-run-checklist.md` | Student-owned manual launch and interaction checks; not yet marked complete |

## Data and present limits

The [Lab 15 snapshot](https://github.com/cmainville/FIN43900/blob/main/lab15/prices_growth.csv) contains Yahoo Finance daily adjusted closes for **VTI, VXUS, XLE, IWM, IAU**, retrieved **2026-10-22** and sampled at each completed month's final trading day. The fixed labels run from October 2021 through September 2026; September 2026 is the observation cutoff, while October 22 is the documented snapshot retrieval/availability date. The local copy is byte-for-byte identical to the course snapshot. The app derives 59 full-window monthly returns and a last-36-return comparison. See the [methodology and signal data card](docs/mandate-and-methodology.md) for field conventions, provenance, formulas, and limits.

The separate [extended snapshot](data/extended-provenance.md) was retrieved from Yahoo Finance on **2026-11-16**. It covers October 2016 through September 2026: 120 monthly prices and 119 returns. Raw responses, the preparation script, the frozen CSV, and hashes support offline reproduction. The original Lab 15 CSV and its 59- and 36-return analyses remain unchanged; the two downloads are not spliced. The newer overlapping prices differ slightly from the original snapshot.

The [visible executed output](docs/visible-executed-output.md) is generated from code and reports actual A/B/C/D estimates, momentum, sensitivity scenarios, three-window robustness, the **NOT APPROVED** IAU ≤20% / VXUS ≥15% policy overlay, and the current **REVIEW HOLD**. A separate [generated D downside artifact](docs/portfolio-d-sensitivity-output.md) holds the recommended weights fixed under three hypothetical assumption shocks; it does not change the official optimizer or locked record. The dashboard adds hypothetical controls, finite-grid frontier, and historical growth/drawdown. Growth starts at $100 and resets portfolio weights monthly; optimized weights applied to their own estimation history are hindsight reconstructions. Returns are arithmetic historical estimates, not compounded growth forecasts or guarantees. The 5-point grid is approximate; the original 59-vs-36 window change breaches the student's monitoring threshold. Costs are hypothetical one-time implementation amounts and exclude taxes. Neither snapshot proves that adjusted-price history was archived at its earlier observation dates. Ten years remains shorter than the 15-year planning horizon; overlapping windows are not an independent out-of-sample test. Hard-rule compliance and the signal do not establish suitability. The student has approved the memo's pilot proposal, ranges, and monitoring cadence; committee authorization and hold resolution remain outstanding.

Project 2 has no submitted Edition A/B or PDF artifact. The final submission requires this repository, the decision memo and validation Markdown files, three YouTube video links with corrected transcripts, and a [manifest](docs/submission-manifest.md). Video 3 must open with the functioning app. The student confirms personally completing the [Test 2 changed-input record](docs/locked-changed-input-record-v2.md) without AI assistance; its pre-run commit, results, and screenshots are preserved in [validation](docs/validation-and-ai-use.md). See the [rubric audit](docs/final-rubric-audit.md) for remaining recording and submission actions.
