#!/usr/bin/env python3
"""Profile and compare signed short-time K_IV residual corrections by voltage."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

from wilbers_k_iv_multivoltage import (
    analyze_postpeak_waveforms,
    read_postpeak_waveforms,
    summary_csv_text,
    tau3_profile_shape_csv_text,
    validate_summary_rows,
    validate_tau3_profile_shape_rows,
    analyze_tau1_tau3_surface,
    tau1_tau3_surface_csv_text,
    validate_tau1_tau3_surface_rows,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--waveforms", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--coarse-profile-points", type=int, default=901)
    parser.add_argument("--local-profile-points", type=int, default=801)
    parser.add_argument("--short-profile-points", type=int, default=801)
    parser.add_argument("--tau3-min-ms", type=float, default=0.6)
    parser.add_argument("--tau3-max-ms", type=float, default=2.0)
    parser.add_argument("--profile-shape-output", type=Path)
    parser.add_argument("--tau1-tau3-surface-output", type=Path)
    parser.add_argument("--surface-tau1-points", type=int, default=9)
    parser.add_argument("--surface-tau3-points", type=int, default=5601)
    parser.add_argument("--surface-tau3-max-ms", type=float, default=10.0)
    parser.add_argument(
        "--emit-to-stdout",
        action="store_true",
        help="Print all 27 eligible-command result rows with explicit delimiters",
    )
    args = parser.parse_args()
    rows = analyze_postpeak_waveforms(
        args.waveforms,
        coarse_profile_points=args.coarse_profile_points,
        local_profile_points=args.local_profile_points,
        short_profile_points=args.short_profile_points,
        tau3_min_ms=args.tau3_min_ms,
        tau3_max_ms=args.tau3_max_ms,
    )
    validate_summary_rows(
        rows, tau3_min_ms=args.tau3_min_ms, tau3_max_ms=args.tau3_max_ms
    )
    content = summary_csv_text(rows)
    args.output.expanduser().resolve().write_text(content, encoding="utf-8")
    if args.profile_shape_output:
        shape_rows = [row["tau3_profile_shape"] for row in rows]
        validate_tau3_profile_shape_rows(shape_rows)
        shape_content = tau3_profile_shape_csv_text(shape_rows)
        args.profile_shape_output.expanduser().resolve().write_text(
            shape_content, encoding="utf-8"
        )
    else:
        shape_content = ""
    if args.tau1_tau3_surface_output:
        surface_rows = analyze_tau1_tau3_surface(
            read_postpeak_waveforms(args.waveforms),
            rows,
            tau1_grid_points=args.surface_tau1_points,
            tau3_min_ms=args.tau3_min_ms,
            tau3_max_ms=args.surface_tau3_max_ms,
            tau3_grid_points=args.surface_tau3_points,
        )
        validate_tau1_tau3_surface_rows(
            surface_rows,
            tau1_grid_points=args.surface_tau1_points,
            tau3_grid_points=args.surface_tau3_points,
            tau3_min_ms=args.tau3_min_ms,
            tau3_max_ms=args.surface_tau3_max_ms,
        )
        surface_content = tau1_tau3_surface_csv_text(surface_rows)
        args.tau1_tau3_surface_output.expanduser().resolve().write_text(
            surface_content, encoding="utf-8"
        )
    else:
        surface_rows = []
        surface_content = ""
    if args.emit_to_stdout:
        print("BEGIN_HUMANJS_K_IV_MULTIVOLTAGE_SUMMARY")
        print(content, end="")
        print("END_HUMANJS_K_IV_MULTIVOLTAGE_SUMMARY")
        if args.profile_shape_output:
            print("BEGIN_HUMANJS_K_IV_TAU3_PROFILE_SHAPE")
            print(shape_content, end="")
            print("END_HUMANJS_K_IV_TAU3_PROFILE_SHAPE")
        if args.tau1_tau3_surface_output:
            print("BEGIN_HUMANJS_K_IV_TAU1_TAU3_SURFACE")
            print(surface_content, end="")
            print("END_HUMANJS_K_IV_TAU1_TAU3_SURFACE")
    for row in rows:
        print(
            f"{row['voltage_mv']:g} mV: tau1={row['local_tau1_ms']:.6g} ms, "
            f"tau3={row['tau3_ms']:.6g} ms, a3={row['a3_ma_cm2']:.6g} mA/cm2, "
            f"full/early/late RMSE reductions="
            f"{row['full_improvement_pct']:.2f}%/"
            f"{row['first_10ms_improvement_pct']:.2f}%/"
            f"{row['after_10ms_improvement_pct']:.2f}%, "
            f"positive control collapsed={row['nonnegative_control_collapsed']}, "
            f"tau3 boundary={row['tau3_profile_at_boundary']}, "
            f"1%/5%/10% RSS spans="
            f"{row['tau3_profile_shape']['near_minimum_1pct_objective_span_ms']:.6g}/"
            f"{row['tau3_profile_shape']['near_minimum_5pct_objective_span_ms']:.6g}/"
            f"{row['tau3_profile_shape']['near_minimum_10pct_objective_span_ms']:.6g} ms"
        )
    if surface_rows:
        for voltage in (-30.0, -60.0, 55.0):
            group = [row for row in surface_rows if row["voltage_mv"] == voltage]
            center = group[len(group) // 2]
            global_row = next(row for row in group if row["is_global_surface_minimum"])
            conditional_taus = [row["selected_tau3_ms"] for row in group]
            print(
                f"{voltage:g} mV tau1-tau3 surface: reference tau1="
                f"{center['reference_tau1_ms']:.6g} ms, reference tau3="
                f"{center['reference_tau3_ms']:.6g} ms; global minimum at "
                f"tau1={global_row['tau1_ms']:.6g} ms/tau3={global_row['selected_tau3_ms']:.6g} ms "
                f"({global_row['relative_rss_to_surface_min_pct']:.6g}% relative RSS); "
                f"conditional tau3 range across the 6% window="
                f"{min(conditional_taus):.6g}..{max(conditional_taus):.6g} ms"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
