#!/usr/bin/env python3
"""Diagnose numerical solver contributions to the Wilbers human L2/L3 AP1 replay.

The original source mechanisms and author's rheobase procedure are preserved.
NEURON's integration order, fixed step, and human Na lookup-table switch are
varied; optional NMODL/HumanJS gate traces expose internal state differences.
A shared-voltage counterfactual isolates the gate-update method from voltage
feedback. This is a numerical sensitivity experiment, not a new fit.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import tempfile
from pathlib import Path
from typing import Any

import reproduce_wilbers_current_clamp_neuron as reproduction


SOURCE_GATE_NAMES = (
    "m_na_human",
    "h_na_human",
    "m_k_human",
    "h1_k_human",
    "h2_k_human",
)
HUMANJS_GATE_NAMES = (
    "sodium_activation",
    "sodium_inactivation",
    "potassium_activation",
    "potassium_fast_inactivation",
    "potassium_slow_inactivation",
)
SOURCE_TO_HUMANJS_GATE = dict(zip(SOURCE_GATE_NAMES, HUMANJS_GATE_NAMES))


def floats(values: Any) -> list[float]:
    return [float(value) for value in values]


def summarize_trace(
    times_ms: Any,
    voltage_mv: Any,
    feature_extractor: Any,
    trace_path: Path | None = None,
) -> dict[str, Any]:
    import numpy as np

    times = np.asarray(times_ms, dtype=float)
    voltage = np.asarray(voltage_mv, dtype=float)
    if len(times) < 2 or len(times) != len(voltage):
        raise reproduction.ReproductionError("NEURON returned an invalid trace")
    features = feature_extractor(times, voltage)
    result: dict[str, Any] = {
        "samples": int(len(times)),
        "time_start_ms": float(times[0]),
        "time_end_ms": float(times[-1]),
        "sample_interval_ms": float(times[1] - times[0]),
        "peak_voltage_mV": float(np.max(voltage)),
        "peak_time_ms": float(times[int(np.argmax(voltage))]),
        "minimum_voltage_mV": float(np.min(voltage)),
        "features": {key: floats(value) for key, value in features.items()},
    }
    if trace_path is not None:
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        np.savetxt(
            trace_path,
            np.column_stack((times, voltage)),
            delimiter=",",
            header="time_ms,voltage_mv",
            comments="",
            fmt="%.12g",
        )
        result["trace_file"] = str(trace_path)
    return result


def compare_traces(
    reference_times: Any,
    reference_voltage: Any,
    compared_times: Any,
    compared_voltage: Any,
) -> dict[str, Any]:
    import numpy as np

    reference_time = np.asarray(reference_times, dtype=float)
    reference_values = np.asarray(reference_voltage, dtype=float)
    sample_time = np.asarray(compared_times, dtype=float)
    sample_values = np.asarray(compared_voltage, dtype=float)
    time_tolerance = max(1.0e-9, 1.0e-12 * abs(float(reference_time[-1])))
    mask = (sample_time >= reference_time[0] - time_tolerance) & (
        sample_time <= reference_time[-1] + time_tolerance
    )
    if not np.any(mask):
        raise reproduction.ReproductionError(
            "The compared trace has no samples within the reference trace interval"
        )
    aligned_time = np.clip(sample_time[mask], reference_time[0], reference_time[-1])
    residual = sample_values[mask] - np.interp(
        aligned_time, reference_time, reference_values
    )
    maximum_index = int(np.argmax(np.abs(residual)))
    return {
        "samples_compared": int(len(residual)),
        "rmse_mV": float(np.sqrt(np.mean(residual * residual))),
        "mean_absolute_error_mV": float(np.mean(np.abs(residual))),
        "maximum_absolute_error_mV": float(np.max(np.abs(residual))),
        "maximum_absolute_error_time_ms": float(sample_time[mask][maximum_index]),
        "mean_signed_residual_mV": float(np.mean(residual)),
    }


def load_trace(path: Path) -> tuple[Any, Any]:
    import numpy as np

    reference = np.loadtxt(path, delimiter=",", skiprows=1)
    if reference.ndim != 2 or reference.shape[1] < 2:
        raise reproduction.ReproductionError(
            "Trace must be a two-column CSV: time_ms,voltage_mv"
        )
    return reference[:, 0], reference[:, 1]


def compare_with_humanjs(
    humanjs_path: Path,
    source_times: Any,
    source_voltage: Any,
) -> dict[str, Any]:
    human_time, human_voltage = load_trace(humanjs_path)
    return compare_traces(source_times, source_voltage, human_time, human_voltage)


def compare_gate_traces(
    reference_times: Any,
    reference_gates: dict[str, Any],
    compared_times: Any,
    compared_gates: dict[str, Any],
) -> dict[str, Any]:
    import numpy as np

    reference_time = np.asarray(reference_times, dtype=float)
    sample_time = np.asarray(compared_times, dtype=float)
    time_tolerance = max(1.0e-9, 1.0e-12 * abs(float(reference_time[-1])))
    mask = (sample_time >= reference_time[0] - time_tolerance) & (
        sample_time <= reference_time[-1] + time_tolerance
    )
    if not np.any(mask):
        raise reproduction.ReproductionError(
            "The compared gate trace has no samples within the reference interval"
        )

    summaries: dict[str, Any] = {}
    for source_name, humanjs_name in SOURCE_TO_HUMANJS_GATE.items():
        reference_values = np.asarray(reference_gates[source_name], dtype=float)
        sample_values = np.asarray(compared_gates[humanjs_name], dtype=float)
        aligned_time = np.clip(sample_time[mask], reference_time[0], reference_time[-1])
        residual = sample_values[mask] - np.interp(
            aligned_time, reference_time, reference_values
        )
        maximum_index = int(np.argmax(np.abs(residual)))
        summaries[humanjs_name] = {
            "rmse_gate_fraction": float(np.sqrt(np.mean(residual * residual))),
            "mean_absolute_error_gate_fraction": float(np.mean(np.abs(residual))),
            "maximum_absolute_error_gate_fraction": float(np.max(np.abs(residual))),
            "maximum_absolute_error_time_ms": float(sample_time[mask][maximum_index]),
            "mean_signed_residual_gate_fraction": float(np.mean(residual)),
        }
    return {"samples_compared": int(np.count_nonzero(mask)), "gates": summaries}


def load_humanjs_gate_trace(path: Path) -> tuple[Any, dict[str, Any]]:
    import numpy as np

    trace = np.genfromtxt(path, delimiter=",", names=True, dtype=float)
    if trace.dtype.names is None or not set(("time_ms", *HUMANJS_GATE_NAMES)).issubset(
        trace.dtype.names
    ):
        raise reproduction.ReproductionError(
            "HumanJS gate CSV must contain time_ms and all five named gate columns"
        )
    if trace.ndim == 0 or len(trace) < 2:
        raise reproduction.ReproductionError("HumanJS gate CSV must contain at least two rows")
    times = np.asarray(trace["time_ms"], dtype=float)
    if not np.isfinite(times).all() or np.any(np.diff(times) <= 0.0):
        raise reproduction.ReproductionError("HumanJS gate timestamps must be finite and strictly increasing")
    gates = {name: np.asarray(trace[name], dtype=float) for name in HUMANJS_GATE_NAMES}
    for name, values in gates.items():
        if not np.isfinite(values).all() or np.any((values < 0.0) | (values > 1.0)):
            raise reproduction.ReproductionError(
                f"HumanJS gate {name} must contain finite values within [0, 1]"
            )
    return times, gates


def load_humanjs_voltage_stage_trace(path: Path) -> tuple[Any, Any]:
    import numpy as np

    names = (
        "time_ms",
        "stage_1_voltage_mv",
        "stage_2_voltage_mv",
        "stage_3_voltage_mv",
        "stage_4_voltage_mv",
    )
    trace = np.genfromtxt(path, delimiter=",", names=True, dtype=float)
    if trace.dtype.names is None or not set(names).issubset(trace.dtype.names):
        raise reproduction.ReproductionError(
            "HumanJS RK4 stage CSV must contain time_ms and all four named voltage stages"
        )
    if trace.ndim == 0 or len(trace) < 2:
        raise reproduction.ReproductionError(
            "HumanJS RK4 stage CSV must contain at least two rows"
        )
    times = np.asarray(trace["time_ms"], dtype=float)
    stages = np.column_stack([np.asarray(trace[name], dtype=float) for name in names[1:]])
    if (
        not np.isfinite(times).all()
        or not np.isfinite(stages).all()
        or np.any(np.diff(times) <= 0.0)
    ):
        raise reproduction.ReproductionError(
            "HumanJS RK4 stage timestamps and voltage values must be finite and timestamps strictly increasing"
        )
    return times, stages



def load_humanjs_current_balance_trace(path: Path) -> tuple[Any, Any, Any]:
    import numpy as np

    names = ["time_ms"]
    for stage in range(1, 5):
        names.extend(
            f"stage_{stage}_{field}"
            for field in (
                "na_a_per_m2",
                "k_a_per_m2",
                "leak_a_per_m2",
                "injected_a_per_m2",
                "dvdt_v_per_s",
            )
        )
    names.extend(
        (
            "endpoint_na_a_per_m2",
            "endpoint_k_a_per_m2",
            "endpoint_leak_a_per_m2",
            "endpoint_injected_a_per_m2",
            "endpoint_dvdt_v_per_s",
        )
    )
    trace = np.genfromtxt(path, delimiter=",", names=True, dtype=float)
    if trace.dtype.names is None or not set(names).issubset(trace.dtype.names):
        raise reproduction.ReproductionError(
            "HumanJS current CSV must contain four five-term RK4 current-balance stages and endpoint balance"
        )
    if trace.ndim == 0 or len(trace) < 2:
        raise reproduction.ReproductionError("HumanJS current CSV must contain at least two rows")
    times = np.asarray(trace["time_ms"], dtype=float)
    stages = np.empty((len(times), 4, 5), dtype=float)
    for stage in range(1, 5):
        for column, field in enumerate(
            ("na_a_per_m2", "k_a_per_m2", "leak_a_per_m2", "injected_a_per_m2", "dvdt_v_per_s")
        ):
            stages[:, stage - 1, column] = np.asarray(
                trace[f"stage_{stage}_{field}"], dtype=float
            )
    endpoint = np.column_stack(
        [
            np.asarray(trace[f"endpoint_{field}"], dtype=float)
            for field in (
                "na_a_per_m2",
                "k_a_per_m2",
                "leak_a_per_m2",
                "injected_a_per_m2",
                "dvdt_v_per_s",
            )
        ]
    )
    if (
        not np.isfinite(times).all()
        or not np.isfinite(stages).all()
        or not np.isfinite(endpoint).all()
        or np.any(np.diff(times) <= 0.0)
    ):
        raise reproduction.ReproductionError(
            "HumanJS current timestamps and stage/endpoint values must be finite with strictly increasing timestamps"
        )
    return times, stages, endpoint


def _wilbers_current_density_a_per_m2(
    voltage_mv: Any,
    gates: Any,
    gbar_na: float,
    gbar_k: float,
) -> Any:
    import numpy as np

    voltage = np.asarray(voltage_mv, dtype=float)
    state = np.asarray(gates, dtype=float)
    if (
        voltage.ndim != 1
        or state.shape != (len(voltage), 5)
        or not np.isfinite(voltage).all()
        or not np.isfinite(state).all()
        or np.any((state < 0.0) | (state > 1.0))
    ):
        raise reproduction.ReproductionError(
            "Wilbers current reconstruction requires finite voltage and five bounded gate columns"
        )
    m_na, h_na, m_k, h1_k, h2_k = state.T
    sodium_q10 = 2.3 ** ((34.0 - 25.0) / 10.0)
    sodium = gbar_na * sodium_q10 * m_na**3 * h_na * (
        voltage / 1000.0 - 0.068
    )
    potassium = gbar_k * m_k**2 * (
        h1_k * 0.85 * 0.60 + h2_k * 0.85 * 0.40 + 0.15
    ) * (voltage / 1000.0 + 0.086)
    leak = voltage / 1000.0 + 0.070
    return np.column_stack((sodium, potassium, leak))



def _numeric_metrics(reference: Any, compared: Any) -> dict[str, Any]:
    import numpy as np

    a = np.asarray(reference, dtype=float)
    b = np.asarray(compared, dtype=float)
    if a.shape != b.shape or a.size == 0 or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise reproduction.ReproductionError("Numerical metrics require matching finite arrays")
    residual = a - b
    return {
        "rmse": float(np.sqrt(np.mean(residual * residual))),
        "maximum_absolute_error": float(np.max(np.abs(residual))),
        "mean_absolute_error": float(np.mean(np.abs(residual))),
    }


def _current_component_metrics(reference: Any, compared: Any) -> dict[str, Any]:
    import numpy as np

    a = np.asarray(reference, dtype=float)
    b = np.asarray(compared, dtype=float)
    if a.shape != b.shape or a.size == 0 or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise reproduction.ReproductionError("Current-balance metrics require matching finite arrays")
    residual = a - b
    return {
        "rmse_A_per_m2": float(np.sqrt(np.mean(residual * residual))),
        "maximum_absolute_error_A_per_m2": float(np.max(np.abs(residual))),
        "mean_absolute_error_A_per_m2": float(np.mean(np.abs(residual))),
    }



def replay_wilbers_source_order(
    times_ms: Any,
    initial_voltage_mv: float,
    initial_gates: Any,
    injected_current_pa: float,
    gbar_na: float,
    gbar_k: float,
    na_rate_table: tuple[Any, Any] | None,
) -> tuple[Any, Any]:
    """Replay secondorder=0 voltage-first / post-voltage CNEXP source ordering."""
    import numpy as np

    times = np.asarray(times_ms, dtype=float)
    gates = np.asarray(initial_gates, dtype=float)
    if (
        times.ndim != 1
        or len(times) < 2
        or not np.isfinite(times).all()
        or np.any(np.diff(times) <= 0.0)
        or not np.isfinite(initial_voltage_mv)
        or gates.shape != (5,)
        or not np.isfinite(gates).all()
        or np.any((gates < 0.0) | (gates > 1.0))
    ):
        raise reproduction.ReproductionError("Source-order replay requires finite, aligned initial states")
    steps_ms = np.diff(times)
    if not np.allclose(steps_ms, steps_ms[0], rtol=0.0, atol=1.0e-9):
        raise reproduction.ReproductionError("Source-order replay requires a uniform fixed timestep")

    dt_seconds = float(steps_ms[0]) * 1.0e-3
    capacitance_f_per_m2 = 0.01
    area_m2 = np.pi * 100.0e-12
    injected_density = injected_current_pa * 1.0e-12 / area_m2
    sodium_q10 = 2.3 ** ((34.0 - 25.0) / 10.0)
    voltage = np.empty(len(times), dtype=float)
    gate_path = np.empty((len(times), 5), dtype=float)
    voltage[0] = float(initial_voltage_mv)
    gate_path[0] = gates
    for index, interval_start_ms in enumerate(times[:-1]):
        current_density = (
            injected_density
            if 1.0 - 1.0e-9 <= interval_start_ms < 4.0 - 1.0e-9
            else 0.0
        )
        m_na, h_na, m_k, h1_k, h2_k = gates
        sodium_conductance = gbar_na * sodium_q10 * m_na**3 * h_na
        potassium_conductance = gbar_k * m_k**2 * (
            h1_k * 0.85 * 0.60 + h2_k * 0.85 * 0.40 + 0.15
        )
        conductance_sum = sodium_conductance + potassium_conductance + 1.0
        old_voltage_v = voltage[index] * 1.0e-3
        new_voltage_v = (
            capacitance_f_per_m2 / dt_seconds * old_voltage_v
            + current_density
            + sodium_conductance * 0.068
            - potassium_conductance * 0.086
            - 0.070
        ) / (capacitance_f_per_m2 / dt_seconds + conductance_sum)
        voltage[index + 1] = new_voltage_v * 1.0e3
        gates = _shared_voltage_cnexp_step(
            gates,
            voltage[index + 1] - 10.0,
            float(steps_ms[index]),
            na_rate_table,
        )
        if not np.isfinite(gates).all() or np.any((gates < 0.0) | (gates > 1.0)):
            raise reproduction.ReproductionError("Source-order replay produced invalid gate fractions")
        gate_path[index + 1] = gates
    return voltage, gate_path


def compare_membrane_current_balance(
    source_times_ms: Any,
    source_voltage_mv: Any,
    source_gates: dict[str, Any],
    source_currents_mA_per_cm2: dict[str, Any],
    humanjs_voltage_times_ms: Any,
    humanjs_voltage_mv: Any,
    humanjs_current_times_ms: Any,
    humanjs_current_stages: Any,
    humanjs_endpoint_currents: Any,
    injected_current_pa: float,
    gbar_na: float,
    gbar_k: float,
) -> dict[str, Any]:
    """Compare the source's staggered fixed-step current balance with HumanJS RK4."""
    import numpy as np

    source_times = np.asarray(source_times_ms, dtype=float)
    source_voltage = np.asarray(source_voltage_mv, dtype=float)
    hj_times = np.asarray(humanjs_voltage_times_ms, dtype=float)
    hj_voltage = np.asarray(humanjs_voltage_mv, dtype=float)
    current_times = np.asarray(humanjs_current_times_ms, dtype=float)
    stages = np.asarray(humanjs_current_stages, dtype=float)
    endpoint = np.asarray(humanjs_endpoint_currents, dtype=float)
    source_gate_matrix = np.column_stack(
        [np.asarray(source_gates[name], dtype=float) for name in SOURCE_GATE_NAMES]
    )
    source_current_matrix = np.column_stack(
        [
            np.asarray(source_currents_mA_per_cm2[name], dtype=float)
            for name in ("ina", "ik", "i_pas")
        ]
    ) * 10.0  # NEURON mA/cm² -> SI A/m².

    if (
        source_times.ndim != 1
        or len(source_times) < 3
        or source_voltage.shape != source_times.shape
        or source_gate_matrix.shape != (len(source_times), 5)
        or source_current_matrix.shape != (len(source_times), 3)
        or not np.isfinite(source_times).all()
        or not np.isfinite(source_voltage).all()
        or not np.isfinite(source_gate_matrix).all()
        or not np.isfinite(source_current_matrix).all()
        or np.any(np.diff(source_times) <= 0.0)
        or np.any((source_gate_matrix < 0.0) | (source_gate_matrix > 1.0))
    ):
        raise reproduction.ReproductionError("Source current-balance samples are malformed or non-finite")
    step_ms = np.diff(source_times)
    if not np.allclose(step_ms, step_ms[0], rtol=0.0, atol=1.0e-9):
        raise reproduction.ReproductionError("Source current-balance requires a uniform fixed timestep")
    if (
        hj_times.shape != hj_voltage.shape
        or current_times.shape != hj_times.shape
        or stages.shape != (len(hj_times), 4, 5)
        or endpoint.shape != (len(hj_times), 5)
        or not np.allclose(hj_times, source_times[1:], rtol=0.0, atol=1.0e-9)
        or not np.allclose(current_times, hj_times, rtol=0.0, atol=1.0e-9)
    ):
        raise reproduction.ReproductionError(
            "Source, HumanJS voltage, and HumanJS current traces must have exactly aligned post-step timestamps"
        )

    # The source's voltage solve uses the previous recorded gate state with
    # the implicit endpoint voltage. The post-step BREAKPOINT current uses
    # the newly recorded gate state; these are distinct current evaluations.
    source_solver_current = _wilbers_current_density_a_per_m2(
        source_voltage[1:], source_gate_matrix[:-1], gbar_na, gbar_k
    )
    source_endpoint_formula = _wilbers_current_density_a_per_m2(
        source_voltage[1:], source_gate_matrix[1:], gbar_na, gbar_k
    )
    source_voltage_derivative = np.diff(source_voltage) * 1.0e-3 / (
        step_ms[0] * 1.0e-3
    )
    specific_capacitance_f_per_m2 = 0.01
    surface_area_m2 = np.pi * 100.0e-12
    interval_start_times = source_times[:-1]
    injected_density = np.where(
        (interval_start_times >= 1.0 - 1.0e-9)
        & (interval_start_times < 4.0 - 1.0e-9),
        injected_current_pa * 1.0e-12 / surface_area_m2,
        0.0,
    )
    source_capacitance_current = specific_capacitance_f_per_m2 * source_voltage_derivative
    source_current_rhs = injected_density - np.sum(source_solver_current, axis=1)
    recorded_endpoint_current = source_current_matrix[1:]
    humanjs_weighted_current = (
        stages[:, 0, :3]
        + 2.0 * stages[:, 1, :3]
        + 2.0 * stages[:, 2, :3]
        + stages[:, 3, :3]
    ) / 6.0
    humanjs_weighted_dvdt = (
        stages[:, 0, 4]
        + 2.0 * stages[:, 1, 4]
        + 2.0 * stages[:, 2, 4]
        + stages[:, 3, 4]
    ) / 6.0
    humanjs_injected = stages[:, :, 3]
    humanjs_injected_weighted = (
        humanjs_injected[:, 0]
        + 2.0 * humanjs_injected[:, 1]
        + 2.0 * humanjs_injected[:, 2]
        + humanjs_injected[:, 3]
    ) / 6.0
    humanjs_capacitance_current = specific_capacitance_f_per_m2 * humanjs_weighted_dvdt
    humanjs_voltage_derivative = np.diff(
        np.concatenate(([-70.0], hj_voltage))
    ) * 1.0e-3 / (step_ms[0] * 1.0e-3)

    names = ("sodium", "potassium", "leak")
    return {
        "source_voltage_update": {
            "method": "implicit endpoint voltage with the previous-step recorded gate state",
            "gate_state_sample": "G[n] from timestamp t[n], paired with endpoint voltage V[n+1]",
            "current_law_vs_neuron_poststep_current": {
                name: _current_component_metrics(
                    source_endpoint_formula[:, index],
                    recorded_endpoint_current[:, index],
                )
                for index, name in enumerate(names)
            },
            "capacitor_equation_residual": _current_component_metrics(
                source_capacitance_current, source_current_rhs
            ),
            "interpretation": (
                "The source voltage increment is numerically accounted for by the Wilbers current equations "
                "evaluated at V[n+1] with G[n]. The endpoint BREAKPOINT currents use G[n+1]; "
                "the gate/current sampling is staggered across the fixed step."
            ),
        },
        "source_solver_current_vs_humanjs_rk4_weighted_current": {
            name: _current_component_metrics(
                source_solver_current[:, index],
                humanjs_weighted_current[:, index],
            )
            for index, name in enumerate(names)
        },
        "source_solver_total_vs_humanjs_weighted_total": _current_component_metrics(
            np.sum(source_solver_current, axis=1),
            np.sum(humanjs_weighted_current, axis=1),
        ),
        "humanjs_rk4_current_balance": {
            "weighted_capacitance_current_vs_weighted_stage_rhs": _current_component_metrics(
                humanjs_capacitance_current,
                humanjs_injected_weighted - np.sum(humanjs_weighted_current, axis=1),
            ),
            "weighted_stage_voltage_derivative_vs_recorded_increment": _numeric_metrics(
                humanjs_weighted_dvdt,
                humanjs_voltage_derivative,
            ),
            "weighted_injected_current_density_range_A_per_m2": [
                float(np.min(humanjs_injected_weighted)),
                float(np.max(humanjs_injected_weighted)),
            ],
            "endpoint_current_components": {
                name: _current_component_metrics(
                    recorded_endpoint_current[:, index],
                    endpoint[:, index],
                )
                for index, name in enumerate(names)
            },
        },
        "units": {
            "ionic_current_density": "A/m²",
            "specific_capacitance": "0.01 F/m² (1 µF/cm² source setup)",
            "surface_area": "π × 100 µm² (10-µm diameter, 10-µm length cylinder)",
            "neuron_current_conversion": "10 A/m² per mA/cm²",
        },
        "interpretation_limit": (
            "This verifies numerical current-law and integration identities for the deposited source and HumanJS "
            "implementation. It does not establish biological accuracy or imply that either numerical method is "
            "biologically superior."
        ),
    }


