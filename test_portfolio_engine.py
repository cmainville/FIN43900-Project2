"""Independent fixtures and regression checks for the Project 2 portfolio engine."""

import math
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

import portfolio_engine as engine


class PortfolioEngineTests(unittest.TestCase):
    def test_small_return_and_covariance_fixture(self):
        # Three explicitly specified monthly observations. VTI and VXUS have
        # identical deviations, so their sample covariance equals each variance.
        monthly = pd.DataFrame(
            {
                "VTI": [0.01, 0.03, 0.02],
                "VXUS": [0.02, 0.04, 0.03],
                "XLE": [0.0, 0.0, 0.0],
                "IWM": [0.0, 0.0, 0.0],
                "IAU": [0.0, 0.0, 0.0],
            },
            index=pd.date_range("2026-01-31", periods=3, freq="ME"),
        )
        result = engine.estimate_from_returns(monthly)
        self.assertAlmostEqual(result["returns"][0], 0.24)
        self.assertAlmostEqual(result["returns"][1], 0.36)
        self.assertAlmostEqual(result["covariance"][0, 0], 0.0012)
        self.assertAlmostEqual(result["covariance"][0, 1], 0.0012)
        self.assertAlmostEqual(result["covariance"][1, 1], 0.0012)
        weights = dict(zip(engine.TICKERS, (0.5, 0.5, 0, 0, 0)))
        metrics = engine.portfolio_metrics(weights, result)
        self.assertAlmostEqual(metrics["return"], 0.30)
        self.assertAlmostEqual(metrics["variance"], 0.0012)
        self.assertAlmostEqual(metrics["volatility"], math.sqrt(0.0012))

    def test_weight_and_objective_rules(self):
        self.assertEqual(sum(engine.EQUAL_WEIGHT.values()), 1.0)
        self.assertEqual(sum(engine.LAB15_REFERENCE.values()), 1.0)
        self.assertTrue(all(weight >= 0 for weight in engine.EQUAL_WEIGHT.values()))
        passing = engine.mandate_verdict(engine.EQUAL_WEIGHT, 0.06)
        self.assertTrue(passing["pass"])
        below_floor = engine.mandate_verdict(engine.EQUAL_WEIGHT, 0.059)
        self.assertTrue(below_floor["hard_pass"])
        self.assertFalse(below_floor["objective_pass"])
        self.assertIn("below the provisional 6% floor", below_floor["reasons"][0])
        short = dict(engine.EQUAL_WEIGHT, VTI=-0.05, VXUS=0.45)
        verdict = engine.mandate_verdict(short, 0.10)
        self.assertFalse(verdict["hard_pass"])
        self.assertIn("negative weight", verdict["reasons"][0])
        not_full = dict(engine.EQUAL_WEIGHT, VTI=0.10)
        self.assertIn("weights do not total 100%", engine.mandate_verdict(not_full, 0.10)["reasons"][0])
        unapproved = dict(engine.EQUAL_WEIGHT)
        unapproved["QQQ"] = unapproved.pop("IAU")
        self.assertFalse(engine.mandate_verdict(unapproved, 0.10)["pass"])

    def test_grid_and_infeasibility(self):
        units = list(engine.allocation_units())
        self.assertEqual(len(units), 10626)
        self.assertEqual(len(set(units)), 10626)
        self.assertTrue(all(sum(row) == 20 and min(row) >= 0 for row in units))
        fixture = {
            "returns": np.array([0.05, 0.10, 0.05, 0.05, 0.05]),
            "covariance": np.diag([0.01] * 5),
        }
        solution = engine.optimize(fixture)
        self.assertTrue(solution["feasible"])
        self.assertEqual(solution["candidate_count"], 10626)
        weights = solution["result"]["weights"]
        self.assertAlmostEqual(sum(weights.values()), 1.0)
        self.assertTrue(all(round(weight * 20) == weight * 20 for weight in weights.values()))
        self.assertGreaterEqual(solution["result"]["return"], 0.06)
        # For equal, uncorrelated asset variances, equal weight uniquely minimizes
        # sum(w_i^2) and also meets this fixture's return floor exactly.
        self.assertEqual(tuple(weights.values()), (0.2,) * 5)
        self.assertAlmostEqual(solution["result"]["variance"], 0.002)
        impossible = engine.optimize(
            {"returns": np.array([0.05] * 5), "covariance": np.diag([0.01] * 5)}
        )
        self.assertFalse(impossible["feasible"])
        self.assertIsNone(impossible["result"])
        self.assertEqual(impossible["feasible_count"], 0)

    def test_deterministic_tie(self):
        fixture = {"returns": np.array([0.10] * 5), "covariance": np.zeros((5, 5))}
        solution = engine.optimize(fixture)
        self.assertEqual(tuple(solution["result"]["weights"].values()), (0, 0, 0, 0, 1))

    def test_data_snapshot_and_rejection(self):
        prices = engine.load_prices()
        self.assertEqual(prices.shape, (60, 5))
        self.assertEqual(prices.index[0].date().isoformat(), "2021-10-31")
        self.assertEqual(prices.index[-1].date().isoformat(), "2026-09-30")
        self.assertEqual(engine.estimate(prices)["observations"], 59)
        self.assertEqual(engine.estimate(prices, last_36=True)["observations"], 36)
        source = pd.read_csv(engine.DATA_PATH)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            for bad in (
                source.rename(columns={"IAU": "SPY"}),
                source.iloc[:-1],
                source.iloc[::-1],
                source.assign(Date=source["Date"].shift(1).fillna(source["Date"].iloc[0])),
                source.assign(VTI=source["VTI"].mask(source.index == 0)),
                source.assign(VTI=source["VTI"].mask(source.index == 0, -1)),
            ):
                bad.to_csv(path, index=False)
                with self.assertRaises((ValueError, TypeError)):
                    engine.load_prices(path)

    def test_known_lab15_answers_and_benchmarks(self):
        result = engine.analyze()
        a, b, c = result["portfolios"].values()
        self.assertEqual(tuple(a["weights"].values()), (0.2,) * 5)
        self.assertEqual(tuple(b["weights"].values()), (0.45, 0.25, 0.10, 0.10, 0.10))
        self.assertEqual(tuple(c["weights"].values()), (0.50, 0, 0.10, 0, 0.40))
        self.assertEqual((round(b["return"] * 100, 2), round(b["volatility"] * 100, 2)), (12.67, 13.88))
        self.assertEqual((round(c["return"] * 100, 2), round(c["volatility"] * 100, 2)), (15.66, 12.27))
        self.assertEqual((round(a["return"] * 100, 2), round(a["volatility"] * 100, 2)), (14.02, 13.66))
        recent = result["optimized_recent"]["result"]
        self.assertEqual(tuple(recent["weights"].values()), (0.45, 0.20, 0.20, 0, 0.15))
        self.assertEqual((round(recent["return"] * 100, 2), round(recent["volatility"] * 100, 2)), (20.76, 9.79))
        self.assertTrue(all(portfolio["verdict"]["pass"] for portfolio in (a, b, c)))
        self.assertEqual(engine.largest_weight_change(c["weights"], recent["weights"]), ("IAU", 25.0))
        self.assertTrue(result["stability_triggered"])
        self.assertAlmostEqual(result["vti_benchmark"]["return"], result["full"]["returns"][0])
        self.assertAlmostEqual(
            result["vti_benchmark"]["volatility"],
            math.sqrt(result["full"]["covariance"][0, 0]),
        )

    def test_monitoring_threshold_is_strict(self):
        self.assertFalse(engine.stability_trigger(20.0))
        self.assertTrue(engine.stability_trigger(20.01))
        first = dict(engine.EQUAL_WEIGHT)
        exactly = dict(first, VTI=0.40, VXUS=0.0)
        above = dict(first, VTI=0.45, VXUS=0.0, IAU=0.15)
        self.assertAlmostEqual(engine.largest_weight_change(first, exactly)[1], 20.0)
        self.assertFalse(engine.stability_trigger(engine.largest_weight_change(first, exactly)[1]))
        self.assertTrue(engine.stability_trigger(engine.largest_weight_change(first, above)[1]))


if __name__ == "__main__":
    unittest.main()
