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


### Voltage-stage sampling sensitivity (2026-11-12)

The shared-voltage replay now includes four RK4 gate-voltage conventions on the exact recorded NEURON voltage samples: left-endpoint hold, midpoint hold, right-endpoint hold, and a linear voltage ramp sampled at RK4 stages. Each uses identical initial NMODL gates, analytic source rates, timestep intervals, and the −10-mV channel shift. The diagnostic reports per-gate and overall RMSE/max error against the recorded NMODL gates, plus the direct difference between linear-ramp and right-hold RK4 trajectories. All replay trajectories are checked for finite gate fractions in [0, 1].

This is a controlled voltage-sampling counterfactual, not the coupled HumanJS intermediate voltage trajectory. It isolates how the gate ODE responds to voltage sampling on the source's recorded voltage path; it does not by itself separate full membrane/gate feedback. The pinned source replay has now been executed. See the paired source/HumanJS voltage-path attribution section below for numerical results and limitations. The model remains exploratory and unaccepted.


### 2026-11-12 — executable tests for voltage-stage sampling counterfactuals

The shared-voltage gate replay now validates all five source gate traces against the voltage sample count, finite values, and [0, 1] bounds before integration. Its gate-metric helper rejects malformed, non-finite, or shape-mismatched arrays. A standard-library unittest suite exercises (1) constant voltage, where all sampling conventions must coincide, (2) a varying voltage path, where linear-ramp and right-hold RK4 must differ, and (3) malformed gate lengths and metric shapes. CI installs the already-pinned NumPy 1.26.4 test dependency and executes `python3 -m unittest discover -s experiments -p 'test_*.py' -v`. Workflow `43167476483` passed on exact commit `c3dcffcef5b07c40f100a3ed167944afc00b104d`; the new four tests passed, along with rustfmt, Clippy, all Rust workspace tests, experiment syntax, both Wilbers validators, and repository policy.

These are deterministic software tests of the counterfactual implementation, not a NEURON source replay and not biological validation. The pinned Python 3.10 / NEURON 9.0.2 end-to-end diagnostic still needs to be run to produce source-trace-specific sensitivity values. The exploratory single-compartment model remains unaccepted.


### Paired source/HumanJS voltage-path gate attribution (2026-11-12)

The source replay was subsequently executed in a disposable Ubuntu 22.04 environment with Python 3.10.12, NEURON 9.0.2, NumPy 1.26.4, and g++ 11.4.0. The Rust HumanJS trace exporter generated the matching 20-µs AP1 voltage and five-gate traces. The unchanged author-helper baseline reproduced exactly (1,451 samples); source-vs-HumanJS voltage RMSE was 0.4552211065 mV, maximum 4.6158729296 mV at 3.94 ms. In the canonical 20-µs, secondorder=0, Na-table-on run, five-gate RMSEs were 0.003212673 Na activation, 0.002729390 Na inactivation, 0.001386170 K activation, 0.0000810083 K fast inactivation, and 0.0000769564 K slow inactivation.

On the identical recorded NEURON voltage path, RK4 gate replay RMSE against NMODL gates was 0.00330024 for left-endpoint hold, 0.00161205 for midpoint hold, 0.00157222 for linear voltage ramp, and 0.0000369553 for right-endpoint hold. This independently confirms the source NMODL gate-state update is reproduced by the post-step voltage convention.

A second counterfactual replayed the source gate equations on the HumanJS voltage samples, with the same initial source gates. With direct analytic Na rates (table off), five-gate RMSE against HumanJS live gates was 0.00199367 for source-vs-HumanJS actual gate traces, 0.00161879 for right-endpoint CNEXP, 0.00172408 for left-endpoint RK4, 0.0000385578 for midpoint RK4, and 0.0000447473 for linear-ramp RK4. The midpoint replay reduces the aggregate five-gate residual by about 51.7-fold (98.07%). Enabling the source 200-node Na table raises the midpoint/linear replay residuals to 0.0000527946 / 0.0000587224. This strongly indicates that most of the observed gate mismatch comes from the different voltage trajectories and per-step voltage sampling, rather than a different set of gate-rate parameters.

The complete 12-variant source matrix (dt 20/10/5 µs, secondorder 0/1, Na table on/off) completed. Key source-vs-HumanJS voltage RMSEs were 0.455221 mV for the unchanged author baseline, 0.0381243 mV for 20-µs secondorder=1/table-on, 0.0127377 mV for 10-µs secondorder=1/table-on, and 0.00475618 mV for 5-µs secondorder=1/table-off. The diagnostic output and generated traces stayed outside Git.

