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
    read_postpeak_waveforms,
    validate_summary_rows,
)


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
        self.assertLess(result["corrected_full_rmse_ma_cm2"], result["baseline_full_rmse_ma_cm2"])
        self.assertLess(result["full_improvement_pct"], 100.0)
        self.assertGreater(result["full_improvement_pct"], 50.0)
        self.assertAlmostEqual(result["tau3_ms"], 1.23, delta=0.1)

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
        for voltage, (times, source_times, currents) in waveforms.items():
            self.assertEqual(len(times), 100)
            self.assertAlmostEqual(float(source_times[0]), 30.9)
            self.assertAlmostEqual(float(times[-1]), 9.9)
            self.assertEqual(len(currents), 100)

    def test_rejects_clock_misalignment_and_nonmonotone_time(self) -> None:
        times = np.arange(0.0, 120.0, 0.1)
        currents = 4.0e-4 + 1.0e-5 * np.exp(-times / 20.0)
        with self.assertRaises(ValueError):
            analyze_k_iv_waveform(-70.0, times, times + 31.0, currents)
        invalid_times = times.copy()
        invalid_times[40] = invalid_times[39]
        with self.assertRaises(ValueError):
            analyze_k_iv_waveform(-70.0, invalid_times, invalid_times + 30.9, currents)


if __name__ == "__main__":
    unittest.main()
