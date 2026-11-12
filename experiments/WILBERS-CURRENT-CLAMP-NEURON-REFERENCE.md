# Wilbers human L2/L3 current-clamp AP1 source execution

**Date:** 2026-11-12  
**Purpose:** reproduce the deposited model-side current-clamp rheobase and first-spike protocol in NEURON, then compare the same protocol against the HumanJS Rust model.  
**Source:** Wilbers et al., Science Advances (2023), DOI 10.1126/sciadv.ade3300; DataverseNL DOI 10.34894/L5J0SD, version 3.0, CC0-1.0.

## Execution

The runner experiments/reproduce_wilbers_current_clamp_neuron.py downloads the original helper and four hybrid current-clamp NMODL mechanisms into a temporary directory, checks the published Dataverse file IDs, byte counts, and SHA-1 hashes, compiles the mechanisms with nrnivmodl, and calls the deposited cc_tools.py functions unchanged.

Tested environment: Python 3.10.12, NEURON 9.0.2, NumPy 1.26.4, SciPy 1.11.4, pandas 2.1.4, matplotlib 3.8.4, seaborn 0.13.2, Linux x86_64 with a GNU C++ compiler. The runner pins Python package versions in experiments/requirements-wilbers-neuron.txt. A working C++ compiler, make, and nrnivmodl are required.

From the repository root, install the pinned packages and run:

    python3.10 -m pip install -r experiments/requirements-wilbers-neuron.txt
    python3.10 experiments/reproduce_wilbers_current_clamp_neuron.py --output /tmp/wilbers-neuron-ap1.json --trace-output /tmp/wilbers-neuron-ap1.csv

Both output paths are outside the tracked repository. The default conductance values are the exact all-human-kinetic endpoint of the checked 20×20 Dataverse grids: Na 114.47654963753565 pS/μm² and K 29.045736151752504 pS/μm²; Na and K human ratios are both 1.0.

## Verified source provenance

| File | Dataverse file ID | Bytes | SHA-1 |
|---|---:|---:|---|
| cc_tools.py | 318557 | 10,448 | f64162577fa5dd86892b46570d597e58e083a02b |
| na_human.mod | 318563 | 3,711 | ef158980e4bb427c97cfb8f379cd63006130b3b2 |
| na_mouse.mod | 318561 | 3,726 | 84cc161f3c38fc71d399cc998d91f0c60cbd2df1 |
| k_human.mod | 318566 | 4,326 | 622f7c9867e727a3dc7dea1f9ba2efbfb94cfd3a |
| k_mouse.mod | 318560 | 4,303 | 8b1761352a44cc57c29f3345242a4060186d84eb |

No downloaded source mechanism or helper is copied into the repository. The runner verifies the expected file identities every time it downloads the sources.

## Protocol and result

The source helper's getrheo starts by testing an initial 0.1-nA current pulse (3 ms after a 2-ms delay, dt 0.1 ms, APCount threshold −20 mV), then performs 0.1, 0.01, and 0.001-nA current increments with one-step backoff after the first two phases. The first AP is then measured with a 3-ms pulse at 1.5× rheobase, after a 1-ms delay, using dt 0.02 ms over 29 ms.

Both the original NEURON execution and corrected HumanJS replay find rheobase 20.0 pA and use a 30.0-pA AP1 pulse.

| Feature | NEURON 9.0.2 | HumanJS RK4 | Difference |
|---|---:|---:|---:|
| Peak amplitude (mV) | 49.743162 | 50.793612 | +1.050450 |
| Threshold (mV) | −39.997189 | −39.871467 | +0.125721 |
| Upstroke (mV/ms) | 414.571519 | 421.654482 | +7.082963 |
| Downstroke (mV/ms) | −73.026082 | −75.336764 | −2.310682 |
| AHP (mV) | −69.604161 | −69.627149 | −0.022987 |

The NEURON trace has 1,451 samples including t=0, and HumanJS produces 1,450 post-step samples from 0.02 to 29 ms. Aligning the common 1,450 samples gives 0.455221 mV RMSE, 4.615873 mV maximum absolute residual, and 0.197286 mV mean absolute residual. Both models peak at 4.16 ms.

## Correction to an earlier intermediate finding

The earlier Rust-only test reported 101 pA rheobase, a 151.5-pA AP1 pulse, a 59.594-mV peak, and an undefined source threshold extractor. Those values are invalid as a source-protocol comparison: the test helper omitted the initial 0.1-nA trial that the original cc_tools.getrheo performs before entering its increment loops. The source model and corrected Rust helper both return 20 pA; the corrected 30-pA pulse makes the source threshold rule well-defined. The code and research record now supersede the faulty intermediate diagnosis.

## Interpretation and limits

This is independent model-side execution of the authors' deposited model and helper, compared against HumanJS. It is not a comparison to raw experimental recordings, not an optimizer rerun, and not biological validation. The remaining trace residual includes possible differences from NEURON cnexp versus HumanJS RK4 and the explicit analytic-limit correction in HumanJS's trap0 implementation; this experiment does not apportion the residual among those mechanisms.

The model remains exploratory and unaccepted for the reasons in ADR-014/ADR-016 and the current research record: defective source trap0 behavior is not exactly reproduced, the public deposit lacks raw per-cell K voltage-clamp data and missing kinetic targets, the slow K recovery parameter is pooled human/mouse, the conductance optimizer targets cross-species midpoint AP features, fitted channel densities are not direct human measurements, and the model has no spatial AIS/axon/dendrite structure.


### CI verification of corrected NEURON reference replay (2026-11-12)

Commit 3ea7cb43fcc0e9627cfc7b6cdde3c28055356dd0 passed GitHub Actions run 43139126138. All required steps succeeded: Rust formatting, Clippy, complete Rust workspace tests, Python experiment-runner syntax, Figure S5 digitization validator, current-clamp conductance-grid validator, and repository policy. Two immediately preceding runs stopped at rustfmt because the source file lacked its terminal newline; that formatting-only issue was corrected. The source-model comparison assertions themselves passed unchanged. This CI validates the implementation and its pinned reference checks, not biological validity.
