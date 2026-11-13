#!/usr/bin/env python3
"""Cross-voltage audit of short-time K_IV post-peak model residuals.

All waveforms are produced by the unchanged Dataverse human K mechanism and
original NEURON/VClamp K_IV command protocol. The extra exponential remains a
signed descriptive residual correction, not a channel state or biological
kinetic component.
"""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from wilbers_k_iv_fit_diagnostics import profile_k_iv_postpeak_tau
from wilbers_k_iv_three_component import (
    profile_three_exponential_correction,
)

K_IV_MULTIVOLTAGE_TARGETS_MV = tuple(float(v) for v in range(-75, 60, 5))
K_IV_MULTIVOLTAGE_FIELDNAMES = (
    "voltage_mv",
    "sample_count",
    "source_start_ms",
    "source_end_ms",
    "relative_end_ms",
    "peak_current_ma_cm2",
    "coarse_tau1_ms",
    "local_tau1_ms",
    "local_tau1_rmse_ma_cm2",
    "tau3_ms",
    "a1_ma_cm2",
    "a2_ma_cm2",
    "a3_ma_cm2",
    "steady_offset_ma_cm2",
    "baseline_full_rmse_ma_cm2",
    "corrected_full_rmse_ma_cm2",
    "full_improvement_pct",
    "baseline_first_10ms_rmse_ma_cm2",
    "corrected_first_10ms_rmse_ma_cm2",
    "first_10ms_improvement_pct",
    "baseline_after_10ms_rmse_ma_cm2",
    "corrected_after_10ms_rmse_ma_cm2",
    "after_10ms_improvement_pct",
    "baseline_r2_full",
    "corrected_r2_full",
    "a1_shift_pct",
    "a2_shift_pct",
    "offset_shift_pct",
    "extra_amplitude_pct_peak",
    "positive_control_a3_ma_cm2",
    "positive_control_full_rmse_ma_cm2",
    "positive_control_improvement_pct",
    "coarse_profile_points",
    "local_profile_points",
    "short_component_profile_points",
    "coarse_profile_at_boundary",
    "local_profile_at_boundary",
    "signed_extra_is_negative",
    "nonnegative_control_collapsed",
    "tau3_profile_min_ms",
    "tau3_profile_max_ms",
    "tau3_profile_at_boundary",
)

