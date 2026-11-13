# HumanJS — session boot

**Updated:** 2026-11-13
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

The live repository check immediately before the 2026-11-13 AP1 sodium trap0 trajectory-proximity update verified default branch `main`, HEAD `b9aebdd833172c049e52628191f74d472893c0cd`, a complete non-truncated 75-entry tree, exactly one branch (`main`), no open issues and no open pull requests. GitHub Actions run `43423674648` completed successfully on that exact HEAD. Re-fetch the live main HEAD and newest workflow at every session start; do not rely on a stored SHA as current.

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

Do not infer withholding or manufacture missing observations. The HumanJS single-compartment Na+/K+ model remains exploratory and unaccepted. The missing Figure S5 J/K/M/N generation state and per-cell/raw K recordings remain evidence gaps. Continue only with independently accessible public sources; do not contact authors or researchers. Raster digitization remains a separate estimate, not a substitute for those sources.


### 2026-11-12 — current repository and contact-route check

A fresh live check on 2026-11-13 verified public repository codexclai/HumanJS, default branch main, HEAD 9344ccfa47cd82d308d10c44305d8176d82410f9, a complete non-truncated 75-entry tree, exactly one branch/ref (main), and zero open issues or pull requests. Workflow run 43213722785 completed successfully on that exact HEAD. A historical public-source contact-route lookup was recorded, but the project owner directed that no authors or researchers be contacted; no message was sent and no outreach is planned. The spike-capable model remains exploratory and unaccepted.


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


### 2026-11-12 — internal AP1 gate-state diagnostic committed and CI verified

Commit `ada7a9e8ecd478adfd3b411d2ccd0bdefbd1b137` (`feat(neuro): compare AP1 channel-gate trajectories`) extends the Rust trace example and NEURON diagnostic to export/compare all five live channel gates, documents author-default and high-resolution results, and refreshes scientific handoff notes. GitHub Actions run `43147714885` passed on this exact main commit: Rust format, Clippy, all Rust tests, experiment Python syntax, both Wilbers evidence validators, and repository policy. This is numerical model-to-model analysis only; the single-compartment spike mechanism remains exploratory and not biologically accepted.

### 2026-11-12 — shared-voltage gate-integrator decomposition

The diagnostic now applies both cnexp-equivalent and RK4 gate updates to the same source voltage samples, using the post-step voltage `V[n+1]`, common initial NMODL gate states, and the same continuous rate equations. The source exponential recurrence reproduces actual direct-rate NMODL gate states within a maximum 1.76e-6 fraction (diagnostic guard 1e-4). At 20 µs, the isolated RK4-versus-cnexp difference is 2.8221e-6 overall gate RMSE / 1.16295e-4 max, dominated by Na activation; at 1 µs it falls to 1.1710e-11 / 4.8856e-10. On the same path, Na TABLE versus direct-rate CNEXP yields 3.70195e-5 overall RMSE / 1.23720e-4 max, affecting only Na gates. These effects are much smaller than actual dynamic source-vs-HumanJS gate errors, so differing voltage paths/stage sampling/coupled feedback remain the main unresolved numerical contributors. No biological validity claim follows.


### 2026-11-12 — shared-voltage gate integrator and Na TABLE experiment committed

Commit `eec5651c80b71e0d7706f617d944cfad772c38fb` (`research(neuro): isolate gate solver effects on shared voltage`) adds the identical sampled-voltage counterfactual and 200-node Na rate-table sensitivity to the NEURON diagnostic, records its results in the research/experiment notes, and updates the next handoff. GitHub Actions run `43149669478` passed on the exact main commit. The analysis remains numerical and does not alter the model's exploratory/unaccepted status.


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

Interpretation limits: source NMODL CNEXP effectively advances gates using the post-step voltage sample; HumanJS uses coupled RK4 with voltage evaluated at internal stages. Prescribed midpoint and linear interpolation on the HumanJS voltage path closely reproduce HumanJS gates, but neither captures the actual internal RK4 stage voltages. This is a numerical model-to-model attribution, not proof that either solver is biologically more accurate and not biological validation. The single-compartment spike-capable mechanism remains exploratory and unaccepted. The exact four RK4 stage voltages are now captured by the opt-in diagnostic API and replayed against HumanJS live gates. Direct-rate stage replay reduces aggregate gate RMSE to 2.45e-8; source Na TABLE replay gives 3.93e-5. See the exact-stage section below. The next numerical question is the remaining membrane-voltage solver difference at matched states.



### Exact coupled RK4 voltage-stage capture and gate replay (2026-11-12)

