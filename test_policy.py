"""Independent fixture and frozen-result checks for the unapproved policy scenario."""

import hashlib
import itertools
import math
import statistics
import unittest

import numpy as np

import portfolio_engine as engine


class PolicySensitivityTests(unittest.TestCase):
    def test_bounds_against_independent_grid_enumeration(self):
        means = (0.10, 0.09, 0.06, 0.05, 0.08)
        variances = (0.04, 0.025, 0.08, 0.07, 0.015)
        fixture = {"returns": np.array(means), "covariance": np.diag(variances)}
        observed = engine.optimize(
            fixture, minimum_weights={"VXUS": 0.15}, maximum_weights={"IAU": 0.20}
        )
        manually_feasible = []
        for units in itertools.product(range(21), repeat=4):
            last = 20 - sum(units)
            if last < 0 or last > 20 or units[1] < 3 or last > 4:
                continue
            weights = tuple(value / 20 for value in (*units, last))
            annual_return = sum(weight * mean for weight, mean in zip(weights, means))
            if annual_return < 0.06:
                continue
            variance = sum(weight * weight * risk for weight, risk in zip(weights, variances))
            manually_feasible.append((variance, weights, annual_return))
        minimum = min(manually_feasible, key=lambda row: row[0])
        selected = observed["result"]
        self.assertTrue(observed["feasible"])
        self.assertEqual(observed["candidate_count"], 10626)
        self.assertEqual(observed["feasible_count"], len(manually_feasible))
        self.assertEqual(tuple(selected["weights"].values()), minimum[1])
        self.assertAlmostEqual(selected["return"], minimum[2])
        self.assertAlmostEqual(selected["volatility"], math.sqrt(minimum[0]))
        self.assertAlmostEqual(sum(selected["weights"].values()), 1)
        self.assertTrue(all(value >= 0 and value * 20 == round(value * 20)
                            for value in selected["weights"].values()))

    def test_infeasibility_and_invalid_policy_bounds(self):
        fixture = {"returns": np.array([0.08] * 5), "covariance": np.eye(5) * 0.01}
        impossible = engine.optimize(
            fixture, floor=0.09, minimum_weights={"VXUS": 0.15},
            maximum_weights={"IAU": 0.20}
        )
        self.assertFalse(impossible["feasible"])
        self.assertEqual(impossible["feasible_count"], 0)
        self.assertIsNone(impossible["result"])
        for bounds in (
            {"minimum_weights": {"QQQ": 0.15}},
            {"maximum_weights": {"IAU": 0.23}},
            {"minimum_weights": {"IAU": 0.25}, "maximum_weights": {"IAU": 0.20}},
        ):
            with self.assertRaises(ValueError):
                engine.optimize(fixture, **bounds)

    def test_frozen_windows_and_policy_are_separate(self):
        original = engine.analyze()
        extended = engine.analyze_extended(original)
        policy = engine.analyze_policy(extended)
        self.assertEqual(
            [tuple(row["original"]["result"]["weights"].values()) for row in policy["rows"]],
            [(0.5, 0, 0, 0, 0.5), (0.5, 0, 0.1, 0, 0.4),
             (0.45, 0.2, 0.2, 0, 0.15)],
        )
        self.assertEqual(
            [tuple(row["alternative"]["result"]["weights"].values()) for row in policy["rows"]],
            [(0.4, 0.4, 0, 0, 0.2), (0.4, 0.25, 0.15, 0, 0.2),
             (0.45, 0.2, 0.2, 0, 0.15)],
        )
        self.assertTrue(all(row["alternative"]["feasible"] and
                            row["alternative"]["feasible_count"] == 4165
                            for row in policy["rows"]))
        self.assertEqual(policy["original_monitoring_change"], ("IAU", 25.0))
        self.assertEqual(policy["illustrative_monitoring_change"][0], "XLE")
        self.assertAlmostEqual(policy["illustrative_monitoring_change"][1], 5.0)
        self.assertFalse(policy["illustrative_monitoring_breach"])
        self.assertEqual(original["process"]["status"], "REVIEW HOLD")
        self.assertEqual(tuple(original["portfolios"]),
                         ("A — Equal Weight", "B — Lab 15 Reference",
                          "C — Constrained Minimum Volatility"))
        for row in policy["rows"]:
            self.assertGreaterEqual(row["alternative"]["result"]["weights"]["VXUS"], 0.15)
            self.assertLessEqual(row["alternative"]["result"]["weights"]["IAU"], 0.20)
            self.assertGreaterEqual(row["volatility_cost"], -1e-12)

    def test_direct_policy_return_and_risk_from_frozen_prices(self):
        for prices, number, weights in (
            (engine.load_extended_prices(), 119, (0.4, 0.4, 0, 0, 0.2)),
            (engine.load_prices(), 59, (0.4, 0.25, 0.15, 0, 0.2)),
            (engine.load_prices(), 36, (0.45, 0.2, 0.2, 0, 0.15)),
        ):
            columns = [prices[ticker].tolist() for ticker in engine.TICKERS]
            monthly = [[column[index] / column[index - 1] - 1
                        for index in range(1, len(column))][-number:] for column in columns]
            portfolio_monthly = [sum(weight * monthly[asset][month]
                                     for asset, weight in enumerate(weights))
                                 for month in range(number)]
            annual_return = statistics.fmean(portfolio_monthly) * 12
            annual_risk = math.sqrt(statistics.variance(portfolio_monthly) * 12)
            estimates = (engine.estimate_extended(prices) if number == 119
                         else engine.estimate(prices, last_36=number == 36))
            result = engine.portfolio_metrics(dict(zip(engine.TICKERS, weights)), estimates)
            self.assertAlmostEqual(result["return"], annual_return)
            self.assertAlmostEqual(result["volatility"], annual_risk)

    def test_frozen_data_hashes(self):
        self.assertEqual(hashlib.sha256(engine.DATA_PATH.read_bytes()).hexdigest(),
                         "9b8d269bddae60e67548ae9f68f71429a4eab001b67cb7efb03e14082cd2609d")
        self.assertEqual(hashlib.sha256(engine.EXTENDED_DATA_PATH.read_bytes()).hexdigest(),
                         "d011f64fddc6c3d68ce6301a655375563875fc7272b3e28f76f37d9092b93c34")
        self.assertEqual(hashlib.sha256(engine.EXTENDED_RAW_PATH.read_bytes()).hexdigest(),
                         "de32e16737f9d003af9b13dc18bb8032e36eb9833c73c0d7efcad8aeea9d296f")

    def test_app_policy_table_matches_engine(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file("app.py").run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.radio[0].value, "Overview")
        app.radio[0].set_value("Analytics").run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual([tab.label for tab in app.tabs],
                         ["Portfolio Explorer", "Optimization",
                          "Risk & Stress Tests", "Historical Analysis"])
        tables = [table.value for table in app.table if "Case" in table.value.columns]
        self.assertEqual(len(tables), 1)
        table = tables[0]
        self.assertEqual(len(table), 6)
        policy = engine.analyze_policy(engine.analyze_extended(engine.analyze()))
        for index, row in enumerate(policy["rows"]):
            selected = row["alternative"]["result"]
            rendered = table.iloc[index * 2 + 1]
            self.assertEqual(rendered["Case"], "Illustrative policy")
            self.assertEqual(
                rendered["Weights (VTI/VXUS/XLE/IWM/IAU)"],
                " / ".join(f"{selected['weights'][ticker]:.0%}" for ticker in engine.TICKERS),
            )
            self.assertEqual(rendered["Est. return"], f"{selected['return']:.2%}")
            self.assertEqual(rendered["Est. volatility"], f"{selected['volatility']:.2%}")
            self.assertEqual(rendered["Feasible candidates"],
                             f"{row['alternative']['feasible_count']:,}/10,626")


if __name__ == "__main__":
    unittest.main()
