# HumanJS — current status

**As of:** 2026-11-11  
**Stage:** two foundational Rust CPU mechanisms plus one exploratory, unaccepted human L2/L3 single-compartment spike-capable mechanism. HumanJS is not a whole-brain simulator.

## Canonical repository and live state

- Repository: `codexclai/HumanJS`, public, default branch `main`.
- `main` is the only branch; the live branch listing returned exactly `main`.
- No open issues or pull requests were returned by live checks.
- Latest source/code commit: `5dfba6257ffb375bf741b8149026f13274600ae5`. Latest K+ protocol/optimizer audit: `d2fc1d2acb09b4011a7b018276e119e0d1cb8ed9`.
- GitHub Actions run `42973247775` passed on exact head `5dfba6257ffb375bf741b8149026f13274600ae5`: https://github.com/codexclai/HumanJS/actions/runs/42973247775. Rust formatting, Clippy, Rust workspace tests, Python syntax validation, and repository policy all passed.
- This chat did not complete a fresh local clone because network DNS resolution failed. No local Rust test run is claimed.
- A fresh local clone in this chat was not completed because network DNS resolution failed. No local cargo test run is claimed.

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

Current software tests cover the analytic rate limit/continuity, human gate half-voltage steady states, potassium fast/slow inactivation branch constants and conductance fractions, positive finite time constants over a bounded voltage scan, Q10 scaling, one-spike waveform scale, approximate step-size convergence, reset, and transactional failure. They do not reproduce the full published voltage-clamp protocols or independently validate the fitted current-clamp model. See ADR-014, ADR-016, `docs/architecture/SYSTEM-ARCHITECTURE.md`, and `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`.

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
- This closes the source-protocol/optimizer audit, not the numerical reproduction gate. A Rust clamp-protocol replay and comparison to available paper-level summaries remain; raw-trace and exact per-voltage target reproduction cannot be claimed from the inspected public deposit.

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

Keep the spike-capable code provisional. Reproduce the Wilbers K+ fast/slow inactivation and recovery protocols independently; audit rate-prefactor dimensional conventions and temperature semantics; compare gate curves/time constants/recovery behavior against the published voltage-clamp protocols and human summaries; and verify the current-clamp conductance-fit objective and setup. Add independent validation tests before considering promotion. Keep the single-compartment preparation-equivalent distinct from any anatomical soma/AIS model. Do not claim biological validation from software tests or external model reproduction.
