# HumanJS — session boot

**Updated:** 2026-11-12  
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

The live repository check on 2026-11-12 verified default branch `main`, HEAD `a54a71f440004d251325a54cb4687b909835322a`, a complete 67-entry tree, exactly one branch (`main`), and no open issues or pull requests. GitHub Actions run `43128130076` passed on that exact HEAD: Rust formatting, Clippy, workspace tests, Python experiment-runner syntax, the Figure S5 research validator, the current-clamp conductance-grid validator, and repository policy. Recheck all live state at the start of every session.

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

The previous main workflow passed at `43071811472` on `959e7a27c894db872b635a2d46d617af39755be3`. This session adds CI-checked panel-J/K model-versus-marker residuals and audits the source current-clamp optimizer: its AP feature targets are 50:50 human/mouse median amplitude/upstroke/downstroke, not human-only targets. The AP1 target values and complete outcome extractor have since been retrieved and checksum-verified; see the 2026-11-12 current-clamp audit below. These are source-method findings and software checks, not biological validation. Recheck the latest workflow and HEAD live.

Checkpointing, Rust-native concurrency, the configurable 10,000-unit default, Python package, C/C++, JSON model loading, and WGSL remain future work. Do not claim these capabilities until implemented and tested.


## Latest Wilbers K+ protocol audit (2026-11-11)

The deposited K+ source workflow is now audited in `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`. The source helper uses a 20-ms −140-mV prepulse, 500-ms test steps, a +60-mV inactivation test, and a recovery protocol with 5-s depolarization followed by 4–8,464-ms recovery intervals. The human optimizer's fast-recovery target is explicitly pooled across human and mouse (236.824345 ms); the 450-ms slow-inactivation and 2,789.7929-ms slow-recovery constants are fixed, not optimizer variables. The slow-inactivation objective has a much poorer reported score (2.4386) and only 0.05 relative weight. The public 65-file Dataverse version lacks the Experimental-means K tau CSVs, the `data_fig5.xlsx` referenced by its K plotting script, and raw K voltage-clamp NWB traces. This is a source-workflow audit, not independent trace reproduction; keep the HumanJS spike-capable model exploratory and unaccepted.

The Rust core now has source-protocol regression tests for K+ current activation, post-peak biexponential inactivation, the original gate recovery clamp grid, and the `K_recovery` current protocol. The latter covers all five recovery voltages at all ten source delays (50 test-pulse peaks) and fits both current-recovery components. This is protocol/equation regression coverage only; the missing experimental K tau CSVs and raw traces still prevent full data validation.

The full K_IV_ss model-side voltage series has now been compared with the published human group summaries. Using half-range interpolation (not the source nonlinear fit), the Rust replay gives activation V1/2 −3.25 mV, inactivation V1/2 −51.48 mV, and availability at −80 mV 0.936, all within the paper's reported human mean ± SD. The test and Rust suite passed in workflow 42975907351 on code commit 46ed2817758e6dcf36cc15a57e11a32f96085342. This remains a coarse group-summary check, not raw-trace or kinetic validation.

The NEURON 9.0.2 unit checker has now been run on the original pure Na+ and K+ mechanisms. Both compile with `nrnivmodl`, but unmodified `modlunit` stops at untyped voltage arguments. Temporary typed probes confirm that the declared `/ms` rate prefactors, singularity fallback, Q10 exponent, and activation parameter annotations need correction; corrected temporary copies pass. The deposited source files were not changed. See the research audit and ADR-014 for exact diagnostic steps and limitations.

