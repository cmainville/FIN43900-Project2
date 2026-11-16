# Validation and AI-Use Record

**Status:** Working record through Milestone 3. Historical portfolio calculations, the signal, four stress dimensions, data-shape checks, and application execution have been tested. Investment suitability and the final recommendation remain unverified.

## Sources and as-of dates

| Source | As-of or access date | Use and boundary | Verification |
| --- | --- | --- | --- |
| `requirements/` governing Markdown files | Read 2026-11-15 | Project 2 scope and evidence requirements | Read all four files; Project 2 exceptions applied |
| [Lab 13 mandate](https://github.com/cmainville/FIN43900/blob/main/lab13-defense.md) | Read 2026-11-15 | Original personal five-year home-purchase mandate | Compared with explicit Lab 15 amendment; earlier 4% floor and 30% reserve are superseded for Project 2 |
| [Lab 14 methodology](https://github.com/cmainville/FIN43900/blob/main/portfolio.py) and [Lab 15 engine/tests](https://github.com/cmainville/FIN43900/blob/main/lab15/portfolio.py) | Read 2026-11-15 | Arithmetic returns, covariance risk, exhaustive 5-point search, known answers | Adapted with small independent fixtures and regression comparisons |
| [Lab 15 source notes](https://github.com/cmainville/FIN43900/blob/main/lab15/lab15-notes.md) and [price snapshot](https://github.com/cmainville/FIN43900/blob/main/lab15/prices_growth.csv) | Retrieved 2026-10-22 per Lab 15; inspected/copied 2026-11-15 | Yahoo Finance daily `Adj Close`; last trading-day close per month labeled calendar month-end; September 2026 observation cutoff, October 22 snapshot retrieval/availability | Local snapshot Git blob SHA `55604a3c2b34cbe041c99fb4ae828495cb0b1f1b` matches original; SHA-256 `9b8d269bddae60e67548ae9f68f71429a4eab001b67cb7efb03e14082cd2609d`; schema/window/value checks passed. Original raw vendor downloads were not independently re-fetched |
| One cross-sectional momentum signal | Calculated 2026-11-15 from snapshot retrieved 2026-10-22 | September 2025 and September 2026 adjusted-price endpoints; no later observations | Exact endpoint, no-future-data, ranking, and invalid-endpoint tests in `test_milestone3.py`; complete data card in `docs/mandate-and-methodology.md` |

## Tests and independent checks

| Date | Check | Result | Evidence or follow-up |
| --- | --- | --- | --- |
| 2026-11-15 | Python syntax check for `app.py` | PASS | `python3 -m py_compile app.py` exited 0 |
| 2026-11-15 | Streamlit script and four-tab smoke test | PASS | `streamlit.testing.v1.AppTest.from_file("app.py").run()` returned no exception and exactly the four expected tab labels |
| 2026-11-15 | Local Streamlit server launch and health check | PASS | `python3 -m streamlit run app.py --server.headless true --server.port 8505 --browser.gatherUsageStats false` started; `curl --fail --silent --show-error http://localhost:8505/_stcore/health` returned `ok`; server stopped afterward. Initial sandboxed port bind and health request were denied, so these checks ran with local network permission |
| 2026-11-15 | Milestone 2 syntax | PASS | `python3 -m py_compile app.py portfolio_engine.py test_portfolio_engine.py` exited 0 |
| 2026-11-15 | Frozen snapshot integrity | PASS | `git hash-object data/prices_growth.csv` matched prior repo blob SHA; loader accepted 60 ordered month labels, five exact tickers, finite positive prices; malformed schema/dates/missing/nonpositive values rejected |
| 2026-11-15 | Unit tests | PASS: 7 tests | `python3 -m unittest -v test_portfolio_engine.py`; independent three-month arithmetic/covariance fixture, weights, objective, full 10,626-point grid, infeasibility, tie rule, data rejection, benchmark, threshold boundary, and Lab 15 known-answer comparisons |
| 2026-11-15 | Streamlit AppTest | PASS | Four required tabs, no script exception, and required REVIEW REQUIRED warning observed. First smoke-test assertion used an incorrect AppTest element attribute (`.message`); correcting the harness to `.value` passed without an app change |
| 2026-11-15 | Local Streamlit server | PASS | `python3 -m streamlit run app.py --server.headless true --server.port 8505 --browser.gatherUsageStats false` started; `/_stcore/health` returned `ok`; server stopped afterward |
| 2026-11-15 | Visible executed finance output | PASS | `python3 -m portfolio_engine > docs/visible-executed-output.md` generated the included artifact from the fixed snapshot; values match the tested engine |
| 2026-11-15 | Milestone 3 syntax | PASS | `python3 -m py_compile app.py portfolio_engine.py test_portfolio_engine.py test_milestone3.py` exited 0 |
| 2026-11-15 | Milestone 3 independent fixtures and regressions | PASS: 14 tests | `python3 -m unittest -v test_portfolio_engine.py test_milestone3.py`; signal cutoffs/ranking/no future row, isolated return shock, covariance/correlation stress, buy-plus-sell cost, 6/16/25% floor feasibility, hard-failure/review-hold precedence, prior allocations preserved |
| 2026-11-15 | Milestone 3 Streamlit AppTest | PASS | Four required tabs, no exception, momentum table value 41.60%, and REVIEW REQUIRED warning present. A first harness assertion mistakenly tested DataFrame column membership; checking its rendered value passed without an app change |
| 2026-11-15 | Milestone 3 local server | PASS | `python3 -m streamlit run app.py --server.headless true --server.port 8505 --browser.gatherUsageStats false` started; `/_stcore/health` returned `ok`; server stopped afterward |
| 2026-11-15 | Milestone 3 visible output | PASS | `python3 -m portfolio_engine > docs/visible-executed-output.md` generated signal, scenarios, costs, status, and limits from the engine and frozen snapshot; a second run matched the saved artifact byte-for-byte with `cmp` |

## Current limitations

- The app now reports historical portfolio estimates, a momentum ranking, stress scenarios, and a **REVIEW HOLD**, but **no investment recommendation**.
- The provisional 6% floor is slack across all grid allocations in the frozen sample. Minimum historical variance is sensitive to the estimation window; the largest weight movement is 25 points in IAU.
- The original Yahoo downloads were not re-fetched for this milestone; adjusted histories may be revised by the vendor. The frozen CSV and hash support reproducibility of this snapshot, not future-price validity.
- The signal uses the September 2026 observation cutoff, but the snapshot was retrieved October 22. Adjusted histories can be revised; this is not a true September archived point-in-time dataset. It uses no forward returns and does not drive the optimizer.
- Execution costs are illustrative one-time estimates that exclude taxes and may omit market impact or other frictions. The app does not model forward drawdowns or a compound 15-year growth forecast.
- A passing modeled mandate verdict is not an investment suitability determination.

## Material AI contributions and dispositions

| Interaction date | Named tool/model/version | Contribution | Independent verification | Disposition |
| --- | --- | --- | --- | --- |
| 2026-11-15 | OpenAI Codex, GPT-6; product/model version beyond that label not exposed | Initial Streamlit shell, dependency pin, README, requirements tracker, memo outline, and this working log | Governing documents read; syntax, script execution, tab labels, and server health checked above. Financial content remains unverified | PENDING student review: choose ACCEPT, MODIFY, or REJECT and explain why |
| 2026-11-15 | OpenAI Codex, GPT-6; product/model version beyond that label not exposed | Milestone 2 engine, app integration, independent fixtures, output generator, and mandate/data documentation | Compared formulas and allocations with Lab 15; checked local CSV against original Git blob; seven focused tests, AppTest, and local server health passed. These checks verify implementation, not future investment merit | PENDING student review: choose ACCEPT, MODIFY, or REJECT and explain why |
| 2026-11-15 | OpenAI Codex, GPT-6; product/model version beyond that label not exposed | Milestone 3 momentum signal, stress scenarios, process status, UI integration, tests, generated output, and data card | Seven new small-fixture tests plus seven prior tests passed; AppTest checked tabs/warning; prior portfolio allocations matched. Financial interpretation and committee decision remain for student review | PENDING student review: choose ACCEPT, MODIFY, or REJECT and explain why |

For later material AI suggestions, record the task and output or concise trace, an independent source/calculation/invariant/counterexample, the resulting revision or decision, and the student's **ACCEPT / MODIFY / REJECT** reason. Do not treat AI agreement as verification.

## Locked Changed-Input Record

**EMPTY — reserved for the student's personally authored AI-off prediction and the later designated run. No prediction has been written and no changed-input test has been executed.**
