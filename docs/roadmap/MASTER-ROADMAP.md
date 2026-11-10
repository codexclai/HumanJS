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
- [ ] Remove the remaining non-main Git references when a safe branch-deletion operation is available; do not use or update them.

## P1 — scientific evidence workflow

- [ ] For each mechanism selected for implementation, gather relevant primary literature and authoritative technical references.
- [ ] Record species, preparation, method, anatomical resolution, measurement limits, provenance, parameter source, uncertainty, disputes, and validation boundaries.
- [ ] Add a research record only when it informs a concrete mechanism, parameter, or validation task.
- [ ] Add reproducible experiment protocols and results under `experiments/` only when real experiments are designed.

## P2 — native Rust simulation foundation

- [ ] Establish a minimal Rust workspace based on real module and ownership boundaries.
- [ ] Define core time, state, population, event, error, resource-budget, and checkpoint contracts.
- [ ] Implement an integrated CPU-first simulation slice with numerical and behavioral tests.
- [ ] Retain the configurable 10,000 spiking-neuron-unit default as an engineering configuration, not a biological claim.
- [ ] Implement Rust-native concurrency with explicit ownership, synchronization, interruption, and recovery behavior.
- [ ] Implement save/restore that preserves live and learned state and safely rejects corrupted or resource-exhausting input.

## P3 — Python-first developer interface and native interoperability

- [ ] Expose the real Rust core through a documented, typed Python package.
- [ ] Define a stable C ABI with explicit ownership, lifetimes, errors, buffer contracts, and thread-safety.
- [ ] Add C++ wrappers over the stable native boundary where useful.
- [ ] Test cross-language ownership, lifetime, error, persistence, and concurrency behavior.

## P4 — scientific mechanisms and whole-brain integration

- [ ] Build evidence-grounded neuronal, dendritic, synaptic, receptor, release, plasticity, glial, and extracellular mechanisms.
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