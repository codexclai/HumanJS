#!/usr/bin/env python3
"""Reproduce the six Eyal et al. human L2/L3 Figure 7A soma/axon models.

This script consumes an independently downloaded and extracted canonical
ModelDB model 238347 archive. It does not download or modify third-party source.
It compiles only the ten NMODL mechanisms inserted by the six Figure 7A HOC
templates, in a temporary directory, then runs the published HOC/morphology/
stimulus setup and compares the first spike with the released current-clamp
repetitions.

Requirements tested: Python 3.10, NEURON 9.0.2, NumPy, nrnivmodl, and a C++
compiler. No HumanJS files are generated or altered by a normal run.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np

MODELDB_MODELS = (
    {
        "cell": "cell0603_03",
        "model": "cell0603_03_model_476",
        "morphology": "2013_03_06_cell03_789_H41_03.ASC",
        "current_nA": 0.70,
        "recorded_current_pA": 700,
    },
    {
        "cell": "cell0603_08",
        "model": "cell0603_08_model_602",
        "morphology": "2013_03_06_cell08_876_H41_05_Cell2.ASC",
        "current_nA": 0.70,
        "recorded_current_pA": 700,
    },
    {
        "cell": "cell0603_11",
        "model": "cell0603_11_model_937",
        "morphology": "2013_03_06_cell11_1125_H41_06.ASC",
        "current_nA": 0.70,
        "recorded_current_pA": 700,
    },
    {
        "cell": "cell1303_03",
        "model": "cell1303_03_model_448",
        "morphology": "2013_03_13_cell03_1204_H42_02.ASC",
        "current_nA": 0.55,
        "recorded_current_pA": 550,
    },
    {
        "cell": "cell1303_05",
        "model": "cell1303_05_model_643",
        "morphology": "2013_03_13_cell05_675_H42_04.ASC",
        "current_nA": 0.55,
        "recorded_current_pA": 550,
    },
    {
        "cell": "cell1303_06",
        "model": "cell1303_06_model_263",
        "morphology": "2013_03_13_cell06_945_H42_05.ASC",
        "current_nA": 0.60,
        "recorded_current_pA": 600,
    },
)

# Exact mechanisms inserted by ActiveModels/*.hoc insertChannel(). Ca_HVA.mod
# exists in the archive but is not inserted by these six spike-model templates.
ACTIVE_MECHANISMS = (
    "NaTg",
    "Nap_Et2",
    "K_Tst",
    "K_Pst",
    "SKv3_1",
    "SK_E2",
    "Ca",
    "Ca_LVAst",
    "Im",
    "CaDynamics_E2",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--modeldb-root",
        type=Path,
        required=True,
        help="Path to the extracted EyalEtAl2018 directory from ModelDB model 238347.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for a JSON result file. Defaults to stdout only.",
    )
    return parser.parse_args()


def require_model_tree(root: Path) -> tuple[Path, Path, Path]:
    root = root.expanduser().resolve()
    mechanisms = root / "ActiveMechanisms"
    models = root / "ActiveModels"
    morphologies = root / "Morphs"
    data = root / "Figure7" / "data"
    for path in (mechanisms, models, morphologies, data):
        if not path.is_dir():
            raise FileNotFoundError(
                f"Expected canonical ModelDB directory is missing: {path}"
            )
    for mechanism in ACTIVE_MECHANISMS:
        mod_file = mechanisms / f"{mechanism}.mod"
        if not mod_file.is_file():
            raise FileNotFoundError(f"Required original mechanism is missing: {mod_file}")
    return mechanisms, models, morphologies


def compile_original_mechanisms(mechanisms: Path) -> Path:
    compiler = shutil.which("nrnivmodl")
    if compiler is None:
        raise RuntimeError("nrnivmodl was not found; install NEURON with its compiler tools.")

    build_root = Path(tempfile.mkdtemp(prefix="humanjs-eyal-modeldb-"))
    mod_dir = build_root / "mod"
    mod_dir.mkdir()
    for name in ACTIVE_MECHANISMS:
        shutil.copy2(mechanisms / f"{name}.mod", mod_dir / f"{name}.mod")

    environment = os.environ.copy()
    environment["MAKEFLAGS"] = "-j1"
    command = [compiler, "mod"]
    result = subprocess.run(
        command,
        cwd=build_root,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        shutil.rmtree(build_root, ignore_errors=True)
        raise RuntimeError(
            "Canonical Eyal mechanism compilation failed.\n"
            f"Command: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    library = build_root / "x86_64" / "libnrnmech.so"
    if not library.is_file():
        shutil.rmtree(build_root, ignore_errors=True)
        raise RuntimeError(f"nrnivmodl succeeded but did not produce {library}")
    return library


def first_spike_metrics(time_ms: np.ndarray, voltage_mV: np.ndarray) -> dict[str, float] | None:
    """Extract the first spike with the same voltage baseline correction as Figure 7A.

    The first 0-mV crossing after 120 ms is an alignment marker, not a claimed
    biological spike-threshold measurement. Peak is the local maximum within
    2 ms of that crossing. Half-width is measured at half the excursion from
    the pre-stimulus median baseline to that local peak.
    """
    start = int(np.searchsorted(time_ms, 120.0))
    crossings = np.flatnonzero(voltage_mV[start:] >= 0.0)
    if not len(crossings):
        return None

    first_crossing = start + int(crossings[0])
    end = min(len(voltage_mV), int(np.searchsorted(time_ms, time_ms[first_crossing] + 2.0)))
    peak_index = first_crossing + int(np.argmax(voltage_mV[first_crossing:end]))
    baseline = float(np.median(voltage_mV[time_ms < 100.0]))
    peak = float(voltage_mV[peak_index])
    half_level = (baseline + peak) / 2.0

    left = peak_index
    while left > 0 and voltage_mV[left] >= half_level:
        left -= 1
    right = peak_index
    while right < len(voltage_mV) - 1 and voltage_mV[right] >= half_level:
        right += 1

    return {
        "baseline_mV": baseline,
        "first_0mV_crossing_ms": float(time_ms[first_crossing]),
        "peak_mV": peak,
        "peak_time_ms": float(time_ms[peak_index]),
        "half_width_ms": float(time_ms[right] - time_ms[left]),
    }


def recorded_summary(data_dir: Path, current_pA: int) -> dict[str, Any]:
    files = sorted(data_dir.glob(f"{current_pA}_*.txt"))
    if not files:
        raise FileNotFoundError(
            f"No released {current_pA} pA recordings found in {data_dir}"
        )

    samples: list[dict[str, float]] = []
    for path in files:
        values = np.loadtxt(path)
        if values.ndim != 2 or values.shape[1] < 2:
            raise ValueError(f"Expected two-column time/voltage data: {path}")
        # Figure7A.py subtracts a 16 mV liquid-junction potential.
        metrics = first_spike_metrics(values[:, 0], values[:, 1] - 16.0)
        if metrics is not None:
            samples.append(metrics)

    if not samples:
        raise RuntimeError(f"No first action potential found in recordings for {current_pA} pA")

    fields = (
        "first_0mV_crossing_ms",
        "peak_mV",
        "peak_time_ms",
        "half_width_ms",
    )
    summary: dict[str, Any] = {
        "repetitions_with_detected_spike": len(samples),
        "files_found": len(files),
    }
    for field in fields:
        values = [sample[field] for sample in samples]
        summary[field] = {
            "median": float(median(values)),
            "minimum": float(min(values)),
            "maximum": float(max(values)),
        }
    return summary


def run_models(root: Path, library: Path) -> dict[str, Any]:
    # Import after nrnivmodl has produced the shared library.
    import neuron
    from neuron import h

    if not h.nrn_load_dll(str(library)):
        raise RuntimeError(f"NEURON failed to load compiled mechanisms: {library}")

    if not h.load_file("stdrun.hoc"):
        raise RuntimeError("NEURON failed to load stdrun.hoc")
    if not h.load_file("import3d.hoc"):
        raise RuntimeError("NEURON failed to load import3d.hoc")

    h("objref HCell")
    h.steps_per_ms = 100
    h.dt = 1.0 / h.steps_per_ms
    h.tstop = 1500.0
    h.celsius = 37.0
    h.v_init = -86.0

    results: list[dict[str, Any]] = []
    for config in MODELDB_MODELS:
        cell_name = config["cell"]
        model_name = config["model"]
        model_hoc = root / "ActiveModels" / f"{model_name}.hoc"
        morphology = root / "Morphs" / config["morphology"]
        data_dir = root / "Figure7" / "data" / cell_name

        for path in (model_hoc, morphology, data_dir):
            if not path.exists():
                raise FileNotFoundError(f"Required Figure 7A input is missing: {path}")
        if not h.load_file(str(model_hoc)):
            raise RuntimeError(f"NEURON failed to load original HOC template: {model_hoc}")

        h(f"HCell = new {model_name}()")
        cell = h.HCell
        importer = h.Import3d_Neurolucida3()
        importer.quiet = 1
        importer.input(str(morphology))
        import_gui = h.Import3d_GUI(importer, 0)
        import_gui.instantiate(cell)

        # This follows the original Figure7A.py model construction sequence.
        cell.indexSections(import_gui)
        cell.geom_nsec()
        cell.geom_nseg()
        cell.delete_axon()
        cell.insertChannel()
        cell.init_biophys()
        cell.biophys()

        stimulus = h.IClamp(0.5, sec=cell.soma[0])
        stimulus.dur = 1000.0
        stimulus.delay = 120.33
        stimulus.amp = config["current_nA"]

        voltage = h.Vector()
        voltage.record(cell.soma[0](0.5)._ref_v)
        time = h.Vector()
        time.record(h._ref_t)

        cell.soma[0].push()
        h.init(h.v_init)
        h.run()

        simulated = first_spike_metrics(np.asarray(time), np.asarray(voltage))
        if simulated is None:
            raise RuntimeError(f"No model spike detected for {model_name}")
        recorded = recorded_summary(data_dir, config["recorded_current_pA"])

        results.append(
            {
                "cell": cell_name,
                "model": model_name,
                "stimulus_nA": config["current_nA"],
                "recorded_dataset_current_pA": config["recorded_current_pA"],
                "simulated_single_run": simulated,
                "recorded_repetitions": recorded,
                "model_sections": {
                    "all": int(cell.nSecAll),
                    "soma": int(cell.nSecSoma),
                    "apical": int(cell.nSecApical),
                    "basal": int(cell.nSecBasal),
                    "axon_stub_sections": int(cell.nSecAxonal),
                    "axon_stub_lengths_um": [float(section.L) for section in cell.axonal],
                },
            }
        )

        # Release the HOC cell before constructing the next model.
        h("HCell = nil")
        del cell, importer, import_gui, stimulus, voltage, time

    return {
        "experiment": "Eyal et al. 2018 Figure 7A human L2/L3 pyramidal cell spike reproduction",
        "neuron_version": neuron.__version__,
        "python_version": sys.version.split()[0],
        "temperature_C": 37.0,
        "dt_ms": 0.01,
        "initial_voltage_mV": -86.0,
        "stimulus_delay_ms": 120.33,
        "stimulus_duration_ms": 1000.0,
        "analysis": {
            "recording_junction_potential_subtracted_mV": 16.0,
            "first_spike_search_start_ms": 120.0,
            "first_spike_peak_window_ms": 2.0,
            "threshold_marker_mV": 0.0,
            "half_width_reference": "halfway from pre-stimulus median baseline to local first-spike peak",
            "warning": "The first 0-mV crossing is an alignment marker, not a measured biological spike threshold.",
        },
        "models": results,
    }


def main() -> int:
    args = parse_args()
    root = args.modeldb_root.expanduser().resolve()
    mechanisms, _, _ = require_model_tree(root)
    try:
        library = compile_original_mechanisms(mechanisms)
        result = run_models(root, library)
        rendered = json.dumps(result, indent=2, sort_keys=True)
        if args.output:
            destination = args.output.expanduser().resolve()
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(rendered + "\n", encoding="utf-8")
            print(f"Wrote reproduction results to {destination}")
        else:
            print(rendered)
        return 0
    finally:
        # nrniv_load_dll keeps the loaded library resident for this process;
        # the build workspace is removed once the process is complete.
        if "library" in locals():
            shutil.rmtree(library.parent.parent, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
