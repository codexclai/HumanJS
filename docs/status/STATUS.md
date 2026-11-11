# HumanJS — current status

**As of:** 2026-11-11  
**Stage:** two foundational Rust CPU mechanisms plus one exploratory, unaccepted human L2/L3 single-compartment spike-capable mechanism. HumanJS is not a whole-brain simulator.

## Canonical repository and live state

- Repository: `codexclai/HumanJS`, public, default branch `main`.
- Live verification on 2026-11-11: default branch `main`; HEAD `65fb7d37e410a2eedc44b1f29e1f528956c8d535`; complete 63-entry tree, not truncated; exactly one branch (`main`); zero open issues and zero open pull requests.
- Latest implementation commit remains `3c28de63c8a953c85084ff7c6731caae144b4ee6`; latest research evidence commit is `7df2bb1e25021fe454b9c18979e5a54602dd3272`. The latest documentation reconciliation commits are `22c9e5ca0b696dd4bc230f8f6a96889e16b307f5` and `65fb7d37e410a2eedc44b1f29e1f528956c8d535`.
- GitHub Actions run `43070078342` passed on exact HEAD `65fb7d37e410a2eedc44b1f29e1f528956c8d535`: https://github.com/codexclai/HumanJS/actions/runs/43070078342. The `policy-and-rust` job passed Rust formatting, Clippy, workspace tests, Python experiment-runner syntax, the seven-CSV Figure S5 validator, and repository policy. This run is the current verification record; it does not establish biological validation.
- A fresh NEURON 9.0.2 check independently reconfirmed that unchanged `k_human.mod` and `k_mouse.mod` compile with `nrnivmodl` but fail unmodified `modlunit` at the untyped `trates(v+vshift)` call (line 82). This is a source unit-annotation failure, not a HumanJS CI failure; ADR-014 records the typed temporary diagnostic findings. No deposited source was modified.
- No fresh local Rust test run is claimed; the verified Rust checks above ran in GitHub Actions.

## Implemented Rust CPU mechanisms

### 1. Passive membrane

The Rust workspace `crates/humanjs-core` contains:
- Validated SI wrappers for voltage, current, capacitance, conductance, input resistance, and membrane time constant.
- Integer-nanosecond simulation time and positive step durations.
- Separate passive model parameters, initial conditions, and live runtime state.
- A single-compartment passive RC equation integrated analytically for piecewise-constant injected current.
- Derivation of lumped capacitance and leak conductance from supplied input resistance and time constant.
- Failed-step handling that does not partially update membrane state.

### 2. Glutamatergic synapse

The CPU synapse contains independent AMPA-like and NMDA-like normalized biexponential conductance kernels, voltage-dependent NMDA magnesium unblock, and deterministic presynaptic availability/depression/recovery. The membrane step uses interval-mean conductances and midpoint NMDA unblock. The membrane and synapse states update transactionally.

This is an effective conductance abstraction for an adult human L2/L3 pyramidal-to-pyramidal evidence context, not a complete molecular or ultrastructural synapse. It excludes stochastic vesicle fusion, presynaptic calcium/release-site machinery, cleft glutamate dynamics/uptake, receptor Markov/desensitization states, dendritic spines/cable, and inhibitory inputs.

### 3. Exploratory human L2/L3 single-compartment Na+/K+ spike model

`crates/humanjs-core/src/ion_channels.rs` adds `HumanL23SingleCompartmentModel`, its initial conditions, runtime state, and CPU simulation. It integrates voltage plus five channel gates using fixed-step RK4, explicit SI surface/capacitance/conductance quantities, finite/bounded gate checks, and transactional state updates. The checked-in software fixture generates one spike for a 25 pA current pulse and checks selected waveform-scale values.

**Classification: exploratory, not scientifically accepted or biologically validated.** It is one electrically lumped compartment, not a spatial soma/AIS neuron, intact pyramidal neuron, axon, dendritic tree, or propagating neural system.

