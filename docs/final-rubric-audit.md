# Final Project 2 Rubric Audit — Submission Preparation

**Audit date:** 2026-11-19. This audit maps the six published categories (**300 points total; 270 across the five non-communication categories**) to evidence and remaining risks; it does **not** predict a grade. Project 2 uses Markdown and has no Edition A/B or research-evolution artifact. Three videos are uploaded, their corrected transcripts and the 12-row manifest are present, and YouTube captions require final student verification. The student approved the conditional D pilot proposal, ranges, monitoring framework, revised REVIEW HOLD procedure, and supplementary D downside analysis; the approved optimizer's **REVIEW HOLD** remains active and no committee authorization exists.

| Grading category | Evidence already present | Checks actually performed | Material weakness / grading risk | Outstanding student action |
| --- | --- | --- | --- | --- |
| **Problem definition and decision usefulness — 45** | [Mandate](mandate-and-methodology.md), [D analysis](proposed-allocation-analysis.md), [student-approved decision proposal](decision-memo.md), app Decision view | Lab 15 amendment and five-ETF/benchmark rules compared with code; memo figures checked against engine; D range grid has 26 feasible allocations under each frozen window; memo separates hard failure, monitoring hold, suitability, and authorization | REVIEW HOLD blocks implementation; a committee has not authorized the proposal | Obtain any committee authorization separately |
| **Data integrity and traceability — 45** | Original and extended frozen CSVs, [extended provenance](../data/extended-provenance.md), raw Yahoo archive, [validation record](validation-and-ai-use.md), signal data card | Current audit rechecked five exact ETFs, 60/120 ordered month ends, positive finite prices, 59/36/119 returns, three hashes, raw ZIP entries, and 151/300 exact overlap matches; test suite replays raw archive | Original vendor raw downloads were not re-fetched; adjusted histories can revise; snapshots are not archives from original observation dates | Confirm the distinction between observation and retrieval dates in the final presentation |
| **Financial soundness and judgment — 60** | A/B/C/D, VTI benchmark, three windows, drawdown, costs, C/policy comparisons, proposed guardrails, [D downside output](portfolio-d-sensitivity-output.md) | Direct standard-library monthly return/sample covariance checks reproduce D on 59/36/119 returns; five new fixture tests check fixed-D shocks. A 10-point equity return cut gives 5.24% and modeled FAIL; +0.20 gold-equity correlations give 13.85% risk; 1.25× equity volatility gives 16.31% risk | D is not minimum variance; XLE overlap and equity concentration remain. Shocks are hypothetical and not forecasts | Keep implementation paused pending formal hold resolution and committee authorization |
| **Technical execution and usability — 45** | Streamlit app, pinned dependencies, sidebar dashboard, Explorer, optimization and stress controls, [original output](visible-executed-output.md), [D output](portfolio-d-sensitivity-output.md), README | New Python 3.14 environment installed pinned dependencies; 43 tests including AppTest passed; syntax, server health `ok`, and two byte-for-byte output comparisons passed. A separate local `/tmp` copy passed all 43 tests. Codex also interacted with the live Chrome UI: Overview, Explorer, Optimization, Stress, and Decision rendered; D weights/metrics, comparison, invalid 105% warning, resets, 25% infeasibility, and REVIEW HOLD were observed | One concurrent run in the cloud-synced working folder hit a transient empty CSV read; sequential rerun and local copy passed. The student has not completed their personal cold-run checklist | Perform the [manual cold-run checklist](manual-cold-run-checklist.md) from a fresh local checkout and record first failure/resolution if any |
| **Validation, sensitivity, and reproducibility — 75** | Independent-fixture tests, stress workbench, hashes, complete [Test 2 record](validation-and-ai-use.md#locked-changed-input-record--test-2) with unchanged [source](locked-changed-input-record-v2.md), [D scenario generator](../portfolio_d_sensitivity.py) and output | 43 tests pass; existing shocks, costs, instability, policy, D, and hashes remain checked; new fixtures verify correlation-matrix validity and covariance scaling; both output artifacts replay byte-for-byte. Student confirms personal AI-off Test 2, reports independent Excel verification of base D, and has ACCEPTED nine earlier material AI contributions | AI-assisted tests are not independent student verification; historical snapshots are not independent out-of-sample evidence; final transcript/manifest AI-use entry awaits student disposition | Review the final packaging AI-use entry while retaining Excel and locked evidence |
| **Professional communication — 30** | README, committee memo, methodology, D analysis, validation record, [12-row manifest](submission-manifest.md), and three [plain-text transcripts](transcript-video-1.txt) | Memo states four concrete decision gates; three Unlisted YouTube pages played logged out, titles/durations met limits, transcript-panel times support the manifest, and Video 3's app was visible at 0:01 | YouTube player reported CC unavailable on all three; exact Video 3 0:00 frame, caption corrections, instructional-team access, and Brightspace receipt remain unconfirmed | Complete caption and final playback checks, then submit the matching Markdown and transcript files |

## Final status checklist

### COMPLETE — repository evidence prepared and tested

- [x] Approved Lab 15 mandate, ETF universe, benchmark, formulas, A/B/C/D comparisons, and official REVIEW HOLD preserved.
- [x] Generated financial output includes D from executable code and matches a second run byte for byte.
- [x] Pinned dependencies installed in a fresh temporary environment; 43 automated tests, syntax, AppTest interactions, and local server health check passed.
- [x] Student-approved conditional-pilot proposal, ranges, and monitoring framework documented; committee approval is still required.
- [x] Student-reported independent Excel verification of D's original figures and nine ACCEPT dispositions recorded; Codex workbook inspection is separately described.
- [x] Complete Test 2 Part A/B integrated in validation; source, screenshots, and Git history preserved; 12-row manifest and six-category audit prepared.
- [x] Fixed-D downside scenarios are reproducible from frozen data and show the provisional return floor can fail under a broad equity-estimate shock. The official REVIEW HOLD remains unchanged.

### NEEDS STUDENT REVIEW — investment and ownership decisions

- [ ] Perform a cold user launch and review that app, memo, generated output, and validation agree.
- [ ] Review the final transcript/manifest AI-use entry and record ACCEPT, MODIFY, or REJECT with a reason; the nine earlier ACCEPT decisions remain unchanged.

### RECORDED — final caption and playback checks

- [x] Three videos uploaded as Unlisted; logged-out playback, titles, and durations checked: 2:58, 4:57, and 4:37. Opening disclosures appear in the time-coded transcript panels; Video 3's app is visible at 0:01.
- [x] Three corrected plain-text transcripts placed in `docs/`; manifest now has the stable video and GitHub links and observed timestamp indices.
- [ ] Confirm the exact 0:00 Video 3 frame, webcam/equivalent and audio across all recordings, and timestamp/caption accuracy. YouTube's player currently reports captions unavailable for all three.

### NEEDS SUBMISSION — frozen delivery

- [ ] Confirm instructional-team GitHub access, final link integrity, no secrets, and matching Markdown versions.
- [ ] Submit repository, final `decision-memo.md`, final `validation-and-ai-use.md`, three YouTube links, three corrected transcripts, and completed manifest through Brightspace; retain receipt.