Interpretation limits: source NMODL CNEXP effectively advances gates using the post-step voltage sample; HumanJS uses coupled RK4 with voltage evaluated at internal stages. Prescribed midpoint and linear interpolation on the HumanJS voltage path closely reproduce HumanJS gates, but neither captures the actual internal RK4 stage voltages. This is a numerical model-to-model attribution, not proof that either solver is biologically more accurate and not biological validation. The single-compartment spike-capable mechanism remains exploratory and unaccepted. The next experiment should capture the actual four RK4 stage voltages from the HumanJS step and compare exact stage replay with these midpoint/linear proxies, without changing biological parameters.



### Exact coupled RK4 voltage-stage capture and gate replay (2026-11-12)

HumanJS now exposes an opt-in `step_with_voltage_stages` diagnostic that returns the exact four membrane-voltage components of the intermediate state vectors passed to its coupled RK4 derivative evaluations: k1 at t, k2 at t+dt/2, k3 at t+dt/2, and k4 at t+dt. The ordinary `step` path does not materialize the diagnostic output. The AP1 example accepts `--stages-output` and writes one four-stage row per completed step; the NEURON diagnostic accepts `--humanjs-voltage-stages` and validates the stage CSV's columns, finite values, sample count, and timestamps before replay.

Pinned execution: Ubuntu 22.04, Python 3.10.12, NEURON 9.0.2, NumPy 1.26.4, g++ 11.4.0, Rust 1.85.0. The final AP1 run exported 1,450 voltage-stage rows aligned to the 1,450 HumanJS voltage and gate samples. The unchanged author-helper source baseline remained 0.4552211065 mV voltage RMSE (4.6158729296 mV maximum at 3.94 ms) against HumanJS.

The source gate equations were then replayed using the four actual HumanJS voltage stages at each step, with identical initial gates and the same RK4 gate-stage update:
- Direct analytic Na rates (Na TABLE off): five-gate RMSE **2.45244e-8**, maximum absolute gate error **3.99679e-7**. Per-gate RMSE: Na activation 1.71060e-8, Na inactivation 2.86599e-13, K activation 5.21020e-8, K fast inactivation 2.86267e-13, K slow inactivation 2.83516e-13.
- Source 200-node Na TABLE enabled: five-gate RMSE **3.93000e-5**, maximum absolute error **1.25180e-4**. The residual is confined overwhelmingly to Na gates (activation 3.78226e-5; inactivation 7.93216e-5); K activation remains 5.21020e-8 and both K inactivation gates remain approximately 2.86e-13.

For context, the source NMODL gate traces versus HumanJS live gates have aggregate five-gate RMSE 0.00198518. Thus exact-stage replay reduces that discrepancy by about 80,900-fold with direct rates, and by about 50.5-fold with the source Na TABLE enabled. The remaining table-on difference is a lookup-table/direct-rate effect, not evidence of a different K gate mechanism. The k2 and k3 voltage stages are not interchangeable: their maximum absolute difference was 0.399717 mV at 3.98 ms; k1-to-k2 and k3-to-k4 differences reached 4.69044 and 4.57701 mV during the spike.

The complete 12-variant NEURON matrix (20/10/5 µs, secondorder 0/1, Na TABLE on/off) was rerun against the exact-stage trace. The HumanJS-stage gate replay is independent of the NEURON variant, while the source voltage comparisons retain the earlier solver sensitivity (author default 0.455221 mV; 20-µs CN/table-on 0.0381243 mV; 10-µs CN/table-on 0.0127377 mV; 5-µs CN/table-off 0.00475618 mV).

Interpretation: this is strong numerical evidence that the gate-update equations and RK4 gate-stage handling in HumanJS match the replayed Wilbers gate equations when supplied with HumanJS's actual coupled voltage stages. It does not explain away the remaining membrane-voltage trajectory difference, validate either solver biologically, or change the exploratory/unaccepted status of the single-compartment model. All stage traces and diagnostic JSON remained outside Git.

The source-order and CN replay methods now reproduce their NEURON variants within 0.00056 mV. The 250-ns current-balance identities close, and the residual is numerically accounted for by actual source midpoint currents versus HumanJS RK4-weighted currents. Next compare same-path midpoint/left-gate current and fully evolved source/HumanJS current mismatch across timestep refinement and Na TABLE settings.


### Matched-state membrane-current balance and source-order replay (2026-11-12)