The official 13-page Supplementary Figure S5 PDF is retrieved from the new public PMC AWS dataset (1,468,232 bytes; SHA-256 `dfa1daaf4dd0e3979bac84b9cb8b1874c4514d40588969a21d7766a7f12f2a1d`). The legend is visually verified: red model line/human open-circle means; blue model line/mouse cross means. Panels I, J, K have 46 manually digitized experimental markers; panels M and N have four exact group means transcribed from `channel_tools.K_IV`, for 50 total. Seven research CSVs preserve those markers, source recovery-fit references, and the mouse pre-fit curve comparison. The validator also checks a six-point raster comparison showing the blue mouse activation model line matches the pre-fit default `Ra=0.0167/ms` (pixel RMSE 5.35) much better than the later optimized `Ra=0.020746083599133762/ms` (36.06); this strongly supports a stale pre-fit mouse curve in the available plotting call. Panels I and J are apparent current-fit time constants, not direct gate `mtau`: Rust regressions reproduce the rising-current activation fit at seven voltages and reconstruct the intended post-peak fixed-450-ms slow-component current fit for both human and mouse model parameters. **Source-code limitation:** the deposited `channel_tools.get_tau_inact_double_fixedtau2` helper has four free fit parameters but passes five initial values to SciPy; it catches the resulting error and returns NaNs. Thus the exact plotted J/K model-line generation is not traceable from the available source snapshot, and the Rust J/K values are transparent reconstructions, not exact Figure S5 line reproductions. The source `K_recovery` protocol is replayed for both species across five recovery voltages and ten delays (50 test-pulse peaks per species), with the two-component current fit reproduced. At −80 mV its fast/slow current-fit values are close to the pooled species means, not human-only targets. The source slow-recovery parameter is ≈39.5% above the human-only mean; do not reuse pooled constants as human-specific parameters without raw human data. The voltage-clamp helper uses zero shift. The available fitting scripts call `K_IV` before activation optimization; the mouse activation model line strongly matches its pre-fit default, not the later optimized parameter. No separate final Figure S5 generator is deposited. These are group-mean data, not raw traces or source CSVs. The exact Dataverse K tau CSVs and raw voltage-clamp traces remain absent; NEURON itself has not been executed in this environment.

### Current-clamp conductance-grid follow-up (2026-11-11)

The deposited current-clamp scripts run the cross-species-midpoint Powell objective over a 20×20 grid of Na/K human-kinetic ratios (400 conductance fits). The exact source CSVs and `get_outcomes_full` are now retrieved and checksum-verified. The all-human kinetic grid corner maps to the HumanJS 114.48/29.05 pS/µm² preset after rounding. The optimizer still targets 50:50 human/mouse median AP features; this is not a human-only fit or direct channel-density measurement. The spike model remains exploratory.

### Current-clamp source completeness finding (2026-11-11)

The complete Dataverse `cc_tools.py` (file 318557) defines `get_outcomes_full` and `get_outcomes`; the prior contrary conclusion was an incomplete extraction. The feature definitions, targets, grid orientation, and exact preset mapping are recorded in the 2026-11-12 research audit. The original NEURON/SciPy optimizer was not rerun; the deposited grid outputs were verified by SHA-1 and CI.


### Current-clamp dataset inventory correction (2026-11-12)

The 65-file inventory lists all three unrestricted current-clamp CSVs and the three source scripts. The CSV contents and helper have since been retrieved through the signed object-store redirect, checksums verified, and exact all-human grid-corner mapping established. See the final provenance section below.


### Wilbers current-clamp provenance resolved (2026-11-12)

The complete `cc_tools.py` (Dataverse file 318557) and all three unrestricted calibration CSVs are now retrieved and SHA-1 verified. `get_outcomes_full` is present in the helper; the earlier missing-helper conclusion was an incomplete-extraction error. The all-human kinetic (Na=1, K=1) corner of the deposited 20×20 grid is exactly 114.47654963753565 pS/μm² Na and 29.045736151752504 pS/μm² K, rounding to the HumanJS preset 114.48/29.05. The objective targets the 50:50 mean of human/mouse median AP peak voltage, upstroke, and downstroke, even at the all-human kinetic corner. Full details, source hashes, feature extraction, and protocol are in the final 2026-11-12 section of `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`. A CI validator checks the preserved CC0 source CSVs. NEURON/SciPy optimization was not rerun and no biological-validation claim is made.


