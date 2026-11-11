# HumanJS — current session handoff

**Updated:** 2026-11-11  
**Canonical repository:** `codexclai/HumanJS`, branch `main` only.  
**Latest implementation/CI change:** `6e1842579113ddb1542628e033107b07db20a526`.  
**Latest research-data record:** `3a13199d21c58377dbd3517ab47c4984267d6753`.  
Verify the live HEAD and newest workflow before relying on this handoff.  
**Documentation reconciliation:** subsequent commits on `main`; verify the live HEAD and workflow before using this handoff in a later session.

## Verified repository state at start of this continuation

- Public repository; default branch `main`.
- Full tree retrieved: 55 entries, not truncated.
- Live branch listing contained exactly `main`.
- No open issues or pull requests were returned.
- GitHub Actions run `43016424733` passed on exact code head `660dee7287376720d37d96dac939941fe26df7d6`: https://github.com/codexclai/HumanJS/actions/runs/43016424733. Rust formatting, Clippy, workspace tests (including all 50 conditions in the K+ recovery protocol), Python syntax validation, and repository policy all passed.
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

Current code tests cover the analytic `trap0` limit/continuity, half-voltage steady states, potassium fast/slow inactivation branch constants and conductance fractions, positive finite time constants over a bounded voltage scan, Q10 scaling, the K+ activation/inactivation clamp replay, all 50 combinations of five recovery voltages and ten recovery delays against independent model-side gate references, one-spike waveform scale, approximate step-size convergence, reset, and transactional failure. These are software tests, not biological validation.

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


### Wilbers K+ voltage-clamp protocol and fitting objective audit

- Directly inspected Dataverse files `fit_k_hh_cma_human.py` (326237), `channel_tools.py` (326242), `channel_kinetics.py` (326241), and pure `k_human.mod` (318647), from dataset DOI 10.34894/L5J0SD version 3.0.
- Activation/inactivation model clamp: −140 mV for 20 ms, each test voltage for 500 ms, +60 mV for 50 ms, then −140 mV for 100 ms. `K_IV` scans −110 to +55 mV in 5-mV increments; `K_IV_ss` scans −110 to +50 mV in 10-mV increments.
- Recovery model clamp: −120 mV for 2 ms, +40 mV for 5,000 ms, recovery at −90/−85/−80/−75/−70 mV for 4, 144, 484, 1,024, 1,764, 2,704, 3,844, 5,184, 6,724, and 8,464 ms, then +40 mV for 5 ms. Temperature is 34°C. Deactivation protocol exists in the helper but is not used by the optimizer.
- The human optimizer fits six inactivation/recovery parameters, then activation kinetics, then activation steady state. Its fast-recovery target is hard-coded to 236.824345 ms, commented as the mean of human and mouse values. Slow inactivation (450 ms) and slow recovery (2,789.7929 ms) are fixed mechanism settings, not fitted variables. Reported inactivation/recovery component scores are fast 0.0721, slow 2.4386, and fast recovery 0.00235; the slow component has 0.05 relative weight.
- The public 65-file Dataverse inventory lacks the `Experimental means/k_tau_*.csv` files read by the fitting helper, the `data_fig5.xlsx` referenced by the K plotting script, and raw K voltage-clamp NWB current traces. `K_data_fig2.xlsx` is AP-clamp repeated-waveform amplitude data, not the missing voltage-step kinetic dataset.
- Rust unit tests in `crates/humanjs-core/src/ion_channels.rs` replay activation, inactivation, and recovery command sequences with exact first-order gate updates. The recovery regression now covers all five deposited recovery voltages × all ten delays (50 combinations) and checks independent model-side reference conductance values plus monotonic recovery at each voltage. A full `K_IV_ss` series uses the deposited −110 to +50 mV, 10-mV grid. Transparent half-range interpolation gives −3.25 mV activation midpoint, −51.48 mV inactivation midpoint, and 0.936 availability at −80 mV; all fall within the published human group mean ± SD. This is a coarse summary comparison and software regression, not the source nonlinear fit or raw-trace validation.
- Workflow `43016424733` passed formatting, Clippy, Rust workspace tests, Python syntax validation, and repository policy on code commit `660dee7287376720d37d96dac939941fe26df7d6`. The local clone attempt still fails because GitHub DNS cannot be resolved in this environment; no local Rust test run is claimed.


### NEURON 9.0.2 unit-check result

- Original `k_human.mod` and `na_human.mod` compile unchanged with `nrnivmodl`, but the compiler warns that GLOBAL `tadj` assignment is not thread-safe.
- Original `modlunit` runs stop at the untyped `trates(v+vshift)` call (K line 82; Na line 80). Temporary diagnostic copies with typed signatures expose the declared `/ms` versus equation-required `mV^-1 ms^-1` mismatch, the fallback's missing prefactor/wrong dimensions, the wrong-sign branch predicate, the dimensionful Q10 exponent, and missing mV units on activation midpoint/slope parameters.
- Temporary typed K/Na copies pass `modlunit` 9.0.2 only after those unit corrections and replacing the active fallback with the source's commented-out `a*q` limit. No Dataverse source was modified.
- The original NMODL is therefore not a unit-checked reference implementation. HumanJS's Rust rate units and analytic singularity handling are equation-consistent corrections, not exact reproduction of the source branch.