def save_source_gate_trace(
    path: Path,
    times_ms: Any,
    gates: dict[str, Any],
) -> None:
    import numpy as np

    path.parent.mkdir(parents=True, exist_ok=True)
    matrix = np.column_stack((times_ms, *[gates[name] for name in SOURCE_GATE_NAMES]))
    np.savetxt(
        path,
        matrix,
        delimiter=",",
        header="time_ms," + ",".join(SOURCE_GATE_NAMES),
        comments="",
        fmt="%.12g",
    )


def _sigmoid(value: float) -> float:
    import math

    if value >= 0.0:
        exponential = math.exp(-value)
        return 1.0 / (1.0 + exponential)
    exponential = math.exp(value)
    return exponential / (1.0 + exponential)


def _source_trap0(voltage_mv: float, half_voltage_mv: float, prefactor: float, slope_mv: float) -> float:
    """Stable analytic form of the deposited trap0 rate, away from its defective fallback."""
    import math

    x = (voltage_mv - half_voltage_mv) / slope_mv
    if abs(x) < 1.0e-7:
        ratio = 1.0 + x / 2.0 + x * x / 12.0 - x**4 / 720.0
    else:
        ratio = x / -math.expm1(-x)
    return prefactor * slope_mv * ratio


def _wilbers_gate_rate_bundle(
    effective_voltage_mv: float,
    na_rate_table: tuple[Any, Any] | None = None,
) -> tuple[float, ...]:
    """Pure human Na/K rates; optionally linearly interpolate source Na TABLE outputs."""
    na_temperature_factor = 2.3 ** 0.9

    na_alpha_m = _source_trap0(
        effective_voltage_mv, -58.59235606617833, 0.2139849270413559, 9.21455371864071
    )
    na_beta_m = _source_trap0(
        -effective_voltage_mv, 58.59235606617833, 0.2139849270413559, 9.21455371864071
    )
    na_m_inf = _sigmoid((effective_voltage_mv + 42.29145668954657) / 10.231152896063074)
    na_m_tau = 1.0 / (na_temperature_factor * (na_alpha_m + na_beta_m))

    na_alpha_h = _source_trap0(
        effective_voltage_mv, -39.298676911255, 0.0476391878313753, 7.21636386592805
    )
    na_beta_h = _source_trap0(
        -effective_voltage_mv, 77.16674532461128, 0.011951655023359499, 4.749450048393884
    )
    na_h_inf = _sigmoid((-64.48 - effective_voltage_mv) / 11.02)
    na_h_tau = 1.0 / (na_temperature_factor * (na_alpha_h + na_beta_h))

    k_alpha_m = _source_trap0(
        effective_voltage_mv, -29.961798016904638, 0.018459250585411965, 6.590405688881463
    )
    k_beta_m = _source_trap0(
        -effective_voltage_mv, 29.961798016904638, 0.018459250585411965, 6.590405688881463
    )
    k_m_inf = _sigmoid((effective_voltage_mv + 18.406163539758502) / 19.199550273441083)
    k_m_tau = 1.0 / (k_alpha_m + k_beta_m)

    k_alpha_h = _source_trap0(
        effective_voltage_mv, 40.5659148938157, 0.0016901435659310753, 26.773929244740913
    )
    k_beta_h = _source_trap0(
        -effective_voltage_mv, 75.93822659307075, 0.0004968791312639546, 0.40183382749400054
    )
    k_h_inf = _sigmoid((-52.61 - effective_voltage_mv) / 13.09)
    k_h_tau = 1.0 / (k_alpha_h + k_beta_h)

    if na_rate_table is not None:
        import numpy as np

        table_voltage, table_values = na_rate_table
        na_m_inf, na_m_tau, na_h_inf, na_h_tau = (
            float(np.interp(effective_voltage_mv, table_voltage, table_values[:, index]))
            for index in range(4)
        )

    return (
        na_m_inf, na_m_tau, na_h_inf, na_h_tau,
        k_m_inf, k_m_tau, k_h_inf, k_h_tau,
        2789.7929428108187, 450.0,
    )


