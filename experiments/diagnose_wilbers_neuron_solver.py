#!/usr/bin/env python3
"""Diagnose numerical solver contributions to the Wilbers human L2/L3 AP1 replay.

The original source mechanisms and author's rheobase procedure are preserved.
NEURON's integration order, fixed step, and human Na lookup-table switch are
varied; optional NMODL/HumanJS gate traces expose internal state differences.
This is a numerical sensitivity experiment, not a new fit.
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
    humanjs_path: Path | None,
    humanjs_gates_path: Path | None,
    baseline_times: Any,
    baseline_voltage: Any,
) -> dict[str, Any]:
    import numpy as np

    if dt_ms <= 0.0:
        raise reproduction.ReproductionError("dt-ms must be positive")
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
    h.finitialize(-70.0)
    for _ in range(sample_count):
        h.fadvance()

    times = np.asarray(time_vector, dtype=float)
    voltage = np.asarray(voltage_vector, dtype=float)
    gates = {name: np.asarray(vector, dtype=float) for name, vector in gate_vectors.items()}
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
    result["gate_state_method"] = "Original NMODL state variables advanced by METHOD cnexp"
    result["comparison_to_author_baseline"] = compare_traces(
        baseline_times, baseline_voltage, times, voltage
    )
    if humanjs_gates_path is not None:
        humanjs_gate_times, humanjs_gates = load_humanjs_gate_trace(humanjs_gates_path)
        result["comparison_to_humanjs_gates"] = compare_gate_traces(
            times, gates, humanjs_gate_times, humanjs_gates
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
    parser.add_argument("--trace-dir", type=Path)
    parser.add_argument("--gate-dir", type=Path)
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
    trace_dir = args.trace_dir.expanduser().resolve() if args.trace_dir else None
    gate_dir = args.gate_dir.expanduser().resolve() if args.gate_dir else None

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
                                humanjs_path,
                                humanjs_gates_path,
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
