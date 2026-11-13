#!/usr/bin/env python3
"""Synthetic and input-contract tests for the multivoltage K_IV audit."""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import numpy as np

from wilbers_k_iv_multivoltage import (
    K_IV_MULTIVOLTAGE_TARGETS_MV,
    analyze_k_iv_waveform,
    analyze_tau1_tau3_surface,
    read_postpeak_waveforms,
    summarize_tau3_profile_shape,
    validate_summary_rows,
    validate_tau3_profile_shape_rows,
    validate_tau1_tau3_surface_rows,
)
from wilbers_k_iv_three_component import profile_three_exponential_correction


class KIVMultivoltageTests(unittest.TestCase):
    def test_signed_short_component_is_recovered_on_a_source_length_waveform(self) -> None:
        times = np.arange(0.0, 489.0, 0.1)
        source_times = times + 30.9
        current = (
            6.0e-5 * np.exp(-times / 339.4)
            + 2.6e-5 * np.exp(-times / 450.0)
            - 3.2e-7 * np.exp(-times / 1.23)
            + 4.144e-4
        )
        result = analyze_k_iv_waveform(
            -70.0,
            times,
            source_times,
            current,
            coarse_profile_points=201,
            local_profile_points=101,
            short_profile_points=101,
        )
        self.assertTrue(result["signed_extra_is_negative"])
        self.assertTrue(result["nonnegative_control_collapsed"])
        self.assertEqual(result["positive_control_improvement_pct"], 0.0)
        self.assertLess(result["corrected_full_rmse_ma_cm2"], result["baseline_full_rmse_ma_cm2"])
        self.assertLess(result["full_improvement_pct"], 100.0)
        self.assertGreater(result["full_improvement_pct"], 50.0)
        self.assertAlmostEqual(result["tau3_ms"], 1.23, delta=0.1)
        self.assertAlmostEqual(result["tau3_profile_min_ms"], 0.6)
        self.assertAlmostEqual(result["tau3_profile_max_ms"], 2.0)
        self.assertFalse(result["tau3_profile_at_boundary"])

    def test_wider_tau3_grid_recovers_component_outside_previous_bounds(self) -> None:
        times = np.arange(0.0, 489.0, 0.1)
        source_times = times + 30.9
        current = (
            6.0e-5 * np.exp(-times / 339.4)
            + 2.6e-5 * np.exp(-times / 450.0)
            - 3.2e-7 * np.exp(-times / 3.2)
            + 4.144e-4
        )
        result = profile_three_exponential_correction(
            times,
            current,
            339.4,
            tau2_ms=450.0,
            tau3_min_ms=0.1,
            tau3_max_ms=5.0,
            grid_points=2801,
        )
        fitted = result["best_signed"]
        self.assertAlmostEqual(fitted["tau3_ms"], 3.2, delta=0.002)
        self.assertLess(fitted["a3_ma_cm2"], 0.0)
        self.assertEqual(fitted["profile_grid_points"], 2801)
        self.assertAlmostEqual(fitted["profile_tau3_min_ms"], 0.1)
        self.assertAlmostEqual(fitted["profile_tau3_max_ms"], 5.0)

    def test_tau3_objective_shape_reports_nested_near_minimum_basins(self) -> None:
        times = np.arange(0.0, 100.0 + 0.1, 0.1)
        current = (
            6.0e-5 * np.exp(-times / 339.4)
            + 2.6e-5 * np.exp(-times / 450.0)
            - 3.2e-7 * np.exp(-times / 3.2)
            + 4.144e-4
        )
        result = profile_three_exponential_correction(
            times, current, 339.4,
            tau2_ms=450.0, tau3_min_ms=0.1, tau3_max_ms=5.0,
            grid_points=801,
        )
        shape = summarize_tau3_profile_shape(-70.0, 339.4, result["profile"])
        validate_tau3_profile_shape_rows([shape | {"voltage_mv": voltage}
            for voltage in K_IV_MULTIVOLTAGE_TARGETS_MV])
        self.assertAlmostEqual(shape["selected_tau3_ms"], 3.2, delta=0.01)
        self.assertGreater(shape["profile_objective_normalized_curvature_per_ms2"], 0.0)
        self.assertLessEqual(
            shape["near_minimum_1pct_objective_span_ms"],
            shape["near_minimum_5pct_objective_span_ms"],
        )
        self.assertLessEqual(
            shape["near_minimum_5pct_objective_span_ms"],
            shape["near_minimum_10pct_objective_span_ms"],
        )
        self.assertFalse(shape["minimum_at_grid_boundary"])

    def test_tau1_tau3_surface_stays_inside_the_existing_local_tau1_window(self) -> None:
        times = np.arange(0.0, 120.0, 0.1)
        current = (
            6.0e-5 * np.exp(-times / 100.0)
            + 2.6e-5 * np.exp(-times / 450.0)
            - 3.2e-7 * np.exp(-times / 3.2)
            + 4.144e-4
        )
        waveforms = {
            voltage: (times.copy(), times.copy() + 30.0, current.copy())
            for voltage in K_IV_MULTIVOLTAGE_TARGETS_MV
        }
        reference_fit = profile_three_exponential_correction(
            times,
            current,
            100.0,
            tau2_ms=450.0,
            tau3_min_ms=0.1,
            tau3_max_ms=5.0,
            grid_points=101,
        )
        reference_tau3 = reference_fit["best_signed"]["tau3_ms"]
        baseline_rows = [
            {
                "voltage_mv": voltage,
                "coarse_tau1_ms": 100.0,
                "local_tau1_ms": 100.0,
                "tau3_ms": reference_tau3,
            }
            for voltage in K_IV_MULTIVOLTAGE_TARGETS_MV
        ]
        rows = analyze_tau1_tau3_surface(
            waveforms,
            baseline_rows,
            tau1_grid_points=3,
            tau3_min_ms=0.1,
            tau3_max_ms=5.0,
            tau3_grid_points=101,
        )
        validate_tau1_tau3_surface_rows(
            rows,
            tau1_grid_points=3,
            tau3_grid_points=101,
            tau3_min_ms=0.1,
            tau3_max_ms=5.0,
        )
        self.assertEqual(len(rows), 9)
        for voltage in (-30.0, -60.0, 55.0):
            group = [row for row in rows if row["voltage_mv"] == voltage]
            self.assertEqual([row["tau1_grid_index"] for row in group], [0, 1, 2])
            self.assertEqual([row["tau1_ms"] for row in group], [94.0, 100.0, 106.0])
            self.assertAlmostEqual(group[1]["selected_tau3_ms"], reference_tau3, delta=1.0e-12)
            self.assertLess(group[1]["a3_ma_cm2"], 0.0)
            self.assertGreaterEqual(group[1]["rmse_full_ma_cm2"], 0.0)
            self.assertGreaterEqual(group[1]["rmse_first_10ms_ma_cm2"], 0.0)
            self.assertGreaterEqual(group[1]["rmse_after_10ms_ma_cm2"], 0.0)
            self.assertEqual(sum(row["is_global_surface_minimum"] for row in group), 1)
        rows[0]["tau1_ms"] = 107.0
        with self.assertRaises(ValueError):
            validate_tau1_tau3_surface_rows(
                rows,
                tau1_grid_points=3,
                tau3_grid_points=101,
                tau3_min_ms=0.1,
                tau3_max_ms=5.0,
            )

    def test_tau3_boundary_flag_is_enforced_by_summary_validation(self) -> None:
        times = np.arange(0.0, 489.0, 0.1)
        source_times = times + 30.9
        current = (
            6.0e-5 * np.exp(-times / 339.4)
            + 2.6e-5 * np.exp(-times / 450.0)
            - 3.2e-7 * np.exp(-times / 3.2)
            + 4.144e-4
        )
        result = analyze_k_iv_waveform(
            -70.0, times, source_times, current,
            coarse_profile_points=101,
            local_profile_points=81,
            short_profile_points=101,
            tau3_min_ms=0.1,
            tau3_max_ms=5.0,
        )
        row = dict(result)
        row["tau3_ms"] = 0.1
        row["tau3_profile_at_boundary"] = True
        rows = []
        for voltage in K_IV_MULTIVOLTAGE_TARGETS_MV:
            cloned = dict(row)
            cloned["voltage_mv"] = voltage
            rows.append(cloned)
        validate_summary_rows(rows, tau3_min_ms=0.1, tau3_max_ms=5.0)
        rows[0]["tau3_profile_at_boundary"] = False
        with self.assertRaises(ValueError):
            validate_summary_rows(rows, tau3_min_ms=0.1, tau3_max_ms=5.0)

    def test_reader_preserves_exact_voltage_and_two_clock_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "waveforms.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                stream.write(
                    "# DataverseNL v3.0; NEURON 9.0.2\n"
                    "# channel_tools.py SHA-1 615595a270c6170987757cd35743f5d5b5b2af0e\n"
                    "# k_human.mod SHA-1 d299b3430ecda7a94f6d1c37ac76b2878052c7d5\n"
                )
                writer = csv.writer(stream, lineterminator="\n")
                writer.writerow(
                    [
                        "voltage_mv",
                        "time_since_peak_ms",
                        "source_simulation_time_ms",
                        "observed_current_ma_cm2",
                    ]
                )
                for voltage in K_IV_MULTIVOLTAGE_TARGETS_MV:
                    for index in range(100):
                        time = index * 0.1
                        writer.writerow([voltage, time, time + 30.9, 5.0e-4 - index * 1e-9])
            waveforms = read_postpeak_waveforms(path)
        self.assertEqual(tuple(waveforms), K_IV_MULTIVOLTAGE_TARGETS_MV)
        self.assertEqual(len(waveforms), 27)
        self.assertEqual(K_IV_MULTIVOLTAGE_TARGETS_MV[0], -75.0)
        self.assertEqual(K_IV_MULTIVOLTAGE_TARGETS_MV[-1], 55.0)
        for voltage, (times, source_times, currents) in waveforms.items():
            self.assertEqual(len(times), 100)
            self.assertAlmostEqual(float(source_times[0]), 30.9)
            self.assertAlmostEqual(float(times[-1]), 9.9)
            self.assertEqual(len(currents), 100)

    def test_reader_rejects_missing_eligible_voltage_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "waveforms.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                stream.write(
                    "# DataverseNL v3.0; NEURON 9.0.2\n"
                    "# channel_tools.py SHA-1 615595a270c6170987757cd35743f5d5b5b2af0e\n"
                    "# k_human.mod SHA-1 d299b3430ecda7a94f6d1c37ac76b2878052c7d5\n"
                )
                writer = csv.writer(stream, lineterminator="\n")
                writer.writerow(
                    [
                        "voltage_mv",
                        "time_since_peak_ms",
                        "source_simulation_time_ms",
                        "observed_current_ma_cm2",
                    ]
                )
                for voltage in K_IV_MULTIVOLTAGE_TARGETS_MV[:-1]:
                    for index in range(100):
                        time = index * 0.1
                        writer.writerow([voltage, time, time + 30.9, 5.0e-4 - index * 1e-9])
            with self.assertRaises(ValueError):
                read_postpeak_waveforms(path)

    def test_rejects_clock_misalignment_and_nonmonotone_time(self) -> None:
        times = np.arange(0.0, 120.0, 0.1)
        currents = 4.0e-4 + 1.0e-5 * np.exp(-times / 20.0)
        misaligned_source_times = times + 31.0
        misaligned_source_times[50] += 0.01
        with self.assertRaises(ValueError):
            analyze_k_iv_waveform(
                -70.0, times, misaligned_source_times, currents
            )
        invalid_times = times.copy()
        invalid_times[40] = invalid_times[39]
        with self.assertRaises(ValueError):
            analyze_k_iv_waveform(-70.0, invalid_times, invalid_times + 30.9, currents)


if __name__ == "__main__":
    unittest.main()
