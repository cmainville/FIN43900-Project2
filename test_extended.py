"""Focused independent checks for the supplementary ten-year snapshot."""

import hashlib
import math
import statistics
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd

import portfolio_engine as engine
from prepare_extended_prices import TICKERS as PREP_TICKERS, build_snapshot


class ExtendedHistoryTests(unittest.TestCase):
    def test_snapshot_integrity_and_separate_source(self):
        prices = engine.load_extended_prices()
        self.assertEqual(prices.shape, (120, 5))
        self.assertEqual(tuple(prices.columns), engine.TICKERS)
        self.assertEqual(str(prices.index[0].date()), "2016-10-31")
        self.assertEqual(str(prices.index[-1].date()), "2026-09-30")
        self.assertTrue(np.isfinite(prices.to_numpy()).all())
        self.assertTrue((prices.to_numpy() > 0).all())
        self.assertEqual(engine.estimate_extended(prices)["observations"], 119)
        self.assertEqual(
            hashlib.sha256(engine.DATA_PATH.read_bytes()).hexdigest(),
            "9b8d269bddae60e67548ae9f68f71429a4eab001b67cb7efb03e14082cd2609d",
        )
        self.assertNotEqual(engine.DATA_PATH.read_bytes(), engine.EXTENDED_DATA_PATH.read_bytes())

    def test_archive_rebuilds_csv_exactly(self):
        self.assertEqual(PREP_TICKERS, engine.TICKERS)
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            with ZipFile(engine.EXTENDED_RAW_PATH) as archive:
                self.assertEqual(set(archive.namelist()), {ticker + ".json" for ticker in engine.TICKERS})
                archive.extractall(folder)
            output = folder / "rebuilt.csv"
            build_snapshot({ticker: folder / f"{ticker}.json" for ticker in engine.TICKERS}, output)
            self.assertEqual(output.read_bytes(), engine.EXTENDED_DATA_PATH.read_bytes())

    def test_direct_return_covariance_and_volatility_calculation(self):
        prices = engine.load_extended_prices()
        estimates = engine.estimate_extended(prices)
        vti = prices["VTI"].tolist()
        iau = prices["IAU"].tolist()
        vti_returns = [vti[i] / vti[i - 1] - 1 for i in range(1, len(vti))]
        iau_returns = [iau[i] / iau[i - 1] - 1 for i in range(1, len(iau))]
        self.assertAlmostEqual(vti_returns[0], prices["VTI"].iloc[1] / prices["VTI"].iloc[0] - 1)
        self.assertAlmostEqual(estimates["returns"][0], statistics.fmean(vti_returns) * 12)
        self.assertAlmostEqual(estimates["returns"][4], statistics.fmean(iau_returns) * 12)
        vti_mean = statistics.fmean(vti_returns)
        iau_mean = statistics.fmean(iau_returns)
        manual_cov = (
            sum((x - vti_mean) * (y - iau_mean) for x, y in zip(vti_returns, iau_returns))
            / (len(vti_returns) - 1) * 12
        )
        self.assertAlmostEqual(estimates["covariance"][0, 4], manual_cov)
        self.assertAlmostEqual(
            estimates["covariance"][4, 4],
            statistics.variance(iau_returns) * 12,
        )
        weights = {ticker: (0.5 if ticker in ("VTI", "IAU") else 0) for ticker in engine.TICKERS}
        manual_variance = (
            0.25 * estimates["covariance"][0, 0]
            + 0.5 * manual_cov
            + 0.25 * estimates["covariance"][4, 4]
        )
        self.assertAlmostEqual(engine.portfolio_metrics(weights, estimates)["volatility"],
                               math.sqrt(manual_variance))

    def test_extended_invalid_inputs_are_rejected(self):
        frame = pd.read_csv(engine.EXTENDED_DATA_PATH)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            for bad in (
                frame.iloc[:-1],
                frame.iloc[::-1],
                frame.rename(columns={"IAU": "QQQ"}),
                frame.assign(VTI=frame["VTI"].mask(frame.index == 0)),
                frame.assign(IAU=frame["IAU"].mask(frame.index == 0, -1)),
            ):
                bad.to_csv(path, index=False)
                with self.assertRaises((ValueError, TypeError)):
                    engine.load_extended_prices(path)

    def test_three_windows_preserve_original_results(self):
        base = engine.analyze()
        extended = engine.analyze_extended(base)
        self.assertEqual([row[1]["observations"] for row in extended["windows"]], [119, 59, 36])
        solutions = [row[2] for row in extended["windows"]]
        self.assertEqual(tuple(solutions[0]["result"]["weights"].values()), (0.5, 0, 0, 0, 0.5))
        self.assertEqual(tuple(solutions[1]["result"]["weights"].values()), (0.5, 0, 0.1, 0, 0.4))
        self.assertEqual(tuple(solutions[2]["result"]["weights"].values()), (0.45, 0.2, 0.2, 0, 0.15))
        self.assertTrue(all(row["feasible"] and row["feasible_count"] == 10626 for row in solutions))
        self.assertEqual([row["largest_change"][1] for row in extended["comparisons"]], [10, 35, 25])
        self.assertEqual([row["supplementary_threshold_breach"] for row in extended["comparisons"]],
                         [False, True, None])
        self.assertTrue(base["stability_triggered"])


if __name__ == "__main__":
    unittest.main()
