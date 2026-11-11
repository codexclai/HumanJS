# HumanJS — session boot

**Updated:** 2026-11-11  
**Canonical source:** public GitHub repository `codexclai/HumanJS`, branch `main`.

Read this file first whenever a new session begins. GitHub `main` is authoritative. The ChatGPT Project Sources area is expected to be empty; no upload or local snapshot is a project dependency.

## Mandatory reading order

1. This file.
2. `docs/PROJECT-INSTRUCTIONS.md`.
3. `docs/OWNER-REQUIREMENTS.md`.
4. `docs/architecture/SYSTEM-ARCHITECTURE.md`.
5. `docs/spec/BRAIN-SCOPE-AND-COMPLETENESS.md`.
6. `docs/REPOSITORY-STRUCTURE.md`.
7. `docs/decisions/DECISIONS.md`.
8. `docs/roadmap/MASTER-ROADMAP.md`.
9. `docs/status/STATUS.md`.
10. `docs/operations/GITHUB-SECURITY.md`.
11. `docs/policies/REPOSITORY-HYGIENE.md`.
12. `docs/status/SESSION-HANDOFF.md`.
13. Read only the research, experiment, API, implementation, and issue records relevant to the current task.

Do not search for or request old uploads or copied source snapshots. If evidence or a design detail is missing, research or generate the needed current record from reliable sources when the task requires it.

## Current authoritative decisions

- Repository `codexclai/HumanJS`, branch `main`, is the sole source of truth for current code, documentation, requirements, decisions, research, experiments, issues, workflows, and history.
- ChatGPT Project Sources may remain empty. No project ZIP or separate source synchronization artifact is maintained or delivered.
- Keep the working tree focused on current project files. Do not add legacy source archives, duplicate inputs, general backup trees, or unreviewed historical project dumps.
- Repository is public and licensed Apache-2.0.
- Approved stack: Rust (native core), WGSL (GPU compute), Python (developer interface), C (ABI), and C++ (interop).
- Node.js, JavaScript, TypeScript, npm, JavaScript runtimes, and `.ajs` implementation are discontinued.
- Scope is a scientifically defensible computational model of the human brain only, not a whole-body simulator or chatbot.
- Preserve correct save/restore, Rust-native multi-threaded execution, and a configurable 10,000-spiking-neuron-unit default. This is an engineering default, not a biological count or hard maximum.
- CPU execution must work. GPU support is not a capability claim until actual hardware integration, correctness checks, and reproducible benchmarks succeed.
- Keep model definitions, initial conditions, live state, learned state, and checkpoints distinct.
- HumanJS has no requirement to store credentials, private user data, or secrets. Do not introduce authentication or generic secret/configuration infrastructure without an approved requirement.

## Branch policy and verified branch state

`main` is the only branch to use, permanently. Never create, check out, update, merge, or otherwise use another branch. Make authorized changes directly on `main`. Do not create branches, PRs, or automation that opens non-main update branches. No branch protection, rulesets, or deletion-prevention settings are required. Force pushes are permitted but exceptional and must be inspected and verified.

The live repository check on 2026-11-11 verified default branch `main`, HEAD `65fb7d37e410a2eedc44b1f29e1f528956c8d535`, a complete 63-entry tree, exactly one branch (`main`), and no open issues or pull requests. GitHub Actions run `43070078342` passed on that exact HEAD: formatting, Clippy, all Rust workspace tests, Python experiment-runner syntax, the seven-CSV Figure S5 evidence validator, and repository policy. Recheck the live repository, tree, branch list, and workflow at the start of every session; do not rely on this historical check.

## Session procedure

1. Retrieve repository metadata and verify the owner/repository, public/private state, and default branch.
2. Fetch the live `main` HEAD and inspect the entire tracked tree. When using a local checkout, clone/fetch from GitHub and verify the checked-out commit equals the live `main` HEAD.
3. Inspect recent commits, open issues/PRs, the latest main workflow runs, and relevant CI checks. Do not use non-main refs.
4. Read this file and follow the mandatory reading order.
5. Inspect relevant source, interfaces, dependencies, data flow, and tests before editing.
6. Commit authorized changes directly to `main`; verify the commit and resulting remote HEAD.
7. Run relevant checks and report exact commands/results, failures, timeouts, and unrun checks.
8. Update canonical documentation, current status, and handoff after meaningful work.
9. Verify all GitHub operations and disclose capability limits.