The remaining AP1 voltage discrepancy was isolated without changing any biological parameter. The Rust single-compartment simulation now provides opt-in current-balance diagnostics at the four actual coupled RK4 derivative stages. Each record contains sodium, potassium, leak, and injected current density in A/m² plus the voltage derivative in V/s. A non-advancing current_balance query exposes the live endpoint balance. The ordinary step path passes no diagnostic output and does not construct current-balance records. The AP1 exporter accepts --currents-output; its CSV contains all four stage balances and the committed endpoint balance.

The NEURON runner now calls h.fcurrent() after each h.fadvance() and manually samples ina, ik, and i_pas at that committed endpoint. This is necessary because Vector.record sampling of BREAKPOINT current values occurs before the next fixed-step current refresh; the manual samples align current values with the same endpoint voltage and gates. NEURON current density is converted from mA/cm² to SI A/m² by multiplying by 10. The comparison is restricted to the all-human kinetic endpoint (na_ratio=k_ratio=1) and secondorder=0; the HumanJS current-stage trace must have exactly aligned timestamps.

The measured source voltage update is:

    C_m * (V[n+1] - V[n]) / dt = I_inj[n] - I_ion(V[n+1], G[n])

The source voltage solve therefore uses the previous recorded gate state G[n] with the implicit endpoint voltage V[n+1]. The NMODL gates are then advanced by CNEXP using the post-step voltage sample V[n+1] (with the deposited -10-mV channel shift) to produce G[n+1]. The post-step BREAKPOINT current refreshed after fadvance uses G[n+1], and is not the same current evaluation that drove the preceding voltage solve. This is the source's sequential voltage/gate update ordering.

The current-law check at 20 µs, secondorder=0, Na TABLE on, compared the deposited Na/K/leak equations evaluated at the source endpoint state against the refreshed NEURON endpoint currents. Maximum absolute differences were 1.78×10⁻¹⁵, 3.33×10⁻¹⁶, and 1.39×10⁻¹⁷ A/m² respectively. The source voltage capacitor-equation residual using V[n+1] and G[n] was 1.60×10⁻¹³ A/m² RMSE and 3.71×10⁻¹² A/m² maximum. This confirms the current equations, signs, geometry/capacitance conversion, and endpoint sampling; it does not merely compare two unrelated voltage traces.

HumanJS's RK4 stage balances independently close: the weighted four-stage capacitance current versus the weighted stage current RHS has 2.73×10⁻¹³ A/m² RMSE and 9.35×10⁻¹³ A/m² maximum error. The RK4-weighted voltage derivative versus the recorded voltage increment has 2.03×10⁻¹¹ V/s RMSE and 4.96×10⁻¹¹ V/s maximum error. These identities are also covered by Rust regression tests.

At 20 µs, the source voltage-solver current (implicit endpoint voltage with G[n]) versus the HumanJS RK4-weighted stage current has 0.026606 A/m² total RMSE and 0.428910 A/m² maximum error. Component RMSEs are 0.025245 A/m² Na, 0.004299 A/m² K, and 0.000257 A/m² leak. The difference between the source solver current and its refreshed post-step current is itself substantial around the upstroke (Na 0.061751 A/m² RMSE / 1.139587 A/m² max; K 0.004484 / 0.037382; leak effectively zero), which is exactly where the source's sequential gate update matters most.

An independent source-order replay was added to the Python diagnostic. It solves the implicit voltage equation with the previous gate state, then advances all five gates by the deposited CNEXP equations using the new voltage. It uses the exact source conductance densities, temperature factor, reversal potentials, leak density, current pulse, and selected 200-node Na rate table; it does not fit or modify parameters. Results:

| Fixed step / Na rate mode | Source-order replay vs NEURON voltage RMSE | Maximum error | Source-order replay vs HumanJS at matching step |
|---|---:|---:|---:|
| 20 µs, Na TABLE on | 0.00053756 mV | 0.00718343 mV | 0.455684 mV RMSE |
| 10 µs, Na TABLE on | 0.00054825 mV | 0.00741506 mV | 0.205701 mV RMSE |
| 5 µs, Na TABLE on | 0.00055351 mV | 0.00757305 mV | 0.0901381 mV RMSE |
| 20 µs, direct Na rates | 0.00054034 mV | 0.00722508 mV | 0.479236 mV RMSE |

