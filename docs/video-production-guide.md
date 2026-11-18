# Project 2 Video Preparation — Recording Plan

**Preparation only.** No recording, transcript, caption correction, YouTube URL, or actual timestamp is claimed. The student should review and adapt the spoken wording, record the three videos with a small webcam view or approved equivalent, and replace the [manifest](submission-manifest.md) placeholders with observed facts. YouTube videos must be **Unlisted or Public, never Private**; corrected plain-text transcripts are created **after** recording.

## Required opening for each video

Speak both statements at the start of each recording. For **Video 3, show the functioning Streamlit app from the first frame while speaking them**; do not begin on a title slide.

> AI use: OpenAI Codex (GPT-6) assisted with the application, calculations, tests, documentation, and presentation preparation. I independently reviewed the material I present; my validation and AI-use record identifies checks and remaining questions.
>
> Ownership and educational purpose: I selected Portfolio D and own the final investment analysis and decision. This project is for education, not investment advice.

The student has confirmed independent review of the eight material AI-use contributions and personal completion of the AI-off locked test; the [validation record](validation-and-ai-use.md) documents those statements and the supporting evidence. Any recording should describe the student's actual work accurately.

## Video 1 — How the system and thinking changed; one AI-output check (maximum 3:00)

| Planned time, not evidence | Scene and points to cover |
| --- | --- |
| 0:00–0:20 | Both opening statements; show repository README or the app |
| 0:20–1:15 | Explain the intentional Lab 13 → Lab 15 mandate amendment, then the shift from minimum-variance C to student-selected D as a *suitability* question; distinguish D from optimizer and unapproved policy bounds |
| 1:15–2:20 | Show one material Codex output **after the student checks it**: for example, D's original 59-return 13.74% estimated return / 13.27% volatility, checked by direct monthly-return arithmetic and the frozen source/test. State whether the student accepts, modifies, or rejects it and why; do not portray an AI-authored test alone as independent student verification |
| 2:20–2:55 | Explain the accepted volatility trade-off, remaining REVIEW HOLD, and why the final pilot remains conditional |

Use Project 2's evolution format; **do not** introduce Edition A/B or a research-evolution artifact. Actual segment timestamps go into the manifest only after the final edit.

## Video 2 — Technical ownership and reproducibility (maximum 5:00)

| Planned time, not evidence | Scene and points to cover |
| --- | --- |
| 0:00–0:20 | Both opening statements; open the submitted repository |
| 0:20–1:15 | Trace frozen `data/` CSVs through `portfolio_engine.py` and `dashboard_analytics.py` to `app.py`; explain retrieval date versus observation cutoff and no live download |
| 1:15–2:30 | Explain monthly simple returns, mean ×12, sample covariance ×12, `wᵀΣw`, the 10,626-point five-percent grid, infeasibility, baselines, D fixed weights, and VTI benchmark |
| 2:30–3:45 | Demonstrate the README test/output commands and one financial fixture or direct check; show the preserved generated output and source hashes. Show the committed changed-input record and screenshots as preserved evidence without rerunning or rewriting the locked test |
| 3:45–4:50 | Show how app navigation, hypothetical overrides, stress tests, and REVIEW HOLD work; state a material limitation: overlapping windows are not out of sample and the adjusted histories may be revised |

Keep the code walkthrough substantive. Verify every spoken command against the final environment and fill actual timestamps in the manifest after recording.

## Video 3 — Investment committee presentation (maximum 5:00)

| Planned time, not evidence | Scene and points to cover |
| --- | --- |
| **0:00** | **The working app is already visible and functioning.** Speak both opening statements over the app |
| 0:20–1:10 | Lead with the proposed **conditional D pilot** and the explicit implementation pause; show D in Portfolio Explorer and official REVIEW HOLD |
| 1:10–2:15 | Defend D 40/25/15/5/15 and proposed ranges 35–45/20–30/10–15/5–10/10–20; note ranges are not approved mandate constraints |
| 2:15–3:15 | Compare original 59-return D 13.74%/13.27% against C 15.66%/12.27%; explain C's 40% gold and 0% VXUS, the extended 50% gold result, and D's accepted higher estimated volatility. Mention historical samples and benchmark context without promising future returns |
| 3:15–4:10 | Cover drawdown, energy/gold concentration, stress/estimation uncertainty, costs, and the 25-point IAU instability that keeps REVIEW HOLD active |
| 4:10–4:55 | State proposed quarterly review and annual rebalance considerations, hard-failure/review-hold conditions, and explicit committee ask: evaluate D and ranges now; authorize a pilot only after independent validation and a documented hold resolution |

## After recording

1. Inspect the first and final frames, exact durations, audio, webcam/equivalent, and each required visual demonstration. Graders stop at **3:00 / 5:00 / 5:00**.
2. Generate or obtain platform captions; correct substantive ticker names, numbers, finance terms, and speaker attribution. Save matching corrected plain-text files as `docs/transcript-video-1.txt`, `docs/transcript-video-2.txt`, and `docs/transcript-video-3.txt`.
3. Confirm logged-out YouTube access, then add stable URLs, actual titles/durations, and **actual** evidence timestamps to the [manifest](submission-manifest.md). Do not invent timestamps from this plan.
4. Compare the final spoken recommendation and ranges with the [memo](decision-memo.md) and active app status. Freeze matching Markdown attachments for Brightspace.