The 2026-11-12 current-clamp audit also verified the complementary human/mouse channel split in both species' NMODL files: human currents scale by the selected ratio and mouse currents by its complement. At the all-human endpoint the mouse mechanisms contribute zero. Sodium Q10 scales both rates and conductance in the source; potassium Q10 scales rates only. The CI validator checks Dataverse SHA-1, local SHA-256, matrix axes/endpoints, and the Rust preset literals. Latest workflow `43128130076` passed on exact HEAD `a54a71f440004d251325a54cb4687b909835322a`.


### Wilbers v3.0 K-data inventory and cited ModelDB reference (2026-11-12)

The released DataverseNL DOI `10.34894/L5J0SD` has one current released version (3.0, CC0-1.0; release date 2022-12-13). The version-specific live API reports 65 files. The complete 65-filename metadata export has been cross-checked independently in the DANS Labs ODISSEI portal mirror (repository commit `ac75eb2a48cc0bf876ec451ed82d68c101326540`; metadata only). It contains none of the specific K tau measurement CSVs, `data_fig5.xlsx`, raw `.nwb` recordings, or a separate final Figure S5 plot generator. The earlier bioRxiv v2 ModelDB/GitHub URLs are unfinished placeholders. The published paper's ModelDB 8210 reference is the separate Mainen et al. (1995) neocortical spike-initiation model, not the Wilbers model/code deposit. Full evidence, exact URLs, and caveats are recorded in `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md` Section 4 and `docs/status/STATUS.md`.

Do not infer withholding or manufacture missing observations. The HumanJS single-compartment Na+/K+ model remains exploratory and unaccepted. The next evidence action is a targeted request for the original Figure S5 J/K/M/N generation state and missing per-cell/raw K recordings (or an explicit availability statement); raster digitization remains a separate estimate, not a substitute for those sources.


### 2026-11-12 — current repository and contact-route check

A fresh live check verified public repository codexclai/HumanJS, default branch main, HEAD 7318fb1cfbb467e33404d0e14e0617ab8c969f7b, a complete non-truncated 67-entry tree, exactly one branch/ref (main), and no open issues or pull requests. Latest main workflow run 43128282842 completed successfully on that exact HEAD. The publisher's corresponding-author contact route for the Wilbers K+ data/plotting clarification is now documented in the research record and handoff; no email has been sent. The spike-capable model remains exploratory and unaccepted.


### 2026-11-12 — model-line raster audit and live repository recheck

A new 23-point raster estimate of the combined visible red/blue Figure S5 model traces in panels J/K/M/N is preserved in research/HUMAN-L23-WILBERS-FIG-S5-MODEL-LINE-RASTER.csv. The official supplement PDF was retrieved and hash-verified; the Figure S5 validator now checks the added raster record. These estimates are not species-separated curves, raw data, exact source-code outputs, or biological validation. See the final 2026-11-12 section of research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md.

Immediately before this BOOT update, live main was 1e721852bf3b49c72ff9c49cb249a376ccd339dc, with a complete non-truncated 68-entry tree, exactly one branch (main), no open issues or PRs, and workflow run 43129934568 pending on that exact commit. Recheck the final BOOT commit and its workflow before relying on this state.


### 2026-11-12 — refined J/K/M/N model-line evidence

The 23-point model-line raster CSV is now marker-anchored for panel J. The inter-marker J curve agrees with both existing human and mouse equation-level current-fit reconstructions at about 0.36 ms RMSE, but the red/blue model curves overlap and cannot be species-discriminated. K is approximately 444.8 ms versus the fixed 450-ms component; N is approximately 2.78–2.79 s versus the pooled slow-recovery constant. Panel M remains a raster-only estimate pending direct comparison with the deposited K_IV model path. Full detail is in the research record and current status/handoff.

