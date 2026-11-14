#!/usr/bin/env python3
"""Profile one fixed-tau1 K_IV model-output residual beyond the prior 40-ms grid.

This is a non-source sensitivity diagnostic on deterministic NEURON/VClamp
model output. It is not a human experimental trace refit or a biological
kinetic mechanism.
"""
from __future__ import annotations

import argparse
import csv
import io
import math
from pathlib import Path
from typing import Any

from wilbers_k_iv_multivoltage import (
    read_postpeak_waveforms,
    summarize_tau3_profile_shape,
)
from wilbers_k_iv_three_component import profile_three_exponential_correction

VOLTAGE_MV = 55.0
TAU1_GRID_INDEX = 5
TAU1_MS = 17.44495210313133
TAU2_MS = 450.0
FIELDNAMES = (
    "voltage_mv",
    "tau1_grid_index",
    "tau1_ms",
    "tau2_ms",
    "profile_grid_min_ms",
    "profile_grid_max_ms",
    "profile_grid_points",
    "profile_grid_step_ms",
    "selected_tau3_ms",
    "minimum_at_grid_boundary",
    "rss_full",
    "rmse_full_ma_cm2",
    "rmse_first_10ms_ma_cm2",
    "rmse_after_10ms_ma_cm2",
    "a1_ma_cm2",
    "a2_ma_cm2",
    "a3_ma_cm2",
    "steady_offset_ma_cm2",
    "positive_control_rss_full",
    "positive_control_a3_ma_cm2",
    "positive_control_rss_increase_pct",
    "profile_objective_normalized_curvature_per_ms2",
    "left_neighbor_delta_rss_pct",
    "right_neighbor_delta_rss_pct",
    "near_minimum_1pct_objective_lower_ms",
    "near_minimum_1pct_objective_upper_ms",
    "near_minimum_1pct_objective_span_ms",
    "near_minimum_1pct_objective_point_count",
    "near_minimum_1pct_touches_grid_edge",
    "near_minimum_5pct_objective_lower_ms",
    "near_minimum_5pct_objective_upper_ms",
    "near_minimum_5pct_objective_span_ms",
    "near_minimum_5pct_objective_point_count",
    "near_minimum_5pct_touches_grid_edge",
    "near_minimum_10pct_objective_lower_ms",
    "near_minimum_10pct_objective_upper_ms",
    "near_minimum_10pct_objective_span_ms",
    "near_minimum_10pct_objective_point_count",
    "near_minimum_10pct_touches_grid_edge",
)
BOOL_FIELDS = frozenset(
    {
        "minimum_at_grid_boundary",
        "near_minimum_1pct_touches_grid_edge",
        "near_minimum_5pct_touches_grid_edge",
        "near_minimum_10pct_touches_grid_edge",
    }
)
INT_FIELDS = frozenset(
    {
        "tau1_grid_index",
        "profile_grid_points",
        "near_minimum_1pct_objective_point_count",
        "near_minimum_5pct_objective_point_count",
        "near_minimum_10pct_objective_point_count",
    }
)
NAN_FIELDS = frozenset(
    {
        "profile_objective_normalized_curvature_per_ms2",
        "left_neighbor_delta_rss_pct",
        "right_neighbor_delta_rss_pct",
    }
)


