#!/usr/bin/env python3
"""Unit tests for the prescribed-voltage gate-sampling counterfactuals."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

import diagnose_wilbers_neuron_solver as diagnostic
import reproduce_wilbers_current_clamp_neuron as reproduction


class VoltageSamplingTests(unittest.TestCase):
    def _source_gate_path(self, times: np.ndarray, voltage: np.ndarray) -> dict[str, np.ndarray]:
        states = np.empty((len(times), len(diagnostic.SOURCE_GATE_NAMES)), dtype=float)
        states[0] = np.asarray([0.05, 0.95, 0.02, 0.99, 0.99], dtype=float)
        for index, dt_ms in enumerate(np.diff(times)):
            states[index + 1] = diagnostic._shared_voltage_cnexp_step(
                states[index], float(voltage[index + 1]) - 10.0, float(dt_ms)
            )
        return {
            name: states[:, index].copy()
            for index, name in enumerate(diagnostic.SOURCE_GATE_NAMES)
        }

    def test_constant_voltage_makes_all_sampling_conventions_identical(self) -> None:
        times = np.arange(7, dtype=float) * 0.02
        voltage = np.full(len(times), -70.0, dtype=float)
        source_gates = self._source_gate_path(times, voltage)
        result = diagnostic.compare_gate_integrators_on_shared_voltage(
            times, voltage, source_gates, use_na_table=0
        )
        sensitivity = result["voltage_stage_sampling_sensitivity"]
        difference = sensitivity["linear_ramp_vs_right_hold"]
        self.assertEqual(difference["overall_rmse_gate_fraction"], 0.0)
        self.assertEqual(difference["overall_maximum_absolute_error_gate_fraction"], 0.0)

    def test_varying_voltage_reports_distinct_bounded_replays(self) -> None:
        times = np.arange(9, dtype=float) * 0.02
        voltage = np.asarray(
            [-70.0, -69.0, -62.0, -45.0, -15.0, 18.0, 8.0, -25.0, -70.0],
            dtype=float,
        )
        source_gates = self._source_gate_path(times, voltage)
        result = diagnostic.compare_gate_integrators_on_shared_voltage(
            times, voltage, source_gates, use_na_table=0
        )
        sensitivity = result["voltage_stage_sampling_sensitivity"]
        self.assertGreater(
            sensitivity["linear_ramp_vs_right_hold"][
                "overall_maximum_absolute_error_gate_fraction"
            ],
            0.0,
        )
        self.assertEqual(
            set(sensitivity["methods_against_recorded_nmodl_gates"]),
            {
                "left_endpoint_hold_rk4",
                "midpoint_hold_rk4",
                "right_endpoint_hold_rk4",
                "linear_voltage_ramp_rk4",
            },
        )
        for metrics in sensitivity["methods_against_recorded_nmodl_gates"].values():
            self.assertTrue(np.isfinite(metrics["overall_rmse_gate_fraction"]))
            self.assertTrue(np.isfinite(metrics["overall_maximum_absolute_error_gate_fraction"]))

    def test_rejects_source_gate_trace_with_wrong_sample_count(self) -> None:
        times = np.arange(4, dtype=float) * 0.02
        voltage = np.full(len(times), -70.0, dtype=float)
        source_gates = self._source_gate_path(times, voltage)
        source_gates[diagnostic.SOURCE_GATE_NAMES[0]] = source_gates[
            diagnostic.SOURCE_GATE_NAMES[0]
        ][:-1]
        with self.assertRaises(reproduction.ReproductionError):
            diagnostic.compare_gate_integrators_on_shared_voltage(
                times, voltage, source_gates, use_na_table=0
            )

    def test_actual_stage_rk4_matches_linear_ramp_for_linear_stage_values(self) -> None:
        gates = np.asarray([0.05, 0.95, 0.02, 0.99, 0.99], dtype=float)
        left = -80.0
        right = 20.0
        stages = np.asarray([left, 0.5 * (left + right), 0.5 * (left + right), right])
        actual = diagnostic._shared_voltage_rk4_step_with_stages(
            gates, stages, 0.02
        )
        expected = diagnostic._shared_voltage_rk4_step_linear_voltage(
            gates, left, right, 0.02
        )
        np.testing.assert_array_equal(actual, expected)

    def test_actual_voltage_stages_replay_matches_recorded_humanjs_gates(self) -> None:
        times = np.arange(9, dtype=float) * 0.02
        voltage = np.asarray(
            [-70.0, -69.0, -62.0, -45.0, -15.0, 18.0, 8.0, -25.0, -70.0],
            dtype=float,
        )
        initial = np.asarray([0.05, 0.95, 0.02, 0.99, 0.99], dtype=float)
        stage_values = np.column_stack(
            (
                voltage[:-1],
                0.5 * (voltage[:-1] + voltage[1:]),
                0.5 * (voltage[:-1] + voltage[1:]),
                voltage[1:],
            )
        )
        actual = np.empty((len(times), 5), dtype=float)
        actual[0] = initial
        for index, dt_ms in enumerate(np.diff(times)):
            actual[index + 1] = diagnostic._shared_voltage_rk4_step_with_stages(
                actual[index], stage_values[index] - 10.0, float(dt_ms)
            )
        gates = {
            name: actual[1:, index].copy()
            for index, name in enumerate(diagnostic.HUMANJS_GATE_NAMES)
        }
        result = diagnostic.compare_gate_sampling_on_humanjs_voltage(
            times[0],
            float(voltage[0]),
            initial,
            times[1:],
            voltage[1:],
            times[1:],
            gates,
            use_na_table=0,
            humanjs_voltage_stage_times_ms=times[1:],
            humanjs_voltage_stages_mv=stage_values,
        )
        metrics = result["methods_against_humanjs_gates"][
            "actual_humanjs_rk4_voltage_stages"
        ]
        self.assertEqual(metrics["overall_rmse_gate_fraction"], 0.0)
        self.assertEqual(
            metrics["overall_maximum_absolute_error_gate_fraction"], 0.0
        )

    def test_voltage_stage_csv_loader_reads_exact_four_stage_columns(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "stages.csv"
            path.write_text(
                "time_ms,stage_1_voltage_mv,stage_2_voltage_mv,stage_3_voltage_mv,stage_4_voltage_mv\n"
                "0.02,-70,-69.9,-69.8,-69.7\n"
                "0.04,-69.7,-69.6,-69.5,-69.4\n",
                encoding="utf-8",
            )
            times, stages = diagnostic.load_humanjs_voltage_stage_trace(path)
        np.testing.assert_array_equal(times, np.asarray([0.02, 0.04]))
        np.testing.assert_array_equal(
            stages,
            np.asarray([[-70.0, -69.9, -69.8, -69.7], [-69.7, -69.6, -69.5, -69.4]]),
        )

    def test_voltage_stage_csv_loader_rejects_nonfinite_voltage(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "stages.csv"
            path.write_text(
                "time_ms,stage_1_voltage_mv,stage_2_voltage_mv,stage_3_voltage_mv,stage_4_voltage_mv\n"
                "0.02,-70,nan,-69.8,-69.7\n"
                "0.04,-69.7,-69.6,-69.5,-69.4\n",
                encoding="utf-8",
            )
            with self.assertRaises(reproduction.ReproductionError):
                diagnostic.load_humanjs_voltage_stage_trace(path)

    def test_actual_voltage_stage_replay_rejects_misaligned_timestamps(self) -> None:
        times = np.arange(5, dtype=float) * 0.02
        voltage = np.full(len(times), -70.0, dtype=float)
        initial = np.asarray([0.05, 0.95, 0.02, 0.99, 0.99], dtype=float)
        gates = {
            name: np.full(4, initial[index], dtype=float)
            for index, name in enumerate(diagnostic.HUMANJS_GATE_NAMES)
        }
        stages = np.full((4, 4), -70.0, dtype=float)
        with self.assertRaises(reproduction.ReproductionError):
            diagnostic.compare_gate_sampling_on_humanjs_voltage(
                times[0],
                float(voltage[0]),
                initial,
                times[1:],
                voltage[1:],
                times[1:],
                gates,
                use_na_table=0,
                humanjs_voltage_stage_times_ms=times[1:] + 0.001,
                humanjs_voltage_stages_mv=stages,
            )

    def test_humanjs_voltage_midpoint_replay_matches_generated_rk4_path(self) -> None:
        times = np.arange(9, dtype=float) * 0.02
        voltage = np.asarray(
            [-70.0, -69.0, -62.0, -45.0, -15.0, 18.0, 8.0, -25.0, -70.0],
            dtype=float,
        )
        initial = np.asarray([0.05, 0.95, 0.02, 0.99, 0.99], dtype=float)
        actual = np.empty((len(times), 5), dtype=float)
        actual[0] = initial
        for index, dt_ms in enumerate(np.diff(times)):
            actual[index + 1] = diagnostic._shared_voltage_rk4_step(
                actual[index],
                0.5 * (voltage[index] + voltage[index + 1]) - 10.0,
                float(dt_ms),
            )
        gates = {
            name: actual[1:, index].copy()
            for index, name in enumerate(diagnostic.HUMANJS_GATE_NAMES)
        }
        result = diagnostic.compare_gate_sampling_on_humanjs_voltage(
            times[0],
            float(voltage[0]),
            initial,
            times[1:],
            voltage[1:],
            times[1:],
            gates,
            use_na_table=0,
        )
        midpoint = result["methods_against_humanjs_gates"]["midpoint_hold_rk4"]
        self.assertEqual(midpoint["overall_rmse_gate_fraction"], 0.0)
        self.assertEqual(
            midpoint["overall_maximum_absolute_error_gate_fraction"], 0.0
        )

    def test_humanjs_voltage_replay_rejects_misaligned_gate_timestamps(self) -> None:
        times = np.arange(5, dtype=float) * 0.02
        voltage = np.full(len(times), -70.0, dtype=float)
        initial = np.asarray([0.05, 0.95, 0.02, 0.99, 0.99], dtype=float)
        gates = {
            name: np.full(4, initial[index], dtype=float)
            for index, name in enumerate(diagnostic.HUMANJS_GATE_NAMES)
        }
        with self.assertRaises(reproduction.ReproductionError):
            diagnostic.compare_gate_sampling_on_humanjs_voltage(
                times[0],
                float(voltage[0]),
                initial,
                times[1:],
                voltage[1:],
                times[1:] + 0.001,
                gates,
                use_na_table=0,
            )

    def test_humanjs_voltage_replay_rejects_nonfinite_initial_time(self) -> None:
        times = np.arange(5, dtype=float) * 0.02
        voltage = np.full(len(times), -70.0, dtype=float)
        initial = np.asarray([0.05, 0.95, 0.02, 0.99, 0.99], dtype=float)
        gates = {
            name: np.full(4, initial[index], dtype=float)
            for index, name in enumerate(diagnostic.HUMANJS_GATE_NAMES)
        }
        with self.assertRaises(reproduction.ReproductionError):
            diagnostic.compare_gate_sampling_on_humanjs_voltage(
                float("nan"),
                float(voltage[0]),
                initial,
                times[1:],
                voltage[1:],
                times[1:],
                gates,
                use_na_table=0,
            )

    def test_rejects_malformed_gate_metric_shapes(self) -> None:
        with self.assertRaises(reproduction.ReproductionError):
            diagnostic._gate_path_metrics(
                np.zeros((3, 5), dtype=float),
                np.zeros((3, 4), dtype=float),
            )


if __name__ == "__main__":
    unittest.main()
