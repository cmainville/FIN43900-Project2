"""Reproducible, hypothetical fixed-weight downside checks for Portfolio D.

These scenarios do not change the approved optimizer, mandate, or frozen inputs.
"""

from __future__ import annotations

import hashlib

import numpy as np

from portfolio_engine import (
    DATA_PATH, SNAPSHOT_RETRIEVED, STUDENT_PROPOSED,
    analyze, assess,
)


SCENARIOS = (
    ("Equity return −10 pp", "All four equity ETF annual arithmetic return estimates −10 percentage points; covariance fixed."),
    ("Gold correlation +0.20", "IAU correlation with each equity ETF +0.20; standalone volatilities and annual returns fixed."),
    ("Equity volatility ×1.25", "Each equity ETF annualized volatility ×1.25; correlations and annual returns fixed."),
)


def stressed_estimates(estimates: dict, scenario: str) -> dict:
    """Change one assumption family and reject an invalid risk matrix."""
    returns = np.array(estimates["returns"], dtype=float, copy=True)
    covariance = np.array(estimates["covariance"], dtype=float, copy=True)
    if returns.shape != (5,) or covariance.shape != (5, 5):
        raise ValueError("Expected five approved ETF estimates.")
    if not np.isfinite(returns).all() or not np.isfinite(covariance).all():
        raise ValueError("Estimates must be finite.")
    if not np.allclose(covariance, covariance.T, atol=1e-12):
        raise ValueError("Covariance must be symmetric.")
    volatilities = np.sqrt(np.diag(covariance))
    if not np.isfinite(volatilities).all() or (volatilities <= 0).any():
        raise ValueError("Standalone volatilities must be positive.")
    if scenario == SCENARIOS[0][0]:
        returns[:4] -= 0.10
    elif scenario == SCENARIOS[1][0]:
        correlation = covariance / np.outer(volatilities, volatilities)
        correlation[:4, 4] += 0.20
        correlation[4, :4] += 0.20
        if np.max(np.abs(correlation)) > 1 + 1e-12:
            raise ValueError("Gold correlation shock exceeds valid correlation bounds.")
        covariance = correlation * np.outer(volatilities, volatilities)
    elif scenario == SCENARIOS[2][0]:
        scale = np.array([1.25, 1.25, 1.25, 1.25, 1.0])
        covariance *= np.outer(scale, scale)
    else:
        raise ValueError("Unknown Portfolio D scenario.")
    if np.linalg.eigvalsh(covariance).min() < -1e-10:
        raise ValueError("Stressed covariance is not positive semidefinite.")
    return {**estimates, "returns": returns, "covariance": covariance}


def sensitivity_rows(estimates: dict) -> list[dict]:
    """Evaluate the same fixed student weights before and after each shock."""
    baseline = assess(STUDENT_PROPOSED, estimates)
    rows = []
    for name, assumption in SCENARIOS:
        stressed = assess(STUDENT_PROPOSED, stressed_estimates(estimates, name))
        rows.append({
            "name": name,
            "assumption": assumption,
            "baseline": baseline,
            "stressed": stressed,
            "return_change_pp": (stressed["return"] - baseline["return"]) * 100,
            "volatility_change_pp": (stressed["volatility"] - baseline["volatility"]) * 100,
        })
    return rows


def report_markdown() -> str:
    """Generate a frozen, inspectable result from the approved original snapshot."""
    base = analyze()
    rows = sensitivity_rows(base["full"])
    lines = [
        "# Portfolio D — Supplementary Downside Sensitivity Output",
        "",
        f"Input: `data/prices_growth.csv`; SHA-256 `{hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()}`.",
        f"Observation cutoff: **2026-09-30**; snapshot retrieval/availability: **{SNAPSHOT_RETRIEVED}**; original **59 monthly returns**.",
        "Weights held fixed: **VTI 40% / VXUS 25% / XLE 15% / IWM 5% / IAU 15%**. Each shock is separate and hypothetical; Portfolio D is not reoptimized.",
        "Annual arithmetic return = mean monthly simple return ×12; annual sample covariance = monthly sample covariance ×12; volatility = √(wᵀΣw).",
        "",
        "| Scenario | Exact hypothetical input | Base return | Stressed return | Change | Base volatility | Stressed volatility | Change | Modeled mandate |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        before, after = row["baseline"], row["stressed"]
        verdict = "PASS" if after["verdict"]["pass"] else "FAIL: " + "; ".join(after["verdict"]["reasons"])
        lines.append(
            f"| {row['name']} | {row['assumption']} | {before['return']:.2%} | "
            f"{after['return']:.2%} | {row['return_change_pp']:+.2f} pp | "
            f"{before['volatility']:.2%} | {after['volatility']:.2%} | "
            f"{row['volatility_change_pp']:+.2f} pp | {verdict} |"
        )
    lines += [
        "",
        "The return shock tests equity-estimate dependence; its covariance is unchanged. The gold shock tests reduced diversification: correlations rise together, standalone risk stays fixed, and the resulting covariance is checked for positive semidefiniteness. The volatility shock tests a broad equity-risk increase: covariance is rebuilt by scaling both axes, so historical correlations are preserved.",
        f"The approved original 59-versus-36 process status remains **{base['process']['status']}**. A hypothetical failure does not itself change the approved base-case mandate verdict; a comparable validated input change would require review before implementation. No scenario is a forecast, independent backtest, or part of the student-owned Locked Changed-Input Record.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(report_markdown(), end="")
