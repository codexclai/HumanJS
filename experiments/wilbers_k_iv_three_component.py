#!/usr/bin/env python3
"""Non-source signed exponential residual correction for the Wilbers K_IV fit.

This descriptive counterfactual is fitted to the checked-in source-model
residual waveform. Its extra coefficient may be signed; it is not a new
channel state, biological inactivation component, or experimental refit.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import lsq_linear

K_IV_FIXED_SLOW_TAU_MS = 450.0
K_IV_PROFILE_MIN_TAU_MS = 0.6
K_IV_PROFILE_MAX_TAU_MS = 2.0
K_IV_PROFILE_POINTS = 801


def _validate_waveform(
    times_ms: Any, currents_ma_cm2: Any
) -> tuple[np.ndarray, np.ndarray]:
    times = np.asarray(times_ms, dtype=float)
    currents = np.asarray(currents_ma_cm2, dtype=float)
    if (
        times.ndim != 1
        or currents.ndim != 1
        or times.shape != currents.shape
        or len(times) < 10
        or not np.isfinite(times).all()
        or not np.isfinite(currents).all()
        or np.any(np.diff(times) <= 0.0)
    ):
        raise ValueError(
            "K_IV waveform requires at least ten matched, finite, increasing samples"
        )
    if not np.any(times < 10.0) or not np.any(times >= 10.0):
        raise ValueError(
            "K_IV waveform must contain samples both before and after 10 ms"
        )
    return times, currents


def read_residual_waveform(
    path: Path,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load the source-model residual record and retain both time bases."""
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(
            csv.DictReader(
                line for line in stream if not line.lstrip().startswith("#")
            )
        )
    if len(rows) != 4890:
        raise ValueError(
            f"Expected 4,890 source-model residual samples, found {len(rows)}"
        )
    required = {
        "time_since_peak_ms",
        "source_simulation_time_ms",
        "observed_current_ma_cm2",
    }
    if not rows or not required.issubset(rows[0]):
        raise ValueError("K_IV residual CSV schema is incomplete")
    relative_time = np.asarray(
        [float(row["time_since_peak_ms"]) for row in rows]
    )
    source_time = np.asarray(
        [float(row["source_simulation_time_ms"]) for row in rows]
    )
    current = np.asarray(
        [float(row["observed_current_ma_cm2"]) for row in rows]
    )
    relative_time, current = _validate_waveform(relative_time, current)
    if not np.isfinite(source_time).all() or np.any(np.diff(source_time) <= 0.0):
        raise ValueError("K_IV source simulation clock must be finite and increasing")
    if not np.allclose(
        np.diff(relative_time), 0.1, atol=1.0e-9, rtol=0.0
    ):
        raise ValueError(
            "K_IV residual waveform must preserve its 0.1-ms relative sampling"
        )
    if not np.allclose(
        source_time - source_time[0], relative_time, atol=1.0e-8, rtol=0.0
    ):
        raise ValueError("K_IV source and shifted clocks do not align")
    return relative_time, source_time, current


def read_profile_tau(path: Path) -> float:
    """Use the best sampled tau from the existing high-resolution local profile."""
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(
            csv.DictReader(
                line for line in stream if not line.lstrip().startswith("#")
            )
        )
    if (
        len(rows) != 801
        or not rows
        or not {"tau1_ms", "fit_rmse_ma_cm2"}.issubset(rows[0])
    ):
        raise ValueError("Expected the existing 801-point K_IV local profile")
    best = min(rows, key=lambda row: float(row["fit_rmse_ma_cm2"]))
    tau1 = float(best["tau1_ms"])
    if not math.isfinite(tau1) or tau1 <= 0.0:
        raise ValueError("Local K_IV profile returned an invalid tau1")
    return tau1


def _metrics(
    times: np.ndarray, current: np.ndarray, fitted: np.ndarray
) -> dict[str, float]:
    residual = current - fitted
    early = times < 10.0
    late = ~early
    rss = float(np.dot(residual, residual))
    total = float(np.sum((current - np.mean(current)) ** 2))
    if total <= 0.0 or not math.isfinite(total):
        raise ValueError("K_IV current waveform has no finite variance")
    return {
        "rmse_full_ma_cm2": math.sqrt(rss / len(current)),
        "rmse_first_10ms_ma_cm2": math.sqrt(
            float(np.mean(residual[early] ** 2))
        ),
        "rmse_after_10ms_ma_cm2": math.sqrt(
            float(np.mean(residual[late] ** 2))
        ),
        "r2_full": 1.0 - rss / total,
        "rss_full": rss,
    }


