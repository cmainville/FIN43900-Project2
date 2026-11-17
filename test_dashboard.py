"""Focused numerical and interaction checks for the Streamlit dashboard."""

import math
import unittest

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

import dashboard_analytics as dashboard
import portfolio_engine as engine


def by_label(elements, label):
    return next(item for item in elements if item.label == label)


class DashboardMathTests(unittest.TestCase):
    def test_custom_weights_are_never_normalized(self):
        valid = dict(zip(engine.TICKERS, (0.4, 0.2, 0.2, 0.1, 0.1)))
        self.assertTrue(dashboard.validate_custom_weights(valid)[0])
        invalid = {**valid, "VTI": 0.5}
        accepted, reason = dashboard.validate_custom_weights(invalid)
        self.assertFalse(accepted)
        self.assertIn("110.0%", reason)
        self.assertFalse(dashboard.validate_custom_weights({**valid, "IAU": -0.1})[0])

    def test_return_and_volatility_overrides_preserve_correlation(self):
        covariance = np.eye(5) * 0.04
        covariance[0, 1] = covariance[1, 0] = 0.02
        fixture = {"returns": np.array([0.10, 0.08, 0.06, 0.05, 0.07]),
                   "covariance": covariance}
        changed = dashboard.override_estimates(
            fixture, (0.12, 0.08, 0.06, 0.05, 0.07),
            (0.30, 0.20, 0.20, 0.20, 0.20))
        self.assertAlmostEqual(changed["returns"][0], 0.12)
        self.assertAlmostEqual(changed["covariance"][0, 0], 0.09)
        self.assertAlmostEqual(changed["covariance"][0, 1], 0.03)
        self.assertAlmostEqual(changed["covariance"][1, 1], 0.04)
        self.assertTrue(np.array_equal(fixture["covariance"], covariance))
        with self.assertRaises(ValueError):
            dashboard.override_estimates(fixture, (0.1,) * 5, (0.2, 0.2, 0, 0.2, 0.2))

    def test_frontier_is_nondominated_finite_grid_boundary(self):
        fixture = {"returns": np.array([0.10, 0.08, 0.06, 0.05, 0.07]),
                   "covariance": np.diag([0.04, 0.03, 0.02, 0.05, 0.01])}
        cloud = dashboard.candidate_cloud(fixture)
        self.assertEqual(len(cloud), 10626)
        frontier = dashboard.nondominated_frontier(cloud)
        self.assertGreater(len(frontier), 1)
        self.assertTrue(frontier["Volatility"].is_monotonic_increasing)
        self.assertTrue(frontier["Return"].is_monotonic_increasing)
        self.assertAlmostEqual(frontier.iloc[0]["Volatility"],
                               engine.optimize(fixture)["result"]["volatility"] * 100)
        small = pd.DataFrame({"Volatility": [10, 10, 11, 12],
                              "Return": [6, 7, 6, 8], "Feasible": [True] * 4})
        self.assertEqual(dashboard.nondominated_frontier(small)["Return"].tolist(), [7, 8])

    def test_monthly_rebalanced_growth_and_drawdown(self):
        dates = pd.date_range("2025-01-31", periods=3, freq="ME")
        prices = pd.DataFrame({ticker: [100, 100, 100] for ticker in engine.TICKERS},
                              index=dates)
        prices["VTI"] = [100, 110, 99]
        weights = dict(zip(engine.TICKERS, (0.5, 0, 0, 0, 0.5)))
        wealth = dashboard.monthly_wealth(prices, weights)
        self.assertEqual(wealth.tolist(), [100, 105, 99.75])
        self.assertAlmostEqual(dashboard.maximum_drawdown(wealth), -0.05)
        with self.assertRaises(ValueError):
            dashboard.monthly_wealth(prices, {**weights, "IAU": 0.4})


class DashboardInteractionTests(unittest.TestCase):
    def app(self):
        app = AppTest.from_file("app.py").run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        return app

    def test_default_navigation_and_approved_status(self):
        app = self.app()
        self.assertEqual(app.radio[0].value, "Overview")
        self.assertEqual(len(app.tabs), 0)
        values = " ".join(str(item.value) for item in app.markdown)
        self.assertIn("REVIEW HOLD", values)
        self.assertTrue(any("Portfolio in focus: C — Original Minimum-Volatility Portfolio"
                            in str(item.value) for item in app.get("caption")))
        app.radio[0].set_value("Decision").run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        self.assertIn("REVIEW HOLD", " ".join(str(item.value) for item in app.markdown))

    def test_custom_allocation_and_reset(self):
        app = self.app()
        app.radio[0].set_value("Analytics").run(timeout=30)
        by_label(app.selectbox, "Portfolio").set_value("Custom Portfolio").run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        by_label(app.number_input, "VTI weight (%)").set_value(40.0).run(timeout=30)
        self.assertTrue(any("120.0%" in str(item.value) for item in app.error))
        by_label(app.number_input, "IAU weight (%)").set_value(0.0).run(timeout=30)
        self.assertFalse(any("120.0%" in str(item.value) for item in app.error))
        by_label(app.button, "Reset to Defaults").click().run(timeout=30)
        self.assertEqual(by_label(app.selectbox, "Portfolio").value,
                         "C — Original Minimum-Volatility Portfolio")

    def test_optimization_controls_recalculate_and_reset(self):
        app = self.app()
        app.radio[0].set_value("Analytics").run(timeout=30)
        self.assertEqual(by_label(app.selectbox, "Estimation window").value, "Original 59 returns")
        self.assertEqual(by_label(app.number_input, "Minimum expected annual return (%)").value, 6.0)
        by_label(app.checkbox, "Enable hypothetical concentration bounds · NOT APPROVED").set_value(True).run(timeout=30)
        text = " ".join(str(item.value) for item in app.markdown)
        self.assertIn("40% / 25% / 15% / 0% / 20%", text)
        by_label(app.number_input, "VTI arithmetic return (%)").set_value(20.0).run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        by_label(app.number_input, "IAU annualized volatility (%)").set_value(30.0).run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        by_label(app.button, "Reset to Approved Defaults").click().run(timeout=30)
        self.assertEqual(by_label(app.number_input, "Minimum expected annual return (%)").value, 6.0)
        self.assertFalse(by_label(app.checkbox,
                                  "Enable hypothetical concentration bounds · NOT APPROVED").value)
        self.assertAlmostEqual(by_label(app.number_input, "VTI arithmetic return (%)").value,
                               engine.analyze()["full"]["returns"][0] * 100)

    def test_scenario_recalculation_and_reset_keeps_official_hold(self):
        app = self.app()
        app.radio[0].set_value("Analytics").run(timeout=30)
        by_label(app.selectbox, "Scenario").set_value("Return-floor sensitivity").run(timeout=30)
        by_label(app.number_input, "Hypothetical minimum annual return (%)").set_value(25.0).run(timeout=30)
        self.assertTrue(any("INFEASIBLE" in str(item.value) for item in app.error))
        self.assertTrue(any("Official implementation status: REVIEW HOLD" in str(item.value)
                            for item in app.info))
        by_label(app.button, "Reset scenario").click().run(timeout=30)
        self.assertEqual(by_label(app.selectbox, "Scenario").value, "Expected-return shock")
        self.assertEqual(by_label(app.number_input,
                                  "Change in annual return estimate (percentage points)").value, -5.0)


if __name__ == "__main__":
    unittest.main()