Parameter/evidence boundaries:
- Na+ gates use values transcribed from the pure Wilbers human `na_human.mod`.
- K+ gates use the pure `k_human.mod` values that match Table S2 and the first optimizer result. Inspection of `fit_k_hh_cma_human.py` shows that this first result is explicitly applied; the trailing alternate six-value dictionary is a bare literal, never assigned or applied.
- The script assigns `h12factor_k_human=10.5`, but all three inspected pure/hybrid K+ NMODL variants contain only a commented-out `h2tau = h1tau * h12factor` line, with no active declaration or use; `channel_tools.py` does not read the Python attribute.
- The article's 14-parameter description counts two inactivation steady-state values and an independent `Rb`; the deposited scripts assign the former from experimental fits and constrain `Rb = Ra`, leaving 11 optimizer variables. The parameter-count difference is traced to these constraints, though full protocol reproduction remains outstanding. The article Discussion also acknowledges that its HH channel models did not accurately reproduce potassium inactivation and that this likely contributed to poor K+ current and AP-fall fits.
- Current-clamp maximum conductance densities (114.48 pS/μm² Na+, 29.05 pS/μm² K+) are fitted against cross-species mean AP features, not direct human channel-density measurements.
- The 10 μm cylindrical geometry, 34°C, −10 mV channel shift, +15 mV reversal offsets, 1 μF/cm² capacitance, leak corresponding to Rm=10,000 Ω·cm², and 20 μs step follow the authors' current-clamp helper.
- The Rust `trap0` function uses a stable analytic limit at the mathematical singularity. It does not reproduce the problematic source branch logic exactly. The pure NMODL files declare the prefactor as `/ms`, but the voltage-valued numerator in the source equation requires `mV⁻¹·ms⁻¹`; HumanJS retains numeric values and uses the equation-consistent internal unit pending source unit-contract verification.

Current software tests cover the analytic rate limit/continuity, human gate half-voltage steady states, potassium fast/slow inactivation branch constants and conductance fractions, positive finite time constants over a bounded voltage scan, Q10 scaling, deposited K+ gate-clamp replay, all 50 recovery voltage/delay gate-clamp conditions, source `K_IV` current-activation fitting at seven voltages, post-peak biexponential inactivation fitting at six voltages, and the 50-condition `K_recovery` current/bi-exponential-fit protocol with five-voltage SciPy references preserved in a CSV, plus one-spike waveform scale, approximate step-size convergence, reset, and transactional failure. These remain software/source-protocol regressions, not biological validation. They do not reproduce the full published voltage-clamp protocols or independently validate the fitted current-clamp model. See ADR-014, ADR-016, `docs/architecture/SYSTEM-ARCHITECTURE.md`, and `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`.

## Human spike-initiation evidence and external model reproduction

The canonical evidence record is `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`. The Eyal external reproduction protocol/results are in `experiments/HUMAN-L23-SPIKE-MODEL-REPRODUCTION.md`, with runner `experiments/reproduce_eyal_figure7a.py`.

### Eyal et al. (2018)

The official 139,316,573-byte ModelDB archive for model 238347 was retrieved, integrity-tested, and audited. SHA-256: `12dfd8b8fb38b28136d6904da69aaf5e200fa5fb64cd03d845a96d972057354b`. It is not stored in this repository.

The six HOC models map to Table S4. The active spike-model templates insert nine conductance mechanisms in soma and axon plus `CaDynamics_E2`; `Ca_HVA` is present in the archive but is not inserted by those six templates, and `NMDA.mod` is a separate synaptic mechanism. The six models use a two-section 60 μm axon stub; dendritic branches remain passive. The model uses rodent-like channel kinetic forms, so fitted conductances and transferred kinetics remain distinct evidence classes.

The ten mechanisms actually inserted by those six templates compiled in NEURON 9.0.2. A Python 3 reproduction of the Figure 7A construction/stimulus sequence ran all six cells and compared first-spike metrics with released human current-clamp traces. Some model/data timing, width, and peak differences remain. This is a selected model-execution audit, not an independent refit, exact trace match, HumanJS implementation, or biological validation.

### Wilbers et al. (2023)

The pure human `na_human.mod` and `k_human.mod` files were retrieved from the CC0 DataverseNL deposit, checksum-verified, compiled unchanged, and probed in NEURON 9.0.2. Direct exact-singularity probes exposed non-finite `trap0` values. The active Na+ table's 200 nodes were finite; with the table disabled, exact-singularity rates were non-finite. K+ has no active table; exact singularities are non-finite and two opposite-sign branch triggers produce negative inactivation time constants.

The K+ file matches the parameter values actually applied in the deposited fitting sequence; the trailing alternate dictionary is not applied. The article's 14-parameter model description is reconciled with the deposited 11-variable optimizer sequence by the two experimentally fixed inactivation steady-state values and `Rb = Ra` constraint. `h12factor_k_human` is not consumed by the pure mechanism/helper. The full Wilbers voltage-clamp fitting workflow was not rerun from raw traces; public workbooks are summary fits and the original NWB traces were absent from the 65-file Dataverse version examined.


