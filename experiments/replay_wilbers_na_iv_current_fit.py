#!/usr/bin/env python3
"""Reconstruct the Wilbers Na_IV model-current fit from its deposited protocol.

This is an independent, normalized-current reconstruction using the deposited
human Na gate equations and the released channel_tools.py fitting procedure.
It is not a NEURON execution, raw-recording replay, or biological validation.
"""
from __future__ import annotations
import csv
import math
import sys
from typing import Any

import numpy as np
from scipy.optimize import curve_fit

import diagnose_wilbers_neuron_solver as diagnostic

SOURCE_DOI = "10.34894/L5J0SD"
CHANNEL_TOOLS_FILE_ID = 326242
CHANNEL_TOOLS_SHA1 = "615595a270c6170987757cd35743f5d5b5b2af0e"
PURE_NA_MOD_FILE_ID = 318629
PURE_NA_MOD_SHA1 = "b199d70c3d0e7a2e991fd8d26c54b1318e3c0970"
TEMPERATURE_CELSIUS = 25.0
REFERENCE_TEMPERATURE_CELSIUS = 25.0
Q10 = 2.3
SAMPLE_INTERVAL_MS = 0.01
HOLD_DURATION_MS = 2.0
TEST_DURATION_MS = 10.0
HOLD_VOLTAGE_MV = -120.0
TEST_VOLTAGES_MV = tuple(float(v) for v in range(-80, 11, 5))
SAMPLE_MASK_START_MS = 2.02
SAMPLE_MASK_END_MS = 12.0
SODIUM_REVERSAL_MV = 60.0
COMPOSITE_DELAY_MS = 0.05
FIT_R2_THRESHOLD = 0.95

_FIELDNAMES = (
    "voltage_mv", "samples_fitted", "gate_tau_m_ms", "gate_tau_h_ms",
    "preliminary_tau_m_ms", "preliminary_tau_h_ms", "joint_tau_m_ms",
    "joint_tau_h_ms", "r2_conditional_tau_m_ms", "r2_conditional_tau_h_ms",
    "joint_r_squared", "passed_joint_fit_r2",
    "joint_tau_h_at_upper_bound",
)


def _sodium_rates_25c(voltage_mv: float) -> tuple[float, float, float, float]:
    """Return m_inf, tau_m, h_inf, tau_h using the deposited equations at 25°C.

    The shared source-equation bundle evaluates Na kinetics at 34°C.
    Multiplying its Na taus by the 34°C Q10 factor restores the 25°C
    reference values; steady-state gates do not change with temperature.
    """
    m_inf, tau_m_34c, h_inf, tau_h_34c, *_ = diagnostic._wilbers_gate_rate_bundle(
        float(voltage_mv)
    )
    q10_at_34c = Q10 ** ((34.0 - REFERENCE_TEMPERATURE_CELSIUS) / 10.0)
    temperature_factor_25c = Q10 ** (
        (TEMPERATURE_CELSIUS - REFERENCE_TEMPERATURE_CELSIUS) / 10.0
    )
    tau_m_25c = tau_m_34c * q10_at_34c / temperature_factor_25c
    tau_h_25c = tau_h_34c * q10_at_34c / temperature_factor_25c
    return float(m_inf), float(tau_m_25c), float(h_inf), float(tau_h_25c)


def _advance_gate(gate: float, steady_state: float, tau_ms: float, dt_ms: float) -> float:
    return steady_state + (gate - steady_state) * math.exp(-dt_ms / tau_ms)