The source-order replay's gate RMSE against NEURON at the author-default 20-µs/Na-table-on condition is 2.81×10⁻⁶ overall, with maximum 6.52×10⁻⁵ gate fraction. Thus the independently coded update sequence reproduces the original NEURON trace within about 0.00054 mV, while the source-vs-HumanJS voltage difference falls as the first-order timestep is reduced. This attributes the remaining model-to-model voltage residual to the source's sequential implicit-voltage/CNEXP-gate update versus HumanJS's fully coupled RK4 stage updates, with the Na TABLE as a smaller rate-evaluation contribution. It does not imply that either solver is biologically superior.

Reproduce the 20-µs current-balance comparison and Na TABLE toggle (pinned Ubuntu 22.04, Python 3.10.12, NEURON 9.0.2, NumPy 1.26.4, g++ 11.4.0, Rust 1.85.0):

    cargo run -p humanjs-core --release --example wilbers_current_clamp_trace -- --step-us 20 --gates-output /tmp/humanjs-gates.csv --stages-output /tmp/humanjs-stages.csv --currents-output /tmp/humanjs-currents.csv > /tmp/humanjs-voltage.csv
    python3.10 experiments/diagnose_wilbers_neuron_solver.py --humanjs-trace /tmp/humanjs-voltage.csv --humanjs-gates /tmp/humanjs-gates.csv --humanjs-voltage-stages /tmp/humanjs-stages.csv --humanjs-current-stages /tmp/humanjs-currents.csv --dt-ms 0.02 --secondorder 0 --na-table 1 0 --trace-dir /tmp/wilbers-voltage --gate-dir /tmp/wilbers-gates --current-dir /tmp/wilbers-currents --output /tmp/wilbers-current-balance-results.json

The 10-µs and 5-µs matched-step convergence runs use the same exporter with --step-us 10 / --step-us 5 and the corresponding --dt-ms 0.01 / --dt-ms 0.005, without --humanjs-current-stages. All generated traces and JSON remain outside Git. The spike-capable single-compartment mechanism remains exploratory and unaccepted; these are numerical source-reproduction and software regression results, not biological validation.

### Crank–Nicolson midpoint-current replay and matched-path quadrature (2026-11-13)

The AP1 diagnostic now implements a separate secondorder=1 replay. For each interval, it solves the deposited membrane equation with ionic conductances fixed at G[n] and ionic driving force evaluated at the midpoint voltage, then advances the five NMODL gates with CNEXP using the new endpoint voltage V[n+1] and the source -10-mV channel shift. This is separate from the secondorder=0 backward-Euler replay; the authors' unchanged 20-µs / secondorder=0 / Na-TABLE-on helper remains the reference.

The source integration-mode mapping follows NEURON's programmatic fadvance documentation: secondorder=1 is the Crank–Nicolson scheme (ionic currents first-order accurate and channel conductances second-order accurate at the interval midpoint); secondorder=2 adds the ionic-current output correction. See https://www.neuronsimulator.org/en/latest/progref/simctrl/programmatic.html.

The independent CN replay was checked against actual NEURON 9.0.2 direct-rate CN outputs at both 1 µs and 250 ns:
- At 1 µs, voltage RMSE 0.000557252 mV and maximum 0.00769237 mV; five-gate RMSE 2.86183×10⁻⁶ and maximum 6.76770×10⁻⁵ gate fraction.
- At 250 ns, voltage RMSE 0.000557258 mV and maximum 0.00769172 mV; five-gate RMSE 2.86169×10⁻⁶ and maximum 6.76001×10⁻⁵ gate fraction.

At 250 ns / direct-rate CN, the actual source CN midpoint-current capacitor identity closes to 1.48×10⁻¹³ A/m² RMSE / 2.84×10⁻¹³ A/m² maximum. HumanJS's exact four-stage RK4 weighted current identity closes to 2.96×10⁻¹³ A/m² RMSE / 1.10×10⁻¹² A/m² maximum. The difference between the derivative of the actual source-minus-HumanJS voltage residual and the negative difference between source CN midpoint currents and HumanJS RK4-weighted currents is 1.64×10⁻¹¹ A/m² RMSE / 4.12×10⁻¹¹ A/m² maximum. Thus, for this AP1 run and current definitions, the observed inter-solver voltage-path difference is numerically accounted for by the difference in current evaluation/quadrature, without a residual sign or units mismatch.

