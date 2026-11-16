"""Independent fixtures for the signal, stresses, costs, and process rule."""

import math
import unittest

import numpy as np
import pandas as pd

import portfolio_engine as engine


class Milestone3Tests(unittest.TestCase):
    def test_momentum_cutoff_ranking_and_no_future_prices(self):
        prices = pd.DataFrame(
            [[100, 100, 100, 100, 100], [110, 120, 90, 105, 100]],
            columns=engine.TICKERS,
            index=pd.to_datetime(["2025-09-30", "2026-09-30"]),
        )
        expected = [("VXUS", 0.20), ("VTI", 0.10), ("IWM", 0.05),
                    ("IAU", 0.0), ("XLE", -0.10)]
        signal = engine.momentum_signal(prices)
        self.assertEqual([(row["ticker"], round(row["momentum"], 2)) for row in signal], expected)
        self.assertEqual([row["rank"] for row in signal], [1, 2, 3, 4, 5])
        future = pd.DataFrame(
            [[1_000_000, 1, 1_000_000, 1, 1_000_000]],
            columns=engine.TICKERS,
            index=pd.to_datetime(["2026-10-31"]),
        )
        self.assertEqual(engine.momentum_signal(pd.concat([prices, future])), signal)
        with self.assertRaisesRegex(ValueError, "September 2025"):
            engine.momentum_signal(prices.drop(pd.Timestamp("2025-09-30")))
        bad = prices.copy()
        bad.loc[pd.Timestamp("2026-09-30"), "VTI"] = 0
        with self.assertRaisesRegex(ValueError, "positive"):
            engine.momentum_signal(bad)

    def test_return_estimate_stress_is_isolated(self):
        base = {"returns": np.array([0.08, 0.10, 0.08, 0.08, 0.08]),
                "covariance": np.diag([0.01] * 5)}
        stressed = engine.stressed_return(base, "IAU", -0.05)
        self.assertAlmostEqual(stressed["returns"][-1], 0.03)
        np.testing.assert_array_equal(base["returns"], [0.08, 0.10, 0.08, 0.08, 0.08])
        np.testing.assert_array_equal(stressed["covariance"], base["covariance"])
        base_metrics = engine.portfolio_metrics(engine.EQUAL_WEIGHT, base)
        stress_metrics = engine.portfolio_metrics(engine.EQUAL_WEIGHT, stressed)
        self.assertAlmostEqual(stress_metrics["return"] - base_metrics["return"], -0.01)
        self.assertAlmostEqual(stress_metrics["volatility"], base_metrics["volatility"])
        self.assertTrue(engine.optimize(stressed)["feasible"])

    def test_volatility_stress_preserves_correlation(self):
        covariance = np.diag([0.04, 0.01, 0.01, 0.01, 0.09])
        covariance[0, 4] = covariance[4, 0] = 0.01
        base = {"returns": np.array([0.1] * 5), "covariance": covariance}
        stressed = engine.stressed_volatility(base, "IAU", 1.25)
        new = stressed["covariance"]
        self.assertAlmostEqual(new[4, 4], 0.09 * 1.25**2)
        self.assertAlmostEqual(new[0, 4], 0.01 * 1.25)
        self.assertAlmostEqual(new[4, 0], 0.01 * 1.25)
        old_correlation = covariance[0, 4] / math.sqrt(covariance[0, 0] * covariance[4, 4])
        new_correlation = new[0, 4] / math.sqrt(new[0, 0] * new[4, 4])
        self.assertAlmostEqual(new_correlation, old_correlation)
        self.assertAlmostEqual(base["covariance"][4, 4], 0.09)

    def test_turnover_and_cost_count_buys_and_sells(self):
        before = dict(zip(engine.TICKERS, (0.5, 0.5, 0, 0, 0)))
        after = dict(zip(engine.TICKERS, (0.25, 0.75, 0, 0, 0)))
        cost = engine.rebalance_costs(before, after, 10)
        self.assertAlmostEqual(cost["one_way_turnover"], 0.25)
        self.assertAlmostEqual(cost["total_traded"], 0.50)
        self.assertAlmostEqual(cost["cost"], 0.0005)
        self.assertAlmostEqual(engine.rebalance_costs(before, after, 0)["cost"], 0)
        with self.assertRaises(ValueError):
            engine.rebalance_costs(before, after, -1)

    def test_constraint_floors_and_infeasibility(self):
        fixture = {"returns": np.array([0.10, 0.05, 0.05, 0.05, 0.05]),
                   "covariance": np.diag([0.01] * 5)}
        feasible = engine.optimize(fixture, floor=0.06)
        impossible = engine.optimize(fixture, floor=0.16)
        self.assertTrue(feasible["feasible"])
        self.assertGreater(feasible["feasible_count"], 0)
        self.assertFalse(impossible["feasible"])
        self.assertEqual(impossible["feasible_count"], 0)
        self.assertIsNone(impossible["result"])
        self.assertEqual(engine.RETURN_FLOOR, 0.06)

    def test_stop_rule_precedence(self):
        feasible = {"feasible": True}
        impossible = {"feasible": False}
        self.assertEqual(engine.process_status(False, feasible, feasible, True)["status"], "HARD FAILURE")
        self.assertEqual(engine.process_status(True, impossible, feasible, False)["status"], "HARD FAILURE")
        self.assertEqual(engine.process_status(True, feasible, feasible, True)["status"], "REVIEW HOLD")
        self.assertEqual(engine.process_status(True, feasible, feasible, False)["status"], "NO AUTOMATIC HOLD")

    def test_prior_results_and_current_hold_preserved(self):
        result = engine.analyze()
        self.assertEqual(tuple(result["optimized_full"]["result"]["weights"].values()),
                         (0.50, 0, 0.10, 0, 0.40))
        self.assertEqual(tuple(result["optimized_recent"]["result"]["weights"].values()),
                         (0.45, 0.20, 0.20, 0, 0.15))
        self.assertEqual(result["largest_change"], ("IAU", 25.0))
        self.assertEqual(result["process"]["status"], "REVIEW HOLD")
        self.assertEqual(result["estimation_scenarios"][0]["change"][1], 0)
        self.assertGreater(result["estimation_scenarios"][1]["change"][1], 0)
        self.assertEqual([row["solution"]["feasible"] for row in result["constraint_scenarios"]],
                         [True, True, False])


if __name__ == "__main__":
    unittest.main()