### Wilbers K+ voltage-clamp source audit (2026-11-11)

- Retrieved and inspected the original `fit_k_hh_cma_human.py`, `channel_tools.py`, `channel_kinetics.py`, and pure `k_human.mod` from DataverseNL version 3.0 (DOI 10.34894/L5J0SD; 65 public files).
- Reconstructed the model-side activation/inactivation and recovery clamp sequences, including the 5-s +40-mV inactivation pulse and recovery intervals 4–8,464 ms at −90 to −70 mV. The helper also contains a deactivation protocol, but it is not part of the human fit criteria.
- The human optimizer uses a pooled human/mouse fast-recovery target of 236.824345 ms. The 450-ms slow-inactivation and 2,789.7929-ms slow-recovery constants are fixed mechanism values, not fitted variables. The reported slow-inactivation score (2.4386) is substantially larger than fast-inactivation (0.0721) and fast-recovery (0.00235), and receives 0.05 relative weight.
- The K fitting helper reads `Experimental means/k_tau_act.csv`, `k_tau_inact_fast.csv`, and `k_tau_inact_slow.csv`; these files are absent from the public 65-file inventory. The K plotting script references `data_fig5.xlsx`, also absent. The available `K_data_fig2.xlsx` contains AP-clamp amplitude series, not voltage-step kinetic traces. No raw K voltage-clamp NWB current traces were found in the inspected public inventory.
- This closes the source-protocol/optimizer audit, not the numerical reproduction gate. Rust tests now replay the deposited activation, inactivation, and recovery command sequences and compare the full K_IV_ss steady-state voltage series with the paper-level human summary. Half-range interpolation gives −3.25 mV activation midpoint, −51.48 mV inactivation midpoint, and 0.936 availability at −80 mV, each within the published human mean ± SD. This is a coarse summary comparison, not raw-trace or kinetic validation. The expanded recovery test now checks all 50 combinations in the deposited five-voltage × ten-delay protocol against independent model-side reference values; it passed formatting, Clippy, Rust workspace tests, Python syntax validation, and repository policy in workflow `43016424733` on code commit `660dee7287376720d37d96dac939941fe26df7d6`. This is protocol/equation regression only. Full voltage-series comparisons against published group-level summaries remain; raw-trace and exact per-voltage experimental-target reproduction cannot be claimed from the inspected public deposit.


### NEURON 9.0.2 unit-check audit

- `nrnivmodl` compiles the original pure `k_human.mod` and `na_human.mod` unchanged, but emits the warning that assignment to GLOBAL `tadj` is not thread-safe.
- `modlunit` 9.0.2 on each unmodified file fails before reaching the kinetic equations: K line 82 and Na line 80, at the call `trates(v+vshift)`, because the procedure argument has no voltage-unit annotation.
- Temporary typed probes show the source `(/ms)` prefactors are incompatible with the voltage numerator in `trap0`; the equation requires `mV^-1 ms^-1`. The same probes expose the fallback's wrong dimensions/missing prefactor, the branch predicate's `v+th` versus the denominator's `v-th` singularity, the missing temperature unit in the Q10 exponent, and missing mV units on activation midpoint/slope parameters.
- With explicit function/procedure/return units, equation-consistent prefactors, the Q10 temperature interval, activation parameter units, and the commented-out `a*q` limit, temporary K+ and Na+ diagnostic copies pass `modlunit` 9.0.2. No deposited source file was modified.
- HumanJS already uses the equation-consistent prefactor unit and stable analytic limit. The source's original NMODL is not a unit-checked reference implementation; do not claim exact reproduction of its defective branch.


### Publisher supplementary Figure S5: verified series mapping and five-panel digitization

