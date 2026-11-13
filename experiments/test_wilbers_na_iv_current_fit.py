#!/usr/bin/env python3
"""Tests for the independent Wilbers Na_IV composite-current fit replay."""
from __future__ import annotations

import math
import unittest

import numpy as np

import replay_wilbers_na_iv_current_fit as replay


class WilbersNaIvCurrentFitTests(unittest.TestCase):
    def test_deposited_protocol_grid_and_sample_mask_are_exact(self) -> None:
        self.assertEqual(
            replay.TEST_VOLTAGES_MV,
            tuple(float(value) for value in range(-80, 11, 5)),
        )
        times, current = replay.simulate_normalized_sodium_current(-35.0)
        mask = (times > 2.02) & (times < 12.0)
        self.assertEqual(len(times), 1201)
        self.assertEqual(int(np.count_nonzero(mask)), 997)
        self.assertAlmostEqual(float(times[mask][0]), 2.03, places=12)
        self.assertAlmostEqual(float(times[mask][-1]), 11.99, places=12)
        self.assertTrue(np.isfinite(current).all())
        self.assertTrue(np.all(current[mask] > 0.0))
        self.assertGreater(float(np.max(current[mask])), replay.SOURCE_MIN_INWARD_CURRENT_MA_CM2)
        self.assertEqual(replay.SODIUM_GBAR_PS_PER_UM2, 40.0)
        self.assertEqual(replay.SODIUM_REVERSAL_MV, 141.0)

    def test_composite_current_has_the_deposited_50_microsecond_delay(self) -> None:
        times = np.asarray([0.0, 0.049, 0.05, 0.06, 0.1], dtype=float)
        current = replay._source_composite_sodium_current(times, 0.2, 2.0, 1.0, 0.1)
        np.testing.assert_array_equal(current[:3], np.zeros(3))
        self.assertGreater(float(current[3]), 0.0)
        self.assertGreater(float(current[4]), float(current[3]))

    def test_current_amplitude_scaling_does_not_change_fit_time_constants(self) -> None:
        times, current = replay.simulate_normalized_sodium_current(-45.0)
        mask = (times > 2.02) & (times < 12.0)
        baseline = replay.fit_source_composite_current(times[mask], current[mask])
        scaled = replay.fit_source_composite_current(times[mask], current[mask] * 37.0)
        for field in (
            "preliminary_tau_m_ms", "preliminary_tau_h_ms",
            "joint_tau_m_ms", "joint_tau_h_ms",
        ):
            self.assertAlmostEqual(baseline[field], scaled[field], delta=2.0e-5)
        self.assertAlmostEqual(
            baseline["joint_r_squared"], scaled["joint_r_squared"], delta=1.0e-10
        )

    def test_na_iv_replays_19_voltages_and_source_fit_quality_rule(self) -> None:
        rows = replay.replay_na_iv_current_fits()
        self.assertEqual(len(rows), 19)
        self.assertEqual([row["voltage_mv"] for row in rows], list(replay.TEST_VOLTAGES_MV))
        self.assertTrue(all(row["samples_fitted"] == 997 for row in rows))
        self.assertTrue(all(row["absolute_current_gate_passed"] for row in rows))
        accepted = [
            row["voltage_mv"] for row in rows if row["passed_joint_fit_r2"]
        ]
        self.assertEqual(accepted, list(map(float, range(-70, 11, 5))))
        self.assertLess(rows[0]["joint_r_squared"], replay.FIT_R2_THRESHOLD)
        self.assertLess(rows[1]["joint_r_squared"], replay.FIT_R2_THRESHOLD)
        self.assertTrue(all(math.isfinite(row["source_mapped_tau_m_ms"]) for row in rows[2:]))

    def test_source_returns_joint_tau_m_but_preliminary_tau_h(self) -> None:
        row = next(
            item for item in replay.replay_na_iv_current_fits()
            if item["voltage_mv"] == -70.0
        )
        self.assertTrue(row["passed_joint_fit_r2"])
        self.assertAlmostEqual(row["source_mapped_tau_m_ms"], row["joint_tau_m_ms"], delta=1.0e-12)
        self.assertAlmostEqual(row["source_mapped_tau_h_ms"], row["preliminary_tau_h_ms"], delta=1.0e-12)
        self.assertGreater(row["joint_tau_h_ms"], 1.5 * row["source_mapped_tau_h_ms"])
        self.assertGreater(row["preliminary_tau_m_r_squared"], 0.95)
        self.assertGreater(row["preliminary_tau_h_r_squared"], 0.95)
        self.assertGreater(abs(row["source_mapped_tau_h_ms"] - row["gate_tau_h_ms"]), 0.1)
        self.assertTrue(row["joint_tau_h_at_upper_bound"])

    def test_low_r_squared_step_returns_nan_taus_as_source_does(self) -> None:
        row = replay.replay_na_iv_current_fits()[0]
        self.assertEqual(row["voltage_mv"], -80.0)
        self.assertTrue(row["absolute_current_gate_passed"])
        self.assertFalse(row["passed_joint_fit_r2"])
        self.assertTrue(math.isnan(row["source_mapped_tau_m_ms"]))
        self.assertTrue(math.isnan(row["source_mapped_tau_h_ms"]))


if __name__ == "__main__":
    unittest.main()