### Supplementary Figure S5: verified legend and first calibrated digitization

- Retrieved the official 13-page supplement from the new PMC AWS Article Dataset object: https://pmc-oa-opendata.s3.amazonaws.com/PMC10569700.1/sciadv.ade3300_sm.pdf. Size 1,468,232 bytes; SHA-256 `dfa1daaf4dd0e3979bac84b9cb8b1874c4514d40588969a21d7766a7f12f2a1d`.
- Rendered Figure S5 page 7 and visually verified the legend: red model line/human open-circle experimental means; blue model line/mouse cross experimental means. The caption duplicates “(I)” for fast inactivation; the actual plotted panel is labelled J.
- Digitized panel K slow-inactivation group means: 10 red human open-circle points and 10 blue mouse cross points at −30 to +60 mV. The checked-in CSV records pixel centers, axis calibration, source checksum, and conservative ±2.5 mV / ±25 ms plot-reading uncertainty. These uncertainties are not biological SD.
- Added `experiments/validate_wilbers_fig_s5_digitization.py` and a CI step checking provenance, marker mapping, counts, and axis-derived values. This validates the transcription/calibration, not the biology.
- The panel's two model curves are visually near the fixed 450-ms slow-inactivation setting. Experimental markers vary substantially with voltage and between group means, consistent with the authors' statement that their HH models did not accurately reproduce K+ inactivation.
- Main-text summary values: activation V1/2 human −3.0 ± 5.9 mV (n=13), mouse −7.9 ± 6.0 mV (n=29), P=0.02; inactivation V1/2 human −52.7 ± 6.0 mV (n=11), mouse −65.0 ± 5.3 mV (n=26), P<10⁻⁶; resting-potential availability human 0.94 ± 0.05, mouse 0.86 ± 0.06. Human K+ currents activate faster at lower voltages; fast/slow inactivation and recovery time constants were described as similar between species, although human currents recover to a larger proportion.
- Remaining: digitize panels I, J, M, and N. The exact Dataverse `Experimental means/k_tau_*.csv` files and raw per-cell K+ voltage-clamp traces remain absent. No raw-trace reproduction or biological validation is claimed.

## Corrective documentation work completed in this continuation

- Updated `docs/BOOT.md` to describe the three current CPU mechanisms and classify the spike model as exploratory.
- Updated `docs/architecture/SYSTEM-ARCHITECTURE.md` with the model's actual equations/parameter provenance boundary and an explicit scientific acceptance checklist.
- Updated `docs/decisions/DECISIONS.md`: ADR-014 remains the evidence gate; ADR-016 records the exploratory implementation and its unaccepted status.
- Updated `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md` to remove the obsolete claim that no spike code exists and reconcile the K+ applied fit dictionary, the article's 14-parameter description versus the deposited 11-variable optimizer, the unused `h12factor_k_human` assignment, and the `trap0` prefactor dimensional convention.
- Added regression tests for potassium slow inactivation/recovery constants, the three-component conductance fractions, and human gate half-voltage steady states. The half-voltage test accounts for the current-clamp −10 mV channel shift.
- Corrected the `RatePrefactor` dimensional name and error label to `mV^-1 ms^-1`; no channel parameter values were changed.
- Updated `docs/roadmap/MASTER-ROADMAP.md` to keep the accepted somatic-patch milestone unchecked and classify existing code as provisional.
- Retrieved and rendered the official PMC AWS supplement; visually mapped the Figure S5 series and added an uncertainty-qualified panel K digitization.
- Added a stdlib-only validator for the Figure S5 CSV and wired it into `.github/workflows/repository-policy.yml`.
- Updated `docs/BOOT.md`, `docs/status/STATUS.md`, `docs/REPOSITORY-STRUCTURE.md`, and `docs/roadmap/MASTER-ROADMAP.md` with the new research state.
- This handoff is the final documentation file to update after this commit.

## Next concrete work

1. Verify the live `main` HEAD and the workflow that executes the new Figure S5 digitization validator.
2. Digitize Figure S5 panels I (activation), J (fast inactivation), M (fast recovery), and N (slow recovery), keeping human, mouse, and model series separate and recording axis/point uncertainty.
3. Compare the panel-level group-mean curves with the deposited K+ equations and fixed model constants. Do not treat the pooled 236.824345-ms fast-recovery optimizer target as a human-only target.
4. Preserve the absence of the exact Dataverse K tau CSVs and raw voltage-clamp NWB traces; no fitting or biological-validation claim is justified without them.
5. Independently verify the cross-species current-clamp fit objective, geometry, reversal/channel shifts, temperature handling, and source rate-prefactor dimensional convention.
6. Keep AIS-resolved modeling separate. Human NaV1.2/NaV1.6 immunostaining does not provide functional conductance densities or gating parameters.

No biological validation, clinical validity, whole-brain functionality, or consciousness claim is made. Save/restore, Rust-native concurrency, the configurable 10,000-unit default, JSON model loading, Python, C/C++, and WGSL remain unimplemented.
