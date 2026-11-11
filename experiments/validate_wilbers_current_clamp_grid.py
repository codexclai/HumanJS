#!/usr/bin/env python3
"""Validate the released Wilbers current-clamp conductance grid and provenance."""

from __future__ import annotations

import csv
import hashlib
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research"

EXPECTED = {
    "WILBERS-CURRENT-CLAMP-AP1COMPARISON.csv": (
        846,
        "85fea00fea374ed0595d032180a798371d96aa4d",
    ),
    "WILBERS-CURRENT-CLAMP-GBAR-NA.csv": (
        8224,
        "ac2f1b3ae108e8f256e53b0d85c4e0b353eb173a",
    ),
    "WILBERS-CURRENT-CLAMP-GBAR-K.csv": (
        8037,
        "6867798db8a5a2a77a66bb72b7cae77590ff0247",
    ),
}

ALL_HUMAN = {
    "WILBERS-CURRENT-CLAMP-GBAR-NA.csv": 114.47654963753565,
    "WILBERS-CURRENT-CLAMP-GBAR-K.csv": 29.045736151752504,
}
ALL_MOUSE = {
    "WILBERS-CURRENT-CLAMP-GBAR-NA.csv": 148.61916853685673,
    "WILBERS-CURRENT-CLAMP-GBAR-K.csv": 64.99989629764137,
}


def fail(message: str) -> None:
    raise SystemExit(message)


def verify_source_file(filename: str) -> bytes:
    path = DATA / filename
    raw = path.read_bytes()
    expected_size, expected_sha1 = EXPECTED[filename]
    actual_sha1 = hashlib.sha1(raw).hexdigest()
    if len(raw) != expected_size or actual_sha1 != expected_sha1:
        fail(
            f"{filename}: source identity mismatch; "
            f"expected {expected_size} bytes / {expected_sha1}, "
            f"found {len(raw)} bytes / {actual_sha1}"
        )
    print(f"{filename}: {len(raw)} bytes; Dataverse SHA-1 {actual_sha1} verified")
    return raw


def validate_ap1_targets(raw: bytes) -> None:
    rows = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if len(rows) != 7:
        fail(f"AP1comparison: expected seven feature rows, found {len(rows)}")
    by_name = {row["Parameter"]: row for row in rows}
    expected = {
        "amplitude": (46.18614959716797, 50.54020118713379, 48.36317539215088),
        "upstroke": (378.1895103071972, 461.7445706513443, 419.96704047927074),
        "downstroke": (-76.07215575073627, -70.13677842818666, -73.10446708946147),
    }
    for name, (human, mouse, midpoint) in expected.items():
        row = by_name[name]
        actual_human = float(row["median_human"])
        actual_mouse = float(row["median_mouse"])
        actual_midpoint = (actual_human + actual_mouse) / 2.0
        if not math.isclose(actual_human, human, rel_tol=0.0, abs_tol=1e-12):
            fail(f"AP1comparison: {name} human median changed")
        if not math.isclose(actual_mouse, mouse, rel_tol=0.0, abs_tol=1e-12):
            fail(f"AP1comparison: {name} mouse median changed")
        if not math.isclose(actual_midpoint, midpoint, rel_tol=0.0, abs_tol=1e-12):
            fail(f"AP1comparison: {name} cross-species midpoint changed")
    print(
        "AP1comparison: three fitted features verified; targets are 50:50 "
        "human/mouse medians (not human-only targets)"
    )


def validate_grid(filename: str) -> None:
    raw = verify_source_file(filename)
    rows = list(csv.reader(raw.decode("utf-8-sig").splitlines()))
    if len(rows) != 21 or any(len(row) != 21 for row in rows):
        fail(f"{filename}: expected a 20x20 matrix plus header and row labels")

    k_axis = [float(value) for value in rows[0][1:]]
    na_axis_descending = [float(row[0]) for row in rows[1:]]
    expected_axis = [index / 19.0 for index in range(20)]
    if any(
        not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-14)
        for actual, expected in zip(k_axis, expected_axis)
    ):
        fail(f"{filename}: potassium-ratio columns do not span 0..1 in 20 steps")
    if any(
        not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-14)
        for actual, expected in zip(na_axis_descending, reversed(expected_axis))
    ):
        fail(f"{filename}: sodium-ratio rows are not stored in descending order")

    matrix = [[float(value) for value in row[1:]] for row in rows[1:]]
    all_human = matrix[0][-1]  # Na ratio 1.0, K ratio 1.0
    all_mouse = matrix[-1][0]  # Na ratio 0.0, K ratio 0.0
    if not math.isclose(all_human, ALL_HUMAN[filename], rel_tol=0.0, abs_tol=1e-12):
        fail(f"{filename}: all-human kinetic endpoint changed")
    if not math.isclose(all_mouse, ALL_MOUSE[filename], rel_tol=0.0, abs_tol=1e-12):
        fail(f"{filename}: all-mouse kinetic endpoint changed")
    if not (20.0 <= min(map(min, matrix)) <= max(map(max, matrix)) <= 150.0):
        fail(f"{filename}: fitted conductance values escaped optimizer bounds [20, 150]")
    print(
        f"{filename}: 20x20 grid verified; all-human (1,1)={all_human:.14g}, "
        f"all-mouse (0,0)={all_mouse:.14g} pS/um^2"
    )


def main() -> int:
    ap1 = verify_source_file("WILBERS-CURRENT-CLAMP-AP1COMPARISON.csv")
    validate_ap1_targets(ap1)
    validate_grid("WILBERS-CURRENT-CLAMP-GBAR-NA.csv")
    validate_grid("WILBERS-CURRENT-CLAMP-GBAR-K.csv")
    print(
        "Wilbers current-clamp source tables verified. The all-human grid "
        "corner rounds to the HumanJS preset 114.48/29.05 pS/um^2; this is "
        "a source-provenance check, not a rerun of the NEURON optimizer or "
        "biological validation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
