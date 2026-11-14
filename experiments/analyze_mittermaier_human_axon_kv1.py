#!/usr/bin/env python3
"""Reproduce per-recording human axonal Kv1 source-data fits from Mittermaier et al. (2024).

The public inputs are pseudonymized/preprocessed source tables, not raw current
waveforms. This script reproduces voltage-conductance summaries and sparse
recovery/toxin fits; it does not estimate channel kinetics from raw sweeps.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import math
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import curve_fit

FIGSHARE_DOI = "10.6084/m9.figshare.24793218.v1"
SOURCE_FILES = {
    "activation": {
        "filename": "t_Kv_activation_voltage_psd.csv",
        "url": "https://ndownloader.figshare.com/files/48304387",
        "sha256": "a2e44974b3691c9f9078e9bae91c61089cac16a0beb5ec5bbc578a693c38fc75",
        "file_id": "48304387",
    },
    "inactivation": {
        "filename": "t_Kv_inactivation_voltage_psd.csv",
        "url": "https://ndownloader.figshare.com/files/48304384",
        "sha256": "0e97dc80027de9e37f9e732aa383d65f6fe61a1075770e11e70d297824cc0590",
        "file_id": "48304384",
    },
    "recovery": {
        "filename": "t_Kv_recovery_psd.csv",
        "url": "https://ndownloader.figshare.com/files/48304390",
        "sha256": "f8a429419040ab07d88b47903ba7f27591567079b7bf2fc1187df9fcfe04fad5",
        "file_id": "48304390",
    },
    "toxin": {
        "filename": "t_Kv_toxin_psd.csv",
        "url": "https://ndownloader.figshare.com/files/48304393",
        "sha256": "09feb2c5f27595a0f6acaf8d8ba049dd808efaeae08bf377ba88c1366aadea36",
        "file_id": "48304393",
    },
}

# Derived from the final 101 samples of the authors' mean normalized long-
# inactivation trace (their R script uses rows 144900:145000 as t=0 recovery).
RECOVERY_ZERO_TIME_NORMALIZED = 0.4423915697884116

FIELDNAMES = (
    "analysis",
    "recording_id",
    "n_points",
    "voltage_min_mv",
    "voltage_max_mv",
    "bottom",
    "top",
    "vhalf_mv",
    "slope_mv",
    "rmse",
    "amplitude_fast",
    "amplitude_slow",
    "tau_fast_ms",
    "tau_slow_ms",
    "offset",
    "mean_block_fraction",
    "sd_block_fraction",
    "sem_block_fraction",
)
STRING_FIELDS = frozenset({"analysis", "recording_id"})


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download_sources(source_dir: Path) -> dict[str, Path]:
    """Download the four compact public source tables and verify pinned hashes."""
    source_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for key, metadata in SOURCE_FILES.items():
        path = source_dir / metadata["filename"]
        if not path.exists():
            request = urllib.request.Request(
                metadata["url"],
                headers={"User-Agent": "HumanJS-research/1.0"},
            )
            with urllib.request.urlopen(request, timeout=90) as response, path.open("wb") as out:
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    out.write(block)
        actual = _sha256(path)
        if actual != metadata["sha256"]:
            raise ValueError(
                f"Figshare source checksum mismatch for {metadata['filename']}: "
                f"expected {metadata['sha256']}, got {actual}"
            )
        paths[key] = path
    return paths


def _boltzmann_increasing(
    voltage: np.ndarray, bottom: float, top: float, vhalf: float, slope: float
) -> np.ndarray:
    exponent = np.clip((vhalf - voltage) / slope, -700.0, 700.0)
    return bottom + (top - bottom) / (1.0 + np.exp(exponent))


def _boltzmann_decreasing(
    voltage: np.ndarray, bottom: float, top: float, vhalf: float, slope: float
) -> np.ndarray:
    exponent = np.clip((voltage - vhalf) / slope, -700.0, 700.0)
    return bottom + (top - bottom) / (1.0 + np.exp(exponent))


def fit_boltzmann(
    voltage_mv: np.ndarray,
    normalized_conductance: np.ndarray,
    *,
    direction: str,
) -> dict[str, float]:
    """Fit a per-recording increasing activation or decreasing availability curve."""
    voltage = np.asarray(voltage_mv, dtype=float)
    conductance = np.asarray(normalized_conductance, dtype=float)
    if voltage.ndim != 1 or conductance.ndim != 1 or len(voltage) != len(conductance):
        raise ValueError("Boltzmann inputs must be equal-length one-dimensional arrays")
    if len(voltage) < 5 or not np.all(np.isfinite(voltage)) or not np.all(np.isfinite(conductance)):
        raise ValueError("Boltzmann inputs are too short or non-finite")
    if len(np.unique(voltage)) != len(voltage):
        raise ValueError("Boltzmann voltage levels must be unique")
    if np.any(conductance < -0.5) or np.any(conductance > 1.5):
        raise ValueError("Normalized conductance lies outside the declared fitting range")

    if direction == "increasing":
        function = _boltzmann_increasing
        initial = (-0.02, 1.0, -7.0, 24.0)
    elif direction == "decreasing":
        function = _boltzmann_decreasing
        initial = (0.1, 1.0, -43.0, 13.0)
    else:
        raise ValueError(f"Unsupported Boltzmann direction: {direction}")

    fitted, _ = curve_fit(
        function,
        voltage,
        conductance,
        p0=initial,
        bounds=((-0.5, 0.5, -150.0, 1.0), (0.5, 1.5, 100.0, 100.0)),
        maxfev=50000,
    )
    residual = conductance - function(voltage, *fitted)
    return {
        "bottom": float(fitted[0]),
        "top": float(fitted[1]),
        "vhalf_mv": float(fitted[2]),
        "slope_mv": float(fitted[3]),
        "rmse": float(np.sqrt(np.mean(residual**2))),
    }


def _load_voltage_source(
    path: Path,
    *,
    voltage_field: str,
    protocol: str,
) -> tuple[list[dict[str, Any]], dict[str, np.ndarray]]:
    """Apply the author's chord-conductance calculation and per-cell G/Gmax normalization."""
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        expected = ("exp_id", voltage_field, "current_amp")
        if tuple(reader.fieldnames or ()) != expected:
            raise ValueError(f"Unexpected {protocol} source columns: {reader.fieldnames}")
        grouped: dict[str, list[tuple[float, float]]] = {}
        for row in reader:
            voltage = float(row[voltage_field])
            current = float(row["current_amp"])
            driving_force = voltage + 105.0 if protocol == "activation" else 145.0
            if driving_force <= 0.0:
                raise ValueError(f"Invalid {protocol} driving force at {voltage} mV")
            conductance = current / driving_force
            grouped.setdefault(row["exp_id"], []).append((voltage, conductance))

    expected_group_count, expected_points = (9, 9) if protocol == "activation" else (5, 12)
    if len(grouped) != expected_group_count:
        raise ValueError(
            f"Unexpected {protocol} recording count: {len(grouped)} != {expected_group_count}"
        )

    curves: dict[str, np.ndarray] = {}
    records: list[dict[str, Any]] = []
    direction = "increasing" if protocol == "activation" else "decreasing"
    for recording_id, pairs in sorted(grouped.items()):
        array = np.asarray(pairs, dtype=float)
        if array.shape != (expected_points, 2):
            raise ValueError(
                f"{protocol} recording {recording_id} has shape {array.shape}, "
                f"expected {(expected_points, 2)}"
            )
        order = np.argsort(array[:, 0])
        voltage = array[order, 0]
        conductance = array[order, 1]
        if len(np.unique(voltage)) != expected_points:
            raise ValueError(f"Duplicate voltage in {protocol} recording {recording_id}")
        maximum = float(np.max(conductance))
        if not math.isfinite(maximum) or maximum <= 0.0:
            raise ValueError(f"Invalid maximum conductance in {protocol} recording {recording_id}")
        normalized = conductance / maximum
        curves[recording_id] = normalized
        fit = fit_boltzmann(voltage, normalized, direction=direction)
        records.append(
            _result_row(
                analysis=f"{protocol}_per_recording",
                recording_id=recording_id,
                n_points=expected_points,
                voltage_min_mv=float(voltage.min()),
                voltage_max_mv=float(voltage.max()),
                **fit,
            )
        )

    common_voltage = np.sort(
        np.asarray(sorted({v for v, _ in grouped[next(iter(grouped))]}), dtype=float)
    )
    if any(
        not np.array_equal(
            np.sort(np.asarray([v for v, _ in pairs], dtype=float)), common_voltage
        )
        for pairs in grouped.values()
    ):
        raise ValueError(f"{protocol} recordings do not share the same voltage grid")
    group_mean = np.mean(np.vstack([curves[key] for key in sorted(curves)]), axis=0)
    group_fit = fit_boltzmann(common_voltage, group_mean, direction=direction)
    records.append(
        _result_row(
            analysis=f"{protocol}_group_mean",
            recording_id="group_mean",
            n_points=expected_points,
            voltage_min_mv=float(common_voltage.min()),
            voltage_max_mv=float(common_voltage.max()),
            **group_fit,
        )
    )
    return records, curves