At the same 250-ns condition, source CN midpoint currents versus HumanJS RK4-weighted currents have total RMSE 1.74232×10⁻⁵ A/m² and maximum 2.39224×10⁻⁴ A/m². Interval detail:
- Upstroke, 3–4 ms: total current RMSE 7.16403×10⁻⁵ A/m²; sodium is dominant at 7.22564×10⁻⁵, potassium 1.49083×10⁻⁶, leak 7.07477×10⁻⁷ A/m².
- Early repolarization, 4–5 ms: total 5.47228×10⁻⁵; potassium 6.28213×10⁻⁵, sodium 2.71011×10⁻⁵, leak 2.42433×10⁻⁶ A/m².
- Late repolarization, 5–10 ms: total 1.15445×10⁻⁵; sodium 1.31111×10⁻⁵, potassium 1.31717×10⁻⁵, leak 3.07192×10⁻⁶ A/m².
- Post-spike tail, 10–29 ms: total 6.91008×10⁻⁷; leak dominates at 7.16022×10⁻⁷, sodium 8.16136×10⁻⁸, potassium 1.04786×10⁻⁷ A/m².

A further controlled counterfactual evaluates the CN-style current law on the prescribed HumanJS path: the source current law is evaluated at the midpoint of adjacent HumanJS voltages using the previous HumanJS live gate state G[n], then compared against the exact HumanJS RK4-weighted stage currents. This does not run a separate CN membrane simulation. Across the full 29-ms trace, its total current RMSE is 4.02293×10⁻⁴ A/m² (maximum 7.57115×10⁻³); sodium RMSE is 3.96583×10⁻⁴, potassium 4.34073×10⁻⁵, and leak 1.49820×10⁻⁹ A/m². During the 3–4-ms upstroke, total RMSE is 2.09938×10⁻³ A/m² and is sodium-dominated; during 4–5-ms early repolarization it is 5.31656×10⁻⁴ A/m², with sodium and potassium both contributing. This prescribed-path current difference is much larger than the 1.74232×10⁻⁵ A/m² actual source-path current mismatch. The contrast demonstrates that current quadrature on a held-left-gate HumanJS path and the fully evolved source/HumanJS state histories are not interchangeable: state-history feedback changes the current residual. It does not show that quadrature alone explains the source/HumanJS voltage difference, and it does not identify either solver as biologically superior.

At 250 ns, exact HumanJS RK4-stage replay of the source gate equations still matches HumanJS live gates with aggregate five-gate RMSE 2.50549×10⁻⁸ / maximum 5.04566×10⁻⁷. The live source-versus-HumanJS gate paths remain farther apart (Na activation 3.53941×10⁻⁵ RMSE, Na inactivation 3.15885×10⁻⁵, K activation 1.51490×10⁻⁵). This is consistent with the gate-rate equations matching on identical voltage stages while the coupled source and HumanJS voltage/gate histories differ.

A fresh 125-ns HumanJS voltage/gate/stage/current trace was generated successfully (232,000 post-step samples in each CSV). The expanded 125-ns NEURON diagnostic was then killed by the VM's memory limit (exit 137) before producing its output JSON; no new 125-ns source current-balance or exact-stage results are claimed. Earlier CSV-only 125-ns voltage RMSE values remain separately recorded in the timestep-convergence section and must not be conflated with this incomplete current run.

Reproduce the completed 250-ns paired current analysis from the repository root:

    cargo run -p humanjs-core --release --example wilbers_current_clamp_trace -- --step-ns 250 --gates-output /tmp/humanjs-250ns-gates.csv --stages-output /tmp/humanjs-250ns-stages.csv --currents-output /tmp/humanjs-250ns-currents.csv > /tmp/humanjs-250ns.csv
    python3.10 experiments/diagnose_wilbers_neuron_solver.py --humanjs-trace /tmp/humanjs-250ns.csv --humanjs-gates /tmp/humanjs-250ns-gates.csv --humanjs-voltage-stages /tmp/humanjs-250ns-stages.csv --humanjs-current-stages /tmp/humanjs-250ns-currents.csv --dt-ms 0.00025 --secondorder 1 --na-table 0 --trace-dir /tmp/wilbers-cn-direct-250ns --gate-dir /tmp/wilbers-cn-direct-gates-250ns --output /tmp/wilbers-cn-direct-250ns.json

The --step-ns option retains --step-us; --step-us 20 and --step-ns 20000 voltage CSVs were byte-identical, and 333 ns is rejected because it does not divide the protocol pulse boundaries. Generated CSVs and JSON remain outside Git. The 125-ns full diagnostic is memory-limited in the 1-GiB VM. The single-compartment mechanism remains exploratory and unaccepted; none of these numerical checks constitutes biological validation.

