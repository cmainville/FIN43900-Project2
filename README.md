AI use: OpenAI Codex (GPT-6) assisted with the application, portfolio engine, signal, stress tests, supplementary historical and illustrative policy analysis, dashboard redesign, automated tests, and documentation on 2026-11-15 and 2026-11-16. Material contributions and checks are tracked in [docs/validation-and-ai-use.md](docs/validation-and-ai-use.md).

Ownership and educational purpose: The investment analysis and final decision will be my own. This project is for education, not investment advice.

# FIN 43900 | Portfolio Decision System

This Streamlit application helps an investment committee evaluate a five-ETF portfolio process for a young investor with a flexible 15-year horizon. It compares two baselines with a constrained minimum-volatility portfolio, reports mandate verdicts, ranks one trailing-momentum signal, and shows four stress dimensions, a supplementary ten-year historical comparison, an illustrative diversification-policy sensitivity, and an implementation process status. The governing mandate is the student's intentional Lab 15 amendment to the earlier Lab 13 home-purchase mandate; see [mandate and methodology](docs/mandate-and-methodology.md). The app makes **no investment recommendation** yet.

## Install and launch

Use Python 3.14; Milestone 4B's clean-environment check used Python 3.14.7. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. The persistent sidebar opens on **Overview** and offers **Analytics** and **Decision**. Analytics contains Portfolio Explorer, Optimization, Risk & Stress Tests, and Historical Analysis. No credentials or live market download are required. To check the preserved financial output and run validation:

```bash
python -m portfolio_engine | cmp - docs/visible-executed-output.md
python -m unittest -v test_portfolio_engine.py test_milestone3.py test_extended.py test_policy.py test_dashboard.py
```

The first command compares fresh engine output with the frozen artifact without replacing it. Interactive scenarios use local frozen inputs and session state; they never overwrite official output.

## Repository map

| Path | Purpose |
| --- | --- |
| `app.py` | Single Streamlit dashboard with sidebar navigation and four Analytics tabs |
| `dashboard_analytics.py` | Interactive scenario estimates, finite-grid frontier, custom-weight validation, growth, and drawdown |
| `.streamlit/config.toml` | Native dark theme and institutional color palette |
| `portfolio_engine.py` | Data validation, estimates, baselines, grid optimizer, mandate checks, and output generation |
| `test_portfolio_engine.py` | Independent numerical fixtures and regression tests |
| `test_milestone3.py` | Signal, stress, cost, and process-rule fixtures |
| `test_extended.py` | Extended-data integrity, offline replay, arithmetic checks, and window regressions |
| `test_policy.py` | Independent grid fixture, policy bounds, preserved results, and app table checks |
| `test_dashboard.py` | Dashboard math fixtures and Streamlit interaction checks |
| `data/prices_growth.csv` | Frozen five-ETF adjusted-price snapshot |
| `data/prices_growth_extended.csv` | Separate frozen ten-year Yahoo adjusted-price snapshot |
| `data/yahoo_raw_extended_2026-11-16.zip` | Raw Yahoo responses for offline replay |
| `data/extended-provenance.md` | Extended-source dates, hashes, and overlap comparison |
| `prepare_extended_prices.py` | Offline raw-response to month-end CSV preparation |
| `requirements.txt` | Pinned application dependencies |
| `requirements/` | Governing Project 2 brief, architecture, checklist, and AI boundary card |
| `docs/mandate-and-methodology.md` | Approved mandate and calculation conventions |
| `docs/visible-executed-output.md` | Actual generated finance results visible without running code |
| `docs/requirements-tracker.md` | Requirement-to-evidence work plan |
| `docs/decision-memo.md` | Investment committee memo outline |
| `docs/validation-and-ai-use.md` | Working validation and AI-use record; reserved Locked Changed-Input Record section |

## Data and present limits

The [Lab 15 snapshot](https://github.com/cmainville/FIN43900/blob/main/lab15/prices_growth.csv) contains Yahoo Finance daily adjusted closes for **VTI, VXUS, XLE, IWM, IAU**, retrieved **2026-10-22** and sampled at each completed month's final trading day. The fixed labels run from October 2021 through September 2026; September 2026 is the observation cutoff, while October 22 is the documented snapshot retrieval/availability date. The local copy is byte-for-byte identical to the course snapshot. The app derives 59 full-window monthly returns and a last-36-return comparison. See the [methodology and signal data card](docs/mandate-and-methodology.md) for field conventions, provenance, formulas, and limits.

The separate [extended snapshot](data/extended-provenance.md) was retrieved from Yahoo Finance on **2026-11-16**. It covers October 2016 through September 2026: 120 monthly prices and 119 returns. Raw responses, the preparation script, the frozen CSV, and hashes support offline reproduction. The original Lab 15 CSV and its 59- and 36-return analyses remain unchanged; the two downloads are not spliced. The newer overlapping prices differ slightly from the original snapshot.

The [visible executed output](docs/visible-executed-output.md) reports actual program results, momentum ranking, sensitivity scenarios, three-window robustness, the **NOT APPROVED** IAU ≤20% / VXUS ≥15% policy overlay, and the current **REVIEW HOLD**. The dashboard adds hypothetical controls, finite-grid frontier, and historical growth/drawdown. Growth starts at $100 and resets portfolio weights monthly; optimized weights applied to their own estimation history are hindsight reconstructions. Returns are arithmetic historical estimates, not compounded growth forecasts or guarantees. The 5-point grid is approximate; the original 59-vs-36 window change breaches the student's monitoring threshold. Cost estimates are hypothetical one-time implementation amounts and exclude taxes. Neither snapshot proves that adjusted-price history was archived at its earlier observation dates. Ten years remains shorter than the 15-year planning horizon; overlapping windows are not an independent out-of-sample test. Hard-rule compliance and the signal do not establish suitability; the final recommendation and allocation range remain pending.

Project 2 has no submitted Edition A/B or PDF artifact. The final submission requires this repository, the two Markdown documents, three YouTube video links with corrected transcripts, and a manifest. Video 3 must open with the functioning app. The student must personally author and commit the AI-off prediction for the Locked Changed-Input Record before the designated test is run.
