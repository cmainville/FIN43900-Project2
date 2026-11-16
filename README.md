AI use: OpenAI Codex (GPT-6) assisted with the application, portfolio engine, tests, and documentation on 2026-11-15. Material contributions and checks are tracked in [docs/validation-and-ai-use.md](docs/validation-and-ai-use.md).

Ownership and educational purpose: The investment analysis and final decision will be my own. This project is for education, not investment advice.

# FIN 43900 | Portfolio Decision System

This Streamlit application helps an investment committee evaluate a five-ETF portfolio process for a young investor with a flexible 15-year horizon. It compares two baselines with a constrained minimum-volatility portfolio, reports mandate verdicts, and flags allocation instability. The governing mandate is the student's intentional Lab 15 amendment to the earlier Lab 13 home-purchase mandate; see [mandate and methodology](docs/mandate-and-methodology.md). The app makes **no investment recommendation** yet.

## Install and launch

Use Python 3.14, the version used for the initial smoke test. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit and navigate the four tabs. No credentials or live market download are required. To reproduce the preserved financial output and run validation:

```bash
python -m portfolio_engine > docs/visible-executed-output.md
python -m unittest -v test_portfolio_engine.py
```

The first command regenerates the output artifact from the local fixed dataset. Review the diff before replacing a prior output snapshot.

## Repository map

| Path | Purpose |
| --- | --- |
| `app.py` | Single Streamlit application with four tabs |
| `portfolio_engine.py` | Data validation, estimates, baselines, grid optimizer, mandate checks, and output generation |
| `test_portfolio_engine.py` | Independent numerical fixtures and regression tests |
| `data/prices_growth.csv` | Frozen five-ETF adjusted-price snapshot |
| `requirements.txt` | Pinned application dependencies |
| `requirements/` | Governing Project 2 brief, architecture, checklist, and AI boundary card |
| `docs/mandate-and-methodology.md` | Approved mandate and calculation conventions |
| `docs/visible-executed-output.md` | Actual generated finance results visible without running code |
| `docs/requirements-tracker.md` | Requirement-to-evidence work plan |
| `docs/decision-memo.md` | Investment committee memo outline |
| `docs/validation-and-ai-use.md` | Working validation and AI-use record; reserved Locked Changed-Input Record section |

## Data and present limits

The [Lab 15 snapshot](https://github.com/cmainville/FIN43900/blob/main/lab15/prices_growth.csv) contains Yahoo Finance daily adjusted closes for **VTI, VXUS, XLE, IWM, IAU**, retrieved **2026-10-22** and sampled at each completed month's final trading day. The fixed labels run from October 2021 through September 2026; September 2026 is the as-of boundary. The local copy is byte-for-byte identical to the course snapshot. The app derives 59 full-window monthly returns and a last-36-return comparison. See the [methodology](docs/mandate-and-methodology.md) for field conventions, provenance, formulas, and limits.

The [visible executed output](docs/visible-executed-output.md) reports actual program results and the stability warning. Returns are arithmetic historical estimates, not compounded growth forecasts or guarantees. The 5-point grid is approximate; the historical window change breaches the student's monitoring threshold. Costs, taxes, future drawdowns, the required point-in-time signal, and the remaining stress scenarios are **not yet implemented**. Hard-rule compliance does not establish suitability.

Project 2 has no submitted Edition A/B or PDF artifact. The final submission requires this repository, the two Markdown documents, three YouTube video links with corrected transcripts, and a manifest. Video 3 must open with the functioning app. The student must personally author and commit the AI-off prediction for the Locked Changed-Input Record before the designated test is run.
