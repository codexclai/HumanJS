# HumanJS — current status

**As of:** 2026-11-11  
**Stage:** two foundational Rust CPU mechanisms plus one exploratory, unaccepted human L2/L3 single-compartment spike-capable mechanism. HumanJS is not a whole-brain simulator.

## Canonical repository and live state

- Repository: `codexclai/HumanJS`, public, default branch `main`.
- `main` is the only branch; the live branch listing returned exactly `main`.
- No open issues or pull requests were returned by live checks.
- Latest source/code commit: `660dee7287376720d37d96dac939941fe26df7d6`. Latest research audit update: `8944ad147ece6aa33d73efdfdc5ab985b919407a`.
- GitHub Actions run `43016424733` passed on exact code head `660dee7287376720d37d96dac939941fe26df7d6`: https://github.com/codexclai/HumanJS/actions/runs/43016424733. Rust formatting, Clippy, Rust workspace tests (including the 50-condition K+ recovery grid), Python syntax validation, and repository policy all passed.
- This chat did not complete a fresh local clone because network DNS resolution failed. No local Rust test run is claimed.

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
- Panel K slow inactivation: 10 voltages per species (−30 to +60 mV); model `tau2` is fixed at 450 ms. This gives RMSE ≈149 ms against human and ≈166 ms against mouse digitized means, consistent with the paper's caveat about poor K+ inactivation reproduction.
- Panel M fast recovery at −80 mV: exact `channel_tools.K_IV` constants are 228.52749381071555 ms (human) and 245.12119700268607 ms (mouse); their mean 236.82434540670081 ms exactly reproduces the pooled optimizer target.
- Panel N slow recovery at −80 mV: exact source constants are 1999.7294967866596 ms (human) and 3579.8563888349777 ms (mouse); their mean 2789.7929428108187 ms exactly reproduces the shared model slow-recovery constant. These are source-script experimental group means, not raw traces.
- Rust now reproduces the source `K_recovery` protocol: 2-ms hold, 5-s conditioning, five recovery voltages × ten delays, and 5-ms test pulse at 0.5-ms steps. It fits all 50 peak currents with the source two-component recovery equation. At −80 mV, current-fit references are ≈235.15 ms fast and ≈2803.29 ms slow, close to pooled human/mouse means 236.82 and 2789.79 ms; this is not a human-only target.
- Added `experiments/validate_wilbers_fig_s5_digitization.py`; it passed in a clean temporary workspace, validating all 50 marker values, source hash, species/marker identity, voltage grids, axis-derived values, exact K_IV recovery constants, and the mouse model-line pre-fit comparison. CI executes the same validator.
- Panel I's ordinate is an apparent current-activation time constant fitted to the rising K current, not the direct activation-gate `mtau`. The deposited `channel_tools.K_IV` uses 34°C, 0.1-ms steps, a 20-ms hold at −140 mV, a 500-ms test pulse, and an exponential-plus-offset fit to the pre-peak current. The voltage-clamp helper uses the MOD default zero voltage shift; the separate −10-mV current-clamp shift is not applicable. The Rust regression now reproduces the source current-fit protocol at seven voltages, matching independent SciPy references within 0.01 ms; its RMSE against the digitized human group means is ≈0.145 ms. This is a source-equation/protocol regression, not biological validation. NEURON itself has not been executed.
- Figure-model provenance: both available `fit_k_hh_cma_*` scripts call `K_IV(cell)` before activation optimization. Human MOD defaults match the final fit; mouse default activation `Ra=0.0167/ms` differs from the later fitted `0.020746083599133762/ms`. Six unmarked blue model-line samples from the raster give pixel RMSE 5.35 against the pre-fit default current-fit curve and 36.06 against the post-fit curve. This strongly supports that the published mouse activation model line is pre-fit. The comparison is preserved in `research/HUMAN-L23-WILBERS-FIG-S5-I-MOUSE-MODEL-PREFIT-CHECK.csv`; no separate final-figure generator is deposited.
- Main-text K+ summary values: activation V1/2 human −3.0 ± 5.9 mV (n=13) vs mouse −7.9 ± 6.0 mV (n=29), P=0.02; inactivation V1/2 human −52.7 ± 6.0 mV (n=11) vs mouse −65.0 ± 5.3 mV (n=26), P<10⁻⁶; resting-potential availability human 0.94 ± 0.05 vs mouse 0.86 ± 0.06. Human K+ currents activate faster at lower voltages; fast/slow inactivation and recovery time constants were described as similar between species, although human currents recover to a larger proportion of initial amplitude.
- Remaining: compare the reproduced source model curves for panels J/K/M/N directly against raster line coordinates, inspect any un-deposited post-fit Figure S5 generator, and obtain the missing raw K tau CSVs/traces. The exact Dataverse `Experimental means/k_tau_*.csv` files and raw per-cell K+ voltage-clamp traces remain absent. This is not raw-trace reproduction or biological validation.
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

Keep the spike-capable code provisional. Compare the reproduced source model curves for panels J/K/M/N directly against raster line coordinates, trace any un-deposited post-fit figure generation, and obtain the missing raw K tau CSVs/traces. Panels I/J current-fit replay and the fixed K slow-inactivation component are now covered by Rust regression; the published mouse activation line strongly matches pre-fit defaults. The voltage-clamp helper uses zero shift; do not import the separate −10-mV current-clamp shift. Preserve the missing raw-trace/Dataverse CSV limitation. Then independently verify current-clamp conductance-fit objective and setup, temperature semantics, and the source rate-prefactor dimensional convention before considering any promotion. Keep the single-compartment preparation-equivalent distinct from an anatomical soma/AIS model. Do not claim biological validation from software tests or external model reproduction.