def _build_source_na_rate_table() -> tuple[Any, Any]:
    import numpy as np

    voltage_nodes = np.linspace(-120.0, 100.0, 200)
    values = np.asarray(
        [_wilbers_gate_rate_bundle(float(voltage))[:4] for voltage in voltage_nodes],
        dtype=float,
    )
    return voltage_nodes, values


def _shared_voltage_gate_derivative(
    gates: Any,
    effective_voltage_mv: float,
    na_rate_table: tuple[Any, Any] | None = None,
) -> Any:
    import numpy as np

    (
        na_m_inf, na_m_tau, na_h_inf, na_h_tau,
        k_m_inf, k_m_tau, k_h_inf, k_h_tau,
        k_h_slow_recovery_tau, k_h_slow_inactivation_tau,
    ) = _wilbers_gate_rate_bundle(effective_voltage_mv, na_rate_table)
    k_h2_tau = k_h_slow_recovery_tau if k_h_inf > gates[4] else k_h_slow_inactivation_tau
    return np.asarray(
        [
            (na_m_inf - gates[0]) / na_m_tau,
            (na_h_inf - gates[1]) / na_h_tau,
            (k_m_inf - gates[2]) / k_m_tau,
            (k_h_inf - gates[3]) / k_h_tau,
            (k_h_inf - gates[4]) / k_h2_tau,
        ],
        dtype=float,
    )


