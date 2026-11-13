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

INACTIVATION_SAMPLE_INTERVAL_MS = 0.005
INACTIVATION_INITIAL_VOLTAGE_MV = -70.0
INACTIVATION_TEST_VOLTAGE_MV = -10.0
INACTIVATION_CONDITIONING_VOLTAGES_MV = tuple(
    float(v) for v in range(-105, -45, 2)
)
INACTIVATION_TEST_WINDOW_START_MS = 51.0
INACTIVATION_TEST_WINDOW_END_MS = 55.0
RECOVERY_SAMPLE_INTERVAL_MS = 0.02
RECOVERY_VOLTAGES_MV = tuple(float(v) for v in range(-90, -65, 2))
RECOVERY_INTERVALS_MS = tuple(float(v * v) for v in range(1, 13))
RECOVERY_FIRST_TEST_VOLTAGE_MV = 0.0
RECOVERY_SECOND_TEST_VOLTAGE_MV = 0.0
INACTIVATION_FIELDNAMES = (
    "conditioning_voltage_mv",
    "samples_fitted",
    "test_window_first_sample_ms",
    "test_window_last_sample_ms",
    "test_current_min_ma_cm2",
    "test_current_max_ma_cm2",
    "source_denominator",
    "source_ggmax_value",
    "normalized_ggmax",
    "boltzmann_vhalf_mv",
    "boltzmann_slope_mv",
)
RECOVERY_FIELDNAMES = (
    "recovery_voltage_mv",
    "recovery_interval_ms",
    "samples_fitted",
    "test_window_first_sample_ms",
    "test_window_last_sample_ms",
    "second_test_current_peak_magnitude_ma_cm2",
    "apparent_recovery_tau_ms",
    "source_returned_finite_tau",
)

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


def replay_na_iv_inactivation(
    channel_tools: Any, cell: Any, time_vector: Any, h: Any, np: Any
) -> dict[str, Any]:
    """Replay channel_tools.Na_IV_inact without plotting or changing its math."""
    h.celsius = 25.0
    h.dt = INACTIVATION_SAMPLE_INTERVAL_MS
    durations = [1.0, 50.0, 10.0]
    amplitudes = [
        INACTIVATION_INITIAL_VOLTAGE_MV,
        INACTIVATION_CONDITIONING_VOLTAGES_MV[0],
        INACTIVATION_TEST_VOLTAGE_MV,
    ]
    ggmax = np.empty(len(INACTIVATION_CONDITIONING_VOLTAGES_MV), dtype=float)
    provisional_rows: list[dict[str, Any]] = []
    for index, voltage in enumerate(INACTIVATION_CONDITIONING_VOLTAGES_MV):
        amplitudes[1] = voltage
        current = np.asarray(channel_tools.runIna(cell, durations, amplitudes), dtype=float)
        times = np.asarray(time_vector, dtype=float)
        if (
            current.ndim != 1
            or times.shape != current.shape
            or len(times) != round(61.0 / INACTIVATION_SAMPLE_INTERVAL_MS) + 1
            or not np.isfinite(times).all()
            or not np.isfinite(current).all()
            or np.any(np.diff(times) <= 0.0)
        ):
            raise ReproductionError(
                f"NEURON returned invalid Na_IV_inact samples at {voltage:g} mV"
            )
        if (
            abs(float(times[0])) > 1.0e-12
            or abs(float(times[-1]) - 61.0) > 1.0e-9
            or not np.allclose(
                np.diff(times),
                INACTIVATION_SAMPLE_INTERVAL_MS,
                atol=1.0e-12,
                rtol=0.0,
            )
        ):
            raise ReproductionError(
                f"Na_IV_inact time grid differs from source 0.005-ms protocol at {voltage:g} mV"
            )

        mask = (
            (times > INACTIVATION_TEST_WINDOW_START_MS)
            & (times < INACTIVATION_TEST_WINDOW_END_MS)
        )
        sample_count = int(np.count_nonzero(mask))
        if sample_count not in (799, 800, 801):
            raise ReproductionError(
                f"Unexpected Na_IV_inact sample count {sample_count} at {voltage:g} mV"
            )
        # Preserve the deposited helper's literal denominator, including +1e10.
        # It is a source-code convention and is not silently replaced by a
        # physically dimensional conductance calculation.
        source_denominator = (
            float(amplitudes[1]) - float(cell.ena) + 1.0e10
        )
        source_g = -current[mask] / source_denominator
        source_ggmax = float(np.max(source_g))
        ggmax[index] = source_ggmax
        provisional_rows.append(
            {
                "conditioning_voltage_mv": voltage,
                "samples_fitted": sample_count,
                "test_window_first_sample_ms": float(times[mask][0]),
                "test_window_last_sample_ms": float(times[mask][-1]),
                "test_current_min_ma_cm2": float(np.min(current[mask])),
                "test_current_max_ma_cm2": float(np.max(current[mask])),
                "source_denominator": source_denominator,
                "source_ggmax_value": source_ggmax,
            }
        )

    if not np.isfinite(ggmax).all() or float(np.max(ggmax)) <= 0.0:
        raise ReproductionError("Na_IV_inact produced an invalid peak-availability curve")
    normalized = ggmax / float(np.max(ggmax))
    vhalf, slope = channel_tools.fit_boltz_inact(
        np.asarray(INACTIVATION_CONDITIONING_VOLTAGES_MV, dtype=float),
        normalized.copy(),
    )
    rows = [
        {
            **row,
            "normalized_ggmax": float(normalized[index]),
            "boltzmann_vhalf_mv": float(vhalf),
            "boltzmann_slope_mv": float(slope),
        }
        for index, row in enumerate(provisional_rows)
    ]
    return {
        "rows": rows,
        "boltzmann_vhalf_mv": float(vhalf),
        "boltzmann_slope_mv": float(slope),
    }


