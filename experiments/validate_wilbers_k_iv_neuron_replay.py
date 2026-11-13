#!/usr/bin/env python3
"""Validate original NEURON K_IV and K_recovery source-protocol records."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_IV = ROOT / "research" / "HUMAN-L23-WILBERS-K-IV-NEURON-REPLAY.csv"
EXPECTED_RECOVERY = ROOT / "research" / "HUMAN-L23-WILBERS-K-RECOVERY-NEURON-REPLAY.csv"
SOURCE_HASHES = (
    "615595a270c6170987757cd35743f5d5b5b2af0e",
    "d299b3430ecda7a94f6d1c37ac76b2878052c7d5",
    "c819e59813acd70fae7af7151752bb1d8bbc7357",
)
IV_MARKERS = (
    "NEURON 9.0.2", "Temperature=34 C; dt=0.1 ms",
    "K_IV protocol: 20 ms at -140 mV", "(t>20.4)&(t<520)",
    "(t>520)&(t<570)", "fixed slow inactivation fit component is 450 ms",
    "no K tau CSVs or raw NWB K voltage-clamp traces",
)
RECOVERY_MARKERS = (
    "NEURON 9.0.2", "dt=0.5 ms",
    "K_recovery protocol: 2 ms at -120 mV; 5000 ms at +40 mV",
    "squared intervals 4..8464 ms", "get_double_tau_rec(rectimes,pulse2)",
    "apparent double-exponential current-fit parameters",
    "no raw human K NWB current traces",
)
IV_FIELDS = (
    "voltage_mv", "samples_activation_window",
    "activation_window_first_sample_ms", "activation_window_last_sample_ms",
    "samples_inactivation_window", "inactivation_window_first_sample_ms",
    "inactivation_window_last_sample_ms", "activation_current_max_ma_cm2",
    "inactivation_current_max_ma_cm2", "activation_gmax_source_units",
    "inactivation_gmax_source_units", "normalized_activation_gmax",
    "normalized_inactivation_gmax", "source_tau_activation_ms",
    "source_tau_inactivation_fast_ms", "source_tau_inactivation_fixed_slow_ms",
    "tau_activation_fit_attempted", "tau_inactivation_fit_attempted",
    "boltzmann_vhalf_activation_mv", "boltzmann_slope_activation_mv",
    "boltzmann_vhalf_inactivation_mv", "boltzmann_slope_inactivation_mv",
)
RECOVERY_FIELDS = (
    "recovery_voltage_mv", "recovery_interval_ms", "samples_test_window",
    "test_window_first_sample_ms", "test_window_last_sample_ms",
    "second_test_peak_current_ma_cm2", "source_double_exp_tau_fast_ms",
    "source_double_exp_tau_slow_ms", "source_fast_tau_finite",
    "source_slow_tau_finite",
)
IV_TOLERANCES = {
    "activation_current_max_ma_cm2": 2e-8,
    "inactivation_current_max_ma_cm2": 2e-8,
    "activation_gmax_source_units": 2e-8,
    "inactivation_gmax_source_units": 2e-8,
    "normalized_activation_gmax": 2e-8,
    "normalized_inactivation_gmax": 2e-8,
    "activation_window_first_sample_ms": 1e-9,
    "activation_window_last_sample_ms": 1e-9,
    "inactivation_window_first_sample_ms": 1e-9,
    "inactivation_window_last_sample_ms": 1e-9,
    "boltzmann_vhalf_activation_mv": 2e-5,
    "boltzmann_slope_activation_mv": 2e-5,
    "boltzmann_vhalf_inactivation_mv": 2e-5,
    "boltzmann_slope_inactivation_mv": 2e-5,
}
RECOVERY_TOLERANCES = {
    "test_window_first_sample_ms": 1e-8,
    "test_window_last_sample_ms": 1e-8,
    "second_test_peak_current_ma_cm2": 2e-8,
}
RECOVERY_INTERVALS_MS = (
    4.0, 144.0, 484.0, 1024.0, 1764.0,
    2704.0, 3844.0, 5184.0, 6724.0, 8464.0,
)


def read_table(path: Path) -> tuple[str, list[dict[str, str]]]:
    content = path.read_text(encoding="utf-8")
    rows = list(csv.DictReader(
        line for line in content.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ))
    return content, rows


def compare_float(actual: str, expected: str, tolerance: float, label: str) -> None:
    if expected == "":
        if actual != "":
            raise SystemExit(f"Expected blank {label}, received {actual!r}")
        return
    if actual == "":
        raise SystemExit(f"Expected finite {label}, received blank")
    value, reference = float(actual), float(expected)
    if not math.isfinite(value) or abs(value - reference) > tolerance:
        raise SystemExit(
            f"{label} mismatch: expected {reference:.12g}, got {value:.12g}; "
            f"tolerance={tolerance:g}"
        )


def check_provenance(expected_text: str, actual_text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in (*SOURCE_HASHES, *markers):
        if marker not in expected_text or marker not in actual_text:
            raise SystemExit(f"Missing {label} source provenance/protocol marker: {marker}")


def validate_iv(actual_path: Path):
    expected_text, expected = read_table(EXPECTED_IV)
    actual_text, actual = read_table(actual_path)
    check_provenance(expected_text, actual_text, IV_MARKERS, "K_IV")
    if len(expected) != 34 or len(actual) != 34:
        raise SystemExit(f"K_IV requires 34 rows, got {len(expected)} expected and {len(actual)} actual")
    if set(expected[0]) != set(IV_FIELDS) or set(actual[0]) != set(IV_FIELDS):
        raise SystemExit("K_IV CSV schema mismatch")

    activation_finite = 0
    inactivation_finite = 0
    boltzmann = None
    boltzmann_fields = (
        "boltzmann_vhalf_activation_mv", "boltzmann_slope_activation_mv",
        "boltzmann_vhalf_inactivation_mv", "boltzmann_slope_inactivation_mv",
    )
    for index, (ref, got) in enumerate(zip(expected, actual, strict=True)):
        voltage = -110.0 + 5.0 * index
        if float(got["voltage_mv"]) != voltage:
            raise SystemExit(f"K_IV voltage order mismatch at row {index}")
        if int(got["samples_activation_window"]) != 4996:
            raise SystemExit(f"K_IV activation mask count mismatch at {voltage:g} mV")
        if int(got["samples_inactivation_window"]) != 500:
            raise SystemExit(f"K_IV inactivation mask count mismatch at {voltage:g} mV")
        for field, tolerance in IV_TOLERANCES.items():
            compare_float(got[field], ref[field], tolerance, f"K_IV {field} at {voltage:g} mV")
        for field in ("tau_activation_fit_attempted", "tau_inactivation_fit_attempted"):
            if got[field] != ref[field]:
                raise SystemExit(f"K_IV {field} mismatch at {voltage:g} mV")
        for field in ("source_tau_activation_ms", "source_tau_inactivation_fast_ms"):
            if (got[field] == "") != (ref[field] == ""):
                raise SystemExit(f"K_IV fit availability mismatch for {field} at {voltage:g} mV")
        activation_value = got["source_tau_activation_ms"]
        if activation_value != "" and (
            not math.isfinite(float(activation_value)) or float(activation_value) <= 0.0
        ):
            raise SystemExit(f"K_IV source activation fit outside positive domain at {voltage:g} mV")
        fast_value = got["source_tau_inactivation_fast_ms"]
        slow_value = got["source_tau_inactivation_fixed_slow_ms"]
        if fast_value != "":
            fast_tau = float(fast_value)
            if not math.isfinite(fast_tau) or not 0.0 < fast_tau <= 300.0:
                raise SystemExit(f"K_IV source fast inactivation fit outside [0,300] ms at {voltage:g} mV")
            if float(slow_value) != 450.0:
                raise SystemExit(f"K_IV fixed slow inactivation component is not 450 ms at {voltage:g} mV")
        elif slow_value != "":
            raise SystemExit(f"K_IV fixed slow component present without accepted fast fit at {voltage:g} mV")
        activation_finite += activation_value != ""
        inactivation_finite += fast_value != ""
        current_boltzmann = tuple(float(got[field]) for field in boltzmann_fields)
        if boltzmann is None:
            boltzmann = current_boltzmann
        elif any(abs(a-b) > 1e-12 for a,b in zip(current_boltzmann, boltzmann, strict=True)):
            raise SystemExit("K_IV Boltzmann fit changed within the voltage series")

    if activation_finite != 32 or inactivation_finite != 27:
        raise SystemExit(
            f"Unexpected K_IV finite fits: activation={activation_finite}/34, "
            f"fast inactivation={inactivation_finite}/34"
        )
    return len(actual), activation_finite, inactivation_finite, boltzmann


def validate_recovery(actual_path: Path):
    expected_text, expected = read_table(EXPECTED_RECOVERY)
    actual_text, actual = read_table(actual_path)
    check_provenance(expected_text, actual_text, RECOVERY_MARKERS, "K_recovery")
    if len(expected) != 50 or len(actual) != 50:
        raise SystemExit(f"K_recovery requires 50 rows, got {len(expected)} expected and {len(actual)} actual")
    if set(expected[0]) != set(RECOVERY_FIELDS) or set(actual[0]) != set(RECOVERY_FIELDS):
        raise SystemExit("K_recovery CSV schema mismatch")

    fast_voltages: set[float] = set()
    slow_voltages: set[float] = set()
    for index, (ref, got) in enumerate(zip(expected, actual, strict=True)):
        voltage = -90.0 + 5.0 * (index // 10)
        interval = RECOVERY_INTERVALS_MS[index % 10]
        if float(got["recovery_voltage_mv"]) != voltage or float(got["recovery_interval_ms"]) != interval:
            raise SystemExit(f"K_recovery command order mismatch at row {index}")
        if int(got["samples_test_window"]) != 9:
            raise SystemExit(f"K_recovery source-window count mismatch at {voltage:g} mV / {interval:g} ms")
        for field, tolerance in RECOVERY_TOLERANCES.items():
            compare_float(got[field], ref[field], tolerance, f"K_recovery {field} at {voltage:g} mV / {interval:g} ms")
        for field in ("source_fast_tau_finite", "source_slow_tau_finite"):
            if got[field] != ref[field]:
                raise SystemExit(f"K_recovery {field} mismatch at {voltage:g} mV / {interval:g} ms")
        fast_value = got["source_double_exp_tau_fast_ms"]
        slow_value = got["source_double_exp_tau_slow_ms"]
        if got["source_fast_tau_finite"] == "True":
            fast_tau = float(fast_value)
            if not math.isfinite(fast_tau) or not 0.0 < fast_tau < 1000.0:
                raise SystemExit(f"K_recovery fast fit violates original (0,1000) ms bounds at {voltage:g} mV")
            fast_voltages.add(voltage)
        elif fast_value != "":
            raise SystemExit(f"K_recovery non-finite fast fit was serialized at {voltage:g} mV")
        if got["source_slow_tau_finite"] == "True":
            slow_tau = float(slow_value)
            if not math.isfinite(slow_tau) or not 1000.0 <= slow_tau <= 5000.0:
                raise SystemExit(f"K_recovery slow fit violates original [1000,5000] ms bounds at {voltage:g} mV")
            slow_voltages.add(voltage)
        elif slow_value != "":
            raise SystemExit(f"K_recovery non-finite slow fit was serialized at {voltage:g} mV")
        # Both fit parameters are repeated on every delay row for the same
        # recovery voltage; retain the recorded value, but require a constant
        # per-voltage fit throughout that ten-point recovery curve.
        group_start = (index // 10) * 10
        if index % 10:
            prior = actual[group_start]
            for field in ("source_double_exp_tau_fast_ms", "source_double_exp_tau_slow_ms"):
                if got[field] != prior[field]:
                    raise SystemExit(f"K_recovery {field} changes within {voltage:g} mV delay series")

    if len(fast_voltages) != 5 or len(slow_voltages) != 5:
        raise SystemExit("K_recovery expected finite fast/slow fits at all 5 voltages")
    return len(actual), len(fast_voltages), len(slow_voltages)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iv-actual", type=Path, required=True)
    parser.add_argument("--recovery-actual", type=Path, required=True)
    args = parser.parse_args()
    iv_count, act_count, inact_count, boltzmann = validate_iv(args.iv_actual)
    rec_count, rec_fast, rec_slow = validate_recovery(args.recovery_actual)
    print(
        f"Validated original NEURON K_IV replay: {iv_count}/34 commands; "
        f"{act_count}/34 finite activation fits; {inact_count}/34 finite fast-inactivation fits; "
        f"activation Vhalf/slope={boltzmann[0]:.6g}/{boltzmann[1]:.6g} mV; "
        f"inactivation Vhalf/slope={boltzmann[2]:.6g}/{boltzmann[3]:.6g} mV."
    )
    print(
        f"Validated original NEURON K_recovery replay: {rec_count}/50 traces; "
        f"{rec_fast}/5 finite fast and {rec_slow}/5 finite slow source fits."
    )
    print("Source/model execution only; no raw human K current traces or biological validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
