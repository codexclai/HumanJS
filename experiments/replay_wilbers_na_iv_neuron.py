#!/usr/bin/env python3
"""Execute the deposited Wilbers human Na_IV voltage-clamp fit path in NEURON.

The original channel_tools.py helpers and pure human na_human.mod mechanism are
downloaded unchanged, identity-checked, and executed with NEURON 9.0.2. This
tests the source NMODL gates and VClamp implementation, not raw recordings.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import math
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
NEURON_VERSION = "9.0.2"
SAMPLE_INTERVAL_MS = 0.01
HOLD_DURATION_MS = 2.0
TEST_DURATION_MS = 10.0
HOLD_VOLTAGE_MV = -120.0
TEST_VOLTAGES_MV = tuple(float(v) for v in range(-80, 11, 5))
FIT_MASK_START_MS = 2.02
FIT_MASK_END_MS = 12.0
SOURCE_MIN_INWARD_CURRENT_MA_CM2 = 1.0e-6
FIT_R2_THRESHOLD = 0.95

SOURCE_FILES = {
    "channel_tools.py": (
        326242, 35609, "615595a270c6170987757cd35743f5d5b5b2af0e",
    ),
    "mod/na_human.mod": (
        318629, 3602, "b199d70c3d0e7a2e991fd8d26c54b1318e3c0970",
    ),
    "fit_na_hh_cma_human.py": (
        326238, 3663, "3fac7eb5d25c2e02f6a3530d746de292548ef368",
    ),
}

FIELDNAMES = (
    "voltage_mv",
    "samples_fitted",
    "source_ina_min_ma_cm2",
    "source_current_density_gate_passed",
    "preliminary_tau_m_ms",
    "preliminary_tau_h_ms",
    "joint_tau_m_ms",
    "joint_tau_h_ms",
    "source_mapped_tau_m_ms",
    "source_mapped_tau_h_ms",
    "joint_r_squared",
    "passed_joint_fit_r2",
    "joint_tau_h_at_upper_bound",
)


class ReproductionError(RuntimeError):
    """A source, toolchain, or voltage-clamp reproduction step failed."""


def download_source(file_id: int, timeout: int = 60) -> bytes:
    request = urllib.request.Request(
        DATAFILE_URL.format(file_id),
        headers={"User-Agent": "HumanJS-Wilbers-Na-IV-source-replay/1.0"},
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
    for relative_path, (file_id, expected_size, expected_sha1) in SOURCE_FILES.items():
        raw = download_source(file_id)
        actual_sha1 = hashlib.sha1(raw).hexdigest()
        if len(raw) != expected_size or actual_sha1 != expected_sha1:
            raise ReproductionError(
                f"{relative_path}: source identity mismatch; expected "
                f"{expected_size} bytes / SHA-1 {expected_sha1}, got "
                f"{len(raw)} bytes / SHA-1 {actual_sha1}"
            )
        destination = workdir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        inventory[relative_path] = {
            "dataverse_file_id": file_id,
            "bytes": len(raw),
            "sha1": actual_sha1,
        }
    return inventory


def compile_mechanism(workdir: Path) -> str:
    compiler = shutil.which("nrnivmodl")
    if not compiler:
        raise ReproductionError("nrnivmodl is not on PATH; install NEURON 9.0.2")
    env = os.environ.copy()
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


def import_channel_tools(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("wilbers_channel_tools", path)
    if spec is None or spec.loader is None:
        raise ReproductionError(f"Cannot load source helper at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_protocol() -> dict[str, Any]:
    if sys.version_info < (3, 10):
        raise ReproductionError(
            f"Python 3.10 or newer is required; found {platform.python_version()}"
        )

    original_cwd = Path.cwd()
    original_path = list(sys.path)
    try:
        with tempfile.TemporaryDirectory(prefix="wilbers_na_iv_neuron_") as temp_name:
            workdir = Path(temp_name)
            inventory = verify_and_write(workdir)
            build_log = compile_mechanism(workdir)

            os.chdir(workdir)
            sys.path.insert(0, str(workdir))
            import matplotlib
            matplotlib.use("Agg")
            import numpy as np
            import neuron
            from neuron import h

            if neuron.__version__ != NEURON_VERSION:
                raise ReproductionError(
                    f"Expected NEURON {NEURON_VERSION}, found {neuron.__version__}"
                )

            # NEURON may auto-load a mechanism library from the working
            # directory during import. This replay compiles only na_human.mod;
            # avoid loading it a second time when the suffix is already present.
            if not hasattr(h, "na_human"):
                library = workdir / "x86_64" / "libnrnmech.so"
                if not library.is_file():
                    raise ReproductionError(f"Compiled mechanism library not found: {library}")
                h.nrn_load_dll(str(library))
            h.load_file("stdrun.hoc")
            channel_tools = import_channel_tools(workdir / "channel_tools.py")

            caller_text = (workdir / "fit_na_hh_cma_human.py").read_text(encoding="utf-8")
            required_setup = (
                "cell.diam=10",
                "cell.insert(mechname)",
                "cell.Ra=200",
                "cell.cm=1",
                "cell.ena=141",
                "ax = Na_IV(cell)",
            )
            for source_line in required_setup:
                if source_line not in caller_text:
                    raise ReproductionError(
                        f"Verified human Na fitting caller no longer contains {source_line!r}"
                    )

            # Reproduce fit_na_hh_cma_human.py's pure-human Na_IV cell setup.
            cell = h.Section(name="cell[0]")
            cell.diam = 10.0
            cell.insert("na_human")
            cell.Ra = 200.0
            cell.cm = 1.0
            cell.ena = 141.0

            segment = cell(0.5)
            default_gbar = float(segment.gbar_na_human)
            voltage_shift = float(segment.vshift_na_human)
            if not math.isclose(default_gbar, 40.0, rel_tol=0.0, abs_tol=1.0e-12):
                raise ReproductionError(f"Unexpected deposited Na gbar default: {default_gbar}")
            if not math.isclose(voltage_shift, 0.0, rel_tol=0.0, abs_tol=1.0e-12):
                raise ReproductionError(
                    f"Unexpected pure Na voltage shift: {voltage_shift}"
                )

            h.celsius = 25.0
            h.dt = SAMPLE_INTERVAL_MS
            secondorder = float(h.secondorder)
            if secondorder != 0.0:
                raise ReproductionError(
                    f"Expected NEURON's unmodified secondorder=0 default, found {secondorder}"
                )

            # These are the built-in NEURON VClamp defaults; runIna does not
            # override them. A temporary probe is discarded before the replay.
            probe = h.VClamp(cell(0.5))
            vclamp = {
                "gain": float(probe.gain),
                "rstim_mohm": float(probe.rstim),
                "tau1_ms": float(probe.tau1),
                "tau2_ms": float(probe.tau2),
                "fac": float(probe.fac),
            }
            del probe
            expected_vclamp = {
                "gain": 1.0e5,
                "rstim_mohm": 1.0,
                "tau1_ms": 0.001,
                "tau2_ms": 0.0,
                "fac": 0.0,
            }
            for name, expected in expected_vclamp.items():
                if not math.isclose(vclamp[name], expected, rel_tol=0.0, abs_tol=1.0e-12):
                    raise ReproductionError(
                        f"Unexpected NEURON VClamp default {name}: {vclamp[name]}"
                    )

            time_vector = h.Vector()
            time_vector.record(h._ref_t)
            rows: list[dict[str, Any]] = []
            for voltage in TEST_VOLTAGES_MV:
                durs = [HOLD_DURATION_MS, TEST_DURATION_MS]
                amps = [HOLD_VOLTAGE_MV, voltage]
                current = np.asarray(
                    channel_tools.runIna(cell, durs, amps), dtype=float
                )
                times = np.asarray(time_vector, dtype=float)
                if (
                    current.ndim != 1
                    or times.shape != current.shape
                    or len(times) != 1201
                    or not np.isfinite(times).all()
                    or not np.isfinite(current).all()
                    or np.any(np.diff(times) <= 0.0)
                ):
                    raise ReproductionError(
                        f"NEURON returned invalid voltage-clamp samples at {voltage:g} mV"
                    )
                if (
                    abs(float(times[0])) > 1.0e-12
                    or abs(float(times[-1]) - 12.0) > 1.0e-9
                    or not np.allclose(np.diff(times), SAMPLE_INTERVAL_MS, atol=1.0e-12, rtol=0.0)
                ):
                    raise ReproductionError(
                        f"NEURON time grid differs from the 0.01-ms source protocol at {voltage:g} mV"
                    )

                mask = (times > FIT_MASK_START_MS) & (times < FIT_MASK_END_MS)
                if int(np.count_nonzero(mask)) != 997:
                    raise ReproductionError(
                        f"Unexpected source fit sample count at {voltage:g} mV"
                    )
                x = times[mask]
                y = -current[mask]
                source_ina_min = float(np.min(current[mask]))
                density_gate = source_ina_min < -SOURCE_MIN_INWARD_CURRENT_MA_CM2
                base: dict[str, Any] = {
                    "voltage_mv": voltage,
                    "samples_fitted": int(np.count_nonzero(mask)),
                    "source_ina_min_ma_cm2": source_ina_min,
                    "source_current_density_gate_passed": density_gate,
                }
                if not density_gate:
                    rows.append(
                        {
                            **base,
                            "preliminary_tau_m_ms": math.nan,
                            "preliminary_tau_h_ms": math.nan,
                            "joint_tau_m_ms": math.nan,
                            "joint_tau_h_ms": math.nan,
                            "source_mapped_tau_m_ms": math.nan,
                            "source_mapped_tau_h_ms": math.nan,
                            "joint_r_squared": math.nan,
                            "passed_joint_fit_r2": False,
                            "joint_tau_h_at_upper_bound": False,
                            "fit_error": "source current-density selection gate not met",
                        }
                    )
                    continue

                try:
                    peak = int(np.argmax(y))
                    estimate_activation = float(
                        channel_tools.get_tau_act(x[:peak], y[:peak], est=0.1)
                    )
                    estimate_inactivation = float(
                        channel_tools.get_tau_inact(x[peak:-1], y[peak:-1], est=2.0)
                    )
                    parameters, r_squared = channel_tools.fit_na_curr(
                        x, y, estimate_activation, estimate_inactivation
                    )
                    r_squared = float(r_squared)
                    accepted = r_squared > FIT_R2_THRESHOLD
                    rows.append(
                        {
                            **base,
                            "preliminary_tau_m_ms": estimate_activation,
                            "preliminary_tau_h_ms": estimate_inactivation,
                            "joint_tau_m_ms": float(parameters[0]),
                            "joint_tau_h_ms": float(parameters[1]),
                            "source_mapped_tau_m_ms": (
                                float(parameters[0]) if accepted else math.nan
                            ),
                            "source_mapped_tau_h_ms": (
                                estimate_inactivation if accepted else math.nan
                            ),
                            "joint_r_squared": r_squared,
                            "passed_joint_fit_r2": accepted,
                            "joint_tau_h_at_upper_bound": (
                                abs(float(parameters[1]) - 2.0 * estimate_inactivation)
                                <= 1.0e-6 * max(1.0, abs(float(parameters[1])))
                            ),
                        }
                    )
                except Exception as exc:
                    rows.append(
                        {
                            **base,
                            "preliminary_tau_m_ms": math.nan,
                            "preliminary_tau_h_ms": math.nan,
                            "joint_tau_m_ms": math.nan,
                            "joint_tau_h_ms": math.nan,
                            "source_mapped_tau_m_ms": math.nan,
                            "source_mapped_tau_h_ms": math.nan,
                            "joint_r_squared": math.nan,
                            "passed_joint_fit_r2": False,
                            "joint_tau_h_at_upper_bound": False,
                            "fit_error": f"{type(exc).__name__}: {exc}",
                        }
                    )

            if len(rows) != len(TEST_VOLTAGES_MV):
                raise ReproductionError("Did not produce all 19 Na_IV voltage rows")
            return {
                "environment": {
                    "python": platform.python_version(),
                    "neuron": neuron.__version__,
                    "numpy": np.__version__,
                    "scipy": __import__("scipy").__version__,
                    "secondorder": secondorder,
                    "temperature_celsius": float(h.celsius),
                    "dt_ms": float(h.dt),
                    "cell_diameter_um": float(cell.diam),
                    "cell_length_um": float(cell.L),
                    "cell_axial_resistance_ohm_cm": float(cell.Ra),
                    "cell_capacitance_uF_cm2": float(cell.cm),
                    "na_reversal_mV": float(cell.ena),
                    "na_default_gbar_pS_um2": default_gbar,
                    "na_voltage_shift_mV": voltage_shift,
                    "vclamp": vclamp,
                },
                "source_files": inventory,
                "compiler": shutil.which("g++") or "unavailable",
                "compile_log_tail": (build_log[-3000:] if build_log else ""),
                "rows": rows,
            }
    finally:
        os.chdir(original_cwd)
        sys.path[:] = original_path


def csv_text(result: dict[str, Any]) -> str:
    env = result["environment"]
    clamp = env["vclamp"]
    source = result["source_files"]
    lines = [
        "# Executed original Wilbers Na_IV gate/current-fit path with NEURON 9.0.2 and built-in VClamp.",
        f"# Dataset: DataverseNL DOI {DATASET_DOI}, version {DATASET_VERSION}, CC0-1.0.",
        f"# channel_tools.py SHA-1 {source['channel_tools.py']['sha1']}.",
        f"# na_human.mod SHA-1 {source['mod/na_human.mod']['sha1']}.",
        f"# fit_na_hh_cma_human.py SHA-1 {source['fit_na_hh_cma_human.py']['sha1']}.",
        f"# Environment: Python {env['python']}; NEURON {env['neuron']}; NumPy {env['numpy']}; SciPy {env['scipy']}; compiler {result['compiler']}.",
        f"# Source cell: diameter {env['cell_diameter_um']:g} um; length {env['cell_length_um']:g} um (NEURON default); Ra={env['cell_axial_resistance_ohm_cm']:g}; cm={env['cell_capacitance_uF_cm2']:g}; ena={env['na_reversal_mV']:g} mV; default gbar={env['na_default_gbar_pS_um2']:g} pS/um2; vshift={env['na_voltage_shift_mV']:g} mV.",
        f"# Protocol: {env['temperature_celsius']:g} C; dt={env['dt_ms']:g} ms; secondorder={env['secondorder']}; hold -120 mV for 2 ms; 19 test steps -80..+10 mV for 10 ms.",
        f"# Built-in VClamp defaults (not changed by runIna): gain={clamp['gain']:g}; rstim={clamp['rstim_mohm']:g} MOhm; tau1={clamp['tau1_ms']:g} ms; tau2={clamp['tau2_ms']:g} ms; fac={clamp['fac']:g}.",
        "# Source fits use current density ina (mA/cm2), the exact (t>2.02)&(t<12) 997-sample mask, original preliminary exponential helpers and joint composite-fit helper.",
        "# Source output mapping: joint fit parameter 0 is tau_m; tau_h remains the preliminary post-peak decay estimate; no raw human NWB traces are involved.",
        "# This is original NMODL/VClamp model execution, not experimental-current refitting or biological validation.",
        ",".join(FIELDNAMES),
    ]
    import io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDNAMES, extrasaction="ignore", lineterminator="\n")
    for row in result["rows"]:
        writer.writerow(
            {
                key: (
                    "" if isinstance(value, float) and not math.isfinite(value)
                    else value
                )
                for key, value in row.items()
            }
        )
    lines.append(output.getvalue().rstrip("\n"))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="Optional output CSV path")
    args = parser.parse_args()
    result = run_protocol()
    content = csv_text(result)
    if args.output:
        args.output.expanduser().resolve().write_text(content, encoding="utf-8")
    print(content, end="")
    passed = sum(bool(row["passed_joint_fit_r2"]) for row in result["rows"])
    density_gate = sum(bool(row["source_current_density_gate_passed"]) for row in result["rows"])
    print(
        f"# NEURON VClamp replay: {density_gate}/19 pass current-density selection; "
        f"{passed}/19 pass joint-fit R² > {FIT_R2_THRESHOLD:.2f}.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReproductionError as error:
        print(f"REPRODUCTION ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
