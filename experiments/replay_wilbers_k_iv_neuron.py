#!/usr/bin/env python3
"""Execute the deposited human K_IV and K_recovery source protocols in NEURON.

The original channel_tools.py and pure human k_human.mod are downloaded
unchanged, identity-checked, and executed with NEURON 9.0.2. This is source/model
execution, not a refit to unavailable raw experimental K-current traces.
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

from wilbers_k_iv_fit_diagnostics import (
    K_IV_FIT_DIAGNOSTIC_FIELDNAMES,
    K_IV_PROFILE_FIELDNAMES,
    diagnose_k_iv_postpeak_fit,
    profile_k_iv_postpeak_tau,
)

DATAFILE_URL = "https://dataverse.nl/api/access/datafile/{}"
DATASET_DOI = "10.34894/L5J0SD"
DATASET_VERSION = "3.0"
NEURON_VERSION = "9.0.2"
TEMPERATURE_CELSIUS = 34.0

K_IV_SAMPLE_INTERVAL_MS = 0.1
K_IV_HOLD_DURATION_MS = 20.0
K_IV_ACTIVATION_DURATION_MS = 500.0
K_IV_INACTIVATION_DURATION_MS = 50.0
K_IV_RETURN_DURATION_MS = 100.0
K_IV_HOLD_VOLTAGE_MV = -140.0
K_IV_INACTIVATION_VOLTAGE_MV = 60.0
K_IV_VOLTAGES_MV = tuple(float(v) for v in range(-110, 60, 5))
K_IV_ACTIVATION_MASK_START_MS = 20.4
K_IV_ACTIVATION_MASK_END_MS = 520.0
K_IV_INACTIVATION_MASK_START_MS = 520.0
K_IV_INACTIVATION_MASK_END_MS = 570.0
K_IV_SOURCE_FIT_CURRENT_THRESHOLD_MA_CM2 = 1.0e-8
K_IV_FIXED_SLOW_TAU_MS = 450.0

K_RECOVERY_SAMPLE_INTERVAL_MS = 0.5
K_RECOVERY_VOLTAGES_MV = tuple(float(v) for v in range(-90, -65, 5))
K_RECOVERY_INTERVALS_MS = tuple(
    float(v * v) for v in __import__("numpy").linspace(2.0, 92.0, 10)
)
K_RECOVERY_HOLD_VOLTAGE_MV = -120.0
K_RECOVERY_INACTIVATING_VOLTAGE_MV = 40.0
K_RECOVERY_TEST_VOLTAGE_MV = 40.0
K_RECOVERY_INITIAL_DURATION_MS = 2.0
K_RECOVERY_INACTIVATING_DURATION_MS = 5000.0
K_RECOVERY_TEST_DURATION_MS = 5.0
K_RECOVERY_WINDOW_SAMPLE_MIN = 8
K_RECOVERY_WINDOW_SAMPLE_MAX = 11

SOURCE_FILES = {
    "channel_tools.py": (
        326242, 35609, "615595a270c6170987757cd35743f5d5b5b2af0e",
    ),
    "mod/k_human.mod": (
        318647, 4220, "d299b3430ecda7a94f6d1c37ac76b2878052c7d5",
    ),
    "fit_k_hh_cma_human.py": (
        326237, 3875, "c819e59813acd70fae7af7151752bb1d8bbc7357",
    ),
}

K_IV_FIELDNAMES = (
    "voltage_mv",
    "samples_activation_window",
    "activation_window_first_sample_ms",
    "activation_window_last_sample_ms",
    "samples_inactivation_window",
    "inactivation_window_first_sample_ms",
    "inactivation_window_last_sample_ms",
    "activation_current_max_ma_cm2",
    "inactivation_current_max_ma_cm2",
    "activation_gmax_source_units",
    "inactivation_gmax_source_units",
    "normalized_activation_gmax",
    "normalized_inactivation_gmax",
    "source_tau_activation_ms",
    "source_tau_inactivation_fast_ms",
    "source_tau_inactivation_fixed_slow_ms",
    "tau_activation_fit_attempted",
    "tau_inactivation_fit_attempted",
    "boltzmann_vhalf_activation_mv",
    "boltzmann_slope_activation_mv",
    "boltzmann_vhalf_inactivation_mv",
    "boltzmann_slope_inactivation_mv",
)

K_RECOVERY_FIELDNAMES = (
    "recovery_voltage_mv",
    "recovery_interval_ms",
    "samples_test_window",
    "test_window_first_sample_ms",
    "test_window_last_sample_ms",
    "second_test_peak_current_ma_cm2",
    "source_double_exp_tau_fast_ms",
    "source_double_exp_tau_slow_ms",
    "source_fast_tau_finite",
    "source_slow_tau_finite",
)


class ReproductionError(RuntimeError):
    """A source, toolchain, or voltage-clamp reproduction step failed."""


def download_source(file_id: int, timeout: int = 60) -> bytes:
    request = urllib.request.Request(
        DATAFILE_URL.format(file_id),
        headers={"User-Agent": "HumanJS-Wilbers-K-IV-source-replay/1.0"},
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
    spec = importlib.util.spec_from_file_location("wilbers_channel_tools_k", path)
    if spec is None or spec.loader is None:
        raise ReproductionError(f"Cannot load source helper at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_k_iv(
    channel_tools: Any, cell: Any, time_vector: Any, h: Any, np: Any
) -> dict[str, Any]:
    """Replay the numerical portion of channel_tools.K_IV, including its fits."""
    h.celsius = TEMPERATURE_CELSIUS
    h.dt = K_IV_SAMPLE_INTERVAL_MS
    durations = [
        K_IV_HOLD_DURATION_MS,
        K_IV_ACTIVATION_DURATION_MS,
        K_IV_INACTIVATION_DURATION_MS,
        K_IV_RETURN_DURATION_MS,
    ]
    activation_gmax = np.empty(len(K_IV_VOLTAGES_MV), dtype=float)
    inactivation_gmax = np.empty(len(K_IV_VOLTAGES_MV), dtype=float)
    provisional_rows: list[dict[str, Any]] = []
    fit_diagnostics: list[dict[str, Any]] = []
    fit_profile: list[dict[str, Any]] = []
    fit_profile_extended: list[dict[str, Any]] = []

    for index, voltage in enumerate(K_IV_VOLTAGES_MV):
        amplitudes = [
            K_IV_HOLD_VOLTAGE_MV,
            voltage,
            K_IV_INACTIVATION_VOLTAGE_MV,
            K_IV_HOLD_VOLTAGE_MV,
        ]
        current = np.asarray(
            channel_tools.runIk(cell, durations, amplitudes), dtype=float
        )
        times = np.asarray(time_vector, dtype=float)
        expected_samples = round(sum(durations) / K_IV_SAMPLE_INTERVAL_MS) + 1
        if (
            current.ndim != 1
            or times.shape != current.shape
            or len(times) != expected_samples
            or not np.isfinite(times).all()
            or not np.isfinite(current).all()
            or np.any(np.diff(times) <= 0.0)
        ):
            raise ReproductionError(
                f"NEURON returned invalid K_IV samples at {voltage:g} mV"
            )
        if (
            abs(float(times[0])) > 1.0e-12
            or abs(float(times[-1]) - sum(durations)) > 1.0e-8
            or not np.allclose(
                np.diff(times),
                K_IV_SAMPLE_INTERVAL_MS,
                atol=1.0e-10,
                rtol=0.0,
            )
        ):
            raise ReproductionError(
                f"K_IV time grid differs from source 0.1-ms protocol at {voltage:g} mV"
            )

        activation_mask = (
            (times > K_IV_ACTIVATION_MASK_START_MS)
            & (times < K_IV_ACTIVATION_MASK_END_MS)
        )
        inactivation_mask = (
            (times > K_IV_INACTIVATION_MASK_START_MS)
            & (times < K_IV_INACTIVATION_MASK_END_MS)
        )
        activation_sample_count = int(np.count_nonzero(activation_mask))
        inactivation_sample_count = int(np.count_nonzero(inactivation_mask))
        # The helper compares its strict masks against NEURON's accumulated
        # floating-point clock. Boundary inclusion can differ by one sample;
        # retain the actual count and first/last timestamp rather than
        # replacing that recorded time vector with an idealized grid.
        if activation_sample_count not in (4995, 4996) or inactivation_sample_count not in (499, 500):
            raise ReproductionError(
                f"K_IV source sample-mask count differs at {voltage:g} mV: "
                f"{activation_sample_count}/{inactivation_sample_count}"
            )

        activation_current = current[activation_mask]
        activation_times = times[activation_mask]
        activation_peak = float(np.max(activation_current))
        activation_g = activation_current / (voltage - float(cell.ek))
        activation_gmax[index] = float(np.max(activation_g))

        inactivation_current = current[inactivation_mask]
        inactivation_times = times[inactivation_mask]
        inactivation_g = (
            inactivation_current / (K_IV_INACTIVATION_VOLTAGE_MV - float(cell.ek))
        )
        inactivation_gmax[index] = float(np.max(inactivation_g))

        tau_activation = math.nan
        tau_inactivation_fast = math.nan
        tau_inactivation_slow = math.nan
        tau_activation_attempted = activation_peak > K_IV_SOURCE_FIT_CURRENT_THRESHOLD_MA_CM2
        tau_inactivation_attempted = tau_activation_attempted
        if tau_activation_attempted:
            peak_index = int(np.argmax(activation_current))
            try:
                # Exact source calls: get_tau_act(x[0:pk], y[0:pk]) and
                # get_tau_inact_double_fixedtau2(x[pk:-1], y[pk:-1]).
                tau_activation = float(
                    channel_tools.get_tau_act(
                        activation_times[:peak_index],
                        activation_current[:peak_index],
                    )
                )
                tau_inactivation_fast, tau_inactivation_slow = (
                    channel_tools.get_tau_inact_double_fixedtau2(
                        activation_times[peak_index:-1],
                        activation_current[peak_index:-1],
                    )
                )
                tau_inactivation_fast = float(tau_inactivation_fast)
                tau_inactivation_slow = float(tau_inactivation_slow)
                try:
                    postpeak_times = activation_times[peak_index:-1]
                    postpeak_current = activation_current[peak_index:-1]
                    fit_diagnostics.extend(
                        diagnose_k_iv_postpeak_fit(
                            voltage,
                            postpeak_times,
                            postpeak_current,
                            tau_inactivation_fast,
                        )
                    )
                    if math.isclose(voltage, -70.0, abs_tol=1.0e-12):
                        fit_profile.extend(
                            profile_k_iv_postpeak_tau(
                                voltage, postpeak_times, postpeak_current
                            )
                        )
                        fit_profile_extended.extend(
                            profile_k_iv_postpeak_tau(
                                voltage,
                                postpeak_times,
                                postpeak_current,
                                tau_max_ms=1200.0,
                                grid_points=901,
                            )
                        )
                except Exception as diagnostic_error:
                    raise ReproductionError(
                        f"K_IV fit-start diagnostic failed at {voltage:g} mV: "
                        f"{type(diagnostic_error).__name__}: {diagnostic_error}"
                    ) from diagnostic_error
            except Exception as exc:
                raise ReproductionError(
                    f"Original K_IV current fit failed at {voltage:g} mV: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc

        provisional_rows.append(
            {
                "voltage_mv": voltage,
                "samples_activation_window": int(np.count_nonzero(activation_mask)),
                "activation_window_first_sample_ms": float(activation_times[0]),
                "activation_window_last_sample_ms": float(activation_times[-1]),
                "samples_inactivation_window": int(np.count_nonzero(inactivation_mask)),
                "inactivation_window_first_sample_ms": float(inactivation_times[0]),
                "inactivation_window_last_sample_ms": float(inactivation_times[-1]),
                "activation_current_max_ma_cm2": activation_peak,
                "inactivation_current_max_ma_cm2": float(np.max(inactivation_current)),
                "activation_gmax_source_units": float(activation_gmax[index]),
                "inactivation_gmax_source_units": float(inactivation_gmax[index]),
                "tau_activation_ms": tau_activation,
                "tau_inactivation_fast_ms": tau_inactivation_fast,
                "tau_inactivation_slow_ms": tau_inactivation_slow,
                "tau_activation_fit_attempted": tau_activation_attempted,
                "tau_inactivation_fit_attempted": tau_inactivation_attempted,
            }
        )

    if (
        not np.isfinite(activation_gmax).all()
        or not np.isfinite(inactivation_gmax).all()
        or float(np.max(activation_gmax)) <= 0.0
        or float(np.max(inactivation_gmax)) <= 0.0
    ):
        raise ReproductionError("K_IV produced invalid activation/inactivation conductance curves")

    normalized_activation = activation_gmax / float(np.max(activation_gmax))
    normalized_inactivation = inactivation_gmax / float(np.max(inactivation_gmax))
    vhalf_activation, slope_activation = channel_tools.fit_boltz_act(
        np.asarray(K_IV_VOLTAGES_MV, dtype=float), normalized_activation.copy()
    )
    vhalf_inactivation, slope_inactivation = channel_tools.fit_boltz_inact(
        np.asarray(K_IV_VOLTAGES_MV, dtype=float), normalized_inactivation.copy()
    )

    rows = []
    for index, row in enumerate(provisional_rows):
        rows.append(
            {
                "voltage_mv": row["voltage_mv"],
                "samples_activation_window": row["samples_activation_window"],
                "activation_window_first_sample_ms": row["activation_window_first_sample_ms"],
                "activation_window_last_sample_ms": row["activation_window_last_sample_ms"],
                "samples_inactivation_window": row["samples_inactivation_window"],
                "inactivation_window_first_sample_ms": row["inactivation_window_first_sample_ms"],
                "inactivation_window_last_sample_ms": row["inactivation_window_last_sample_ms"],
                "activation_current_max_ma_cm2": row["activation_current_max_ma_cm2"],
                "inactivation_current_max_ma_cm2": row["inactivation_current_max_ma_cm2"],
                "activation_gmax_source_units": row["activation_gmax_source_units"],
                "inactivation_gmax_source_units": row["inactivation_gmax_source_units"],
                "normalized_activation_gmax": float(normalized_activation[index]),
                "normalized_inactivation_gmax": float(normalized_inactivation[index]),
                "source_tau_activation_ms": row["tau_activation_ms"],
                "source_tau_inactivation_fast_ms": row["tau_inactivation_fast_ms"],
                "source_tau_inactivation_fixed_slow_ms": row["tau_inactivation_slow_ms"],
                "tau_activation_fit_attempted": row["tau_activation_fit_attempted"],
                "tau_inactivation_fit_attempted": row["tau_inactivation_fit_attempted"],
                "boltzmann_vhalf_activation_mv": float(vhalf_activation),
                "boltzmann_slope_activation_mv": float(slope_activation),
                "boltzmann_vhalf_inactivation_mv": float(vhalf_inactivation),
                "boltzmann_slope_inactivation_mv": float(slope_inactivation),
            }
        )
    return {
        "rows": rows,
        "fit_diagnostics": fit_diagnostics,
        "fit_profile": fit_profile,
        "fit_profile_extended": fit_profile_extended,
        "boltzmann_vhalf_activation_mv": float(vhalf_activation),
        "boltzmann_slope_activation_mv": float(slope_activation),
        "boltzmann_vhalf_inactivation_mv": float(vhalf_inactivation),
        "boltzmann_slope_inactivation_mv": float(slope_inactivation),
    }


def run_k_recovery(
    channel_tools: Any, cell: Any, time_vector: Any, h: Any, np: Any
) -> dict[str, Any]:
    """Replay the deposited K_recovery paired-pulse grid and double fit."""
    h.celsius = TEMPERATURE_CELSIUS
    h.dt = K_RECOVERY_SAMPLE_INTERVAL_MS
    rows: list[dict[str, Any]] = []
    for voltage in K_RECOVERY_VOLTAGES_MV:
        peak_amplitudes = np.empty(len(K_RECOVERY_INTERVALS_MS), dtype=float)
        provisional: list[dict[str, Any]] = []
        for index, recovery_time in enumerate(K_RECOVERY_INTERVALS_MS):
            durations = [
                K_RECOVERY_INITIAL_DURATION_MS,
                K_RECOVERY_INACTIVATING_DURATION_MS,
                recovery_time,
                K_RECOVERY_TEST_DURATION_MS,
            ]
            amplitudes = [
                K_RECOVERY_HOLD_VOLTAGE_MV,
                K_RECOVERY_INACTIVATING_VOLTAGE_MV,
                voltage,
                K_RECOVERY_TEST_VOLTAGE_MV,
            ]
            current = np.asarray(
                channel_tools.runIk(cell, durations, amplitudes), dtype=float
            )
            times = np.asarray(time_vector, dtype=float)
            total_duration = float(sum(durations))
            expected_samples = round(
                total_duration / K_RECOVERY_SAMPLE_INTERVAL_MS
            ) + 1
            if (
                current.ndim != 1
                or times.shape != current.shape
                or len(times) != expected_samples
                or not np.isfinite(times).all()
                or not np.isfinite(current).all()
                or np.any(np.diff(times) <= 0.0)
            ):
                raise ReproductionError(
                    f"NEURON returned invalid K_recovery samples at "
                    f"{voltage:g} mV / {recovery_time:g} ms"
                )
            if (
                abs(float(times[0])) > 1.0e-12
                or abs(float(times[-1]) - total_duration) > 1.0e-7
                or not np.allclose(
                    np.diff(times),
                    K_RECOVERY_SAMPLE_INTERVAL_MS,
                    atol=1.0e-9,
                    rtol=0.0,
                )
            ):
                raise ReproductionError(
                    f"K_recovery time grid differs from source 0.5-ms protocol at "
                    f"{voltage:g} mV / {recovery_time:g} ms"
                )

            window_start = (
                K_RECOVERY_INITIAL_DURATION_MS
                + K_RECOVERY_INACTIVATING_DURATION_MS
                + recovery_time
            )
            window_end = window_start + K_RECOVERY_TEST_DURATION_MS
            mask = (times > window_start) & (times < window_end)
            sample_count = int(np.count_nonzero(mask))
            if not (
                K_RECOVERY_WINDOW_SAMPLE_MIN
                <= sample_count
                <= K_RECOVERY_WINDOW_SAMPLE_MAX
            ):
                raise ReproductionError(
                    f"Unexpected K_recovery sample count {sample_count} at "
                    f"{voltage:g} mV / {recovery_time:g} ms"
                )
            peak = float(np.max(current[mask]))
            peak_amplitudes[index] = peak
            provisional.append(
                {
                    "recovery_voltage_mv": voltage,
                    "recovery_interval_ms": recovery_time,
                    "samples_test_window": sample_count,
                    "test_window_first_sample_ms": float(times[mask][0]),
                    "test_window_last_sample_ms": float(times[mask][-1]),
                    "second_test_peak_current_ma_cm2": peak,
                }
            )

        # The original K_recovery helper invokes get_double_tau_rec(rectimes,
        # pulse2) with the unshifted square-millisecond vector and its own p0,
        # bounds, and R² acceptance rule. Do not replace it with a gate fit.
        try:
            tau_fast, tau_slow = channel_tools.get_double_tau_rec(
                np.asarray(K_RECOVERY_INTERVALS_MS, dtype=float),
                peak_amplitudes,
            )
        except Exception as exc:
            raise ReproductionError(
                f"Original K_recovery double-exponential fit failed at {voltage:g} mV: "
                f"{type(exc).__name__}: {exc}"
            ) from exc
        tau_fast = float(tau_fast)
        tau_slow = float(tau_slow)
        for row in provisional:
            rows.append(
                {
                    **row,
                    "source_double_exp_tau_fast_ms": tau_fast,
                    "source_double_exp_tau_slow_ms": tau_slow,
                    "source_fast_tau_finite": math.isfinite(tau_fast),
                    "source_slow_tau_finite": math.isfinite(tau_slow),
                }
            )
    if len(rows) != len(K_RECOVERY_VOLTAGES_MV) * len(K_RECOVERY_INTERVALS_MS):
        raise ReproductionError("K_recovery did not produce all 50 paired-pulse traces")
    return {"rows": rows}


def validate_caller_setup(caller_text: str) -> None:
    required = (
        "cell.diam=10",
        "cell.insert(mechname)",
        "cell.Ra=200",
        "cell.cm=1",
        "cell.ek=-101",
        "cell.th_inact_inf_k_human  = -52.6",
        "cell.q_inact_inf_k_human  = 13.09",
        "ax = K_IV(cell)",
    )
    for source_line in required:
        if source_line not in caller_text:
            raise ReproductionError(
                f"Verified human K fitting caller no longer contains {source_line!r}"
            )


def run_protocol() -> dict[str, Any]:
    if sys.version_info < (3, 10):
        raise ReproductionError(
            f"Python 3.10 or newer is required; found {platform.python_version()}"
        )

    original_cwd = Path.cwd()
    original_path = list(sys.path)
    try:
        with tempfile.TemporaryDirectory(prefix="wilbers_k_iv_neuron_") as temp_name:
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
            caller_text = (
                workdir / "fit_k_hh_cma_human.py"
            ).read_text(encoding="utf-8")
            validate_caller_setup(caller_text)

            cell = h.Section(name="cell[0]")
            cell.diam = 10.0
            try:
                cell.insert("k_human")
            except Exception as insert_error:
                library = workdir / "x86_64" / "libnrnmech.so"
                if not library.is_file():
                    raise ReproductionError(
                        f"Human K mechanism unavailable and compiled library missing: {library}"
                    ) from insert_error
                try:
                    h.nrn_load_dll(str(library))
                    cell.insert("k_human")
                except Exception as load_error:
                    raise ReproductionError(
                        f"Unable to register/insert human K mechanism: {load_error}"
                    ) from load_error
            cell.Ra = 200.0
            cell.cm = 1.0
            cell.ek = -101.0
            cell.th_inact_inf_k_human = -52.6
            cell.q_inact_inf_k_human = 13.09

            segment = cell(0.5)
            mechanism = segment.k_human
            expected_defaults = {
                "gbar": 40.0,
                "vshift": 0.0,
                "prop_inact": 0.85,
                "prop_h2": 0.4,
                "inact_rate_factor": 1.0,
                "tha": -29.961798016904638,
                "thb": -29.961798016904638,
                "Ra": 0.018459250585411965,
                "Rb": 0.018459250585411965,
                "Rd": 0.0016901435659310753,
                "Rg": 0.0004968791312639546,
                "thi1": 40.5659148938157,
                "thi2": -75.93822659307075,
                "h2tau_inact": 450.0,
                "h2tau_inact_rec": 2789.7929428108187,
            }
            for name, expected in expected_defaults.items():
                actual = float(getattr(mechanism, name))
                # NMODL translates PARAMETER literals into compiled
                # mechanism defaults with finite decimal precision; the
                # original source SHA-1 above remains the exact identity check.
                if not math.isclose(actual, expected, rel_tol=5.0e-6, abs_tol=1.0e-7):
                    raise ReproductionError(
                        f"Unexpected pure human K mechanism default {name}: {actual}"
                    )
            # NMODL declares temp and q10 GLOBAL, not RANGE; NEURON
            # exposes them as mechanism-suffixed HOC globals rather than
            # attributes on the segment mechanism object.
            if not math.isclose(
                float(getattr(h, "temp_k_human")), 34.0,
                rel_tol=0.0, abs_tol=1.0e-12,
            ):
                raise ReproductionError("Unexpected pure human K global reference temperature")
            if not math.isclose(
                float(getattr(h, "q10_k_human")), 2.3,
                rel_tol=0.0, abs_tol=1.0e-12,
            ):
                raise ReproductionError("Unexpected pure human K global Q10")
            if not math.isclose(
                float(mechanism.th_inact_inf), -52.6, rel_tol=0.0, abs_tol=1.0e-12
            ):
                raise ReproductionError("Source caller K inactivation midpoint override was not applied")
            if not math.isclose(
                float(mechanism.q_inact_inf), 13.09, rel_tol=0.0, abs_tol=1.0e-12
            ):
                raise ReproductionError("Source caller K inactivation slope override was not applied")

            h.celsius = TEMPERATURE_CELSIUS
            h.dt = K_IV_SAMPLE_INTERVAL_MS
            secondorder = float(h.secondorder)
            if secondorder != 0.0:
                raise ReproductionError(
                    f"Expected NEURON's unmodified secondorder=0 default, found {secondorder}"
                )

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
                if not math.isclose(
                    vclamp[name], expected, rel_tol=0.0, abs_tol=1.0e-12
                ):
                    raise ReproductionError(
                        f"Unexpected NEURON VClamp default {name}: {vclamp[name]}"
                    )

            time_vector = h.Vector()
            time_vector.record(h._ref_t)
            iv = run_k_iv(channel_tools, cell, time_vector, h, np)
            recovery = run_k_recovery(channel_tools, cell, time_vector, h, np)
            return {
                "environment": {
                    "python": platform.python_version(),
                    "neuron": neuron.__version__,
                    "numpy": np.__version__,
                    "scipy": __import__("scipy").__version__,
                    "secondorder": secondorder,
                    "temperature_celsius": float(h.celsius),
                    "cell_diameter_um": float(cell.diam),
                    "cell_length_um": float(cell.L),
                    "cell_axial_resistance_ohm_cm": float(cell.Ra),
                    "cell_capacitance_uF_cm2": float(cell.cm),
                    "k_reversal_mV": float(cell.ek),
                    "k_default_gbar_pS_um2": float(mechanism.gbar),
                    "k_voltage_shift_mV": float(mechanism.vshift),
                    "k_inactivation_inf_vhalf_override_mV": float(mechanism.th_inact_inf),
                    "k_inactivation_inf_slope_override_mV": float(mechanism.q_inact_inf),
                    "k_fast_gate_inactivation_factor": float(mechanism.inact_rate_factor),
                    "k_slow_gate_inactivation_tau_ms": float(mechanism.h2tau_inact),
                    "k_slow_gate_recovery_tau_ms": float(mechanism.h2tau_inact_rec),
                    "vclamp": vclamp,
                    "iv_dt_ms": K_IV_SAMPLE_INTERVAL_MS,
                    "recovery_dt_ms": K_RECOVERY_SAMPLE_INTERVAL_MS,
                },
                "source_files": inventory,
                "compiler": shutil.which("g++") or "unavailable",
                "compile_log_tail": build_log[-3000:] if build_log else "",
                "iv": iv,
                "recovery": recovery,
            }
    finally:
        os.chdir(original_cwd)
        sys.path[:] = original_path


def _write_csv(rows: list[dict[str, Any]], fieldnames: tuple[str, ...]) -> str:
    import io
    output = io.StringIO()
    writer = csv.DictWriter(
        output, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n"
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                key: (
                    "" if isinstance(value, float) and not math.isfinite(value)
                    else value
                )
                for key, value in row.items()
            }
        )
    return output.getvalue().rstrip("\n")


def iv_csv_text(result: dict[str, Any]) -> str:
    env = result["environment"]
    source = result["source_files"]
    clamp = env["vclamp"]
    lines = [
        "# Original Wilbers K_IV numerical source protocol executed with NEURON 9.0.2 and built-in VClamp.",
        f"# DataverseNL v{DATASET_VERSION}, DOI {DATASET_DOI}, CC0-1.0.",
        f"# channel_tools.py SHA-1 {source['channel_tools.py']['sha1']}; k_human.mod SHA-1 {source['mod/k_human.mod']['sha1']}; fit_k_hh_cma_human.py SHA-1 {source['fit_k_hh_cma_human.py']['sha1']}.",
        f"# Environment: Python {env['python']}; NEURON {env['neuron']}; NumPy {env['numpy']}; SciPy {env['scipy']}; compiler {result['compiler']}.",
        f"# Cell: diameter={env['cell_diameter_um']:g} um; default length={env['cell_length_um']:g} um; Ra={env['cell_axial_resistance_ohm_cm']:g}; cm={env['cell_capacitance_uF_cm2']:g}; ek={env['k_reversal_mV']:g} mV; default gbar={env['k_default_gbar_pS_um2']:g} pS/um2; vshift={env['k_voltage_shift_mV']:g} mV.",
        f"# Source caller override: th_inact_inf={env['k_inactivation_inf_vhalf_override_mV']:g} mV; q_inact_inf={env['k_inactivation_inf_slope_override_mV']:g} mV; unmodified NMODL other defaults retained.",
        f"# Mechanism mixture: prop_inact={0.85:g}; prop_h2={0.4:g}; h2tau_inact={env['k_slow_gate_inactivation_tau_ms']:g} ms; h2tau_inact_rec={env['k_slow_gate_recovery_tau_ms']:g} ms; inact_rate_factor={env['k_fast_gate_inactivation_factor']:g}.",
        f"# Temperature={env['temperature_celsius']:g} C; dt={env['iv_dt_ms']:g} ms; secondorder={env['secondorder']}.",
        f"# VClamp defaults (runIk sets dur[0] to total duration and plays the command vector into amp[0]): gain={clamp['gain']:g}; rstim={clamp['rstim_mohm']:g} MOhm; tau1={clamp['tau1_ms']:g} ms; tau2={clamp['tau2_ms']:g} ms; fac={clamp['fac']:g}.",
        "# K_IV protocol: 20 ms at -140 mV; 34 test steps -110..+55 mV in 5-mV increments for 500 ms; 50 ms at +60 mV; 100 ms at -140 mV.",
        "# Source activation window is (t>20.4)&(t<520); source inactivation window is (t>520)&(t<570). Current fit is attempted only when max(I[activation_mask])>1e-8 mA/cm2.",
        "# Original get_tau_act, get_tau_inact_double_fixedtau2, fit_boltz_act and fit_boltz_inact helpers are called unchanged. The source fixed slow inactivation fit component is 450 ms.",
        "# Plotting and unavailable Experimental means overlays are omitted; no K tau CSVs or raw NWB K voltage-clamp traces were in the inspected Dataverse v3.0 inventory. These are model/source outputs, not empirical current refits or biological validation.",
        # _write_csv emits the column header once.
        _write_csv(result["iv"]["rows"], K_IV_FIELDNAMES),
    ]
    return "\n".join(lines) + "\n"


def fit_diagnostic_csv_text(result: dict[str, Any]) -> str:
    source = result["source_files"]
    env = result["environment"]
    lines = [
        "# Controlled multi-start counterfactuals on the exact original NEURON K_IV post-peak samples.",
        f"# DataverseNL v{DATASET_VERSION}, DOI {DATASET_DOI}, CC0-1.0.",
        f"# channel_tools.py SHA-1 {source['channel_tools.py']['sha1']}; k_human.mod SHA-1 {source['mod/k_human.mod']['sha1']}.",
        f"# Environment: Python {env['python']}; NEURON {env['neuron']}; NumPy {env['numpy']}; SciPy {env['scipy']}.",
        "# Fit: a1*exp(-t/tau1)+a2*exp(-t/450 ms)+ss; original [0,300] ms tau1 bounds and R2>0.95 reporting threshold retained.",
        "# source_literal reproduces original p0=((y0-yend)/2,(y0-yend)/2,30,y0/10); alternatives change only p0 on the same sampled waveform.",
        "# Diagnostic fits are numerical counterfactuals on a deposited computational model, not empirical human current fits, microscopic gate taus, or biological validation.",
        _write_csv(result["iv"]["fit_diagnostics"], K_IV_FIT_DIAGNOSTIC_FIELDNAMES),
    ]
    return "\n".join(lines) + "\n"


def fit_profile_csv_text(result: dict[str, Any]) -> str:
    source = result["source_files"]
    env = result["environment"]
    lines = [
        "# Profiled K_IV fast-inactivation tau objective at the −70-mV repeat-sensitive source voltage.",
        f"# DataverseNL v{DATASET_VERSION}, DOI {DATASET_DOI}, CC0-1.0.",
        f"# channel_tools.py SHA-1 {source['channel_tools.py']['sha1']}; k_human.mod SHA-1 {source['mod/k_human.mod']['sha1']}.",
        f"# Environment: Python {env['python']}; NEURON {env['neuron']}; NumPy {env['numpy']}; SciPy {env['scipy']}.",
        "# Same original NEURON post-peak samples as K_IV. For each fixed tau1, nonnegative (a1,a2,ss) are solved by bounded linear least squares.",
        "# Model: a1*exp(-t/tau1)+a2*exp(-t/450 ms)+ss; tau1 grid 0.05..300 ms, 601 logarithmic points. Original source fit remains unchanged.",
        "# This profile measures numerical identifiability of a model-current fit; it is not a human experimental current fit or biological validation.",
        _write_csv(result["iv"]["fit_profile"], K_IV_PROFILE_FIELDNAMES),
    ]
    return "\n".join(lines) + "\n"


def fit_extended_profile_csv_text(result: dict[str, Any]) -> str:
    source = result["source_files"]
    env = result["environment"]
    lines = [
        "# Extended-bound K_IV tau1 profile at −70 mV; tau1 values above 300 ms are outside the deposited source fit bounds.",
        f"# DataverseNL v{DATASET_VERSION}, DOI {DATASET_DOI}, CC0-1.0.",
        f"# channel_tools.py SHA-1 {source['channel_tools.py']['sha1']}; k_human.mod SHA-1 {source['mod/k_human.mod']['sha1']}.",
        f"# Environment: Python {env['python']}; NEURON {env['neuron']}; NumPy {env['numpy']}; SciPy {env['scipy']}.",
        "# Same original NEURON post-peak samples; for each fixed tau1, nonnegative (a1,a2,ss) are solved by bounded linear least squares.",
        "# Diagnostic counterfactual grid: tau1 0.05..1200 ms, 901 logarithmic points; fixed tau2=450 ms. Values beyond the source upper bound are not source parameter estimates.",
        "# This extended profile tests whether the constrained source-domain optimum is boundary-limited; it is not a refit to human experimental currents or biological validation.",
        _write_csv(result["iv"]["fit_profile_extended"], K_IV_PROFILE_FIELDNAMES),
    ]
    return "\n".join(lines) + "\n"


def recovery_csv_text(result: dict[str, Any]) -> str:
    env = result["environment"]
    source = result["source_files"]
    clamp = env["vclamp"]
    lines = [
        "# Original Wilbers K_recovery paired-pulse source protocol executed with NEURON 9.0.2 and built-in VClamp.",
        f"# DataverseNL v{DATASET_VERSION}, DOI {DATASET_DOI}, CC0-1.0.",
        f"# channel_tools.py SHA-1 {source['channel_tools.py']['sha1']}; k_human.mod SHA-1 {source['mod/k_human.mod']['sha1']}; fit_k_hh_cma_human.py SHA-1 {source['fit_k_hh_cma_human.py']['sha1']}.",
        f"# Environment: Python {env['python']}; NEURON {env['neuron']}; NumPy {env['numpy']}; SciPy {env['scipy']}; compiler {result['compiler']}.",
        f"# Cell: diameter={env['cell_diameter_um']:g} um; default length={env['cell_length_um']:g} um; Ra={env['cell_axial_resistance_ohm_cm']:g}; cm={env['cell_capacitance_uF_cm2']:g}; ek={env['k_reversal_mV']:g} mV; default gbar={env['k_default_gbar_pS_um2']:g} pS/um2; source activation voltage shift={env['k_voltage_shift_mV']:g} mV.",
        f"# Temperature={env['temperature_celsius']:g} C; dt={env['recovery_dt_ms']:g} ms; VClamp defaults: gain={clamp['gain']:g}; rstim={clamp['rstim_mohm']:g} MOhm; tau1={clamp['tau1_ms']:g} ms; tau2={clamp['tau2_ms']:g} ms; fac={clamp['fac']:g}.",
        "# K_recovery protocol: 2 ms at -120 mV; 5000 ms at +40 mV; recovery at -90,-85,-80,-75,-70 mV for squared intervals 4..8464 ms; 5-ms test at +40 mV.",
        "# The source extracts max(I) over the strict interval (5002+recovery_time, 5007+recovery_time), then calls get_double_tau_rec(rectimes,pulse2) with unshifted times, original p0/bounds and R2>0.95.",
        "# Source recovery tau values are apparent double-exponential current-fit parameters, not microscopic gate recovery time constants. No raw human K NWB current traces or per-voltage K tau measurement CSVs were in the inspected Dataverse v3.0 inventory. This is model/source execution, not empirical current refitting or biological validation.",
        # _write_csv emits the column header once.
        _write_csv(result["recovery"]["rows"], K_RECOVERY_FIELDNAMES),
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iv-output", type=Path, help="Optional K_IV output CSV path")
    parser.add_argument("--recovery-output", type=Path, help="Optional K_recovery output CSV path")
    parser.add_argument("--fit-diagnostic-output", type=Path, help="Optional K_IV fit-start diagnostic CSV path")
    parser.add_argument("--fit-profile-output", type=Path, help="Optional K_IV profiled fast-tau objective CSV path")
    parser.add_argument("--fit-extended-profile-output", type=Path, help="Optional extended-bound K_IV fast-tau profile CSV path")
    parser.add_argument(
        "--emit-to-stdout",
        action="store_true",
        help="Print all source and diagnostic CSVs with explicit delimiters for CI result capture",
    )
    args = parser.parse_args()
    result = run_protocol()
    iv_content = iv_csv_text(result)
    recovery_content = recovery_csv_text(result)
    fit_diagnostic_content = fit_diagnostic_csv_text(result)
    fit_profile_content = fit_profile_csv_text(result)
    fit_extended_profile_content = fit_extended_profile_csv_text(result)
    for output_path, content in (
        (args.iv_output, iv_content),
        (args.recovery_output, recovery_content),
        (args.fit_diagnostic_output, fit_diagnostic_content),
        (args.fit_profile_output, fit_profile_content),
        (args.fit_extended_profile_output, fit_extended_profile_content),
    ):
        if output_path:
            output_path.expanduser().resolve().write_text(content, encoding="utf-8")

    if args.emit_to_stdout:
        print("BEGIN_HUMANJS_K_IV_CSV")
        print(iv_content, end="")
        print("END_HUMANJS_K_IV_CSV")
        print("BEGIN_HUMANJS_K_RECOVERY_CSV")
        print(recovery_content, end="")
        print("END_HUMANJS_K_RECOVERY_CSV")
        print("BEGIN_HUMANJS_K_IV_FIT_DIAGNOSTIC_CSV")
        print(fit_diagnostic_content, end="")
        print("END_HUMANJS_K_IV_FIT_DIAGNOSTIC_CSV")
        print("BEGIN_HUMANJS_K_IV_FIT_PROFILE_CSV")
        print(fit_profile_content, end="")
        print("END_HUMANJS_K_IV_FIT_PROFILE_CSV")
        print("BEGIN_HUMANJS_K_IV_FIT_EXTENDED_PROFILE_CSV")
        print(fit_extended_profile_content, end="")
        print("END_HUMANJS_K_IV_FIT_EXTENDED_PROFILE_CSV")

    finite_act = sum(
        math.isfinite(row["source_tau_activation_ms"]) for row in result["iv"]["rows"]
    )
    finite_inact = sum(
        math.isfinite(row["source_tau_inactivation_fast_ms"])
        for row in result["iv"]["rows"]
    )
    finite_recovery = sum(
        bool(row["source_fast_tau_finite"])
        for row in result["recovery"]["rows"][::len(K_RECOVERY_INTERVALS_MS)]
    )
    print(
        f"K_IV: {len(result['iv']['rows'])}/34 voltage commands; "
        f"{finite_act}/34 finite activation fits; "
        f"{finite_inact}/34 finite source fast-inactivation fits; "
        f"activation Vhalf/slope="
        f"{result['iv']['boltzmann_vhalf_activation_mv']:.6g}/"
        f"{result['iv']['boltzmann_slope_activation_mv']:.6g} mV; "
        f"inactivation Vhalf/slope="
        f"{result['iv']['boltzmann_vhalf_inactivation_mv']:.6g}/"
        f"{result['iv']['boltzmann_slope_inactivation_mv']:.6g} mV",
        file=sys.stderr,
    )
    diagnostic_rows = result["iv"]["fit_diagnostics"]
    diagnostic_successes = sum(bool(row["fit_converged"]) for row in diagnostic_rows)
    print(
        f"K_IV fit-start diagnostics: {diagnostic_successes}/{len(diagnostic_rows)} fits converged "
        f"across {len({row['voltage_mv'] for row in diagnostic_rows})} attempted voltages.",
        file=sys.stderr,
    )
    print(
        f"K_recovery: {len(result['recovery']['rows'])}/50 paired-pulse traces; "
        f"{finite_recovery}/5 voltages have finite source double-exponential fast fits",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReproductionError as error:
        print(f"REPRODUCTION ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
