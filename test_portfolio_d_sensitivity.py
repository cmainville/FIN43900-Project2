"""Independent numerical fixtures for supplementary fixed-weight D scenarios."""

import math
from pathlib import Path
import unittest

import numpy as np

import portfolio_engine as engine
from portfolio_d_sensitivity import SCENARIOS, report_markdown, sensitivity_rows, stressed_estimates


class PortfolioDSensitivityTests(unittest.TestCase):
    @staticmethod
    def fixture():
        return {"returns": np.array([0.14] * 5),
                "covariance": np.diag([0.04, 0.04, 0.04, 0.04, 0.01])}

    def test_equity_return_shock_uses_fixed_weights_and_can_fail_floor(self):
        base = self.fixture()
        shocked = stressed_estimates(base, SCENARIOS[0][0])
        np.testing.assert_allclose(shocked["returns"], [0.04, 0.04, 0.04, 0.04, 0.14])
        np.testing.assert_array_equal(shocked["covariance"], base["covariance"])
        before = engine.assess(engine.STUDENT_PROPOSED, base)
        after = engine.assess(engine.STUDENT_PROPOSED, shocked)
        self.assertAlmostEqual(after["return"], 0.055)
        self.assertAlmostEqual(after["return"] - before["return"], -0.085)
        self.assertAlmostEqual(after["volatility"], before["volatility"])
        self.assertTrue(before["verdict"]["pass"])
        self.assertFalse(after["verdict"]["objective_pass"])
        np.testing.assert_array_equal(base["returns"], [0.14] * 5)

    def test_gold_correlation_shock_rebuilds_valid_covariance(self):
        base = self.fixture()
        shocked = stressed_estimates(base, SCENARIOS[1][0])
        covariance = shocked["covariance"]
        np.testing.assert_allclose(covariance[:4, 4], [0.004] * 4)
        np.testing.assert_allclose(covariance[4, :4], [0.004] * 4)
        np.testing.assert_allclose(np.diag(covariance), np.diag(base["covariance"]))
        self.assertGreaterEqual(np.linalg.eigvalsh(covariance).min(), 0)
        weights = engine.STUDENT_PROPOSED
        equity_squares = sum(weights[t] ** 2 for t in engine.TICKERS[:4])
        expected_variance = equity_squares * 0.04 + weights["IAU"] ** 2 * 0.01
        expected_variance += 2 * weights["IAU"] * sum(weights[t] for t in engine.TICKERS[:4]) * 0.004
        self.assertAlmostEqual(engine.portfolio_metrics(weights, shocked)["volatility"],
                               math.sqrt(expected_variance))
        np.testing.assert_array_equal(base["covariance"], self.fixture()["covariance"])

    def test_equity_volatility_shock_scales_both_covariance_axes(self):
        base = self.fixture()
        shocked = stressed_estimates(base, SCENARIOS[2][0])
        covariance = shocked["covariance"]
        np.testing.assert_allclose(np.diag(covariance), [0.0625] * 4 + [0.01])
        weights = engine.STUDENT_PROPOSED
        expected_variance = sum(weights[t] ** 2 for t in engine.TICKERS[:4]) * 0.0625
        expected_variance += weights["IAU"] ** 2 * 0.01
        self.assertAlmostEqual(engine.portfolio_metrics(weights, shocked)["volatility"],
                               math.sqrt(expected_variance))
        self.assertAlmostEqual(engine.portfolio_metrics(weights, shocked)["return"], 0.14)

    def test_rejects_invalid_correlation_and_unknown_scenario(self):
        base = self.fixture()
        covariance = base["covariance"].copy()
        covariance[0, 4] = covariance[4, 0] = 0.019
        with self.assertRaisesRegex(ValueError, "bounds"):
            stressed_estimates({**base, "covariance": covariance}, SCENARIOS[1][0])
        with self.assertRaisesRegex(ValueError, "Unknown"):
            stressed_estimates(base, "unapproved scenario")

    def test_rows_and_generated_artifact_preserve_official_process(self):
        base = engine.analyze()
        rows = sensitivity_rows(base["full"])
        self.assertEqual(len(rows), 3)
        self.assertAlmostEqual(rows[0]["return_change_pp"], -8.5)
        self.assertFalse(rows[0]["stressed"]["verdict"]["pass"])
        self.assertEqual(base["process"]["status"], "REVIEW HOLD")
        self.assertEqual(base["optimized_full"]["result"]["weights"],
                         {"VTI": .5, "VXUS": 0, "XLE": .1, "IWM": 0, "IAU": .4})
        self.assertEqual(report_markdown(),
                         Path("docs/portfolio-d-sensitivity-output.md").read_text())


if __name__ == "__main__":
    unittest.main()
