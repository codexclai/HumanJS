#!/usr/bin/env python3
"""Validate the tracked normalized-current replay against its fitting runner."""
from __future__ import annotations

import csv
import math
from pathlib import Path

import replay_wilbers_na_iv_current_fit as replay

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "research" / "HUMAN-L23-WILBERS-NA-IV-CURRENT-FIT-REPLAY.csv"
REQUIRED_PROVENANCE = (
    "615595a270c6170987757cd35743f5d5b5b2af0e",
    "b199d70c3d0e7a2e991fd8d26c54b1318e3c0970",
    "absolute-current gate",
    "not individual microscopic HH gate taus",
)


def main() -> None:
    text = CSV_PATH.read_text(encoding="utf-8")
    for marker in REQUIRED_PROVENANCE:
        if marker not in text:
            raise SystemExit(f"Missing replay provenance or limitation: {marker}")
    records = list(
        csv.DictReader(
            line for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    )
    expected = replay.replay_na_iv_current_fits()
    if len(records) != 19 or len(expected) != 19:
        raise SystemExit("Expected 19 Na_IV command-voltage rows")

    strict_fields = ("gate_tau_m_ms", "gate_tau_h_ms")
    fit_fields = (
        "preliminary_tau_m_ms", "preliminary_tau_h_ms",
        "joint_tau_m_ms", "joint_tau_h_ms",
        "r2_conditional_tau_m_ms", "r2_conditional_tau_h_ms",
    )
    r_squared_field = "joint_r_squared"
    for actual, reference in zip(records, expected, strict=True):
        voltage = float(actual["voltage_mv"])
        if voltage != reference["voltage_mv"]:
            raise SystemExit(f"Voltage-grid mismatch: {actual['voltage_mv']}")
        if int(actual["samples_fitted"]) != 997:
            raise SystemExit(f"Unexpected fitted sample count at {voltage:g} mV")
        for field in strict_fields:
            value = actual[field]
            ref_value = reference.get(field)
            if value == "" or ref_value is None or not math.isfinite(float(ref_value)):
                raise SystemExit(f"Missing finite {field} at {voltage:g} mV")
            if abs(float(value) - float(ref_value)) > 1.0e-12:
                raise SystemExit(f"{field} mismatch at {voltage:g} mV")

        # SciPy's bounded nonlinear fit can differ by sub-microsecond amounts
        # across hosted runners/BLAS builds. Keep the gate equations exact,
        # but bound fit-output drift to 2 microseconds in absolute tau units.
        for field in fit_fields:
            value = actual[field]
            ref_value = reference.get(field)
            if ref_value is None or not math.isfinite(float(ref_value)):
                if value != "":
                    raise SystemExit(f"Expected blank {field} at {voltage:g} mV")
            elif value == "" or abs(float(value) - float(ref_value)) > 2.0e-6:
                raise SystemExit(f"{field} mismatch at {voltage:g} mV")

        value = actual[r_squared_field]
        ref_value = reference.get(r_squared_field)
        if ref_value is None or not math.isfinite(float(ref_value)):
            if value != "":
                raise SystemExit(f"Expected blank {r_squared_field} at {voltage:g} mV")
        elif value == "" or abs(float(value) - float(ref_value)) > 2.0e-8:
            raise SystemExit(f"{r_squared_field} mismatch at {voltage:g} mV")
        if actual["passed_joint_fit_r2"] != str(bool(reference["passed_joint_fit_r2"])):
            raise SystemExit(f"R-squared pass flag mismatch at {voltage:g} mV")
        if actual["joint_tau_h_at_upper_bound"] != str(bool(reference["joint_tau_h_at_upper_bound"])):
            raise SystemExit(f"joint tau_h bound flag mismatch at {voltage:g} mV")

    passed = sum(bool(row["passed_joint_fit_r2"]) for row in expected)
    print(
        f"Validated 19 normalized Na_IV current-fit replay rows "
        f"({passed} passed joint-fit R-squared > 0.95), source hashes and caveats."
    )
    print(
        "The absolute-current gate remains untested; this is not an exact NEURON "
        "or experimental-current reproduction."
    )


if __name__ == "__main__":
    main()