def replay_na_inactivation_recovery(
    channel_tools: Any, cell: Any, time_vector: Any, h: Any, np: Any
) -> dict[str, Any]:
    """Replay channel_tools.Na_recovery's paired-pulse protocol and tau fit."""
    h.celsius = 25.0
    h.dt = RECOVERY_SAMPLE_INTERVAL_MS
    recovery_times = np.asarray(RECOVERY_INTERVALS_MS, dtype=float)
    rows: list[dict[str, Any]] = []
    for voltage in RECOVERY_VOLTAGES_MV:
        pulse2 = np.empty(len(RECOVERY_INTERVALS_MS), dtype=float)
        row_indices: list[int] = []
        for index, recovery_time in enumerate(RECOVERY_INTERVALS_MS):
            durations = [2.0, 10.0, recovery_time, 2.0]
            amplitudes = [
                HOLD_VOLTAGE_MV,
                RECOVERY_FIRST_TEST_VOLTAGE_MV,
                voltage,
                RECOVERY_SECOND_TEST_VOLTAGE_MV,
            ]
            total_duration = sum(durations)
            current = np.asarray(
                channel_tools.runIna(cell, durations, amplitudes), dtype=float
            )
            times = np.asarray(time_vector, dtype=float)
            expected_count = round(total_duration / RECOVERY_SAMPLE_INTERVAL_MS) + 1
            if (
                current.ndim != 1
                or times.shape != current.shape
                or len(times) != expected_count
                or not np.isfinite(times).all()
                or not np.isfinite(current).all()
                or np.any(np.diff(times) <= 0.0)
            ):
                raise ReproductionError(
                    f"NEURON returned invalid Na_recovery samples at {voltage:g} mV / {recovery_time:g} ms"
                )
            if (
                abs(float(times[0])) > 1.0e-12
                or abs(float(times[-1]) - total_duration) > 1.0e-9
                or not np.allclose(
                    np.diff(times),
                    RECOVERY_SAMPLE_INTERVAL_MS,
                    atol=1.0e-12,
                    rtol=0.0,
                )
            ):
                raise ReproductionError(
                    f"Na_recovery time grid differs from source 0.02-ms protocol at {voltage:g} mV"
                )

            window_start = 12.0 + recovery_time
            window_end = window_start + 2.0
            mask = (times > window_start) & (times < window_end)
            sample_count = int(np.count_nonzero(mask))
            if sample_count not in (99, 100, 101):
                raise ReproductionError(
                    f"Unexpected Na_recovery sample count {sample_count} at {voltage:g} mV / {recovery_time:g} ms"
                )
            # channel_tools.Na_recovery stores -I[mask].min() as pulse2.
            pulse2[index] = -float(np.min(current[mask]))
            rows.append(
                {
                    "recovery_voltage_mv": voltage,
                    "recovery_interval_ms": recovery_time,
                    "samples_fitted": sample_count,
                    "test_window_first_sample_ms": float(times[mask][0]),
                    "test_window_last_sample_ms": float(times[mask][-1]),
                    "second_test_current_peak_magnitude_ma_cm2": float(pulse2[index]),
                }
            )
            row_indices.append(len(rows) - 1)

        # Preserve the authors' exact get_tau_act call, initial estimate, and
        # R² rejection behavior. The function returns NaN on an R² failure.
        try:
            apparent_tau = float(
                channel_tools.get_tau_act(recovery_times, pulse2, est=15)
            )
        except Exception:
            apparent_tau = math.nan
        for row_index in row_indices:
            rows[row_index]["apparent_recovery_tau_ms"] = apparent_tau
            rows[row_index]["source_returned_finite_tau"] = math.isfinite(apparent_tau)

    return {"rows": rows}


