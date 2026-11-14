#!/usr/bin/env python3
"""Synthetic contract tests for the fixed-tau1 K_IV profile extension."""
from __future__ import annotations

import unittest

import numpy as np

from analyze_wilbers_k_iv_fixed_tau1 import (
    TAU1_MS,
    TAU2_MS,
    analyze_fixed_tau1_profile,
    compare_expected,
    validate_summary_row,
)


class FixedTau1KIVProfileTests(unittest.TestCase):
    def test_recovers_a_signed_component_beyond_the_previous_40_ms_domain(self) -> None:
        times = np.arange(0.0, 489.0, 0.1)
        tau3 = 66.25
        current = (
            1.5e-4 * np.exp(-times / TAU1_MS)
            + 8.0e-5 * np.exp(-times / TAU2_MS)
            - 2.0e-6 * np.exp(-times / tau3)
            + 4.0e-4
        )
        row = analyze_fixed_tau1_profile(
            times,
            current,
            tau3_min_ms=0.1,
            tau3_max_ms=120.0,
            tau3_grid_points=481,
        )
        self.assertEqual(row["tau1_grid_index"], 5)
        self.assertEqual(row["tau1_ms"], TAU1_MS)
        self.assertEqual(row["tau2_ms"], 450.0)
        self.assertAlmostEqual(row["selected_tau3_ms"], tau3, delta=0.15)
        self.assertLess(row["a3_ma_cm2"], 0.0)
        self.assertAlmostEqual(row["positive_control_a3_ma_cm2"], 0.0, delta=1e-12)
        self.assertGreater(row["positive_control_rss_increase_pct"], 0.0)
        self.assertFalse(row["minimum_at_grid_boundary"])
        self.assertFalse(row["near_minimum_1pct_touches_grid_edge"])
        self.assertLessEqual(
            row["near_minimum_1pct_objective_span_ms"],
            row["near_minimum_5pct_objective_span_ms"],
        )
        self.assertLessEqual(
            row["near_minimum_5pct_objective_span_ms"],
            row["near_minimum_10pct_objective_span_ms"],
        )

    def test_validator_rejects_a_changed_tau1_or_basin_geometry(self) -> None:
        times = np.arange(0.0, 489.0, 0.1)
        current = (
            1.5e-4 * np.exp(-times / TAU1_MS)
            + 8.0e-5 * np.exp(-times / TAU2_MS)
            - 2.0e-6 * np.exp(-times / 66.25)
            + 4.0e-4
        )
        row = analyze_fixed_tau1_profile(
            times, current, tau3_min_ms=0.1, tau3_max_ms=120.0, tau3_grid_points=241
        )
        invalid = dict(row)
        invalid["tau1_ms"] += 0.01
        with self.assertRaises(ValueError):
            validate_summary_row(
                invalid,
                tau3_min_ms=0.1,
                tau3_max_ms=120.0,
                tau3_grid_points=241,
            )
        invalid = dict(row)
        invalid["near_minimum_1pct_objective_upper_ms"] += 1.0
        with self.assertRaises(ValueError):
            validate_summary_row(
                invalid,
                tau3_min_ms=0.1,
                tau3_max_ms=120.0,
                tau3_grid_points=241,
            )


    def test_expected_comparison_allows_only_roundoff_scale_neighbor_delta_drift(self) -> None:
        times = np.arange(0.0, 489.0, 0.1)
        current = (
            1.5e-4 * np.exp(-times / TAU1_MS)
            + 8.0e-5 * np.exp(-times / TAU2_MS)
            - 2.0e-6 * np.exp(-times / 66.25)
            + 4.0e-4
        )
        actual = analyze_fixed_tau1_profile(
            times, current, tau3_min_ms=0.1, tau3_max_ms=120.0, tau3_grid_points=241
        )
        expected = dict(actual)
        expected["left_neighbor_delta_rss_pct"] += 5e-11
        compare_expected(actual, expected)

        expected["left_neighbor_delta_rss_pct"] += max(
            abs(actual["left_neighbor_delta_rss_pct"]) * 1e-3, 1e-6
        )
        with self.assertRaises(ValueError):
            compare_expected(actual, expected)


if __name__ == "__main__":
    unittest.main()