K_IV_TAU3_PROFILE_SHAPE_FIELDNAMES = (
    "voltage_mv",
    "tau1_ms",
    "selected_tau3_ms",
    "profile_grid_min_ms",
    "profile_grid_max_ms",
    "profile_grid_points",
    "profile_grid_step_ms",
    "minimum_at_grid_boundary",
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

K_IV_TAU3_PROFILE_SHAPE_INT_FIELDS = frozenset(["profile_grid_points","near_minimum_1pct_objective_point_count","near_minimum_5pct_objective_point_count","near_minimum_10pct_objective_point_count"])
K_IV_TAU3_PROFILE_SHAPE_BOOL_FIELDS = frozenset(["minimum_at_grid_boundary","near_minimum_1pct_touches_grid_edge","near_minimum_5pct_touches_grid_edge","near_minimum_10pct_touches_grid_edge"])

K_IV_TAU1_TAU3_SURFACE_VOLTAGES_MV = (-30.0, -60.0, 55.0)
K_IV_TAU1_TAU3_SURFACE_FIELDNAMES = (
    "voltage_mv",
    "tau1_grid_index",
    "tau1_grid_points",
    "coarse_tau1_ms",
    "tau1_window_min_ms",
    "tau1_window_max_ms",
    "reference_tau1_ms",
    "reference_tau3_ms",
    "tau1_ms",
    "tau1_offset_from_reference_pct",
    "tau1_at_window_boundary",
    "tau3_grid_points",
    "tau3_min_ms",
    "tau3_max_ms",
    "selected_tau3_ms",
    "tau3_minimum_at_grid_boundary",
    "rss_full",
    "relative_rss_to_surface_min_pct",
    "rmse_full_ma_cm2",
    "rmse_first_10ms_ma_cm2",
    "rmse_after_10ms_ma_cm2",
    "a1_ma_cm2",
    "a2_ma_cm2",
    "a3_ma_cm2",
    "steady_offset_ma_cm2",
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
    "is_global_surface_minimum",
)
K_IV_TAU1_TAU3_SURFACE_INT_FIELDS = frozenset({
    "tau1_grid_index",
    "tau1_grid_points",
    "tau3_grid_points",
    "near_minimum_1pct_objective_point_count",
    "near_minimum_5pct_objective_point_count",
    "near_minimum_10pct_objective_point_count",
})
K_IV_TAU1_TAU3_SURFACE_BOOL_FIELDS = frozenset({
    "tau1_at_window_boundary",
    "tau3_minimum_at_grid_boundary",
    "near_minimum_1pct_touches_grid_edge",
    "near_minimum_5pct_touches_grid_edge",
    "near_minimum_10pct_touches_grid_edge",
    "is_global_surface_minimum",
})


def summarize_tau3_profile_shape(
    voltage_mv: float,
    tau1_ms: float,
    profile: list[dict[str, Any]],
) -> dict[str, Any]:
    """Describe the local full-waveform RSS profile around its selected tau3.

    Threshold spans are contiguous grid basins around the selected minimum.
    They are descriptive objective-shape summaries, not confidence intervals.
    """
    if len(profile) < 3:
        raise ValueError("K_IV tau3 profile shape requires at least three grid points")
    tau = np.asarray([float(row["tau3_ms"]) for row in profile], dtype=float)
    rss = np.asarray([float(row["rss_full"]) for row in profile], dtype=float)
    if not np.isfinite(tau).all() or not np.isfinite(rss).all() or np.any(rss <= 0.0):
        raise ValueError("K_IV tau3 profile shape requires finite positive RSS values")
    steps = np.diff(tau)
    if np.any(steps <= 0.0) or not np.allclose(
        steps, steps[0], rtol=1.0e-10, atol=1.0e-14
    ):
        raise ValueError("K_IV tau3 profile shape requires an increasing uniform grid")
    best_index = int(np.argmin(rss))
    best_rss = float(rss[best_index])
    normalized_delta = rss / best_rss - 1.0
    step_ms = float(steps[0])
    at_boundary = best_index in (0, len(profile) - 1)
    if at_boundary:
        curvature = math.nan
        left_delta = math.nan
        right_delta = math.nan
    else:
        curvature = float(
            (
                normalized_delta[best_index - 1]
                - 2.0 * normalized_delta[best_index]
                + normalized_delta[best_index + 1]
            )
            / (step_ms * step_ms)
        )
        left_delta = 100.0 * float(normalized_delta[best_index - 1])
        right_delta = 100.0 * float(normalized_delta[best_index + 1])

    result: dict[str, Any] = {
        "voltage_mv": float(voltage_mv),
        "tau1_ms": float(tau1_ms),
        "selected_tau3_ms": float(tau[best_index]),
        "profile_grid_min_ms": float(tau[0]),
        "profile_grid_max_ms": float(tau[-1]),
        "profile_grid_points": int(len(profile)),
        "profile_grid_step_ms": step_ms,
        "minimum_at_grid_boundary": bool(at_boundary),
        "profile_objective_normalized_curvature_per_ms2": curvature,
        "left_neighbor_delta_rss_pct": left_delta,
        "right_neighbor_delta_rss_pct": right_delta,
    }
    for threshold_pct in (1, 5, 10):
        threshold = threshold_pct / 100.0
        left = best_index
        right = best_index
        while left > 0 and normalized_delta[left - 1] <= threshold:
            left -= 1
        while right < len(profile) - 1 and normalized_delta[right + 1] <= threshold:
            right += 1
        lower = float(tau[left])
        upper = float(tau[right])
        result.update({
            f"near_minimum_{threshold_pct}pct_objective_lower_ms": lower,
            f"near_minimum_{threshold_pct}pct_objective_upper_ms": upper,
            f"near_minimum_{threshold_pct}pct_objective_span_ms": upper - lower,
            f"near_minimum_{threshold_pct}pct_objective_point_count": right - left + 1,
            f"near_minimum_{threshold_pct}pct_touches_grid_edge": bool(
                left == 0 or right == len(profile) - 1
            ),
        })
    return result


def tau3_profile_shape_csv_text(rows: list[dict[str, Any]]) -> str:
    """Serialize compact per-voltage near-minimum objective-shape diagnostics."""
    import io

    output = io.StringIO()
    output.write(
        "# Exact post-peak model-current waveforms from the unchanged DataverseNL v3.0 pure-human K source replay (NEURON 9.0.2/VClamp); not raw experimental current.\n"
    )
    output.write(
        "# At each tau3 grid point all coefficients are refit to the full waveform; per-command tau1 is fixed at its independently profiled value and source tau2=450 ms.\n"
    )
    output.write(
        "# Basins are contiguous grid points around the selected minimum with relative full-waveform RSS increases <=1%, <=5%, and <=10%; local curvature is a normalized central second difference.\n"
    )
    output.write(
        "# These deterministic objective-shape spans and curvature values are not statistical confidence intervals or biological uncertainty estimates.\n"
    )
    writer = csv.DictWriter(
        output,
        fieldnames=K_IV_TAU3_PROFILE_SHAPE_FIELDNAMES,
        extrasaction="raise",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def validate_tau3_profile_shape_rows(rows: list[dict[str, Any]]) -> None:
    """Validate per-command local objective-shape summaries and nested basins."""
    if tuple(row.get("voltage_mv") for row in rows) != K_IV_MULTIVOLTAGE_TARGETS_MV:
        raise ValueError("K_IV tau3 profile-shape summary must preserve all 27 ordered commands")
    for row in rows:
        for field in K_IV_TAU3_PROFILE_SHAPE_FIELDNAMES:
            value = row.get(field)
            if field in K_IV_TAU3_PROFILE_SHAPE_INT_FIELDS | K_IV_TAU3_PROFILE_SHAPE_BOOL_FIELDS:
                continue
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise ValueError(f"K_IV tau3 profile-shape field is non-finite: {field}")
        if row["profile_grid_points"] < 3 or row["profile_grid_step_ms"] <= 0.0:
            raise ValueError("K_IV tau3 profile-shape grid is underspecified")
        if row["minimum_at_grid_boundary"]:
            raise ValueError("K_IV extended tau3 minimum remains on a profile boundary")
        selected = row["selected_tau3_ms"]
        if not (row["profile_grid_min_ms"] < selected < row["profile_grid_max_ms"]):
            raise ValueError("K_IV tau3 selected minimum is not interior to its declared grid")
        if row["profile_objective_normalized_curvature_per_ms2"] < -1.0e-8:
            raise ValueError("K_IV tau3 selected minimum has negative local RSS curvature")
        if row["left_neighbor_delta_rss_pct"] < -1.0e-8 or row["right_neighbor_delta_rss_pct"] < -1.0e-8:
            raise ValueError("K_IV tau3 neighboring objective is below the selected minimum")
        previous_lower = math.inf
        previous_upper = -math.inf
        previous_count = 0
        for threshold_pct in (1, 5, 10):
            lower = row[f"near_minimum_{threshold_pct}pct_objective_lower_ms"]
            upper = row[f"near_minimum_{threshold_pct}pct_objective_upper_ms"]
            span = row[f"near_minimum_{threshold_pct}pct_objective_span_ms"]
            count = row[f"near_minimum_{threshold_pct}pct_objective_point_count"]
            touches_edge = row[f"near_minimum_{threshold_pct}pct_touches_grid_edge"]
            if not lower <= selected <= upper or upper < lower:
                raise ValueError("K_IV tau3 near-minimum basin does not contain its selected minimum")
            if not math.isclose(span, upper - lower, rel_tol=0.0, abs_tol=1.0e-12):
                raise ValueError("K_IV tau3 near-minimum basin span is inconsistent")
            if count < 1 or count < previous_count or count > row["profile_grid_points"]:
                raise ValueError("K_IV tau3 near-minimum basin grid-point count is invalid")
            if lower > previous_lower + 1.0e-12 or upper < previous_upper - 1.0e-12:
                raise ValueError("K_IV tau3 near-minimum basins do not expand with objective threshold")
            if not isinstance(touches_edge, bool):
                raise ValueError("K_IV tau3 near-minimum grid-edge flag is not boolean")
            previous_lower, previous_upper, previous_count = lower, upper, count



def _finite_vector(values: Any, field: str) -> np.ndarray:
    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1 or len(vector) < 100 or not np.isfinite(vector).all():
        raise ValueError(f"{field} must contain at least 100 finite one-dimensional samples")
    return vector


def analyze_k_iv_waveform(
    voltage_mv: float,
    times_ms: Any,
    source_times_ms: Any,
    currents_ma_cm2: Any,
    *,
    coarse_profile_points: int = 901,
    local_profile_points: int = 801,
    short_profile_points: int = 801,
    tau3_min_ms: float = 0.6,
    tau3_max_ms: float = 2.0,
) -> dict[str, Any]:
    """Profile long tau1, then test the signed short residual over all samples."""
    if not math.isfinite(voltage_mv):
        raise ValueError("K_IV command voltage must be finite")
    times = _finite_vector(times_ms, "relative time")
    source_times = _finite_vector(source_times_ms, "source time")
    current = _finite_vector(currents_ma_cm2, "current")
    if times.shape != source_times.shape or times.shape != current.shape:
        raise ValueError("K_IV waveform time/current columns must have equal lengths")
    if np.any(np.diff(times) <= 0.0) or np.any(np.diff(source_times) <= 0.0):
        raise ValueError("K_IV waveform clocks must be strictly increasing")
    if not np.allclose(
        source_times - source_times[0], times, atol=1.0e-8, rtol=0.0
    ):
        raise ValueError("K_IV shifted and original NEURON clocks do not align")
    if not np.allclose(np.diff(times), 0.1, atol=1.0e-9, rtol=0.0):
        raise ValueError("K_IV post-peak samples must retain the 0.1-ms source spacing")
    if times[0] < -1.0e-9 or np.any(times < 0.0):
        raise ValueError("K_IV post-peak time must start at zero")

    coarse = profile_k_iv_postpeak_tau(
        voltage_mv,
        times,
        current,
        tau_min_ms=0.05,
        tau_max_ms=1200.0,
        grid_points=coarse_profile_points,
    )
    coarse_best = min(coarse, key=lambda row: row["fit_rmse_ma_cm2"])
    coarse_tau = float(coarse_best["tau1_ms"])
    coarse_index = coarse.index(coarse_best)
    coarse_at_boundary = coarse_index in (0, len(coarse) - 1)

    # Refine only a neighborhood of the independently profiled coarse minimum.
    # A 6% multiplicative window keeps a similar relative scale at each voltage.
    local_min = max(0.05, coarse_tau * 0.94)
    local_max = min(1200.0, coarse_tau * 1.06)
    if local_max <= local_min:
        raise ValueError("K_IV local tau1 refinement window is degenerate")
    local = profile_k_iv_postpeak_tau(
        voltage_mv,
        times,
        current,
        tau_min_ms=local_min,
        tau_max_ms=local_max,
        grid_points=local_profile_points,
    )
    local_best = min(local, key=lambda row: row["fit_rmse_ma_cm2"])
    local_index = local.index(local_best)
    local_at_boundary = local_index in (0, len(local) - 1)
    tau1 = float(local_best["tau1_ms"])

    three = profile_three_exponential_correction(
        times,
        current,
        tau1,
        tau2_ms=450.0,
        tau3_min_ms=tau3_min_ms,
        tau3_max_ms=tau3_max_ms,
        grid_points=short_profile_points,
    )
    baseline = three["baseline"]
    signed = three["best_signed"]
    positive = three["positive_control"]

    def reduction(base: float, improved: float) -> float:
        if not math.isfinite(base) or base <= 0.0:
            raise ValueError("K_IV residual RMSE baseline must be finite and positive")
        return 100.0 * (1.0 - improved / base)

    peak = float(np.max(np.abs(current)))
    if not math.isfinite(peak) or peak <= 0.0:
        raise ValueError("K_IV peak current must be finite and nonzero")
    a1_shift = 100.0 * (signed["a1_ma_cm2"] / baseline["a1_ma_cm2"] - 1.0)
    a2_shift = 100.0 * (signed["a2_ma_cm2"] / baseline["a2_ma_cm2"] - 1.0)
    offset_shift = 100.0 * (
        signed["steady_offset_ma_cm2"] / baseline["steady_offset_ma_cm2"] - 1.0
    )
    positive_collapsed = abs(float(positive["a3_ma_cm2"])) <= 1.0e-13
    positive_control_improvement = reduction(
        baseline["rmse_full_ma_cm2"], positive["rmse_full_ma_cm2"]
    )
    # The control collapses to the baseline mathematically; report sub-1e-8%
    # differences as zero rather than preserving floating-point solver residue.
    if abs(positive_control_improvement) < 1.0e-8:
        positive_control_improvement = 0.0

    return {
        "voltage_mv": float(voltage_mv),
        "sample_count": int(len(times)),
        "source_start_ms": float(source_times[0]),
        "source_end_ms": float(source_times[-1]),
        "relative_end_ms": float(times[-1]),
        "peak_current_ma_cm2": peak,
        "coarse_tau1_ms": coarse_tau,
        "local_tau1_ms": tau1,
        "local_tau1_rmse_ma_cm2": float(local_best["fit_rmse_ma_cm2"]),
        "tau3_ms": float(signed["tau3_ms"]),
        "a1_ma_cm2": float(signed["a1_ma_cm2"]),
        "a2_ma_cm2": float(signed["a2_ma_cm2"]),
        "a3_ma_cm2": float(signed["a3_ma_cm2"]),
        "steady_offset_ma_cm2": float(signed["steady_offset_ma_cm2"]),
        "baseline_full_rmse_ma_cm2": float(baseline["rmse_full_ma_cm2"]),
        "corrected_full_rmse_ma_cm2": float(signed["rmse_full_ma_cm2"]),
        "full_improvement_pct": reduction(
            baseline["rmse_full_ma_cm2"], signed["rmse_full_ma_cm2"]
        ),
        "baseline_first_10ms_rmse_ma_cm2": float(
            baseline["rmse_first_10ms_ma_cm2"]
        ),
        "corrected_first_10ms_rmse_ma_cm2": float(
            signed["rmse_first_10ms_ma_cm2"]
        ),
        "first_10ms_improvement_pct": reduction(
            baseline["rmse_first_10ms_ma_cm2"],
            signed["rmse_first_10ms_ma_cm2"],
        ),
        "baseline_after_10ms_rmse_ma_cm2": float(
            baseline["rmse_after_10ms_ma_cm2"]
        ),
        "corrected_after_10ms_rmse_ma_cm2": float(
            signed["rmse_after_10ms_ma_cm2"]
        ),
        "after_10ms_improvement_pct": reduction(
            baseline["rmse_after_10ms_ma_cm2"],
            signed["rmse_after_10ms_ma_cm2"],
        ),
        "baseline_r2_full": float(baseline["r2_full"]),
        "corrected_r2_full": float(signed["r2_full"]),
        "a1_shift_pct": float(a1_shift),
        "a2_shift_pct": float(a2_shift),
        "offset_shift_pct": float(offset_shift),
        "extra_amplitude_pct_peak": 100.0 * abs(float(signed["a3_ma_cm2"])) / peak,
        "positive_control_a3_ma_cm2": float(positive["a3_ma_cm2"]),
        "positive_control_full_rmse_ma_cm2": float(
            positive["rmse_full_ma_cm2"]
        ),
        "positive_control_improvement_pct": float(positive_control_improvement),
        "coarse_profile_points": int(coarse_profile_points),
        "local_profile_points": int(local_profile_points),
        "short_component_profile_points": int(short_profile_points),
        "coarse_profile_at_boundary": bool(coarse_at_boundary),
        "local_profile_at_boundary": bool(local_at_boundary),
        "signed_extra_is_negative": bool(signed["a3_ma_cm2"] < 0.0),
        "nonnegative_control_collapsed": bool(positive_collapsed),
        "tau3_profile_min_ms": float(tau3_min_ms),
        "tau3_profile_max_ms": float(tau3_max_ms),
        "tau3_profile_at_boundary": bool(
            math.isclose(signed["tau3_ms"], tau3_min_ms, rel_tol=0.0, abs_tol=1.0e-12)
            or math.isclose(signed["tau3_ms"], tau3_max_ms, rel_tol=0.0, abs_tol=1.0e-12)
        ),
        "tau3_profile_shape": summarize_tau3_profile_shape(
            voltage_mv, tau1, three["profile"]
        ),
    }


def read_postpeak_waveforms(
    path: Path,
) -> dict[float, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Read the exact post-peak vectors emitted by the NEURON source runner."""
    grouped: dict[float, list[tuple[float, float, float]]] = defaultdict(list)
    preamble = path.read_text(encoding="utf-8").splitlines()[:10]
    preamble_text = "\n".join(preamble)
    for marker in (
        "DataverseNL v3.0",
        "615595a270c6170987757cd35743f5d5b5b2af0e",
        "d299b3430ecda7a94f6d1c37ac76b2878052c7d5",
        "NEURON 9.0.2",
    ):
        if marker not in preamble_text:
            raise ValueError(f"K_IV post-peak waveform provenance marker missing: {marker}")
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = csv.DictReader(
            line for line in stream if line.strip() and not line.lstrip().startswith("#")
        )
        expected = {
            "voltage_mv",
            "time_since_peak_ms",
            "source_simulation_time_ms",
            "observed_current_ma_cm2",
        }
        if not rows.fieldnames or not expected.issubset(rows.fieldnames):
            raise ValueError("K_IV post-peak waveform CSV schema mismatch")
        for row in rows:
            try:
                values = (
                    float(row["time_since_peak_ms"]),
                    float(row["source_simulation_time_ms"]),
                    float(row["observed_current_ma_cm2"]),
                )
                voltage = float(row["voltage_mv"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("K_IV post-peak waveform contains an invalid number") from exc
            if not all(math.isfinite(value) for value in (*values, voltage)):
                raise ValueError("K_IV post-peak waveform contains a non-finite value")
            grouped[voltage].append(values)

    if tuple(sorted(grouped)) != K_IV_MULTIVOLTAGE_TARGETS_MV:
        raise ValueError(
            "K_IV post-peak waveform must contain all 27 finite-positive source-fit "
            "commands from -75 to +55 mV; "
            f"found {tuple(sorted(grouped))}"
        )
    result = {}
    for voltage in K_IV_MULTIVOLTAGE_TARGETS_MV:
        entries = grouped[voltage]
        times = np.asarray([entry[0] for entry in entries], dtype=float)
        source_times = np.asarray([entry[1] for entry in entries], dtype=float)
        currents = np.asarray([entry[2] for entry in entries], dtype=float)
        _finite_vector(times, f"{voltage:g}-mV relative time")
        _finite_vector(source_times, f"{voltage:g}-mV source time")
        _finite_vector(currents, f"{voltage:g}-mV current")
        if np.any(np.diff(times) <= 0.0) or np.any(np.diff(source_times) <= 0.0):
            raise ValueError(f"K_IV {voltage:g}-mV waveform times are not increasing")
        if not math.isclose(float(times[0]), 0.0, abs_tol=1.0e-9):
            raise ValueError(f"K_IV {voltage:g}-mV shifted waveform does not start at zero")
        result[voltage] = (times, source_times, currents)
    return result


def analyze_postpeak_waveforms(
    path: Path,
    *,
    coarse_profile_points: int = 901,
    local_profile_points: int = 801,
    short_profile_points: int = 801,
    tau3_min_ms: float = 0.6,
    tau3_max_ms: float = 2.0,
) -> list[dict[str, Any]]:
    waveforms = read_postpeak_waveforms(path)
    return [
        analyze_k_iv_waveform(
            voltage,
            *waveforms[voltage],
            coarse_profile_points=coarse_profile_points,
            local_profile_points=local_profile_points,
            short_profile_points=short_profile_points,
            tau3_min_ms=tau3_min_ms,
            tau3_max_ms=tau3_max_ms,
        )
        for voltage in K_IV_MULTIVOLTAGE_TARGETS_MV
    ]





def _local_tau1_neighborhood(
    coarse_tau1_ms: float,
    reference_tau1_ms: float,
    grid_points: int,
) -> tuple[np.ndarray, float, float]:
    """Build a tau1 grid confined to the already defined 6% local window."""
    if (
        not math.isfinite(coarse_tau1_ms)
        or not math.isfinite(reference_tau1_ms)
        or coarse_tau1_ms <= 0.0
        or grid_points < 3
        or grid_points % 2 == 0
    ):
        raise ValueError("K_IV tau1 surface requires a positive odd grid of at least three points")
    lower = max(0.05, coarse_tau1_ms * 0.94)
    upper = min(1200.0, coarse_tau1_ms * 1.06)
    if not lower < reference_tau1_ms < upper:
        raise ValueError("K_IV reference tau1 must lie inside its pre-existing 6% neighborhood")
    half = (grid_points - 1) // 2
    left = np.linspace(lower, reference_tau1_ms, half + 1)
    right = np.linspace(reference_tau1_ms, upper, half + 1)
    grid = np.concatenate((left, right[1:]))
    return grid, float(lower), float(upper)


def analyze_tau1_tau3_surface(
    waveforms: dict[float, tuple[np.ndarray, np.ndarray, np.ndarray]],
    baseline_rows: list[dict[str, Any]],
    *,
    tau1_grid_points: int = 9,
    tau3_min_ms: float = 0.1,
    tau3_max_ms: float = 5.0,
    tau3_grid_points: int = 2801,
) -> list[dict[str, Any]]:
    """Profile tau3 while tau1 varies within three predeclared local windows.

    Each row is one tau1 slice of the conditional tau3 profile surface. All
    coefficients are refit against the complete waveform at every tau3 grid
    point. The stored row captures that slice's minimum, basin shape and
    full/early/late residual diagnostics; it is not a statistical uncertainty
    region or biological parameter estimate.
    """
    if tuple(sorted(waveforms)) != K_IV_MULTIVOLTAGE_TARGETS_MV:
        raise ValueError("K_IV tau1-tau3 surface requires all 27 source-fit waveforms")
    if tuple(row.get("voltage_mv") for row in baseline_rows) != K_IV_MULTIVOLTAGE_TARGETS_MV:
        raise ValueError("K_IV tau1-tau3 surface requires the ordered 27-row baseline profile")
    if (
        not math.isfinite(tau3_min_ms)
        or not math.isfinite(tau3_max_ms)
        or tau3_min_ms <= 0.0
        or tau3_max_ms <= tau3_min_ms
    ):
        raise ValueError("K_IV surface tau3 bounds must be finite, positive, and increasing")
    if (
        isinstance(tau3_grid_points, bool)
        or int(tau3_grid_points) != tau3_grid_points
        or tau3_grid_points < 3
    ):
        raise ValueError("K_IV surface tau3 grid must contain at least three integer points")
    if (
        isinstance(tau1_grid_points, bool)
        or int(tau1_grid_points) != tau1_grid_points
        or tau1_grid_points < 3
        or tau1_grid_points % 2 == 0
    ):
        raise ValueError("K_IV surface tau1 grid must contain an odd number of at least three points")

    baseline_by_voltage = {float(row["voltage_mv"]): row for row in baseline_rows}
    output: list[dict[str, Any]] = []
    for voltage in K_IV_TAU1_TAU3_SURFACE_VOLTAGES_MV:
        baseline = baseline_by_voltage[voltage]
        coarse_tau1 = float(baseline["coarse_tau1_ms"])
        reference_tau1 = float(baseline["local_tau1_ms"])
        reference_tau3 = float(baseline["tau3_ms"])
        tau1_grid, tau1_lower, tau1_upper = _local_tau1_neighborhood(
            coarse_tau1, reference_tau1, int(tau1_grid_points)
        )
        times, _, current = waveforms[voltage]
        slices: list[dict[str, Any]] = []
        for tau1_index, tau1 in enumerate(tau1_grid):
            fit = profile_three_exponential_correction(
                times,
                current,
                float(tau1),
                tau2_ms=450.0,
                tau3_min_ms=tau3_min_ms,
                tau3_max_ms=tau3_max_ms,
                grid_points=int(tau3_grid_points),
            )
            profile = fit["profile"]
            best_index = min(range(len(profile)), key=lambda index: profile[index]["rss_full"])
            best = profile[best_index]
            shape = summarize_tau3_profile_shape(voltage, float(tau1), profile)
            slices.append({
                "tau1_grid_index": tau1_index,
                "tau1_ms": float(tau1),
                "best_index": best_index,
                "best": best,
                "shape": shape,
            })

        global_slice = min(
            slices,
            key=lambda item: float(item["best"]["rss_full"]),
        )
        global_rss = float(global_slice["best"]["rss_full"])
        if not math.isfinite(global_rss) or global_rss <= 0.0:
            raise ValueError("K_IV tau1-tau3 surface has an invalid global full-waveform RSS")

        for item in slices:
            best = item["best"]
            shape = item["shape"]
            tau1 = float(item["tau1_ms"])
            tau1_index = int(item["tau1_grid_index"])
            rss = float(best["rss_full"])
            row: dict[str, Any] = {
                "voltage_mv": float(voltage),
                "tau1_grid_index": tau1_index,
                "tau1_grid_points": int(tau1_grid_points),
                "coarse_tau1_ms": coarse_tau1,
                "tau1_window_min_ms": tau1_lower,
                "tau1_window_max_ms": tau1_upper,
                "reference_tau1_ms": reference_tau1,
                "reference_tau3_ms": reference_tau3,
                "tau1_ms": tau1,
                "tau1_offset_from_reference_pct": 100.0 * (tau1 / reference_tau1 - 1.0),
                "tau1_at_window_boundary": bool(
                    tau1_index in (0, int(tau1_grid_points) - 1)
                ),
                "tau3_grid_points": int(tau3_grid_points),
                "tau3_min_ms": float(tau3_min_ms),
                "tau3_max_ms": float(tau3_max_ms),
                "selected_tau3_ms": float(best["tau3_ms"]),
                "tau3_minimum_at_grid_boundary": bool(shape["minimum_at_grid_boundary"]),
                "rss_full": rss,
                "relative_rss_to_surface_min_pct": 100.0 * (rss / global_rss - 1.0),
                "rmse_full_ma_cm2": float(best["rmse_full_ma_cm2"]),
                "rmse_first_10ms_ma_cm2": float(best["rmse_first_10ms_ma_cm2"]),
                "rmse_after_10ms_ma_cm2": float(best["rmse_after_10ms_ma_cm2"]),
                "a1_ma_cm2": float(best["a1_ma_cm2"]),
                "a2_ma_cm2": float(best["a2_ma_cm2"]),
                "a3_ma_cm2": float(best["a3_ma_cm2"]),
                "steady_offset_ma_cm2": float(best["steady_offset_ma_cm2"]),
                "profile_objective_normalized_curvature_per_ms2": float(
                    shape["profile_objective_normalized_curvature_per_ms2"]
                ),
                "left_neighbor_delta_rss_pct": float(shape["left_neighbor_delta_rss_pct"]),
                "right_neighbor_delta_rss_pct": float(shape["right_neighbor_delta_rss_pct"]),
                "is_global_surface_minimum": bool(
                    tau1_index == int(global_slice["tau1_grid_index"])
                ),
            }
            for threshold_pct in (1, 5, 10):
                for suffix in (
                    "objective_lower_ms",
                    "objective_upper_ms",
                    "objective_span_ms",
                    "objective_point_count",
                    "touches_grid_edge",
                ):
                    field = f"near_minimum_{threshold_pct}pct_{suffix}"
                    row[field] = shape[field]
            output.append(row)

    validate_tau1_tau3_surface_rows(
        output,
        tau1_grid_points=int(tau1_grid_points),
        tau3_grid_points=int(tau3_grid_points),
        tau3_min_ms=tau3_min_ms,
        tau3_max_ms=tau3_max_ms,
    )
    return output


def validate_tau1_tau3_surface_rows(
    rows: list[dict[str, Any]],
    *,
    tau1_grid_points: int = 9,
    tau3_grid_points: int = 2801,
    tau3_min_ms: float = 0.1,
    tau3_max_ms: float = 5.0,
) -> None:
    """Validate the ordered conditional tau1-tau3 objective-surface summary."""
    expected_count = (
        len(K_IV_TAU1_TAU3_SURFACE_VOLTAGES_MV) * int(tau1_grid_points)
    )
    expected_voltages = tuple(
        voltage
        for voltage in K_IV_TAU1_TAU3_SURFACE_VOLTAGES_MV
        for _ in range(int(tau1_grid_points))
    )
    if len(rows) != expected_count or tuple(
        row.get("voltage_mv") for row in rows
    ) != expected_voltages:
        raise ValueError("K_IV tau1-tau3 surface must preserve all three ordered voltages and tau1 slices")
    if (
        isinstance(tau1_grid_points, bool)
        or int(tau1_grid_points) != tau1_grid_points
        or tau1_grid_points < 3
        or tau1_grid_points % 2 == 0
        or isinstance(tau3_grid_points, bool)
        or int(tau3_grid_points) != tau3_grid_points
        or tau3_grid_points < 3
    ):
        raise ValueError("K_IV tau1-tau3 surface grid dimensions are invalid")
    expected_numeric = set(K_IV_TAU1_TAU3_SURFACE_FIELDNAMES) - (
        K_IV_TAU1_TAU3_SURFACE_INT_FIELDS | K_IV_TAU1_TAU3_SURFACE_BOOL_FIELDS
    )
    allowed_boundary_nan = {
        "profile_objective_normalized_curvature_per_ms2",
        "left_neighbor_delta_rss_pct",
        "right_neighbor_delta_rss_pct",
    }
    if (
        not math.isfinite(tau3_min_ms)
        or not math.isfinite(tau3_max_ms)
        or tau3_min_ms <= 0.0
        or tau3_max_ms <= tau3_min_ms
    ):
        raise ValueError("K_IV tau1-tau3 surface tau3 bounds are invalid")

    cursor = 0
    for voltage in K_IV_TAU1_TAU3_SURFACE_VOLTAGES_MV:
        group = rows[cursor : cursor + int(tau1_grid_points)]
        cursor += int(tau1_grid_points)
        reference = group[int(tau1_grid_points) // 2]
        coarse_tau1 = float(reference.get("coarse_tau1_ms", math.nan))
        reference_tau1 = float(reference.get("reference_tau1_ms", math.nan))
        reference_tau3 = float(reference.get("reference_tau3_ms", math.nan))
        lower = max(0.05, coarse_tau1 * 0.94)
        upper = min(1200.0, coarse_tau1 * 1.06)
        if not (
            math.isfinite(coarse_tau1)
            and math.isfinite(reference_tau1)
            and math.isfinite(reference_tau3)
            and lower < reference_tau1 < upper
            and lower < upper
        ):
            raise ValueError("K_IV tau1-tau3 surface has invalid reference tau/window")
        tau1_grid, expected_lower, expected_upper = _local_tau1_neighborhood(
            coarse_tau1, reference_tau1, int(tau1_grid_points)
        )
        if not math.isclose(expected_lower, lower, rel_tol=0.0, abs_tol=1.0e-12) or not math.isclose(
            expected_upper, upper, rel_tol=0.0, abs_tol=1.0e-12
        ):
            raise ValueError("K_IV tau1-tau3 surface changed the 6% tau1 window")
        global_min_row: dict[str, Any] | None = None
        for tau1_index, row in enumerate(group):
            if row.get("voltage_mv") != voltage or row.get("tau1_grid_index") != tau1_index:
                raise ValueError("K_IV tau1-tau3 surface tau1 slice order/index changed")
            for integer_field in K_IV_TAU1_TAU3_SURFACE_INT_FIELDS:
                value = row.get(integer_field)
                if not isinstance(value, int) or isinstance(value, bool):
                    raise ValueError(f"K_IV tau1-tau3 surface integer field is invalid: {integer_field}")
            for boolean_field in K_IV_TAU1_TAU3_SURFACE_BOOL_FIELDS:
                if not isinstance(row.get(boolean_field), bool):
                    raise ValueError(f"K_IV tau1-tau3 surface Boolean field is invalid: {boolean_field}")
            for numeric_field in expected_numeric:
                value = row.get(numeric_field)
                if not isinstance(value, (int, float)):
                    raise ValueError(f"K_IV tau1-tau3 surface numeric field is invalid: {numeric_field}")
                if not math.isfinite(float(value)):
                    if not (
                        row["tau3_minimum_at_grid_boundary"]
                        and numeric_field in allowed_boundary_nan
                        and math.isnan(float(value))
                    ):
                        raise ValueError(f"K_IV tau1-tau3 surface has non-finite {numeric_field}")
            if (
                row["tau1_grid_points"] != int(tau1_grid_points)
                or row["tau3_grid_points"] != int(tau3_grid_points)
            ):
                raise ValueError("K_IV tau1-tau3 surface grid-point metadata is inconsistent")
            for name, expected_value in (
                ("coarse_tau1_ms", coarse_tau1),
                ("tau1_window_min_ms", lower),
                ("tau1_window_max_ms", upper),
                ("reference_tau1_ms", reference_tau1),
                ("reference_tau3_ms", reference_tau3),
                ("tau1_ms", float(tau1_grid[tau1_index])),
                ("tau3_min_ms", tau3_min_ms),
                ("tau3_max_ms", tau3_max_ms),
            ):
                if not math.isclose(float(row[name]), expected_value, rel_tol=0.0, abs_tol=1.0e-12):
                    raise ValueError(f"K_IV tau1-tau3 surface {name} differs from its declared grid")
            expected_offset = 100.0 * (float(row["tau1_ms"]) / reference_tau1 - 1.0)
            if not math.isclose(
                row["tau1_offset_from_reference_pct"], expected_offset,
                rel_tol=1.0e-10, abs_tol=1.0e-12
            ):
                raise ValueError("K_IV tau1-tau3 surface tau1 offset is inconsistent")
            if row["tau1_at_window_boundary"] is not (
                tau1_index in (0, int(tau1_grid_points) - 1)
            ):
                raise ValueError("K_IV tau1-tau3 surface tau1 boundary flag is inconsistent")
            if not (tau3_min_ms <= row["selected_tau3_ms"] <= tau3_max_ms):
                raise ValueError("K_IV tau1-tau3 surface selected tau3 is outside its grid")
            if not row["tau3_minimum_at_grid_boundary"] and not (
                tau3_min_ms < row["selected_tau3_ms"] < tau3_max_ms
            ):
                raise ValueError("K_IV tau1-tau3 surface interior flag is inconsistent")
            if row["rss_full"] <= 0.0 or row["relative_rss_to_surface_min_pct"] < -1.0e-8:
                raise ValueError("K_IV tau1-tau3 surface full-waveform RSS is invalid")
            if any(row[name] < 0.0 for name in (
                "rmse_full_ma_cm2",
                "rmse_first_10ms_ma_cm2",
                "rmse_after_10ms_ma_cm2",
                "a1_ma_cm2",
                "a2_ma_cm2",
                "steady_offset_ma_cm2",
            )):
                raise ValueError("K_IV tau1-tau3 surface contains a negative constrained term")
            if not row["tau3_minimum_at_grid_boundary"]:
                if (
                    row["profile_objective_normalized_curvature_per_ms2"] < -1.0e-8
                    or row["left_neighbor_delta_rss_pct"] < -1.0e-8
                    or row["right_neighbor_delta_rss_pct"] < -1.0e-8
                ):
                    raise ValueError("K_IV tau1-tau3 surface selected point is not a local minimum")
            previous_lower = math.inf
            previous_upper = -math.inf
            previous_count = 0
            for threshold_pct in (1, 5, 10):
                lower_basin = row[f"near_minimum_{threshold_pct}pct_objective_lower_ms"]
                upper_basin = row[f"near_minimum_{threshold_pct}pct_objective_upper_ms"]
                span = row[f"near_minimum_{threshold_pct}pct_objective_span_ms"]
                count = row[f"near_minimum_{threshold_pct}pct_objective_point_count"]
                if not (
                    lower_basin <= row["selected_tau3_ms"] <= upper_basin
                    and upper_basin >= lower_basin
                    and math.isclose(span, upper_basin - lower_basin, rel_tol=0.0, abs_tol=1.0e-12)
                    and 1 <= count <= int(tau3_grid_points)
                    and count >= previous_count
                    and lower_basin <= previous_lower + 1.0e-12
                    and upper_basin >= previous_upper - 1.0e-12
                    and isinstance(row[f"near_minimum_{threshold_pct}pct_touches_grid_edge"], bool)
                ):
                    raise ValueError("K_IV tau1-tau3 surface conditional basin is inconsistent")
                previous_lower, previous_upper, previous_count = lower_basin, upper_basin, count
            if row["is_global_surface_minimum"]:
                if global_min_row is not None:
                    raise ValueError("K_IV tau1-tau3 surface has more than one global minimum")
                global_min_row = row
        if global_min_row is None:
            raise ValueError("K_IV tau1-tau3 surface lacks a global minimum")
        minimum_rss = min(float(row["rss_full"]) for row in group)
        if not math.isclose(float(global_min_row["rss_full"]), minimum_rss, rel_tol=1.0e-12, abs_tol=1.0e-24):
            raise ValueError("K_IV tau1-tau3 surface global-minimum flag does not mark the minimum")
        for row in group:
            expected_relative = 100.0 * (float(row["rss_full"]) / minimum_rss - 1.0)
            if not math.isclose(
                float(row["relative_rss_to_surface_min_pct"]),
                expected_relative,
                rel_tol=2.0e-8,
                abs_tol=1.0e-10,
            ):
                raise ValueError("K_IV tau1-tau3 surface relative RSS is inconsistent")
        if not math.isclose(
            float(reference["selected_tau3_ms"]),
            reference_tau3,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ):
            raise ValueError("K_IV center tau1 slice does not reproduce the reference tau3 optimum")
        if not math.isclose(float(global_min_row["relative_rss_to_surface_min_pct"]), 0.0, abs_tol=1.0e-10):
            raise ValueError("K_IV global surface minimum must have zero relative RSS")
    return None


def tau1_tau3_surface_csv_text(rows: list[dict[str, Any]]) -> str:
    """Serialize the reduced three-voltage tau1-tau3 conditional profile surface."""
    import io

    output = io.StringIO()
    output.write(
        "# Conditional tau1-tau3 sensitivity surface for predeclared K_IV commands -30, -60, and +55 mV.
"
    )
    output.write(
        "# Waveforms are deterministic NEURON 9.0.2/VClamp outputs from the unchanged DataverseNL v3.0 pure-human K source replay; not raw human experimental current.
"
    )
    output.write(
        "# At each voltage, nine tau1 values span only the existing local 6% refinement interval from the independently profiled coarse tau1; the center node is the existing selected local tau1.
"
    )
    output.write(
        "# At each tau1 node, tau3 is profiled over 0.1..5.0 ms on 2,801 equally spaced points and all four coefficients are refit against the full waveform; tau2 remains fixed at 450 ms.
"
    )
    output.write(
        "# Each row stores the conditional tau3 minimum and its 1/5/10% relative-full-RSS basin; relative_rss_to_surface_min_pct compares that slice minimum with the best minimum across tau1 values at the same voltage.
"
    )
    output.write(
        "# Full/first-10-ms/after-10-ms RMSE values are diagnostics of the same full-waveform objective. This numerical sensitivity surface is not a confidence region or biological uncertainty estimate.
"
    )
    writer = csv.DictWriter(
        output,
        fieldnames=K_IV_TAU1_TAU3_SURFACE_FIELDNAMES,
        extrasaction="raise",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def summary_csv_text(rows: list[dict[str, Any]]) -> str:
    """Serialize the compact multi-voltage fit summary."""
    import io

    output = io.StringIO()
    output.write(
        "# Non-source short-time residual correction tested across all 27 finite-positive K_IV source-fit commands.\n"
    )
    output.write(
        "# Input consists of the exact source-model NEURON/VClamp post-peak samples; "
        "this is not raw human experimental current.\n"
    )
    output.write(
        "# Source K_IV selection: current threshold >1e-8 mA/cm2; 32 commands attempted "
        "(-100..+55 mV), 27 finite-positive fast-fit results exported (-75..+55 mV).\n"
    )
    output.write(
        "# Five attempted commands (-100,-95,-90,-85,-80 mV) returned non-finite fast fits; "
        "-110 and -105 mV did not pass the source threshold. Neither group was silently dropped.\n"
    )
    output.write(
        "# Long tau1 is profiled independently at each eligible voltage (0.05..1200 ms coarse grid, "
        "then 6% local refinement); source tau2 remains fixed at 450 ms.\n"
    )
    if not rows:
        raise ValueError("K_IV summary requires all 27 eligible voltage rows")
    tau3_min_ms = float(rows[0]["tau3_profile_min_ms"])
    tau3_max_ms = float(rows[0]["tau3_profile_max_ms"])
    tau3_points = int(rows[0]["short_component_profile_points"])
    output.write(
        f"# Short tau3 is independently profiled at each eligible voltage "
        f"({tau3_min_ms:g}..{tau3_max_ms:g} ms; {tau3_points} equally spaced points); "
        "signed a3 is a descriptive model-residual correction, not a channel kinetic parameter.\n"
    )
    writer = csv.DictWriter(
        output,
        fieldnames=K_IV_MULTIVOLTAGE_FIELDNAMES,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def validate_summary_rows(
    rows: list[dict[str, Any]],
    *,
    tau3_min_ms: float = 0.6,
    tau3_max_ms: float = 2.0,
) -> None:
    """Check structural and numerical invariants without requiring improvement."""
    if (
        not math.isfinite(tau3_min_ms)
        or not math.isfinite(tau3_max_ms)
        or tau3_min_ms <= 0.0
        or tau3_max_ms <= tau3_min_ms
    ):
        raise ValueError("K_IV tau3 validation bounds must be finite, positive, and increasing")
    if tuple(row.get("voltage_mv") for row in rows) != K_IV_MULTIVOLTAGE_TARGETS_MV:
        raise ValueError("K_IV multivoltage summary must preserve all 27 ordered eligible commands")
    for row in rows:
        for name in K_IV_MULTIVOLTAGE_FIELDNAMES:
            value = row.get(name)
            if name in {
                "coarse_profile_at_boundary",
                "local_profile_at_boundary",
                "signed_extra_is_negative",
                "nonnegative_control_collapsed",
                "tau3_profile_at_boundary",
                "sample_count",
                "coarse_profile_points",
                "local_profile_points",
                "short_component_profile_points",
                "voltage_mv",
            }:
                continue
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise ValueError(f"K_IV summary has non-finite numeric field: {name}")
        if row["sample_count"] < 100 or row["coarse_profile_points"] < 2:
            raise ValueError("K_IV multivoltage profile lacks adequate samples")
        if row["local_profile_points"] < 2 or row["short_component_profile_points"] < 2:
            raise ValueError("K_IV local/short profile grid is underspecified")
        if not math.isclose(
            row["tau3_profile_min_ms"], tau3_min_ms, rel_tol=0.0, abs_tol=1.0e-12
        ) or not math.isclose(
            row["tau3_profile_max_ms"], tau3_max_ms, rel_tol=0.0, abs_tol=1.0e-12
        ):
            raise ValueError("K_IV summary tau3 bounds differ from the declared validation grid")
        if not (tau3_min_ms <= row["tau3_ms"] <= tau3_max_ms):
            raise ValueError("K_IV short time constant fell outside its declared grid")
        expected_boundary = (
            math.isclose(row["tau3_ms"], tau3_min_ms, rel_tol=0.0, abs_tol=1.0e-12)
            or math.isclose(row["tau3_ms"], tau3_max_ms, rel_tol=0.0, abs_tol=1.0e-12)
        )
        if row["tau3_profile_at_boundary"] is not expected_boundary:
            raise ValueError("K_IV tau3 boundary flag does not match the selected grid point")
        if row["extra_amplitude_pct_peak"] < 0.0:
            raise ValueError("K_IV extra-amplitude magnitude must not be negative")
        if row["positive_control_full_rmse_ma_cm2"] < 0.0:
            raise ValueError("K_IV positive-control RMSE must not be negative")
