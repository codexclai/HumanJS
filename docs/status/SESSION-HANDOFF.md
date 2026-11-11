# HumanJS — current session handoff

**Updated:** 2026-11-11  
**Canonical repository:** `codexclai/HumanJS`, branch `main` only.  
**Verified source/code commit:** `5dfba6257ffb375bf741b8149026f13274600ae5`.  
**Documentation reconciliation:** subsequent commits on `main`; verify the live HEAD and workflow before using this handoff in a later session.

## Verified repository state at start of this continuation

- Public repository; default branch `main`.
- Full tree retrieved: 55 entries, not truncated.
- Live branch listing contained exactly `main`.
- No open issues or pull requests were returned.
- GitHub Actions run `42973247775` passed on exact head `5dfba6257ffb375bf741b8149026f13274600ae5`: https://github.com/codexclai/HumanJS/actions/runs/42973247775. Rust formatting, Clippy, workspace tests, Python syntax validation, and repository policy all passed.
- This chat did not complete a fresh local clone because DNS resolution failed. Do not claim a local Rust test run.

## Current HumanJS implementation

The Rust core `crates/humanjs-core` contains three mechanisms:

1. A validated single-compartment passive RC membrane, analytically integrated for piecewise-constant injected current.
2. An effective human L2/L3 glutamatergic synapse with separate AMPA/NMDA conductance kernels, voltage-dependent NMDA magnesium unblock, deterministic short-term availability/depression/recovery, and transactional coupling to the passive membrane.
3. An **exploratory, not scientifically accepted** human L2/L3 single-compartment Na+/K+ conductance model in `crates/humanjs-core/src/ion_channels.rs`. It integrates voltage and five gates with fixed-step RK4 and can generate one spike for its software test pulse.

The third mechanism was committed before the scientific evidence gate in ADR-014 was closed. It must be described accurately as existing code, but it does not satisfy that gate and must not be called biologically validated. It is one lumped electrical compartment, not an anatomical soma/AIS neuron, intact pyramidal neuron, axon, dendritic tree, or propagating neuron.

### Exploratory model parameter choices and unresolved issues

- Na+ gates use the pure Wilbers human `na_human.mod` values.
- K+ gates use the pure `k_human.mod` values that match Table S2 and the first optimizer result. The fitting script explicitly applies this first result; its trailing alternate dictionary is a bare literal and is never applied.
- The K+ script assigns `h12factor_k_human=10.5`, but all three inspected pure/hybrid K+ NMODL variants contain only a commented-out `h2tau = h1tau * h12factor` line; the helper does not read the Python attribute.
- The article's 14-parameter model description includes two inactivation steady-state values and independent `Rb`; the deposited scripts fix the former from experiment and constrain `Rb = Ra`, leaving 11 optimizer variables.
- Current-clamp fitted conductance densities (114.48 pS/μm² Na+, 29.05 pS/μm² K+) were fitted against cross-species mean AP features; they are not direct human channel-density measurements.
- The 10 μm cylindrical geometry, 34°C, −10 mV channel shift, +15 mV reversal offsets, 1 μF/cm² capacitance, Rm=10,000 Ω·cm² leak, and 20 μs maximum step follow the deposited current-clamp helper.
- The Rust `trap0` uses a stable analytic limit at the mathematical singularity. This is not an exact reproduction of the source's branch behavior. The pure NMODL files declare its prefactor as `/ms`, but the voltage-valued numerator requires `mV⁻¹·ms⁻¹`; HumanJS keeps numeric values and uses the equation-consistent internal unit pending verification against the original NEURON unit contract.

Current code tests cover the analytic `trap0` limit/continuity, half-voltage steady states, potassium fast/slow inactivation branch constants and conductance fractions, positive finite time constants over a bounded voltage scan, Q10 scaling, one-spike waveform scale, approximate step-size convergence, reset, and transactional failure. These are software tests, not biological validation.

## Human spike-initiation source audit and external reproduction

Canonical evidence: `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`.  
Eyal reproduction: `experiments/HUMAN-L23-SPIKE-MODEL-REPRODUCTION.md`.  
Runner: `experiments/reproduce_eyal_figure7a.py`.

### Eyal et al. (2018)

