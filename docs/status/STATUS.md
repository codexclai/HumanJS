# HumanJS — current status

**As of:** 2026-11-10  
**Stage:** two integrated Rust CPU mechanisms implemented; latest full verification passed.

## Canonical repository

- Repository: `codexclai/HumanJS`.
- Current session handoff: `docs/status/SESSION-HANDOFF.md`.
- Visibility: public. Default branch: `main`.
- GitHub `main` is the sole authoritative source. ChatGPT Project Sources may remain empty.
- The live branch listing returned exactly one branch, `main`; no non-main refs remained.
- No open issues or open pull requests were returned by the latest live checks.
- Latest verified pre-documentation `main` HEAD: `a101a57a5946cd97ca216b69f3ad1264b63dc6e1`.
- Successful full workflow on that exact HEAD: run `42845287511`: https://github.com/codexclai/HumanJS/actions/runs/42845287511.
- Integrated CPU code commit: `d561df97ae0bbd1012d8cd3bb3b0e466e4f78304`, separately passed in run `42829179222`.

## Implemented CPU mechanisms

### Passive membrane

The Rust workspace `crates/humanjs-core` contains:
- Validated SI wrappers for voltage, current, capacitance, conductance, input resistance, and membrane time constant.
- Integer-nanosecond simulation time and positive step durations.
- Separate passive model parameters, initial conditions, and live runtime state.
- A single-compartment passive RC equation integrated analytically for piecewise-constant injected current.
- Derivation of lumped capacitance and leak conductance from supplied input resistance and time constant.
- Failed-step handling that does not partially update membrane state.

### Glutamatergic synapse

A first integrated, CPU-only excitatory synaptic mechanism contains:
- Independent AMPA-like and NMDA-like normalized biexponential conductance kernels.
- Explicit conductance peak, rise time, and decay time parameters, validated so decay is longer than rise.
- NMDA voltage-dependent magnesium unblock using gamma, extracellular magnesium concentration, and the Jahr-Stevens coefficient.
- A deterministic presynaptic availability model with utilization and exponential recovery, fitted to the effective short-term depression/recovery scale reported for adult human L2/L3 pyramidal-to-pyramidal connections.
- An integrated membrane step that uses interval-mean receptor conductances and a midpoint estimate for NMDA magnesium unblock.
- Transactional coupled updates: a failed step leaves both membrane runtime state and synapse runtime state unchanged.

The current synapse parameter fixture uses explicit human L2/L3 literature-based values in tests. It is not a universal default or a direct microscopic measurement of all receptor parameters.

## Scientific evidence and limitations

- `research/HUMAN-NEOCORTEX-PASSIVE-MEMBRANE.md` records human layer-specific passive membrane measurements and their limitations.
- `research/HUMAN-CORTICAL-GLUTAMATERGIC-SYNAPSE.md` records human adult L2/L3 pyramidal-to-pyramidal evidence, the fitted AMPA/NMDA conductance-waveform parameters, short-term depression/recovery fits, and a separate pyramidal-to-interneuron study that is deliberately not used as the parameter source for the selected connection class.

The synapse remains a bounded abstraction. It does not simulate presynaptic action potentials, calcium entry, docked/releasable vesicles, stochastic fusion, multivesicular release, explicit synaptic-cleft glutamate concentration/diffusion/uptake, molecular AMPA/NMDA Markov states or desensitization, dendritic spines/cable structure, or local NMDA dendritic spikes. It applies a connection-level depression fit to one effective contact as an explicit reduction. Tests establish computational behavior for these equations; they do not biologically validate the mechanism.

## Spike-initiation evidence review (no spike code)

`research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md` records the first targeted evidence review for intrinsic spike initiation. Three evidence levels are kept distinct:

- Wilbers et al. (2023) directly measured human L2/L3 somatic Na+ and K+ channel properties in nucleated patches. The patch preparation excludes the AIS. Its Table S1 contains human steady-state measurements; Table S2 contains fitted parameters for a 10-μm single-compartment nucleated-patch approximation; Table S3 contains direct patch area/conductance summaries. The fitted Na+ conductance in Table S2 (114.5 pS/μm²) is not the measured nucleated-patch mean (5.9 ± 0.8 pS/μm²).
- Tian et al. (2014) used human surgical-tissue immunohistochemistry to localize NaV1.2 more proximally and NaV1.6 more distally along pyramidal-cell AISs. This provides subtype-location evidence, not functional channel density or gating kinetics.
- Eyal et al. (2018) fitted somatic/axonal conductances to human AP recordings but explicitly assumed rodent-like channel kinetics and lacked human dendritic recordings. Its Table S4/model-source mapping still requires reconciliation against the original ModelDB package.

The Wilbers supplement and original CC0 author-deposited fitting scripts are documented in the research note. The fit scripts resolve the repeated Table S2 label: the intended inactivation variable is named `th_inact_inf` in the source. They expose the staged Na+ and K+ fits and the 25°C Na+/34°C K+ voltage-clamp settings. The original `na_human.mod` and `k_human.mod` files are confirmed in the deposit but their source text remains unavailable through the supported extractor (`audio/mod` MIME). The K+ fitting script contains inactivation values that differ between its initial optimizer result, its final printed dictionary, and Table S2. The paper's 14-parameter count also does not yet reconcile with the explicit fit-variable lists in the deposited scripts (13 named Na+ fit/assigned variables and 11 explicit K+ fit variables before additional fixed quantities). The exact `Rb` value/use and the actual NEURON gate equations remain unverified against those mechanism files. No threshold-only, generic rodent, or AIS-invented spike mechanism has been added.