Immediately before this BOOT update, live main was 0727cb0d0b4bf309b98799d37bc609ab05536518, with a complete non-truncated 68-entry tree, exactly one branch (main), and the workflow queued on that exact commit. Recheck the final BOOT commit and its workflow; no claim of success is made from a queued run.


### 2026-11-12 — raster validator correction and final live check

The refined Figure S5 panel-J raster samples and J/K/N comparison checks are now in the research CSV and validator. CI run 43130214819 failed because the validator's lower range bound (18 ms) excluded the valid 17.51-ms last sample; the bound was corrected to 17 ms without changing the data. Follow-up run 43130293760 passed every step on exact commit b9060fdc407cf1606b42c29d4f88663f169ca703. The failure and correction are recorded in status and handoff.

Immediately before this BOOT update, live main was 0e390abef81c30674ef356c50c93e9702d1699e7, with a complete non-truncated 68-entry tree, exactly one branch (main), no open issues or PRs, and workflow run 43130351490 pending on that exact commit. Recheck the final BOOT commit and its workflow before relying on this state.


### 2026-11-12 — historical pre-migration archive reviewed

The owner supplied a historical `HumanJSProject.zip` for a one-time audit. It was inspected read-only (422 ZIP entries, 375 files; SHA-256 `0deb7789a8df444ea6a4e957dc63520cf6e786c18887286c3a31a319f61eccdf`). It contains the discontinued JS/Node runtime, 28 architecture notes, 143 experiment documents, 92 old simulator-result JSONs, and a large research dossier. The archive itself is not in GitHub and is not needed for future sessions. No legacy source or old simulator outputs were imported; prior results are not current Rust-core results or biological evidence. Selective historical research reuse requires primary-source revalidation; old experiment claims require independent Rust reproduction. See ADR-017, current status, and session handoff. This was an inventory triage, not a complete line-by-line revalidation of the historical dossier.


### 2026-11-12 — Figure S5 panel-M source comparison and CI

The exact pre-optimizer `K_IV` -> `K_recovery` path is now recorded. Panel M is the source fit's first recovery component (`tau1`); panel N is `tau2`. The recalibrated panel-M raster (134.36, 193.41, 304.46, 350.03 ms) agrees with the pooled human/mouse source-output polyline at 2.01-ms RMSE (3.32-ms maximum absolute residual). This is raster consistency, not raw-data reproduction or biological validation. Two intermediate CI failures were due to the validator not permitting the explicitly recorded 5-pixel uncertainty; data were retained and the bound corrected. Run 43131570918 passed all workflow steps on exact commit 49978d3920eb3d6d53e6dbc2e8aa20c25ef41fae. See the research record, replay CSV, status, handoff, and ADR-017.


### 2026-11-12 — Human L2/L3 single-compartment acceptance audit

The author-deposited hybrid current-clamp Na/K mechanisms and cc_tools.py were fetched and inspected directly. The source confirms trates(v+vshift) with helper vshift = −10 mV, so HumanJS's effective V−10 mV shift is correct. Source initialization, Na/K temperature-factor placement, three-fraction K gate behavior, SI current-density conversions, geometry, capacitance, leak and reversal potentials were reconciled. A dedicated Rust regression now locks the shift polarity and source-equivalent initialized gate states. This does not establish a source-exact run: HumanJS repairs the deposited trap0 defect and uses RK4 rather than NEURON cnexp. The existing 25-pA spike test is not the paper's rheobase/1.5×-rheobase protocol. The complete acceptance audit is appended to research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md; the model remains exploratory and unaccepted.


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


### 2026-11-12 — independent Wilbers NEURON AP1 execution and corrected rheobase replay