- Official ModelDB archive for model 238347 retrieved; 139,316,573 bytes; SHA-256 `12dfd8b8fb38b28136d6904da69aaf5e200fa5fb64cd03d845a96d972057354b`. Not stored in HumanJS.
- Canonical HOC templates and Table S4 parameter assignments mapped for all six cells.
- Nine inserted active conductance mechanisms in soma/axon plus `CaDynamics_E2`; `Ca_HVA` is not inserted by these six templates; `NMDA.mod` belongs to separate synaptic workflows.
- Two-section 60 μm axon stub; dendritic branches passive; channel kinetics assumed rodent-like.
- Ten mechanisms actually inserted by the six templates compiled with NEURON 9.0.2.
- Six-cell Figure 7A construction/stimulus sequence reproduced with the checked-in Python 3 script against released human current-clamp repetitions. Model/data timing, width, and peak differences remain. This is not an independent refit, exact trace match, HumanJS implementation, or biological validation.

### Wilbers et al. (2023)

- Pure human `na_human.mod` and `k_human.mod` retrieved from the CC0 DataverseNL deposit, checksum-verified, compiled unchanged, and probed in NEURON 9.0.2.
- Exact-singularity probes exposed non-finite `trap0` values. The active Na+ table's 200 nodes were finite; direct Na+ rates with table disabled were non-finite at exact singularities. K+ has no active table; exact singularities return non-finite values and two opposite-sign branch triggers produce negative inactivation time constants.
- The K+ source matches the parameter values actually applied by the script; its alternate dictionary is a bare literal and is not applied. The 14-versus-11 parameter count is explained by fixed inactivation steady states and `Rb = Ra`. The fit script's `h12factor_k_human` assignment is not declared in the pure mechanism or read by `channel_tools.py`. The source's printed Table S2 rate-prefactor unit (`ms^-1`) is dimensionally incomplete for the voltage-valued `trap0` numerator; the code interprets the coefficient as `mV^-1 ms^-1`.
- Full Wilbers voltage-clamp fitting was not reproduced from raw NWB traces; public workbooks are summary fits and original NWB traces were not present in the 65-file Dataverse listing examined.

## Corrective documentation work completed in this continuation

- Updated `docs/BOOT.md` to describe the three current CPU mechanisms and classify the spike model as exploratory.
- Updated `docs/architecture/SYSTEM-ARCHITECTURE.md` with the model's actual equations/parameter provenance boundary and an explicit scientific acceptance checklist.
- Updated `docs/decisions/DECISIONS.md`: ADR-014 remains the evidence gate; ADR-016 records the exploratory implementation and its unaccepted status.
- Updated `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md` to remove the obsolete claim that no spike code exists and reconcile the K+ applied fit dictionary, the article's 14-parameter description versus the deposited 11-variable optimizer, the unused `h12factor_k_human` assignment, and the `trap0` prefactor dimensional convention.
- Added regression tests for potassium slow inactivation/recovery constants, the three-component conductance fractions, and human gate half-voltage steady states. The half-voltage test accounts for the current-clamp −10 mV channel shift.
- Corrected the `RatePrefactor` dimensional name and error label to `mV^-1 ms^-1`; no channel parameter values were changed.
- Updated `docs/roadmap/MASTER-ROADMAP.md` to keep the accepted somatic-patch milestone unchecked and classify existing code as provisional.
- Reconciled `docs/status/STATUS.md` with the current implementation and passing verification run.
- This handoff is the final documentation file to update after this commit.

## Next concrete work

1. Verify the live main HEAD and the latest workflow after documentation updates.
2. Independently reproduce the Wilbers K+ fast/slow inactivation and recovery protocols from the source equations; inspect any alternate mechanism variants separately from the pure fit path.
3. Verify the equation-level `trap0` prefactor units against the NMODL unit declarations and NEURON's unit checker; preserve the discrepancy between the printed Table S2 label and dimensional analysis until resolved from the source's unit contract.
4. Build independent numerical comparisons for Na+/K+ steady states, time constants, fast/slow recovery and source-singularity neighborhoods; reproduce published voltage-clamp protocols where raw data permit.
6. Verify the cross-species current-clamp fit target and geometry/reversal/channel-shift setup before promoting the model.
7. Keep AIS-resolved modeling separate. Human NaV1.2/NaV1.6 immunostaining does not provide functional conductance densities or gating parameters.

No biological validation, clinical validity, whole-brain functionality, or consciousness claim is made. Save/restore, Rust-native concurrency, the configurable 10,000-unit default, JSON model loading, Python, C/C++, and WGSL remain unimplemented.
