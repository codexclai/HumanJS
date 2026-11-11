#!/usr/bin/env python3
"""Validate provenance, axis calibration, and values in digitized Wilbers Figure S5 K+ panels."""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA256 = "dfa1daaf4dd0e3979bac84b9cb8b1874c4514d40588969a21d7766a7f12f2a1d"
SPECIES_MARKERS = {"human": "red_open_circle", "mouse": "blue_cross"}


def close(actual: float, expected: float, tolerance: float) -> bool:
    return math.isfinite(actual) and abs(actual - expected) <= tolerance


def read_rows(filename: str) -> tuple[str, list[dict[str, str]]]:
    text = (ROOT / "research" / filename).read_text(encoding="utf-8")
    if EXPECTED_SHA256 not in text:
        raise SystemExit(f"{filename}: source PDF SHA-256 provenance is missing")
    rows = list(csv.DictReader(line for line in text.splitlines() if not line.startswith("#")))
    return text, rows


def validate_panel(
    *,
    filename: str,
    tau_column: str,
    tau_uncertainty_column: str,
    expected_voltages: list[float],
    x_reference_pixel: float,
    x_reference_mv: float,
    x_pixels_per_mv: float,
    y_reference_pixel: float,
    y_reference_value: float,
    y_second_pixel: float,
    y_second_value: float,
    voltage_uncertainty: float,
    tau_uncertainty: float,
    voltage_tolerance: float,
    tau_tolerance: float,
    tau_bounds: tuple[float, float],
) -> tuple[float, float, int]:
    _, rows = read_rows(filename)
    expected_count = len(expected_voltages) * len(SPECIES_MARKERS)
    if len(rows) != expected_count:
        raise SystemExit(f"{filename}: expected {expected_count} markers, found {len(rows)}")
    counts = Counter(row["species"] for row in rows)
    expected_counts = Counter({species: len(expected_voltages) for species in SPECIES_MARKERS})
    if counts != expected_counts:
        raise SystemExit(f"{filename}: unexpected marker counts: {dict(counts)}")

    max_voltage_error = 0.0
    max_tau_error = 0.0
    for species, expected_marker in SPECIES_MARKERS.items():
        selected = [row for row in rows if row["species"] == species]
        voltages = [float(row["voltage_mV"]) for row in selected]
        if voltages != expected_voltages:
            raise SystemExit(f"{filename}: {species} voltage grid is incorrect")
        for row in selected:
            x_pixel = float(row["x_pixel_crop"])
            y_pixel = float(row["y_pixel_crop"])
            voltage = float(row["voltage_mV"])
            tau = float(row[tau_column])
            derived_voltage = x_reference_mv + (
                x_pixel - x_reference_pixel
            ) / x_pixels_per_mv
            derived_tau = y_reference_value + (
                y_pixel - y_reference_pixel
            ) * (y_second_value - y_reference_value) / (
                y_second_pixel - y_reference_pixel
            )
            max_voltage_error = max(max_voltage_error, abs(derived_voltage - voltage))
            max_tau_error = max(max_tau_error, abs(derived_tau - tau))
            if not close(derived_voltage, voltage, voltage_tolerance):
                raise SystemExit(f"{filename}: voltage calibration mismatch: {row}")
            if not close(derived_tau, tau, tau_tolerance):
                raise SystemExit(f"{filename}: time-constant calibration mismatch: {row}")
            if row["marker"] != expected_marker:
                raise SystemExit(f"{filename}: marker/species mismatch: {row}")
            if float(row["voltage_digitization_uncertainty_mV"]) != voltage_uncertainty:
                raise SystemExit(f"{filename}: voltage uncertainty missing or changed: {row}")
            if float(row[tau_uncertainty_column]) != tau_uncertainty:
                raise SystemExit(f"{filename}: time-constant uncertainty missing or changed: {row}")
            if not (tau_bounds[0] < tau < tau_bounds[1]):
                raise SystemExit(f"{filename}: implausible plotted time constant: {row}")
    return max_voltage_error, max_tau_error, len(rows)


def validate_source_marker_values(
    *,
    filename: str,
    tau_column: str,
    tau_uncertainty_column: str,
    expected_values: dict[str, float],
) -> int:
    _, rows = read_rows(filename)
    if len(rows) != len(expected_values):
        raise SystemExit(f"{filename}: expected {len(expected_values)} source marker values, found {len(rows)}")
    for row in rows:
        species = row["species"]
        if species not in expected_values:
            raise SystemExit(f"{filename}: unexpected species: {species}")
        if float(row["voltage_mV"]) != -80.0:
            raise SystemExit(f"{filename}: recovery marker voltage is not -80 mV: {row}")
        if row["marker"] != SPECIES_MARKERS[species]:
            raise SystemExit(f"{filename}: marker/species mismatch: {row}")
        if row["value_provenance"] != "channel_tools.K_IV":
            raise SystemExit(f"{filename}: value is not attributed to deposited channel_tools.K_IV: {row}")
        if abs(float(row[tau_column]) - expected_values[species]) > 1.0e-9:
            raise SystemExit(f"{filename}: source-code recovery value mismatch: {row}")
        if float(row["voltage_digitization_uncertainty_mV"]) != 0.0:
            raise SystemExit(f"{filename}: exact source value should not be labelled plot-digitized: {row}")
        if float(row[tau_uncertainty_column]) != 0.0:
            raise SystemExit(f"{filename}: exact source value should not be labelled plot-digitized: {row}")
    if {row["species"] for row in rows} != set(expected_values):
        raise SystemExit(f"{filename}: one or more species source values are missing")
    print(f"{filename}: {len(rows)} exact experimental marker values transcribed from channel_tools.K_IV")
    return len(rows)


