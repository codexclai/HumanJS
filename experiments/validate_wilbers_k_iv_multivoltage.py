#!/usr/bin/env python3
"""Validate cross-voltage K_IV residual-correction summary outputs."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

from wilbers_k_iv_multivoltage import (
    K_IV_MULTIVOLTAGE_FIELDNAMES,
    K_IV_MULTIVOLTAGE_TARGETS_MV,
    validate_summary_rows,
)

BOOL_FIELDS = {
    "coarse_profile_at_boundary",
    "local_profile_at_boundary",
    "signed_extra_is_negative",
    "nonnegative_control_collapsed",
}
INT_FIELDS = {
    "sample_count",
    "coarse_profile_points",
    "local_profile_points",
    "short_component_profile_points",
}
NUMERIC_FIELDS = set(K_IV_MULTIVOLTAGE_FIELDNAMES) - BOOL_FIELDS - INT_FIELDS


def read_summary(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(
            csv.DictReader(
                line for line in stream if line.strip() and not line.lstrip().startswith("#")
            )
        )
    if not rows or tuple(rows[0].keys()) != K_IV_MULTIVOLTAGE_FIELDNAMES:
        raise SystemExit(f"K_IV multivoltage summary schema mismatch: {path}")
    parsed: list[dict[str, Any]] = []
    for row in rows:
        converted: dict[str, Any] = {}
        for field, value in row.items():
            try:
                if field in BOOL_FIELDS:
                    if value not in ("True", "False"):
                        raise ValueError("invalid boolean token")
                    converted[field] = value == "True"
                elif field in INT_FIELDS:
                    converted[field] = int(value)
                else:
                    converted[field] = float(value)
            except (TypeError, ValueError) as exc:
                raise SystemExit(
                    f"Invalid K_IV multivoltage value {field}={value!r} in {path}"
                ) from exc
        parsed.append(converted)
    return parsed


def compare_expected(
    actual: list[dict[str, Any]],
    expected: list[dict[str, Any]],
    *,
    relative_tolerance: float = 2.0e-5,
    absolute_tolerance: float = 1.0e-12,
) -> None:
    if len(actual) != len(expected):
        raise SystemExit(
            f"K_IV multivoltage row count changed: expected {len(expected)}, got {len(actual)}"
        )
    for row_index, (found, reference) in enumerate(zip(actual, expected, strict=True)):
        for field in K_IV_MULTIVOLTAGE_FIELDNAMES:
            a, b = found[field], reference[field]
            if field in BOOL_FIELDS or field in INT_FIELDS:
                if a != b:
                    raise SystemExit(
                        f"K_IV multivoltage mismatch at row {row_index}, {field}: "
                        f"expected {b!r}, got {a!r}"
                    )
            elif not math.isclose(
                float(a),
                float(b),
                rel_tol=relative_tolerance,
                abs_tol=absolute_tolerance,
            ):
                raise SystemExit(
                    f"K_IV multivoltage mismatch at row {row_index}, {field}: "
                    f"expected {b:.12g}, got {a:.12g}"
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--expected", type=Path)
    args = parser.parse_args()
    actual = read_summary(args.actual)
    try:
        validate_summary_rows(actual)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if args.expected:
        expected = read_summary(args.expected)
        try:
            validate_summary_rows(expected)
        except ValueError as exc:
            raise SystemExit(f"Invalid expected summary: {exc}") from exc
        compare_expected(actual, expected)
        print(
            "K_IV residual summary matches the committed 27-command "
            "finite-positive source-fit reference."
        )
    else:
        print("K_IV 27-command finite-source-fit residual summary passed structural validation.")
    for row in actual:
        print(
            f"{row['voltage_mv']:g} mV: tau1={row['local_tau1_ms']:.6g} ms; "
            f"tau3={row['tau3_ms']:.6g} ms; a3={row['a3_ma_cm2']:.6g} mA/cm2; "
            f"full RMSE improvement={row['full_improvement_pct']:.3f}%; "
            f"early={row['first_10ms_improvement_pct']:.3f}%; "
            f"late={row['after_10ms_improvement_pct']:.3f}%; "
            f"negative correction={row['signed_extra_is_negative']}; "
            f"nonnegative control collapsed={row['nonnegative_control_collapsed']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
