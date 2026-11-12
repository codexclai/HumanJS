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

This is independent model-side execution of the authors' deposited model and helper, compared against HumanJS. It is not a comparison to raw experimental recordings, not an optimizer rerun, and not biological validation. The initial residual is now partially attributed by the controlled solver-sensitivity experiment below; it must not be interpreted as a biological model error or a parameter-fitting target.

The model remains exploratory and unaccepted for the reasons in ADR-014/ADR-016 and the current research record: defective source trap0 behavior is not exactly reproduced, the public deposit lacks raw per-cell K voltage-clamp data and missing kinetic targets, the slow K recovery parameter is pooled human/mouse, the conductance optimizer targets cross-species midpoint AP features, fitted channel densities are not direct human measurements, and the model has no spatial AIS/axon/dendrite structure.




### Channel-gate state comparison (2026-11-12)

The voltage-only residual did not show which internal mechanism states differed. The Rust trace exporter now accepts an optional gates-output path and writes all five live gate fractions alongside the unchanged voltage CSV. The NEURON diagnostic records the original NMODL m, h, m, h1, and h2 state variables, exports them with gate-dir, and compares them with HumanJS through humanjs-gates. The source states are advanced by the deposited METHOD cnexp; HumanJS advances voltage and all five gates together with its fixed-step RK4 implementation. Gate columns are dimensionless fractions, not measured channel occupancies.

For the author's default source settings (20 µs, NEURON secondorder=0, Na table on), aligned post-step gate errors against HumanJS are:

| Gate | RMSE (fraction) | Maximum absolute error (fraction) | Time of maximum |
|---|---:|---:|---:|
| Na activation m | 0.003213 | 0.016551 | 5.78 ms |
| Na inactivation h | 0.002729 | 0.006711 | 3.90 ms |
| K activation m | 0.001386 | 0.004554 | 6.90 ms |
| K fast inactivation h1 | 0.0000810 | 0.0002465 | 4.50 ms |
| K slow inactivation h2 | 0.0000770 | 0.0000948 | 29.00 ms |

The pre-spike 0–2 ms state differences are very small (Na activation RMSE 0.000216; Na inactivation 0.000123; K activation 0.000050). They rise during the AP upstroke/peak (3–4.2 ms): Na activation RMSE 0.00517, Na inactivation 0.00238, and K activation 0.00113. K fast/slow inactivation remain much closer (4.40×10⁻⁵ and 9.01×10⁻⁶). This localizes the dominant state divergence to fast activation/inactivation gates during the rapidly changing voltage trajectory, rather than a large slow-K recovery-state mismatch.

Converting the measured gate trajectories back through the deposited conductance equations at the same fitted densities gives derived model conductance-density differences of 0.1436 pS/µm² Na RMSE (2.596 pS/µm² maximum, 3.88 ms) and 0.02367 pS/µm² K RMSE (0.1081 pS/µm² maximum, 4.48 ms). These are computed mechanism outputs from the two model trajectories, not observed conductances or experimental estimates.

At a 1-µs source step with secondorder=1 and the Na table disabled, compared with the 1-µs HumanJS trace, all five state trajectories converge much more closely:

| Gate | RMSE (fraction) | Maximum absolute error (fraction) |
|---|---:|---:|
| Na activation | 0.0001406 | 0.0020874 |
| Na inactivation | 0.0000990 | 0.0012626 |
| K activation | 0.0000544 | 0.0004639 |
| K fast inactivation | 0.00000352 | 0.0000199 |
| K slow inactivation | 0.000000572 | 0.000000994 |

The source-vs-HumanJS 1-µs gate and voltage comparisons both include all 29,000 post-step samples. This high-resolution configuration is a numerical convergence diagnostic, not the authors' original simulation setting. It does not prove which numerical method is closer to biology. The source-default comparison remains the appropriate reproduction baseline.

Reproduction commands from the repository root:

    cargo run -p humanjs-core --example wilbers_current_clamp_trace -- --step-us 20 --gates-output /tmp/humanjs-gates-20us.csv > /tmp/humanjs-voltage-20us.csv
    python3.10 experiments/diagnose_wilbers_neuron_solver.py --humanjs-trace /tmp/humanjs-voltage-20us.csv --humanjs-gates /tmp/humanjs-gates-20us.csv --dt-ms 0.02 0.005 --secondorder 0 1 --na-table 1 0 --trace-dir /tmp/wilbers-voltage --gate-dir /tmp/wilbers-gates --output /tmp/wilbers-gate-diagnostics.json

For the high-resolution convergence comparison, run the Rust example with --step-us 1 and pass its voltage/gate outputs to the diagnostic with --dt-ms 0.001 --secondorder 1 --na-table 0. All output paths above are caller-selected temporary outputs, not committed traces. The five source rate-state variables are recorded using NEURON Vector recording; the unchanged author helper's voltage baseline is still independently checked in the same diagnostic.

This remains a model-to-model numerical comparison. It is not a biological state measurement, a fit acceptance test, or biological validation. It also does not isolate cnexp from RK4 on an externally prescribed identical membrane-voltage path; that is a distinct follow-up experiment if a tighter integrator-only decomposition is needed.