def inactivation_csv_text(result: dict[str, Any]) -> str:
    env = result["environment"]
    source = result["source_files"]
    clamp = env["vclamp"]
    lines = [
        "# Original Wilbers Na_IV_inact source protocol executed in NEURON 9.0.2 with the pure human na_human.mod.",
        f"# DataverseNL v{DATASET_VERSION}, DOI {DATASET_DOI}, CC0-1.0.",
        f"# channel_tools.py SHA-1 {source['channel_tools.py']['sha1']}; na_human.mod SHA-1 {source['mod/na_human.mod']['sha1']}; fit_na_hh_cma_human.py SHA-1 {source['fit_na_hh_cma_human.py']['sha1']}.",
        f"# Environment: Python {env['python']}; NEURON {env['neuron']}; NumPy {env['numpy']}; SciPy {env['scipy']}; compiler {result['compiler']}.",
        f"# Cell: diameter={env['cell_diameter_um']:g} um; default length={env['cell_length_um']:g} um; Ra={env['cell_axial_resistance_ohm_cm']:g}; cm={env['cell_capacitance_uF_cm2']:g}; ena={env['na_reversal_mV']:g} mV; default gbar={env['na_default_gbar_pS_um2']:g} pS/um2; vshift={env['na_voltage_shift_mV']:g} mV.",
        f"# VClamp defaults: gain={clamp['gain']:g}; rstim={clamp['rstim_mohm']:g} MOhm; tau1={clamp['tau1_ms']:g} ms; tau2={clamp['tau2_ms']:g} ms; fac={clamp['fac']:g}.",
        "# Protocol: 25 C; dt=0.005 ms; -70 mV initial segment for 1 ms; 30 conditioning voltages -105..-47 mV in 2-mV increments for 50 ms; -10 mV test for 10 ms.",
        "# The original (t>51)&(t<55) test window is evaluated against NEURON's recorded floating-point time vector. Per-row sample count and first/last included samples are retained; tiny boundary roundoff can add a boundary sample. Source formula is g=-I/(conditioning_voltage-ena+1e10), followed by peak and max-normalization; this literal denominator is reproduced without dimensional reinterpretation.",
        f"# Original fit_boltz_inact result: Vhalf={result['inactivation']['boltzmann_vhalf_mv']:.12g} mV; slope={result['inactivation']['boltzmann_slope_mv']:.12g} mV.",
        "# These are pure-model source-code outputs, not experimental current measurements or biological validation; the inspected Dataverse release has no raw human NWB voltage-clamp traces.",
        # CSV column names are emitted once by DictWriter below.
    ]
    import io
    output = io.StringIO()
    writer = csv.DictWriter(
        output, fieldnames=INACTIVATION_FIELDNAMES, extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for row in result["inactivation"]["rows"]:
        writer.writerow({
            key: ("" if isinstance(value, float) and not math.isfinite(value) else value)
            for key, value in row.items()
        })
    lines.append(output.getvalue().rstrip("\n"))
    return "\n".join(lines) + "\n"


def recovery_csv_text(result: dict[str, Any]) -> str:
    env = result["environment"]
    source = result["source_files"]
    clamp = env["vclamp"]
    lines = [
        "# Original Wilbers Na_recovery paired-pulse source protocol executed in NEURON 9.0.2 with the pure human na_human.mod.",
        f"# DataverseNL v{DATASET_VERSION}, DOI {DATASET_DOI}, CC0-1.0.",
        f"# channel_tools.py SHA-1 {source['channel_tools.py']['sha1']}; na_human.mod SHA-1 {source['mod/na_human.mod']['sha1']}; fit_na_hh_cma_human.py SHA-1 {source['fit_na_hh_cma_human.py']['sha1']}.",
        f"# Environment: Python {env['python']}; NEURON {env['neuron']}; NumPy {env['numpy']}; SciPy {env['scipy']}; compiler {result['compiler']}.",
        f"# Cell: diameter={env['cell_diameter_um']:g} um; default length={env['cell_length_um']:g} um; Ra={env['cell_axial_resistance_ohm_cm']:g}; cm={env['cell_capacitance_uF_cm2']:g}; ena={env['na_reversal_mV']:g} mV; default gbar={env['na_default_gbar_pS_um2']:g} pS/um2; vshift={env['na_voltage_shift_mV']:g} mV.",
        f"# VClamp defaults: gain={clamp['gain']:g}; rstim={clamp['rstim_mohm']:g} MOhm; tau1={clamp['tau1_ms']:g} ms; tau2={clamp['tau2_ms']:g} ms; fac={clamp['fac']:g}.",
        "# Protocol: 25 C; dt=0.02 ms; 2 ms at -120 mV; 10 ms at 0 mV first test; recovery intervals 1^2..12^2 ms at -90..-66 mV in 2-mV increments; final 2-ms test at 0 mV.",
        "# For each test pulse the source takes -min(I) in the open interval (12+recovery_time, 14+recovery_time). Sample count and first/last included times are recorded because NEURON's floating-point clock may include a boundary point. Its fit is channel_tools.get_tau_act(rectimes,pulse2,est=15); the source labels the plotted current nA although runIna returns local ina density (mA/cm2).",
        "# Returned recovery taus are source apparent-current fit values, not microscopic h-gate taus. These model outputs are not experimental data or biological validation.",
        # CSV column names are emitted once by DictWriter below.
    ]
    import io
    output = io.StringIO()
    writer = csv.DictWriter(
        output, fieldnames=RECOVERY_FIELDNAMES, extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for row in result["recovery"]["rows"]:
        writer.writerow({
            key: ("" if isinstance(value, float) and not math.isfinite(value) else value)
            for key, value in row.items()
        })
    lines.append(output.getvalue().rstrip("\n"))
    return "\n".join(lines) + "\n"


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
            try:
                cell.insert("na_human")
            except Exception as insert_error:
                # The NEURON wheel can auto-load a mechanism library from the
                # working directory during import, or it can require an
                # explicit load. Test by inserting the mechanism itself rather
                # than guessing from unrelated hoc names; a duplicate load of
                # an already-registered suffix is an error in NEURON.
                library = workdir / "x86_64" / "libnrnmech.so"
                if not library.is_file():
                    raise ReproductionError(
                        f"Human Na mechanism unavailable and compiled library missing: {library}"
                    ) from insert_error
                try:
                    h.nrn_load_dll(str(library))
                    cell.insert("na_human")
                except Exception as load_error:
                    raise ReproductionError(
                        f"Unable to register/insert human Na mechanism: {load_error}"
                    ) from load_error
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

            # Na_IV itself calls Na_IV_inact and Na_recovery in this order.
            # Keep their distinct sample intervals and original source helpers.
            inactivation = replay_na_iv_inactivation(
                channel_tools, cell, time_vector, h, np
            )
            recovery = replay_na_inactivation_recovery(
                channel_tools, cell, time_vector, h, np
            )
            if len(inactivation["rows"]) != 30:
                raise ReproductionError("Did not produce all 30 Na_IV_inact rows")
            if len(recovery["rows"]) != 156:
                raise ReproductionError("Did not produce all 156 Na_recovery rows")

            return {
                "environment": {
                    "python": platform.python_version(),
                    "neuron": neuron.__version__,
                    "numpy": np.__version__,
                    "scipy": __import__("scipy").__version__,
                    "secondorder": secondorder,
                    "temperature_celsius": 25.0,
                    "dt_ms": SAMPLE_INTERVAL_MS,
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
                "inactivation": inactivation,
                "recovery": recovery,
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
    parser.add_argument("--output", type=Path, help="Optional Na_IV current-fit CSV path")
    parser.add_argument("--inactivation-output", type=Path, help="Optional Na_IV_inact CSV path")
    parser.add_argument("--recovery-output", type=Path, help="Optional Na_recovery CSV path")
    parser.add_argument(
        "--emit-aux-to-stdout",
        action="store_true",
        help="Print auxiliary source CSVs with explicit delimiters for CI result capture",
    )
    args = parser.parse_args()
    result = run_protocol()
    content = csv_text(result)
    inactivation_content = inactivation_csv_text(result)
    recovery_content = recovery_csv_text(result)
    for output_path, output_content in (
        (args.output, content),
        (args.inactivation_output, inactivation_content),
        (args.recovery_output, recovery_content),
    ):
        if output_path:
            output_path.expanduser().resolve().write_text(
                output_content, encoding="utf-8"
            )
    print(content, end="")
    if args.emit_aux_to_stdout:
        print("\\nBEGIN_HUMANJS_NA_IV_INACT_CSV")
        print(inactivation_content, end="")
        print("END_HUMANJS_NA_IV_INACT_CSV")
        print("BEGIN_HUMANJS_NA_RECOVERY_CSV")
        print(recovery_content, end="")
        print("END_HUMANJS_NA_RECOVERY_CSV")
    passed = sum(bool(row["passed_joint_fit_r2"]) for row in result["rows"])
    density_gate = sum(bool(row["source_current_density_gate_passed"]) for row in result["rows"])
    recovery_finite = sum(
        bool(row["source_returned_finite_tau"])
        for row in result["recovery"]["rows"][::len(RECOVERY_INTERVALS_MS)]
    )
    print(
        f"# NEURON VClamp Na_IV replay: {density_gate}/19 pass current-density selection; "
        f"{passed}/19 pass joint-fit R² > {FIT_R2_THRESHOLD:.2f}.",
        file=sys.stderr,
    )
    print(
        f"# Na_IV_inact replay: {len(result['inactivation']['rows'])}/30 conditioning voltages; "
        f"Boltzmann Vhalf={result['inactivation']['boltzmann_vhalf_mv']:.6g} mV, "
        f"slope={result['inactivation']['boltzmann_slope_mv']:.6g} mV.",
        file=sys.stderr,
    )
    print(
        f"# Na_recovery replay: {len(result['recovery']['rows'])}/156 paired-pulse traces; "
        f"{recovery_finite}/13 finite source recovery taus.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReproductionError as error:
        print(f"REPRODUCTION ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
