# HumanJS — target system architecture

**Status:** accepted direction, with one minimal CPU mechanism implemented.  
**Updated:** 2026-11-10.

This document defines architectural boundaries and responsibilities. The full biological and functional scope is enumerated separately in ../spec/BRAIN-SCOPE-AND-COMPLETENESS.md. The target architecture is not a claim that all listed mechanisms, interfaces, GPU paths, or persistence formats already exist.

## 1. High-level topology

- Python developer interface → native Rust binding → Rust simulation core.
- C applications → stable C ABI → Rust simulation core.
- C++ applications → C++ convenience layer → stable C ABI → Rust simulation core.
- Rust-native applications → native Rust API → Rust simulation core.
- Rust GPU execution layer → WGSL compute kernels on supported hardware.
- CPU execution remains available and is the correctness reference/fallback path.
- Model/brain definition data is loaded and validated separately from runtime and learned state.

Rust owns the authoritative simulation state. Bindings must not duplicate or independently invent biological state transitions.

## 2. Responsibility boundaries

### Rust core

Owns time advancement, state transitions, neural and glial mechanisms, population and connectivity representations, plasticity, regional interactions, scheduling, state integrity, resource budgets, checkpointing, and deterministic controls where scientifically and computationally appropriate. Split crates only where ownership, dependency, testing, or build boundaries justify it.

### Python interface

Python is the main developer experience. It should expose intuitive construction, configuration, simulation control, inspection, persistence, experiment orchestration, and scientific analysis without moving core simulation truth into Python or turning the native core into a subprocess service. PyO3/maturin are candidates, not final dependencies.

### C ABI and C++

The C ABI is the stable interoperability boundary. Specify opaque handles, ownership/lifetime rules, error reporting, buffer lengths, struct layout, ABI compatibility policy, thread safety, and shutdown behavior before exposing it. C++ wrappers should be idiomatic and must not become a second simulation core.

### WGSL and GPU execution

WGSL contains GPU compute kernels only. A Rust-owned backend selects CPU or GPU execution after capability discovery and correctness checks. Account for transfer costs, synchronization, precision, determinism expectations, device memory, and workload crossover. A detected GPU is not automatically faster. A shader compiling is not evidence of an integrated backend. Require actual hardware execution, correctness comparison against CPU reference behavior, fallback/error tests, and reproducible benchmarks.

## 3. Biological model layers

The eventual model is expected to connect evidence-grounded layers rather than isolated labels:

1. Cell classes and intrinsic electrophysiology, including relevant ion-channel and membrane dynamics.
2. Dendritic structure and integration where model scale and evidence warrant it.
3. Synaptic transmission, vesicle release, receptor kinetics, postsynaptic effects, plasticity, and relevant local chemistry.
4. Glial and extracellular contributions where they materially affect modeled dynamics.
5. Spatially and temporally structured neuromodulation.
6. Anatomically qualified regional populations, microcircuits, and long-range connections.
7. Development, homeostasis, circadian timing, sleep-related dynamics, and state-dependent regulation.
8. Sensory neural boundaries and central sensory pathways.
9. Distributed memory, valuation, executive, language, action-selection, and other cognitive systems emerging from interactions and learning.

This is a target decomposition, not a statement that every item is understood or fully modelable. Evidence gaps must remain visible.

## 4. Cognition is not a software registry

Do not implement cognitive functions as fixed fact tables, an English lexicon/parser, object-ID registry, numbered goal slots, fixed switch timer, or capped sequence lookup. Build generalized mechanisms with learned dynamics, distributed representations, competition, plasticity, recurrent activity, and causal interaction as supported by research. External diagnostic labels may exist for analysis, but must not be mistaken for internal cognitive machinery.

## 5. Sensory and body boundary

HumanJS is a brain model, not a whole-eye, whole-ear, peripheral-nerve, or body simulator. However, a generic feature vector or frequency transform cannot be described as retinal or cochlear processing. Include retinal circuitry and evidence-bounded cochlear/auditory-nerve transduction within the modeled sensory boundary, or define an external transducer that actually implements those mechanisms and provides suitable neural outputs. Body/peripheral systems remain external host responsibilities.

## 6. State and data boundaries

Keep separate: brain/model definitions and anatomical/connectivity priors; initial conditions and configuration; live simulation state; learned/plastic state; persisted checkpoints and restoration metadata; experimental stimuli and diagnostic outputs; research evidence and parameter provenance.

Inspectable model and IR data should use .json where appropriate. Runtime state encoding should be chosen based on correctness, performance, inspectability, size, and safe recovery; do not invent a format or compatibility promise before testing it.

## 7. Concurrency and scale

Use Rust-native concurrency rather than Node worker APIs. Define ownership of mutable state, scheduling granularity, synchronization, determinism expectations, checkpoint coordination, cancellation, and error propagation. Retain a configurable default of 10,000 spiking neuron units and count rate/mean-field populations and state variables separately. This default is not a biological estimate or maximum.

## 8. Repository implementation boundaries

Future code may live under `crates/` for Rust, `python/` for the primary Python package, `bindings/c/` and `bindings/cpp/` for interoperability, `gpu/` for WGSL, `models/` for inspectable JSON model definitions, `research/` for evidence, `experiments/` for reproducible protocols, `tests/` for cross-layer validation, and `benchmarks/` for reproducible performance tests. Create directories only when real content is introduced.

## 9. Architecture acceptance principles

- CPU baseline and correctness tests precede GPU optimization claims.
- Every public binding has explicit input, ownership, error, and lifetime semantics.
- Every biological claim has traceable evidence and a stated abstraction boundary.
- Save/restore round-trips representative live and learned state and safely rejects corruption.
- Concurrency tests verify correctness, ownership/synchronization, interruption, and restore behavior.
- No legacy Node.js or JavaScript dependency exists in active source or workflows.
- No test or document calls an unimplemented mechanism complete.

## 10. Implemented CPU slice — passive membrane patch

The active Rust workspace is currently `crates/humanjs-core`. It implements one lumped passive membrane patch with capacitance, leak conductance, an effective zero-current equilibrium potential, initial voltage, injected current, and an integer-nanosecond simulation clock.

The update solves the passive RC equation analytically over each interval for a current held constant over that interval. This avoids Euler-step stability constraints for this linear subthreshold equation. Physical inputs use validated SI newtypes. Parameters, initial conditions, and live runtime state are separate types. A failed step leaves the previous state unchanged.

The model can derive total capacitance and leak conductance from an input resistance and membrane time constant using the lumped RC relationship. This conversion is a modeling reduction; it does not recover dendritic morphology or identify a specific ion-channel reversal potential. No population parameter defaults are shipped.

The evidence note `research/HUMAN-NEOCORTEX-PASSIVE-MEMBRANE.md` documents human surgical-tissue recordings that show layer-dependent means and substantial heterogeneity. The current code is not calibrated to a complete cell dataset and has only software-level numerical/behavioral tests.

Explicit exclusions at this stage: active channels (including sag currents), synaptic transmission/receptor kinetics, dendritic cable structure, action-potential initiation, neuron populations, network connectivity, save/restore, native concurrency, Python/C/C++ interfaces, JSON model loading, and WGSL. These remain future work, not implicit capabilities.