## Current implementation starting point

The Rust workspace `crates/humanjs-core` currently contains three integrated CPU mechanisms, but the third is exploratory and has not passed its scientific acceptance gate.

The passive-membrane model represents one lumped compartment with capacitance, leak conductance, an effective zero-current equilibrium, initial voltage, injected current, and integer-nanosecond simulation time. Constant-current steps use the analytic passive RC solution. Physical quantities use validated SI wrappers, and model parameters, initial conditions, and live state are distinct.

The glutamatergic synapse model adds AMPA- and NMDA-like normalized biexponential conductance waveforms, voltage-dependent NMDA magnesium unblock, and deterministic short-term depression/recovery. Its state is coupled to the passive membrane using interval-mean conductances and a midpoint magnesium-block approximation. The coupled states are committed together only when a step succeeds.

The exploratory `HumanL23SingleCompartmentModel` adds voltage-dependent human L2/L3 sodium and potassium gates and a lumped membrane equation integrated by fixed-step RK4. It is parameterized from the pure Wilbers human Na+/K+ voltage-clamp mechanisms, the Table S2 / first-optimizer potassium parameter set, and the authors' separate current-clamp fitted conductance densities and setup. Its 10 μm cylindrical area, 34°C temperature, −10 mV channel voltage shift, +15 mV reversal-potential offsets, and 20 μs maximum step follow the deposited current-clamp helper. A software test produces one spike for a specified 25 pA pulse and checks waveform-scale features.

This third mechanism is **not yet an accepted or biologically validated human neuron model**. It is one electrically lumped compartment, not an anatomical soma/AIS model; it has no axon, AIS, dendrites, propagation, spatial channel distributions, or population context. The current-clamp conductance densities were fitted against cross-species mean AP features and are not direct human channel-density measurements. The K+ fit script's trailing alternate dictionary is a bare literal never applied; its operative inactivation fit matches Table S2. The `h12factor_k_human` assignment is unused: all three inspected pure/hybrid K+ NMODL variants contain only a commented-out `h2tau = h1tau * h12factor` line and do not declare an active parameter. The article's 14-parameter description counts two inactivation steady states and an independent activation closing rate, whereas the deposited workflow fixes the inactivation steady states from experimental fits and constrains `Rb = Ra`, yielding 11 optimizer variables. The pure Na+/K+ NMODL files explicitly declare rate prefactors as `/ms`, matching Table S2, but their `trap0` equation multiplies each coefficient by a voltage-valued numerator; dimensional consistency requires `mV^-1 ms^-1`. HumanJS retains source numeric values and explicitly uses the equation-consistent internal unit without rescaling. The source's `trap0` singularity is replaced by its analytic mathematical limit, so the Rust implementation is not an exact source reproduction. These remaining numerical and validation limitations mean the code must remain explicitly exploratory and must not be extended as a validated mechanism until the evidence audit is complete.

The research record `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md` documents human somatic patch evidence, AIS localization limits, the Wilbers source/runtime discrepancies, and the separate Eyal six-cell soma/axon reproduction. Eyal's transferred rodent-like kinetics are not a source of human channel gating parameters. External model execution is not HumanJS implementation or biological validation.

The previous main workflow passed at `43071811472` on `959e7a27c894db872b635a2d46d617af39755be3`. This session adds CI-checked panel-J/K model-versus-marker residuals and audits the source current-clamp optimizer: its AP feature targets are 50:50 human/mouse median amplitude/upstroke/downstroke, not human-only targets. Exact `AP1comparison.csv` target values and the complete outcome extractor remain unretrieved. These are source-method findings and software checks, not biological validation. Recheck the latest workflow and HEAD live.

Checkpointing, Rust-native concurrency, the configurable 10,000-unit default, Python package, C/C++, JSON model loading, and WGSL remain future work. Do not claim these capabilities until implemented and tested.