def validate_mouse_model_prefit_check() -> None:
    filename = "HUMAN-L23-WILBERS-FIG-S5-I-MOUSE-MODEL-PREFIT-CHECK.csv"
    _, rows = read_rows(filename)
    expected_voltages = [-5.0, 5.0, 15.0, 25.0, 35.0, 45.0]
    if len(rows) != len(expected_voltages):
        raise SystemExit(f"{filename}: expected six unmarked model-line samples")
    observed_y = []
    default_y = []
    postfit_y = []
    for row, voltage in zip(rows, expected_voltages):
        if float(row["voltage_mV"]) != voltage:
            raise SystemExit(f"{filename}: model-line voltage grid mismatch: {row}")
        if float(row["default_Ra_per_ms"]) != 0.0167:
            raise SystemExit(f"{filename}: deposited mouse default Ra changed: {row}")
        if abs(float(row["postfit_Ra_per_ms"]) - 0.020746083599133762) > 1.0e-14:
            raise SystemExit(f"{filename}: optimizer mouse Ra provenance changed: {row}")
        observed_y.append(float(row["observed_blue_model_line_y_pixel"]))
        default_y.append(float(row["default_model_y_pixel"]))
        postfit_y.append(float(row["postfit_model_y_pixel"]))
        for tau_key, pixel_key in (
            ("default_model_tau_ms", "default_model_y_pixel"),
            ("postfit_model_tau_ms", "postfit_model_y_pixel"),
        ):
            expected_pixel = 104.0 + (7.5 - float(row[tau_key])) * (232.0 / 5.0)
            if abs(expected_pixel - float(row[pixel_key])) > 0.01:
                raise SystemExit(f"{filename}: model line axis conversion mismatch: {row}")
    default_rmse = math.sqrt(
        sum((actual - predicted) ** 2 for actual, predicted in zip(observed_y, default_y))
        / len(rows)
    )
    postfit_rmse = math.sqrt(
        sum((actual - predicted) ** 2 for actual, predicted in zip(observed_y, postfit_y))
        / len(rows)
    )
    if abs(default_rmse - 5.3483597199) > 0.01 or abs(postfit_rmse - 36.0577657963) > 0.01:
        raise SystemExit(
            f"{filename}: expected default/post-fit pixel RMSE 5.348/36.058, "
            f"found {default_rmse:.3f}/{postfit_rmse:.3f}"
        )
    print(
        f"{filename}: blue model line matches pre-fit default Ra more closely "
        f"(pixel RMSE {default_rmse:.2f} vs {postfit_rmse:.2f} post-fit)"
    )


def validate_recovery_model_replay() -> None:
    filename = "HUMAN-L23-WILBERS-FIG-S5-MN-RECOVERY-MODEL-REPLAY.csv"
    _, rows = read_rows(filename)
    expected = [
        (-90.0, 115.73075979, 2791.29666336),
        (-85.0, 155.66825752, 2794.57789332),
        (-80.0, 235.14906691, 2803.29195806),
        (-75.0, 376.90997245, 2816.54937565),
        (-70.0, 332.21621839, 2814.89062697),
    ]
    if len(rows) != len(expected):
        raise SystemExit(f"{filename}: expected five recovery-voltage model references")
    pooled_fast = (228.52749381071555 + 245.12119700268607) / 2.0
    pooled_slow = (1999.7294967866596 + 3579.8563888349777) / 2.0
    for row, (voltage, tau1, tau2) in zip(rows, expected):
        if float(row["recovery_voltage_mV"]) != voltage:
            raise SystemExit(f"{filename}: recovery voltage grid mismatch: {row}")
        if abs(float(row["model_tau1_ms_scipy_reference"]) - tau1) > 1.0e-8:
            raise SystemExit(f"{filename}: fast current-fit reference mismatch: {row}")
        if abs(float(row["model_tau2_ms_scipy_reference"]) - tau2) > 1.0e-8:
            raise SystemExit(f"{filename}: slow current-fit reference mismatch: {row}")
        if abs(float(row["pooled_fast_mean_ms"]) - pooled_fast) > 1.0e-9:
            raise SystemExit(f"{filename}: pooled fast-recovery mean mismatch: {row}")
        if abs(float(row["pooled_slow_mean_ms"]) - pooled_slow) > 1.0e-9:
            raise SystemExit(f"{filename}: pooled slow-recovery mean mismatch: {row}")
        if voltage == -80.0:
            source_values = {
                "experimental_human_fast_at_minus80_ms": 228.52749381071555,
                "experimental_mouse_fast_at_minus80_ms": 245.12119700268607,
                "experimental_human_slow_at_minus80_ms": 1999.7294967866596,
                "experimental_mouse_slow_at_minus80_ms": 3579.8563888349777,
            }
            for column, value in source_values.items():
                if abs(float(row[column]) - value) > 1.0e-9:
                    raise SystemExit(f"{filename}: experimental source value mismatch: {row}")
        else:
            for column in (
                "experimental_human_fast_at_minus80_ms",
                "experimental_mouse_fast_at_minus80_ms",
                "experimental_human_slow_at_minus80_ms",
                "experimental_mouse_slow_at_minus80_ms",
            ):
                if row[column] != "":
                    raise SystemExit(f"{filename}: experimental marker incorrectly assigned away from -80 mV: {row}")
    print(f"{filename}: five current-fit recovery model references and pooled source means verified")


