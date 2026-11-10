# HumanJS — target system architecture

**Status:** accepted direction, with two bounded CPU mechanisms implemented.  
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

## 11. Implemented CPU slice — human L2/L3 glutamatergic synapse

The Rust core also contains a single effective glutamatergic synaptic-contact model parameterized for an adult human L2/L3 pyramidal-to-pyramidal evidence context. AMPA-like and NMDA-like inputs use separate normalized biexponential conductance waveforms. The waveforms use explicit peak conductance, rise time, and decay time; their time constants are effective conductance-shape parameters rather than molecular receptor transition rates.

NMDA conductance is multiplied by a voltage-dependent magnesium-unblock factor using the Jahr-Stevens form. The gamma parameter, extracellular magnesium concentration, and coefficient are explicit. The initial parameter fixture uses the representative fitted Eyal et al. human L2/L3 model values and is not a universal default.

Short-term depression/recovery uses an availability variable. A presynaptic spike triggers an effective response proportional to available resource and depletes the resource by the fitted utilization fraction. Availability recovers exponentially between events. Human paired-recording observations and model-fitted U/recovery values are documented in `research/HUMAN-CORTICAL-GLUTAMATERGIC-SYNAPSE.md`. The connection-level fitted values are applied to one effective contact as an explicit abstraction.

The coupled membrane update analytically averages each receptor conductance waveform over the requested interval and uses a midpoint predictor-corrector for voltage-dependent NMDA magnesium unblock. A failed coupled step leaves both the membrane state and the synaptic state unchanged. The approximation depends on simulation step size; tests compare a 1 ms step with ten 0.1 ms steps.

This is not a complete biological synapse. Explicitly unmodeled are presynaptic spike waveform/calcium entry, release-site/docked-vesicle/fusion mechanisms, stochastic or multivesicular release, cleft glutamate concentration/diffusion/uptake, molecular receptor Markov/desensitization states, spines/dendritic cable, and inhibitory inputs. The first implementation does not model local dendritic NMDA spikes. These mechanisms remain future work, not implicit capabilities.

## 12. Validation status of current mechanisms

The current Rust tests validate SI input handling, time arithmetic, exact passive RC integration, normalized conductance kernels, voltage-dependent magnesium unblock, fitted-scale short-term resource dynamics, depolarizing synaptic current, approximate step-size convergence, and atomic failure behavior. GitHub Actions runs formatting, Clippy, workspace tests, and repository policy checks. These are software-level checks only; they do not establish biological validation or whole-brain functionality.


## 13. Intrinsic spike-initiation boundary — evidence review, not implementation

The current CPU mechanisms remain subthreshold; HumanJS does not yet generate action potentials. The evidence review in research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md separates direct human somatic nucleated-patch Na+/K+ measurements (Wilbers et al. 2023), fitted single-compartment channel parameters, human AIS NaV1.2/NaV1.6 immunolocalization (Tian et al. 2014), and Eyal et al. (2018) somatic/axonal model fits that assume rodent-like channel kinetics.

- **Somatic nucleated-patch equivalent:** a single electrical compartment constrained by human L2/L3 somatic voltage-clamp data. It is a preparation-equivalent model, not an anatomical soma/AIS neuron. The Wilbers fitted Na+ conductance differs substantially from direct nucleated-patch conductance measurements and must remain separately tagged.
- **Anatomical soma/AIS model:** requires AIS geometry and functional channel density/gating evidence. Human NaV1.2/NaV1.6 immunolocalization is spatial subtype evidence only; immunostaining does not supply functional conductance or gating parameters. Eyal et al. provides human AP recordings and fitted soma/axon conductances, but its kinetics were assumed rodent-like and dendritic active conductances were not constrained by human dendritic recordings.

The original Wilbers human channel files are source-inspected, but their trap0 rate-function fallback has not been tested in compiled NEURON, and the K+ fit-script dictionary and paper parameter-count discrepancies remain open. The per-cell workbooks corroborate sample counts but are not raw current traces. NEURON/nrnivmodl was unavailable, so no Wilbers mechanism runtime reproduction was performed.

The original Eyal et al. supplementary Table S4 is now transcribed in the research note. It resolves the parameter manifest: nine maximal conductance densities (NaTg, SK_E2, SKv3_1, Ca_LVAst, Ca, Nap_Et2, K_Pst, K_Tst and Im), three NaTg kinetic parameters (slopem, vshiftm, vshifth), two CaDynamics_E2 parameters (gamma and decay), fitted separately for soma and axon, plus one shared e_pas reversal potential. This matches the paper's 2(9+3+2)+1=29 parameter count. All six-cell soma/axon values are documented from Table S4. The table values are optimized fits, not direct measurements of channel density. The main paper states that channel kinetic functions were assumed similar to rodent models and that active dendritic parameters were omitted because suitable human dendritic recordings were unavailable.

The official ModelDB record identifies the canonical 133 MB EyalEtAl2018.zip archive, but the SenseLab download endpoint returned HTTP 504 from the available research-browser network. The official ModelDB GitHub repository currently exposes only its readme, while the inspected secondary GPL-3.0 repository is not a canonical source substitute. Consequently, the Table S4 parameter map is resolved, but exact original .mod file contents, compartment assignments and mechanism-to-table mapping still need direct package inspection.

Do not equate fitted channel parameters with direct measurements, transfer kinetics across species without provenance, or infer AIS conductance from immunostaining. No AP-capable implementation should be added until the Wilbers trap0 behavior and fitting discrepancies are resolved and the human somatic voltage-clamp behavior is reproduced in a verified runtime. Any first AP-capable model needs comparisons against voltage-clamp and AP targets; these are model-correspondence tests, not biological validation. An AIS-resolved model remains a stricter, separate evidence gate.
