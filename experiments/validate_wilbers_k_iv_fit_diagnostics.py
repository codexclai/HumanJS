#!/usr/bin/env python3
"""Validate same-waveform multi-start diagnostics for the Wilbers K_IV fit."""
from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

from wilbers_k_iv_fit_diagnostics import (
    K_IV_FIT_DIAGNOSTIC_FIELDNAMES,
    K_IV_SOURCE_R2_THRESHOLD,
)

STARTS = (
    "source_literal",
    "tau30_equal_amplitudes",
    "tau100_equal_amplitudes",
    "tau200_equal_amplitudes",
    "tau100_slow25pct",
    "tau100_slow75pct",
)


def read_csv(path: Path) -> tuple[str, list[dict[str, str]]]:
    content = path.read_text(encoding="utf-8")
    rows = list(csv.DictReader(
        line for line in content.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ))
    if not rows:
        raise SystemExit(f"No CSV rows found in {path}")
    return content, rows


def finite(value: str, label: str) -> float:
    if value == "":
        raise SystemExit(f"Expected finite {label}, received blank")
    number = float(value)
    if not math.isfinite(number):
        raise SystemExit(f"Expected finite {label}, received {number}")
    return number


def parse_bool(value: str, label: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise SystemExit(f"Invalid boolean for {label}: {value!r}")


def validate(actual_path: Path, source_iv_path: Path) -> None:
    _, diagnostic_rows = read_csv(actual_path)
    _, source_iv_rows = read_csv(source_iv_path)

    if set(diagnostic_rows[0]) != set(K_IV_FIT_DIAGNOSTIC_FIELDNAMES):
        raise SystemExit("K_IV fit diagnostic CSV schema mismatch")
    if len(source_iv_rows) != 34:
        raise SystemExit(f"Expected 34 source K_IV rows, got {len(source_iv_rows)}")

    source_by_voltage: dict[float, dict[str, str]] = {}
    for row in source_iv_rows:
        voltage = float(row["voltage_mv"])
        if voltage in source_by_voltage:
            raise SystemExit(f"Duplicate source K_IV voltage {voltage:g} mV")
        source_by_voltage[voltage] = row

    expected_voltages = {
        voltage for voltage, row in source_by_voltage.items()
        if parse_bool(row["tau_inactivation_fit_attempted"], "source fit attempted")
    }
    grouped: dict[float, list[dict[str, str]]] = defaultdict(list)
    for row in diagnostic_rows:
        voltage = float(row["voltage_mv"])
        if voltage not in expected_voltages:
            raise SystemExit(f"Unexpected diagnostic voltage {voltage:g} mV")
        grouped[voltage].append(row)

    if set(grouped) != expected_voltages:
        missing = sorted(expected_voltages - set(grouped))
        raise SystemExit(f"Missing K_IV diagnostic voltages: {missing}")

    accepted_spread_by_voltage: list[float] = []
    fit_counts = {name: 0 for name in STARTS}
    accepted_counts = {name: 0 for name in STARTS}
    fitted_taus: dict[str, list[float]] = {name: [] for name in STARTS}
    source_literal_checked = 0

    for voltage in sorted(expected_voltages):
        rows = grouped[voltage]
        by_start = {row["initialization"]: row for row in rows}
        if len(rows) != len(STARTS) or set(by_start) != set(STARTS):
            raise SystemExit(
                f"Expected exactly {len(STARTS)} named fit starts at {voltage:g} mV"
            )

        source_record = source_by_voltage[voltage]
        helper_tau_text = source_record["source_tau_inactivation_fast_ms"]

        for name in STARTS:
            row = by_start[name]
            fit_counts[name] += 1
            helper_value = row["source_helper_tau_fast_ms"]
            if helper_tau_text == "":
                if helper_value != "":
                    raise SystemExit(
                        f"Source helper tau disagreement at {voltage:g} mV for {name}"
                    )
            else:
                source_tau = finite(helper_tau_text, "source helper tau")
                observed_tau = finite(helper_value, "diagnostic source helper tau")
                if abs(source_tau - observed_tau) > 1e-10:
                    raise SystemExit(
                        f"Source helper tau changed within diagnostics at {voltage:g} mV"
                    )

            delta = finite(row["source_delta_current_ma_cm2"], "source current delta")
            initial_a1 = finite(
                row["initial_fast_amplitude_ma_cm2"], "initial fast amplitude"
            )
            initial_tau = finite(row["initial_tau1_value"], "initial tau1")
            initial_a2 = finite(
                row["initial_slow_amplitude_ma_cm2"], "initial slow amplitude"
            )
            initial_offset = finite(row["initial_offset_ma_cm2"], "initial offset")
            if min(initial_a1, initial_a2, initial_offset) < 0.0:
                raise SystemExit(f"Negative bounded initial amplitude at {voltage:g} mV")

            if name == "source_literal":
                for value, expected, label in (
                    (initial_a1, 0.5 * delta, "a1"),
                    (initial_tau, 0.5 * delta, "tau1"),
                    (initial_a2, 30.0, "a2/default est1"),
                ):
                    if abs(value - expected) > 1e-12:
                        raise SystemExit(
                            f"Original helper p0 {label} was not preserved at {voltage:g} mV"
                        )
                source_literal_checked += 1
            else:
                expected_tau, expected_slow_fraction = {
                    "tau30_equal_amplitudes": (30.0, 0.50),
                    "tau100_equal_amplitudes": (100.0, 0.50),
                    "tau200_equal_amplitudes": (200.0, 0.50),
                    "tau100_slow25pct": (100.0, 0.25),
                    "tau100_slow75pct": (100.0, 0.75),
                }[name]
                if initial_tau != expected_tau:
                    raise SystemExit(f"Alternative tau1 start changed for {name}")
                total_amplitude = initial_a1 + initial_a2
                if total_amplitude <= 0.0:
                    raise SystemExit(f"Non-positive initial amplitude sum for {name}")
                fraction = initial_a2 / total_amplitude
                if abs(fraction - expected_slow_fraction) > 1e-10:
                    raise SystemExit(f"Alternative amplitude split changed for {name}")

            converged = parse_bool(row["fit_converged"], "fit_converged")
            passed_gate = parse_bool(
                row["fit_passes_source_r2_gate"], "fit_passes_source_r2_gate"
            )
            if converged:
                tau = finite(row["fit_tau_fast_ms"], "fitted fast tau")
                _ = finite(row["fit_fast_amplitude_ma_cm2"], "fitted fast amplitude")
                _ = finite(row["fit_slow_amplitude_ma_cm2"], "fitted slow amplitude")
                _ = finite(row["fit_offset_ma_cm2"], "fitted offset")
                r_squared = finite(row["fit_r_squared"], "fit R-squared")
                _ = finite(row["fit_rmse_ma_cm2"], "fit RMSE")
                if not 0.0 < tau <= 300.0:
                    raise SystemExit(f"Fitted tau outside (0,300] ms at {voltage:g} mV")
                if passed_gate != (r_squared > K_IV_SOURCE_R2_THRESHOLD):
                    raise SystemExit(f"Source R-squared gate mismatch at {voltage:g} mV")
                if row["fit_error_type"] != "":
                    raise SystemExit(f"Converged fit carries error type at {voltage:g} mV")
                fit_counts[name] += 0
                fitted_taus[name].append(tau)
                accepted_counts[name] += int(passed_gate)
            else:
                if passed_gate:
                    raise SystemExit(f"Failed fit cannot pass R-squared gate at {voltage:g} mV")
                if row["fit_error_type"] == "":
                    raise SystemExit(f"Failed fit missing error type at {voltage:g} mV")
                for field in (
                    "fit_tau_fast_ms", "fit_fast_amplitude_ma_cm2",
                    "fit_slow_amplitude_ma_cm2", "fit_offset_ma_cm2",
                    "fit_r_squared", "fit_rmse_ma_cm2",
                ):
                    if row[field] != "":
                        raise SystemExit(f"Failed fit serialized {field} at {voltage:g} mV")

        source_fit = by_start["source_literal"]
        if helper_tau_text != "":
            if not (
                parse_bool(source_fit["fit_converged"], "source literal converged")
                and parse_bool(source_fit["fit_passes_source_r2_gate"], "source literal gate")
            ):
                raise SystemExit(
                    f"Source helper accepted a fit that source_literal did not at {voltage:g} mV"
                )
            diagnostic_tau = finite(source_fit["fit_tau_fast_ms"], "source literal tau")
            if abs(diagnostic_tau - float(helper_tau_text)) > 1e-7:
                raise SystemExit(
                    f"source_literal fit does not reproduce helper tau at {voltage:g} mV"
                )

        passing = [
            finite(row["fit_tau_fast_ms"], "accepted fit tau")
            for row in rows
            if parse_bool(row["fit_passes_source_r2_gate"], "fit gate")
        ]
        if len(passing) >= 2:
            accepted_spread_by_voltage.append(max(passing) - min(passing))

    if source_literal_checked != len(expected_voltages):
        raise SystemExit("Not all source literal initializations were checked")

    print(
        f"Validated K_IV fit diagnostics: {len(diagnostic_rows)} rows; "
        f"{len(expected_voltages)} attempted voltages; six initializations per voltage; "
        f"source helper p0 reproduced at all {source_literal_checked} voltages."
    )
    for name in STARTS:
        values = fitted_taus[name]
        if values:
            print(
                f"{name}: {len(values)}/{fit_counts[name]} converged; "
                f"{accepted_counts[name]} passed source R2>0.95; "
                f"accepted tau range={min(values):.6g}..{max(values):.6g} ms."
            )
        else:
            print(f"{name}: no converged fits.")
    if accepted_spread_by_voltage:
        print(
            "Within-voltage accepted multi-start tau spread: "
            f"max={max(accepted_spread_by_voltage):.6g} ms over "
            f"{len(accepted_spread_by_voltage)} voltages with at least two accepted starts."
        )
    minus70 = grouped.get(-70.0, [])
    if minus70:
        print("−70 mV same-waveform fit starts:")
        for row in minus70:
            tau = row["fit_tau_fast_ms"] or "failed"
            r2 = row["fit_r_squared"] or "n/a"
            print(
                f"  {row['initialization']}: tau={tau} ms; "
                f"R2={r2}; converged={row['fit_converged']}"
            )
    print(
        "These are numerical optimizer-start counterfactuals on the deposited model, "
        "not fits to experimental human K-current traces or biological validation."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--source-iv", type=Path, required=True)
    args = parser.parse_args()
    validate(args.actual, args.source_iv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
