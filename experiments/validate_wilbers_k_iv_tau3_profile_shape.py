#!/usr/bin/env python3
"""Validate descriptive full-waveform tau3 objective-shape summaries."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

from wilbers_k_iv_multivoltage import (
    K_IV_TAU3_PROFILE_SHAPE_BOOL_FIELDS,
    K_IV_TAU3_PROFILE_SHAPE_FIELDNAMES,
    K_IV_TAU3_PROFILE_SHAPE_INT_FIELDS,
    validate_tau3_profile_shape_rows,
)

NUMERIC_FIELDS = set(K_IV_TAU3_PROFILE_SHAPE_FIELDNAMES) - (
    K_IV_TAU3_PROFILE_SHAPE_BOOL_FIELDS | K_IV_TAU3_PROFILE_SHAPE_INT_FIELDS
)


def read_shape_summary(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(
            line for line in stream if line.strip() and not line.lstrip().startswith("#")
        ))
    if not rows or tuple(rows[0].keys()) != K_IV_TAU3_PROFILE_SHAPE_FIELDNAMES:
        raise SystemExit(f"K_IV tau3 profile-shape schema mismatch: {path}")
    parsed = []
    for row in rows:
        item = {}
        for field, value in row.items():
            try:
                if field in K_IV_TAU3_PROFILE_SHAPE_BOOL_FIELDS:
                    if value not in ("True", "False"):
                        raise ValueError("invalid boolean")
                    item[field] = value == "True"
                elif field in K_IV_TAU3_PROFILE_SHAPE_INT_FIELDS:
                    item[field] = int(value)
                else:
                    item[field] = float(value)
            except (TypeError, ValueError) as exc:
                raise SystemExit(f"Invalid K_IV profile-shape value {field}={value!r}") from exc
        parsed.append(item)
    try:
        validate_tau3_profile_shape_rows(parsed)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    return parsed


def compare_expected(
    actual: list[dict[str, Any]],
    expected: list[dict[str, Any]],
    *,
    relative_tolerance: float = 2.0e-5,
    absolute_tolerance: float = 1.0e-12,
) -> None:
    if len(actual) != len(expected):
        raise SystemExit(f"K_IV profile-shape row count changed: {len(actual)} != {len(expected)}")
    for row_index, (found, reference) in enumerate(zip(actual, expected, strict=True)):
        for field in K_IV_TAU3_PROFILE_SHAPE_FIELDNAMES:
            a, b = found[field], reference[field]
            if field in K_IV_TAU3_PROFILE_SHAPE_BOOL_FIELDS | K_IV_TAU3_PROFILE_SHAPE_INT_FIELDS:
                if a != b:
                    raise SystemExit(
                        f"K_IV profile-shape mismatch row {row_index}, {field}: {a!r} != {b!r}"
                    )
            elif not math.isclose(float(a), float(b),
                rel_tol=relative_tolerance, abs_tol=absolute_tolerance):
                raise SystemExit(
                    f"K_IV profile-shape mismatch row {row_index}, {field}: "
                    f"{float(a):.12g} != {float(b):.12g}"
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--expected", type=Path)
    args = parser.parse_args()
    actual = read_shape_summary(args.actual)
    if args.expected:
        expected = read_shape_summary(args.expected)
        compare_expected(actual, expected)
        print("K_IV tau3 objective-shape summary matches the committed 27-command reference.")
    spans = {
        threshold: [row[f"near_minimum_{threshold}pct_objective_span_ms"] for row in actual]
        for threshold in (1, 5, 10)
    }
    curvatures = [row["profile_objective_normalized_curvature_per_ms2"] for row in actual]
    def median(values: list[float]) -> float:
        ordered = sorted(values)
        return ordered[len(ordered) // 2]
    print(
        "K_IV tau3 objective-shape diagnostics (not confidence intervals): "
        f"median normalized local RSS curvature={median(curvatures):.6g} ms^-2; "
        + "; ".join(
            f"median {threshold}% objective basin span={median(values):.6g} ms "
            f"(range {min(values):.6g}..{max(values):.6g})"
            for threshold, values in spans.items()
        )
    )
    for row in actual:
        print(
            f"{row['voltage_mv']:g} mV: tau3={row['selected_tau3_ms']:.6g} ms; "
            f"curvature={row['profile_objective_normalized_curvature_per_ms2']:.6g} ms^-2; "
            f"1%/5%/10% basin spans="
            f"{row['near_minimum_1pct_objective_span_ms']:.6g}/"
            f"{row['near_minimum_5pct_objective_span_ms']:.6g}/"
            f"{row['near_minimum_10pct_objective_span_ms']:.6g} ms; "
            f"10% basin touches grid edge={row['near_minimum_10pct_touches_grid_edge']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
