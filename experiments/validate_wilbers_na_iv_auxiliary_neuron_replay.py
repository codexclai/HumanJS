#!/usr/bin/env python3
"""Validate original NEURON Na_IV_inact and Na_recovery source-protocol runs."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INACTIVATION_EXPECTED = ROOT / "research" / "HUMAN-L23-WILBERS-NA-IV-INACT-NEURON-REPLAY.csv"
RECOVERY_EXPECTED = ROOT / "research" / "HUMAN-L23-WILBERS-NA-RECOVERY-NEURON-REPLAY.csv"
SOURCE_HASHES = (
    "615595a270c6170987757cd35743f5d5b5b2af0e",
    "b199d70c3d0e7a2e991fd8d26c54b1318e3c0970",
    "3fac7eb5d25c2e02f6a3530d746de292548ef368",
)
INACTIVATION_MARKERS = (
    "NEURON 9.0.2",
    "dt=0.005 ms",
    "30 conditioning voltages -105..-47 mV",
    "(t>51)&(t<55)",
    "source_denominator",
    "not experimental current measurements",
)
RECOVERY_MARKERS = (
    "NEURON 9.0.2",
    "dt=0.02 ms",
    "recovery intervals 1^2..12^2 ms",
    "(12+recovery_time, 14+recovery_time)",
    "get_tau_act(rectimes,pulse2,est=15)",
    "not experimental data",
)
INACTIVATION_FIELDS = (
    "conditioning_voltage_mv",
    "samples_fitted",
    "test_window_first_sample_ms",
    "test_window_last_sample_ms",
    "test_current_min_ma_cm2",
    "test_current_max_ma_cm2",
    "source_denominator",
    "source_ggmax_value",
    "normalized_ggmax",
    "boltzmann_vhalf_mv",
    "boltzmann_slope_mv",
)
RECOVERY_FIELDS = (
    "recovery_voltage_mv",
    "recovery_interval_ms",
    "samples_fitted",
    "test_window_first_sample_ms",
    "test_window_last_sample_ms",
    "second_test_current_peak_magnitude_ma_cm2",
    "apparent_recovery_tau_ms",
    "source_returned_finite_tau",
)


def read_table(path: Path) -> tuple[str, list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8")
    rows = list(
        csv.DictReader(
            line for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    )
    return text, rows


def finite_or_blank(actual: str, expected: str, tolerance: float, label: str) -> None:
    if expected == "":
        if actual != "":
            raise SystemExit(f"Expected blank {label}, received {actual!r}")
        return
    if actual == "":
        raise SystemExit(f"Expected finite {label}, received blank")
    value = float(actual)
    reference = float(expected)
    if not math.isfinite(value) or abs(value - reference) > tolerance:
        raise SystemExit(
            f"{label} mismatch: expected {reference:.12g}, got {value:.12g}, "
            f"tolerance {tolerance:g}"
        )


def validate_inactivation(actual_path: Path) -> tuple[int, float, float]:
    expected_text, expected_rows = read_table(INACTIVATION_EXPECTED)
    actual_text, actual_rows = read_table(actual_path)
    for marker in (*SOURCE_HASHES, *INACTIVATION_MARKERS):
        if marker not in expected_text or marker not in actual_text:
            raise SystemExit(f"Missing Na_IV_inact provenance/protocol marker: {marker}")
    if len(expected_rows) != 30 or len(actual_rows) != 30:
        raise SystemExit(
            f"Na_IV_inact requires 30 rows, got {len(expected_rows)} expected and {len(actual_rows)} actual"
        )
    if set(expected_rows[0]) != set(INACTIVATION_FIELDS) or set(actual_rows[0]) != set(INACTIVATION_FIELDS):
        raise SystemExit("Na_IV_inact CSV schema mismatch")

    for index, (expected, actual) in enumerate(zip(expected_rows, actual_rows, strict=True)):
        voltage = -105.0 + 2.0 * index
        if float(actual["conditioning_voltage_mv"]) != voltage:
            raise SystemExit(f"Na_IV_inact voltage order mismatch at row {index}")
        sample_count = int(actual["samples_fitted"])
        if sample_count not in (799, 800, 801):
            raise SystemExit(f"Na_IV_inact sample-count mismatch at {voltage:g} mV")
        finite_or_blank(actual["test_window_first_sample_ms"], expected["test_window_first_sample_ms"], 1.0e-9, f"Na_IV_inact first sample time at {voltage:g} mV")
        finite_or_blank(actual["test_window_last_sample_ms"], expected["test_window_last_sample_ms"], 1.0e-9, f"Na_IV_inact last sample time at {voltage:g} mV")
        finite_or_blank(actual["test_current_min_ma_cm2"], expected["test_current_min_ma_cm2"], 2.0e-10, f"Na_IV_inact current minimum at {voltage:g} mV")
        finite_or_blank(actual["test_current_max_ma_cm2"], expected["test_current_max_ma_cm2"], 2.0e-10, f"Na_IV_inact current maximum at {voltage:g} mV")
        finite_or_blank(actual["source_denominator"], expected["source_denominator"], 1.0e-6, f"Na_IV_inact source denominator at {voltage:g} mV")
        finite_or_blank(actual["source_ggmax_value"], expected["source_ggmax_value"], max(1.0e-15, abs(float(expected["source_ggmax_value"])) * 1.0e-8), f"Na_IV_inact source Gmax at {voltage:g} mV")
        finite_or_blank(actual["normalized_ggmax"], expected["normalized_ggmax"], 2.0e-8, f"Na_IV_inact normalized Gmax at {voltage:g} mV")
        finite_or_blank(actual["boltzmann_vhalf_mv"], expected["boltzmann_vhalf_mv"], 2.0e-5, f"Na_IV_inact Vhalf at {voltage:g} mV")
        finite_or_blank(actual["boltzmann_slope_mv"], expected["boltzmann_slope_mv"], 2.0e-5, f"Na_IV_inact slope at {voltage:g} mV")

    vhalf = expected_rows[0]["boltzmann_vhalf_mv"]
    slope = expected_rows[0]["boltzmann_slope_mv"]
    return len(actual_rows), float(vhalf) if vhalf else math.nan, float(slope) if slope else math.nan


def validate_recovery(actual_path: Path) -> tuple[int, int]:
    expected_text, expected_rows = read_table(RECOVERY_EXPECTED)
    actual_text, actual_rows = read_table(actual_path)
    for marker in (*SOURCE_HASHES, *RECOVERY_MARKERS):
        if marker not in expected_text or marker not in actual_text:
            raise SystemExit(f"Missing Na_recovery provenance/protocol marker: {marker}")
    if len(expected_rows) != 156 or len(actual_rows) != 156:
        raise SystemExit(
            f"Na_recovery requires 156 rows, got {len(expected_rows)} expected and {len(actual_rows)} actual"
        )
    if set(expected_rows[0]) != set(RECOVERY_FIELDS) or set(actual_rows[0]) != set(RECOVERY_FIELDS):
        raise SystemExit("Na_recovery CSV schema mismatch")

    finite_tau_voltages: set[float] = set()
    index = 0
    for voltage in range(-90, -65, 2):
        for recovery_index, recovery_time in enumerate(range(1, 13)):
            recovery_time_ms = float(recovery_time * recovery_time)
            expected = expected_rows[index]
            actual = actual_rows[index]
            index += 1
            if float(actual["recovery_voltage_mv"]) != float(voltage):
                raise SystemExit(f"Na_recovery voltage order mismatch at row {index - 1}")
            if float(actual["recovery_interval_ms"]) != recovery_time_ms:
                raise SystemExit(f"Na_recovery interval mismatch at {voltage} mV / {recovery_time_ms:g} ms")
            sample_count = int(actual["samples_fitted"])
            if sample_count not in (99, 100, 101):
                raise SystemExit(f"Na_recovery sample-count mismatch at {voltage} mV / {recovery_time_ms:g} ms")
            finite_or_blank(actual["test_window_first_sample_ms"], expected["test_window_first_sample_ms"], 1.0e-9, f"Na_recovery first sample time at {voltage} mV / {recovery_time_ms:g} ms")
            finite_or_blank(actual["test_window_last_sample_ms"], expected["test_window_last_sample_ms"], 1.0e-9, f"Na_recovery last sample time at {voltage} mV / {recovery_time_ms:g} ms")
            finite_or_blank(
                actual["second_test_current_peak_magnitude_ma_cm2"],
                expected["second_test_current_peak_magnitude_ma_cm2"],
                2.0e-10,
                f"Na_recovery second-pulse peak at {voltage} mV / {recovery_time_ms:g} ms",
            )
            if actual["source_returned_finite_tau"] != expected["source_returned_finite_tau"]:
                raise SystemExit(f"Na_recovery fit-availability mismatch at {voltage} mV")
            finite_or_blank(
                actual["apparent_recovery_tau_ms"],
                expected["apparent_recovery_tau_ms"],
                2.0e-5,
                f"Na_recovery apparent tau at {voltage} mV",
            )
            if actual["source_returned_finite_tau"] == "True":
                finite_tau_voltages.add(float(voltage))
    return len(actual_rows), len(finite_tau_voltages)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inactivation-actual", type=Path, required=True)
    parser.add_argument("--recovery-actual", type=Path, required=True)
    args = parser.parse_args()
    inactivation_count, vhalf, slope = validate_inactivation(args.inactivation_actual)
    recovery_count, finite_tau_count = validate_recovery(args.recovery_actual)
    print(
        f"Validated NEURON Na_IV_inact: {inactivation_count}/30 conditioning voltages, "
        f"Boltzmann Vhalf={vhalf:.6g} mV, slope={slope:.6g} mV."
    )
    print(
        f"Validated NEURON Na_recovery: {recovery_count}/156 paired-pulse traces; "
        f"{finite_tau_count}/13 voltages returned finite source recovery taus."
    )
    print("Original NMODL and source fitting helpers executed; no raw experimental current or biological validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
