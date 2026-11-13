#!/usr/bin/env python3
"""Recompute the non-source K_IV third-exponential residual counterfactual."""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from wilbers_k_iv_three_component import (
    profile_three_exponential_correction,
    read_profile_tau,
    read_residual_waveform,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESIDUALS = ROOT / "research/HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-RESIDUALS.csv"
DEFAULT_LOCAL_PROFILE = ROOT / "research/HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-LOCAL.csv"


def validate(residuals_path: Path, profile_path: Path) -> None:
    # Confirm the upstream record still identifies the exact public source and
    # states that these are deterministic source-model residuals.
    preamble = residuals_path.read_text(encoding="utf-8").splitlines()[:8]
    joined_preamble = "\n".join(preamble)
    for required in (
        "DataverseNL v3.0",
        "615595a270c6170987757cd35743f5d5b5b2af0e",
        "d299b3430ecda7a94f6d1c37ac76b2878052c7d5",
        "No measurement-noise model",
    ):
        if required not in joined_preamble:
            raise SystemExit(f"Residual source provenance marker is missing: {required}")

    times, source_times, current = read_residual_waveform(residuals_path)
    tau1 = read_profile_tau(profile_path)
    if len(times) != 4890 or not math.isclose(float(times[0]), 0.0, abs_tol=1e-12):
        raise SystemExit("K_IV counterfactual input does not begin at the expected post-peak time")
    if not math.isclose(float(source_times[0]), 30.9, abs_tol=1e-6):
        raise SystemExit("K_IV source clock no longer begins at the recorded 30.9-ms sample")

    result = profile_three_exponential_correction(times, current, tau1)
    baseline = result["baseline"]
    signed = result["best_signed"]
    positive = result["positive_control"]
    grid_step = (2.0 - 0.6) / (801 - 1)
    if not (0.6 + grid_step < signed["tau3_ms"] < 2.0 - grid_step):
        raise SystemExit("Signed-model tau3 minimum lies on the profile boundary")
    if signed["a3_ma_cm2"] >= 0.0:
        raise SystemExit("The extra term is no longer a negative residual correction")
    peak_fraction = abs(signed["a3_ma_cm2"]) / float(max(abs(current)))
    if peak_fraction >= 0.001:
        raise SystemExit("The signed residual correction is not below 0.1% of peak current")

    full_improvement = 1.0 - signed["rmse_full_ma_cm2"] / baseline["rmse_full_ma_cm2"]
    early_improvement = (
        1.0
        - signed["rmse_first_10ms_ma_cm2"]
        / baseline["rmse_first_10ms_ma_cm2"]
    )
    late_improvement = (
        1.0
        - signed["rmse_after_10ms_ma_cm2"]
        / baseline["rmse_after_10ms_ma_cm2"]
    )
    if full_improvement < 0.70 or early_improvement < 0.90 or late_improvement < 0.20:
        raise SystemExit(
            "The signed third exponential no longer improves the full and partitioned objectives"
        )
    if abs(signed["a1_ma_cm2"] / baseline["a1_ma_cm2"] - 1.0) >= 0.01:
        raise SystemExit("The fitted first exponential amplitude changed by 1% or more")
    if abs(signed["a2_ma_cm2"] / baseline["a2_ma_cm2"] - 1.0) >= 0.02:
        raise SystemExit("The fitted fixed-450-ms amplitude changed by 2% or more")
    if (
        abs(
            signed["steady_offset_ma_cm2"]
            / baseline["steady_offset_ma_cm2"]
            - 1.0
        )
        >= 2.0e-4
    ):
        raise SystemExit("The fitted steady offset changed by 0.02% or more")
    if abs(positive["a3_ma_cm2"]) > 1.0e-13:
        raise SystemExit(
            "Nonnegative control unexpectedly retained a positive extra component"
        )
    if not math.isclose(
        positive["rmse_full_ma_cm2"],
        baseline["rmse_full_ma_cm2"],
        rel_tol=2.0e-3,
        abs_tol=1.0e-13,
    ):
        raise SystemExit(
            "Nonnegative control does not reproduce the two-component baseline"
        )

    print(
        "K_IV three-exponential residual counterfactual: "
        f"tau1={tau1:.9f} ms; best tau3={signed['tau3_ms']:.4f} ms; "
        f"a3={signed['a3_ma_cm2']:.6g} mA/cm2 "
        f"({100.0 * peak_fraction:.4f}% of peak); "
        f"full RMSE {baseline['rmse_full_ma_cm2']:.6g} -> "
        f"{signed['rmse_full_ma_cm2']:.6g} "
        f"({100.0 * full_improvement:.2f}% lower); "
        f"first-10-ms RMSE {baseline['rmse_first_10ms_ma_cm2']:.6g} -> "
        f"{signed['rmse_first_10ms_ma_cm2']:.6g} "
        f"({100.0 * early_improvement:.2f}% lower); "
        f"post-10-ms RMSE change {100.0 * late_improvement:.2f}% lower."
    )
    print(
        "Coefficient shifts after refitting the original terms: "
        f"a1={100.0 * (signed['a1_ma_cm2'] / baseline['a1_ma_cm2'] - 1.0):+.4f}%; "
        f"a2={100.0 * (signed['a2_ma_cm2'] / baseline['a2_ma_cm2'] - 1.0):+.4f}%; "
        "offset="
        f"{100.0 * (signed['steady_offset_ma_cm2'] / baseline['steady_offset_ma_cm2'] - 1.0):+.5f}%."
    )
    print(
        "Nonnegative a3 control: extra coefficient is zero within tolerance and "
        "reproduces the two-component baseline at the signed optimum; the improved "
        "term is therefore a signed residual correction, not a positive additive "
        "current component."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--residuals", type=Path, default=DEFAULT_RESIDUALS)
    parser.add_argument("--local-profile", type=Path, default=DEFAULT_LOCAL_PROFILE)
    args = parser.parse_args()
    validate(args.residuals, args.local_profile)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
