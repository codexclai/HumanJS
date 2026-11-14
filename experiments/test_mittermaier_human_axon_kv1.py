#!/usr/bin/env python3
"""Synthetic tests for the published human axonal Kv1 source-data analysis."""
from __future__ import annotations

import unittest

import numpy as np

from analyze_mittermaier_human_axon_kv1 import (
    fit_boltzmann,
    _boltzmann_decreasing,
    _boltzmann_increasing,
    _result_row,
    serialize_rows,
)


class MittermaierHumanAxonalKv1Tests(unittest.TestCase):
    def test_activation_boltzmann_recovers_known_increasing_curve(self) -> None:
        voltage = np.arange(-90.0, 71.0, 20.0)
        conductance = _boltzmann_increasing(voltage, 0.02, 1.0, -7.0, 24.0)
        fit = fit_boltzmann(voltage, conductance, direction="increasing")
        self.assertAlmostEqual(fit["vhalf_mv"], -7.0, places=6)
        self.assertAlmostEqual(fit["slope_mv"], 24.0, places=6)
        self.assertLess(fit["rmse"], 1e-9)

    def test_inactivation_boltzmann_recovers_known_decreasing_curve(self) -> None:
        voltage = np.arange(-110.0, 1.0, 10.0)
        conductance = _boltzmann_decreasing(voltage, 0.08, 1.0, -43.0, 13.0)
        fit = fit_boltzmann(voltage, conductance, direction="decreasing")
        self.assertAlmostEqual(fit["vhalf_mv"], -43.0, places=6)
        self.assertAlmostEqual(fit["slope_mv"], 13.0, places=6)
        self.assertLess(fit["rmse"], 1e-9)

    def test_inactivation_fit_direction_is_decreasing_not_activation(self) -> None:
        voltage = np.array([-110.0, -90.0, -70.0, -50.0, -30.0, -10.0, 0.0])
        conductance = _boltzmann_decreasing(voltage, 0.05, 1.0, -43.0, 13.0)
        fit = fit_boltzmann(voltage, conductance, direction="decreasing")
        self.assertLess(fit["vhalf_mv"], -30.0)
        self.assertGreater(fit["slope_mv"], 0.0)

    def test_long_inactivation_mean_fit_recovers_two_time_scales(self) -> None:
        time = np.linspace(0.02, 2900.02, 1500)
        mean = (
            0.35 * np.exp(-time / 1330.0)
            + 0.24 * np.exp(-time / 120.0)
            + 0.41
        )
        from analyze_mittermaier_human_axon_kv1 import fit_long_inactivation_mean

        fit = fit_long_inactivation_mean(time, mean)
        self.assertAlmostEqual(fit["tau_fast_ms"], 120.0, delta=0.5)
        self.assertAlmostEqual(fit["tau_slow_ms"], 1330.0, delta=1.0)
        self.assertAlmostEqual(fit["offset"], 0.41, delta=0.002)

    def test_summary_serialization_preserves_schema_and_blank_fields(self) -> None:
        row = _result_row(
            analysis="dtx_block_summary",
            recording_id="group_summary",
            n_points=5,
            mean_block_fraction=0.55,
            sd_block_fraction=0.13,
            sem_block_fraction=0.06,
        )
        content = serialize_rows([row])
        lines = content.splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("mean_block_fraction", lines[0])
        self.assertIn("group_summary", lines[1])
        self.assertTrue(lines[1].endswith("0.55,0.13,0.06"))


if __name__ == "__main__":
    unittest.main()
