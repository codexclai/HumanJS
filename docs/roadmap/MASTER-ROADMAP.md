# HumanJS — master roadmap

**Status:** accepted direction and sequence, not a promise of dates or implementation completion.

## P0 — authoritative project foundation

- [x] Establish the public GitHub repository as the sole source of truth on `main`.
- [x] Establish Apache-2.0 licensing and owner attribution.
- [x] Add canonical session boot instructions and concise Project Instructions that work with empty ChatGPT Project Sources.
- [x] Consolidate current owner requirements, approved technology, brain-only scope, and biological authenticity boundaries.
- [x] Define the target system architecture and stack boundaries.
- [x] Define the whole-brain scope catalogue and validation ladder.
- [x] Establish a main-only workflow with no branch-generating update automation.
- [x] Add read-only repository policy validation on pushes to `main` and manual dispatch.
- [x] Remove duplicate, superseded, unreviewed, and temporary project material from the current working tree.
- [x] Document repository hygiene, security reporting, current status, and session continuity.
- [x] Verify that the live branch listing contains exactly `main` and no non-main refs.

## P1 — scientific evidence workflow

- [x] Review primary human evidence relevant to the passive-membrane mechanism.
- [x] Record species, preparation, method, anatomical resolution, measured values, heterogeneity, inference, and validation limits.
- [x] Review human adult L2/L3 pyramidal-to-pyramidal short-term synaptic dynamics and model-fitted AMPA/NMDA conductance waveforms.
- [x] Record the connection class, species, experimental methods, direct observations, fitted values, assumptions, and parameter provenance for the first glutamatergic mechanism.
- [x] Review human L2/L3 somatic Na+/K+ current measurements, human AIS sodium-subtype localization, and the model/measurement boundary for intrinsic spike initiation.
- [x] Retrieve and inspect the Wilbers supplementary Tables S1–S3 and original CC0 Dataverse fitting scripts, including protocol and temperature settings.
- [x] Retrieve the official PMC AWS copy of Wilbers Supplementary Figure S5, visually map model/human/mouse series, record 46 digitized markers plus four exact source-script recovery means, and validate seven evidence/model CSVs; reproduce the human K_IV current-activation fit in Rust and identify the published mouse activation curve as strongly matching pre-fit defaults rather than the later optimizer value. Rust now reproduces the human K_IV current-activation and current-inactivation fits plus the full 50-condition K_recovery current protocol and two-component recovery fits; raster comparison of model curves and raw-trace validation remain outstanding; assess human-only recovery parameters separately because the source slow-recovery constant is pooled across human and mouse.
- [x] Retrieve and inspect the original Wilbers pure human na_human.mod and k_human.mod sources, equations, parameter values, units, Q10 behavior, conductance expressions and fixed Rb=Ra relation.
- [x] Execute the deposited pure-human Na_IV, Na_IV_inact and Na_recovery source routines in NEURON 9.0.2 with the unmodified human sodium NMODL mechanism; preserve and validate the 19-voltage current-fit, 30-point inactivation and 156-run paired-pulse recovery records and source/current-fit output mapping. Raw NWB experimental current refitting remains outstanding.
- [x] Execute the deposited pure-human K_IV and K_recovery numerical source protocols in NEURON 9.0.2 with the unmodified human potassium NMODL mechanism; preserve the 34-voltage K_IV and 50 paired-pulse recovery records, source fits, and output validators. Correct the earlier source-helper audit: `get_tau_inact_double_fixedtau2` uses four initial values for four free parameters and fixes `tau2=450 ms`; document the remaining nonlinear fit-tau sensitivity rather than claiming exact repeatability.
- [x] Diagnose the deposited K_IV fast-inactivation fitting sensitivity on identical NEURON post-peak samples using six nonlinear initializations and fixed-`tau1` nonnegative linear profiles over both the original 0–300-ms bound and an explicitly counterfactual extended range; preserve and validate all 192 start fits, source-bound/extended/local tau profiles, and 4,890 time-resolved residuals at the refined local optimum. Record amplitude/offset compensation and the early post-peak residual mismatch without changing the deposited source helper; raw human K current-trace refitting remains outstanding.
- [x] Evaluate one explicitly non-source third-exponential correction on the complete 4,890-sample K_IV source-model waveform at −70 mV. Profile tau3 over 0.6–2.0 ms on an 801-point grid; fit all coefficients against the full waveform; compare signed and nonnegative extra-amplitude constraints; preserve the full/first-10-ms/after-10-ms objective and changes to the original amplitudes/offset. Record that the best extra term is negative and therefore a descriptive residual correction, not a positive biological current component.
- [x] Test the signed K_IV short-time residual correction across every predeclared command with a finite-positive fast-inactivation fit from the unchanged NEURON source replay. Preserve the original threshold exclusions (-110/-105 mV), five attempted-but-nonfinite fits (-100 through -80 mV), and all 27 eligible commands (-75 through +55 mV); profile/refit each full waveform, compare nonnegative-amplitude controls, and commit both the baseline 27-row/42-column summary and the expanded 27-row/42-column tau3 profile (0.1–5.0 ms, 2,801 points). Record that the wider grid removes the previous 11/27 tau3 boundary hits, but tau3 remains non-monotonic and the late-window residual worsens at seven depolarized commands. Interpret only as model-output residual analysis.
- [x] Quantify the local full-waveform K_IV tau3 objective shape at all 27 expanded-grid minima, including normalized central curvature, adjacent-point objective rises, and contiguous 1%/5%/10% relative-RSS basins. Commit the 27-row/26-column reference and compare every field in CI; document that no reported basin touches the search bounds, while basin widths vary by voltage and are conditional model-objective diagnostics, not confidence intervals.
- [x] Test tau1–tau3 coupling on the predeclared -30/-60/+55 mV representatives by profiling tau3 on a 0.1–10 ms grid across nine tau1 values in each existing local 6% refinement interval. Commit the 27-slice/44-column conditional surface and compare every field in CI. Record that the joint objective minimum shifts strongly at -30/-60 mV, while six of nine +55 mV tau1 slices still hit the tau3 upper bound and the signed added amplitude changes sign. This is a deterministic model-output sensitivity surface, not uncertainty or biological kinetics.