def fit_recovery(path: Path) -> dict[str, Any]:
    """Reproduce the published sparse biexponential recovery fit including its t=0 anchor."""
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != ("exp_id", "time_point", "normalized_amp"):
            raise ValueError(f"Unexpected Kv recovery source columns: {reader.fieldnames}")
        rows = [(float(row["time_point"]), float(row["normalized_amp"])) for row in reader]
    if len(rows) != 20:
        raise ValueError(f"Unexpected Kv recovery row count: {len(rows)} != 20")
    rows.append((0.0, RECOVERY_ZERO_TIME_NORMALIZED))
    data = np.asarray(rows, dtype=float)
    time = data[:, 0]
    current = data[:, 1]

    def recovery_model(
        t: np.ndarray, amp_fast: float, amp_slow: float, tau_fast: float, tau_slow: float
    ) -> np.ndarray:
        return (
            amp_fast * (1.0 - np.exp(-t / tau_fast))
            + amp_slow * (1.0 - np.exp(-t / tau_slow))
            + (1.0 - amp_fast - amp_slow)
        )

    fitted, _ = curve_fit(
        recovery_model,
        time,
        current,
        p0=(0.55, 0.2, 150.0, 1500.0),
        bounds=((0.0, 0.0, 1.0, 10.0), (1.0, 1.0, 1000.0, 10000.0)),
        maxfev=50000,
    )
    amp_fast, amp_slow, tau_fast, tau_slow = (float(x) for x in fitted)
    if tau_fast > tau_slow:
        amp_fast, amp_slow = amp_slow, amp_fast
        tau_fast, tau_slow = tau_slow, tau_fast
    residual = current - recovery_model(time, amp_fast, amp_slow, tau_fast, tau_slow)
    return _result_row(
        analysis="recovery_group_fit",
        recording_id="group_sparse",
        n_points=len(rows),
        tau_fast_ms=tau_fast,
        tau_slow_ms=tau_slow,
        amplitude_fast=amp_fast,
        amplitude_slow=amp_slow,
        offset=1.0 - amp_fast - amp_slow,
        rmse=float(np.sqrt(np.mean(residual**2))),
    )