def analyze_fixed_tau1_profile(
    times_ms: Any,
    currents_ma_cm2: Any,
    *,
    tau3_min_ms: float = 0.1,
    tau3_max_ms: float = 120.0,
    tau3_grid_points: int = 34258,
) -> dict[str, Any]:
    """Profile tau3 at the fixed index-5 tau1 value against full-waveform RSS."""
    fit = profile_three_exponential_correction(
        times_ms,
        currents_ma_cm2,
        TAU1_MS,
        tau2_ms=TAU2_MS,
        tau3_min_ms=tau3_min_ms,
        tau3_max_ms=tau3_max_ms,
        grid_points=tau3_grid_points,
    )
    best = fit["best_signed"]
    positive = fit["positive_control"]
    shape = summarize_tau3_profile_shape(VOLTAGE_MV, TAU1_MS, fit["profile"])
    rss = float(best["rss_full"])
    positive_rss = float(positive["rss_full"])
    row: dict[str, Any] = {
        "voltage_mv": VOLTAGE_MV,
        "tau1_grid_index": TAU1_GRID_INDEX,
        "tau1_ms": TAU1_MS,
        "tau2_ms": TAU2_MS,
        "profile_grid_min_ms": float(tau3_min_ms),
        "profile_grid_max_ms": float(tau3_max_ms),
        "profile_grid_points": int(tau3_grid_points),
        "profile_grid_step_ms": float(
            (tau3_max_ms - tau3_min_ms) / (tau3_grid_points - 1)
        ),
        "selected_tau3_ms": float(best["tau3_ms"]),
        "minimum_at_grid_boundary": bool(shape["minimum_at_grid_boundary"]),
        "rss_full": rss,
        "rmse_full_ma_cm2": float(best["rmse_full_ma_cm2"]),
        "rmse_first_10ms_ma_cm2": float(best["rmse_first_10ms_ma_cm2"]),
        "rmse_after_10ms_ma_cm2": float(best["rmse_after_10ms_ma_cm2"]),
        "a1_ma_cm2": float(best["a1_ma_cm2"]),
        "a2_ma_cm2": float(best["a2_ma_cm2"]),
        "a3_ma_cm2": float(best["a3_ma_cm2"]),
        "steady_offset_ma_cm2": float(best["steady_offset_ma_cm2"]),
        "positive_control_rss_full": positive_rss,
        "positive_control_a3_ma_cm2": float(positive["a3_ma_cm2"]),
        "positive_control_rss_increase_pct": 100.0 * (positive_rss / rss - 1.0),
        "profile_objective_normalized_curvature_per_ms2": float(
            shape["profile_objective_normalized_curvature_per_ms2"]
        ),
        "left_neighbor_delta_rss_pct": float(shape["left_neighbor_delta_rss_pct"]),
        "right_neighbor_delta_rss_pct": float(shape["right_neighbor_delta_rss_pct"]),
    }
    for threshold in (1, 5, 10):
        for suffix in (
            "objective_lower_ms",
            "objective_upper_ms",
            "objective_span_ms",
            "objective_point_count",
        ):
            field = f"near_minimum_{threshold}pct_{suffix}"
            row[field] = shape[field]
        row[f"near_minimum_{threshold}pct_touches_grid_edge"] = shape[
            f"near_minimum_{threshold}pct_touches_grid_edge"
        ]
    validate_summary_row(
        row,
        tau3_min_ms=tau3_min_ms,
        tau3_max_ms=tau3_max_ms,
        tau3_grid_points=tau3_grid_points,
    )
    return row


