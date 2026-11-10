# HumanJS — master roadmap

**Status:** direction and sequence, not a promise of dates or implementation completion.

## P0 — GitHub authority, project definition, and baseline governance

- [x] Identify the correct public GitHub repository and make it canonical.
- [x] Establish Apache-2.0 licensing and an owner attribution notice.
- [x] Add canonical session boot instructions and concise Project Instructions.
- [x] Preserve the original owner prompt and consolidate current owner requirements.
- [x] Record approved technologies, brain-only scope, biological authenticity boundaries, and the whole-brain validation ladder.
- [x] Define repository structure and archive, deferred-work, backup, trash, and temporary-output policy.
- [x] Add contribution and vulnerability-reporting guidance.
- [x] Add a read-only repository policy workflow and weekly Dependabot configuration for GitHub Actions.
- [x] Pin `actions/checkout` to a reviewed full commit SHA; merge PR #2 after push and pull-request checks passed.
- [x] Verify the post-merge repository-policy workflow for preparation PR #8 passed (run `42811770679`, success).
- [ ] Owner: create and verify an active all-branches ruleset that prevents branch deletion, while leaving force pushes allowed. For `main`, require PR and policy CI where practical. See `docs/operations/GITHUB-SECURITY.md`.

## P1 — legacy disposition and scientific evidence workflow

- [x] Decide that GitHub is the sole current source of truth and no project ZIP is required.
- [x] Consolidate the accepted owner requirements and active target specification into current GitHub documents.
- [x] Retire the Node.js/JavaScript/npm runtime and reject a line-by-line port.
- [x] Define selective migration rules for historical research and experiment artifacts; do not bulk-import unreviewed material.
- [ ] As each new mechanism is designed, promote the relevant primary research and reproducible historical experimental context into canonical `research/` and `experiments/` records after provenance, relevance, and redistribution review.

## P2 — native Rust simulation foundation

- [ ] Establish a minimal Rust workspace based on real module and ownership boundaries.
- [ ] Define core time, state, population, event, error, resource-budget, and checkpoint contracts.
- [ ] Implement a genuinely integrated CPU-first simulation slice with numerical and behavioral tests.
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

Roadmap items are not completed because a document, module name, API declaration, region inventory, or workflow exists. Mark work complete only after integrated implementation, relevant tests, evidence/provenance review, and documentation are verified. Maintain current progress in `docs/status/STATUS.md`.
