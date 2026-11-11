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
- [x] Retrieve the official PMC AWS copy of Wilbers Supplementary Figure S5, visually map model/human/mouse series, record 46 digitized markers plus four exact source-script recovery means, and validate six evidence CSVs; reproduce the human K_IV current-activation fit in Rust and identify the published mouse activation curve as strongly matching pre-fit defaults rather than the later optimizer value. Reproducing the remaining current-fit/inactivation/recovery panels and raw-trace validation remains outstanding.
- [x] Retrieve and inspect the original Wilbers pure human na_human.mod and k_human.mod sources, equations, parameter values, units, Q10 behavior, conductance expressions and fixed Rb=Ra relation.
- [x] Inspect author-deposited per-cell summary workbooks and verify the published human Na+/K+ sample counts and steady-state fit summaries.
- [x] Compile the original pure Wilbers human Na+/K+ mechanisms in NEURON 9.0.2 and probe exact trap0 singularities plus the actual Na+ lookup grid; record the numerical outcomes without patching the source.
- [x] Reconcile the article's 14-parameter model description with the deposited 11-variable optimizer workflow (two inactivation steady states fixed from experiment; `Rb = Ra`); trace the K+ script's trailing alternate dictionary as an unapplied literal and document that `h12factor_k_human` occurs only in commented-out lines in all inspected K+ variants.
- [ ] Reproduce the complete Wilbers voltage-clamp fitting workflow against raw current traces; the deposited per-cell workbooks are summary fits and the original NWB traces were not in the 65-file Dataverse listing examined.
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

  Exploratory spike-capable code currently exists in `crates/humanjs-core/src/ion_channels.rs`, but it was added before this evidence gate was closed. It is not counted as completion of this roadmap item. Keep it provisional until the Wilbers voltage-clamp protocols are independently reproduced, the source-declared `/ms` versus equation-derived `mV^-1 ms^-1` prefactor mismatch is resolved, temperature handling is verified, and current-clamp fit assumptions are independently checked.
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
