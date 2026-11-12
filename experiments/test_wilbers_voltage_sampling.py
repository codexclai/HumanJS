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


    def test_humanjs_current_balance_loader_reads_four_exact_stages(self) -> None:
        fields = ["time_ms"]
        row = ["0.02"]
        for stage in range(1, 5):
            for name, value in (
                ("na_a_per_m2", -0.1),
                ("k_a_per_m2", 0.2),
                ("leak_a_per_m2", 0.01),
                ("injected_a_per_m2", 0.0),
                ("dvdt_v_per_s", -11.0),
            ):
                fields.append(f"stage_{stage}_{name}")
                row.append(str(value))
        endpoint_names = (
            "endpoint_na_a_per_m2",
            "endpoint_k_a_per_m2",
            "endpoint_leak_a_per_m2",
            "endpoint_injected_a_per_m2",
            "endpoint_dvdt_v_per_s",
        )
        fields.extend(endpoint_names)
        row.extend(["-0.1", "0.2", "0.01", "0.0", "-11.0"])
        second_row = ["0.04", *row[1:]]
        with TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "currents.csv"
            path.write_text(
                ",".join(fields) + "\n" + ",".join(row) + "\n" + ",".join(second_row) + "\n",
                encoding="utf-8",
            )
            times, stages, endpoint = diagnostic.load_humanjs_current_balance_trace(path)
        np.testing.assert_array_equal(times, np.asarray([0.02, 0.04]))
        self.assertEqual(stages.shape, (2, 4, 5))
        self.assertEqual(endpoint.shape, (2, 5))
        np.testing.assert_array_equal(stages[0, 0], np.asarray([-0.1, 0.2, 0.01, 0.0, -11.0]))

    def test_humanjs_current_balance_loader_rejects_nonfinite_stage(self) -> None:
        fields = ["time_ms"]
        row = ["0.02"]
        for stage in range(1, 5):
            for name in ("na_a_per_m2", "k_a_per_m2", "leak_a_per_m2", "injected_a_per_m2", "dvdt_v_per_s"):
                fields.append(f"stage_{stage}_{name}")
                row.append("nan" if stage == 2 and name == "k_a_per_m2" else "0.0")
        fields.extend(("endpoint_na_a_per_m2", "endpoint_k_a_per_m2", "endpoint_leak_a_per_m2", "endpoint_injected_a_per_m2", "endpoint_dvdt_v_per_s"))
        row.extend(["0.0"] * 5)
        with TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "currents.csv"
            path.write_text(
                ",".join(fields) + "\n" + ",".join(row) + "\n" + ",".join(["0.04", *row[1:]]) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(reproduction.ReproductionError):
                diagnostic.load_humanjs_current_balance_trace(path)

    def test_source_implicit_and_humanjs_rk4_current_balances_close(self) -> None:
        times = np.asarray([1.0, 1.02, 1.04], dtype=float)
        voltage = np.full(3, -70.0, dtype=float)
        gate_state = np.asarray([0.0244876225, 0.803433478, 0.03886289, 0.89016592, 0.89016592])
        source_gates = {
            name: np.full(3, gate_state[index], dtype=float)
            for index, name in enumerate(diagnostic.SOURCE_GATE_NAMES)
        }
        source_current = diagnostic._wilbers_current_density_a_per_m2(
            voltage, np.tile(gate_state, (3, 1)), 114.47654963753565, 29.045736151752504
        )
        injected_pa = float(source_current[0].sum() * np.pi * 100.0e-12 * 1.0e12)
        source_currents = {
            "ina": source_current[:, 0] / 10.0,
            "ik": source_current[:, 1] / 10.0,
            "i_pas": source_current[:, 2] / 10.0,
        }
        stages = np.zeros((2, 4, 5), dtype=float)
        stages[:, :, :3] = source_current[0]
        stages[:, :, 3] = source_current[0].sum()
        endpoint = np.zeros((2, 5), dtype=float)
        endpoint[:, :3] = source_current[0]
        endpoint[:, 3] = source_current[0].sum()
        result = diagnostic.compare_membrane_current_balance(
            times,
            voltage,
            source_gates,
            source_currents,
            times[1:],
            voltage[1:],
            times[1:],
            stages,
            endpoint,
            injected_pa,
            114.47654963753565,
            29.045736151752504,
        )
        self.assertLess(
            result["source_voltage_update"]["capacitor_equation_residual"]["maximum_absolute_error_A_per_m2"],
            1.0e-12,
        )
        self.assertLess(
            result["humanjs_rk4_current_balance"]["weighted_capacitance_current_vs_weighted_stage_rhs"]["maximum_absolute_error_A_per_m2"],
            1.0e-12,
        )

    def test_source_order_replay_preserves_zero_current_reversal_state(self) -> None:
        voltage, gates = diagnostic.replay_wilbers_source_order(
            np.asarray([0.0, 0.02]),
            -70.0,
            np.zeros(5, dtype=float),
            0.0,
            114.47654963753565,
            29.045736151752504,
            None,
        )
        np.testing.assert_array_equal(voltage, np.asarray([-70.0, -70.0]))
        self.assertEqual(gates.shape, (2, 5))
        self.assertTrue(np.isfinite(gates).all())
        self.assertTrue(np.all((gates >= 0.0) & (gates <= 1.0)))

    def test_current_balance_rejects_misaligned_humanjs_timestamps(self) -> None:
        times = np.asarray([1.0, 1.02, 1.04], dtype=float)
        voltage = np.full(3, -70.0, dtype=float)
        gate_state = np.asarray([0.0244876225, 0.803433478, 0.03886289, 0.89016592, 0.89016592])
        source_gates = {
            name: np.full(3, gate_state[index], dtype=float)
            for index, name in enumerate(diagnostic.SOURCE_GATE_NAMES)
        }
        source_current = diagnostic._wilbers_current_density_a_per_m2(
            voltage, np.tile(gate_state, (3, 1)), 114.47654963753565, 29.045736151752504
        )
        injected_pa = float(source_current[0].sum() * np.pi * 100.0e-12 * 1.0e12)
        source_currents = {
            "ina": source_current[:, 0] / 10.0,
            "ik": source_current[:, 1] / 10.0,
            "i_pas": source_current[:, 2] / 10.0,
        }
        stages = np.zeros((2, 4, 5), dtype=float)
        stages[:, :, :3] = source_current[0]
        stages[:, :, 3] = source_current[0].sum()
        endpoint = np.zeros((2, 5), dtype=float)
        endpoint[:, :3] = source_current[0]
        endpoint[:, 3] = source_current[0].sum()
        with self.assertRaises(reproduction.ReproductionError):
            diagnostic.compare_membrane_current_balance(
                times,
                voltage,
                source_gates,
                source_currents,
                times[1:],
                voltage[1:],
                times[1:] + 0.001,
                stages,
                endpoint,
                injected_pa,
                114.47654963753565,
                29.045736151752504,
            )

    def test_rejects_malformed_gate_metric_shapes(self) -> None:
        with self.assertRaises(reproduction.ReproductionError):
            diagnostic._gate_path_metrics(
                np.zeros((3, 5), dtype=float),
                np.zeros((3, 4), dtype=float),
            )


if __name__ == "__main__":
    unittest.main()
