# HumanJS — master roadmap

**Status:** direction and sequence, not a promise of dates or implementation completion.

## P0 — repository authority and governance

- [x] Identify the correct public GitHub repository.
- [x] Establish Apache-2.0 and owner attribution for Thamindu.
- [x] Add canonical session boot instructions and concise Project Instructions.
- [x] Consolidate owner requirements, architecture boundaries, decisions, and status.
- [x] Define archive, deferred, backup, trash, and temporary-output policy.
- [x] Add least-privilege repository policy workflow, Dependabot Actions updates, contribution guidance, and vulnerability-reporting guidance.
- [ ] Apply and verify main branch protection and available repository security settings in GitHub.
- [ ] Verify the post-merge push-triggered workflow run.

## P1 — legacy audit and selective migration

- [ ] Reconcile the old project documentation against the latest owner decisions.
- [ ] Identify valuable source research, bibliographies, evidence notes, unique owner prompts, and reproducible experiments.
- [ ] Review redistribution rights and third-party content before copying historical material into the public repository.
- [ ] Promote revalidated science to canonical research records; preserve historical results as legacy evidence rather than proof of biological validity.
- [ ] Retain old Node.js source only as explicitly archived provenance if it is useful and legally suitable; do not port it line-by-line.
- [ ] Record what is migrated, retained externally, rejected, or intentionally discarded.

## P2 — native Rust simulation foundation

- [ ] Establish a minimal Rust workspace based on real module and ownership boundaries.
- [ ] Define core time, state, population, event, error, resource-budget, and checkpoint contracts.
- [ ] Implement a genuinely integrated CPU-first simulation slice with tests.
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
- [ ] Develop spatially and temporally structured neuromodulation, homeostasis, circadian/sleep processes, memory systems, sensory pathways, executive/valuation systems, language and action-related processes.
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

Roadmap items are not completed because a document, module name, API declaration, region inventory, or workflow exists. Mark work complete only after integrated implementation, relevant tests, evidence/provenance review, and documentation are verified. Maintain a single current status document at docs/status/STATUS.md.