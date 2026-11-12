# HumanJS — current status

**As of:** 2026-11-12  
**Stage:** two foundational Rust CPU mechanisms plus one exploratory, unaccepted human L2/L3 single-compartment spike-capable mechanism. HumanJS is not a whole-brain simulator.

## Canonical repository and live state

- Repository: `codexclai/HumanJS`, public, default branch `main`.
- Live verification on 2026-11-12: default branch `main`; HEAD `2c47917b407052c4cbe768ddda22ea08406c5462`; complete 67-entry tree, not truncated; exactly one branch (`main`); zero open issues and zero open pull requests.
- Latest code/test change remains `adfacd7f8d3f8b6e7088a00507af4e51832a80d8` (paired human/mouse K+ fixed-component current-fit references and five-voltage recovery replays). Latest research evidence commit: `2c47917b407052c4cbe768ddda22ea08406c5462`, which adds a versioned Dataverse manifest cross-check and disambiguates the cited Mainen ModelDB precedent.
- GitHub Actions run `43128024657` passed on exact HEAD `2c47917b407052c4cbe768ddda22ea08406c5462`: https://github.com/codexclai/HumanJS/actions/runs/43128024657. `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace --locked`, Python experiment-runner syntax, `python3 experiments/validate_wilbers_fig_s5_digitization.py`, `python3 experiments/validate_wilbers_current_clamp_grid.py`, and `python3 .github/scripts/repository_policy.py` all passed. These are software/evidence-integrity checks, not biological validation.
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
- Rust now reconstructs the K+ fixed-450-ms post-peak current-fit model for both human and mouse channel parameters (six fast-inactivation voltages per species) and replays the two-component recovery current protocol at all five recovery voltages for both species. The mouse model uses pure `k_mouse.mod` defaults including pre-fit `Ra=0.0167/ms`; its five-voltage SciPy references are checked by the Rust workspace tests. These are source-equation current-fit reconstructions, not gate time constants or biological validation.
- **Figure S5J/K source-path limitation:** the deposited `channel_tools.get_tau_inact_double_fixedtau2` helper passes five `curve_fit` initial values to a four-parameter function, catches the resulting error, and returns NaNs. The available 65-file dataset has no separate final Figure S5 generator. Accordingly, the J/K Rust fit values and marker residuals are transparent reconstructions, not exact reproductions or pixel-level matches of the published red/blue model lines. The actual J/K model-line source remains unresolved.
- Remaining: quantitatively digitize model-line pixels in J/K/M/N and locate the non-deposited figure-generation path or export inputs; obtain the missing raw K tau CSVs/traces. The exact Dataverse `Experimental means/k_tau_*.csv` files and raw per-cell K+ voltage-clamp traces remain absent. This is not raw-trace reproduction or biological validation.
- Current-clamp fit provenance is now fully traced: `get_outcomes_full` and the three CC0 CSVs are retrieved and checksum-verified. The all-human kinetic grid endpoint matches the Rust 114.48/29.05 pS/μm² preset after rounding. The optimizer targets cross-species midpoint medians, not human-only AP medians. The original NEURON/SciPy optimizer was not rerun.

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

Keep the spike-capable code provisional. The exact 65-file Dataverse v3.0 manifest has now been rechecked against the live API and an independently preserved metadata export: the named K tau CSV inputs, `data_fig5.xlsx`, raw K voltage-clamp NWB traces, and a separate S5 plot generator are not in that released inventory. The earlier bioRxiv ModelDB/GitHub URLs are unfinished placeholders; the final paper's ModelDB 8210 citation resolves to the separate Mainen et al. (1995) neocortical model, not the Wilbers authors' plotting/data repository. The HumanJS research record now captures this source reconciliation and the exact inventory provenance. The remaining evidence action is to request the original S5 J/K/M/N figure-generation state and missing per-cell/raw K recordings from the corresponding authors, or an explicit statement that those inputs are unavailable. Independently, digitize any visible model-line pixels only as raster-derived estimates, separate from marker means and not a substitute for source code or raw traces. Do not infer that data were withheld. Keep pooled human/mouse recovery constants distinct from human-only parameters; the voltage-clamp helper uses zero shift, not the separate −10-mV current-clamp shift. Reconsider the provisional spike mechanism only after the current-clamp objective, temperature semantics, source dimensional issues, and relevant human validation targets are independently satisfied. Keep the single-compartment preparation-equivalent separate from anatomical soma/AIS modeling. Do not claim biological validation from software tests or external model reproduction.