## Latest Wilbers K+ protocol audit (2026-11-11)

The deposited K+ source workflow is now audited in `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`. The source helper uses a 20-ms −140-mV prepulse, 500-ms test steps, a +60-mV inactivation test, and a recovery protocol with 5-s depolarization followed by 4–8,464-ms recovery intervals. The human optimizer's fast-recovery target is explicitly pooled across human and mouse (236.824345 ms); the 450-ms slow-inactivation and 2,789.7929-ms slow-recovery constants are fixed, not optimizer variables. The slow-inactivation objective has a much poorer reported score (2.4386) and only 0.05 relative weight. The public 65-file Dataverse version lacks the Experimental-means K tau CSVs, the `data_fig5.xlsx` referenced by its K plotting script, and raw K voltage-clamp NWB traces. This is a source-workflow audit, not independent trace reproduction; keep the HumanJS spike-capable model exploratory and unaccepted.

The Rust core now has source-protocol regression tests for K+ current activation, post-peak biexponential inactivation, the original gate recovery clamp grid, and the `K_recovery` current protocol. The latter covers all five recovery voltages at all ten source delays (50 test-pulse peaks) and fits both current-recovery components. This is protocol/equation regression coverage only; the missing experimental K tau CSVs and raw traces still prevent full data validation.

The full K_IV_ss model-side voltage series has now been compared with the published human group summaries. Using half-range interpolation (not the source nonlinear fit), the Rust replay gives activation V1/2 −3.25 mV, inactivation V1/2 −51.48 mV, and availability at −80 mV 0.936, all within the paper's reported human mean ± SD. The test and Rust suite passed in workflow 42975907351 on code commit 46ed2817758e6dcf36cc15a57e11a32f96085342. This remains a coarse group-summary check, not raw-trace or kinetic validation.

The NEURON 9.0.2 unit checker has now been run on the original pure Na+ and K+ mechanisms. Both compile with `nrnivmodl`, but unmodified `modlunit` stops at untyped voltage arguments. Temporary typed probes confirm that the declared `/ms` rate prefactors, singularity fallback, Q10 exponent, and activation parameter annotations need correction; corrected temporary copies pass. The deposited source files were not changed. See the research audit and ADR-014 for exact diagnostic steps and limitations.

The official 13-page Supplementary Figure S5 PDF is retrieved from the new public PMC AWS dataset (1,468,232 bytes; SHA-256 `dfa1daaf4dd0e3979bac84b9cb8b1874c4514d40588969a21d7766a7f12f2a1d`). The legend is visually verified: red model line/human open-circle means; blue model line/mouse cross means. Panels I, J, K have 46 manually digitized experimental markers; panels M and N have four exact group means transcribed from `channel_tools.K_IV`, for 50 total. Seven research CSVs preserve those markers, source recovery-fit references, and the mouse pre-fit curve comparison. The validator also checks a six-point raster comparison showing the blue mouse activation model line matches the pre-fit default `Ra=0.0167/ms` (pixel RMSE 5.35) much better than the later optimized `Ra=0.020746083599133762/ms` (36.06); this strongly supports a stale pre-fit mouse curve in the available plotting call. Panels I and J are apparent current-fit time constants, not direct gate `mtau`: Rust regressions reproduce the rising-current activation fit at seven voltages and the post-peak biexponential inactivation fit at six voltages, with the source's fixed 450-ms slow component. The source `K_recovery` protocol is also replayed across five recovery voltages and ten delays (50 test-pulse peaks), with the two-component current-fit reproduced. At −80 mV its fast/slow current-fit values are close to the pooled species means, not human-only targets. The source slow-recovery parameter is ≈39.5% above the human-only mean; do not reuse pooled constants as human-specific parameters without raw human data. The voltage-clamp helper uses zero shift. The available fitting scripts call `K_IV` before activation optimization; the mouse activation model line strongly matches its pre-fit default, not the later optimized parameter. No separate final Figure S5 generator is deposited. These are group-mean data, not raw traces or source CSVs. The exact Dataverse K tau CSVs and raw voltage-clamp traces remain absent; NEURON itself has not been executed in this environment.