HumanJS now exposes an opt-in `step_with_voltage_stages` diagnostic that returns the exact four membrane-voltage components of the intermediate state vectors passed to its coupled RK4 derivative evaluations: k1 at t, k2 at t+dt/2, k3 at t+dt/2, and k4 at t+dt. The ordinary `step` path does not materialize the diagnostic output. The AP1 example accepts `--stages-output` and `--currents-output`; the latter writes Na/K/leak/injected current densities and voltage derivatives at all four exact RK4 stages plus the committed endpoint. `step_with_current_balance_stages`, `step_with_voltage_and_current_stages`, and the non-advancing `current_balance` query expose these opt-in values; ordinary `step` does not construct diagnostic records. The NEURON diagnostic accepts `--humanjs-voltage-stages` and `--humanjs-current-stages`, validates columns, finite values, sample counts, and exact timestamps, and records refreshed endpoint NMODL currents.

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

### CN midpoint-current replay and coupled state-history attribution (2026-11-13)

The AP1 diagnostics now reconstruct NEURON secondorder=1 with midpoint membrane voltage and the previous gate state, followed by CNEXP gate updates at endpoint voltage. At 1 µs and 250 ns, this replay reproduces actual NEURON voltage within 0.000558 mV RMSE and gates within 2.87e-6 aggregate RMSE. At 250 ns, the CN midpoint and HumanJS RK4 weighted current-balance identities close below 1.1e-12 A/m²; the derivative of their actual voltage residual equals the negative current difference to 4.2e-11 A/m² maximum. Actual source/HumanJS total current RMSE is 1.742e-5 A/m². A same-HumanJS-path CN midpoint/left-gate counterfactual is larger (4.023e-4 A/m²), showing that the fully evolved state histories matter and that a one-step current-evaluation comparison cannot be mistaken for the coupled source trajectory. A fresh 125-ns HumanJS trace was generated, but the expanded NEURON run hit the VM memory limit; no 125-ns source current result is claimed. See the Wilbers experiment/research records. The mechanism remains exploratory and unaccepted.


### 2026-11-13 — matched 5-µs current-history refinement

A fresh 5-µs HumanJS trace (voltage, five gates, exact voltage stages and RK4 current stages) was paired with NEURON 9.0.2 secondorder=1 at the same step. The unchanged author-helper baseline remains 20 µs / secondorder=0 / Na TABLE on, with 20-pA rheobase and 30-pA AP1 current. No biological parameters changed.

| NEURON Na TABLE | HumanJS vs source voltage RMSE | Actual source CN midpoint vs HumanJS RK4 total-current RMSE | Held-left-gate HumanJS-path counterfactual RMSE |
|---|---:|---:|---:|
| On | 0.02487096 mV | 0.00208318 A/m² | 0.00785330 A/m² |
| Off | 0.00463648 mV | 0.000408145 A/m² | 0.00785330 A/m² |

The actual source/HumanJS difference is dominated by Na current during the upstroke, with K becoming comparable/larger during late repolarization and leak largest in the post-spike tail. Both capacitor-current identities close below 8.7×10⁻¹³ A/m²; the voltage-residual/current-difference identity closes below 2.51×10⁻¹² A/m². The prescribed-path value is a held-left-gate current counterfactual, not a coupled CN simulation; it is intentionally not interchangeable with the fully evolved source/HumanJS path.

At TABLE-off, the 5-µs actual total-current RMSE (4.08145×10⁻⁴ A/m²) is about 23.4× the earlier 250-ns value (1.74232×10⁻⁵); the prescribed-path counterfactual falls by about 19.5× between those same resolutions. This is consistent with timestep sensitivity, not proof of an asymptotic order. A fresh matched 1-µs HumanJS trace exists, but its NEURON rerun failed because nrnivmodl exceeded a 600-s build allowance in the 1-GiB VM; no new 1-µs current results are claimed. The 125-ns full NEURON run remains separately memory-limited as previously documented. No generated traces were committed. The mechanism remains exploratory/unaccepted; numerical comparisons do not constitute biological validation.


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

### 2026-11-13 — Human sodium-rate Rust regressions

Code commit `ed07cec9982622f9c3dcb8c0825c7951c3515442` adds two software regressions in `crates/humanjs-core/src/ion_channels.rs`. `human_sodium_rates_are_continuous_at_all_trap0_landmarks` checks each Na m / h-alpha / h-beta wrong-sign guard on both sides and at its centre, plus each true denominator singularity and nearby points, against the independent analytic rate equation. `human_sodium_rates_match_source_equations_over_voltage_grid` checks both sodium gate time constants and steady states at 441 effective voltages from −120 to +100 mV in 0.5-mV increments, applying the configured −10-mV current-clamp voltage shift explicitly.

GitHub Actions run [43425235022](https://github.com/codexclai/HumanJS/actions/runs/43425235022) completed successfully on that exact code commit: formatting, Clippy, Rust tests (38 unit, 3 synapse integration, 6 passive-membrane integration), Python syntax and 22 experiment tests, both Wilbers data validators, and repository policy all passed. These are source-equation and software regressions only; they do not repair the external NMODL files or establish biological validation.
