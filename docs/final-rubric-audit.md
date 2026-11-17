# Final Project 2 Rubric Audit — Submission Preparation

**Audit date:** 2026-11-17. This audit maps the six published categories (**300 points total**) to evidence and remaining risks; it does **not** predict a grade. Project 2 uses Markdown, has no Edition A/B or research-evolution artifact, and still requires the student-owned changed-input evidence, three videos/transcripts, and manifest. The approved optimizer's **REVIEW HOLD** remains active. Proposed D ranges and the conditional pilot are awaiting student review and committee authorization.

| Grading category | Evidence already present | Checks actually performed | Material weakness / grading risk | Outstanding student action |
| --- | --- | --- | --- | --- |
| **Problem definition and decision usefulness — 45** | [Mandate](mandate-and-methodology.md), [D analysis](proposed-allocation-analysis.md), [proposed decision memo](decision-memo.md), app Decision view | Lab 15 amendment and five-ETF/benchmark rules compared with code; memo figures checked against engine; D range grid has 26 feasible allocations under each frozen window | Memo is a proposal until student approves suitability, range, and committee ask; REVIEW HOLD blocks implementation | Independently defend why D's diversification benefit warrants higher estimated risk, finalize proposed ranges and committee request |
| **Data integrity and traceability — 45** | Original and extended frozen CSVs, [extended provenance](../data/extended-provenance.md), raw Yahoo archive, [validation record](validation-and-ai-use.md), signal data card | Exact schemas/months and hashes tested; raw extended archive replay and fixed retrieval/observation boundaries documented; local Markdown links checked | Original vendor raw downloads were not re-fetched; adjusted histories can revise; snapshots are not archives from the original observation dates | Review source conventions, confirm no unsupported point-in-time or predictive claim in videos |
| **Financial soundness and judgment — 60** | A/B/C/D, VTI benchmark, three windows, drawdown, costs, C/policy comparisons, proposed guardrails in memo | Full regression and direct monthly-return/variance checks; D's 13.74%/13.27% original estimate and 2.57/1.00/0.29-pp risk costs versus C checked; proposed ranges checked on grid | D is not minimum variance; XLE overlaps broad U.S. equity and has 15% sector tilt; overlapping historical windows do not prove future suitability | Make the suitability judgment and explicitly accept or revise the modeled volatility cost; keep pilot conditional until hold resolution |
| **Technical execution and usability — 45** | Streamlit app, pinned dependencies, dark sidebar dashboard, Explorer, optimization and stress controls, [generated visible output](visible-executed-output.md), README | Python syntax; 38 tests including AppTest navigation, custom weights, resets and scenarios; fresh Python 3.14.7 install; fresh-environment server health `ok`; output regeneration byte-for-byte match | Local health and scripted UI checks do not prove a grader can use every interaction or access a deployment; no deployment is required | Conduct a student cold launch and screen walkthrough; record live application opening in Video 3 |
| **Validation, sensitivity, and reproducibility — 75** | Independent-fixture tests, stress workbench, source hashes, preserved [Test 2 record](locked-changed-input-record-v2.md) and screenshots, validation record | 38 tests pass; 6/16/25% floors, estimate shocks, costs, 59/36 instability, policy sensitivity, D metrics and hashes checked; Test 2 old/new metrics recalculated; Part A commit predates recorded run | **Material AI-off provenance issue:** Test 2's pre-run committed file title says “AI-Assisted Draft.” Chronology and numeric evidence are present, but AI-off authorship cannot be proven from Git and the title conflicts with the requirement. AI-generated tests do not replace student verification | Explain the title and actual authorship to instructor without changing evidence; independently reproduce a critical calculation and record honest AI accept/modify/reject dispositions |
| **Professional communication — 30** | README, memo, methodology, D analysis, validation record, [12-row manifest](submission-manifest.md), [video guide](video-production-guide.md) | Two required opening statements checked in README/memo and drafted for video openings; local Markdown references checked; memo/output number consistency reviewed | Three YouTube recordings and corrected transcripts do not yet exist; video timestamps, access, captions, and Brightspace receipt are pending | Record within time limits with webcam/equivalent; Video 3 starts on working app; correct captions/transcripts; fill manifest with actual links/times; submit matching Markdown |

## Final status checklist

### COMPLETE — repository evidence prepared and tested

- [x] Approved Lab 15 mandate, ETF universe, benchmark, formulas, A/B/C/D comparisons, and official REVIEW HOLD preserved.
- [x] Generated financial output includes D from executable code and matches a second run byte for byte.
- [x] Pinned dependencies installed in a fresh temporary environment; 38 automated tests, syntax, AppTest interactions, and local server health check passed.
- [x] Memo proposal, validation record, video plan, 12-row manifest, and six-category audit drafted; locked Test 2 source, screenshots, and Git history preserved.

### NEEDS STUDENT REVIEW — investment and ownership decisions

- [ ] Review and either accept, modify, or reject the memo's conditional D pilot, ranges (35–45/20–30/10–15/5–10/10–20%), proposed quarterly monitoring, annual rebalance consideration, and committee ask. No committee approval is claimed.
- [ ] Independently verify a material portfolio calculation and document actual dispositions for each material AI contribution in [validation](validation-and-ai-use.md).
- [ ] Resolve the Test 2 pre-run “AI-Assisted Draft” title against the required human-authored AI-off prediction with the instructor; preserve the original record and commit chronology.
- [ ] Perform a cold user launch and review that app, memo, generated output, validation, and intended video narration agree.

### NEEDS RECORDING — student-owned oral evidence

- [ ] Record Video 1 ≤3:00, Video 2 ≤5:00, and Video 3 ≤5:00, with the two required opening statements and webcam/equivalent. Video 3 must begin on the functioning app.
- [ ] Upload as Unlisted/Public YouTube videos, enable captions, correct substantive errors, and create three matching plain-text transcripts in `docs/`.
- [ ] Replace video, duration, transcript-link, and timestamp placeholders in the manifest with **observed** facts; check logged-out access.

### NEEDS SUBMISSION — frozen delivery

- [ ] Confirm instructional-team GitHub access, final link integrity, no secrets, and matching Markdown versions.
- [ ] Submit repository, final `decision-memo.md`, final `validation-and-ai-use.md`, three YouTube links, three corrected transcripts, and completed manifest through Brightspace; retain receipt.
