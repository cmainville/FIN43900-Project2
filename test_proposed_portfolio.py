"""Independent checks for the student's fixed Portfolio D and preserved baseline."""

import hashlib
import math
import statistics
import unittest

from streamlit.testing.v1 import AppTest

import portfolio_engine as engine
from dashboard_analytics import maximum_drawdown, monthly_wealth


class ProposedPortfolioTests(unittest.TestCase):
    def test_exact_student_weights_and_mandate(self):
        self.assertEqual(engine.STUDENT_PROPOSED,
                         dict(zip(engine.TICKERS, (0.40, 0.25, 0.15, 0.05, 0.15))))
        self.assertAlmostEqual(sum(engine.STUDENT_PROPOSED.values()), 1.0)
        self.assertTrue(all(value >= 0 for value in engine.STUDENT_PROPOSED.values()))
        self.assertTrue(engine.assess(engine.STUDENT_PROPOSED,
                                      engine.analyze()["full"])["verdict"]["pass"])

    def test_three_window_metrics_against_direct_monthly_returns(self):
        base = engine.analyze()
        extended = engine.analyze_extended(base)
        for index, (name, estimates, _) in enumerate(extended["windows"]):
            prices = engine.load_extended_prices() if index == 0 else engine.load_prices()
            months = 36 if index == 2 else (119 if index == 0 else 59)
            monthly = prices.pct_change(fill_method=None).iloc[1:].tail(months)
            direct = [sum(engine.STUDENT_PROPOSED[ticker] * row[ticker]
                          for ticker in engine.TICKERS)
                      for _, row in monthly.iterrows()]
            result = engine.assess(engine.STUDENT_PROPOSED, estimates)
            self.assertAlmostEqual(result["return"], statistics.fmean(direct) * 12, msg=name)
            self.assertAlmostEqual(result["volatility"],
                                   math.sqrt(statistics.variance(direct) * 12), msg=name)
            self.assertTrue(result["verdict"]["pass"])
        self.assertAlmostEqual(engine.assess(engine.STUDENT_PROPOSED,
                                            extended["windows"][1][1])["return"],
                               0.1374340126958819)

    def test_drawdown_and_wealth_direct_monthly_rebalance(self):
        prices = engine.load_prices()
        monthly = prices.pct_change(fill_method=None).iloc[1:]
        value = 100.0
        peak = 100.0
        drawdown = 0.0
        for _, row in monthly.iterrows():
            value *= 1 + sum(engine.STUDENT_PROPOSED[ticker] * row[ticker]
                             for ticker in engine.TICKERS)
            peak = max(peak, value)
            drawdown = min(drawdown, value / peak - 1)
        wealth = monthly_wealth(prices, engine.STUDENT_PROPOSED)
        self.assertAlmostEqual(wealth.iloc[-1], value)
        self.assertAlmostEqual(maximum_drawdown(wealth), drawdown)

    def test_costs_baselines_hold_and_hashes(self):
        base = engine.analyze()
        self.assertEqual(base["process"]["status"], "REVIEW HOLD")
        self.assertEqual(tuple(base["portfolios"]),
                         ("A — Equal Weight", "B — Lab 15 Reference",
                          "C — Constrained Minimum Volatility"))
        self.assertEqual(tuple(base["optimized_full"]["result"]["weights"].values()),
                         (0.5, 0, 0.1, 0, 0.4))
        self.assertEqual(tuple(base["optimized_recent"]["result"]["weights"].values()),
                         (0.45, 0.2, 0.2, 0, 0.15))
        for source, turnover in ((engine.LAB15_REFERENCE, 0.1),
                                 (base["optimized_full"]["result"]["weights"], 0.35)):
            for bps in (0, 10, 25):
                result = engine.rebalance_costs(source, engine.STUDENT_PROPOSED, bps)
                self.assertAlmostEqual(result["one_way_turnover"], turnover)
                self.assertAlmostEqual(result["total_traded"], 2 * turnover)
                self.assertAlmostEqual(result["cost"], 2 * turnover * bps / 10000)
        for path, expected in (
            (engine.DATA_PATH, "9b8d269bddae60e67548ae9f68f71429a4eab001b67cb7efb03e14082cd2609d"),
            (engine.EXTENDED_DATA_PATH, "d011f64fddc6c3d68ce6301a655375563875fc7272b3e28f76f37d9092b93c34"),
            (engine.EXTENDED_RAW_PATH, "de32e16737f9d003af9b13dc18bb8032e36eb9833c73c0d7efcad8aeea9d296f"),
        ):
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_dashboard_selection_and_decision_status(self):
        app = AppTest.from_file("app.py").run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        app.radio[0].set_value("Analytics").run(timeout=30)
        selected = next(item for item in app.selectbox if item.label == "Portfolio")
        self.assertIn("D — Student-Proposed Diversified Portfolio", selected.options)
        selected.set_value("D — Student-Proposed Diversified Portfolio").run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("Student-proposed fixed allocation" in str(item.value)
                            for item in app.info))
        app.radio[0].set_value("Decision").run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        text = " ".join(str(item.value) for item in app.markdown)
        self.assertIn("Student-proposed conditional-pilot candidate", text)
        self.assertIn("REVIEW HOLD", text)


if __name__ == "__main__":
    unittest.main()
