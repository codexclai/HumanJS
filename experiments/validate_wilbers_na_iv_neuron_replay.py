#!/usr/bin/env python3
"""Compare the real NEURON/VClamp Na_IV run to its pinned research record."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "research" / "HUMAN-L23-WILBERS-NA-IV-NEURON-REPLAY.csv"
SOURCE_HASHES = (
    "615595a270c6170987757cd35743f5d5b5b2af0e",
    "b199d70c3d0e7a2e991fd8d26c54b1318e3c0970",
    "3fac7eb5d25c2e02f6a3530d746de292548ef368",
)
REQUIRED_TEXT = (
    "NEURON 9.0.2",
    "rstim=1 MOhm",
    "gain=100000",
    "secondorder=0.0",
    "original channel_tools.runIna",
    "not experimental current data",
)
EXPECTED_FIELDS = (
    "voltage_mv",
    "samples_fitted",
    "source_ina_min_ma_cm2",
    "source_current_density_gate_passed",
    "preliminary_tau_m_ms",
    "preliminary_tau_h_ms",
    "joint_tau_m_ms",
    "joint_tau_h_ms",
    "source_mapped_tau_m_ms",
    "source_mapped_tau_h_ms",
    "joint_r_squared",
    "passed_joint_fit_r2",
    "joint_tau_h_at_upper_bound",
)
FIT_TAU_FIELDS = (
    "preliminary_tau_m_ms",
    "preliminary_tau_h_ms",
    "joint_tau_m_ms",
    "joint_tau_h_ms",
    "source_mapped_tau_m_ms",
    "source_mapped_tau_h_ms",
)
R2_FIELDS = ("joint_r_squared",)


def read_table(path: Path) -> tuple[str, list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8")
    records = list(
        csv.DictReader(
            line for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    )
    return text, records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual", type=Path, required=True)
    args = parser.parse_args()
    expected_text, expected_rows = read_table(EXPECTED)
    actual_text, actual_rows = read_table(args.actual)

    for marker in (*SOURCE_HASHES, *REQUIRED_TEXT):
        if marker not in expected_text or marker not in actual_text:
            raise SystemExit(f"Missing NEURON replay provenance/configuration: {marker}")
    if len(expected_rows) != 19 or len(actual_rows) != 19:
        raise SystemExit(
            f"Expected 19 rows in both NEURON replay files, got "
            f"{len(expected_rows)} reference and {len(actual_rows)} actual"
        )
    if set(expected_rows[0]) != set(EXPECTED_FIELDS) or set(actual_rows[0]) != set(EXPECTED_FIELDS):
        raise SystemExit("NEURON replay CSV schema differs from expected columns")

    density_gate_count = 0
    r2_pass_count = 0
    for expected, actual in zip(expected_rows, actual_rows, strict=True):
        voltage = float(expected["voltage_mv"])
        if float(actual["voltage_mv"]) != voltage:
            raise SystemExit(f"Voltage order mismatch at row {voltage:g} mV")
        if int(actual["samples_fitted"]) != 997:
            raise SystemExit(f"Unexpected sample count at {voltage:g} mV")
        for field in ("source_current_density_gate_passed", "passed_joint_fit_r2", "joint_tau_h_at_upper_bound"):
            if actual[field] != expected[field]:
                raise SystemExit(f"{field} mismatch at {voltage:g} mV")

        density_gate_count += actual["source_current_density_gate_passed"] == "True"
        r2_pass_count += actual["passed_joint_fit_r2"] == "True"

        for field in ("source_ina_min_ma_cm2",):
            actual_value = float(actual[field])
            expected_value = float(expected[field])
            if not math.isfinite(actual_value) or abs(actual_value - expected_value) > 2.0e-10:
                raise SystemExit(f"{field} mismatch at {voltage:g} mV")
        for field in FIT_TAU_FIELDS:
            actual_value = actual[field]
            expected_value = expected[field]
            if expected_value == "":
                if actual_value != "":
                    raise SystemExit(f"Expected blank {field} at {voltage:g} mV")
            elif actual_value == "" or abs(float(actual_value) - float(expected_value)) > 2.0e-6:
                raise SystemExit(f"{field} mismatch at {voltage:g} mV")
        for field in R2_FIELDS:
            actual_value = actual[field]
            expected_value = expected[field]
            if expected_value == "":
                if actual_value != "":
                    raise SystemExit(f"Expected blank {field} at {voltage:g} mV")
            elif actual_value == "" or abs(float(actual_value) - float(expected_value)) > 2.0e-8:
                raise SystemExit(f"{field} mismatch at {voltage:g} mV")

    if density_gate_count != 19 or r2_pass_count != 17:
        raise SystemExit(
            f"Unexpected source-fit acceptance counts: {density_gate_count}/19 density, "
            f"{r2_pass_count}/19 joint fit"
        )
    print(
        "Validated actual NEURON 9.0.2 VClamp replay: 19/19 passed source current-density selection; "
        "17/19 passed joint-fit R² > 0.95; 19 rows, file hashes and VClamp configuration verified."
    )
    print(
        "This verifies deposited model/source-code execution only; no raw experimental current traces or biological validation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