The earlier 101-pA / 59.594-mV / undefined-threshold diagnosis is retracted: the Rust test helper had omitted cc_tools.getrheo's initial 0.1-nA trial. The corrected search finds 20.0-pA rheobase in both source NEURON 9.0.2 and HumanJS; both then use a 30.0-pA AP1 pulse. The exact deposited NMODL files and cc_tools.py were SHA-1 verified, compiled unchanged, and executed by the new pinned runner. HumanJS matches source peak, threshold, upstroke, downstroke, and AHP features within measured solver differences. Full trace comparison: 0.455221-mV RMSE, 4.615873-mV maximum absolute error. See the Section 6 research record and reproducible experiment runner. This is model-to-model reproduction, not biological validation; the spike-capable model remains exploratory and unaccepted.


### CI verification of corrected NEURON reference replay (2026-11-12)

Commit 3ea7cb43fcc0e9627cfc7b6cdde3c28055356dd0 passed GitHub Actions run 43139126138. All required steps succeeded: Rust formatting, Clippy, complete Rust workspace tests, Python experiment-runner syntax, Figure S5 digitization validator, current-clamp conductance-grid validator, and repository policy. Two immediately preceding runs stopped at rustfmt because the source file lacked its terminal newline; that formatting-only issue was corrected. The source-model comparison assertions themselves passed unchanged. This CI validates the implementation and its pinned reference checks, not biological validity.

### 2026-11-12 — Wilbers AP1 solver-residual attribution

The unchanged `cc_tools.run_1AP` sets `h.dt=0.02` ms and leaves `h.secondorder` untouched; the NEURON 9.0.2 replay measured the default `secondorder=0` (fully implicit backward Euler). Both source NMODL channel mechanisms continue to use `METHOD cnexp` for their gates. The human Na mechanism has an active voltage-rate table (`FROM -120 TO 100 WITH 199`); the human K table code is commented out. NEURON's current reference documents the default and the Crank–Nicolson alternatives: https://www.neuronsimulator.org/en/latest/progref/simctrl/programmatic.html.

A source-verified numerical sensitivity experiment now separates the major solver effect. The original 20-µs, secondorder=0, Na-table-on baseline remains 0.455221-mV RMSE / 4.615873-mV max residual against HumanJS. Changing only the diagnostic NEURON voltage solver to secondorder=1 at the same 20-µs step reduces this to 0.038124 / 0.594290 mV. With 5-µs CN and Na table off the residual is 0.004756 / 0.062958 mV against the 20-µs HumanJS trace; a separately matched 1-µs CN/table-off comparison gives 0.001515 / 0.005020 mV. No biological parameters were changed. Table on/off is a secondary, timestep-dependent effect; the original table-on source remains canonical. Temporary diagnostic-only counters around the unchanged source `trap0` predicate observed 800 Na calls (including table generation) and 13,188 K calls, with zero fallback entries; the instrumented and original source traces were bit-identical over all 1,451 samples. The source defect remains relevant to other voltage trajectories and protocols.

New tools: `crates/humanjs-core/examples/wilbers_current_clamp_trace.rs` exports a HumanJS trace and independently replays the deposited rheobase search; `experiments/diagnose_wilbers_neuron_solver.py` downloads/checksums the five CC0 files, compiles unchanged NMODL, verifies the unmodified source baseline, then varies timestep, NEURON voltage integration order, and Na table use. Details and exact numbers are in `experiments/WILBERS-CURRENT-CLAMP-NEURON-REFERENCE.md` and Section 6 of the research record. This attribution is specific to a model-side AP1 numerical comparison, not biological validation; the human data/model-acceptance blockers remain open.

The clean main clone at pre-change HEAD `d9b0b871e4aadacb3cc1b58e873a1c32fd11563f` passed `cargo test --workspace --locked` locally (31 unit + 3 synapse integration + 6 passive membrane integration tests). The new Rust trace example also ran, independently returned rheobase 20.0 pA / AP1 30.0 pA, and emitted 1,450 samples. The diagnostic script passed Python 3.10 syntax, CLI, and end-to-end execution against the checksum-verified NEURON 9.0.2 environment; its author-helper baseline reproduced the prior reference to floating-point precision. GitHub CI for these new paths is pending until the main commit is pushed.
