#!/usr/bin/env python3
"""Validate provenance, axis calibration, and values in the Figure S5 K slow-inactivation digitization."""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/HUMAN-L23-WILBERS-FIG-S5-K-SLOW-INACTIVATION.csv"
EXPECTED_SHA256 = "dfa1daaf4dd0e3979bac84b9cb8b1874c4514d40588969a21d7766a7f12f2a1d"
VOLTAGES_MV = [float(value) for value in range(-30, 61, 10)]
SPECIES_MARKERS = {
    "human": "red_open_circle",
    "mouse": "blue_cross",
}
X_REFERENCE_PIXEL = 108.0
X_REFERENCE_MV = -20.0
X_PIXELS_PER_MV = 7.2
Y_REFERENCE_PIXEL = 204.0
Y_REFERENCE_MS = 600.0
Y_SECOND_PIXEL = 487.0
Y_SECOND_MS = 200.0
VOLTAGE_UNCERTAINTY_MV = 2.5
TAU_UNCERTAINTY_MS = 25.0


def close(actual: float, expected: float, tolerance: float = 0.11) -> bool:
    return math.isfinite(actual) and abs(actual - expected) <= tolerance


def main() -> int:
    text = DATA.read_text(encoding="utf-8")
    if EXPECTED_SHA256 not in text:
        raise SystemExit("source PDF SHA-256 provenance is missing from the digitization record")
    rows = list(csv.DictReader(line for line in text.splitlines() if not line.startswith("#")))
    if len(rows) != 20:
        raise SystemExit(f"expected 20 experimental markers, found {len(rows)}")

    counts = Counter(row["species"] for row in rows)
    if counts != Counter({"human": 10, "mouse": 10}):
        raise SystemExit(f"unexpected marker counts by species: {dict(counts)}")

    max_voltage_error = 0.0
    max_tau_error = 0.0
    for species in SPECIES_MARKERS:
        selected = [row for row in rows if row["species"] == species]
        voltages = [float(row["voltage_mV"]) for row in selected]
        if voltages != VOLTAGES_MV:
            raise SystemExit(f"{species} voltage grid is not the digitized -30 to +60 mV series")
        for row in selected:
            x_pixel = float(row["x_pixel_crop"])
            y_pixel = float(row["y_pixel_crop"])
            voltage = float(row["voltage_mV"])
            tau = float(row["tau_slow_inactivation_ms"])
            derived_voltage = X_REFERENCE_MV + (x_pixel - X_REFERENCE_PIXEL) / X_PIXELS_PER_MV
            derived_tau = Y_REFERENCE_MS + (y_pixel - Y_REFERENCE_PIXEL) * (
                Y_SECOND_MS - Y_REFERENCE_MS
            ) / (Y_SECOND_PIXEL - Y_REFERENCE_PIXEL)
            max_voltage_error = max(max_voltage_error, abs(derived_voltage - voltage))
            max_tau_error = max(max_tau_error, abs(derived_tau - tau))
            if not close(derived_voltage, voltage):
                raise SystemExit(f"voltage calibration mismatch: {row}")
            if not close(derived_tau, tau):
                raise SystemExit(f"time-constant calibration mismatch: {row}")
            if row["marker"] != SPECIES_MARKERS[species]:
                raise SystemExit(f"marker/species mismatch: {row}")
            if float(row["voltage_digitization_uncertainty_mV"]) != VOLTAGE_UNCERTAINTY_MV:
                raise SystemExit(f"voltage uncertainty missing or changed: {row}")
            if float(row["tau_digitization_uncertainty_ms"]) != TAU_UNCERTAINTY_MS:
                raise SystemExit(f"time-constant uncertainty missing or changed: {row}")
            if not (0.0 < tau < 800.0):
                raise SystemExit(f"implausible plotted time constant: {row}")

    print(
        "Figure S5 panel K digitization passed: 20 plotted group-mean markers "
        "(10 human, 10 mouse); axis calibration and provenance verified; "
        f"max rounding residuals {max_voltage_error:.3g} mV and {max_tau_error:.3g} ms. "
        "Digitization uncertainty is not biological SD."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