Next, compare the prescribed-path midpoint/left-gate current counterfactual and fully evolved source/HumanJS current paths across timestep refinement and Na TABLE settings. Keep the author-default solver as the reference, do not alter biological parameters, and distinguish current-evaluation effects from coupled state-history feedback.


### Matched 5-µs AP1 current-history refinement and Na TABLE sensitivity (2026-11-13)

A clean checkout of the exact main parent was rerun in Ubuntu 22.04 with Rust 1.85.0, Python 3.10.12, NEURON 9.0.2, NumPy 1.26.4 and g++ 11.4.0. HumanJS exported aligned voltage, five-gate, exact RK4 voltage-stage and four-stage current-balance traces at 5 µs (5,800 post-step samples). The unchanged author helper still defines the baseline as 20 µs, secondorder=0, Na TABLE on; its rheobase is 20 pA and the AP1 pulse is 30 pA from 1 to 4 ms in the 29-ms protocol. Conductance densities and all biological parameters were held fixed (all-human kinetic ratios 1.0; gNa=114.47654963754 and gK=29.045736151753 pS/µm²).

The added NEURON matrix used secondorder=1 (Crank–Nicolson) at the matched 5-µs step, toggling only the deposited human sodium lookup table. Source CN replay agrees with the corresponding NEURON voltage traces to about 0.000558 mV RMSE in both variants. The principal paired results are:

| NEURON Na TABLE | NEURON vs HumanJS voltage RMSE | Actual source CN midpoint vs HumanJS RK4-weighted total-current RMSE | Maximum current difference | Prescribed-HumanJS-path midpoint/left-gate current RMSE |
|---|---:|---:|---:|---:|
| On (source setting) | 0.02487096 mV | 0.00208318 A/m² | 0.02886256 A/m² | 0.00785330 A/m² |
| Off (counterfactual) | 0.00463648 mV | 0.000408145 A/m² | 0.00642427 A/m² | 0.00785330 A/m² |

The actual source-vs-HumanJS current difference is sodium-dominated over the full trace. Its per-component RMSEs are Na 0.00203776, K 0.000162507 and leak 0.0000248763 A/m² with TABLE on; and Na 0.000399798, K 0.0000343948 and leak 0.00000468564 A/m² with TABLE off. The event-phase decomposition is consistent with that changing balance: sodium dominates the 3–4-ms upstroke and most of 4–5-ms early repolarization; potassium becomes comparable to or larger than sodium in 5–10-ms late repolarization; leak is the largest tail component over 10–29 ms. The source CN and HumanJS RK4 capacitor-current identities close to at most 8.7×10⁻¹³ A/m². The derivative of the actual voltage residual is independently accounted for by the negative current difference to at most 2.51×10⁻¹² A/m².

The prescribed-path column is a different counterfactual: it evaluates the source current law at midpoint HumanJS voltage using left-endpoint HumanJS gates and compares it with the HumanJS RK4-weighted currents. It does not integrate a second coupled membrane trajectory and does not consult the NEURON Na lookup table, which is why its value is identical in the two variants. It remains substantially larger than either fully evolved source/HumanJS current mismatch, confirming that a held-left-gate one-step quadrature comparison cannot stand in for the coupled state histories.

For the matched direct-rate/TABLE-off condition, the earlier 250-ns source/HumanJS total-current RMSE was 1.74232×10⁻⁵ A/m², versus 4.08145×10⁻⁴ A/m² at 5 µs (about 23.4-fold). The same-HumanJS-path counterfactual was 4.02293×10⁻⁴ A/m² at 250 ns versus 7.85330×10⁻³ A/m² at 5 µs (about 19.5-fold). These two resolution points are consistent with strong timestep sensitivity, but they do not establish an asymptotic convergence order. The Na TABLE-on 5-µs run also shows materially larger residuals than the direct-rate counterfactual; TABLE-off is not a replacement for the original author setting.

A fresh matched 1-µs HumanJS trace was generated, but the session's new two-mode NEURON diagnostic could not complete: nrnivmodl exceeded a 600-s build allowance in the 1-GiB VM. Its diagnostic produced no JSON/current metrics; the temporary-directory cleanup then also reported a symbolic-link cleanup error. The earlier independently completed 1-µs source/CN replay remains a separate result and is not extended here. No new 250-ns NEURON matrix was run in this session. Generated traces, compiled mechanism attempts and JSON stayed outside Git. No biological parameters were fitted or changed, the author-default baseline was retained, and the single-compartment model remains exploratory and unaccepted. These are numerical solver/current-evaluation comparisons, not biological validation.