def _shared_voltage_cnexp_step(
    gates: Any,
    effective_voltage_mv: float,
    dt_ms: float,
    na_rate_table: tuple[Any, Any] | None = None,
) -> Any:
    import numpy as np

    (
        na_m_inf, na_m_tau, na_h_inf, na_h_tau,
        k_m_inf, k_m_tau, k_h_inf, k_h_tau,
        k_h_slow_recovery_tau, k_h_slow_inactivation_tau,
    ) = _wilbers_gate_rate_bundle(effective_voltage_mv, na_rate_table)
    k_h2_tau = k_h_slow_recovery_tau if k_h_inf > gates[4] else k_h_slow_inactivation_tau
    steady_states = np.asarray([na_m_inf, na_h_inf, k_m_inf, k_h_inf, k_h_inf])
    time_constants = np.asarray([na_m_tau, na_h_tau, k_m_tau, k_h_tau, k_h2_tau])
    return steady_states + (gates - steady_states) * np.exp(-dt_ms / time_constants)


def _shared_voltage_rk4_step(
    gates: Any,
    effective_voltage_mv: float,
    dt_ms: float,
    na_rate_table: tuple[Any, Any] | None = None,
) -> Any:
    import numpy as np

    k1 = _shared_voltage_gate_derivative(gates, effective_voltage_mv, na_rate_table)
    k2 = _shared_voltage_gate_derivative(
        gates + 0.5 * dt_ms * k1, effective_voltage_mv, na_rate_table
    )
    k3 = _shared_voltage_gate_derivative(
        gates + 0.5 * dt_ms * k2, effective_voltage_mv, na_rate_table
    )
    k4 = _shared_voltage_gate_derivative(
        gates + dt_ms * k3, effective_voltage_mv, na_rate_table
    )
    return gates + (dt_ms / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def _shared_voltage_rk4_step_linear_voltage(
    gates: Any,
    voltage_start_mv: float,
    voltage_end_mv: float,
    dt_ms: float,
    na_rate_table: tuple[Any, Any] | None = None,
) -> Any:
    """RK4 gate update with linearly interpolated voltage at RK stage times."""
    import numpy as np

    midpoint_mv = 0.5 * (voltage_start_mv + voltage_end_mv)
    k1 = _shared_voltage_gate_derivative(gates, voltage_start_mv, na_rate_table)
    k2 = _shared_voltage_gate_derivative(
        gates + 0.5 * dt_ms * k1, midpoint_mv, na_rate_table
    )
    k3 = _shared_voltage_gate_derivative(
        gates + 0.5 * dt_ms * k2, midpoint_mv, na_rate_table
    )
    k4 = _shared_voltage_gate_derivative(
        gates + dt_ms * k3, voltage_end_mv, na_rate_table
    )
    return gates + (dt_ms / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def _shared_voltage_rk4_step_with_stages(
    gates: Any,
    effective_voltage_stages_mv: Any,
    dt_ms: float,
    na_rate_table: tuple[Any, Any] | None = None,
) -> Any:
    """RK4 gate update using the four actual coupled membrane voltage stages."""
    import numpy as np

    voltages = np.asarray(effective_voltage_stages_mv, dtype=float)
    if voltages.shape != (4,) or not np.isfinite(voltages).all():
        raise reproduction.ReproductionError(
            "Actual RK4 voltage replay requires four finite voltage-stage samples"
        )
    k1 = _shared_voltage_gate_derivative(gates, float(voltages[0]), na_rate_table)
    k2 = _shared_voltage_gate_derivative(
        gates + 0.5 * dt_ms * k1, float(voltages[1]), na_rate_table
    )
    k3 = _shared_voltage_gate_derivative(
        gates + 0.5 * dt_ms * k2, float(voltages[2]), na_rate_table
    )
    k4 = _shared_voltage_gate_derivative(
        gates + dt_ms * k3, float(voltages[3]), na_rate_table
    )
    return gates + (dt_ms / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def _gate_path_metrics(actual: Any, reference: Any) -> dict[str, Any]:
    import numpy as np

    actual_values = np.asarray(actual, dtype=float)
    reference_values = np.asarray(reference, dtype=float)
    if (
        actual_values.ndim != 2
        or actual_values.shape[1] != len(HUMANJS_GATE_NAMES)
        or actual_values.shape != reference_values.shape
        or actual_values.shape[0] == 0
        or not np.isfinite(actual_values).all()
        or not np.isfinite(reference_values).all()
    ):
        raise reproduction.ReproductionError(
            "Gate-path metrics require matching finite non-empty arrays with five gate columns"
        )
    residual = actual_values - reference_values
    return {
        "overall_rmse_gate_fraction": float(np.sqrt(np.mean(residual * residual))),
        "overall_maximum_absolute_error_gate_fraction": float(np.max(np.abs(residual))),
        "per_gate_rmse_gate_fraction": {
            name: float(np.sqrt(np.mean(residual[:, index] ** 2)))
            for index, name in enumerate(HUMANJS_GATE_NAMES)
        },
        "per_gate_maximum_absolute_error_gate_fraction": {
            name: float(np.max(np.abs(residual[:, index])))
            for index, name in enumerate(HUMANJS_GATE_NAMES)
        },
    }


def compare_gate_integrators_on_shared_voltage(
    times_ms: Any,
    voltage_mv: Any,
    source_gates: dict[str, Any],
    use_na_table: int,
) -> dict[str, Any]:
    """Compare cnexp and RK4 gate updates under an identical sampled voltage path.

    Both methods receive the post-step voltage sample V[n+1] for the gate
    update ending at t[n+1], as confirmed by replaying recorded NMODL states.
    The method-only pair uses the same direct analytic source rates with the
    Na lookup table disabled; a separate CNEXP pair quantifies the source's
    200-node Na TABLE interpolation. This is a numerical-method experiment,
    not a biological comparison.
    """
    import numpy as np

    times = np.asarray(times_ms, dtype=float)
    voltage = np.asarray(voltage_mv, dtype=float)
    if len(times) < 2 or len(times) != len(voltage):
        raise reproduction.ReproductionError("Shared-voltage input must have matching samples")
    steps = np.diff(times)
    if not np.isfinite(times).all() or not np.isfinite(voltage).all() or np.any(steps <= 0.0):
        raise reproduction.ReproductionError("Shared-voltage samples must be finite with increasing times")

    # Validate the complete recorded NMODL state path before constructing any
    # counterfactual, so malformed traces cannot be silently broadcast or sliced.
    source_gate_columns = [
        np.asarray(source_gates[name], dtype=float) for name in SOURCE_GATE_NAMES
    ]
    if any(column.shape != times.shape for column in source_gate_columns):
        raise reproduction.ReproductionError(
            "Shared-voltage source gates must match the voltage sample count"
        )
    recorded_source_gates = np.column_stack(source_gate_columns)
    if (
        not np.isfinite(recorded_source_gates).all()
        or np.any((recorded_source_gates < 0.0) | (recorded_source_gates > 1.0))
    ):
        raise reproduction.ReproductionError(
            "Shared-voltage source gates must be finite [0, 1] arrays matching the voltage samples"
        )

    # Both counterfactual methods begin from the same actual NMODL state at t=0.
    initial = recorded_source_gates[0].copy()
    if not np.isfinite(initial).all() or np.any((initial < 0.0) | (initial > 1.0)):
        raise reproduction.ReproductionError("Shared-voltage initial source gates must be finite and in [0, 1]")
    na_rate_table = _build_source_na_rate_table()
    cnexp = np.empty((len(times), 5), dtype=float)
    rk4 = np.empty((len(times), 5), dtype=float)
    rk4_left = np.empty((len(times), 5), dtype=float)
    rk4_midpoint = np.empty((len(times), 5), dtype=float)
    rk4_linear = np.empty((len(times), 5), dtype=float)
    cnexp_table = np.empty((len(times), 5), dtype=float)
    cnexp[0] = initial
    rk4[0] = initial
    rk4_left[0] = initial
    rk4_midpoint[0] = initial
    rk4_linear[0] = initial
    cnexp_table[0] = initial

    for index, dt_ms in enumerate(steps):
        voltage_left = float(voltage[index]) - 10.0
        voltage_right = float(voltage[index + 1]) - 10.0
        voltage_midpoint = 0.5 * (voltage_left + voltage_right)
        step = float(dt_ms)
        cnexp[index + 1] = _shared_voltage_cnexp_step(
            cnexp[index], voltage_right, step
        )
        rk4[index + 1] = _shared_voltage_rk4_step(
            rk4[index], voltage_right, step
        )
        rk4_left[index + 1] = _shared_voltage_rk4_step(
            rk4_left[index], voltage_left, step
        )
        rk4_midpoint[index + 1] = _shared_voltage_rk4_step(
            rk4_midpoint[index], voltage_midpoint, step
        )
        rk4_linear[index + 1] = _shared_voltage_rk4_step_linear_voltage(
            rk4_linear[index], voltage_left, voltage_right, step
        )
        cnexp_table[index + 1] = _shared_voltage_cnexp_step(
            cnexp_table[index], voltage_right, step, na_rate_table
        )

    paths = (cnexp, rk4, rk4_left, rk4_midpoint, rk4_linear, cnexp_table)
    if any(not np.isfinite(path).all() for path in paths):
        raise reproduction.ReproductionError(
            "Shared-voltage gate integrations produced non-finite states"
        )
    if any(np.any((path < 0.0) | (path > 1.0)) for path in paths):
        raise reproduction.ReproductionError(
            "Shared-voltage gate integration left the [0, 1] state bounds"
        )

    residual = rk4 - cnexp
    table_residual = cnexp_table - cnexp
    gate_metrics: dict[str, Any] = {}
    for index, name in enumerate(HUMANJS_GATE_NAMES):
        values = residual[:, index]
        max_index = int(np.argmax(np.abs(values)))
        gate_metrics[name] = {
            "rmse_gate_fraction": float(np.sqrt(np.mean(values * values))),
            "maximum_absolute_error_gate_fraction": float(np.max(np.abs(values))),
            "maximum_absolute_error_time_ms": float(times[max_index]),
            "final_cnexp_gate_fraction": float(cnexp[-1, index]),
            "final_rk4_gate_fraction": float(rk4[-1, index]),
        }

    table_gate_metrics: dict[str, Any] = {}
    for index, name in enumerate(HUMANJS_GATE_NAMES):
        values = table_residual[:, index]
        max_index = int(np.argmax(np.abs(values)))
        table_gate_metrics[name] = {
            "rmse_gate_fraction": float(np.sqrt(np.mean(values * values))),
            "maximum_absolute_error_gate_fraction": float(np.max(np.abs(values))),
            "maximum_absolute_error_time_ms": float(times[max_index]),
        }

    source_replay_gates = cnexp_table if use_na_table == 1 else cnexp
    source_residual = source_replay_gates - np.column_stack(
        [source_gates[name] for name in SOURCE_GATE_NAMES]
    )
    source_replay_maximum = float(np.max(np.abs(source_residual)))
    source_replay = {
        "rate_mode": "200-node linear Na TABLE" if use_na_table == 1 else "direct analytic Na rates",
        "comparison": "same voltage samples and matching Na rate mode; recorded NMODL gate states",
        "maximum_absolute_error_tolerance_gate_fraction": 1.0e-4,
        "overall_rmse_gate_fraction": float(np.sqrt(np.mean(source_residual * source_residual))),
        "overall_maximum_absolute_error_gate_fraction": source_replay_maximum,
        "per_gate_rmse_gate_fraction": {
            name: float(np.sqrt(np.mean(source_residual[:, index] ** 2)))
            for index, name in enumerate(HUMANJS_GATE_NAMES)
        },
    }
    if source_replay_maximum > 1.0e-4:
        raise reproduction.ReproductionError(
            "Shared-voltage cnexp recurrence did not reproduce the matching "
            f"NMODL gate states within 1e-4 (max {source_replay_maximum:.6g})"
        )

    return {
        "method_a": "exact exponential gate update (cnexp equivalent)",
        "method_b": "classical RK4 gate update",
        "shared_voltage_contract": "post-step V[n+1] held for the gate update ending at t[n+1]",
        "rate_contract": "direct analytic rates for the cnexp/RK4 pair; source-table interpolation evaluated separately",
        "initial_state_contract": "same recorded NMODL gate state at t=0",
        "comparison_to_recorded_nmodl_cnexp": source_replay,
        "samples": int(len(times)),
        "intervals": int(len(steps)),
        "dt_min_ms": float(np.min(steps)),
        "dt_max_ms": float(np.max(steps)),
        "overall_gate_rmse_fraction": float(np.sqrt(np.mean(residual * residual))),
        "overall_gate_maximum_absolute_error_fraction": float(np.max(np.abs(residual))),
        "per_gate": gate_metrics,
        "source_na_table_rate_sensitivity": {
            "comparison": "cnexp with linear 200-node source Na TABLE versus direct analytic rates on the same voltage path",
            "overall_gate_rmse_fraction": float(np.sqrt(np.mean(table_residual * table_residual))),
            "overall_gate_maximum_absolute_error_fraction": float(np.max(np.abs(table_residual))),
            "per_gate": table_gate_metrics,
        },
        "voltage_stage_sampling_sensitivity": {
            "purpose": "isolate gate sensitivity to voltage sampling while keeping the recorded source voltage trajectory, initial gates, rates, and RK4 gate update fixed",
            "voltage_shift_mV": -10.0,
            "methods_against_recorded_nmodl_gates": {
                "left_endpoint_hold_rk4": _gate_path_metrics(
                    rk4_left, recorded_source_gates
                ),
                "midpoint_hold_rk4": _gate_path_metrics(
                    rk4_midpoint, recorded_source_gates
                ),
                "right_endpoint_hold_rk4": _gate_path_metrics(
                    rk4, recorded_source_gates
                ),
                "linear_voltage_ramp_rk4": _gate_path_metrics(
                    rk4_linear, recorded_source_gates
                ),
            },
            "linear_ramp_vs_right_hold": _gate_path_metrics(rk4_linear, rk4),
            "interpretation_limit": "The linear ramp is an externally prescribed interpolation of the NEURON voltage samples, not the actual intermediate voltage stages of the coupled HumanJS RK4 solver. It isolates a voltage-sampling counterfactual and does not partition full coupled feedback.",
        },
    }

def compare_gate_sampling_on_humanjs_voltage(
    initial_time_ms: float,
    initial_voltage_mv: float,
    initial_gates: Any,
    humanjs_voltage_times_ms: Any,
    humanjs_voltage_mv: Any,
    humanjs_gate_times_ms: Any,
    humanjs_gates: dict[str, Any],
    use_na_table: int,
    humanjs_voltage_stage_times_ms: Any | None = None,
    humanjs_voltage_stages_mv: Any | None = None,
) -> dict[str, Any]:
    """Replay source gate equations on HumanJS's sampled voltage path.

    The HumanJS voltage/gate traces contain post-step samples. The source
    initial condition supplies the shared t=0 voltage and gate state. Voltage
    between samples is prescribed as left, midpoint, right, or linear-ramp;
    these are counterfactuals, not captured internal RK4 voltage stages.
    """
    import numpy as np

    voltage_times = np.asarray(humanjs_voltage_times_ms, dtype=float)
    voltage = np.asarray(humanjs_voltage_mv, dtype=float)
    gate_times = np.asarray(humanjs_gate_times_ms, dtype=float)
    gate_columns = [
        np.asarray(humanjs_gates[name], dtype=float) for name in HUMANJS_GATE_NAMES
    ]
    initial = np.asarray(initial_gates, dtype=float)
    if (
        voltage_times.ndim != 1
        or voltage.ndim != 1
        or gate_times.ndim != 1
        or len(voltage_times) < 2
        or voltage.shape != voltage_times.shape
        or gate_times.shape != voltage_times.shape
        or any(column.shape != voltage_times.shape for column in gate_columns)
        or initial.shape != (len(HUMANJS_GATE_NAMES),)
    ):
        raise reproduction.ReproductionError(
            "HumanJS voltage and gate replay requires matching one-dimensional samples and five initial gates"
        )
    if (
        not np.isfinite(initial_time_ms)
        or not np.isfinite(initial_voltage_mv)
        or not np.isfinite(voltage_times).all()
        or not np.isfinite(voltage).all()
        or not np.isfinite(gate_times).all()
        or not np.isfinite(initial).all()
        or not np.isfinite(np.column_stack(gate_columns)).all()
        or np.any(np.diff(voltage_times) <= 0.0)
        or np.any(np.diff(gate_times) <= 0.0)
        or np.any((initial < 0.0) | (initial > 1.0))
        or np.any((np.column_stack(gate_columns) < 0.0) | (np.column_stack(gate_columns) > 1.0))
    ):
        raise reproduction.ReproductionError(
            "HumanJS voltage/gate replay samples must be finite, increasing, and gates within [0, 1]"
        )
    if not np.allclose(gate_times, voltage_times, rtol=0.0, atol=1.0e-9):
        raise reproduction.ReproductionError(
            "HumanJS voltage and gate traces must have identical timestamps"
        )
    if (humanjs_voltage_stage_times_ms is None) != (humanjs_voltage_stages_mv is None):
        raise reproduction.ReproductionError(
            "HumanJS RK4 stage timestamps and voltage values must be supplied together"
        )
    stage_times = None
    stage_voltages = None
    if humanjs_voltage_stage_times_ms is not None:
        stage_times = np.asarray(humanjs_voltage_stage_times_ms, dtype=float)
        stage_voltages = np.asarray(humanjs_voltage_stages_mv, dtype=float)
        if (
            stage_times.shape != voltage_times.shape
            or stage_voltages.shape != (len(voltage_times), 4)
            or not np.isfinite(stage_times).all()
            or not np.isfinite(stage_voltages).all()
            or not np.allclose(stage_times, voltage_times, rtol=0.0, atol=1.0e-9)
        ):
            raise reproduction.ReproductionError(
                "HumanJS RK4 voltage stages must have four finite values at every voltage/gate timestamp"
            )
    if voltage_times[0] <= initial_time_ms:
        raise reproduction.ReproductionError(
            "HumanJS trace must contain post-initial voltage samples"
        )

    times = np.concatenate(([float(initial_time_ms)], voltage_times))
    voltages = np.concatenate(([float(initial_voltage_mv)], voltage))
    actual_gates = np.vstack((initial, np.column_stack(gate_columns)))
    if not np.isfinite(voltages).all():
        raise reproduction.ReproductionError("HumanJS initial voltage must be finite")
    steps = np.diff(times)
    if np.any(steps <= 0.0):
        raise reproduction.ReproductionError("HumanJS replay times must increase from the initial state")

    table = _build_source_na_rate_table() if use_na_table == 1 else None
    names = [
        "right_endpoint_cnexp",
        "left_endpoint_hold_rk4",
        "midpoint_hold_rk4",
        "right_endpoint_hold_rk4",
        "linear_voltage_ramp_rk4",
    ]
    if stage_voltages is not None:
        names.append("actual_humanjs_rk4_voltage_stages")
    paths = {name: np.empty_like(actual_gates) for name in names}
    for path in paths.values():
        path[0] = initial

    for index, dt_ms in enumerate(steps):
        left = float(voltages[index]) - 10.0
        right = float(voltages[index + 1]) - 10.0
        midpoint = 0.5 * (left + right)
        step = float(dt_ms)
        paths["right_endpoint_cnexp"][index + 1] = _shared_voltage_cnexp_step(
            paths["right_endpoint_cnexp"][index], right, step, table
        )
        paths["left_endpoint_hold_rk4"][index + 1] = _shared_voltage_rk4_step(
            paths["left_endpoint_hold_rk4"][index], left, step, table
        )
        paths["midpoint_hold_rk4"][index + 1] = _shared_voltage_rk4_step(
            paths["midpoint_hold_rk4"][index], midpoint, step, table
        )
        paths["right_endpoint_hold_rk4"][index + 1] = _shared_voltage_rk4_step(
            paths["right_endpoint_hold_rk4"][index], right, step, table
        )
        paths["linear_voltage_ramp_rk4"][index + 1] = _shared_voltage_rk4_step_linear_voltage(
            paths["linear_voltage_ramp_rk4"][index], left, right, step, table
        )
        if stage_voltages is not None:
            effective_stages = stage_voltages[index] - 10.0
            paths["actual_humanjs_rk4_voltage_stages"][index + 1] = (
                _shared_voltage_rk4_step_with_stages(
                    paths["actual_humanjs_rk4_voltage_stages"][index],
                    effective_stages,
                    step,
                    table,
                )
            )

    if any(
        not np.isfinite(path).all() or np.any((path < 0.0) | (path > 1.0))
        for path in paths.values()
    ):
        raise reproduction.ReproductionError(
            "HumanJS-voltage gate counterfactual produced invalid gate fractions"
        )
    return {
        "purpose": "compare source-rate gate updates on the HumanJS sampled voltage path against HumanJS live gates",
        "na_rate_mode": "200-node linear Na TABLE" if use_na_table == 1 else "direct analytic Na rates",
        "voltage_shift_mV": -10.0,
        "methods_against_humanjs_gates": {
            name: _gate_path_metrics(path, actual_gates) for name, path in paths.items()
        },
        "actual_stage_replay": stage_voltages is not None,
        "interpretation_limit": (
            "When supplied, actual_humanjs_rk4_voltage_stages uses the four membrane voltage "
            "components recorded from the exact coupled HumanJS RK4 derivative-stage states. "
            "The gate-state replay is still a numerical counterfactual, not an independent "
            "biological model or biological validation."
        ),
    }


def run_variant(
    h: Any,
    cell: Any,
    rheobase_pa: float,
    dt_ms: float,
    secondorder: int,
    use_na_table: int,
    feature_extractor: Any,
    trace_path: Path | None,
    gate_path: Path | None,
    current_path: Path | None,
    humanjs_path: Path | None,
    humanjs_gates_path: Path | None,
    humanjs_voltage_stages_path: Path | None,
    humanjs_current_data: tuple[Any, Any, Any] | None,
    gbar_na: float,
    gbar_k: float,
    na_ratio: float,
    k_ratio: float,
    baseline_times: Any,
    baseline_voltage: Any,
) -> dict[str, Any]:
    import numpy as np

    if dt_ms <= 0.0:
        raise reproduction.ReproductionError("dt-ms must be positive")
    if humanjs_current_data is not None and secondorder != 0:
        raise reproduction.ReproductionError(
            "The matched current-balance comparison currently requires NEURON secondorder=0"
        )
    sample_count = round(29.0 / dt_ms)
    if abs(sample_count * dt_ms - 29.0) > 1.0e-8:
        raise reproduction.ReproductionError(
            f"dt-ms={dt_ms} does not divide the 29-ms AP1 protocol exactly"
        )

    # These are numerical controls only. NMODL files and model parameters are
    # unchanged; the original author rheobase has already been measured.
    h.dt = dt_ms
    h.secondorder = secondorder
    h.usetable_na_human = use_na_table
    clamp = h.IClamp(cell(0.5))
    clamp.delay = 1.0
    clamp.dur = 3.0
    clamp.amp = rheobase_pa / 1000.0 * 1.5

    time_vector = h.Vector()
    time_vector.record(h._ref_t)
    voltage_vector = h.Vector()
    voltage_vector.record(cell(0.5)._ref_v)
    gate_vectors = {name: h.Vector() for name in SOURCE_GATE_NAMES}
    for name, vector in gate_vectors.items():
        vector.record(getattr(cell(0.5), "_ref_" + name))
    capture_currents = current_path is not None or humanjs_current_data is not None
    h.finitialize(-70.0)
    segment = cell(0.5)
    current_samples = None
    if capture_currents:
        h.fcurrent()
        current_samples = [
            [float(h.t), float(segment.ina), float(segment.ik), float(segment.i_pas)]
        ]
    for _ in range(sample_count):
        h.fadvance()
        if capture_currents:
            # Vector.record observes BREAKPOINT currents before the next current
            # refresh at this fixed-step boundary. Re-evaluate currents at the
            # committed endpoint so each row matches its voltage and gate state.
            h.fcurrent()
            current_samples.append(
                [float(h.t), float(segment.ina), float(segment.ik), float(segment.i_pas)]
            )

    times = np.asarray(time_vector, dtype=float)
    voltage = np.asarray(voltage_vector, dtype=float)
    gates = {name: np.asarray(vector, dtype=float) for name, vector in gate_vectors.items()}
    currents = {}
    if capture_currents:
        current_matrix = np.asarray(current_samples, dtype=float)
        if current_matrix.shape != (len(times), 4) or not np.allclose(
            current_matrix[:, 0], times, rtol=0.0, atol=1.0e-9
        ):
            raise reproduction.ReproductionError(
                "NEURON endpoint current samples must align exactly with voltage timestamps"
            )
        currents = {
            "ina": current_matrix[:, 1],
            "ik": current_matrix[:, 2],
            "i_pas": current_matrix[:, 3],
        }
    if len(times) < 2 or not np.isfinite(times).all() or np.any(np.diff(times) <= 0.0):
        raise reproduction.ReproductionError(
            "NEURON gate timestamps must be finite and strictly increasing"
        )
    for name, values in gates.items():
        if len(values) != len(times) or not np.isfinite(values).all() or np.any(
            (values < 0.0) | (values > 1.0)
        ):
            raise reproduction.ReproductionError(
                f"NEURON gate {name} must contain finite values in [0, 1] at every voltage sample"
            )
    if current_path is not None:
        if any(values.shape != times.shape or not np.isfinite(values).all()
               for values in currents.values()):
            raise reproduction.ReproductionError("NEURON membrane-current traces must be finite and match voltage timestamps")
        current_path.parent.mkdir(parents=True, exist_ok=True)
        np.savetxt(
            current_path,
            np.column_stack((times, currents["ina"], currents["ik"], currents["i_pas"])),
            delimiter=",",
            header="time_ms,ina_mA_per_cm2,ik_mA_per_cm2,i_pas_mA_per_cm2",
            comments="",
            fmt="%.12g",
        )
    result: dict[str, Any] = {
        "configuration": {
            "dt_ms": dt_ms,
            "secondorder": secondorder,
            "na_human_usetable": use_na_table,
        },
        "observed_output": summarize_trace(
            times, voltage, feature_extractor, trace_path
        ),
    }
    if gate_path is not None:
        save_source_gate_trace(gate_path, times, gates)
        result["gate_trace_file"] = str(gate_path)
    if current_path is not None:
        result["membrane_current_trace_file"] = str(current_path)

    if secondorder == 0 and na_ratio == 1.0 and k_ratio == 1.0:
        source_gate_matrix = np.column_stack(
            [gates[name] for name in SOURCE_GATE_NAMES]
        )
        replay_voltage, replay_gates = replay_wilbers_source_order(
            times,
            float(voltage[0]),
            source_gate_matrix[0],
            rheobase_pa * 1.5,
            gbar_na,
            gbar_k,
            _build_source_na_rate_table() if use_na_table == 1 else None,
        )
        result["source_order_replay"] = {
            "method": (
                "implicit endpoint voltage using G[n], followed by CNEXP gate advancement "
                "using V[n+1] and the selected Na rate mode"
            ),
            "voltage_vs_neuron": _numeric_metrics(replay_voltage, voltage),
            "voltage_vs_neuron_units": "mV",
            "gates_vs_neuron": _gate_path_metrics(replay_gates, source_gate_matrix),
            "voltage_vs_humanjs": (
                compare_traces(*load_trace(humanjs_path), times, replay_voltage)
                if humanjs_path is not None
                else None
            ),
            "interpretation_limit": (
                "This is an independently coded numerical replay of the source's observed "
                "secondorder=0 update ordering; it is not biological validation."
            ),
        }

    if humanjs_current_data is not None and humanjs_path is not None:
        humanjs_current_times, humanjs_current_stages, humanjs_endpoint = humanjs_current_data
        result["membrane_current_balance"] = compare_membrane_current_balance(
            times,
            voltage,
            gates,
            currents,
            *load_trace(humanjs_path),
            humanjs_current_times,
            humanjs_current_stages,
            humanjs_endpoint,
            rheobase_pa * 1.5,
            gbar_na,
            gbar_k,
        )
    result["gate_state_method"] = "Original NMODL state variables advanced by METHOD cnexp"
    result["same_voltage_gate_integrator_sensitivity"] = compare_gate_integrators_on_shared_voltage(
        times, voltage, gates, use_na_table
    )
    result["comparison_to_author_baseline"] = compare_traces(
        baseline_times, baseline_voltage, times, voltage
    )
    if humanjs_gates_path is not None:
        humanjs_gate_times, humanjs_gates = load_humanjs_gate_trace(humanjs_gates_path)
        result["comparison_to_humanjs_gates"] = compare_gate_traces(
            times, gates, humanjs_gate_times, humanjs_gates
        )
    if humanjs_path is not None and humanjs_gates_path is not None:
        humanjs_voltage_times, humanjs_voltage = load_trace(humanjs_path)
        result["gate_sampling_on_humanjs_voltage"] = compare_gate_sampling_on_humanjs_voltage(
            float(times[0]),
            float(voltage[0]),
            np.asarray([gates[name][0] for name in SOURCE_GATE_NAMES], dtype=float),
            humanjs_voltage_times,
            humanjs_voltage,
            humanjs_gate_times,
            humanjs_gates,
            use_na_table,
            *(
                load_humanjs_voltage_stage_trace(humanjs_voltage_stages_path)
                if humanjs_voltage_stages_path is not None
                else (None, None)
            ),
        )
    if humanjs_path is not None:
        result["comparison_to_humanjs"] = compare_with_humanjs(
            humanjs_path, times, voltage
        )
    del clamp
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gbar-na", type=float, default=114.47654963753565)
    parser.add_argument("--gbar-k", type=float, default=29.045736151752504)
    parser.add_argument("--na-ratio", type=float, default=1.0)
    parser.add_argument("--k-ratio", type=float, default=1.0)
    parser.add_argument(
        "--dt-ms",
        nargs="+",
        type=float,
        default=[0.02, 0.01, 0.005],
        help="Fixed NEURON steps to test; defaults to 0.02 0.01 0.005 ms",
    )
    parser.add_argument(
        "--secondorder",
        nargs="+",
        type=int,
        choices=(0, 1, 2),
        default=[0, 1],
        help="NEURON integration modes to test; 0 is the unchanged default",
    )
    parser.add_argument(
        "--na-table",
        nargs="+",
        type=int,
        choices=(0, 1),
        default=[1, 0],
        help="Human sodium usetable_na_human setting(s)",
    )
    parser.add_argument("--humanjs-trace", type=Path)
    parser.add_argument("--humanjs-gates", type=Path)
    parser.add_argument("--humanjs-voltage-stages", type=Path)
    parser.add_argument("--humanjs-current-stages", type=Path)
    parser.add_argument("--trace-dir", type=Path)
    parser.add_argument("--gate-dir", type=Path)
    parser.add_argument("--current-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    for name, value in (("gbar-na", args.gbar_na), ("gbar-k", args.gbar_k)):
        if not (20.0 <= value <= 150.0):
            parser.error(f"--{name} must remain within source optimizer bounds [20, 150]")
    for name, value in (("na-ratio", args.na_ratio), ("k-ratio", args.k_ratio)):
        if not (0.0 <= value <= 1.0):
            parser.error(f"--{name} must be within [0, 1]")
    return args


def run_diagnostics(args: argparse.Namespace) -> dict[str, Any]:
    if sys.version_info[:2] != (3, 10):
        raise reproduction.ReproductionError(
            f"This pinned source replay requires Python 3.10; found {platform.python_version()}"
        )

    original_cwd = Path.cwd()
    humanjs_path = args.humanjs_trace.expanduser().resolve() if args.humanjs_trace else None
    humanjs_gates_path = (
        args.humanjs_gates.expanduser().resolve() if args.humanjs_gates else None
    )
    humanjs_voltage_stages_path = (
        args.humanjs_voltage_stages.expanduser().resolve()
        if args.humanjs_voltage_stages
        else None
    )
    humanjs_current_stages_path = (
        args.humanjs_current_stages.expanduser().resolve()
        if args.humanjs_current_stages
        else None
    )
    if humanjs_current_stages_path is not None and humanjs_path is None:
        raise reproduction.ReproductionError(
            "--humanjs-current-stages requires --humanjs-trace"
        )
    if humanjs_current_stages_path is not None and (
        args.na_ratio != 1.0 or args.k_ratio != 1.0
    ):
        raise reproduction.ReproductionError(
            "--humanjs-current-stages currently requires the all-human kinetic endpoint (both ratios 1.0)"
        )
    if humanjs_voltage_stages_path is not None and (
        humanjs_path is None or humanjs_gates_path is None
    ):
        raise reproduction.ReproductionError(
            "--humanjs-voltage-stages requires both --humanjs-trace and --humanjs-gates"
        )
    trace_dir = args.trace_dir.expanduser().resolve() if args.trace_dir else None
    gate_dir = args.gate_dir.expanduser().resolve() if args.gate_dir else None
    current_dir = args.current_dir.expanduser().resolve() if args.current_dir else None
    humanjs_current_data = (
        load_humanjs_current_balance_trace(humanjs_current_stages_path)
        if humanjs_current_stages_path is not None
        else None
    )

    with tempfile.TemporaryDirectory(prefix="wilbers_solver_diagnostic_") as temp_name:
        workdir = Path(temp_name)
        inventory = reproduction.verify_and_write(workdir)
        build_log = reproduction.compile_mechanisms(workdir)
        os.chdir(workdir)
        sys.path.insert(0, str(workdir))
        try:
            import numpy as np
            import neuron
            from neuron import h

            if neuron.__version__ != "9.0.2":
                raise reproduction.ReproductionError(
                    f"Expected NEURON 9.0.2, found {neuron.__version__}"
                )
            # Some NEURON wheel/platform combinations preload mechanisms from
            # the working directory during import. Match the baseline runner's
            # guard to avoid registering the same NMODL suffixes twice.
            if not all(
                hasattr(h, mechanism)
                for mechanism in ("na_human", "na_mouse", "k_human", "k_mouse")
            ):
                library = workdir / "x86_64" / "libnrnmech.so"
                if not library.is_file():
                    raise reproduction.ReproductionError(
                        f"Compiled mechanism library not found: {library}"
                    )
                h.nrn_load_dll(str(library))
            h.load_file("stdrun.hoc")
            import cc_tools

            h.na_human_ratio_na_human = args.na_ratio
            h.k_human_ratio_k_human = args.k_ratio
            h.secondorder = 0
            h.usetable_na_human = 1
            cell = cc_tools.init_cell(
                params_range={},
                params_h={
                    "gbar_na_human": args.gbar_na,
                    "gbar_k_human": args.gbar_k,
                },
            )
            rheobase_pa = float(
                cc_tools.getrheo(cell, dur=3, print_output=False)
            )

            # Baseline intentionally calls the deposited run_1AP helper
            # unchanged, preserving its dt=0.02 ms and NEURON defaults.
            baseline_times, baseline_voltage = cc_tools.run_1AP(cell)
            baseline = {
                "configuration": {
                    "dt_ms": float(h.dt),
                    "secondorder": int(h.secondorder),
                    "na_human_usetable": int(h.usetable_na_human),
                    "gate_method": "NMODL cnexp",
                },
                "rheobase_pA": rheobase_pa,
                "observed_output": summarize_trace(
                    baseline_times, baseline_voltage, cc_tools.get_outcomes_full,
                    (trace_dir / "baseline-author-helper.csv") if trace_dir else None,
                ),
            }
            if humanjs_path is not None:
                baseline["comparison_to_humanjs"] = compare_with_humanjs(
                    humanjs_path, baseline_times, baseline_voltage
                )

            variants = []
            for secondorder in args.secondorder:
                for dt_ms in args.dt_ms:
                    for use_table in args.na_table:
                        name = (
                            f"dt-{dt_ms:g}-secondorder-{secondorder}"
                            f"-na-table-{use_table}.csv"
                        )
                        trace_path = trace_dir / name if trace_dir else None
                        gate_name = name.removesuffix(".csv") + "-gates.csv"
                        gate_path = gate_dir / gate_name if gate_dir else None
                        current_path = current_dir / (name.removesuffix('.csv') + '-currents.csv') if current_dir else None
                        variants.append(
                            run_variant(
                                h,
                                cell,
                                rheobase_pa,
                                dt_ms,
                                secondorder,
                                use_table,
                                cc_tools.get_outcomes_full,
                                trace_path,
                                gate_path,
                                current_path,
                                humanjs_path,
                                humanjs_gates_path,
                                humanjs_voltage_stages_path,
                                humanjs_current_data,
                                args.gbar_na,
                                args.gbar_k,
                                args.na_ratio,
                                args.k_ratio,
                                baseline_times,
                                baseline_voltage,
                            )
                        )

            result = {
                "experiment": "Wilbers et al. 2023 human L2/L3 AP1 NEURON solver sensitivity",
                "dataset": {
                    "doi": reproduction.DATASET_DOI,
                    "version": reproduction.DATASET_VERSION,
                    "license": "CC0-1.0",
                    "source_files": inventory,
                },
                "environment": {
                    "python": platform.python_version(),
                    "neuron": neuron.__version__,
                    "numpy": np.__version__,
                    "compiler": reproduction.compiler_description(),
                },
                "model_setup": {
                    "kinetic_ratios": {
                        "na_human": args.na_ratio,
                        "k_human": args.k_ratio,
                    },
                    "conductance_densities_pS_per_um2": {
                        "na_human": args.gbar_na,
                        "k_human": args.gbar_k,
                    },
                    "temperature_celsius": 34.0,
                    "initial_voltage_mV": -70.0,
                    "channel_voltage_shift_mV": -10.0,
                },
                "protocol": {
                    "helper": "cc_tools.getrheo followed by unchanged cc_tools.run_1AP baseline",
                    "rheobase_pA": rheobase_pa,
                    "ap1_current_pA": rheobase_pa * 1.5,
                    "pulse_delay_ms": 1.0,
                    "pulse_duration_ms": 3.0,
                    "recording_duration_ms": 29.0,
                },
                "baseline_author_helper": baseline,
                "gate_state_fields": {
                    "source_nmodl": list(SOURCE_GATE_NAMES),
                    "humanjs": list(HUMANJS_GATE_NAMES),
                    "source_integrator": "NMODL cnexp",
                    "humanjs_integrator": "coupled fixed-step RK4",
                },
                "diagnostic_variants": variants,
                "interpretation_limit": (
                    "Solver, Na lookup-table, and optional gate-state sensitivity only. "
                    "The diagnostic variants are not the authors' reported simulation settings, "
                    "do not tune biological parameters, and do not establish "
                    "biological validation."
                ),
                "build_warnings": [
                    line.strip()
                    for line in build_log.splitlines()
                    if "Notice:" in line or "Warning:" in line
                ],
            }
            return result
        finally:
            os.chdir(original_cwd)
            if str(workdir) in sys.path:
                sys.path.remove(str(workdir))


def main() -> int:
    args = parse_args()
    try:
        result = run_diagnostics(args)
    except reproduction.ReproductionError as exc:
        print(f"solver diagnostic error: {exc}", file=sys.stderr)
        return 2
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        destination = args.output.expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
