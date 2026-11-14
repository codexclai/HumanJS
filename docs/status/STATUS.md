# HumanJS — current status

**As of:** 2026-11-14
**Stage:** two foundational Rust CPU mechanisms plus one exploratory, unaccepted human L2/L3 single-compartment spike-capable mechanism. HumanJS is not a whole-brain simulator.

## Canonical repository and live state

- Repository: codexclai/HumanJS, public, default branch main.
- Live verification immediately before this status refresh: main HEAD `2be947d96a7e079bb05b799e6a01fa704acd1004`; complete 120-entry recursive tree (`truncated=false`); exactly one branch (`main`); zero open issues and zero open pull requests. Workflow [43568457823](https://github.com/codexclai/HumanJS/actions/runs/43568457823) passed on that exact HEAD with all 36 job steps successful (41 core Rust unit tests, 3 synapse integration tests, 6 passive-membrane integration tests, 32 Python experiment scripts parsed, 51 Python tests, original Wilbers NEURON 9.0.2 Na/K replay and validation, every established K_IV reference comparison, the new +55 mV fixed-tau1 0.1–120 ms profile and strict 39-column expected-summary comparison, and repository policy).
- Workflow [43469283136](https://github.com/codexclai/HumanJS/actions/runs/43469283136) completed successfully on exact HEAD 5d5e180bc5068f647edc040de39481801be52a0e: cargo fmt --all -- --check, cargo clippy --workspace --all-targets -- -D warnings, Rust tests (41 unit, 3 synapse integration, 6 passive-membrane integration), syntax for 28 Python experiment scripts, 43 Python tests, all Wilbers data validators, all five original NEURON 9.0.2 Na/K source protocol replays and validators, the 192-fit K_IV multi-start diagnostic, the source-bound/extended/local tau profiles, 4,890-sample residual validation, the signed three-exponential diagnostic at -70 mV, the new three-voltage residual export/profile/expected-summary comparison, and repository policy. The run passed on the exact pushed main commit. Two intermediate CI failures while integrating the new test were corrected: a clock-misalignment fixture that made a uniform clock shift instead of a real sample mismatch, and roundoff residue in a mathematically collapsed positive-control comparison. Neither change weakened a scientific or source acceptance criterion.
- Human sodium source coverage is retained separately as ideal-command equation replay and original NEURON/VClamp execution. The source Na_IV current-density gate passes 19/19 test voltages and the joint-fit R2>0.95 test passes 17/19. Na_IV_inact covers 30 conditioning voltages (Boltzmann Vhalf/slope -68.251977/8.472251 mV); Na_recovery covers 156 paired-pulse runs, with finite source apparent recovery taus at all 13 voltages.
- Original human potassium source execution is recorded. K_IV covers all 34 voltage commands, with 32 finite activation fits and 27 finite source fast-inactivation fits; its source Boltzmann Vhalf/slope are -2.666291/14.516246 mV (activation) and -50.891061/12.286798 mV (inactivation). K_recovery covers all 50 paired-pulse traces and produces finite fast/slow current-fit outputs at all five recovery voltages.
- The K_IV source helper get_tau_inact_double_fixedtau2 was rechecked against the exact Dataverse file: it is a four-free-parameter curve fit with four starting values and fixed tau2=450 ms. Earlier notes alleging a five-versus-four arity error were wrong and are corrected. The K_IV fast-inactivation fit is initialization-sensitive on identical model-current samples; six starts at -70 mV all pass the source R2 gate but return 186.610-213.819 ms, with maximum accepted within-voltage spread 111.420 ms at -85 mV. The source p0 places a current-density difference into the tau1 slot and est1=30 into the a2 amplitude slot. Full source-fit sensitivity methods remain in research/HUMAN-L23-WILBERS-K-IV-FIT-SENSITIVITY.md.
- New adjacent-voltage residual result: the exact source post-peak waveform is now preserved for -75/-70/-65 mV, and the signed, non-source short exponential reduces full-waveform RMSE by 80.386%/79.023%/77.371%, respectively. First-10-ms RMSE falls by 94.278%/94.034%/93.789%; after-10-ms RMSE falls by 27.728%/27.614%/27.433%. The fitted short time constant is 1.111/1.2335/1.384 ms. The extra coefficient is negative at all three commands and only 0.0391%/0.0636%/0.1060% of each waveform's peak. Constraining it to be nonnegative makes it collapse to zero at the signed optimum. This supports generalization of the descriptive model-residual correction across these three nearby model commands only; it does not identify a biological current component or channel time constant. Results and source provenance are preserved in research/HUMAN-L23-WILBERS-K-IV-MULTIVOLTAGE-RESIDUAL-SUMMARY.csv.
- Research records and per-protocol results are under research/; executable runners, protocol tests and output validators are under experiments/. Raw human K NWB current traces and individual K kinetic CSVs remain absent from the inspected DataverseNL v3.0 inventory. No raw human current-trace refit or biological validation is claimed. The exploratory spike-capable single-compartment model remains unaccepted.
- The current environment could not resolve github.com for a local clean clone, so no local Cargo command is claimed. The exact remote main commit was verified by GitHub Actions as above.


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



### Temperature-contract regression coverage (2026-11-13)

Two new Rust tests cover the source temperature contract across 20, 25, 30, 34 and 37°C:

- `channel_temperature_scaling_matches_deposited_rate_contract` checks Na and K Q10 factors using distinct reference temperatures (25°C and 34°C respectively), inverse scaling of all represented fast gate time constants, temperature-invariant steady states, and the two fixed K slow-gate branch constants.
- `temperature_adjustment_scales_sodium_conductance_but_not_potassium_or_leak` checks current balance at a fixed initial voltage and the same steady-state gates. Na current follows the 25°C-referenced Q10 multiplier; K current and leak remain unchanged because their conductances are not multiplied by `T_adj` in the deposited equations.

At the model's 34°C current-clamp setting, these source conventions yield Na `2.3^0.9 ≈ 2.11619` and K `1.0`. The test grid validates equation placement and software behavior only; it does not validate the temperature range biologically or imply that either channel mechanism is accepted. Source provenance and limitations are documented in `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`.



## Wilbers human sodium voltage-clamp audit

The exact source/protocol and data caveats are documented in `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`. In brief:

- Pure `Na_IV`/ `Na_IV_ss`: 25°C; 0.01-ms step; 2-ms holding at −120 mV; 10-ms test voltages −80…+10 mV in 5-mV steps; source voltage shift 0 mV.
- `Na_IV_inact`: 25°C; 0.005-ms step; 1 ms at −70 mV; 50-ms conditioning voltages −105…−47 mV in 2-mV steps; 10-ms test at −10 mV. Rust tests check the analytic gate progression through the first 5 ms of the test segment.
- HumanJS adds two software regressions for these gate command sequences. They check the exact parameterized exponential gate equations; they do not reproduce the source's whole-cell current amplitude, curve-fit machinery, or raw experimental current traces.
- Figure 3 source filters are reproduced in `research/HUMAN-L23-WILBERS-FIG3-NA-IV-TAU-SUMMARY.csv`: 40 voltage/species groups of precomputed `iv_tau_m/h` summaries, with the original workbook and plotting/statistics script hashes. These are current-derived fitted fields, not microscopic gate taus. The empirical workbook grid (−65…+55 mV) differs from the source model Na_IV grid (−80…+10 mV).
- No raw NWB Na voltage-clamp traces were present in the inspected Dataverse v3.0 65-file inventory. This work does not claim raw-trace reproduction, independent refitting, or biological validation.

### Na_IV apparent-current fitting replay

The normalized model-side replay and its per-voltage record are documented in research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md and stored in research/HUMAN-L23-WILBERS-NA-IV-CURRENT-FIT-REPLAY.csv. The runner and validator are experiments/replay_wilbers_na_iv_current_fit.py and experiments/validate_wilbers_na_iv_current_fit_replay.py; both are part of CI.

The ideal-command equation replay and the original NEURON/VClamp source execution are both recorded separately. The ideal-command runner derives local current density from the deposited default gbar and ena, so it can evaluate the source min(ina)<−1e-6 mA/cm² gate; all 19 command voltages pass this selection. Seventeen of 19 pass joint-fit R²>0.95 (−80 and −75 mV fail). The NEURON VClamp run has the same 19/19 current-density and 17/19 fit acceptance counts, but its finite-controller waveform shifts some apparent fit values. In both paths the source returns the first joint-fit parameter as apparent tau_m and retains the preliminary post-peak decay estimate as tau_h. These are apparent current-waveform constants, not microscopic gate taus.


## Original Wilbers human potassium voltage-clamp source execution

The pure human `k_human.mod` was checksum-verified and compiled unchanged in NEURON 9.0.2. The runner also verifies the original `channel_tools.py` and `fit_k_hh_cma_human.py`, applies the source caller's 10-µm section, Ra=200, cm=1, ek=−101 mV, and its `th_inact_inf=-52.6 mV` / `q_inact_inf=13.09 mV` overrides. It retains the pure mechanism's default gbar=40 pS/µm², Q10=2.3 at 34°C, and built-in VClamp settings.

- K_IV executes 34 voltages (−110…+55 mV, 5-mV step) with the source 20-ms −140-mV hold, 500-ms test, 50-ms +60-mV inactivation segment and 100-ms return. There are 32 finite source activation fits and 27 finite source fast-inactivation fits. Source Boltzmann activation Vhalf/slope: −2.666291/14.516246 mV; inactivation: −50.891061/12.286798 mV. The slow inactivation component is held at 450 ms.
- K_recovery executes five recovery voltages × ten source delays (4…8,464 ms), i.e. 50 paired-pulse traces. All five voltages produce finite fast and slow source double-exponential current-fit components.
- The K_IV helper `get_tau_inact_double_fixedtau2` is now verified as a four-parameter fit with four initial values and fixed tau2=450 ms. The earlier assertion that it passes five initial values and is arity-broken was incorrect; it is retracted. The K-IV nonlinear fast tau remains optimizer-sensitive across hosted repeats: at −70 mV it changed from 213.819 to 183.493 ms although current maxima and Boltzmann outputs were unchanged. The validator checks availability and source bounds instead of asserting exact nonlinear tau repeatability.
- The source protocols and current execution records are in `experiments/replay_wilbers_k_iv_neuron.py`, `experiments/validate_wilbers_k_iv_neuron_replay.py`, and the two `research/HUMAN-L23-WILBERS-K-*-NEURON-REPLAY.csv` files. Workflow [43452329852](https://github.com/codexclai/HumanJS/actions/runs/43452329852) passed these runners/validators and the full Rust/Python/repository suite.

No raw human K NWB traces or individual K tau CSV targets were in the inspected Dataverse v3.0 inventory. These records verify original model/source execution, not raw experimental fitting or biological validation. Human-only kinetic estimates remain blocked by the unavailable raw/per-cell K evidence; do not substitute pooled human/mouse recovery targets.

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
- Panel I's ordinate is an apparent current-activation time constant fitted to the rising K current, not the direct activation-gate `mtau`. The deposited `channel_tools.K_IV` uses 34°C, 0.1-ms steps, a 20-ms hold at −140 mV, and a 500-ms test pulse. The original pure-human K NMODL and K_IV/K_recovery source helpers have now been executed in NEURON 9.0.2 with the fitting caller setup and built-in VClamp. This is model/source execution, not empirical current refitting or biological validation.
- Figure-model provenance: both available `fit_k_hh_cma_*` scripts call `K_IV(cell)` before activation optimization. Human MOD defaults match the final fit; mouse default activation `Ra=0.0167/ms` differs from the later fitted `0.020746083599133762/ms`. Six unmarked blue model-line samples from the raster give pixel RMSE 5.35 against the pre-fit default current-fit curve and 36.06 against the post-fit curve. This strongly supports that the published mouse activation model line is pre-fit. The comparison is preserved in `research/HUMAN-L23-WILBERS-FIG-S5-I-MOUSE-MODEL-PREFIT-CHECK.csv`; no separate final-figure generator is deposited.
- Main-text K+ summary values: activation V1/2 human −3.0 ± 5.9 mV (n=13) vs mouse −7.9 ± 6.0 mV (n=29), P=0.02; inactivation V1/2 human −52.7 ± 6.0 mV (n=11) vs mouse −65.0 ± 5.3 mV (n=26), P<10⁻⁶; resting-potential availability human 0.94 ± 0.05 vs mouse 0.86 ± 0.06. Human K+ currents activate faster at lower voltages; fast/slow inactivation and recovery time constants were described as similar between species, although human currents recover to a larger proportion of initial amplitude.
- Rust now reconstructs the K+ fixed-450-ms post-peak current-fit model for both human and mouse channel parameters (six fast-inactivation voltages per species) and replays the two-component recovery current protocol at all five recovery voltages for both species. The mouse model uses pure `k_mouse.mod` defaults including pre-fit `Ra=0.0167/ms`; its five-voltage SciPy references are checked by the Rust workspace tests. These are source-equation current-fit reconstructions, not gate time constants or biological validation.
- **Figure S5J/K source-path limitation:** the exact Dataverse `channel_tools.get_tau_inact_double_fixedtau2` helper has four free parameters and supplies four initial values; its `tau2` is fixed at 450 ms by default. The previously reported five-versus-four parameter mismatch and consequent NaNs were an incorrect source audit and are retracted. This helper has now been executed as part of the original K_IV source protocol in NEURON 9.0.2. The released 65-file inventory still has no separate final Figure S5 generator, per-cell K tau CSVs, or raw human K voltage-clamp traces, so source execution does not establish empirical fit accuracy or prove the exact plotted red/blue line-generation state. The Rust panel J/K reconstructions remain explicitly identified as model-equation reconstructions, not raw-trace validation.
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

Keep the spike-capable code provisional. The exact 65-file Dataverse v3.0 manifest has now been rechecked against the live API and an independently preserved metadata export: the named K tau CSV inputs, `data_fig5.xlsx`, raw K voltage-clamp NWB traces, and a separate S5 plot generator are not in that released inventory. The earlier bioRxiv ModelDB/GitHub URLs are unfinished placeholders; the final paper's ModelDB 8210 citation resolves to the separate Mainen et al. (1995) neocortical model, not the Wilbers authors' plotting/data repository. The HumanJS research record now captures this source reconciliation and the exact inventory provenance. The remaining evidence action is limited to independently accessible public sources and transparent analysis of the existing supplementary figure. Do not contact authors or researchers. Digitized model-line pixels remain raster-derived estimates, separate from experimental group means and not a substitute for source code or raw traces. Do not infer that data were withheld. Keep pooled human/mouse recovery constants distinct from human-only parameters; the voltage-clamp helper uses zero shift, not the separate −10-mV current-clamp shift. Reconsider the provisional spike mechanism only after the current-clamp objective, temperature semantics, source dimensional issues, and relevant human validation targets are independently satisfied. Keep the single-compartment preparation-equivalent separate from anatomical soma/AIS modeling. Do not claim biological validation from software tests or external model reproduction.

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


### 2026-11-12 — historical public contact-route lookup (retired)

A public publisher-page lookup established that a corresponding-author contact route was available and that the article's data statement points to Dataverse DOI 10.34894/L5J0SD. The project owner subsequently directed that no authors or researchers be contacted. No message was sent; outreach is not an intended follow-up. The v3.0/65-file inventory audit remains unchanged: the specific K kinetic CSVs, data_fig5.xlsx, raw K voltage-clamp traces, and a separate final Figure S5 plotting generator were not listed. The HumanJS spike-capable mechanism remains exploratory and unaccepted.


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


### Verification resolved — source-mapping regression

Follow-up workflow run 43133951113 completed successfully on exact commit 3dfc6ea954401e05aafe6aac4c29a3b5b07870f1. Rust formatting, Clippy, Rust tests (including current_clamp_voltage_shift_and_initial_gates_match_hybrid_source), Python syntax, both Wilbers validators, and repository policy all passed. The earlier formatting-only failure in run 43133844647 is resolved; it did not require changing the scientific assertions or relaxing checks.


### Verification correction — current-clamp protocol test

Workflow run 43134237756 failed only at rustfmt after the first source-protocol test commit; no compile or test was run in that attempt. Its formatter output was inspected. The rheobase helper was also corrected to match the deposited Python loop's increment-before-first-trial order in each of its 0.1/0.01/0.001-nA phases, retaining the source's backoff after the first two phases. The 20-nA/200-step guard is a HumanJS resource bound, not a biological threshold. Await the follow-up workflow before considering the protocol test verified.


### Verification correction — exact rustfmt shape

The next workflow (43134383535) again stopped at rustfmt only. The CI diff showed two initial-condition constructors that rustfmt collapses to a wrapped single expression. Those exact formatting changes are applied; the rheobase increment-order correction remains intact. No compile/test result was available from that formatting-only run.


### Verification correction — remaining rustfmt constructor

Workflow run 43134461510 reached the formatter and identified one remaining copy of the initial-condition constructor with the same rustfmt reflow. That exact formatting-only correction is now applied. No compilation or Rust test result was obtained from the previous run; use the next workflow as the verification gate.


### Verification correction — strongly typed voltage comparisons

Workflow run 43134527862 passed rustfmt but Clippy/compilation rejected direct ordering comparisons on the intentionally non-ordered Volts newtype. The regression now compares its explicit SI values via as_volts(), retaining dimensional types everywhere else. The failure was a compile-time API misuse, not a numerical test result.


### Verification correction — voltage-crossing condition formatting

Workflow run 43134596362 identified only the formatter's preferred single-line layout for the two SI-value threshold-crossing conditions. The logic remains the same; exact rustfmt output is now applied. The type-corrected regression still awaits compilation and execution.


### Verification correction — rustfmt condition/brace layout

Workflow run 43134667073 passed no code checks beyond setup because rustfmt requested the line break before the opening brace for both threshold conditions. The condition remains two typed SI-voltage comparisons; only its precise formatter-required wrapping is changed here. No test execution has yet succeeded for the new rheobase protocol.


### Verification failure — current-clamp source threshold extractor

Workflow run 43134731123 passed formatting and Clippy and executed 30 of 31 tests successfully. The new protocol test panicked while reproducing the source threshold heuristic: within its peak-centred −1/+3 ms window, it found no pre-maximum-slope derivative below 40 mV/ms. This is not an accepted spike-feature result and must not be fixed by widening thresholds. The next run adds the derivative/window diagnostics needed to locate whether the issue is the trace window, stimulus replay, or source-equivalence assumptions.


### 2026-11-12 — author current-clamp protocol replay diagnostic

A Rust-side replay of the published rheobase search and 1.5×-rheobase pulse reaches one −20-mV crossing, but the peak is 59.594103 mV (outside the 48–53-mV regression band). The published 40-mV/ms threshold heuristic is also undefined: its peak-centred window begins at 47.44865 mV/ms with no pre-maximum derivative below 40. Both mismatches are explicitly preserved as regressions. This is HumanJS RK4 output, not a biological result or source-exact NEURON reproduction.


### Author current-clamp replay — quantitative mismatch

The 1.5×-rheobase Rust replay finds one −20-mV crossing, but the HumanJS peak is 59.594103 mV, outside the existing 48–53-mV published-scale test band. The source threshold extractor is also undefined: its first derivative sample is 47.448652 mV/ms, already above the strict 40-mV/ms criterion, and maximum derivative is 526.597377 mV/ms. This mismatch is now asserted explicitly; no tolerance or target was widened. It is HumanJS RK4 output, not an original NEURON source run or biological result.


### Verification correction — stale peak-band assertion

Run 43135076696 exposed a stale 48–53-mV assertion that remained ahead of the new explicit mismatch assertions. It correctly failed on the 59.594-mV model output, but prevented the test from reaching its assertions that pin this result and the undefined threshold extractor. The stale success-band assertion is removed; the test is renamed to state that it preserves the published-feature mismatch. The 48–53-mV band is not widened.


### Verified protocol mismatch regression — CI success (2026-11-12)

Commit b44a0650b72501f76864f68ef593a772e16c779f removes the stale peak-band success assertion and renames the new test to `author_current_clamp_rheobase_protocol_preserves_published_feature_mismatch`. The test now checks exactly one −20-mV crossing, pins the HumanJS RK4 peak at 59.59410314264656 mV, asserts it remains above the 53-mV upper regression bound, and preserves the undefined source-threshold case (first derivative 47.448651583561485 mV/ms; max 526.5973771676144 mV/ms). It does not claim the 50:50 AP1 target is met.

GitHub Actions run 43135180538 completed successfully on exact commit b44a0650b72501f76864f68ef593a772e16c779f: rustfmt, Clippy, all Rust tests (31 passed), Python syntax, Figure S5 validator, current-clamp grid validator, and repository-policy validation passed. Earlier failed workflow attempts are recorded above; they surfaced formatting/API mistakes and then the actual model mismatch. This successful test is a regression which preserves the discrepancy, not a pass of the biological/source acceptance gate. No NEURON run or biological validation is claimed.


### Follow-up documentation verification

The documentation commit `5767d020cc096002a3afd83bf014018b6e30e880` is also CI-clean: GitHub Actions run `43135290117` completed successfully on that exact SHA. Formatting, Clippy, the full Rust test suite, Python syntax, both Wilbers scientific validators and repository policy all passed. The protocol-mismatch test is a passing regression because it deliberately preserves the observed out-of-band HumanJS output; it does not imply scientific acceptance.


### 2026-11-12 — corrected Wilbers current-clamp source reproduction

The previous 101-pA/59.594-mV/undefined-threshold conclusion is retracted. The first Rust test transcription omitted the authors' initial 0.1-nA trial before the increment loops. With the initial source trial restored, both NEURON 9.0.2 and HumanJS return 20.0-pA rheobase and use the same 30.0-pA AP1 pulse. The unchanged deposited helper/mechanisms were run independently; HumanJS matches all five extracted AP1 features within the measured RK4-versus-cnexp differences. Shared voltage samples have 0.455221-mV RMSE and 4.615873-mV maximum absolute error. The detailed reference, hashes, and reproduction runner are in research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md Section 6 and experiments/WILBERS-CURRENT-CLAMP-NEURON-REFERENCE.md. The model remains exploratory and unaccepted.


### CI verification of corrected NEURON reference replay (2026-11-12)

Commit 3ea7cb43fcc0e9627cfc7b6cdde3c28055356dd0 passed GitHub Actions run 43139126138. All required steps succeeded: Rust formatting, Clippy, complete Rust workspace tests, Python experiment-runner syntax, Figure S5 digitization validator, current-clamp conductance-grid validator, and repository policy. Two immediately preceding runs stopped at rustfmt because the source file lacked its terminal newline; that formatting-only issue was corrected. The source-model comparison assertions themselves passed unchanged. This CI validates the implementation and its pinned reference checks, not biological validity.

### 2026-11-12 — Wilbers AP1 solver-residual attribution

The unchanged `cc_tools.run_1AP` sets `h.dt=0.02` ms and leaves `h.secondorder` untouched; the NEURON 9.0.2 replay measured the default `secondorder=0` (fully implicit backward Euler). Both source NMODL channel mechanisms continue to use `METHOD cnexp` for their gates. The human Na mechanism has an active voltage-rate table (`FROM -120 TO 100 WITH 199`); the human K table code is commented out. NEURON's current reference documents the default and the Crank–Nicolson alternatives: https://www.neuronsimulator.org/en/latest/progref/simctrl/programmatic.html.

A source-verified numerical sensitivity experiment now separates the major solver effect. The original 20-µs, secondorder=0, Na-table-on baseline remains 0.455221-mV RMSE / 4.615873-mV max residual against HumanJS. Changing only the diagnostic NEURON voltage solver to secondorder=1 at the same 20-µs step reduces this to 0.038124 / 0.594290 mV. With 5-µs CN and Na table off the residual is 0.004756 / 0.062958 mV against the 20-µs HumanJS trace; a separately matched 1-µs CN/table-off comparison gives 0.001515 / 0.005020 mV. No biological parameters were changed. Table on/off is a secondary, timestep-dependent effect; the original table-on source remains canonical. Temporary diagnostic-only counters around the unchanged source `trap0` predicate observed 800 Na calls (including table generation) and 13,188 K calls, with zero fallback entries; the instrumented and original source traces were bit-identical over all 1,451 samples. The source defect remains relevant to other voltage trajectories and protocols.

New tools: `crates/humanjs-core/examples/wilbers_current_clamp_trace.rs` exports a HumanJS trace and independently replays the deposited rheobase search; `experiments/diagnose_wilbers_neuron_solver.py` downloads/checksums the five CC0 files, compiles unchanged NMODL, verifies the unmodified source baseline, then varies timestep, NEURON voltage integration order, and Na table use. Details and exact numbers are in `experiments/WILBERS-CURRENT-CLAMP-NEURON-REFERENCE.md` and Section 6 of the research record. This attribution is specific to a model-side AP1 numerical comparison, not biological validation; the human data/model-acceptance blockers remain open.

The clean main clone at pre-change HEAD `d9b0b871e4aadacb3cc1b58e873a1c32fd11563f` passed `cargo test --workspace --locked` locally (31 unit + 3 synapse integration + 6 passive membrane integration tests). The new Rust trace example also ran, independently returned rheobase 20.0 pA / AP1 30.0 pA, and emitted 1,450 samples. The diagnostic script passed Python 3.10 syntax, CLI, and end-to-end execution against the checksum-verified NEURON 9.0.2 environment; its author-helper baseline reproduced the prior reference to floating-point precision. The final main-branch workflow result is recorded in the current handoff verification entry below.

### 2026-11-12 — direct-main commit and CI verification of solver attribution

The numerical diagnosis, reproducible experiment script, Rust trace-export example, CI syntax-coverage update, and research/status documentation were committed directly to `main` in `65607325083b1152867ef7add5ef8f72eb3d2505` (`research(neuro): attribute Wilbers AP1 solver residual`). Its first workflow attempt, run `43144643445`, failed only at `cargo fmt --all -- --check`: the file-transfer step omitted the Rust example's terminal newline. This was corrected in `443f811296e591d6669c9e26b22b5906d1ae979d` (`style(neuro): preserve final newlines for CI`), which is the current verified `main` HEAD. GitHub Actions run `43144988410` completed successfully on that exact SHA; rustfmt, Clippy, Rust tests, all experiment Python syntax, both Wilbers validators, and repository policy all passed. The workflow now syntax-checks all `experiments/*.py`. The earlier format-only failed attempt remains visible in Actions history and is not concealed.

Current main tree SHA `94d5793aec8b09c94f60ba08f6403bc5d14f54c2` contains 74 entries (`truncated=false`). The branch listing contains only `main`; open issues and pull requests remain zero. No biological acceptance gate has changed. The spike-capable single-compartment model is still exploratory and not scientifically accepted.

### 2026-11-12 — secondary archive cross-check for Wilbers K-current source data

The primary Science Advances article (DOI `10.1126/sciadv.ade3300`) directs its public data, model files and scripts to Dataverse DOI `10.34894/L5J0SD`; its associated-data section lists Supplementary Text, Figs. S1–S7 and Tables S1–S3, without another linked raw-electrophysiology archive. Exact-title/site-restricted search returned no matching additional Wilbers K-current/per-cell kinetic deposit on DANDI, Zenodo, Dryad or Figshare. A Utrecht repository hit was a copy of the article, not an independent raw-data deposit. This is bounded index-search evidence, not proof of global absence. The previously checked Dataverse v3.0 65-file inventory still lacks per-cell K voltage-clamp traces and individual K-kinetic CSV targets. Distinguish the paper's published-conclusion data sufficiency from HumanJS's stronger cell-level reconstruction requirement. References and search limits are recorded in `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`.

### 2026-11-12 — latest-main independent rerun

After synchronizing the local checkout to the latest `main` baseline `30dcee632b9ad5a64e4d6c1f496b9f00e03d3c64`, the local verification was repeated: `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets -- -D warnings`, and `cargo test --workspace --locked` all passed (31 unit, 3 synapse integration, 6 passive membrane integration tests). The Rust AP1 trace example ran at both 20 µs (1,450 samples; peak 50.793612 mV at 4.16 ms) and 1 µs (29,000 samples; peak 50.818920 mV at 4.15 ms); both independently found 20-pA rheobase and applied 30-pA AP1. The 20-µs HumanJS trace's difference from its 1-µs trace is small relative to the original source-default residual.

The NEURON 9.0.2 diagnostic script was re-run end-to-end from this synchronized checkout with the pinned environment and checksum-verified Dataverse sources. It again found 20-pA rheobase and the unchanged source baseline comparison (1,450 common samples; RMSE 0.455221106542 mV; max residual 4.615872929631 mV at 3.94 ms). The controlled variants reproduced the earlier results: 20-µs CN/table-on RMSE 0.038124305 mV; 5-µs CN/table-on 0.024744611 mV; 5-µs CN/table-off 0.004756176 mV. The diagnostic command without the pinned `nrnivmodl` directory on `PATH` correctly failed with an actionable environment error; rerunning with `PATH=/tmp/hjvenv/bin:$PATH MAKEFLAGS=-j1 MPLBACKEND=Agg` succeeded. No generated traces or result JSONs were added to Git.

### 2026-11-12 — Wilbers AP1 internal gate-state comparison

The AP1 diagnostic now exports and compares the five source NMODL STATE variables (Na m/h, K m/h1/h2) with the five HumanJS live gate fractions. In the author-default 20-µs, secondorder=0, Na-table-on run, gate RMSEs are 0.003213 Na activation, 0.002729 Na inactivation, 0.001386 K activation, 0.0000810 K fast inactivation, and 0.0000770 K slow inactivation (dimensionless fractions). The largest state differences occur during the 3–4.2-ms spike upstroke/peak; pre-spike state differences are small. Applying the deposited conductance equations to gate traces gives derived Na/K conductance-density RMSEs of 0.1436/0.02367 pS/µm². These are model outputs, not measurements.

A 1-µs CN/table-off convergence diagnostic compared all 29,000 post-step samples against 1-µs HumanJS: gate RMSEs were 0.0001406 Na activation, 0.0000990 Na inactivation, 0.0000544 K activation, 0.00000352 K fast inactivation, and 0.000000572 K slow inactivation. This does not make the non-default NEURON solver the paper's baseline or establish biological fidelity. The Rust trace example and Python source diagnostic now optionally emit/compare gate CSVs; details and reproducible commands are in the Wilbers experiment note and research Section 6. The gate-integrator-only difference under identical externally prescribed voltage remains unisolated.


### 2026-11-12 — AP1 channel-gate comparison committed

Commit `ada7a9e8ecd478adfd3b411d2ccd0bdefbd1b137` adds optional HumanJS and NEURON five-gate trace capture and quantitative comparison. In the author-default replay, gate RMSEs are 0.003213 Na activation, 0.002729 Na inactivation, 0.001386 K activation, 0.0000810 K fast inactivation, and 0.0000770 K slow inactivation. Differences concentrate around rapid AP voltage change; the high-resolution 1-µs CN/table-off comparison reduces the gate errors substantially. The detailed outputs and limits are in the research and experiment records. Actions run `43147714885` passed on the exact commit. No biological acceptance gate has changed.

### 2026-11-12 — shared-voltage gate-integrator decomposition

The diagnostic now applies both cnexp-equivalent and RK4 gate updates to the same source voltage samples, using the post-step voltage `V[n+1]`, common initial NMODL gate states, and the same continuous rate equations. The source exponential recurrence reproduces actual direct-rate NMODL gate states within a maximum 1.76e-6 fraction (diagnostic guard 1e-4). At 20 µs, the isolated RK4-versus-cnexp difference is 2.8221e-6 overall gate RMSE / 1.16295e-4 max, dominated by Na activation; at 1 µs it falls to 1.1710e-11 / 4.8856e-10. On the same path, Na TABLE versus direct-rate CNEXP yields 3.70195e-5 overall RMSE / 1.23720e-4 max, affecting only Na gates. These effects are much smaller than actual dynamic source-vs-HumanJS gate errors, so differing voltage paths/stage sampling/coupled feedback remain the main unresolved numerical contributors. No biological validity claim follows.


### 2026-11-12 — shared-voltage gate integrator and Na TABLE experiment committed

Commit `eec5651c80b71e0d7706f617d944cfad772c38fb` records a same-voltage counterfactual for the five gates and quantifies source Na TABLE interpolation separately. At 20 µs the isolated RK4-versus-cnexp gate RMSE is 2.8221e-6 (maximum 1.16295e-4), dominated by Na activation; at 1 µs it is 1.1710e-11 (maximum 4.8856e-10). Na TABLE-versus-direct CNEXP on the same path yields 3.70195e-5 RMSE / 1.23720e-4 maximum, affecting Na gates only. These isolated effects are much smaller than the full dynamic source-vs-HumanJS gate residual. Actions run `43149669478` passed on the exact commit. This does not establish biological fidelity or change acceptance status.


### 2026-11-12 — voltage-stage sampling counterfactual added

The shared-voltage gate diagnostic now replays the recorded NEURON voltage path with four RK4 gate-voltage conventions: hold the left endpoint, hold the interval midpoint, hold the right endpoint (the previous comparison), or linearly interpolate voltage at the RK4 stage times. All four start from the same recorded NMODL gate state, use the same analytic Wilbers gate rates and fixed timestep sequence, and are compared against both the recorded NMODL gates and one another. The −10-mV channel shift is applied consistently. All replay trajectories are checked for finite gate fractions in [0, 1].

This isolates sensitivity to voltage sampling on a prescribed source voltage trajectory; the linear ramp is not the actual intermediate voltage of the coupled HumanJS membrane solver. The diagnostic does not yet partition the feedback difference between voltage and gates in a fully coupled run. Numerical outputs require the pinned Python 3.10 / NEURON 9.0.2 environment; the available session runtime is Python 3.13.5 without NEURON, so no new source replay numbers are claimed here. Run the documented solver diagnostic with the pinned environment to obtain the four per-gate error profiles. The spike-capable HumanJS mechanism remains exploratory and scientifically unaccepted.


### 2026-11-12 — executable tests for voltage-stage sampling counterfactuals

The shared-voltage gate replay now validates all five source gate traces against the voltage sample count, finite values, and [0, 1] bounds before integration. Its gate-metric helper rejects malformed, non-finite, or shape-mismatched arrays. A standard-library unittest suite exercises (1) constant voltage, where all sampling conventions must coincide, (2) a varying voltage path, where linear-ramp and right-hold RK4 must differ, and (3) malformed gate lengths and metric shapes. CI installs the already-pinned NumPy 1.26.4 test dependency and executes `python3 -m unittest discover -s experiments -p 'test_*.py' -v`. Workflow `43167476483` passed on exact commit `c3dcffcef5b07c40f100a3ed167944afc00b104d`; the new four tests passed, along with rustfmt, Clippy, all Rust workspace tests, experiment syntax, both Wilbers validators, and repository policy.

These are deterministic software tests of the counterfactual implementation, not a NEURON source replay and not biological validation. The pinned Python 3.10 / NEURON 9.0.2 end-to-end diagnostic still needs to be run to produce source-trace-specific sensitivity values. The exploratory single-compartment model remains unaccepted.


### 2026-11-12 — paired source/HumanJS voltage-path gate attribution

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

The source-order and CN replays now reproduce the corresponding NEURON fixed-step trajectories; matched current balances close. Next, quantify same-path midpoint/left-gate current versus RK4-weighted current and the fully evolved source/HumanJS current mismatch across timestep refinement and Na TABLE settings. Keep biological parameters fixed and retain the author-default baseline.


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

### AP1 CN midpoint current and state-history attribution (2026-11-13)

A new independent secondorder=1 replay evaluates source currents at the voltage midpoint using G[n], then advances the five CNEXP gates using V[n+1]. At 1 µs and 250 ns it reproduces actual NEURON within 0.000558 mV voltage RMSE and 2.87e-6 aggregate gate RMSE. At 250 ns, source CN current balance and HumanJS RK4 weighted current balance close below 1.1e-12 A/m²; their actual voltage-residual/current-difference identity closes to 4.2e-11 A/m² maximum. Actual source/HumanJS total current RMSE is 1.742e-5 A/m². A prescribed-HumanJS-path midpoint/left-gate counterfactual yields 4.023e-4 A/m²; this is a distinct counterfactual, not the coupled source path, and shows that state-history feedback changes the residual. The 125-ns HumanJS stage/current trace generated, but the expanded NEURON diagnostic hit the VM memory limit (exit 137); no 125-ns current-balance result is claimed. Numerical analysis only; no parameter change or biological acceptance.


## 2026-11-13 — matched 5-µs AP1 current-history refinement

A fresh pinned-environment run paired exact HumanJS RK4 stage-current exports with NEURON 9.0.2 secondorder=1 at 5 µs, with the source Na TABLE on and off. The unchanged deposited author-helper baseline remains 20 µs, secondorder=0, TABLE on; rheobase 20 pA and AP1 current 30 pA. All conductance densities and biological parameters were held fixed.

- Source CN replay vs actual NEURON voltage RMSE: 0.00055897 mV (TABLE on) and 0.00055720 mV (off).
- HumanJS voltage vs NEURON: 0.02487096 mV RMSE (TABLE on) and 0.00463648 mV (off).
- Fully evolved source CN midpoint vs HumanJS RK4-weighted total current: 0.00208318 A/m² RMSE (TABLE on), 0.000408145 A/m² (off). With TABLE off, Na/K/leak component RMSEs are 3.99798e-4 / 3.43948e-5 / 4.68564e-6 A/m²; sodium dominates the upstroke, potassium is comparable/larger in late repolarization, and leak dominates the tail.
- The prescribed-HumanJS-path midpoint/left-gate counterfactual is 0.00785330 A/m² RMSE in both TABLE variants. It is not a coupled CN run and uses the same direct current law on the unchanged HumanJS path.
- Source CN and HumanJS RK4 capacitance-current identities close to at most 8.7e-13 A/m²; the voltage-residual/current-difference identity closes to at most 2.51e-12 A/m².
- Compared with the earlier 250-ns TABLE-off result, fully evolved current RMSE is about 23.4 times higher at 5 µs; the prescribed-path counterfactual is about 19.5 times higher. This is consistent with timestep sensitivity but is not an asymptotic-order claim.

The new matched 1-µs NEURON extension was not completed: nrnivmodl exceeded a 600-s build allowance in the 1-GiB VM; no 1-µs current JSON was produced. The 125-ns limitation remains as previously recorded. The generated CSV/JSON files stayed outside Git. No parameters changed; no biological validation is claimed. The single-compartment spike model remains exploratory and unaccepted.


### 2026-11-13 — three-resolution AP1 current refinement

Matched 5-µs, 1-µs and 250-ns HumanJS/NEURON 9.0.2 secondorder=1 traces now have source CN current balances for both Na TABLE settings. The original author helper remains at 20 µs / secondorder=0 / Na TABLE on; all-human channel densities, 20-pA rheobase and 30-pA AP1 pulse were unchanged.

| Step | Na TABLE | Voltage RMSE (mV) | Evolved source/HumanJS current RMSE (A/m²) |
|---:|:---:|---:|---:|
| 5 µs | On / Off | 0.024871 / 0.004636 | 0.002083 / 0.0004081 |
| 1 µs | On / Off | 0.028692 / 0.001515 | 0.002474 / 0.00001277 |
| 250 ns | On / Off | 0.028847 / 0.001477 | 0.002490 / 0.00001742 |

Direct-rate voltage RMSE reaches a floor near 0.001476 mV between 1 µs and 250 ns. Switching the Na TABLE changes the source voltage trajectory by a nearly resolution-invariant 0.02907-mV RMSE (maximum about 0.408 mV around 3.912 ms); this perturbation correlates 0.9987 with the TABLE-on HumanJS residual at the two finer steps. On an identical prescribed voltage path, the 200-node table versus analytic rates leaves a stable 3.76e-5 aggregate Na-gate RMSE, while the direct-rate CNEXP/RK4 same-voltage gate difference falls to 4.9e-13 at 250 ns. The table interpolation, not direct-rate gate integration, is therefore the dominant identified source of the table-on floor.

The prescribed HumanJS midpoint/left-gate current counterfactual falls 0.0078533 → 0.0015841 → 0.0004023 A/m², with empirical refinement slopes about 0.99; it is not the fully coupled source trajectory. Actual TABLE-off source/HumanJS current RMSE is non-monotonic at the two finest steps (1.2767e-5 at 1 µs; 1.7423e-5 at 250 ns), so no convergence order is claimed. Capacitor-current balance identities remain closed to approximately 1e-13 A/m², and the voltage/current residual identity closes below 4.12e-11 A/m².

A 125-ns HumanJS trace was generated, but the new memory-reduced NEURON attempt produced no JSON and its failure mode was not captured. A previous 125-ns NEURON attempt was killed at the VM memory limit. No new 125-ns source current figures are claimed. No model parameters changed; the spike mechanism remains exploratory and unaccepted.


### 2026-11-13 — Na TABLE resolution and K trap0 interaction

A controlled 250-ns counterfactual varied only the temporary sodium TABLE from the original 200 nodes to 400, 800 and 1,600 nodes. The original 20-pA rheobase / 30-pA AP1 pulse, channel densities, secondorder=1, and direct-rate control were held fixed.

| Nodes | TABLE-on voltage RMSE (mV) | TABLE-off voltage RMSE (mV) | TABLE-on evolved current RMSE (A/m²) |
|---:|---:|---:|---:|
| 200 | 0.028847 | 0.001477 | 0.002490 |
| 400 | 0.006918 | 0.001477 | 0.0006111 |
| 800 | 0.002102 | 0.001477 | 0.0001640 |
| 1,600 | 0.001466 | 0.001477 | 0.00005147 |

The TABLE-on source/HumanJS voltage residual approaches the direct-rate floor as the grid is refined. The shared-voltage Na-gate interpolation error drops 63-fold from 200 to 1,600 nodes; the coupled source TABLE-on/off voltage perturbation drops about 65-fold. Both show approximately second-order scaling over these four accepted grid sizes. The direct-rate source control remains unchanged.

The 3,200-node TABLE-on trial is excluded: at 4.402 ms the source trajectory reaches the K activation guard where the deposited trap0 predicate checks v+th while its denominator singularity is at v-th. The independent K activation recurrence then fails its 1e-4 tolerance (maximum residual 1.385e-3). A 3,200-node TABLE-off-only control passes and reproduces the 250-ns direct-rate reference. No 3,200-node TABLE-on current/voltage result is accepted.

Original source files and HumanJS model parameters were not modified. Temporary copies, compiled libraries and traces stayed outside Git. The author baseline remains 200 nodes / 20 µs / secondorder=0 / TABLE on. This is numerical evidence, not biological validation; the spike mechanism remains exploratory and unaccepted.


### 2026-11-13 — direct K trap0 rate probe

A focused NEURON 9.0.2 probe evaluated the unchanged K NMODL rate procedure at 34°C around the wrong-sign branch. For tha=-29.961798 mV and qa=6.590406 mV, the predicate fabs((v+tha)/qa) triggers within only ±6.59041e-6 mV of v=-tha, although the denominator singularity is at v=tha.

At the trigger, the source rates are a=36.552210 and b=-23.371390, versus 1.106272 and +0.000124457 from the continuous source formula. The source mtau drops abruptly from about 0.903835 ms to 0.075868 ms (11.91-fold), while minf stays 0.925478. This confirms a finite branch discontinuity, not a true rate singularity. It explains why a fine-table trajectory can trigger a large K activation recurrence error. Original NMODL source and HumanJS parameters are unchanged; no biological validation is claimed.


### 2026-11-13 — high-resolution Na TABLE and K trap0 control

A fresh pinned NEURON 9.0.2 run regenerated the 250-ns HumanJS AP1 trace (116,000 post-step samples). The original 3,200-node Na-table / original-K run reproduced the gate-replay failure: m_k maximum error 0.00138525 at 4.402 ms. The wrong-sign guard fabs((v+th)/q) triggered at 2.37e-7 although the true denominator distance fabs((v-th)/q) was 9.09255.

A temporary K-only mathematical control changed the guard to v-th and the small-x limit to a*q; no parameters changed and no repository source was patched. The same 3,200-node AP1 run then passed the gate check (corrected m_k maximum replay error 1.5844e-5, 87.4-fold lower). A 6,400-node run also passed. At 3,200/6,400 nodes, TABLE-on voltage RMSE was 0.0014623/0.0014729 mV and evolved current RMSE 2.4856e-5/1.9107e-5 A/m²; the direct-rate control stayed at 0.0014774 mV and 1.7423e-5 A/m². Shared-path Na-table gate error and actual source TABLE-on/off voltage perturbation each fell about fourfold when the grid doubled from 3,200 to 6,400 nodes. The result extends the prior approximately second-order table-spacing trend but is still a bounded numerical counterfactual, not a biological comparison.

The corrected-K source CN replay matches NEURON within about 0.000557 mV; its aggregate gate replay RMSE is 2.86e-6 and maximum error 6.76e-5. Current-balance identities remain closed at approximately 1e-13 A/m². Original Dataverse mechanisms, 20-pA rheobase, 30-pA AP1 stimulus, and conductances were preserved; modified NMODL copies and all traces remained outside Git. The author baseline remains 200 nodes / 20 µs / secondorder=0 / TABLE on.


### 2026-11-13 — 12,800-node Na TABLE extension

The corrected-K 250-ns counterfactual was extended to 12,800 Na-table nodes. TABLE-on voltage/current RMSEs are 0.00147610 mV and 1.78514e-5 A/m², versus 0.00147738 mV and 1.74232e-5 A/m² for the matched direct-rate control. The current mismatch is now 1.0246× the direct-rate residual (1.0967× at 6,400; 1.4266× at 3,200). Shared-path Na gate error is 9.22e-9; source TABLE-on/off trajectory delta is 7.19e-6 mV RMSE. Doubling 6,400→12,800 lowers the shared-path gate error 4.00× and the trajectory delta 3.79×. Current identities remain closed at approximately 1e-13 A/m².

The current Rust implementation's trap0 helper already uses the correct v-th offset, analytic prefactor×slope limit, exp_m1 and asymptotic branches; its existing continuity unit test passed. No HumanJS code change was needed. Temporary corrected-K/12,800-node NMODL files and outputs remained outside Git. This remains a numerical counterfactual, not biological validation or a replacement for the author's 200-node baseline.


### 2026-11-13 — Human K activation trap0 regression

Added `human_potassium_activation_rate_is_continuous_at_both_trap0_voltage_landmarks` in `crates/humanjs-core/src/ion_channels.rs`. It compares HumanJS K activation tau with an independent `exp_m1)-based source-equation evaluation at the former wrong-sign guard (v=-theta), both guard edges, the true denominator singularity (v=theta), and nearby points. The tested discrepancy tolerance is 1e-12 ms. The targeted test and full Rust suite pass. No biological parameter or runtime implementation changed; this is a software regression only.

### 2026-11-13 — K activation source sweep and Rust regressions

An unchanged NEURON 9.0.2 K mechanism was evaluated at 441 voltages from -120 to +100 mV (0.5-mV spacing). Outside the tiny branch/limit regions, source activation tau matched the analytic equation within 9.77e-15 ms; steady states matched. The exact original false guard v=-theta causes an approximately -0.828-ms tau jump only inside +/-6.59041e-6 mV, while the true singularity v=theta returns NaN in NMODL instead of the 4.11000492924-ms analytic-limit tau.

Added two Rust tests: human_potassium_activation_rate_is_continuous_at_both_trap0_voltage_landmarks and human_potassium_activation_rates_match_source_equations_over_voltage_grid. They cover both singularity landmarks and 441 voltages after the explicit -10-mV channel shift. All 34 Rust unit tests pass; this remains software/source-equation verification, not biological validation.

### 2026-11-13 — K fast-inactivation trap0 regression

The original K NMODL fast-inactivation alpha and recovery beta rates exhibit the same wrong-sign guard defect. NEURON 9.0.2 returned negative tau_h1 at the alpha false guard (v=-thi1: source -0.0725058005 ms vs analytic 143.684108 ms) and beta false guard (v=-thi2: source -0.0132529631 ms vs analytic 12.2636432 ms). At the true denominator singularities v=thi1 and v=thi2, the original source returned NaN instead of analytic-limit tau values 22.0986469 and 360.921209 ms. The independent steady-state inactivation sigmoid remained correct.

Added Rust tests for all four landmarks and a 441-point -120 to +100 mV comparison of fast-inactivation tau and steady state with the independent source equation, applying the -10-mV channel shift explicitly. The 441-point unchanged-source sweep was finite and matched the analytic tau within 6.86e-13 ms. Full suite: 36 Rust unit, 3 synapse integration, 6 passive membrane integration and 22 Python tests passed. This is software/source-equation verification, not biological validation.


### 2026-11-13 — direct sodium trap0 rate probe

NEURON 9.0.2 direct calls to the unchanged human sodium `rates(v)` procedure confirm the same wrong-sign trap0 guard already identified in K. The three false guards occur at effective voltages +58.59235669 mV (m activation), +39.29867691 mV (h alpha) and +77.16674532 mV (h beta), with half-widths only 9.21455e-6, 7.21636e-6 and 4.74945e-6 mV. At those centres the source taus are 0.0256413, 0.0101590 and −0.00706676 ms; the analytic continuations are 0.0188446, 0.126201 and +0.0851694 ms. At the three true denominator singularities, direct NMODL rates return NaN rather than finite analytic-limit taus (0.119828, 1.37393 and 7.12695 ms).

The 441-point direct-rate sweep (−120…+100 mV, 0.5-mV spacing) avoids these microscopic windows and agrees with the analytic equations to below 6.3e-15 ms. The default 200-node TABLE path stays finite at all six landmarks and on the sweep; its maximum sweep interpolation errors are 3.55e-5 ms for m and 0.01984 ms for h. Thus the TABLE path masks the micro-window faults at these exact landmarks, but the underlying direct NMODL rate function remains defective. The original source hash and author TABLE baseline are preserved. Numerical/source analysis only; no biological validation.


### AP1 path check — sodium trap0 windows were not sampled

The matched original-source 250-ns AP1 run (both Na TABLE off/on, 116,001 samples, secondorder=1, 20-pA rheobase/30-pA pulse) did not enter any Na false-guard window or land exactly on a true singularity. The closest point was the h-alpha false guard: 0.00103467 mV away with TABLE off (143× guard half-width), and 0.0000882037 mV away with TABLE on (12.2×). The other two false guards were outside the trajectory's effective-voltage range. The nearest true singularity was h-beta, still 7.34e-6 normalized q away in the direct-rate path.

Therefore the direct sodium branch faults characterized at exact landmarks do not explain this specific AP1 voltage residual. The 200-node TABLE-on/off difference remains an independent interpolation/state-history effect (0.0288472 vs 0.00147738 mV voltage RMSE). This is only a path-specific check, not a guarantee for other stimuli or step sizes.

### 2026-11-13 — Human sodium rate regression coverage

Added `human_sodium_rates_are_continuous_at_all_trap0_landmarks` and `human_sodium_rates_match_source_equations_over_voltage_grid` in `crates/humanjs-core/src/ion_channels.rs`. The first tests the three false guards, their inside/outside edges, three true denominator singularities and neighboring voltages against independent `exp_m1` analytic rates (1e-12 ms tau tolerance). The second checks Na activation/inactivation taus and steady states over 441 effective voltages (−120…+100 mV, 0.5-mV spacing), with the current-clamp voltage shift applied explicitly. The two tests do not alter production code or parameters.

Workflow [43425235022](https://github.com/codexclai/HumanJS/actions/runs/43425235022) passed on exact code commit `ed07cec9982622f9c3dcb8c0825c7951c3515442`: Rust 38 unit tests, 3 synapse integration tests, 6 passive-membrane integration tests, 22 Python tests, both Wilbers validators, formatting, Clippy and repository policy. This is software/source-equation verification only, not biological validation.


## 2026-11-13 — K_IV fast-inactivation initialization and profile audit

The original K_IV source helper remains unchanged. Its four free parameters are `(a1, tau1, a2, ss)`, with fixed `tau2=450 ms`, a `tau1` source bound of 0–300 ms, and an R²>0.95 reporting threshold. Exact source inspection confirms that the helper time-shifts with `x=x-x[0]`; the new counterfactuals reproduce that step and reuse the same post-peak NEURON current samples.

The source initial vector is poorly scaled under the recorded mA/cm² convention. At −70 mV the `tau1` initial value is 3.14164 × 10⁻⁵ ms, derived from half a current-density difference; `a2` starts at 30 mA/cm², approximately 59,965 times the observed current peak. This is a code-level initialization observation, not proof of author intent. Across six starts at 32 voltages, all 192 fits converged; source acceptance varies by start. At −70 mV the accepted `tau1` values span 186.610–213.819 ms. The largest accepted within-voltage spread is 111.420 ms at −85 mV.

A nonnegative linear profile of `a1`, `a2`, and `ss` at fixed `tau1` gives its best sampled point at 300 ms at the source upper bound. The extended 0.05–1200-ms grid found a coarse best at 338.237 ms; the 801-point 320–360-ms local profile refines it to 339.411255 ms (R² 0.999999577179; RMSE 1.167677×10⁻⁸ mA/cm²). Its 1%-RMSE band spans 326 points from 331.461 to 347.706 ms; the descriptive a1/a2 Pearson correlation in that band is −0.99999896 and offset span is 0.114%. The 4,890-row residual export at this tau reproduces the objective: RMSE 1.16768×10⁻⁸ mA/cm², with the largest residual (−3.028×10⁻⁷) at the first post-peak sample. Residual RMSE is 7.80×10⁻⁸ over the first 10 ms but only 3.29×10⁻⁹ from 10 ms onward, indicating a localized early transient mismatch in the deterministic model waveform. The residuals are temporally correlated and are not empirical noise or biological validation.

Source/analysis records: `HUMAN-L23-WILBERS-K-IV-FIT-SENSITIVITY.md`, `HUMAN-L23-WILBERS-K-IV-FIT-START-DIAGNOSTICS.csv`, `HUMAN-L23-WILBERS-K-IV-FIT-PROFILE.csv`, `HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-EXTENDED.csv`, `HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-LOCAL.csv`, and `HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-RESIDUALS.csv`. Workflow [43462311680](https://github.com/codexclai/HumanJS/actions/runs/43462311680) passed on exact code HEAD `55d469485edb00a9d65c105645f58b9bb1a92a39`, including all tests, five original NEURON source replays, fit-start and profile diagnostics, 4,890 time-resolved residuals, and repository policy. Raw human K voltage-clamp traces remain absent from the inspected Dataverse v3.0 release; raw-trace refitting and biological validation remain outstanding.


## 2026-11-13 — K_IV residual waveform inspection

The local optimum's residual waveform was exported and validated for all 4,890 post-peak samples at 0.1-ms spacing. At `tau1=339.41125497 ms`, the residual export reproduces R²=0.999999577179 and RMSE=1.16767714×10⁻⁸ mA/cm². The largest absolute discrepancy occurs at the first post-peak sample (−3.02798×10⁻⁷ mA/cm²); the residual first changes sign at 4.0 ms. RMSE over the first 10 ms is 7.80270×10⁻⁸ mA/cm², whereas it is 3.28972×10⁻⁹ mA/cm² over the remaining 4,789 samples. This localizes most of the mismatch to the earliest post-peak transient; the remainder of the model waveform is fit much more closely.

The full residual series has lag-1 correlation 0.9284; after 10 ms it is 0.9979. These are descriptive temporal properties of a deterministic residual sequence, not a stochastic error model or measurement-noise assessment. The source helper, caller, and potassium NMODL mechanism remain unchanged. Canonical data is `research/HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-RESIDUALS.csv`; the new `experiments/validate_wilbers_k_iv_fit_residuals.py` checks the residual equation, source clock alignment, local-profile coefficients, R² and RMSE. Full workflow [43462311680](https://github.com/codexclai/HumanJS/actions/runs/43462311680) passed on exact code HEAD `55d469485edb00a9d65c105645f58b9bb1a92a39`.

The first residual test attempt [43462098026](https://github.com/codexclai/HumanJS/actions/runs/43462098026) failed because its synthetic test incorrectly required every residual to be below 10⁻¹² mA/cm² despite using a grid-sampled tau. The test was corrected to compare independently recomputed residual RMSE with the corresponding profiled objective and require finite residuals; no source model or validation gate was weakened.


## 2026-11-13 — non-source K_IV third-exponential transient correction

Added an explicitly non-source counterfactual to investigate the early residual mismatch in the existing −70-mV K_IV model waveform. Input is the checked-in 4,890-sample NEURON source-model current record (0–488.9 ms relative to the post-peak fit start; original NEURON clock 30.9–519.8 ms). The long component is fixed at the best sampled local-profile value, tau1=339.411255 ms (outside the deposited helper's 0–300-ms bound), and the source slow component remains fixed at 450 ms. A third exponential time constant is profiled linearly over 0.6–2.0 ms at 801 points; its amplitude and the original amplitudes/offset are fit to the entire waveform, with the original terms constrained nonnegative and the new coefficient allowed to be signed.

The full-waveform optimum is approximately tau3=1.2335 ms; the extra amplitude is about −3.18×10⁻⁷ mA/cm², only 0.064% of the observed peak and negative in sign. Against the two-component baseline, full-waveform RMSE falls from about 1.168×10⁻⁸ to 2.450×10⁻⁹ mA/cm² (79.0%); first-10-ms RMSE falls from 7.803×10⁻⁸ to 4.656×10⁻⁹ (94.0%); after-10-ms RMSE also falls by about 27.6%. Refitting changes the original first amplitude by +0.37%, the fixed-450-ms amplitude by −0.93%, and the offset by +0.0077%. At the signed optimum, the same model with a3 >= 0 sets a3 to zero and reproduces the baseline objective.

This is a subtractive, descriptive residual correction—not evidence for a new positive current component, a microscopic gate, a biological fast-inactivation time constant, or a revised channel mechanism. It fits the deposited NEURON model output, not raw human current recordings. The original Dataverse helper, caller, and k_human.mod were not changed. Raw human K voltage-clamp NWB traces and individual K kinetic CSVs remain absent from the inspected DataverseNL v3.0 inventory. The exploratory HumanJS spike-capable model remains unaccepted and biologically unvalidated. Implementation and validation: experiments/wilbers_k_iv_three_component.py, experiments/test_wilbers_k_iv_three_component.py, and experiments/validate_wilbers_k_iv_three_component.py; CI adds this validator to the main workflow.


## 2026-11-13 — signed K_IV residual correction across three adjacent voltages

The earlier -70-mV K_IV residual study was tested against adjacent source commands -75 and -65 mV. The exact NEURON source runner now retains the original post-peak samples at all three voltages, with the relative fit clock and original NEURON simulation clock. For each voltage, the long tau1 was profiled independently over 0.05-1200 ms and locally refined; the source slow component remained fixed at 450 ms. The non-source short tau3 was profiled over 0.6-2.0 ms. All coefficients were fitted against each complete waveform.

| K_IV command | Local tau1 (ms) | Short tau3 (ms) | Signed a3 (mA/cm2) | Absolute a3 (% peak) | Full RMSE reduction | First-10-ms reduction | After-10-ms reduction |
|---:|---:|---:|---:|---:|---:|---:|---:|
| -75 mV | 393.4039 | 1.111 | -1.00654e-7 | 0.0391% | 80.386% | 94.278% | 27.728% |
| -70 mV | 339.4072 | 1.2335 | -3.18235e-7 | 0.0636% | 79.023% | 94.034% | 27.614% |
| -65 mV | 291.4180 | 1.384 | -9.95616e-7 | 0.1060% | 77.371% | 93.789% | 27.433% |

The extra coefficient is negative at all three commands and remains below 0.11% of peak current. The fitted short time constant increases smoothly across this narrow voltage interval, and the signed term reduces RMSE over the full waveform as well as both time partitions. At each command, a nonnegative-extra-amplitude control collapses to zero. The -75/-70 local long tau1 results are outside the deposited source helper's 0-300-ms bound, so these remain explicitly non-source profile estimates.

This is reproducibility of a small negative residual correction across three adjacent model-output waveforms, not evidence for a new positive current component, microscopic channel state, or biological voltage-dependent gate. Three nearby commands do not establish a general voltage law. Raw human K voltage-clamp NWB traces and individual K kinetic targets are still absent from the inspected DataverseNL v3.0 inventory. No empirical current refit or biological validation is claimed; the exploratory Rust spike model remains unaccepted.


## 2026-11-14 — K_IV signed-residual profile across all eligible source-fit voltages

The three-voltage K_IV signed-residual diagnostic was extended to the complete predeclared set of finite-positive source fast-inactivation fits. The NEURON replay runner now derives and asserts each source-selection outcome rather than exporting only favorable commands. Source selection is exhaustive and predeclared from the original K_IV helper: 34 commands were run; the source current threshold passed at 32 (-100 through +55 mV); five attempted fast fits were non-finite (-100, -95, -90, -85 and -80 mV); and the remaining 27 commands (-75 through +55 mV) had finite positive source fast-fit estimates. The two threshold exclusions (-110 and -105 mV) and the five non-finite fit attempts are recorded separately and are not treated as missing-at-random samples.

Across the 27 eligible model-generated waveforms, the signed non-source third-exponential coefficient was negative at all 27 commands; the nonnegative-amplitude control collapsed the extra term to zero at all 27 signed optima. Full-waveform RMSE reduction ranged from 55.467% to 80.386% (median 66.126%); first-10-ms reduction ranged from 75.608% to 94.278% (median 84.935%). After-10-ms RMSE improvement ranged from -41.467% to +27.728% (median +20.814%); the late-window error worsened at +25 through +55 mV (seven commands), despite lower full-waveform error at every command. The extra coefficient magnitude ranged from 0.0391% to 2.0965% of peak current.

The non-source tau3 optimum ranged from 0.6 to 2.0 ms (median 1.384 ms), with 11/27 profiles at one of the declared grid boundaries: 2.0 ms at -50 through -15 mV, and 0.6 ms at +45, +50 and +55 mV. Tau3 is not globally monotonic and these boundary outcomes are not interior estimates. Local tau1 ranged 17.195-393.404 ms; only -75 and -70 mV exceeded the deposited source helper's 300-ms upper bound. These findings describe a chosen numerical correction family on deterministic NEURON/VClamp model output, not human experimental current, a positive ionic component, a microscopic gate, or biological channel kinetics. The inspected DataverseNL v3.0 public inventory still lacks raw human K voltage-clamp NWB traces and individual K tau target CSVs. The deposited helper, caller, pure-human NMODL, and HumanJS runtime parameters were not changed; ADR-014 remains open.

The complete result table `research/HUMAN-L23-WILBERS-K-IV-MULTIVOLTAGE-RESIDUAL-SUMMARY.csv` contains all 27 voltages and 39 columns. The unchanged source runner exports the exact post-peak slice passed to the source helper, with both shifted fit time and original NEURON clock. The analysis profiles tau1, then the signed tau3 and all coefficients against the full waveform; early/late partitions are diagnostics. The main workflow's strict expected-output validator compares every result field to the committed CSV.

GitHub Actions [43488672121](https://github.com/codexclai/HumanJS/actions/runs/43488672121) passed on exact code HEAD `dff6fc6af7959a74263646f96ceb69e62fb725eb`: rustfmt, Clippy, Rust tests (41 core unit, 3 synapse integration, 6 passive-membrane integration), Python syntax, 44 Python tests, Wilbers validators and original NEURON 9.0.2 Na/K source-protocol runs, the expanded 27-command profile and exact committed-CSV comparison, three-exponential counterfactual validation, and repository policy.

No source fitting helper/caller/NMODL, Rust equation, channel parameter, or production mechanism was changed. The broader analysis strengthens only a model-output residual observation. Raw human K voltage-clamp refitting remains blocked by absent public raw recordings and per-cell K kinetic target files. The exploratory single-compartment spike model remains scientifically unaccepted; this software/experiment workflow does not biologically validate it and does not close ADR-014.

**Next concrete work:** investigate tau3 boundary sensitivity using a wider predeclared short-time grid with explicit boundary reporting, and retain the full/early/late objective partitions. Do not optimize only the early window, transfer any fit term into Rust, or infer biological K-channel kinetics.


## 2026-11-14 — expanded K_IV tau3 profile removes the narrow-grid boundary hits

The 27 eligible K_IV source-model post-peak waveforms were reprofiled with tau3 expanded from 0.6–2.0 ms to 0.1–5.0 ms at 2,801 equally spaced points (same approximate spacing as the previous 801-point grid). All 27 profile inputs remain the finite-positive fast-inactivation fits selected by the unchanged source routine: 34 commands were executed; the source current-selection threshold passed at 32 (-100 through +55 mV); five attempted fits (-100, -95, -90, -85 and -80 mV) returned non-finite fast taus; and the remaining 27 commands (-75 through +55 mV) returned finite positive values. The two threshold exclusions (-110 and -105 mV) and five non-finite attempts remain disjoint, explicitly recorded exclusions.

All 27 selected tau3 values are now strictly interior to the expanded 0.1–5.0-ms grid: there are **zero tau3 boundary hits**, compared with 11/27 hits on the narrower 0.6–2.0-ms search. The fitted tau3 values span 0.49725–2.9805 ms (median 1.38275 ms) and are **not globally monotonic** with voltage; the largest selected value is 2.9805 ms at -30 mV.

The signed added amplitude remains negative at all 27 commands, and the nonnegative-amplitude control still collapses to zero at all 27 selected optima. Full-waveform RMSE reduction is 59.945–80.386% (median 66.126%); first-10-ms RMSE reduction is 82.625–94.280% (median 89.018%). After-10-ms RMSE reduction ranges from -35.719% to +27.726% (median +20.817%): the late-window error still worsens at +25 through +55 mV (seven commands), even though the full-waveform fit improves at all 27 commands. The absolute added-amplitude magnitude is 0.0391–1.8791% of peak current (median 1.5976%).

The expanded interval removes the earlier grid-boundary ambiguity for this particular discrete search, but it does not establish a biological time constant or a voltage-dependent kinetic law. The selected tau3 profile remains non-source and non-monotonic; the fit's full-waveform objective can trade late-window accuracy for a lower total residual, as reflected by the seven depolarized commands whose after-10-ms error increases. These currents are generated by the deposited pure-human model under NEURON 9.0.2/VClamp, not raw human experimental recordings. Raw human K voltage-clamp NWB traces and individual K kinetic target CSVs remain absent from the inspected DataverseNL v3.0 inventory. Do not transfer tau3 or the signed term into Rust channel parameters or gate equations; the deposited helper, caller, NMODL and HumanJS runtime parameters remain unchanged. ADR-014 remains open, and the single-compartment spike-capable model remains exploratory and biologically unvalidated.

The strict CI reference is `research/HUMAN-L23-WILBERS-K-IV-TAU3-EXTENDED-RESIDUAL-SUMMARY.csv` (27 rows, 42 columns). The workflow regenerates the table from the current pinned NEURON 9.0.2 replay and compares every field with the committed CSV. GitHub Actions [43492075297](https://github.com/codexclai/HumanJS/actions/runs/43492075297) passed on exact code/data HEAD `8f4dc55bb0af0580b63e0bdac1c375b1d1df2e38` with all 32 workflow steps successful: rustfmt, Clippy, Rust tests (41 core unit, 3 synapse integration, 6 passive-membrane integration), 28 Python experiment scripts parsed, 46 Python tests, original Wilbers NEURON 9.0.2 Na/K protocol replays and validators, the 27-command 0.6–2.0-ms reference comparison, the new 27-command 0.1–5.0-ms profile and strict comparison with its committed 42-column CSV, the existing three-exponential residual validator, and repository policy.

No source helper/caller/NMODL, Rust runtime equation, channel parameter, or production mechanism changed. The extended grid resolves the previous profile-boundary hits but does not convert the residual correction into a biological mechanism or close ADR-014.

**Next concrete work:** assess how well-defined the interior tau3 values are by inspecting the local full-waveform objective around each selected minimum, while preserving the same source waveform, amplitude sign constraints and early/late diagnostics. Do not infer confidence intervals from this deterministic model-output profile, optimize only the early window, or transfer any term into Rust.


## 2026-11-14 — local K_IV tau3 objective-shape diagnostics

The summary is derived from the same 27 exact post-peak NEURON 9.0.2/VClamp model-current waveforms and the same extended 0.1–5.0-ms tau3 grid (2,801 equally spaced points). At each grid point, all four coefficients are refit against the **full-waveform RSS** while tau1 is fixed at that command's independently profiled local optimum and source tau2 remains 450 ms. For each command, the report records the normalized central second difference of relative RSS at the selected grid minimum, the immediately adjacent left/right relative RSS increases, and the contiguous grid basin around the minimum whose relative RSS increase is no more than 1%, 5%, or 10%.

All 27 selected minima are interior, and **none of the 1%, 5%, or 10% near-minimum basins touches either edge** of the 0.1–5.0-ms grid. The normalized local curvature spans 0.382621–17.942831 ms⁻² (median 3.541781 ms⁻²). The contiguous 1%-RSS-increase basin spans 0.06475–0.45500 ms (median 0.14875 ms); the 5% basin spans 0.14875–1.02550 ms (median 0.33425 ms); and the 10% basin spans 0.21175–1.46125 ms (median 0.47600 ms).

The broadest profile occurs at -30 mV: normalized curvature 0.382621 ms⁻², with 1%, 5%, and 10% basin spans of 0.45500, 1.02550, and 1.46125 ms. The narrowest occurs at +55 mV: curvature 17.942831 ms⁻², with corresponding spans of 0.06475, 0.14875, and 0.21175 ms. Thus, although the expanded grid removed the previous boundary clipping, the local objective width is voltage-dependent and some selected minima are appreciably flatter than others.

These are **descriptive grid-basin spans of a deterministic model-output objective**, not statistical confidence intervals, measurement uncertainty, or biological uncertainty estimates. No noise model was fitted. The widths are conditional on tau1 being held at its selected per-voltage local optimum; they do not account for coupling to tau1 or uncertainty in the source fit. The waveforms are generated by the deposited pure-human K mechanism under NEURON 9.0.2/VClamp, not raw human experimental K-current recordings. Raw human K voltage-clamp NWB traces and individual K kinetic target CSVs remain absent from the inspected DataverseNL v3.0 inventory. The deposited fitting helper, caller, pure-human NMODL, HumanJS Rust equations, and channel parameters remain unchanged. Do not transfer tau3 or the signed residual correction into Rust channel kinetics. ADR-014 remains open, and the single-compartment spike-capable model remains exploratory and biologically unvalidated.

The canonical per-voltage reference is `research/HUMAN-L23-WILBERS-K-IV-TAU3-PROFILE-SHAPE.csv` (27 rows, 26 columns). The main workflow regenerates the objective shape from the same exact source replay and strictly compares the 26 fields across all 27 voltages. GitHub Actions [43495085251](https://github.com/codexclai/HumanJS/actions/runs/43495085251) passed on exact code/data HEAD `dfac63b6c99c6c77981a390e4b3da25affd45dfe` with all 33 workflow steps successful: Rust formatting/Clippy/tests (41 core unit, 3 synapse integration, 6 passive-membrane integration), 29 Python experiment scripts parsed, 47 Python tests, original Wilbers NEURON 9.0.2 Na/K protocol replays and validators, strict comparisons of the baseline and expanded 27-row K_IV residual summaries, strict comparison of the 27-row/26-column tau3 objective-shape reference, the three-exponential residual validator, and repository policy.

The extended-grid minima are therefore interior and the chosen objective profile has a measurable finite local basin at all 27 commands, but the basin width varies substantially with voltage. The results remain conditional on fixed tau1 and source tau2, and are not statistical parameter uncertainty. The source fitting routine/caller/NMODL and all Rust channel equations and parameters remain unchanged. ADR-014 remains open.

**Next concrete work:** inspect the +55-mV upper-bound slices with a wider tau3 domain while retaining the same nine tau1 nodes and full-waveform objective; determine whether the sign reversal in the fitted added coefficient persists away from the 10-ms limit. Keep this bounded to the predeclared representative command, and treat it only as numerical sensitivity of deterministic model currents. Do not call the result biological kinetics or transfer any fit term into Rust.


## 2026-11-14 — conditional K_IV tau1–tau3 sensitivity surface

The predeclared subset is -30, -60, and +55 mV, representing the broadest, median, and narrowest single-tau1 1% objective basins in the preceding profile-shape audit. At each command, nine tau1 values span the existing local 6% refinement interval around the already selected local tau1; the middle node is that reference tau1. At every tau1 node, tau3 is profiled over 0.1–10.0 ms on 5,601 equally spaced points. All coefficients are refit at each tau3 against the **full waveform RSS**, with the original two current amplitudes and steady offset constrained nonnegative, the added third amplitude signed, and source tau2 fixed at 450 ms. First-10-ms and after-10-ms RMSE remain diagnostics of the same full-waveform fit, not separate objectives. The result is a conditional tau1–tau3 sensitivity surface on three waveforms, not a global fit across all 27 voltages.

The 27-row/44-column reference is `research/HUMAN-L23-WILBERS-K-IV-TAU1-TAU3-SURFACE-SUMMARY.csv`. It is regenerated from the same source-replay waveforms and strictly compared field-by-field in CI. | Command | Existing local tau1 (ms) | Existing single-tau1 tau3 (ms) | Tau1 local window (ms) | Conditional tau3 minima over the window (ms) | Best sampled surface tau1 / tau3 (ms) | Full-RSS reduction vs center tau1 slice |
|---:|---:|---:|---:|---:|---:|---:|
| -30 mV | 112.958 | 2.9805 | 106.021–119.556 | 2.057–5.092 | 107.755 / 4.339 | 96.276% |
| -60 mV | 251.949 | 1.56825 | 237.580–267.909 | 1.224–2.140 | 244.764 / 1.802 | 96.955% |
| +55 mV | 17.195 | 0.49725 | 16.134–18.194 | 0.498–10.000 | 17.195 / 0.498 | 0% |

At -30 and -60 mV all nine conditional tau3 minima are interior to the 0.1–10-ms grid. Allowing tau1 to move within its existing local interval materially shifts the sampled full-RSS minimum: the -30-mV minimum is at tau1 107.755 ms/tau3 4.339 ms, while the -60-mV minimum is at 244.764 ms/1.802 ms. Relative to the center tau1 slice, their full-waveform RSS falls by 96.276% and 96.955%, respectively. These are reductions in the objective RSS, not RMSE percentages.

The +55-mV surface behaves differently. Six of its nine tau1 slices select tau3 at the expanded 10-ms upper boundary. Its best sampled surface point remains at the center tau1 (17.195 ms) and tau3 0.49777 ms, so the global full-RSS objective does not improve relative to that center slice. The signed extra amplitude is negative at tau1 indices 0–4 but positive at indices 5–8. Thus, the sign and fitted short component are sensitive to the allowed tau1 change at this depolarized command, and the 10-ms upper limit still fails to localize several conditional minima.

At the center tau1 node, the contiguous 1%/5%/10% objective-basin spans are 0.4561/1.0254/1.4620 ms at -30 mV, 0.1485/0.3359/0.4756 ms at -60 mV, and 0.06541/0.14673/0.21037 ms at +55 mV. These widths are conditional slices through a discrete, deterministic objective surface; they are not statistical uncertainty intervals.

This surface demonstrates that the previously reported tau3 curvature and basin width conditional on fixed tau1 do not capture all tau1–tau3 coupling. The strong objective reductions at -30 and -60 mV arise from shifting tau1 inside the existing 6% local window while refitting the signed short component. At +55 mV, both the tau3 boundary and a sign reversal in the added coefficient show that the correction is not stable under tau1 variation. The 0.1–10-ms range therefore does not resolve all +55-mV conditional profiles.

All inputs are deterministic NEURON 9.0.2/VClamp outputs from the deposited pure-human K model, not raw human experimental K-current recordings. Raw human K voltage-clamp NWB traces and individual kinetic target CSVs remain absent from the inspected DataverseNL v3.0 inventory. No noise model was fitted; do not interpret the basin widths as confidence intervals, measurement uncertainty, biological uncertainty, or human channel kinetics. The deposited helper/caller/NMODL, HumanJS Rust equations, and channel parameters remain unchanged. Do not transfer tau3 or the signed correction into Rust. ADR-014 remains open and the single-compartment spike-capable model remains exploratory and biologically unvalidated.

GitHub Actions [43500401868](https://github.com/codexclai/HumanJS/actions/runs/43500401868) passed on exact code/data HEAD `5e41b681bcb6307921f466c90b4fbe680d1f2681` with all 34 workflow steps successful. Hosted verification included Rust formatting/Clippy and tests (41 core unit, 3 synapse integration, 6 passive-membrane integration), syntax parsing of 30 Python experiment scripts, 48 Python tests, original Wilbers NEURON 9.0.2 Na/K protocol replays and validators, strict comparisons of the baseline and extended 27-row K_IV profiles, the 27-row/26-column fixed-tau1 objective-shape reference, the new 27-row/44-column tau1–tau3 surface reference, the three-exponential residual validator, and repository policy (16 required files).

No source helper/caller/NMODL, Rust equations, or channel parameters changed. The surface was added as an exploratory diagnostic only; ADR-014 remains open.


## 2026-11-14 — extended +55 mV K_IV tau1–tau3 surface (0.1–40 ms)

### Method

The previous +55 mV conditional surface used nine fixed tau1 nodes in the already defined local 6% refinement interval and a 0.1–10.0 ms tau3 grid. Six of nine conditional minima were pinned at the 10 ms upper limit, and the added signed coefficient was positive at four of those high-tau1 nodes. To test whether that behavior persisted away from the limit, the same nine tau1 nodes and exact source waveform were reprofiled over 0.1–40.0 ms on 11,401 equally spaced tau3 points (0.0035 ms spacing). At every tau3 point all four coefficients were refit against full-waveform RSS; source tau2 remained fixed at 450 ms; a1, a2 and the steady offset remained nonnegative while a3 remained signed. First-10-ms and after-10-ms RMSE were retained as diagnostics, not alternative objectives.

### Results

All **nine of nine selected tau3 minima are now interior** to the expanded 0.1–40 ms grid, ranging from 0.4955 to 28.6495 ms. Compared with the 0.1–10 ms surface, the six upper-bound minima disappear. More importantly, the signed added coefficient is now negative at all nine tau1 nodes. The four positive coefficients previously found at tau1 indices 5–8 do not persist when tau3 can move beyond 10 ms. That makes the earlier sign reversal consistent with a truncated conditional fit, not a stable feature of this surface.

| Tau1 grid index | Tau1 (ms) | Selected tau3 (ms) | Signed a3 (mA/cm²) |
|---:|---:|---:|---:|
| 0 | 16.134424 | 13.4280 | -0.0965012 |
| 1 | 16.399624 | 11.9685 | -0.0440700 |
| 2 | 16.664824 | 8.4615 | -0.0162458 |
| 3 | 16.930024 | 0.9540 | -0.0103225 |
| 4 | 17.195223 | 0.4955 | -0.0093360 |
| 5 | 17.444952 | 28.6495 | -0.0070376 |
| 6 | 17.694681 | 23.5780 | -0.0239165 |
| 7 | 17.944409 | 21.6355 | -0.0551058 |
| 8 | 18.194138 | 20.6030 | -0.1105878 |

The lowest full-waveform RSS remains at the middle tau1 node (17.195223 ms), with tau3=0.4955 ms; the global surface minimum is therefore still the centre-tau1 fit. The tau3 minima nevertheless move substantially across the allowed tau1 window, spanning approximately 0.50–28.65 ms. This is strong tau1–tau3 coupling in the selected numerical fit family, not an identified biological kinetic process.

The *selected minima* are no longer at the tau3 search boundary, but one local basin remains incompletely enclosed: at tau1 index 5 (17.444952 ms), its 1% basin is interior ([23.9805, 34.5365] ms), while the 5% basin reaches 40 ms ([19.3605, 40] ms; 20.6395 ms span) and the 10% basin also reaches 40 ms ([17.446, 40] ms; 22.554 ms span). The other eight tau1 slices have 1%, 5%, and 10% basin edge flags clear. Thus the point estimate is interior at every node, but the broader 5% and 10% neighbourhood at index 5 is still truncated by the current 40 ms ceiling.

The complete reference is `research/HUMAN-L23-WILBERS-K-IV-TAU1-TAU3-55MV-40MS-SUMMARY.csv` (9 rows, 44 columns). It preserves the selected tau3 and coefficients, full/early/late RMSE diagnostics, relative full-RSS values, conditional basin bounds/spans/point counts and boundary flags. The workflow regenerates this surface from the same original NEURON 9.0.2/VClamp replay and compares all 44 fields against the committed reference.

### Interpretation and limitations

This is a descriptive sensitivity calculation on deterministic model-generated current, not raw human experimental K-current data, a statistical confidence region, measurement uncertainty, or biological uncertainty. The source fitting helper, source caller, pure-human NMODL, HumanJS Rust equations and channel parameters remain unchanged. Raw human K voltage-clamp NWB traces and individual K kinetic target CSVs remain absent from the inspected DataverseNL v3.0 inventory. Do not transfer tau3 or the signed correction into Rust channel kinetics. ADR-014 remains open and the single-compartment spike-capable model remains exploratory and biologically unvalidated.

GitHub Actions [43552164142](https://github.com/codexclai/HumanJS/actions/runs/43552164142) passed on exact code/data HEAD `cdba13783f435645fb5f194a0e2bd2d5858ce1ab` with all 35 job steps successful and no failed steps. Hosted checks included Rust formatting and Clippy, Rust tests (41 core unit, 3 synapse integration, 6 passive-membrane integration), syntax parsing of 30 Python experiment scripts, 48 Python tests, the original Wilbers NEURON 9.0.2 Na/K protocol replays and validators, strict comparisons of the baseline and expanded 27-row K_IV residual summaries, the 27-row/26-column fixed-tau1 objective-shape reference, the 27-row/44-column three-voltage tau1–tau3 surface, the new 9-row/44-column +55 mV 0.1–40 ms surface, the three-exponential residual validator, and repository policy (16 required files).

The fixed-tau1 0.1–120 ms extension is complete; its 1%, 5%, and 10% conditional basins are all interior, and CI now compares the regenerated 39-column summary field by field. No biological parameter or HumanJS channel equation is inferred from this numerical result.


## 2026-11-14 — +55 mV fixed-tau1 K_IV basin extended to 120 ms

The previous +55 mV conditional tau1–tau3 surface left the 5% and 10% relative-full-RSS basins at tau1 index 5 truncated by its 40 ms upper bound. This follow-up fixes tau1 at 17.44495210313133 ms (the same index-5 node), keeps tau2=450 ms, and profiles tau3 from 0.1 to 120 ms on 34,258 equally spaced points. All four linear coefficients are refit at every tau3 grid point against full-waveform RSS. The first two exponential amplitudes and steady offset remain nonnegative; the added third-exponential amplitude is signed. A nonnegative-amplitude control is refit at the signed optimum. Early/late RMSE are diagnostic windows only.

Results from the exact source-replay waveform:
- Selected tau3: 28.649619055959366 ms; the minimum is interior.
- 1% basin: 23.98059958548618–34.53664360568643 ms; span 10.55604402020025 ms; 3,017 grid points; no edge contact.
- 5% basin: 19.36058031935079–44.45918498409085 ms; span 25.098604664740055 ms; 7,172 grid points; no edge contact.
- 10% basin: 17.44607233558105–55.14822955892227 ms; span 37.70215722334122 ms; 10,773 grid points; no edge contact.
- Signed a3: -0.007037549809997629 mA/cm². The nonnegative control clips a3 to zero; its full-waveform RSS is 88.92330427008206% higher than the signed-fit RSS.
- Full-waveform RMSE: 0.00022063629885869346 mA/cm².

Thus all three declared objective basins are enclosed within 0.1–120 ms, resolving the previous 40 ms truncation for this one fixed-tau1 slice. It does not establish global identifiability or quantify tau1–tau3 joint uncertainty.

The canonical one-row/39-column result is `research/HUMAN-L23-WILBERS-K-IV-TAU1-TAU3-55MV-INDEX5-120MS-SUMMARY.csv`. The workflow regenerates the result from the exact post-peak NEURON 9.0.2/VClamp source replay and compares every numeric, integer, and Boolean field against the committed record. GitHub Actions [43567023221](https://github.com/codexclai/HumanJS/actions/runs/43567023221) passed on exact code/data HEAD `d8b623ba4fd0ac1224b4c5ac52b1fce64592851f` with all 36 job steps successful. The run included rustfmt, Clippy, Rust workspace tests (41 core unit, 3 synapse integration, 6 passive-membrane integration), 32 Python script syntax checks, 50 Python tests, the original NEURON Na/K source replays and validators, every established K_IV profile/surface comparison, the new 120 ms profile generation, and repository policy. The main workflow now enforces and passes the field-by-field `--expected` comparison on exact HEAD `2be947d96a7e079bb05b799e6a01fa704acd1004` in run [43568457823](https://github.com/codexclai/HumanJS/actions/runs/43568457823).

This remains a descriptive numerical diagnostic on deterministic model-generated current, not raw human experimental current. Basin spans are not statistical confidence intervals or uncertainty estimates. The signed correction is not a biological gate or positive ionic component. No source helper, caller, pure-human NMODL, Rust equation, or channel parameter was modified. Raw human K current traces and individual kinetic target CSVs remain unavailable in the inspected DataverseNL v3.0 inventory; ADR-014 remains open and the exploratory spike-capable model remains biologically unvalidated.


## Final verification and comparison precision — 2026-11-14

The live main branch is `2be947d96a7e079bb05b799e6a01fa704acd1004`, with a complete 120-entry tree, one branch (`main`), and no open issues or pull requests. Run [43568457823](https://github.com/codexclai/HumanJS/actions/runs/43568457823) passed all 36 job steps on that exact HEAD. It parsed 32 Python experiment scripts, passed 51 Python tests, passed the Rust formatting/Clippy/test steps, replayed the original Wilbers Na/K source protocols in NEURON 9.0.2, and passed every established reference comparison. For the new +55 mV fixed-tau1 analysis, CI regenerated the 0.1–120 ms profile and printed: "Fixed-tau1 K_IV profile matches every field of the committed reference."

Two earlier failed runs remain part of the audit trail and were corrected without changing scientific acceptance criteria. Run [43567926270](https://github.com/codexclai/HumanJS/actions/runs/43567926270) found a 1.62×10⁻¹² absolute difference in the very small left-neighbour RSS-slope metric against a 1×10⁻¹² absolute tolerance. The comparison now applies 1×10⁻¹⁰ absolute tolerance only to the left/right neighbour-delta percentage metrics; relative tolerance remains 2×10⁻⁵ and every other field retains its original tolerance. Run [43568339733](https://github.com/codexclai/HumanJS/actions/runs/43568339733) then showed the rejection test's fixed 1×10⁻³ perturbation could remain within relative tolerance for its fixture. The test perturbation is now the greater of 0.1% of the fixture's actual metric magnitude or 1×10⁻⁶. This verifies acceptance of roundoff-scale numerical drift and rejection of a material change. Final run [43568457823](https://github.com/codexclai/HumanJS/actions/runs/43568457823) passed all steps.