### Current-clamp conductance-grid follow-up (2026-11-11)

The deposited 20×20 conductance matrices and AP1 comparison CSV are now retrieved and checksum-verified. The all-human (Na ratio=1, K ratio=1) grid corner is exactly 114.47654963753565 pS/μm² Na and 29.045736151752504 pS/μm² K, rounding to the HumanJS preset. The helper defines the feature extraction. All target, optimizer, and feature details are in the final research audit.

### Current-clamp source completeness finding (2026-11-11)

The complete `cc_tools.py` does define `get_outcomes_full` and `get_outcomes`; the previous contrary result came from incomplete extraction and is superseded. The source data and grid are now present in the repository, with a CI validator for file identity, target medians, axes, orientation, bounds, and endpoints.


## 2026-11-12 — current-clamp dataset inventory correction

The 65-file inventory lists the three unrestricted current-clamp CSVs. Their contents were later retrieved through the signed SURF object-store redirect and verified against Dataverse metadata; see the subsequent resolution entry.

The complete inventory lists only `cc_tools.py`, `currentclamp.py`, and `fit_gbar_na_k.py` as Python source in `Figures5_6/Current_clamp`; no separate outcome-extractor module is listed. The complete retrieved `cc_tools.py` does define `get_outcomes_full`; the earlier conclusion was caused by an incomplete extraction and is superseded by the later resolution entry. Numeric CSV contents and the exact source table entry for the HumanJS 114.48/29.05 pS/µm² preset remain unverified. No parameter change was made; the single-compartment spike mechanism remains exploratory.


## 2026-11-12 — Wilbers current-clamp fit provenance resolved

The Dataverse current-clamp source helper and all three unrestricted CSVs were retrieved through the documented access API and verified byte-for-byte against Dataverse SHA-1 metadata:

- `AP1comparison.csv` (318555): 846 bytes, SHA-1 `85fea00fea374ed0595d032180a798371d96aa4d`.
- `gbar_na.csv` (318551): 8,224 bytes, SHA-1 `ac2f1b3ae108e8f256e53b0d85c4e0b353eb173a`.
- `gbar_k.csv` (318552): 8,037 bytes, SHA-1 `6867798db8a5a2a77a66bb72b7cae77590ff0247`.
- `cc_tools.py` (318557): 10,448 bytes, SHA-1 `f64162577fa5dd86892b46570d597e58e083a02b`.

The complete helper **does define** `get_outcomes_full` and `get_outcomes`; the earlier missing-extractor finding was an incomplete-extraction error and is superseded. The source feature extractor uses 50-mV prominence peak detection, a 40-mV/ms pre-maximum-slope threshold criterion, and mean dV/dt over the 30–70% rising and 70–30% falling AP-amplitude windows. The density objective uses equally weighted normalized squared residuals for peak voltage, upstroke, and downstroke, with targets equal to the 50:50 human/mouse median average; Powell starts at [95,65], bounds each conductance to [20,150], and multiplies the objective by four unless exactly one AP is detected.

The all-human kinetic endpoint (Na ratio=1, K ratio=1) is the top-right cell of both 20×20 matrices: Na 114.47654963753565 and K 29.045736151752504 pS/μm². These round exactly to the HumanJS preset 114.48/29.05. This resolves its source-grid provenance. “All-human” refers to kinetic mixture, not human-only fitting targets: the objective remains cross-species midpoint calibrated. The exact source data are preserved as three CC0 research CSVs and validated by `experiments/validate_wilbers_current_clamp_grid.py`, now wired into CI.

The original NEURON/SciPy optimizer was not rerun because NEURON, SciPy, and NumPy are unavailable in the execution environment. The deposited outputs are checksum-verified, but no independent optimizer reproduction, raw-trace reproduction, or biological validation is claimed. The spike mechanism remains a provisional lumped single-compartment model.


