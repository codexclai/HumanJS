#!/usr/bin/env python3
"""Validate and summarize the time-resolved K_IV profiled-fit residuals."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from statistics import fmean

from wilbers_k_iv_fit_diagnostics import K_IV_FIT_RESIDUAL_FIELDNAMES


def read_rows(path: Path) -> list[dict[str, str]]:
    rows = list(
        csv.DictReader(
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    )
    if not rows:
        raise SystemExit(f"No residual rows found in {path}")
    if tuple(rows[0].keys()) != K_IV_FIT_RESIDUAL_FIELDNAMES:
        raise SystemExit("K_IV profile residual schema mismatch")
    return rows


def number(row: dict[str, str], field: str) -> float:
    try:
        result = float(row[field])
    except (KeyError, ValueError) as exc:
        raise SystemExit(f"Invalid residual field {field}: {row.get(field)!r}") from exc
    if not math.isfinite(result):
        raise SystemExit(f"Non-finite residual field {field}: {result}")
    return result


def validate(actual_path: Path, profile_path: Path) -> None:
    rows = read_rows(actual_path)
    profile_rows = list(
        csv.DictReader(
            line
            for line in profile_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    )
    if len(profile_rows) != 801:
        raise SystemExit(f"Expected 801 local profile rows, got {len(profile_rows)}")
    profile_best = min(profile_rows, key=lambda row: float(row["fit_rmse_ma_cm2"]))
    expected_tau = float(profile_best["tau1_ms"])
    if len(rows) < 5:
        raise SystemExit(f"Too few residual rows: {len(rows)}")

    times = [number(row, "time_since_peak_ms") for row in rows]
    source_times = [number(row, "source_simulation_time_ms") for row in rows]
    observed = [number(row, "observed_current_ma_cm2") for row in rows]
    fitted = [number(row, "fitted_current_ma_cm2") for row in rows]
    residuals = [number(row, "residual_current_ma_cm2") for row in rows]

    if any(b <= a for a, b in zip(times, times[1:])):
        raise SystemExit("Residual relative times are not strictly increasing")
    if any(b <= a for a, b in zip(source_times, source_times[1:])):
        raise SystemExit("Original NEURON times are not strictly increasing")
    if abs(times[0]) > 1.0e-12:
        raise SystemExit("Residual time origin is not the source fit's first sample")
    if max(abs((t - source_times[0]) - rel) for t, rel in zip(source_times, times)) > 1.0e-9:
        raise SystemExit("Source and relative residual time axes disagree")
    if any(
        abs((y - f) - r) > 2.0e-15
        for y, f, r in zip(observed, fitted, residuals)
    ):
        raise SystemExit("Residual values do not equal observed minus fitted current")

    voltages = {number(row, "voltage_mv") for row in rows}
    taus = {number(row, "profile_tau1_ms") for row in rows}
    if voltages != {-70.0}:
        raise SystemExit(f"Unexpected profile residual voltage(s): {sorted(voltages)}")
    if len(taus) != 1 or abs(next(iter(taus)) - expected_tau) > 1.0e-9:
        raise SystemExit("Residual tau1 does not match the best local-profile point")

    coefficients = {
        field: {number(row, field) for row in rows}
        for field in (
            "profile_fast_amplitude_ma_cm2",
            "profile_slow_amplitude_ma_cm2",
            "profile_offset_ma_cm2",
        )
    }
    if any(len(values) != 1 for values in coefficients.values()):
        raise SystemExit("Profile residual coefficients vary across time samples")

    mean_observed = fmean(observed)
    rss = math.fsum(r * r for r in residuals)
    rmse = math.sqrt(rss / len(rows))
    total = math.fsum((y - mean_observed) ** 2 for y in observed)
    r_squared = 1.0 - rss / total if total > 0.0 else math.nan
    profile_rmse = float(profile_best["fit_rmse_ma_cm2"])
    profile_r2 = float(profile_best["fit_r_squared"])
    if abs(rmse - profile_rmse) > max(1.0e-14, profile_rmse * 1.0e-7):
        raise SystemExit("Residual RMSE disagrees with the profiled objective")
    if abs(r_squared - profile_r2) > 1.0e-9:
        raise SystemExit("Residual R-squared disagrees with the profiled objective")

    residual_mean = fmean(residuals)
    residual_std = math.sqrt(math.fsum((r - residual_mean) ** 2 for r in residuals) / len(rows))
    lag1 = (
        sum((a - residual_mean) * (b - residual_mean) for a, b in zip(residuals, residuals[1:]))
        / math.fsum((r - residual_mean) ** 2 for r in residuals)
        if residual_std > 0.0
        else math.nan
    )
    dw = (
        math.fsum((b - a) ** 2 for a, b in zip(residuals, residuals[1:])) / rss
        if rss > 0.0
        else math.nan
    )
    maximum_index = max(range(len(residuals)), key=lambda index: abs(residuals[index]))
    quartile_size = len(rows) // 4
    quartile_means = [
        fmean(residuals[index * quartile_size : (index + 1) * quartile_size])
        for index in range(4)
    ]
    print(
        f"Validated {len(rows)} time-resolved residuals at −70 mV; "
        f"tau1={expected_tau:.9g} ms; R2={r_squared:.12g}; RMSE={rmse:.12g} mA/cm2."
    )
    print(
        f"Residual mean={residual_mean:.6g}; SD={residual_std:.6g}; "
        f"lag-1 autocorrelation={lag1:.6g}; Durbin-Watson={dw:.6g}."
    )
    print(
        f"Maximum absolute residual={abs(residuals[maximum_index]):.6g} mA/cm2 "
        f"at relative t={times[maximum_index]:.6g} ms."
    )
    print(
        "Residual mean by successive equal-count quarters (mA/cm2): "
        + ", ".join(f"{value:.6g}" for value in quartile_means)
    )
    print(
        "Residual diagnostics are descriptive properties of a deterministic model waveform; "
        "they are not a measurement-noise test or biological validation."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    args = parser.parse_args()
    validate(args.actual, args.profile)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