- [x] Inspect author-deposited per-cell summary workbooks and verify the published human Na+/K+ sample counts and steady-state fit summaries.
- [x] Compile the original pure Wilbers human Na+/K+ mechanisms in NEURON 9.0.2 and probe exact trap0 singularities plus the actual Na+ lookup grid; record the numerical outcomes without patching the source.
- [x] Reconcile the article's 14-parameter model description with the deposited 11-variable optimizer workflow (two inactivation steady states fixed from experiment; `Rb = Ra`); trace the K+ script's trailing alternate dictionary as an unapplied literal and document that `h12factor_k_human` occurs only in commented-out lines in all inspected K+ variants.
- [x] Retrieve and SHA-1 verify the Wilbers current-clamp AP1 target table, complete outcome extractor, and both 20×20 conductance grids; reproduce the exact feature definitions/target aggregation and map the all-human kinetic endpoint to the HumanJS 114.48/29.05 pS/μm² preset, preserving the distinction that its fit targets are 50:50 human/mouse median AP features.
- [ ] Reproduce the complete Wilbers voltage-clamp fitting workflow against raw current traces; the deposited per-cell workbooks are summary fits and the original human Na/K NWB traces were not in the 65-file Dataverse listing examined. The source-code Na and K voltage-clamp protocols have been executed, but those are model outputs, not raw experimental trace refits.
- [x] Retrieve and transcribe the original Eyal et al. 2018 supplementary Table S4 for all six soma/axon model parameter sets, confirming the nine-conductance + three NaTg-gate + two Ca-dynamics values per compartment and shared leak reversal potential.
- [x] Retrieve and audit the canonical 139,316,573-byte Eyal ModelDB archive, map all six Table S4 parameter sets to the original HOC soma/axon templates, and identify the nine inserted conductance mechanisms plus CaDynamics_E2.
- [ ] For each subsequent mechanism, gather relevant primary literature and authoritative technical references.
- [x] Add the Eyal Figure 7A six-cell NEURON reproduction protocol, checked-in Python 3 runner, released-trace comparisons, and explicit validation limitations under experiments/.

