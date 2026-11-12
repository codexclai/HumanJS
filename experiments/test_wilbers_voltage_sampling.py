#!/usr/bin/env python3
"""Unit tests for the prescribed-voltage gate-sampling counterfactuals."""

from __future__ import annotations

import unittest

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

    def test_rejects_malformed_gate_metric_shapes(self) -> None:
        with self.assertRaises(reproduction.ReproductionError):
            diagnostic._gate_path_metrics(
                np.zeros((3, 5), dtype=float),
                np.zeros((3, 4), dtype=float),
            )


if __name__ == "__main__":
    unittest.main()
