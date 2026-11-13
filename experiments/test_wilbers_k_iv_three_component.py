#!/usr/bin/env python3
"""Synthetic regressions for the non-source Wilbers K_IV residual model."""
from __future__ import annotations

import unittest

import numpy as np

from wilbers_k_iv_three_component import (
    fit_two_exponential_baseline,
    profile_three_exponential_correction,
)


class KIVThreeComponentCounterfactualTests(unittest.TestCase):
    def setUp(self) -> None:
        self.times = np.arange(0.0, 100.0 + 0.1, 0.1)
        self.tau1 = 339.41125496954277
        self.tau2 = 450.0

    def test_signed_profile_recovers_a_small_fast_residual_correction(self) -> None:
        expected = np.asarray([6.03e-5, 2.584e-5, -3.18e-7, 4.1447e-4])
        design = np.column_stack(
            (
                np.exp(-self.times / self.tau1),
                np.exp(-self.times / self.tau2),
                np.exp(-self.times / 1.2335),
                np.ones_like(self.times),
            )
        )
        current = design @ expected
        result = profile_three_exponential_correction(
            self.times,
            current,
            self.tau1,
            tau3_min_ms=0.6,
            tau3_max_ms=2.0,
            grid_points=141,
        )
        fit = result["best_signed"]
        self.assertAlmostEqual(fit["tau3_ms"], 1.2335, delta=0.01)
        self.assertLess(fit["a3_ma_cm2"], 0.0)
        self.assertLess(fit["rmse_full_ma_cm2"], 5.0e-11)
        self.assertAlmostEqual(
            result["positive_control"]["a3_ma_cm2"], 0.0, delta=1.0e-13
        )

    def test_nonnegative_control_does_not_add_a_component_to_a_two_term_trace(self) -> None:
        current = (
            6.0e-5 * np.exp(-self.times / self.tau1)
            + 2.6e-5 * np.exp(-self.times / self.tau2)
            + 4.14e-4
        )
        baseline = fit_two_exponential_baseline(self.times, current, self.tau1)
        result = profile_three_exponential_correction(
            self.times,
            current,
            self.tau1,
            tau3_min_ms=0.6,
            tau3_max_ms=2.0,
            grid_points=41,
        )
        control = result["positive_control"]
        self.assertGreaterEqual(control["a3_ma_cm2"], 0.0)
        self.assertAlmostEqual(control["a3_ma_cm2"], 0.0, delta=1.0e-13)
        self.assertAlmostEqual(
            control["rmse_full_ma_cm2"],
            baseline["rmse_full_ma_cm2"],
            delta=1.0e-12,
        )

    def test_rejects_invalid_time_constant_and_waveform(self) -> None:
        with self.assertRaises(ValueError):
            profile_three_exponential_correction(
                self.times, np.ones_like(self.times), -1.0
            )
        with self.assertRaises(ValueError):
            profile_three_exponential_correction(
                self.times[:-1], np.ones_like(self.times), self.tau1
            )


if __name__ == "__main__":
    unittest.main()