### Shared-voltage gate-integrator and Na-table decomposition (2026-11-12)

The remaining `cnexp`-versus-RK4 question was tested with an externally prescribed common voltage sequence. This avoids changing fitted densities or comparing gates under two different membrane-voltage histories. For each interval ending at sample `t[n+1]`, both counterfactual gate solvers receive the same post-step voltage sample `V[n+1]` (including the deposited −10-mV channel shift) and the same initial NMODL gate state. That sampling phase was independently checked: the source-equation exponential recurrence reproduces the recorded NMODL states when the source Na table mode is matched. The maximum direct-rate replay error on the 20-µs source path is 1.7623×10⁻⁶ gate fraction, below the diagnostic's 10⁻⁴ replay guard.

The isolated integrator comparison uses the same continuous source-equation rates with the Na table disabled for both methods. At 20 µs on the direct-rate source voltage path, the overall five-gate RK4-versus-cnexp difference is 2.8221×10⁻⁶ RMSE and 1.16295×10⁻⁴ maximum gate fraction. Nearly all of that is sodium activation (`m`: 6.3101×10⁻⁶ RMSE, 1.16295×10⁻⁴ max); sodium inactivation is 6.6710×10⁻⁸ RMSE and the three K gates are at or near floating-point precision. At 1 µs the overall gate RMSE falls to 1.1710×10⁻¹¹ and the maximum to 4.8856×10⁻¹⁰. The RK4-versus-cnexp difference therefore converges rapidly under the shared piecewise-constant voltage convention.

The same common voltage path also isolates the source's 200-node Na TABLE interpolation from direct analytic rates. With the CNEXP update unchanged, table-on versus direct-rate gate differences are 3.70195×10⁻⁵ overall RMSE and 1.23720×10⁻⁴ maximum; the differences occur only in the Na activation/inactivation gates (K rates are not tabled). The NMODL recurrence with the matching table setting reproduces the recorded source gate states within the 10⁻⁴ gate-fraction integrity bound for both table-on and table-off cases.

For scale, the full dynamic 20-µs source-table-off versus HumanJS gate comparison still has much larger residuals: Na activation 0.003242 RMSE, Na inactivation 0.002694, K activation 0.001448, K fast inactivation 0.0000822, and K slow inactivation 0.0000772. These are orders of magnitude above the isolated update-method errors. This indicates that the gate update rule by itself is not a sufficient explanation for the full dynamic state discrepancy. Different voltage trajectories, voltage-stage sampling and coupled membrane/gate feedback remain the main unresolved numerical contributors; the current experiment does not fully partition them.

The diagnostic adds the shared-voltage calculation to every solver variant and emits both (a) RK4-versus-exponential-update gate differences on the common path and (b) source Na-table-versus-direct-rate effects on that same path. It also checks that a matching exponential recurrence reproduces the recorded NMODL gate states within 10⁻⁴ when the rate mode matches. This is a numerical diagnostic tolerance, not biological uncertainty or model acceptance. It does not establish that either integrator is biologically superior.

Reproduce the shared-path solver and table decomposition with the pinned NEURON environment:

    python3.10 experiments/diagnose_wilbers_neuron_solver.py --dt-ms 0.02 0.001 --secondorder 0 1 --na-table 1 0 --trace-dir /tmp/wilbers-voltage --gate-dir /tmp/wilbers-gates --output /tmp/wilbers-shared-voltage-gate-results.json

The same-voltage output is computed for every variant from its source voltage samples; it does not require HumanJS trace files. Add `--humanjs-trace` and `--humanjs-gates` to also emit the independent dynamic source-vs-HumanJS comparison for the selected HumanJS files.

### CI verification of corrected NEURON reference replay (2026-11-12)

Commit 3ea7cb43fcc0e9627cfc7b6cdde3c28055356dd0 passed GitHub Actions run 43139126138. All required steps succeeded: Rust formatting, Clippy, complete Rust workspace tests, Python experiment-runner syntax, Figure S5 digitization validator, current-clamp conductance-grid validator, and repository policy. Two immediately preceding runs stopped at rustfmt because the source file lacked its terminal newline; that formatting-only issue was corrected. The source-model comparison assertions themselves passed unchanged. This CI validates the implementation and its pinned reference checks, not biological validity.


## Numerical solver sensitivity follow-up (2026-11-12)

The original source comparison's 0.455221-mV RMSE is dominated by an integration-method mismatch at the AP upstroke, not by a failure to reproduce the rheobase protocol. Inspection of the unchanged author helper and NMODL source found:

- `cc_tools.run_1AP` sets `h.dt = 0.02` ms but never assigns `h.secondorder`. The independent NEURON 9.0.2 run confirmed `h.secondorder == 0`; the documented default is fully implicit backward Euler.
- Both source mechanisms solve their channel state equations using `METHOD cnexp`. The human Na mechanism also has an active voltage-rate `TABLE` from −120 to +100 mV with `WITH 199`; the human K mechanism's table code is commented out and evaluates its rates directly.
- HumanJS performs coupled RK4 steps over voltage and all five channel gates. No biological parameter was changed in the comparison below.

