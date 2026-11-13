#!/usr/bin/env python3
"""Protocol and boundary regressions for the deposited Wilbers K clamp assays."""
from __future__ import annotations

import unittest

import numpy as np

import replay_wilbers_k_iv_neuron as replay


class WilbersKVoltageClampProtocolTests(unittest.TestCase):
    def test_k_iv_voltage_grid_and_strict_sample_windows(self) -> None:
        self.assertEqual(replay.TEMPERATURE_CELSIUS, 34.0)
        self.assertEqual(replay.K_IV_SAMPLE_INTERVAL_MS, 0.1)
        self.assertEqual(
            replay.K_IV_VOLTAGES_MV,
            tuple(float(v) for v in range(-110, 60, 5)),
        )
        self.assertEqual(len(replay.K_IV_VOLTAGES_MV), 34)

        times = np.arange(round(670.0 / 0.1) + 1, dtype=float) * 0.1
        activation = (times > 20.4) & (times < 520.0)
        inactivation = (times > 520.0) & (times < 570.0)
        self.assertEqual(len(times), 6_701)
        self.assertEqual(int(np.count_nonzero(activation)), 4_996)
        self.assertEqual(int(np.count_nonzero(inactivation)), 499)
        self.assertAlmostEqual(float(times[activation][0]), 20.4, places=10)
        self.assertAlmostEqual(float(times[activation][-1]), 519.9, places=10)
        self.assertAlmostEqual(float(times[inactivation][0]), 520.1, places=10)
        self.assertAlmostEqual(float(times[inactivation][-1]), 569.9, places=10)

    def test_k_recovery_grid_and_test_window(self) -> None:
        self.assertEqual(replay.K_RECOVERY_SAMPLE_INTERVAL_MS, 0.5)
        self.assertEqual(
            replay.K_RECOVERY_VOLTAGES_MV,
            (-90.0, -85.0, -80.0, -75.0, -70.0),
        )
        self.assertEqual(
            replay.K_RECOVERY_INTERVALS_MS,
            (4.0, 144.0, 484.0, 1024.0, 1764.0, 2704.0, 3844.0, 5184.0, 6724.0, 8464.0),
        )
        self.assertEqual(len(replay.K_RECOVERY_VOLTAGES_MV) * len(replay.K_RECOVERY_INTERVALS_MS), 50)

        for recovery_time in replay.K_RECOVERY_INTERVALS_MS:
            total = 5007.0 + recovery_time
            times = np.arange(round(total / 0.5) + 1, dtype=float) * 0.5
            start = 5002.0 + recovery_time
            stop = start + 5.0
            mask = (times > start) & (times < stop)
            self.assertEqual(int(np.count_nonzero(mask)), 9)
            self.assertAlmostEqual(float(times[mask][0]), start + 0.5, places=9)
            self.assertAlmostEqual(float(times[mask][-1]), stop - 0.5, places=9)

    def test_source_fit_contracts_and_mechanism_identity_are_pinned(self) -> None:
        self.assertEqual(replay.K_IV_FIXED_SLOW_TAU_MS, 450.0)
        self.assertEqual(replay.SOURCE_FILES["mod/k_human.mod"][0], 318647)
        self.assertEqual(replay.SOURCE_FILES["mod/k_human.mod"][2], "d299b3430ecda7a94f6d1c37ac76b2878052c7d5")
        self.assertEqual(replay.SOURCE_FILES["channel_tools.py"][0], 326242)
        self.assertEqual(replay.SOURCE_FILES["fit_k_hh_cma_human.py"][0], 326237)


if __name__ == "__main__":
    unittest.main()
