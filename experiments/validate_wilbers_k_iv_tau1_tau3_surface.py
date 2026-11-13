#!/usr/bin/env python3
"""Validate the conditional three-voltage K_IV tau1-tau3 profile surface."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

from wilbers_k_iv_multivoltage import (
    K_IV_TAU1_TAU3_SURFACE_BOOL_FIELDS,
    K_IV_TAU1_TAU3_SURFACE_FIELDNAMES,
    K_IV_TAU1_TAU3_SURFACE_INT_FIELDS,
    validate_tau1_tau3_surface_rows,
)

BOUNDARY_NAN_FIELDS = {
    "profile_objective_normalized_curvature_per_ms2",
    "left_neighbor_delta_rss_pct",
    "right_neighbor_delta_rss_pct",
}


def read_surface(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(
            line for line in stream if line.strip() and not line.lstrip().startswith("#")
        ))
    if not rows or tuple(rows[0].keys()) != K_IV_TAU1_TAU3_SURFACE_FIELDNAMES:
        raise SystemExit(f"K_IV tau1-tau3 surface schema mismatch: {path}")
    parsed: list[dict[str, Any]] = []
    for row in rows:
        item: dict[str, Any] = {}
        for field, value in row.items():
            try:
                if field in K_IV_TAU1_TAU3_SURFACE_BOOL_FIELDS:
                    if value not in ("True", "False"):
                        raise ValueError("invalid Boolean token")
                    item[field] = value == "True"
                elif field in K_IV_TAU1_TAU3_SURFACE_INT_FIELDS:
                    item[field] = int(value)
                else:
                    item[field] = float(value)
            except (TypeError, ValueError) as exc:
                raise SystemExit(
                    f"Invalid K_IV tau1-tau3 surface value {field}={value!r}"
                ) from exc
        parsed.append(item)
    return parsed


def compare_expected(
    actual: list[dict[str, Any]],
    expected: list[dict[str, Any]],
) -> None:
    if len(actual) != len(expected):
        raise SystemExit(
            f"K_IV tau1-tau3 surface row count changed: expected {len(expected)}, got {len(actual)}"
        )
    for index, (found, reference) in enumerate(zip(actual, expected, strict=True)):
        for field in K_IV_TAU1_TAU3_SURFACE_FIELDNAMES:
            a, b = found[field], reference[field]
            if field in K_IV_TAU1_TAU3_SURFACE_BOOL_FIELDS | K_IV_TAU1_TAU3_SURFACE_INT_FIELDS:
                if a != b:
                    raise SystemExit(
                        f"K_IV tau1-tau3 surface mismatch row {index}, {field}: "
                        f"expected {b!r}, got {a!r}"
                    )
            elif (
                math.isnan(float(a))
                and math.isnan(float(b))
                and field in BOUNDARY_NAN_FIELDS
            ):
                continue
            else:
                absolute_tolerance = (
                    1.0e-20 if field == "rss_full"
                    else 1.0e-12 if field.endswith("_ms")
                    else 1.0e-14 if field.endswith("_ma_cm2")
                    else 1.0e-10
                )
                if not math.isclose(
                    float(a), float(b), rel_tol=2.0e-5, abs_tol=absolute_tolerance
                ):
                    raise SystemExit(
                        f"K_IV tau1-tau3 surface mismatch row {index}, {field}: "
                        f"expected {float(b):.12g}, got {float(a):.12g}"
                    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--tau1-grid-points", type=int, default=9)
    parser.add_argument("--tau3-grid-points", type=int, default=2801)
    parser.add_argument("--tau3-min-ms", type=float, default=0.1)
    parser.add_argument("--tau3-max-ms", type=float, default=5.0)
    args = parser.parse_args()

    actual = read_surface(args.actual)
    try:
        validate_tau1_tau3_surface_rows(
            actual,
            tau1_grid_points=args.tau1_grid_points,
            tau3_grid_points=args.tau3_grid_points,
            tau3_min_ms=args.tau3_min_ms,
            tau3_max_ms=args.tau3_max_ms,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if args.expected:
        expected = read_surface(args.expected)
        try:
            validate_tau1_tau3_surface_rows(
                expected,
                tau1_grid_points=args.tau1_grid_points,
                tau3_grid_points=args.tau3_grid_points,
                tau3_min_ms=args.tau3_min_ms,
                tau3_max_ms=args.tau3_max_ms,
            )
        except ValueError as exc:
            raise SystemExit(f"Invalid expected tau1-tau3 surface: {exc}") from exc
        compare_expected(actual, expected)
        print(
            "K_IV tau1-tau3 profile-surface summary matches the committed "
            "three-voltage, 27-slice reference."
        )
    else:
        print(
            "K_IV tau1-tau3 profile-surface structure passed for "
            f"{len(actual)} conditional profile slices."
        )

    for voltage in (-30.0, -60.0, 55.0):
        group = [row for row in actual if row["voltage_mv"] == voltage]
        center = group[len(group) // 2]
        global_row = next(row for row in group if row["is_global_surface_minimum"])
        taus = [row["selected_tau3_ms"] for row in group]
        spans = {
            threshold: [
                row[f"near_minimum_{threshold}pct_objective_span_ms"] for row in group
            ]
            for threshold in (1, 5, 10)
        }
        medians = {
            threshold: sorted(values)[len(values) // 2]
            for threshold, values in spans.items()
        }
        print(
            f"{voltage:g} mV: reference tau1/tau3="
            f"{center['reference_tau1_ms']:.6g}/{center['reference_tau3_ms']:.6g} ms; "
            f"global surface minimum at tau1/tau3="
            f"{global_row['tau1_ms']:.6g}/{global_row['selected_tau3_ms']:.6g} ms; "
            f"tau3 minima across tau1={min(taus):.6g}..{max(taus):.6g} ms; "
            f"median 1%/5%/10% basin widths="
            f"{medians[1]:.6g}/{medians[5]:.6g}/{medians[10]:.6g} ms; "
            f"global-vs-reference tau1-slice RSS increase="
            f"{center['relative_rss_to_surface_min_pct']:.6g}%"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