def fit_two_exponential_baseline(
    times_ms: Any,
    currents_ma_cm2: Any,
    tau1_ms: float,
    *,
    tau2_ms: float = K_IV_FIXED_SLOW_TAU_MS,
) -> dict[str, Any]:
    """Refit the fixed-tau two-exponential baseline by linear least squares."""
    times, current = _validate_waveform(times_ms, currents_ma_cm2)
    if (
        not math.isfinite(tau1_ms)
        or tau1_ms <= 0.0
        or not math.isfinite(tau2_ms)
        or tau2_ms <= 0.0
    ):
        raise ValueError("K_IV baseline time constants must be finite and positive")
    design = np.column_stack(
        (np.exp(-times / tau1_ms), np.exp(-times / tau2_ms), np.ones_like(times))
    )
    coefficients, _, _, _ = np.linalg.lstsq(design, current, rcond=None)
    if not np.isfinite(coefficients).all() or np.any(coefficients < 0.0):
        raise ValueError("K_IV baseline produced non-finite or negative coefficients")
    fitted = design @ coefficients
    return {
        "tau1_ms": float(tau1_ms),
        "tau2_ms": float(tau2_ms),
        "tau3_ms": math.nan,
        "a1_ma_cm2": float(coefficients[0]),
        "a2_ma_cm2": float(coefficients[1]),
        "a3_ma_cm2": 0.0,
        "steady_offset_ma_cm2": float(coefficients[2]),
        **_metrics(times, current, fitted),
    }


def _fit_three_exponential(
    times: np.ndarray,
    current: np.ndarray,
    tau1_ms: float,
    tau3_ms: float,
    *,
    allow_signed_extra: bool,
    tau2_ms: float,
) -> dict[str, Any]:
    design = np.column_stack(
        (
            np.exp(-times / tau1_ms),
            np.exp(-times / tau2_ms),
            np.exp(-times / tau3_ms),
            np.ones_like(times),
        )
    )
    lower = (0.0, 0.0, -np.inf if allow_signed_extra else 0.0, 0.0)
    result = lsq_linear(
        design,
        current,
        bounds=(lower, (np.inf, np.inf, np.inf, np.inf)),
        method="bvls",
        tol=1.0e-12,
        max_iter=100,
    )
    if not result.success or not np.isfinite(result.x).all():
        raise RuntimeError(
            f"K_IV three-exponential least-squares fit failed at tau3={tau3_ms:g} ms"
        )
    fitted = design @ result.x
    return {
        "tau1_ms": float(tau1_ms),
        "tau2_ms": float(tau2_ms),
        "tau3_ms": float(tau3_ms),
        "a1_ma_cm2": float(result.x[0]),
        "a2_ma_cm2": float(result.x[1]),
        "a3_ma_cm2": float(result.x[2]),
        "steady_offset_ma_cm2": float(result.x[3]),
        "solver_optimality": float(result.optimality),
        **_metrics(times, current, fitted),
    }


def profile_three_exponential_correction(
    times_ms: Any,
    currents_ma_cm2: Any,
    tau1_ms: float,
    *,
    tau2_ms: float = K_IV_FIXED_SLOW_TAU_MS,
    tau3_min_ms: float = K_IV_PROFILE_MIN_TAU_MS,
    tau3_max_ms: float = K_IV_PROFILE_MAX_TAU_MS,
    grid_points: int = K_IV_PROFILE_POINTS,
) -> dict[str, Any]:
    """Fit a signed third exponential over the full waveform, then a positive control."""
    times, current = _validate_waveform(times_ms, currents_ma_cm2)
    if (
        not math.isfinite(tau1_ms)
        or tau1_ms <= 0.0
        or not math.isfinite(tau2_ms)
        or tau2_ms <= 0.0
    ):
        raise ValueError("K_IV long-component time constants must be finite and positive")
    if (
        not math.isfinite(tau3_min_ms)
        or not math.isfinite(tau3_max_ms)
        or tau3_min_ms <= 0.0
        or tau3_max_ms <= tau3_min_ms
    ):
        raise ValueError(
            "K_IV tau3 profile bounds must be finite, positive, and increasing"
        )
    if (
        isinstance(grid_points, bool)
        or int(grid_points) != grid_points
        or grid_points < 2
    ):
        raise ValueError("K_IV tau3 profile requires at least two grid points")

    baseline = fit_two_exponential_baseline(
        times, current, tau1_ms, tau2_ms=tau2_ms
    )
    tau_grid = np.linspace(
        float(tau3_min_ms), float(tau3_max_ms), int(grid_points)
    )
    profile: list[dict[str, Any]] = []
    for tau3 in tau_grid:
        profile.append(
            _fit_three_exponential(
                times,
                current,
                tau1_ms,
                float(tau3),
                allow_signed_extra=True,
                tau2_ms=tau2_ms,
            )
        )
    best_signed = min(profile, key=lambda row: row["rss_full"])

    # At the signed-model optimum, require a3 >= 0. This isolates whether an
    # additive extra term helps at the same tau3 selected by the full objective.
    positive_control = _fit_three_exponential(
        times,
        current,
        tau1_ms,
        float(best_signed["tau3_ms"]),
        allow_signed_extra=False,
        tau2_ms=tau2_ms,
    )
    grid_meta = {
        "profile_grid_points": int(grid_points),
        "profile_tau3_min_ms": float(tau3_min_ms),
        "profile_tau3_max_ms": float(tau3_max_ms),
    }
    baseline.update(grid_meta)
    best_signed.update(grid_meta)
    positive_control.update(grid_meta)
    return {
        "baseline": baseline,
        "best_signed": best_signed,
        "positive_control": positive_control,
        "profile": profile,
    }