def main() -> int:
    panels = {
        "I activation": {
            "filename": "HUMAN-L23-WILBERS-FIG-S5-I-ACTIVATION.csv",
            "tau_column": "tau_activation_ms",
            "tau_uncertainty_column": "tau_digitization_uncertainty_ms",
            "expected_voltages": [float(value) for value in range(-10, 51, 10)],
            "x_reference_pixel": 50.0,
            "x_reference_mv": -10.0,
            "x_pixels_per_mv": 10.2,
            "y_reference_pixel": 104.0,
            "y_reference_value": 7.5,
            "y_second_pixel": 336.0,
            "y_second_value": 2.5,
            "voltage_uncertainty": 1.0,
            "tau_uncertainty": 0.25,
            "voltage_tolerance": 0.11,
            "tau_tolerance": 0.11,
            "tau_bounds": (0.0, 10.0),
        },
        "J fast inactivation": {
            "filename": "HUMAN-L23-WILBERS-FIG-S5-J-FAST-INACTIVATION.csv",
            "tau_column": "tau_fast_inactivation_ms",
            "tau_uncertainty_column": "tau_digitization_uncertainty_ms",
            "expected_voltages": [float(value) for value in range(0, 51, 10)],
            "x_reference_pixel": 36.0,
            "x_reference_mv": -10.0,
            "x_pixels_per_mv": 648.0 / 70.0,
            "y_reference_pixel": 118.0,
            "y_reference_value": 60.0,
            "y_second_pixel": 393.5,
            "y_second_value": 20.0,
            "voltage_uncertainty": 1.0,
            "tau_uncertainty": 2.0,
            "voltage_tolerance": 0.6,
            "tau_tolerance": 0.11,
            "tau_bounds": (0.0, 80.0),
        },
        "K slow inactivation": {
            "filename": "HUMAN-L23-WILBERS-FIG-S5-K-SLOW-INACTIVATION.csv",
            "tau_column": "tau_slow_inactivation_ms",
            "tau_uncertainty_column": "tau_digitization_uncertainty_ms",
            "expected_voltages": [float(value) for value in range(-30, 61, 10)],
            "x_reference_pixel": 108.0,
            "x_reference_mv": -20.0,
            "x_pixels_per_mv": 7.2,
            "y_reference_pixel": 204.0,
            "y_reference_value": 600.0,
            "y_second_pixel": 487.0,
            "y_second_value": 200.0,
            "voltage_uncertainty": 2.5,
            "tau_uncertainty": 25.0,
            "voltage_tolerance": 0.11,
            "tau_tolerance": 0.11,
            "tau_bounds": (0.0, 800.0),
        },
    }

    total = 0
    for name, settings in panels.items():
        voltage_error, tau_error, count = validate_panel(**settings)
        total += count
        print(
            f"{name}: {count} manually digitized markers; max rounding residuals "
            f"{voltage_error:.3g} mV and {tau_error:.3g} axis units"
        )

    total += validate_source_marker_values(
        filename="HUMAN-L23-WILBERS-FIG-S5-M-FAST-RECOVERY.csv",
        tau_column="tau_fast_recovery_ms",
        tau_uncertainty_column="tau_digitization_uncertainty_ms",
        expected_values={
            "human": 228.52749381071555,
            "mouse": 245.12119700268607,
        },
    )
    total += validate_source_marker_values(
        filename="HUMAN-L23-WILBERS-FIG-S5-N-SLOW-RECOVERY.csv",
        tau_column="tau_slow_recovery_s",
        tau_uncertainty_column="tau_digitization_uncertainty_s",
        expected_values={
            "human": 1.9997294967866596,
            "mouse": 3.5798563888349777,
        },
    )
    validate_mouse_model_prefit_check()
    validate_recovery_model_replay()
    print(
        f"Figure S5 evidence record passed: {total} experimental group-mean markers "
        "(46 manually digitized, 4 transcribed from source-script constants); "
        "seven research CSVs preserve marker and model-replay evidence. "
        "Source provenance, species markers, point grids, and axis calibration verified. "
        "Plot-digitization uncertainty is not biological SD."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
