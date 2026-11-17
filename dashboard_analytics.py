"""Presentation-only analytics for interactive Project 2 exploration."""

from functools import lru_cache
import math

import numpy as np
import pandas as pd

from portfolio_engine import GRID_UNITS, TICKERS, allocation_units


@lru_cache(maxsize=1)
def grid_weights() -> np.ndarray:
    """The approved five-point candidate grid, cached independently of UI inputs."""
    weights = np.asarray(list(allocation_units()), dtype=float) / GRID_UNITS
    weights.setflags(write=False)
    return weights


def validate_custom_weights(weights: dict[str, float]) -> tuple[bool, str]:
    if set(weights) != set(TICKERS):
        return False, "Use exactly the five approved ETFs."
    values = np.array([weights[ticker] for ticker in TICKERS], dtype=float)
    if not np.isfinite(values).all() or (values < 0).any() or (values > 1).any():
        return False, "Weights must be finite percentages between 0% and 100%; no shorts or leverage."
    if not math.isclose(float(values.sum()), 1.0, abs_tol=1e-10):
        return False, f"Weights total {values.sum():.1%}; enter exactly 100%. No automatic normalization."
    return True, "Valid fully invested, long-only allocation."


def override_estimates(estimates: dict, annual_returns: tuple[float, ...],
                       annual_volatilities: tuple[float, ...]) -> dict:
    """Apply hypothetical decimal inputs; retain historical correlations."""
    returns = np.asarray(annual_returns, dtype=float)
    target_vol = np.asarray(annual_volatilities, dtype=float)
    if (returns.shape != (5,) or target_vol.shape != (5,)
            or not np.isfinite(returns).all() or not np.isfinite(target_vol).all()
            or (target_vol <= 0).any()):
        raise ValueError("Override returns must be finite and volatilities finite and positive.")
    original = np.asarray(estimates["covariance"], dtype=float)
    original_vol = np.sqrt(np.diag(original))
    if (original_vol <= 0).any() or not np.isfinite(original_vol).all():
        raise ValueError("Historical covariance needs positive finite diagonal values.")
    scale = target_vol / original_vol
    covariance = original * np.outer(scale, scale)
    if (not np.isfinite(covariance).all()
            or not np.allclose(covariance, covariance.T, atol=1e-12)
            or np.linalg.eigvalsh(covariance).min() < -1e-10):
        raise ValueError("Override covariance is not mathematically valid.")
    return {**estimates, "returns": returns, "covariance": covariance}


def candidate_cloud(estimates: dict, floor: float = 0.06,
                    minimum_weights: dict[str, float] | None = None,
                    maximum_weights: dict[str, float] | None = None) -> pd.DataFrame:
    """Vectorized metrics for the same finite grid used by the approved optimizer."""
    weights = grid_weights()
    mean = weights @ estimates["returns"]
    variance = np.einsum("ij,jk,ik->i", weights, estimates["covariance"], weights)
    if not np.isfinite(mean).all() or not np.isfinite(variance).all() or (variance < -1e-10).any():
        raise ValueError("Candidate estimates are invalid.")
    feasible = mean >= floor - 1e-12
    for ticker, lower in (minimum_weights or {}).items():
        feasible &= weights[:, TICKERS.index(ticker)] >= lower - 1e-12
    for ticker, upper in (maximum_weights or {}).items():
        feasible &= weights[:, TICKERS.index(ticker)] <= upper + 1e-12
    frame = pd.DataFrame({
        "Volatility": np.sqrt(np.maximum(variance, 0)) * 100,
        "Return": mean * 100,
        "Feasible": feasible,
        "Weights": [" / ".join(f"{weight:.0%}" for weight in row) for row in weights],
    })
    return frame


def nondominated_frontier(cloud: pd.DataFrame) -> pd.DataFrame:
    """Keep finite-grid points with no other feasible point of <= risk and >= return."""
    feasible = cloud.loc[cloud["Feasible"]].sort_values(
        ["Volatility", "Return"], ascending=[True, False], kind="stable"
    )
    running_best = -math.inf
    keep = []
    for index, row in feasible.iterrows():
        if float(row["Return"]) > running_best + 1e-10:
            keep.append(index)
            running_best = float(row["Return"])
    return feasible.loc[keep].copy()


def monthly_wealth(prices: pd.DataFrame, weights: dict[str, float],
                   start_value: float = 100.0) -> pd.Series:
    """In-sample hindsight reconstruction with constant weights reset each month."""
    valid, reason = validate_custom_weights(weights)
    if not valid:
        raise ValueError(reason)
    if tuple(prices.columns) != TICKERS or len(prices) < 2 or start_value <= 0:
        raise ValueError("Need aligned approved prices and a positive starting value.")
    monthly = prices.pct_change(fill_method=None).iloc[1:]
    returns = monthly.to_numpy(dtype=float) @ np.array([weights[ticker] for ticker in TICKERS])
    if not np.isfinite(returns).all() or (returns <= -1).any():
        raise ValueError("Historical portfolio returns are invalid.")
    values = np.r_[start_value, start_value * np.cumprod(1 + returns)]
    return pd.Series(values, index=prices.index, name="Hypothetical wealth")


def maximum_drawdown(wealth: pd.Series) -> float:
    if wealth.empty or not np.isfinite(wealth.to_numpy()).all() or (wealth <= 0).any():
        raise ValueError("Wealth must contain positive finite observations.")
    return float((wealth / wealth.cummax() - 1).min())


def concentration(weights: dict[str, float]) -> tuple[str, float]:
    return max(((ticker, weights[ticker]) for ticker in TICKERS), key=lambda row: row[1])


