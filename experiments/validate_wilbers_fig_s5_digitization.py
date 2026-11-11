#!/usr/bin/env python3
"""Validate provenance, axis calibration, and values in the Figure S5 K+ digitizations."""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA256 = "dfa1daaf4dd0e3979bac84b9cb8b1874c4514d40588969a21d7766a7f12f2a1d"
SPECIES_MARKERS = {"human": "red_open_circle", "mouse": "blue_cross"}


def close(actual: float, expected: float, tolerance: float = 0.11) -> bool:
    return math.isfinite(actual) and abs(actual - expected) <= tolerance


def validate_panel(
    *,
    filename: str,
    tau_column: str,
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
    tau_bounds: tuple[float, float],
) -> tuple[float, float, int]:
    path = ROOT / "research" / filename
    text = path.read_text(encoding="utf-8")
    if EXPECTED_SHA256 not in text:
        raise SystemExit(f"{filename}: source PDF SHA-256 provenance is missing")
    rows = list(csv.DictReader(line for line in text.splitlines() if not line.startswith("#")))
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
            if not close(derived_voltage, voltage):
                raise SystemExit(f"{filename}: voltage calibration mismatch: {row}")
            if not close(derived_tau, tau):
                raise SystemExit(f"{filename}: time-constant calibration mismatch: {row}")
            if row["marker"] != expected_marker:
                raise SystemExit(f"{filename}: marker/species mismatch: {row}")
            if float(row["voltage_digitization_uncertainty_mV"]) != voltage_uncertainty:
                raise SystemExit(f"{filename}: voltage uncertainty missing or changed: {row}")
            if float(row["tau_digitization_uncertainty_ms"]) != tau_uncertainty:
                raise SystemExit(f"{filename}: time-constant uncertainty missing or changed: {row}")
            if not (tau_bounds[0] < tau < tau_bounds[1]):
                raise SystemExit(f"{filename}: implausible plotted time constant: {row}")

    return max_voltage_error, max_tau_error, len(rows)


def main() -> int:
    panels = {
        "I activation": {
            "filename": "HUMAN-L23-WILBERS-FIG-S5-I-ACTIVATION.csv",
            "tau_column": "tau_activation_ms",
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
            "tau_bounds": (0.0, 10.0),
        },
        "K slow inactivation": {
            "filename": "HUMAN-L23-WILBERS-FIG-S5-K-SLOW-INACTIVATION.csv",
            "tau_column": "tau_slow_inactivation_ms",
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
            "tau_bounds": (0.0, 800.0),
        },
    }
    total = 0
    for name, settings in panels.items():
        voltage_error, tau_error, count = validate_panel(**settings)
        total += count
        print(
            f"{name}: {count} markers; max rounding residuals "
            f"{voltage_error:.3g} mV and {tau_error:.3g} ms"
        )
    print(
        f"Figure S5 digitization passed: {total} experimental group-mean markers; "
        "source provenance, species markers, point grids, and axis calibration verified. "
        "Digitization uncertainty is not biological SD."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