- Retrieved the official 13-page supplement from the new PMC AWS dataset. Size 1,468,232 bytes; SHA-256 `dfa1daaf4dd0e3979bac84b9cb8b1874c4514d40588969a21d7766a7f12f2a1d`.
- Rendered Figure S5 page 7 and verified the legend: red continuous line = human model; blue continuous line = mouse model; red open circles = human experimental means; blue crosses = mouse experimental means. The caption repeats panel label “I” for fast inactivation; the actual plotted panel is J.
- Recorded 50 experimental marker values across panels I, J, K, M, and N, separately identifying human and mouse: 46 manually digitized markers in panels I/J/K and four exact group means transcribed from `channel_tools.K_IV` for panels M/N. Seven research CSVs preserve PDF checksum, raster coordinates, axis calibration, marker identities, source constants, and model-replay references. These are group means, not raw cell-level observations; plot-reading uncertainty is not biological SD.
- Panel I activation: 7 voltages per species (−10 to +50 mV). At −10 mV, human ≈3.36 ms and mouse ≈7.76 ms; at +50 mV, human ≈0.58 ms and mouse ≈0.93 ms.
- Panel J fast inactivation: 6 voltages per species (0 to +50 mV). The Rust regression now reproduces the source post-peak current fit with fixed 450-ms slow component; human model fast time constants are ≈52.28, 41.56, 33.46, 27.26, 22.47, and 18.75 ms. RMSE against digitized human markers is ≈5.91 ms; this is source-model/data comparison, not biological validation.
- Panel K slow inactivation: 10 voltages per species (−30 to +60 mV); model `tau2` is fixed at 450 ms. Recomputed RMSE is 148.967 ms against human and 166.385 ms against mouse digitized means; only 2/10 human and 3/10 mouse residuals fall within the ±25-ms plot-reading estimate. The estimate is not biological SD/SEM.
- Panel J fast inactivation: the six human source-protocol model outputs have RMSE 5.914 ms against digitized human group means, with 3/6 residuals within ±2-ms plot-reading uncertainty. These are model-versus-marker residuals, not pixel-level curve digitization or a refit.
- Panel M fast recovery at −80 mV: exact `channel_tools.K_IV` constants are 228.52749381071555 ms (human) and 245.12119700268607 ms (mouse); their mean 236.82434540670081 ms exactly reproduces the pooled optimizer target.
- Panel N slow recovery at −80 mV: exact source constants are 1999.7294967866596 ms (human) and 3579.8563888349777 ms (mouse); their mean 2789.7929428108187 ms exactly reproduces the shared model slow-recovery constant. These are source-script experimental group means, not raw traces.
- Rust now reproduces the source `K_recovery` protocol: 2-ms hold, 5-s conditioning, five recovery voltages × ten delays, and 5-ms test pulse at 0.5-ms steps. It fits all 50 peak currents with the source two-component recovery equation. At −80 mV, current-fit references are ≈235.15 ms fast and ≈2803.29 ms slow, close to pooled human/mouse means 236.82 and 2789.79 ms; this is not a human-only target. A separate SciPy replay of the deposited mouse model gives nearly overlapping five-voltage curves; both human and mouse model references are preserved and validated in the recovery replay CSV.
- HumanJS parameterization caution: the source slow-recovery parameter 2789.7929 ms is a pooled human/mouse mean, ≈39.5% above the human-only mean 1999.7295 ms. The pooled fast mean is ≈3.6% above the human-only mean. Keep pooled values only for source-model reproduction; do not silently treat them as human-specific. Human-only reparameterization is blocked by missing per-cell CSVs/raw traces.
- `experiments/validate_wilbers_fig_s5_digitization.py` validates all 50 marker values, seven research CSVs, source hash, species/marker identity, voltage grids, axis-derived values, exact K_IV recovery constants, mouse pre-fit model-line comparison, five-voltage K_recovery model references, and now the J/K model-versus-group-mean residual summaries. CI executes the same validator.
- Panel I's ordinate is an apparent current-activation time constant fitted to the rising K current, not the direct activation-gate `mtau`. The deposited `channel_tools.K_IV` uses 34°C, 0.1-ms steps, a 20-ms hold at −140 mV, a 500-ms test pulse, and an exponential-plus-offset fit to the pre-peak current. The voltage-clamp helper uses the MOD default zero voltage shift; the separate −10-mV current-clamp shift is not applicable. The Rust regression now reproduces the source current-fit protocol at seven voltages, matching independent SciPy references within 0.01 ms; its RMSE against the digitized human group means is ≈0.145 ms. This is a source-equation/protocol regression, not biological validation. NEURON itself has not been executed.
- Figure-model provenance: both available `fit_k_hh_cma_*` scripts call `K_IV(cell)` before activation optimization. Human MOD defaults match the final fit; mouse default activation `Ra=0.0167/ms` differs from the later fitted `0.020746083599133762/ms`. Six unmarked blue model-line samples from the raster give pixel RMSE 5.35 against the pre-fit default current-fit curve and 36.06 against the post-fit curve. This strongly supports that the published mouse activation model line is pre-fit. The comparison is preserved in `research/HUMAN-L23-WILBERS-FIG-S5-I-MOUSE-MODEL-PREFIT-CHECK.csv`; no separate final-figure generator is deposited.
- Main-text K+ summary values: activation V1/2 human −3.0 ± 5.9 mV (n=13) vs mouse −7.9 ± 6.0 mV (n=29), P=0.02; inactivation V1/2 human −52.7 ± 6.0 mV (n=11) vs mouse −65.0 ± 5.3 mV (n=26), P<10⁻⁶; resting-potential availability human 0.94 ± 0.05 vs mouse 0.86 ± 0.06. Human K+ currents activate faster at lower voltages; fast/slow inactivation and recovery time constants were described as similar between species, although human currents recover to a larger proportion of initial amplitude.
- Remaining: digitize the plotted model-line pixels in panels J/K/M/N (the new J/K residual analysis compares model outputs to marker means, not raster line coordinates), inspect any un-deposited post-fit Figure S5 generator, and obtain the missing raw K tau CSVs/traces. The exact Dataverse `Experimental means/k_tau_*.csv` files and raw per-cell K+ voltage-clamp traces remain absent. This is not raw-trace reproduction or biological validation.
- Current-clamp conductance-density provenance was further audited from Dataverse `cc_tools.py` and `currentclamp.py`: the optimizer minimizes equally weighted normalized squared errors in AP amplitude/upstroke/downstroke against 50:50 human/mouse median targets, with Powell bounds 20–150 and a ×4 penalty unless exactly one AP is present. The 34°C, 10-µm section, `Ra=200 Ω·cm`, `cm=1`, `Rm=10,000 Ω·cm²`, reversal offsets, −10-mV channel shifts, rheobase procedure, and 1.5× rheobase 3-ms pulse were recorded in the research audit. The outcome extractor and `AP1comparison.csv` exact target values were not retrieved, so the fit is not independently reproducible yet.

