#!/usr/bin/env python3
"""Run the released Wilbers et al. human L2/L3 current-clamp AP1 protocol.

Requires Python 3.10, NEURON 9.0.2, NumPy 1.26.4, SciPy 1.11.4,
pandas 2.1.4, matplotlib 3.8.4, and seaborn 0.13.2.

The runner retrieves the original CC0 Dataverse v3.0 helper and NMODL source,
verifies each download by size and SHA-1, compiles the mechanisms unchanged,
and calls the authors' original NEURON helper. Temporary source and build
files live only in a TemporaryDirectory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

DATAFILE_URL = "https://dataverse.nl/api/access/datafile/{}"
DATASET_DOI = "10.34894/L5J0SD"
DATASET_VERSION = "3.0"

SOURCE_FILES = {
    "cc_tools.py": (318557, 10448, "f64162577fa5dd86892b46570d597e58e083a02b", "Figures5_6/Current_clamp"),
    "mod/na_human.mod": (318563, 3711, "ef158980e4bb427c97cfb8f379cd63006130b3b2", "Figures5_6/Current_clamp/mod"),
    "mod/na_mouse.mod": (318561, 3726, "84cc161f3c38fc71d399cc998d91f0c60cbd2df1", "Figures5_6/Current_clamp/mod"),
    "mod/k_human.mod": (318566, 4326, "622f7c9867e727a3dc7dea1f9ba2efbfb94cfd3a", "Figures5_6/Current_clamp/mod"),
    "mod/k_mouse.mod": (318560, 4303, "8b1761352a44cc57c29f3345242a4060186d84eb", "Figures5_6/Current_clamp/mod"),
}


class ReproductionError(RuntimeError):
    """A source, toolchain, or protocol reproduction step failed."""


def download_source(file_id: int, timeout: int = 60) -> bytes:
    request = urllib.request.Request(
        DATAFILE_URL.format(file_id),
        headers={"User-Agent": "HumanJS-Wilbers-current-clamp-reproduction/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise ReproductionError(
                    f"Dataverse file {file_id}: unexpected HTTP status {response.status}"
                )
            return response.read()
    except Exception as exc:
        raise ReproductionError(
            f"Unable to download Dataverse file {file_id}: {exc}"
        ) from exc


def verify_and_write(workdir: Path) -> dict[str, dict[str, Any]]:
    inventory: dict[str, dict[str, Any]] = {}
    for relative_path, (file_id, expected_size, expected_sha1, directory) in SOURCE_FILES.items():
        raw = download_source(file_id)
        actual_sha1 = hashlib.sha1(raw).hexdigest()
        if len(raw) != expected_size or actual_sha1 != expected_sha1:
            raise ReproductionError(
                f"{relative_path}: source identity mismatch; "
                f"expected {expected_size} bytes / SHA-1 {expected_sha1}, "
                f"got {len(raw)} bytes / SHA-1 {actual_sha1}"
            )
        destination = workdir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        inventory[relative_path] = {
            "dataverse_file_id": file_id,
            "directory": directory,
            "bytes": len(raw),
            "sha1": actual_sha1,
        }
    return inventory


def compiler_description() -> str:
    compiler = shutil.which(os.environ.get("CXX", "g++"))
    if not compiler:
        return "unavailable"
    result = subprocess.run(
        [compiler, "--version"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    return (
        (result.stdout or result.stderr).splitlines()[0]
        if result.returncode == 0
        else "unknown"
    )


def compile_mechanisms(workdir: Path) -> str:
    compiler = shutil.which("nrnivmodl")
    if not compiler:
        raise ReproductionError(
            "nrnivmodl is not on PATH; install NEURON 9.0.2 before running this experiment"
        )
    env = os.environ.copy()
    # Avoid four concurrent C++ compiler jobs on memory-constrained machines.
    env["MAKEFLAGS"] = "-j1"
    env.setdefault("MPLBACKEND", "Agg")
    try:
        result = subprocess.run(
            [compiler, "mod"],
            cwd=workdir,
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
    except subprocess.TimeoutExpired as exc:
        raise ReproductionError("nrnivmodl timed out after 180 seconds") from exc
    if result.returncode != 0:
        detail = (result.stdout + "\n" + result.stderr)[-12000:]
        raise ReproductionError(
            f"nrnivmodl failed with exit code {result.returncode}:\n{detail}"
        )
    return result.stdout + result.stderr


def as_float_list(values: Any) -> list[float]:
    return [float(value) for value in values]


def run_protocol(args: argparse.Namespace) -> dict[str, Any]:
    if sys.version_info[:2] != (3, 10):
        raise ReproductionError(
            f"This pinned source reproduction requires Python 3.10; "
            f"found {platform.python_version()}"
        )

    original_cwd = Path.cwd()
    output_path = Path(args.output).expanduser().resolve() if args.output else None
    trace_path = (
        Path(args.trace_output).expanduser().resolve()
        if args.trace_output
        else None
    )

    with tempfile.TemporaryDirectory(prefix="wilbers_cc_neuron_") as temp_name:
        workdir = Path(temp_name)
        inventory = verify_and_write(workdir)
        build_log = compile_mechanisms(workdir)

        # NEURON discovers the compiled mechanism library from the working
        # directory. Some wheel/platform combinations require explicit loading.
        os.chdir(workdir)
        sys.path.insert(0, str(workdir))
        try:
            import numpy as np
            import neuron
            from neuron import h

            if neuron.__version__ != "9.0.2":
                raise ReproductionError(
                    f"Expected NEURON 9.0.2, found {neuron.__version__}"
                )

            if not all(
                hasattr(h, mechanism)
                for mechanism in ("na_human", "na_mouse", "k_human", "k_mouse")
            ):
                library = workdir / "x86_64" / "libnrnmech.so"
                if not library.is_file():
                    raise ReproductionError(
                        f"Compiled mechanism library not found: {library}"
                    )
                h.nrn_load_dll(str(library))

            h.load_file("stdrun.hoc")
            import cc_tools

            # These ratios select human channel kinetics in both mechanisms.
            h.na_human_ratio_na_human = args.na_ratio
            h.k_human_ratio_k_human = args.k_ratio
            cell = cc_tools.init_cell(
                params_range={},
                params_h={
                    "gbar_na_human": args.gbar_na,
                    "gbar_k_human": args.gbar_k,
                },
            )

            # Preserve the source helper's initial 0.1-nA rheobase trial and
            # coarse-to-fine current increments by calling it unchanged.
            rheobase_pa = float(cc_tools.getrheo(cell, dur=3, print_output=False))
            times_ms, voltage_mv = cc_tools.run_1AP(cell)
            features = cc_tools.get_outcomes_full(times_ms, voltage_mv)

            if len(features["amp"]) != 1:
                raise ReproductionError(
                    "Expected exactly one AP in the author's outcome extractor; "
                    f"found {len(features['amp'])}"
                )

            if trace_path is not None:
                trace_path.parent.mkdir(parents=True, exist_ok=True)
                np.savetxt(
                    trace_path,
                    np.column_stack((times_ms, voltage_mv)),
                    delimiter=",",
                    header="time_ms,voltage_mv",
                    comments="",
                    fmt="%.12g",
                )

            return {
                "experiment": "Wilbers et al. 2023 human L2/L3 current-clamp AP1 source replay",
                "dataset": {
                    "doi": DATASET_DOI,
                    "version": DATASET_VERSION,
                    "license": "CC0-1.0",
                    "source_files": inventory,
                },
                "environment": {
                    "python": platform.python_version(),
                    "neuron": neuron.__version__,
                    "numpy": np.__version__,
                    "scipy": __import__("scipy").__version__,
                    "compiler": compiler_description(),
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
                    "reversal_potentials_mV": {
                        "na": 68.0,
                        "k": -86.0,
                        "leak": -70.0,
                    },
                    "section_geometry_um": {
                        "length": 10.0,
                        "diameter": 10.0,
                        "nseg": 1,
                    },
                    "specific_capacitance_uF_per_cm2": 1.0,
                    "leak_resistance_ohm_cm2": 10000.0,
                },
                "protocol": {
                    "rheobase": {
                        "helper": "cc_tools.getrheo",
                        "duration_ms": 3.0,
                        "delay_ms": 2.0,
                        "initial_current_nA": 0.1,
                        "increments_nA": [0.1, 0.01, 0.001],
                        "apcount_threshold_mV": -20.0,
                        "dt_ms": 0.1,
                    },
                    "ap1": {
                        "helper": "cc_tools.run_1AP",
                        "pulse_amplitude_factor": 1.5,
                        "pulse_amplitude_pA": rheobase_pa * 1.5,
                        "pulse_delay_ms": 1.0,
                        "pulse_duration_ms": 3.0,
                        "dt_ms": 0.02,
                        "total_duration_ms": 29.0,
                    },
                },
                "observed_output": {
                    "rheobase_pA": rheobase_pa,
                    "samples": int(len(times_ms)),
                    "time_start_ms": float(times_ms[0]),
                    "time_end_ms": float(times_ms[-1]),
                    "sample_interval_ms": float(times_ms[1] - times_ms[0]),
                    "peak_voltage_mV": float(np.max(voltage_mv)),
                    "minimum_voltage_mV": float(np.min(voltage_mv)),
                    "features": {
                        key: as_float_list(value)
                        for key, value in features.items()
                    },
                    "trace_file": str(trace_path) if trace_path else None,
                },
                "scope": (
                    "Original released NMODL source and helper execution. "
                    "Model-side reference only; not raw experimental data "
                    "or biological validation."
                ),
                "build_warnings": [
                    line.strip()
                    for line in build_log.splitlines()
                    if "Notice:" in line or "Warning:" in line
                ],
            }
        finally:
            os.chdir(original_cwd)
            if str(workdir) in sys.path:
                sys.path.remove(str(workdir))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gbar-na", type=float, default=114.47654963753565)
    parser.add_argument("--gbar-k", type=float, default=29.045736151752504)
    parser.add_argument("--na-ratio", type=float, default=1.0)
    parser.add_argument("--k-ratio", type=float, default=1.0)
    parser.add_argument(
        "--output",
        help="Optional JSON output path; defaults to standard output",
    )
    parser.add_argument(
        "--trace-output",
        help="Optional CSV path for the NEURON model-side voltage trace",
    )
    args = parser.parse_args()
    for name, value in (
        ("gbar-na", args.gbar_na),
        ("gbar-k", args.gbar_k),
    ):
        if not (20.0 <= value <= 150.0):
            parser.error(
                f"--{name} must remain within source optimizer bounds [20, 150]"
            )
    for name, value in (
        ("na-ratio", args.na_ratio),
        ("k-ratio", args.k_ratio),
    ):
        if not (0.0 <= value <= 1.0):
            parser.error(f"--{name} must be within [0, 1]")
    return args


def main() -> int:
    args = parse_args()
    try:
        result = run_protocol(args)
    except ReproductionError as exc:
        print(f"reproduction error: {exc}", file=sys.stderr)
        return 2
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())