The human/mouse mixture semantics were additionally verified against the unrestricted `na_mouse.mod` (file 318561, SHA-1 `84cc161f3c38fc71d399cc998d91f0c60cbd2df1`) and `k_mouse.mod` (318560, SHA-1 `8b1761352a44cc57c29f3345242a4060186d84eb`): human channel currents scale by the ratio and mouse channel currents by its complement, sharing the same fitted total conductance. Thus ratio 1 truly selects human kinetics only. The source Na mechanism applies Q10 to both gate rates and maximal conductance; the K mechanism applies it to gate rates only, matching the Rust implementation. Current-clamp CSV validation now checks both Dataverse SHA-1 and local SHA-256, and cross-checks the rounded all-human endpoint against the Rust preset literals. Workflow 43124314513 passed on exact HEAD `c73a90270cc92979add481b00856ea2848eea98c`, including fmt, Clippy, all Rust workspace tests, both research validators, Python syntax, and repository policy.


### 2026-11-12 — versioned K-data inventory and ModelDB citation resolved

- Rechecked the single released DataverseNL version (v3.0; released 2022-12-13; CC0-1.0) through the version-specific API. Its live files endpoint reports `totalCount=65`.
- Cross-checked all 65 filename entries in the third-party DANS Labs metadata export, pinned to `Dans-labs/odissei-portal-exp` commit `ac75eb2a48cc0bf876ec451ed82d68c101326540`. This is a metadata mirror only. Neither manifest contains the named `Experimental means/k_tau_*.csv` inputs, `data_fig5.xlsx`, `.nwb` raw recordings, or a separate final Figure S5 plot generator.
- Verified the preprint v2 ModelDB/GitHub source URLs are explicit unfinished placeholders. In the final article, ModelDB 8210 is the Mainen et al. (1995) “Spike Initiation in Neocortical Pyramidal Neurons” model; it is not the Wilbers model-code deposit. The final data statement points to the Dataverse DOI.
- No parameter or runtime code was changed. The single-compartment Na+/K+ model remains exploratory and unaccepted. The current public data allow source/model protocol audits and selected summary checks, not the missing trace-level K refit or exact S5 J/K plotting reproduction.
- Latest research commits: `2e0b0cc3b83aa43ec4a331355d5bae2bf1b5a108` (manifest/source availability) and `2c47917b407052c4cbe768ddda22ea08406c5462` (ModelDB accession identification). Latest CI run `43128024657` passed on the latter.


### 2026-11-12 — Wilbers corresponding-author route verified

The final Science Advances publisher page was queried directly and confirms the corresponding-author contacts Huibert D. Mansvelder (h.d.mansvelder@vu.nl) and Natalia A. Goriounova (n.a.goriounova@vu.nl). Its data-availability statement points to Dataverse DOI 10.34894/L5J0SD. The v3.0/65-file inventory audit above still applies: the specific K kinetic CSVs, data_fig5.xlsx, raw K voltage-clamp traces, and a separate final Figure S5 plotting generator are not listed. This gives us a legitimate, non-accusatory route to request the missing provenance and an explicit availability statement. No message has been sent and no new experimental data have been received. The HumanJS spike-capable mechanism remains exploratory and unaccepted.


### 2026-11-12 — Figure S5 model-line raster estimates

The official 13-page supplement was fetched from the public PMC open-access object store, hash-verified, and page 7 rendered at 300 dpi. Added 23 raster-derived centerline samples for panels J/K/M/N in research/HUMAN-L23-WILBERS-FIG-S5-MODEL-LINE-RASTER.csv. The samples estimate the combined visible red/blue traces because the curves overlap/interleave at the available raster resolution; they are not species-separated fits, experimental observations, or substitutes for the absent source plotting state/raw recordings. The Figure S5 validator now checks this CSV's provenance, grids, units, coordinate bounds, uncertainties, ranges, and trends. Scientific status remains exploratory/unaccepted; no biological validation claim.


The panel-J raster axis was refined against the six existing marker centers. Its six inter-marker model-line estimates now agree with the existing human and mouse equation-level current-fit reconstructions at about 0.36 ms RMSE; because the two plotted species lines overlap, this is a consistency check and cannot identify the sampled species. The panel-K raster is approximately 444.8 ms (near the fixed 450-ms component), and panel-N is approximately 2.78–2.79 s (near the pooled slow-recovery constant). Panel M remains a raster-only estimate pending an explicit method-equivalence comparison with the Rust K_recovery replay. All values remain raster-derived estimates, not raw measurements or biological validation.


### Verification correction — Figure S5 raster validator