## Not yet implemented

- A scientifically accepted/validated somatic-patch-equivalent or anatomical soma/AIS spike model.
- A configurable default of 10,000 spiking neuron units or any population/network runtime.
- Explicit presynaptic calcium/release machinery, stochastic vesicle fusion, glutamate-cleft dynamics/uptake, molecular receptor-state kinetics, and inhibitory synapses.
- Dendritic morphology/spines/cable filtering, multicompartment integration, populations, and connected networks.
- Long-term synaptic plasticity or learning.
- Runtime save/restore/checkpointing or safe interruption/resumption.
- Rust-native multi-threaded simulation execution.
- JSON model-definition loading and schema validation.
- Python developer package, stable C ABI, C++ wrapper, or integrated WGSL backend.

These remain requirements or future objectives, not current capabilities.

## Next milestone

Keep the spike-capable code provisional. The source-protocol J/K model-versus-marker residuals are now quantitatively recomputed in CI; next extract actual model-line pixel coordinates for J/K/M/N, keeping those distinct from experimental-marker residuals. Preserve the missing raw-trace/Dataverse CSV limitation: the deposited data statement is satisfied by the published summary/model materials, but the inspected v3.0 inventory does not contain the specific K tau CSVs or raw per-cell voltage-clamp traces needed for independent refitting. The pooled recovery constants must not be treated as human-only parameters. The voltage-clamp helper uses zero shift; do not import the separate −10-mV current-clamp shift. Then independently verify current-clamp conductance-fit objective and setup, temperature semantics, and the source rate-prefactor dimensional convention before considering any promotion. Keep the single-compartment preparation-equivalent distinct from an anatomical soma/AIS model. Do not claim biological validation from software tests or external model reproduction.

### Current-clamp conductance-grid follow-up (2026-11-11)

The recovered Dataverse fit_gbar_na_k.py confirms a 20×20 sweep of independent human Na and K kinetic ratios (20 values each from 0 to 1), with 400 calls to the already-audited cross-species-midpoint Powell fit. It writes gbar_na.csv and gbar_k.csv; currentclamp.py separately fits all-human, all-mouse, and 0.5/0.5 mixtures and uses the fitted-density interpolation path for kinetic-ratio heatmaps and 200-AP sweeps. The initial conductance values in that script are optimizer starting values, not fit outputs. The actual interpolation CSVs remain unretrieved, and exact provenance of HumanJS's 114.48/29.05 pS/µm² preset values is still unresolved. A targeted source extraction did not recover get_outcomes_full; feature windows/thresholds remain unknown. No conductance refit or biological promotion is justified.

