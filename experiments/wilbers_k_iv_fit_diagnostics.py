#!/usr/bin/env python3
"""Counterfactual multi-start diagnostics for the deposited Wilbers K_IV fit.

The original source helper remains authoritative for the source replay. This
module repeats its fixed-450-ms two-component fit on the exact same NEURON
post-peak current samples, changing only SciPy initial guesses. It does not
modify the source mechanism, source helper, or fit acceptance threshold.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

K_IV_FIXED_SLOW_TAU_MS = 450.0
K_IV_SOURCE_R2_THRESHOLD = 0.95

K_IV_FIT_DIAGNOSTIC_FIELDNAMES = (
    "voltage_mv",
    "initialization",
    "source_helper_tau_fast_ms",
    "source_delta_current_ma_cm2",
    "initial_fast_amplitude_ma_cm2",
    "initial_tau1_value",
    "initial_slow_amplitude_ma_cm2",
    "initial_offset_ma_cm2",
    "fit_converged",
    "fit_tau_fast_ms",
    "fit_fast_amplitude_ma_cm2",
    "fit_slow_amplitude_ma_cm2",
    "fit_offset_ma_cm2",
    "fit_r_squared",
    "fit_rmse_ma_cm2",
    "fit_passes_source_r2_gate",
    "fit_error_type",
)

K_IV_PROFILE_FIELDNAMES = (
    "voltage_mv",
    "tau1_ms",
    "fit_fast_amplitude_ma_cm2",
    "fit_slow_amplitude_ma_cm2",
    "fit_offset_ma_cm2",
    "fit_r_squared",
    "fit_rmse_ma_cm2",
    "residual_sum_squares",
    "solver_success",
    "solver_optimality,
)


# Alternative starts are deliberately finite, dimensionally meaningful values
# within the deposited helper's original tau1 bounds (0, 300) ms. The source
# initialization is included verbatim as a control, not silently corrected.
ALTERNATIVE_STARTS = (
    ("tau30_equal_amplitudes", 30.0, 0.50),
    ("tau100_equal_amplitudes", 100.0, 0.50),
    ("tau200_equal_amplitudes", 200.0, 0.50),
    ("tau100_slow25pct", 100.0, 0.25),
    ("tau100_slow75pct", 100.0, 0.75),
)


def build_k_iv_fit_initializations(
    currents_ma_cm2: Any,
) -> list[tuple[str, tuple[float, float, float, float]]]:
    """Return the exact source p0 and five controlled alternatives.

    The source helper defines f(t, a1, tau1, a2, ss), then uses
    p0=((y0-yend)/2, (y0-yend)/2, est1, y0/10), with est1=30.
    The second member therefore initializes tau1 from a current-density
    difference, and est1 initializes the slow-component amplitude. Both
    assignments are preserved in the source_literal control.
    """
    y = np.asarray(currents_ma_cm2, dtype=float)
    if y.ndim != 1 or len(y) < 5 or not np.isfinite(y).all():
        raise ValueError("K_IV fit diagnostic requires at least five finite current samples")

    delta = float(y[0] - y[-1])
    y0 = float(y[0])
    source_p0 = (0.5 * delta, 0.5 * delta, 30.0, 0.1 * y0)

    amplitude_scale = max(
        abs(delta),
        float(np.ptp(y)),
        float(np.max(np.abs(y))) * 1.0e-6,
        np.finfo(float).tiny,
    )
    offset_guess = max(0.1 * y0, 0.0)
    initializations: list[tuple[str, tuple[float, float, float, float]]] = [
        ("source_literal", source_p0)
    ]
    for name, tau1_ms, slow_fraction in ALTERNATIVE_STARTS:
        fast_fraction = 1.0 - slow_fraction
        p0 = (
            amplitude_scale * fast_fraction,
            tau1_ms,
            amplitude_scale * slow_fraction,
            offset_guess,
        )
        initializations.append((name, p0))
    return initializations


def diagnose_k_iv_postpeak_fit(
    voltage_mv: float,
    times_ms: Any,
    currents_ma_cm2: Any,
    source_helper_tau_fast_ms: float,
) -> list[dict[str, Any]]:
    """Fit the same source post-peak samples from the source and alternative p0s."""
    from scipy.optimize import curve_fit

    times = np.asarray(times_ms, dtype=float)
    currents = np.asarray(currents_ma_cm2, dtype=float)
    if (
        times.ndim != 1
        or currents.ndim != 1
        or times.shape != currents.shape
        or len(times) < 5
        or not np.isfinite(times).all()
        or not np.isfinite(currents).all()
        or np.any(np.diff(times) <= 0.0)
    ):
        raise ValueError("K_IV post-peak diagnostic requires matched, increasing finite samples")

    x = times - times[0]
    delta = float(currents[0] - currents[-1])
    source_tau = (
        float(source_helper_tau_fast_ms)
        if math.isfinite(float(source_helper_tau_fast_ms))
        else math.nan
    )

    def fixed_slow_double_exponential(
        t: np.ndarray, a1: float, tau1: float, a2: float, steady: float
    ) -> np.ndarray:
        return (
            a1 * np.exp(-t / tau1)
            + a2 * np.exp(-t / K_IV_FIXED_SLOW_TAU_MS)
            + steady
        )

    rows: list[dict[str, Any]] = []
    for name, p0 in build_k_iv_fit_initializations(currents):
        row: dict[str, Any] = {
            "voltage_mv": float(voltage_mv),
            "initialization": name,
            "source_helper_tau_fast_ms": source_tau,
            "source_delta_current_ma_cm2": delta,
            "initial_fast_amplitude_ma_cm2": p0[0],
            "initial_tau1_value": p0[1],
            "initial_slow_amplitude_ma_cm2": p0[2],
            "initial_offset_ma_cm2": p0[3],
            "fit_converged": False,
            "fit_tau_fast_ms": math.nan,
            "fit_fast_amplitude_ma_cm2": math.nan,
            "fit_slow_amplitude_ma_cm2": math.nan,
            "fit_offset_ma_cm2": math.nan,
            "fit_r_squared": math.nan,
            "fit_rmse_ma_cm2": math.nan,
            "fit_passes_source_r2_gate": False,
            "fit_error_type": "",
        }
        try:
            parameters, _ = curve_fit(
                fixed_slow_double_exponential,
                x,
                currents,
                p0=p0,
                bounds=(
                    (0.0, 0.0, 0.0, 0.0),
                    (np.inf, 300.0, np.inf, np.inf),
                ),
            )
            fitted = fixed_slow_double_exponential(x, *parameters)
            residual = currents - fitted
            sum_squared_residuals = float(np.sum(residual**2))
            sum_squared_total = float(np.sum((currents - np.mean(currents)) ** 2))
            r_squared = (
                1.0 - sum_squared_residuals / sum_squared_total
                if sum_squared_total > 0.0
                else math.nan
            )
            rmse = math.sqrt(float(np.mean(residual**2)))
            if not (
                np.isfinite(parameters).all()
                and math.isfinite(r_squared)
                and math.isfinite(rmse)
            ):
                raise FloatingPointError("fit returned non-finite parameters or residuals")
            row.update(
                {
                    "fit_converged": True,
                    "fit_tau_fast_ms": float(parameters[1]),
                    "fit_fast_amplitude_ma_cm2": float(parameters[0]),
                    "fit_slow_amplitude_ma_cm2": float(parameters[2]),
                    "fit_offset_ma_cm2": float(parameters[3]),
                    "fit_r_squared": r_squared,
                    "fit_rmse_ma_cm2": rmse,
                    "fit_passes_source_r2_gate": r_squared > K_IV_SOURCE_R2_THRESHOLD,
                }
            )
        except Exception as exc:  # Keep failed starts visible rather than dropping them.
            row["fit_error_type"] = type(exc).__name__
        rows.append(row)
    return rows


def profile_k_iv_postpeak_tau(
    voltage_mv: float,
    times_ms: Any,
    currents_ma_cm2: Any,
) -> list[dict[str, Any]]:
    """Profile the nonnegative linear amplitudes over a fixed tau1 grid.

    For each fixed fast tau1, the remaining (a1, a2, ss) parameters are
    estimated by bounded linear least squares. This is a deterministic profile
    objective, not a change to the deposited source fit.
    """
    from scipy.optimize import lsq_linear

    times = np.asarray(times_ms, dtype=float)
    currents = np.asarray(currents_ma_cm2, dtype=float)
    if (
        times.ndim != 1
        or currents.ndim != 1
        or times.shape != currents.shape
        or len(times) < 5
        or not np.isfinite(times).all()
        or not np.isfinite(currents).all()
        or np.any(np.diff(times) <= 0.0)
    ):
        raise ValueError("K_IV tau profile requires matched, increasing finite samples")

    x = times - times[0]
    total = float(np.sum((currents - np.mean(currents)) ** 2))
    tau_grid = np.geomspace(0.05, 300.0, 601)
    rows: list[dict[str, Any]] = []
    for tau1 in tau_grid:
        design = np.column_stack(
            (
                np.exp(-x / tau1),
                np.exp(-x / K_IV_FIXED_SLOW_TAU_MS),
                np.ones_like(x),
            )
        )
        solution = lsq_linear(
            design,
            currents,
            bounds=(0.0, np.inf),
            method="trf",
            tol=1.0e-12,
            lsmr_tol="auto",
            max_iter=300,
        )
        parameters = np.asarray(solution.x, dtype=float)
        fitted = design @ parameters
        residual = currents - fitted
        rss = float(np.sum(residual**2))
        rmse = math.sqrt(float(np.mean(residual**2)))
        r_squared = 1.0 - rss / total if total > 0.0 else math.nan
        rows.append(
            {
                "voltage_mv": float(voltage_mv),
                "tau1_ms": float(tau1),
                "fit_fast_amplitude_ma_cm2": float(parameters[0]),
                "fit_slow_amplitude_ma_cm2": float(parameters[1]),
                "fit_offset_ma_cm2": float(parameters[2]),
                "fit_r_squared": r_squared,
                "fit_rmse_ma_cm2": rmse,
                "residual_sum_squares": rss,
                "solver_success": bool(solution.success),
                "solver_optimality": float(solution.optimality),
            }
        )
    return rows
