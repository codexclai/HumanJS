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
)


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
        tau3_min_ms=0.6,
        tau3_max_ms=2.0,
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
) -> list[dict[str, Any]]:
    waveforms = read_postpeak_waveforms(path)
    return [
        analyze_k_iv_waveform(
            voltage,
            *waveforms[voltage],
            coarse_profile_points=coarse_profile_points,
            local_profile_points=local_profile_points,
            short_profile_points=short_profile_points,
        )
        for voltage in K_IV_MULTIVOLTAGE_TARGETS_MV
    ]


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
    output.write(
        "# Short tau3 is independently profiled at each eligible voltage (0.6..2.0 ms); signed a3 "
        "is a descriptive model-residual correction, not a channel kinetic parameter.\n"
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


def validate_summary_rows(rows: list[dict[str, Any]]) -> None:
    """Check structural and numerical invariants without requiring improvement."""
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
        if not (0.6 <= row["tau3_ms"] <= 2.0):
            raise ValueError("K_IV short time constant fell outside its declared grid")
        if row["extra_amplitude_pct_peak"] < 0.0:
            raise ValueError("K_IV extra-amplitude magnitude must not be negative")
        if row["positive_control_full_rmse_ma_cm2"] < 0.0:
            raise ValueError("K_IV positive-control RMSE must not be negative")