def validate_summary_row(
    row: dict[str, Any],
    *,
    tau3_min_ms: float,
    tau3_max_ms: float,
    tau3_grid_points: int,
) -> None:
    """Validate the fixed-parameter contract and basin geometry."""
    if set(row) != set(FIELDNAMES):
        raise ValueError("Fixed-tau1 K_IV summary schema mismatch")
    if (
        row["voltage_mv"] != VOLTAGE_MV
        or row["tau1_grid_index"] != TAU1_GRID_INDEX
        or not math.isclose(row["tau1_ms"], TAU1_MS, rel_tol=0.0, abs_tol=1e-12)
        or row["tau2_ms"] != TAU2_MS
    ):
        raise ValueError("Fixed-tau1 K_IV profile changed its predeclared command or tau values")
    if (
        isinstance(tau3_grid_points, bool)
        or int(tau3_grid_points) != tau3_grid_points
        or tau3_grid_points < 3
        or not math.isfinite(tau3_min_ms)
        or not math.isfinite(tau3_max_ms)
        or tau3_min_ms <= 0.0
        or tau3_max_ms <= tau3_min_ms
    ):
        raise ValueError("Fixed-tau1 K_IV profile grid declaration is invalid")
    if row["profile_grid_points"] != int(tau3_grid_points):
        raise ValueError("Fixed-tau1 K_IV profile grid-point count changed")
    if not math.isclose(row["profile_grid_min_ms"], tau3_min_ms, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("Fixed-tau1 K_IV profile lower bound changed")
    if not math.isclose(row["profile_grid_max_ms"], tau3_max_ms, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("Fixed-tau1 K_IV profile upper bound changed")
    expected_step = (tau3_max_ms - tau3_min_ms) / (tau3_grid_points - 1)
    if not math.isclose(row["profile_grid_step_ms"], expected_step, rel_tol=1e-10, abs_tol=1e-14):
        raise ValueError("Fixed-tau1 K_IV profile grid step is inconsistent")
    if not (tau3_min_ms <= row["selected_tau3_ms"] <= tau3_max_ms):
        raise ValueError("Fixed-tau1 K_IV selected tau3 lies outside its grid")
    expected_boundary = (
        math.isclose(row["selected_tau3_ms"], tau3_min_ms, rel_tol=0.0, abs_tol=1e-12)
        or math.isclose(row["selected_tau3_ms"], tau3_max_ms, rel_tol=0.0, abs_tol=1e-12)
    )
    if row["minimum_at_grid_boundary"] is not expected_boundary:
        raise ValueError("Fixed-tau1 K_IV minimum boundary flag is inconsistent")

    for field in FIELDNAMES:
        if field in BOOL_FIELDS:
            if not isinstance(row[field], bool):
                raise ValueError(f"Fixed-tau1 K_IV Boolean field is invalid: {field}")
        elif field in INT_FIELDS:
            if not isinstance(row[field], int) or isinstance(row[field], bool):
                raise ValueError(f"Fixed-tau1 K_IV integer field is invalid: {field}")
        else:
            value = float(row[field])
            if not math.isfinite(value) and not (
                row["minimum_at_grid_boundary"] and field in NAN_FIELDS and math.isnan(value)
            ):
                raise ValueError(f"Fixed-tau1 K_IV non-finite field: {field}")

    for field in (
        "rss_full",
        "rmse_full_ma_cm2",
        "rmse_first_10ms_ma_cm2",
        "rmse_after_10ms_ma_cm2",
    ):
        if row[field] <= 0.0:
            raise ValueError(f"Fixed-tau1 K_IV field must be positive: {field}")
    for field in ("a1_ma_cm2", "a2_ma_cm2", "steady_offset_ma_cm2"):
        if row[field] < -1e-14:
            raise ValueError(f"Fixed-tau1 K_IV constrained coefficient is negative: {field}")
    if row["positive_control_a3_ma_cm2"] < -1e-14:
        raise ValueError("Fixed-tau1 K_IV nonnegative control returned a negative extra coefficient")
    if row["positive_control_rss_full"] < row["rss_full"] * (1.0 - 2e-8):
        raise ValueError("Fixed-tau1 K_IV nonnegative control improved the signed optimum")

    previous_span = -1.0
    previous_lower = math.inf
    previous_upper = -math.inf
    for threshold in (1, 5, 10):
        lower = row[f"near_minimum_{threshold}pct_objective_lower_ms"]
        upper = row[f"near_minimum_{threshold}pct_objective_upper_ms"]
        span = row[f"near_minimum_{threshold}pct_objective_span_ms"]
        count = row[f"near_minimum_{threshold}pct_objective_point_count"]
        touches = row[f"near_minimum_{threshold}pct_touches_grid_edge"]
        if not (tau3_min_ms <= lower <= row["selected_tau3_ms"] <= upper <= tau3_max_ms):
            raise ValueError(f"Fixed-tau1 K_IV {threshold}% basin does not enclose the selected minimum")
        if not math.isclose(span, upper - lower, rel_tol=0.0, abs_tol=1e-10):
            raise ValueError(f"Fixed-tau1 K_IV {threshold}% basin span is inconsistent")
        if count < 1:
            raise ValueError(f"Fixed-tau1 K_IV {threshold}% basin has no grid points")
        expected_touches = math.isclose(lower, tau3_min_ms, abs_tol=1e-12) or math.isclose(
            upper, tau3_max_ms, abs_tol=1e-12
        )
        if touches is not expected_touches:
            raise ValueError(f"Fixed-tau1 K_IV {threshold}% basin edge flag is inconsistent")
        if span < previous_span - 1e-12 or lower > previous_lower + 1e-12 or upper < previous_upper - 1e-12:
            raise ValueError("Fixed-tau1 K_IV near-minimum basins are not nested")
        previous_span, previous_lower, previous_upper = span, lower, upper


def summary_csv_text(row: dict[str, Any]) -> str:
    """Serialize one summary row with explicit provenance and method notes."""
    validate_summary_row(
        row,
        tau3_min_ms=float(row["profile_grid_min_ms"]),
        tau3_max_ms=float(row["profile_grid_max_ms"]),
        tau3_grid_points=int(row["profile_grid_points"]),
    )
    output = io.StringIO(newline="")
    output.write(
        "# Fixed-tau1 conditional K_IV profile for the predeclared +55 mV waveform.\n"
        "# Input is deterministic NEURON 9.0.2/VClamp output from DataverseNL v3.0 pure-human K source replay; not raw human experimental current.\n"
        "# tau1 is fixed at 17.44495210313133 ms (tau1 grid index 5 of the existing nine-node, 6% local window); tau2 is fixed at 450 ms.\n"
        "# tau3 is profiled on the declared uniform grid; all coefficients are refit against full-waveform RSS at each point.\n"
        "# a1, a2 and steady offset are constrained nonnegative; a3 is signed. The positive control refits at the signed optimum with a3 constrained nonnegative.\n"
        "# 1%/5%/10% intervals are contiguous relative-full-RSS grid basins, not statistical confidence intervals. Early/late RMSE are diagnostics, not alternate objectives.\n"
        "# This is a numerical sensitivity diagnostic on model-generated current, not biological kinetics or validation.\n"
    )
    writer = csv.DictWriter(output, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerow(row)
    return output.getvalue()


def read_summary(path: Path) -> dict[str, Any]:
    """Read and type-check the canonical one-row CSV representation."""
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(
            line for line in stream if line.strip() and not line.lstrip().startswith("#")
        )
        if tuple(reader.fieldnames or ()) != FIELDNAMES:
            raise ValueError(f"Fixed-tau1 K_IV summary schema mismatch: {path}")
        rows = list(reader)
    if len(rows) != 1:
        raise ValueError(f"Fixed-tau1 K_IV summary must contain exactly one row: {path}")
    parsed: dict[str, Any] = {}
    for field, value in rows[0].items():
        if field in BOOL_FIELDS:
            if value not in ("True", "False"):
                raise ValueError(f"Invalid Boolean in fixed-tau1 K_IV summary: {field}")
            parsed[field] = value == "True"
        elif field in INT_FIELDS:
            parsed[field] = int(value)
        else:
            parsed[field] = float(value)
    return parsed


def compare_expected(actual: dict[str, Any], expected: dict[str, Any]) -> None:
    """Strictly compare the regenerated summary with the committed reference."""
    for field in FIELDNAMES:
        found, reference = actual[field], expected[field]
        if field in BOOL_FIELDS or field in INT_FIELDS:
            if found != reference:
                raise ValueError(
                    f"Fixed-tau1 K_IV reference mismatch for {field}: expected {reference!r}, got {found!r}"
                )
        elif (
            math.isnan(float(found))
            and math.isnan(float(reference))
            and field in NAN_FIELDS
        ):
            continue
        else:
            abs_tol = (
                1e-20
                if field in ("rss_full", "positive_control_rss_full")
                else 1e-14
                if field.endswith("_ma_cm2")
                else 1e-10
                if field in ("left_neighbor_delta_rss_pct", "right_neighbor_delta_rss_pct")
                else 1e-12
            )
            if not math.isclose(float(found), float(reference), rel_tol=2e-5, abs_tol=abs_tol):
                raise ValueError(
                    f"Fixed-tau1 K_IV reference mismatch for {field}: "
                    f"expected {float(reference):.12g}, got {float(found):.12g}"
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--waveforms", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tau3-min-ms", type=float, default=0.1)
    parser.add_argument("--tau3-max-ms", type=float, default=120.0)
    parser.add_argument("--tau3-grid-points", type=int, default=34258)
    parser.add_argument("--expected", type=Path)
    args = parser.parse_args()

    waveforms = read_postpeak_waveforms(args.waveforms)
    times, _, currents = waveforms[VOLTAGE_MV]
    row = analyze_fixed_tau1_profile(
        times,
        currents,
        tau3_min_ms=args.tau3_min_ms,
        tau3_max_ms=args.tau3_max_ms,
        tau3_grid_points=args.tau3_grid_points,
    )
    content = summary_csv_text(row)
    output_path = args.output.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    if args.expected:
        expected = read_summary(args.expected)
        compare_expected(row, expected)
        print("Fixed-tau1 K_IV profile matches every field of the committed reference.")
    print("BEGIN_HUMANJS_FIXED_TAU1_K_IV_PROFILE")
    print(content, end="")
    print("END_HUMANJS_FIXED_TAU1_K_IV_PROFILE")
    print(
        f"Selected tau3={row['selected_tau3_ms']:.9g} ms; "
        f"1%/5%/10% basin spans="
        f"{row['near_minimum_1pct_objective_span_ms']:.9g}/"
        f"{row['near_minimum_5pct_objective_span_ms']:.9g}/"
        f"{row['near_minimum_10pct_objective_span_ms']:.9g} ms; "
        f"5%/10% edge flags="
        f"{row['near_minimum_5pct_touches_grid_edge']}/"
        f"{row['near_minimum_10pct_touches_grid_edge']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