def simulate_normalized_sodium_current(test_voltage_mv: float) -> tuple[np.ndarray, np.ndarray]:
    """Return command times and inward Na current in arbitrary linear units.

    The current shape is gbar*T_adj*m^3*h*(V-E_Na), with gbar normalized to
    one. The unknown source cell conductance/area affects amplitude only,
    not fitted time constants. The source's absolute-current threshold is
    intentionally not applied in this normalized reconstruction.
    """
    if not math.isfinite(test_voltage_mv) or test_voltage_mv not in TEST_VOLTAGES_MV:
        raise ValueError("test voltage must be one of the deposited -80..+10 mV commands")
    total_duration_ms = HOLD_DURATION_MS + TEST_DURATION_MS
    sample_count = round(total_duration_ms / SAMPLE_INTERVAL_MS)
    times = np.arange(sample_count + 1, dtype=float) * SAMPLE_INTERVAL_MS
    command_voltage = np.where(times < HOLD_DURATION_MS, HOLD_VOLTAGE_MV, test_voltage_mv)

    m, _, h, _ = _sodium_rates_25c(HOLD_VOLTAGE_MV)
    hold_rates = _sodium_rates_25c(HOLD_VOLTAGE_MV)
    test_rates = _sodium_rates_25c(test_voltage_mv)
    m_trace = np.empty(sample_count + 1, dtype=float)
    h_trace = np.empty(sample_count + 1, dtype=float)
    m_trace[0] = m
    h_trace[0] = h
    for index in range(1, sample_count + 1):
        interval_start_ms = times[index - 1]
        m_inf, tau_m, h_inf, tau_h = (
            hold_rates if interval_start_ms < HOLD_DURATION_MS else test_rates
        )
        m = _advance_gate(m, m_inf, tau_m, SAMPLE_INTERVAL_MS)
        h = _advance_gate(h, h_inf, tau_h, SAMPLE_INTERVAL_MS)
        m_trace[index] = m
        h_trace[index] = h

    inward_current = m_trace**3 * h_trace * (SODIUM_REVERSAL_MV - command_voltage)
    return times, inward_current


def _single_exponential(
    t: np.ndarray, amplitude: float, tau_ms: float, steady: float
) -> np.ndarray:
    return amplitude * np.exp(-t / tau_ms) + steady


def _source_composite_sodium_current(
    t_ms: np.ndarray, tau_m_ms: float, tau_h_ms: float,
    amplitude: float, steady: float,
) -> np.ndarray:
    """Literal mathematical form of channel_tools.sodiumcurrent."""
    t = np.asarray(t_ms, dtype=float)
    shifted = t - COMPOSITE_DELAY_MS
    result = (1.0 - np.exp(-shifted / tau_m_ms)) * (
        amplitude * np.exp(-shifted / tau_h_ms) + steady
    )
    result = np.asarray(result, dtype=float)
    result[t < COMPOSITE_DELAY_MS] = 0.0
    return result


def _source_preliminary_activation_tau(t_ms: np.ndarray, y: np.ndarray) -> float:
    # Mirrors channel_tools.get_tau_act: offset time and subtract final y.
    x = t_ms - t_ms[0]
    values = y - y[-1]
    parameters, _ = curve_fit(
        _single_exponential, x, values,
        p0=(values[0], 0.1, values[0] * 0.1),
    )
    return float(parameters[1])


def _source_preliminary_inactivation_tau(t_ms: np.ndarray, y: np.ndarray) -> float:
    # Mirrors channel_tools.get_tau_inact: offset time, but do not offset y.
    x = t_ms - t_ms[0]
    parameters, _ = curve_fit(
        _single_exponential, x, y,
        p0=(y[0] - y[-1], 2.0, y[0] * 0.1),
    )
    return float(parameters[1])


def fit_source_composite_current(
    t_ms: np.ndarray, inward_current: np.ndarray
) -> dict[str, float]:
    """Apply the released fit_na_curr procedure to one sampled current trace."""
    x = np.asarray(t_ms, dtype=float)
    y = np.asarray(inward_current, dtype=float)
    if x.ndim != 1 or y.shape != x.shape or len(x) < 10:
        raise ValueError("current fit requires at least 10 aligned time/current samples")
    if not np.isfinite(x).all() or not np.isfinite(y).all() or np.any(np.diff(x) <= 0.0):
        raise ValueError("current fit requires finite samples and increasing times")
    if np.any(y < 0.0) or float(np.max(y)) <= 0.0:
        raise ValueError("current fit requires a positive inward-current magnitude")
    peak_index = int(np.argmax(y))
    if peak_index < 4 or len(y) - peak_index < 5:
        raise ValueError("current peak leaves too few samples for source preliminary fits")

    estimate_activation = _source_preliminary_activation_tau(x[:peak_index], y[:peak_index])
    estimate_inactivation = _source_preliminary_inactivation_tau(
        x[peak_index:-1], y[peak_index:-1]
    )

    # Mirrors channel_tools.fit_na_curr: x is reset to the first retained
    # sample, the 50-µs delay stays in the model, and these bounds are exact.
    x_fit = x - x[0]
    y_max = float(np.max(y))
    parameters, _ = curve_fit(
        _source_composite_sodium_current,
        x_fit,
        y,
        p0=(estimate_activation, estimate_inactivation, y_max, float(y[-1]) * 0.1),
        bounds=(
            (estimate_activation * 0.5, estimate_inactivation * 0.5, y_max, 0.0),
            (estimate_activation * 2.0, estimate_inactivation * 2.0, y_max * 1.5, y_max),
        ),
    )
    residual = y - _source_composite_sodium_current(x_fit, *parameters)
    ss_residual = float(np.sum(residual**2))
    ss_total = float(np.sum((y - np.mean(y)) ** 2))
    if ss_total <= 0.0:
        raise ValueError("source current-fit R-squared is undefined for a constant waveform")
    r_squared = 1.0 - ss_residual / ss_total
    return {
        "preliminary_tau_m_ms": estimate_activation,
        "preliminary_tau_h_ms": estimate_inactivation,
        "joint_tau_m_ms": float(parameters[0]),
        "joint_tau_h_ms": float(parameters[1]),
        "joint_r_squared": r_squared,
    }


