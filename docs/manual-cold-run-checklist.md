# Student Manual Cold-Run Checklist — Pending

This is for the student's own fresh launch and visual interaction review. **No box below is marked complete by Codex.** Use a fresh local checkout, Python 3.14 environment, and the [README instructions](../README.md); record any failure and its resolution before submission. A concurrent audit once had a transient CSV read error from the cloud-synced working folder; the same suite passed sequentially and from a local `/tmp` copy.

In a new local directory, run:

```bash
git clone https://github.com/cmainville/FIN43900-Project2.git FIN43900-Project2-cold-run
cd FIN43900-Project2-cold-run
git rev-parse HEAD
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

- [ ] From the fresh checkout above, confirm the app opens without credentials or live price downloads.
- [ ] On **Overview**, confirm the title, original data retrieval date **2026-10-22**, default Portfolio **C**, its **50/0/10/0/40%** weights, and **REVIEW HOLD**. Confirm the sidebar offers Overview, Analytics, and Decision.
- [ ] Under **Analytics → Portfolio Explorer**, select **D — Student-Proposed Diversified Portfolio**. Confirm **40/25/15/5/15%**, estimated **13.74%** annual arithmetic return, **13.27%** annualized volatility, modeled PASS, and continuing REVIEW HOLD. Compare D with C; confirm C remains the original optimizer result.
- [ ] Select **Custom Portfolio** and change only VTI from its 20% default to 40%. Confirm an explicit **120% total** error and no silent normalization. Set IAU to 0% so the five weights total 100%; confirm metrics appear. Click **Reset to Defaults** and confirm C returns.
- [ ] Under **Optimization**, confirm default original **59 returns**, **6%** floor, and hypothetical bounds disabled. Enable the **NOT APPROVED** bounds; confirm the original-window illustrative policy displays **40/25/15/0/20%**. Change a return or volatility input, confirm the scenario updates, then click **Reset to Approved Defaults** and confirm the original controls and C allocation return.
- [ ] Under **Risk & Stress Tests**, choose **Return-floor sensitivity**, enter **25%**, and confirm **INFEASIBLE** while the official process still says REVIEW HOLD. Click **Reset scenario** and confirm the predefined expected-return shock returns.
- [ ] Under **Historical Analysis**, confirm 119, 59, and 36 return windows are separately labeled, the original 59-versus-36 IAU movement is **25 percentage points**, and the illustrative policy remains **NOT APPROVED**.
- [ ] On **Decision**, confirm D is a student-approved **conditional proposal**, the original REVIEW HOLD is visible, and no committee authorization or trade is claimed. Read the [memo's decision gates](decision-memo.md#downside-risk-and-implementation-decision) and confirm the app and memo agree.
- [ ] After reviewing the app, stop Streamlit with Ctrl+C. In the same activated environment, run `python -m portfolio_engine | cmp - docs/visible-executed-output.md` and `python -m portfolio_d_sensitivity | cmp - docs/portfolio-d-sensitivity-output.md`. Both commands should exit with code **0** and no output. Confirm the D downside table shows **5.24%** return under the equity-return shock and **16.31%** volatility under the equity-volatility shock.

Automated AppTest coverage is separate from this manual check. Complete the record below only after performing the steps yourself.

## Student cold-run evidence — leave blank until performed

| Field | Student entry |
| --- | --- |
| Actual date and time |  |
| Checkout commit (`git rev-parse HEAD`) |  |
| Python version (`python3 --version`) |  |
| Install and launch commands used |  |
| Overview, Explorer, Optimization, Stress, Historical, and Decision observations |  |
| Output-reproduction commands and exit codes |  |
| First failure or unexpected result, if any |  |
| Resolution and repeat check, if any |  |
| Overall student conclusion |  |