def summarize_toxin(path: Path) -> dict[str, Any]:
    """Summarize the five published per-recording DTX-I block fractions."""
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        expected = ("exp_id", "toxin_block", "current_amp_pre_block", "current_amp_post_block")
        if tuple(reader.fieldnames or ()) != expected:
            raise ValueError(f"Unexpected Kv toxin source columns: {reader.fieldnames}")
        blocks = [float(row["toxin_block"]) for row in reader]
    if len(blocks) != 5 or not np.all(np.isfinite(blocks)):
        raise ValueError(f"Unexpected DTX-I block sample: {len(blocks)}")
    sd = float(np.std(blocks, ddof=1))
    return _result_row(
        analysis="dtx_block_summary",
        recording_id="group_summary",
        n_points=len(blocks),
        mean_block_fraction=float(np.mean(blocks)),
        sd_block_fraction=sd,
        sem_block_fraction=sd / math.sqrt(len(blocks)),
    )


def _result_row(
    *,
    analysis: str,
    recording_id: str,
    n_points: int,
    voltage_min_mv: float | None = None,
    voltage_max_mv: float | None = None,
    bottom: float | None = None,
    top: float | None = None,
    vhalf_mv: float | None = None,
    slope_mv: float | None = None,
    rmse: float | None = None,
    amplitude_fast: float | None = None,
    amplitude_slow: float | None = None,
    tau_fast_ms: float | None = None,
    tau_slow_ms: float | None = None,
    offset: float | None = None,
    mean_block_fraction: float | None = None,
    sd_block_fraction: float | None = None,
    sem_block_fraction: float | None = None,
) -> dict[str, Any]:
    return {
        "analysis": analysis,
        "recording_id": recording_id,
        "n_points": int(n_points),
        "voltage_min_mv": voltage_min_mv,
        "voltage_max_mv": voltage_max_mv,
        "bottom": bottom,
        "top": top,
        "vhalf_mv": vhalf_mv,
        "slope_mv": slope_mv,
        "rmse": rmse,
        "amplitude_fast": amplitude_fast,
        "amplitude_slow": amplitude_slow,
        "tau_fast_ms": tau_fast_ms,
        "tau_slow_ms": tau_slow_ms,
        "offset": offset,
        "mean_block_fraction": mean_block_fraction,
        "sd_block_fraction": sd_block_fraction,
        "sem_block_fraction": sem_block_fraction,
    }