def replay_na_iv_current_fits() -> list[dict[str, Any]]:
    """Run the deposited 19-step Na_IV command and source fitting sequence."""
    rows: list[dict[str, Any]] = []
    for voltage in TEST_VOLTAGES_MV:
        times, current = simulate_normalized_sodium_current(voltage)
        mask = (times > SAMPLE_MASK_START_MS) & (times < SAMPLE_MASK_END_MS)
        fit_times = times[mask]
        fit_current = current[mask]
        _, gate_tau_m, _, gate_tau_h = _sodium_rates_25c(voltage)
        try:
            fits = fit_source_composite_current(fit_times, fit_current)
            accepted = fits["joint_r_squared"] > FIT_R2_THRESHOLD
            rows.append(
                {
                    "voltage_mv": voltage,
                    "samples_fitted": int(np.count_nonzero(mask)),
                    "gate_tau_m_ms": gate_tau_m,
                    "gate_tau_h_ms": gate_tau_h,
                    **fits,
                    # The source returns tau_m=popt[0], but tau_h remains the
                    # preliminary decay estimate (the popt[1] write is commented out).
                    "r2_conditional_tau_m_ms": fits["joint_tau_m_ms"] if accepted else math.nan,
                    "r2_conditional_tau_h_ms": fits["preliminary_tau_h_ms"] if accepted else math.nan,
                    "passed_joint_fit_r2": accepted,
                    "joint_tau_h_at_upper_bound": (
                        abs(fits["joint_tau_h_ms"] - 2.0 * fits["preliminary_tau_h_ms"])
                        <= 1.0e-6 * max(1.0, abs(fits["joint_tau_h_ms"]))
                    ),
                }
            )
        except (RuntimeError, ValueError, FloatingPointError) as error:
            rows.append(
                {
                    "voltage_mv": voltage,
                    "samples_fitted": int(np.count_nonzero(mask)),
                    "gate_tau_m_ms": gate_tau_m,
                    "gate_tau_h_ms": gate_tau_h,
                    "preliminary_tau_m_ms": math.nan,
                    "preliminary_tau_h_ms": math.nan,
                    "joint_tau_m_ms": math.nan,
                    "joint_tau_h_ms": math.nan,
                    "r2_conditional_tau_m_ms": math.nan,
                    "r2_conditional_tau_h_ms": math.nan,
                    "joint_r_squared": math.nan,
                    "passed_joint_fit_r2": False,
                    "joint_tau_h_at_upper_bound": False,
                    "fit_error": str(error),
                }
            )
    return rows


def main() -> int:
    rows = replay_na_iv_current_fits()
    writer = csv.DictWriter(sys.stdout, fieldnames=_FIELDNAMES, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        serializable = {
            key: ("" if isinstance(value, float) and not math.isfinite(value) else value)
            for key, value in row.items()
        }
        writer.writerow(serializable)
    accepted = sum(bool(row["passed_joint_fit_r2"]) for row in rows)
    print(
        f"# {accepted}/{len(rows)} voltages passed the deposited joint-fit R² > {FIT_R2_THRESHOLD:.2f} rule; "
        "absolute source-current threshold not applied to normalized current.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
