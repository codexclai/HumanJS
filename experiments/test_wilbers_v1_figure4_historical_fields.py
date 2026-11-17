#!/usr/bin/env python3
"""Integrity tests for historical Wilbers v1.0 Figure 4 K fit fields."""

from __future__ import annotations

import csv
import io
import math
import statistics
import unittest
from pathlib import Path


DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "HUMAN-L23-WILBERS-FIG4-V1-HISTORICAL-EXTRA-K-FITS.csv"
)
VOLTAGES_MV = (-120, -110, -100, -90, -80, -70, -60, -50, -40)
EXPECTED_COUNTS = (4, 5, 2, 4, 4, 3, 8, 10, 10)
EXPECTED_MEANS_MS = (
    23.3270442652869,
    25.96090821365678,
    29.771663763945448,
    42.07488407844052,
    43.758915721700404,
    30.152629061738498,
    31.510372973578466,
    53.479048089798425,
    77.73548497525488,
)
EXPECTED_SAMPLE_SDS_MS = (
    7.7464901778019195,
    10.860891636086496,
    11.711285579727791,
    34.28444265323052,
    23.81004965368326,
    15.401275131710802,
    15.219437245992966,
    22.641323727968587,
    33.087756207379215,
)


def load_records() -> list[dict[str, str]]:
    text = DATA_PATH.read_text(encoding="utf-8")
    data_lines = [line for line in text.splitlines() if line and not line.startswith("#")]
    return list(csv.DictReader(io.StringIO("\n".join(data_lines))))


class WilbersV1HistoricalFigure4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = load_records()

    def test_preserves_all_human_rows_and_the_nine_voltage_grid(self) -> None:
        self.assertEqual(len(self.records), 13)
        self.assertEqual(
            [int(row["record_index"]) for row in self.records],
            list(range(1, 14)),
        )
        self.assertEqual(
            list(self.records[0].keys()),
            ["record_index", "reversal", "amp1to200", "tau_rec", "ss_rec"]
            + [
                field
                for voltage in VOLTAGES_MV
                for field in (f"tau_deact_{voltage}", f"gof_deact_{voltage}")
            ],
        )

    def test_deactivation_missingness_and_aggregates_are_stable(self) -> None:
        for voltage, expected_n, expected_mean, expected_sd in zip(
            VOLTAGES_MV,
            EXPECTED_COUNTS,
            EXPECTED_MEANS_MS,
            EXPECTED_SAMPLE_SDS_MS,
            strict=True,
        ):
            pairs = []
            for row in self.records:
                tau_text = row[f"tau_deact_{voltage}"]
                gof_text = row[f"gof_deact_{voltage}"]
                self.assertEqual(
                    tau_text == "",
                    gof_text == "",
                    f"tau/gof missingness differs at {voltage} mV",
                )
                if tau_text:
                    tau_ms = float(tau_text)
                    gof = float(gof_text)
                    self.assertGreater(tau_ms, 0.0)
                    self.assertTrue(0.0 <= gof <= 1.0)
                    pairs.append(tau_ms)
            self.assertEqual(len(pairs), expected_n)
            self.assertTrue(
                math.isclose(
                    statistics.fmean(pairs), expected_mean, rel_tol=0.0, abs_tol=1e-11
                )
            )
            self.assertTrue(
                math.isclose(
                    statistics.stdev(pairs), expected_sd, rel_tol=0.0, abs_tol=1e-11
                )
            )

    def test_legacy_scalar_fields_keep_their_source_missingness(self) -> None:
        self.assertEqual(sum(row["reversal"] != "" for row in self.records), 13)
        self.assertEqual(sum(row["amp1to200"] != "" for row in self.records), 12)
        self.assertEqual(sum(row["tau_rec"] != "" for row in self.records), 12)
        self.assertEqual(sum(row["ss_rec"] != "" for row in self.records), 12)
        # The source's literal zero is preserved, not silently rewritten as missing.
        self.assertEqual(sum(float(row["reversal"] or "nan") == 0.0 for row in self.records), 1)

    def test_historical_fits_are_not_all_filtered_by_the_model_helpers_r2_gate(self) -> None:
        # The old model helper accepts a deactivation fit only when R² > 0.90.
        # The workbook stores some tau_deact values with a lower gof; do not
        # silently claim these rows followed that helper's exact selection.
        stored_fits = [
            float(row[f"gof_deact_{voltage}"])
            for row in self.records
            for voltage in VOLTAGES_MV
            if row[f"gof_deact_{voltage}"] != ""
        ]
        self.assertTrue(any(value <= 0.90 for value in stored_fits))
        self.assertTrue(any(value > 0.90 for value in stored_fits))


if __name__ == "__main__":
    unittest.main()
