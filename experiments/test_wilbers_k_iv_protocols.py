#!/usr/bin/env python3
"""Protocol and boundary regressions for the deposited Wilbers K clamp assays."""
from __future__ import annotations

import unittest

import numpy as np

import replay_wilbers_k_iv_neuron as replay
import wilbers_k_iv_fit_diagnostics as fit_diagnostics


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


    def test_source_fit_start_tuple_is_preserved_and_alternative_is_dimensioned(self) -> None:
        current = np.array([0.40, 0.25, 0.10, 0.04, 0.02], dtype=float)
        starts = dict(fit_diagnostics.build_k_iv_fit_initializations(current))
        source = starts["source_literal"]
        delta = float(current[0] - current[-1])

        # The released helper's (a1, tau1, a2, ss) order puts delta/2
        # in the tau1 slot and its default est1=30 in the a2 slot.
        self.assertAlmostEqual(source[0], delta / 2.0)
        self.assertAlmostEqual(source[1], delta / 2.0)
        self.assertEqual(source[2], 30.0)
        self.assertAlmostEqual(source[3], current[0] / 10.0)

        corrected = starts["tau30_equal_amplitudes"]
        self.assertAlmostEqual(corrected[1], 30.0)
        self.assertAlmostEqual(corrected[0], corrected[2])
        self.assertGreaterEqual(corrected[0], 0.0)
        self.assertGreaterEqual(corrected[2], 0.0)

    def test_fit_start_diagnostic_recovers_synthetic_fixed_slow_curve(self) -> None:
        times = np.linspace(0.0, 700.0, 701)
        currents = (
            0.20 * np.exp(-times / 80.0)
            + 0.05 * np.exp(-times / 450.0)
            + 0.01
        )
        rows = fit_diagnostics.diagnose_k_iv_postpeak_fit(
            -70.0, times, currents, 80.0
        )
        selected = next(
            row for row in rows
            if row["initialization"] == "tau100_equal_amplitudes"
        )
        self.assertTrue(selected["fit_converged"])
        self.assertTrue(selected["fit_passes_source_r2_gate"])
        self.assertAlmostEqual(selected["fit_tau_fast_ms"], 80.0, places=2)
        self.assertGreater(selected["fit_r_squared"], 0.99999)

    def test_source_fit_contracts_and_mechanism_identity_are_pinned(self) -> None:
        self.assertEqual(replay.K_IV_FIXED_SLOW_TAU_MS, 450.0)
        self.assertEqual(replay.SOURCE_FILES["mod/k_human.mod"][0], 318647)
        self.assertEqual(replay.SOURCE_FILES["mod/k_human.mod"][2], "d299b3430ecda7a94f6d1c37ac76b2878052c7d5")
        self.assertEqual(replay.SOURCE_FILES["channel_tools.py"][0], 326242)
        self.assertEqual(replay.SOURCE_FILES["fit_k_hh_cma_human.py"][0], 326237)


if __name__ == "__main__":
    unittest.main()
