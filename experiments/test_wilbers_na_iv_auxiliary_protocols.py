#!/usr/bin/env python3
"""Protocol-grid regressions for the deposited Wilbers Na inactivation/recovery assays."""
from __future__ import annotations

import unittest

import numpy as np

import replay_wilbers_na_iv_neuron as replay


class WilbersNaIvAuxiliaryProtocolTests(unittest.TestCase):
    def test_inactivation_prepulse_grid_and_sampling_window(self) -> None:
        self.assertEqual(replay.INACTIVATION_SAMPLE_INTERVAL_MS, 0.005)
        self.assertEqual(replay.INACTIVATION_INITIAL_VOLTAGE_MV, -70.0)
        self.assertEqual(replay.INACTIVATION_TEST_VOLTAGE_MV, -10.0)
        self.assertEqual(
            replay.INACTIVATION_CONDITIONING_VOLTAGES_MV,
            tuple(float(v) for v in range(-105, -45, 2)),
        )
        self.assertEqual(len(replay.INACTIVATION_CONDITIONING_VOLTAGES_MV), 30)

        times = (
            np.arange(round(61.0 / replay.INACTIVATION_SAMPLE_INTERVAL_MS) + 1)
            * replay.INACTIVATION_SAMPLE_INTERVAL_MS
        )
        mask = (
            (times > replay.INACTIVATION_TEST_WINDOW_START_MS)
            & (times < replay.INACTIVATION_TEST_WINDOW_END_MS)
        )
        self.assertEqual(len(times), 12_201)
        self.assertEqual(int(np.count_nonzero(mask)), 799)
        self.assertAlmostEqual(float(times[mask][0]), 51.005, places=12)
        self.assertAlmostEqual(float(times[mask][-1]), 54.995, places=12)

    def test_recovery_paired_pulse_grid_and_test_window(self) -> None:
        self.assertEqual(replay.RECOVERY_SAMPLE_INTERVAL_MS, 0.02)
        self.assertEqual(
            replay.RECOVERY_VOLTAGES_MV,
            tuple(float(v) for v in range(-90, -65, 2)),
        )
        self.assertEqual(
            replay.RECOVERY_INTERVALS_MS,
            tuple(float(v * v) for v in range(1, 13)),
        )
        self.assertEqual(len(replay.RECOVERY_VOLTAGES_MV), 13)
        self.assertEqual(len(replay.RECOVERY_INTERVALS_MS), 12)

        for recovery_time in replay.RECOVERY_INTERVALS_MS:
            total_duration = 14.0 + recovery_time
            times = (
                np.arange(round(total_duration / replay.RECOVERY_SAMPLE_INTERVAL_MS) + 1)
                * replay.RECOVERY_SAMPLE_INTERVAL_MS
            )
            start = 12.0 + recovery_time
            stop = start + 2.0
            mask = (times > start) & (times < stop)
            self.assertEqual(int(np.count_nonzero(mask)), 99)
            self.assertAlmostEqual(float(times[mask][0]), start + 0.02, places=10)
            self.assertAlmostEqual(float(times[mask][-1]), stop - 0.02, places=10)

    def test_inactivation_and_recovery_are_distinct_apparent_current_assays(self) -> None:
        self.assertNotEqual(
            replay.INACTIVATION_SAMPLE_INTERVAL_MS,
            replay.RECOVERY_SAMPLE_INTERVAL_MS,
        )
        self.assertNotEqual(
            replay.INACTIVATION_CONDITIONING_VOLTAGES_MV,
            replay.RECOVERY_VOLTAGES_MV,
        )
        self.assertEqual(
            replay.RECOVERY_FIRST_TEST_VOLTAGE_MV,
            replay.RECOVERY_SECOND_TEST_VOLTAGE_MV,
        )
        self.assertEqual(
            len(replay.RECOVERY_VOLTAGES_MV) * len(replay.RECOVERY_INTERVALS_MS),
            156,
        )


if __name__ == "__main__":
    unittest.main()
