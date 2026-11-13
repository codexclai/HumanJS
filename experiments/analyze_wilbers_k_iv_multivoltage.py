#!/usr/bin/env python3
"""Profile and compare signed short-time K_IV residual corrections by voltage."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

from wilbers_k_iv_multivoltage import (
    analyze_postpeak_waveforms,
    summary_csv_text,
    validate_summary_rows,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--waveforms", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--coarse-profile-points", type=int, default=901)
    parser.add_argument("--local-profile-points", type=int, default=801)
    parser.add_argument("--short-profile-points", type=int, default=801)
    parser.add_argument(
        "--emit-to-stdout",
        action="store_true",
        help="Print the compact three-row result table with explicit delimiters",
    )
    args = parser.parse_args()
    rows = analyze_postpeak_waveforms(
        args.waveforms,
        coarse_profile_points=args.coarse_profile_points,
        local_profile_points=args.local_profile_points,
        short_profile_points=args.short_profile_points,
    )
    validate_summary_rows(rows)
    content = summary_csv_text(rows)
    args.output.expanduser().resolve().write_text(content, encoding="utf-8")
    if args.emit_to_stdout:
        print("BEGIN_HUMANJS_K_IV_MULTIVOLTAGE_SUMMARY")
        print(content, end="")
        print("END_HUMANJS_K_IV_MULTIVOLTAGE_SUMMARY")
    for row in rows:
        print(
            f"{row['voltage_mv']:g} mV: tau1={row['local_tau1_ms']:.6g} ms, "
            f"tau3={row['tau3_ms']:.6g} ms, a3={row['a3_ma_cm2']:.6g} mA/cm2, "
            f"full/early/late RMSE reductions="
            f"{row['full_improvement_pct']:.2f}%/"
            f"{row['first_10ms_improvement_pct']:.2f}%/"
            f"{row['after_10ms_improvement_pct']:.2f}%, "
            f"positive control collapsed={row['nonnegative_control_collapsed']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