## P2 — native Rust simulation foundation

- [x] Establish a minimal Rust workspace based on real mechanism and ownership boundaries.
- [x] Define typed physical quantities, integer simulation time, model parameters, initial conditions, runtime state, and simulation errors.
- [x] Implement an integrated CPU-first passive-membrane slice with numerical and behavioral tests.
- [x] Implement one human-evidence-grounded glutamatergic conductance mechanism coupled to the passive membrane, including transactional runtime-state updates and causal tests.
- [ ] Retain a configurable default of 10,000 spiking-neuron units as an engineering configuration, not a biological claim.
- [ ] Implement a human-evidence-bounded somatic-patch-equivalent spike mechanism only after exact equations, parameters, units, temperature, and fit behavior are reproduced; keep this distinct from a future anatomical AIS model.

  Exploratory spike-capable code currently exists in `crates/humanjs-core/src/ion_channels.rs`, but it was added before this evidence gate was closed. It is not counted as completion of this roadmap item. Keep it provisional: the deposited Na_IV, Na_IV_inact and Na_recovery model/source protocols have now been executed in NEURON 9.0.2, but raw human NWB current traces were absent from the inspected Dataverse v3.0 inventory. Source execution does not resolve the source-declared `/ms` versus equation-derived `mV^-1 ms^-1` prefactor mismatch as a biological convention, nor does it validate human temperature handling or the spike mechanism. The current-clamp fit assumptions and exact 114.48/29.05 preset grid provenance are now checked; this source-provenance result does not itself satisfy the spike-mechanism acceptance gate.
- [ ] Implement an AIS-resolved mechanism only when its geometry and functional channel-density/gating evidence are sufficiently constrained; do not derive conductances from immunostaining alone.
- [ ] Implement Rust-native concurrency with explicit ownership, synchronization, interruption, and recovery behavior.
- [ ] Implement save/restore that preserves live and learned state and safely rejects corrupted or resource-exhausting input.
- [ ] Define and validate inspectable JSON model definitions separately from runtime and learned state.

## P3 — Python-first developer interface and native interoperability

- [ ] Expose the real Rust core through a documented, typed Python package.
- [ ] Define a stable C ABI with explicit ownership, lifetimes, errors, buffer contracts, and thread-safety.
- [ ] Add C++ wrappers over the stable native boundary where useful.
- [ ] Test cross-language ownership, lifetime, error, persistence, and concurrency behavior.

## P4 — scientific mechanisms and whole-brain integration

- [ ] Build evidence-grounded neuronal, dendritic, synaptic, receptor, release, plasticity, glial, and extracellular mechanisms beyond the first reduced glutamatergic slice.
- [ ] Integrate anatomically qualified populations, microcircuits, and long-range pathways while distinguishing human evidence from animal evidence and model inference.
- [ ] Develop spatially and temporally structured neuromodulation, homeostasis, circadian/sleep processes, memory systems, sensory pathways, executive/valuation systems, language, and action-related processes.
- [ ] Include retinal circuitry and evidence-bounded cochlear/auditory-nerve transduction at the sensory boundary, or require an external transducer that genuinely performs those mechanisms.
- [ ] Ensure cognitive capabilities arise through generalized interacting learning mechanisms rather than fixed fact tables, grammar parsers, object registries, goal slots, or sequence lookup tables.
- [ ] Validate mechanisms with causal interventions, reproducible assays, multiple seeds, matched controls, and explicit biological limitations.

## P5 — measured GPU compute and optimization

- [ ] Define a correct CPU reference path before GPU implementation.
- [ ] Integrate WGSL through a Rust-owned backend with capability discovery, validation, and graceful fallback.
- [ ] Compare GPU behavior against CPU reference results on actual hardware.
- [ ] Benchmark transfer overhead, synchronization, precision, memory usage, workload crossover, and reproducibility.
- [ ] Claim acceleration only for workloads with measured, reproducible performance gains.

## Completion rule

A document, module name, API declaration, region inventory, or workflow does not complete a roadmap item. Mark work complete only after integrated implementation, relevant tests, evidence/provenance review, and documentation are verified. Maintain current progress in `docs/status/STATUS.md`.