A possible first implementation is restricted to a clearly named somatic nucleated-patch equivalent. It must not claim a complete neuron, intact AIS, dendrites, or axonal propagation. The AIS-resolved model is a later separate milestone.

## Verification

For code commit `d561df97ae0bbd1012d8cd3bb3b0e466e4f78304`, GitHub Actions run `42829179222` completed successfully and verified:

- `cargo fmt --all -- --check`
- `cargo clippy --workspace --all-targets -- -D warnings`
- `cargo test --workspace --locked` — 10 unit tests and 9 integration tests passed; 0 failed.
- `python3 .github/scripts/repository_policy.py` — repository policy passed (16 required files; no JSON files; no prohibited archives or generated output).

The first synapse commit needed formatting changes; the formatting gate then passed. Clippy identified an overly wide helper signature, which was refactored to pass typed synapse model/conductance values instead. The successful run above passed all checks. No tests were weakened or skipped in the successful workflow.

The evidence/documentation commit `3706624e75437656c2db320f87fde08dc6f13ab1` passed the full workflow in run `42841617776`, including formatting, Clippy, all 19 existing tests, and repository policy. This update made no Rust implementation changes and did not alter or weaken the existing tests.

A fresh local clone was attempted but this execution environment could not resolve `github.com`; no local checkout or local Rust test run was produced. Verification was performed by the GitHub Actions runner against the committed repository state.

## Human intrinsic spike-initiation evidence audit — no AP code added

The direct-source review is recorded in research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md. The pure human Wilbers Na+ and K+ NEURON mechanisms were retrieved from the CC0 DataverseNL deposit and their equations, parameters, units, Q10 behavior and conductance expressions inspected. Rb is fixed equal to Ra in each file. The current-clamp hybrid copies are distinct variants with human/mouse conductance-fraction scaling.

The original Eyal et al. 2018 supplementary Table S4 was retrieved and transcribed for all six somatic/axonal model parameter sets. It identifies nine maximal conductance variables per compartment (NaTg, SK_E2, SKv3_1, Ca_LVAst, Ca, Nap_Et2, K_Pst, K_Tst and Im), three NaTg kinetic variables, two CaDynamics_E2 variables, and one shared e_pas, matching the paper's 29 free-parameter count. Table S4 values are fitted model parameters, not direct channel-density measurements. The paper states that channel kinetics were assumed rodent-like and active dendritic parameters were omitted.

The official 133 MB ModelDB source archive could not be retrieved: its SenseLab download endpoint returned HTTP 504; the official ModelDB GitHub mirror contains only readme.html. Exact .mod contents and mechanism/compartment mapping remain pending.

Several issues still prevent a safe spike implementation:
- The Wilbers paper's 14-free-parameter methods description does not reconcile with the visible 13 Na+ and 11 K+ fit/assignment parameters.
- The pure K+ mechanism file matches Table S2 and the first optimizer result, but the fitting script's final printed six-parameter dictionary differs.
- The K+ fitting script assigns h12factor_k_human, which is not declared in the inspected pure K+ mechanism; its runtime effect is unknown.
- Both human mechanisms contain a trap0 branch test/fallback that does not obviously match the removable singularity in the rate equation. It must be examined under the original NEURON lookup-table/runtime behavior.
- The per-cell workbooks corroborate the reported human sample counts; they are summary tables, not raw current traces. The original NWB traces were not present in the 65-file Dataverse listing inspected.
- No NEURON/nrnivmodl execution was possible in the available environment. Source inspection is complete; model reproduction is not.

Accordingly, no AP-generating code, threshold event, or generic HH substitute has been added. The next code milestone remains blocked on source-model reproduction, not on documentation availability.

## Not yet implemented

- A configurable default of 10,000 spiking neuron units or an intrinsic spike-generation mechanism.
- Active voltage-gated membrane currents or calibrated human axon-initial-segment/somatic excitability.
- Explicit presynaptic release machinery, stochastic vesicle fusion, glutamate-cleft dynamics/uptake, and molecular receptor-state kinetics.
- Dendritic morphology/spines/cable filtering, multiple neuron compartments, population scheduling, and connected network dynamics.
- Long-term synaptic plasticity or learning.
- Runtime save/restore/checkpointing or safe interruption/resumption.
- Rust-native multi-threaded simulation execution.
- JSON model-definition loading and schema validation.
- Python developer package, stable C ABI, C++ wrapper, or integrated WGSL backend.

These remain requirements or future objectives, not current capabilities.

## Next implementation milestone

Reproduce the pure human Wilbers Na+/K+ mechanisms in compiled NEURON, specifically test trap0 lookup-grid behavior, reconcile the fit-parameter count and K+ dictionary mismatch, and compare results with per-cell human summaries and published voltage-clamp targets. The deposit's per-cell summaries do not substitute for raw current traces. Then obtain the canonical Eyal ModelDB archive to map Table S4 to its original mechanisms and compartments. Do not implement an intrinsic AP mechanism until these numerical and provenance issues are resolved. Keep any future somatic-patch model distinct from anatomical soma/AIS modeling.
