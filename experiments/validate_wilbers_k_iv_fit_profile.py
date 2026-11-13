#!/usr/bin/env python3
"""Validate the fixed-tau1 profile of the Wilbers K_IV post-peak objective."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

from wilbers_k_iv_fit_diagnostics import K_IV_PROFILE_FIELDNAMES


def read_profile(path: Path) -> list[dict[str, str]]:
    content = path.read_text(encoding="utf-8")
    rows = list(
        csv.DictReader(
            line for line in content.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    )
    if not rows:
        raise SystemExit(f"No profile rows in {path}")
    if tuple(rows[0].keys()) != K_IV_PROFILE_FIELDNAMES:
        raise SystemExit("K_IV profiled objective schema mismatch")
    return rows


def number(row: dict[str, str], key: str) -> float:
    try:
        value = float(row[key])
    except (KeyError, ValueError) as exc:
        raise SystemExit(f"Invalid numeric profile field {key}: {row.get(key)!r}") from exc
    if not math.isfinite(value):
        raise SystemExit(f"Non-finite profile field {key}: {value}")
    return value


def validate(path: Path, *, upper_bound_ms: float, expected_grid_size: int) -> None:
    rows = read_profile(path)
    if len(rows) != expected_grid_size:
        raise SystemExit(
            f"Expected {expected_grid_size} logarithmic tau1 profile points, got {len(rows)}"
        )
    if not math.isfinite(upper_bound_ms) or upper_bound_ms <= 0.05:
        raise SystemExit("Profile upper bound must be finite and greater than 0.05 ms")

    taus: list[float] = []
    r_squared_values: list[float] = []
    rmse_values: list[float] = []
    rss_sample_counts: list[float] = []
    for row in rows:
        voltage = number(row, "voltage_mv")
        if voltage != -70.0:
            raise SystemExit(f"Unexpected profile voltage: {voltage:g} mV")
        tau = number(row, "tau1_ms")
        if not 0.05 <= tau <= upper_bound_ms:
            raise SystemExit(f"tau1 outside requested profile bounds at {tau:g} ms")
        taus.append(tau)

        amplitudes = [
            number(row, "fit_fast_amplitude_ma_cm2"),
            number(row, "fit_slow_amplitude_ma_cm2"),
            number(row, "fit_offset_ma_cm2"),
        ]
        if any(value < 0.0 for value in amplitudes):
            raise SystemExit(f"Negative profiled amplitude at tau1={tau:g} ms")
        r_squared = number(row, "fit_r_squared")
        if not -1.0 <= r_squared <= 1.0 + 1.0e-10:
            raise SystemExit(f"Invalid profile R-squared at tau1={tau:g} ms")
        r_squared_values.append(r_squared)
        rmse = number(row, "fit_rmse_ma_cm2")
        if rmse < 0.0:
            raise SystemExit("Negative profile RMSE")
        rmse_values.append(rmse)
        rss = number(row, "residual_sum_squares")
        if rss < 0.0:
            raise SystemExit("Negative profile residual sum of squares")
        rss_sample_counts.append(rss / (rmse * rmse) if rmse > 0.0 else math.nan)
        if row["solver_success"] != "True":
            raise SystemExit(f"Bounded profile solver failed at tau1={tau:g} ms")
        optimality = number(row, "solver_optimality")
        if optimality < 0.0:
            raise SystemExit("Negative profile solver optimality")

    if any(b <= a for a, b in zip(taus, taus[1:])):
        raise SystemExit("Profile tau1 grid is not strictly increasing")
    finite_counts = [value for value in rss_sample_counts if math.isfinite(value)]
    if not finite_counts:
        raise SystemExit("Profile residuals do not yield a finite sample count")
    if max(finite_counts) - min(finite_counts) > 1.0e-5:
        raise SystemExit("Profile RSS/RMSE sample-count consistency check failed")

    best_index = min(range(len(rows)), key=lambda i: rmse_values[i])
    best_tau = taus[best_index]
    best_r2 = r_squared_values[best_index]
    best_rmse = rmse_values[best_index]
    if best_r2 < 0.999:
        raise SystemExit(
            f"Profile best fit unexpectedly poor: R2={best_r2:.9g}"
        )

    near_best = [
        tau for tau, rmse in zip(taus, rmse_values)
        if rmse <= best_rmse * (1.0 + 0.01)
    ]
    close_r2 = [
        tau for tau, r2 in zip(taus, r_squared_values)
        if best_r2 - r2 <= 1.0e-6
    ]
    print(
        f"Validated −70-mV K_IV profiled objective: {len(rows)} tau1 values "
        f"from {taus[0]:.6g} to {taus[-1]:.6g} ms; all bounded linear solves succeeded."
    )
    print(
        f"Best profile: tau1={best_tau:.9g} ms; R2={best_r2:.12g}; "
        f"RMSE={best_rmse:.12g} mA/cm2."
    )
    print(
        "Profile flatness: tau1 range within 1% of minimum RMSE "
        f"{min(near_best):.6g}..{max(near_best):.6g} ms; "
        "range within 1e-6 of maximum R2 "
        f"{min(close_r2):.6g}..{max(close_r2):.6g} ms."
    )
    print(
        "The profile is a numerical identifiability diagnostic for the deposited "
        "model current, not a human experimental trace refit or biological validation."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--upper-bound-ms", type=float, default=300.0)
    parser.add_argument("--expected-grid-size", type=int, default=601)
    args = parser.parse_args()
    validate(
        args.actual,
        upper_bound_ms=args.upper_bound_ms,
        expected_grid_size=args.expected_grid_size,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