def serialize_rows(rows: list[dict[str, Any]]) -> str:
    from io import StringIO

    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        if set(row) != set(FIELDNAMES):
            raise ValueError("Kv1 summary schema mismatch")
        formatted = {}
        for field, value in row.items():
            if value is None:
                formatted[field] = ""
            elif field in STRING_FIELDS:
                formatted[field] = str(value)
            elif field == "n_points":
                formatted[field] = str(int(value))
            else:
                number = float(value)
                if not math.isfinite(number):
                    raise ValueError(f"Non-finite Kv1 summary value in {field}")
                formatted[field] = format(number, ".15g")
        writer.writerow(formatted)
    return stream.getvalue()


def compare_expected(actual_path: Path, expected_path: Path) -> None:
    """Compare all per-recording and group rows against the pinned reference."""
    def read(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if tuple(reader.fieldnames or ()) != FIELDNAMES:
                raise ValueError(f"Kv1 expected-summary schema mismatch: {path}")
            rows = list(reader)
        if not rows:
            raise ValueError(f"Kv1 expected-summary is empty: {path}")
        return rows

    actual = read(actual_path)
    expected = read(expected_path)
    if len(actual) != len(expected):
        raise ValueError(f"Kv1 row-count mismatch: {len(actual)} != {len(expected)}")
    for row_index, (found, reference) in enumerate(zip(actual, expected), start=1):
        for field in FIELDNAMES:
            a, e = found[field], reference[field]
            if field in STRING_FIELDS:
                if a != e:
                    raise ValueError(
                        f"Kv1 reference mismatch row {row_index} {field}: {e!r} != {a!r}"
                    )
            elif not a and not e:
                continue
            else:
                try:
                    av, ev = float(a), float(e)
                except ValueError as exc:
                    raise ValueError(f"Invalid Kv1 numeric field {field} at row {row_index}") from exc
                if not math.isclose(av, ev, rel_tol=2e-4, abs_tol=1e-6):
                    raise ValueError(
                        f"Kv1 reference mismatch row {row_index} {field}: "
                        f"expected {ev:.12g}, got {av:.12g}"
                    )


def analyze(source_paths: dict[str, Path]) -> list[dict[str, Any]]:
    activation_rows, _ = _load_voltage_source(
        source_paths["activation"],
        voltage_field="activation_pulse_amp",
        protocol="activation",
    )
    inactivation_rows, _ = _load_voltage_source(
        source_paths["inactivation"],
        voltage_field="inactivation_pulse_amp",
        protocol="inactivation",
    )
    return activation_rows + inactivation_rows + [
        fit_recovery(source_paths["recovery"]),
        summarize_toxin(source_paths["toxin"]),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--source-dir", type=Path)
    args = parser.parse_args()

    if args.source_dir:
        paths = download_sources(args.source_dir.expanduser().resolve())
        rows = analyze(paths)
    else:
        with tempfile.TemporaryDirectory(prefix="humanjs-mittermaier-kv1-") as temp:
            paths = download_sources(Path(temp))
            rows = analyze(paths)

    content = serialize_rows(rows)
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    if args.expected:
        compare_expected(output, args.expected.expanduser().resolve())
        print("Mittermaier human axonal Kv1 summary matches every field of the committed reference.")
    print(f"Source: Figshare DOI {FIGSHARE_DOI} (CC BY 4.0, pseudonymized/preprocessed data)")
    for row in rows:
        if row["analysis"] in ("activation_group_mean", "inactivation_group_mean"):
            print(
                f"{row['analysis']}: Vhalf={row['vhalf_mv']:.6g} mV, "
                f"slope={row['slope_mv']:.6g} mV"
            )
        elif row["analysis"] == "recovery_group_fit":
            print(
                f"recovery biexponential: tau_fast={row['tau_fast_ms']:.6g} ms, "
                f"tau_slow={row['tau_slow_ms']:.6g} ms"
            )
        elif row["analysis"] == "dtx_block_summary":
            print(
                f"DTX-I block={row['mean_block_fraction']:.6g} ± "
                f"{row['sem_block_fraction']:.6g} SEM (n={row['n_points']})"
            )
    print(f"Committed comparison rows: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
