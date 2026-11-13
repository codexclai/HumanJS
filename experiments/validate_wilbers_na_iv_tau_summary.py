#!/usr/bin/env python3
"""Validate provenance and shape of the derived Wilbers Figure 3 Na IV tau summary."""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "research" / "HUMAN-L23-WILBERS-FIG3-NA-IV-TAU-SUMMARY.csv"
EXPECTED_HASHES = {
    "data_fig3.xlsx": "2cb734a19306dadbb3db051d3a55b18b08c86639",
    "plots_fig3.py": "82c5541d1bdc8f68ec0b2057386550bba3385cd3",
    "stats_fig3.py": "4ba8e1e347e667b7cd43bf8c6d86d8d4b884ea0a",
    "channel_tools.py": "615595a270c6170987757cd35743f5d5b5b2af0e",
}
EXPECTED_GRID = {
    "tau_m": [-35, -30, -25, -20, -15, -10, -5, 0, 5, 10],
    "tau_h": [-45, -40, -35, -30, -25, -20, -15, -10, -5, 0],
}
SPECIES_MAX_N = {"human": 19, "mouse": 15}
EXPECTED = {
    ("tau_m", -35, "human"): (11, 0.3088329246),
    ("tau_m", -10, "human"): (17, 0.1460707822),
    ("tau_h", -35, "human"): (17, 2.5496951916),
    ("tau_h", 0, "mouse"): (15, 0.3754951622),
}


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    text = FILE.read_text(encoding="utf-8")
    for name, digest in EXPECTED_HASHES.items():
        if digest not in text:
            fail(f"Missing source SHA-1 provenance for {name}")
    for required in (
        "RsComp > 50",
        "iv_gof_m > 0.9",
        "iv_gof_h > 0.9",
        "-40 < iv_volt < 11",
        "-45 <= iv_volt <= 0",
        "no NWB raw traces",
        "not equate them with individual HH/Markov gate time constants",
    ):
        if required not in text:
            fail(f"Missing source/method limitation: {required}")

    rows = list(csv.DictReader(
        line for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ))
    if len(rows) != 40:
        fail(f"Expected 40 voltage/species summary rows, found {len(rows)}")

    seen: set[tuple[str, int, str]] = set()
    counts: Counter[str] = Counter()
    for row in rows:
        component = row["component"]
        voltage = int(row["voltage_mV"])
        species = row["species"]
        key = (component, voltage, species)
        if component not in EXPECTED_GRID:
            fail(f"Unexpected component: {component}")
        if voltage not in EXPECTED_GRID[component]:
            fail(f"Unexpected voltage grid point: {key}")
        if species not in SPECIES_MAX_N:
            fail(f"Unexpected species: {species}")
        if key in seen:
            fail(f"Duplicate summary key: {key}")
        seen.add(key)
        n = int(row["n"])
        if not 1 <= n <= SPECIES_MAX_N[species]:
            fail(f"Invalid cell count for {key}: {n}")
        mean = float(row["mean_ms"])
        median = float(row["median_ms"])
        sd = float(row["sample_sd_ms"]) if row["sample_sd_ms"] else None
        if not all(math.isfinite(x) and x > 0.0 for x in (mean, median)):
            fail(f"Non-positive or non-finite time constant for {key}")
        if n == 1 and sd is not None:
            fail(f"Sample SD must be empty for singleton group: {key}")
        if n > 1 and (sd is None or not math.isfinite(sd) or sd < 0.0):
            fail(f"Invalid sample SD for {key}")
        if sd is not None and mean <= sd:
            fail(f"Mean/SD sanity check failed for {key}")
        counts[component] += 1

    for component, voltages in EXPECTED_GRID.items():
        for voltage in voltages:
            for species in SPECIES_MAX_N:
                if (component, voltage, species) not in seen:
                    fail(f"Missing group: {(component, voltage, species)}")
    if counts != Counter({"tau_m": 20, "tau_h": 20}):
        fail(f"Unexpected component counts: {dict(counts)}")

    for key, (expected_n, expected_mean) in EXPECTED.items():
        row = next(
            r for r in rows
            if (r["component"], int(r["voltage_mV"]), r["species"]) == key
        )
        if int(row["n"]) != expected_n:
            fail(f"Unexpected n for {key}: {row['n']}")
        if abs(float(row["mean_ms"]) - expected_mean) > 1.0e-9:
            fail(f"Unexpected mean for {key}: {row['mean_ms']}")

    print(
        "Validated 40 Figure 3 Na current-derived tau summaries "
        "(20 tau_m groups, 20 tau_h groups), source hashes and analysis filters."
    )
    print("This validates the derived workbook summary only; it is not raw-trace refitting or gate-model validation.")


if __name__ == "__main__":
    main()