NEURON's official `fadvance` documentation states that `secondorder=0` is fully implicit backward Euler, while `secondorder=1` and `2` are Crank–Nicolson variants; `secondorder=1` gives second-order-correct voltage while ionic currents remain first-order-correct, and `2` applies an additional current correction. See the [NEURON programmatic simulation-control reference](https://www.neuronsimulator.org/en/latest/progref/simctrl/programmatic.html).

The diagnostic script `experiments/diagnose_wilbers_neuron_solver.py` re-downloads and verifies the same five CC0 source files, compiles the unchanged NMODL, preserves the authors' rheobase helper, and varies only fixed timestep, `secondorder`, and the human Na table switch. The executable Rust example `crates/humanjs-core/examples/wilbers_current_clamp_trace.rs` writes the HumanJS waveform to CSV while executing the same 20-pA rheobase search and 30-pA, 3-ms AP1 pulse. Reproduction commands:

    cargo run -p humanjs-core --example wilbers_current_clamp_trace -- --step-us 20 > /tmp/humanjs-wilbers-ap1.csv
    python3.10 experiments/diagnose_wilbers_neuron_solver.py --humanjs-trace /tmp/humanjs-wilbers-ap1.csv --dt-ms 0.02 0.01 0.005 --secondorder 0 1 --na-table 1 0 --output /tmp/wilbers-solver-sensitivity.json --trace-dir /tmp/wilbers-solver-traces

All generated traces/results are outside the repository. The diagnostic baseline is checked against the unchanged source helper in the same run.

| Controlled NEURON condition | Comparison to HumanJS RK4 20-µs trace | RMSE (mV) | Maximum absolute residual (mV) |
|---|---|---:|---:|
| Author default: `dt=0.02`, `secondorder=0`, Na table on | Original source baseline | 0.455221 | 4.615873 |
| `dt=0.02`, `secondorder=1`, Na table on | Voltage Crank–Nicolson diagnostic | 0.038124 | 0.594290 |
| `dt=0.005`, `secondorder=1`, Na table on | Smaller-step CN diagnostic | 0.024745 | 0.342662 |
| `dt=0.005`, `secondorder=1`, Na table off | Direct Na rates, smaller-step CN diagnostic | 0.004756 | 0.062958 |

The same-step `secondorder=1` diagnostic reduces RMSE by about 12-fold versus the authors' default numerical configuration. With the source Na table disabled and a 5-µs CN step, the voltage trace approaches the HumanJS continuous-rate RK4 trace much more closely. A separate 1-µs comparison (CN, Na table off, against a 1-µs HumanJS trace) measured 0.001515-mV RMSE and 0.005020-mV maximum residual. HumanJS's own 20-µs trace differs from its 1-µs trace by only 0.000185-mV RMSE and 0.003502-mV maximum residual. These are numerical convergence observations under this one stimulus and parameterization, not biological accuracy estimates.

The Na table is a secondary numerical contributor, not a universal explanation of the mismatch: toggling it changes the source trace by about 0.0292-mV RMSE at `secondorder=1`, `dt=0.005` ms, but its effect on HumanJS residual depends on integration order and timestep. The author's table-on source execution remains the unchanged reference; table-off runs are diagnostic counterfactuals only.

The source `trap0` predicate was then instrumented in temporary copies of `na_human.mod` and `k_human.mod` by adding counters/minimum-distance diagnostics only; the original branch predicate, fallback expression, rate equations, and source helper were left intact. The instrumented default-source execution recorded 800 Na `trap0` calls (the four rate calls at each of the 200 Na table nodes) and 13,188 K calls across the two rheobase searches and AP1 replay. Neither mechanism entered its fallback branch: both fallback counters remained zero. The minimum observed `abs((v+theta)/q)` was 0.0142343 for Na and 0.00248676 for K, both above the 1e-6 branch threshold. The diagnostic-copy and unmodified-source voltage traces were bit-identical over all 1,451 recorded samples (maximum difference 0 mV). This establishes that the known wrong-sign predicate was not exercised in this specific source AP1 replay, including Na table generation and internal calls to the rate function. It does not make the source implementation generally safe or correct at other voltages/protocols, and does not justify changing HumanJS to reproduce the flawed fallback.

The maximum original residual occurs at 3.94 ms during the rapid upstroke. Before 2 ms, RMSE is 0.00367 mV; during the 3–4-ms upstroke it is 1.4645 mV. The mismatch then declines through repolarization and the late tail. Taken together, the step/order controls identify the source's default first-order voltage integration at 20 µs as the dominant observed cause for this AP1 trace. The diagnostic does not make the non-default CN configuration the authors' reported model, and it does not justify changing model parameters or silently replacing the reference baseline.

The model remains exploratory and unaccepted. All prior biological evidence gates remain open: incomplete per-cell K data, pooled slow recovery, cross-species optimizer targets, fitted rather than directly measured conductance densities, lack of spatial AIS/axon/dendrite structure, and the unresolved source `trap0` discrepancy. This numerical attribution is software-model comparison only.