The first CI run after the refined panel-J samples (run 43130214819) failed only because the validator's lower plotted-range bound was set to 18 ms while the final 55-mV sample is 17.51 ms. The raster point was retained; the validator bound was corrected to 17 ms. The follow-up run 43130293760 passed all workflow steps on its exact commit. This was a test-boundary correction, not a change to scientific observations or model parameters.


### 2026-11-12 — pre-migration archive reconciliation

The owner supplied `HumanJSProject.zip` for a one-time audit. It was inspected read-only; SHA-256 `0deb7789a8df444ea6a4e957dc63520cf6e786c18887286c3a31a319f61eccdf`, 422 ZIP entries / 375 files / 26,045,082 uncompressed bytes. It contains the discontinued Node.js/JavaScript implementation (16 `src/` files), 28 architecture notes, 143 experiment documents, 92 raw simulator-result JSONs, three test files, and a large historical scientific research dossier.

**Disposition:** archive excluded from GitHub and not needed as a future-session dependency. No legacy implementation, old runtime result, or unreviewed research bundle was imported. The previous simulator's outputs are not biological evidence and cannot be treated as results from the current Rust core. The historical architecture and prompts contain designs superseded by current owner requirements; current Rust/WGSL/Python/C/C++ direction remains authoritative. The archive contains potentially useful human-evidence citations and experiment protocols, but these require source-level revalidation and independent Rust reproduction before influencing current mechanisms. This was an inventory and documentation triage, not a line-by-line revalidation of every legacy source or the 715-kB research dossier. See ADR-017 for the policy and scope.


### Figure S5 panel-M recovery comparison resolved (2026-11-12)

The released Dataverse source path is now traced: the human and mouse fitting scripts call `K_IV(cell)` before optimization, using the pure `k_human.mod` / `k_mouse.mod` mechanisms. `channel_tools.K_IV` calls `K_recovery`; its first biexponential current-fit component (`tau1`) is panel M and the second (`tau2`) is panel N. The mouse call uses pre-fit `Ra=0.0167/ms`, not the later optimizer value. The source replay and exact file IDs/checksums are documented in the research CSV header and research record.

Panel M's four raster samples were recalibrated against the printed 300/200-ms ticks: 134.36, 193.41, 304.46, and 350.03 ms at −87.5 to −72.5 mV. Compared against the linearly interpolated pooled human/mouse K_IV `tau1` source-output curves, RMSE is 2.01 ms and maximum absolute residual 3.32 ms. This is a raster/polyline consistency check, not an exact reproduction of the original NEURON run, raw data, or biological validation. The panel-M validator now checks RMSE ≤3 ms and maximum residual ≤5.1 ms.

Two intermediate CI runs (43131449785 and 43131513456) caught the new 5-pixel uncertainty values because the validator only permitted 3 or 4 pixels. The data were retained; the validator was corrected to admit 5-pixel reading uncertainty and panel-M's calibrated range. Final run 43131570918 passed all workflow steps on its exact commit. No scientific values or model parameters were adjusted to obtain the pass.


### 2026-11-12 — single-compartment acceptance audit

- Directly fetched and inspected the deposited current-clamp hybrid sources: Na file 318563 (na_human.mod) and K file 318566 (k_human.mod), plus cc_tools.py (file 318557).
- Confirmed source trates(v+vshift) and helper vshift = −10 mV; the Rust V−10 mV effective gating voltage is correct. Initial gate values, Q10 placement, K three-fraction gating, current-density units, geometry, capacitance, leak and reversal potentials map to the author helper.
- Added a Rust regression for shift polarity and initialization. It does not turn the exploratory model into an accepted biological mechanism.
- Remaining gates: corrected trap0 is not exact NMODL runtime reproduction; K slow recovery is pooled human/mouse and K fit quality is limited; conductance fit targets cross-species AP medians; no spatial AIS; RK4-vs-cnexp trajectory equivalence is untested; current spike smoke test is not the source rheobase/1.5× protocol.
- Full audit and next reproduction step are in research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md. Preserve the exploratory/unaccepted status.


### Verification correction — source-mapping regression formatting

Workflow run 43133844647 failed at the Rust formatting check only. The failure was the exact rustfmt layout of the newly added current-clamp voltage-shift/initial-state regression; all subsequent workflow checks were skipped, so no compile/test result was obtained in that run. The code was reformatted to the CI rustfmt output without changing its assertions or model behavior. A new workflow run on the correction commit is required before calling this change verified.
