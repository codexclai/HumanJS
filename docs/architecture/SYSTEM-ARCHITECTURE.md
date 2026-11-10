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


## 13. Intrinsic spike-initiation boundary — evidence review and external reproduction, not HumanJS implementation

The current HumanJS CPU mechanisms remain subthreshold; the Rust core does not yet generate action potentials. The targeted evidence review is in \`research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md\`; the canonical Eyal reproduction is documented in \`experiments/HUMAN-L23-SPIKE-MODEL-REPRODUCTION.md\` and driven by \`experiments/reproduce_eyal_figure7a.py\`.

- **Somatic nucleated-patch equivalent:** a single electrical compartment constrained by human L2/L3 somatic voltage-clamp data. It is a preparation-equivalent model, not an anatomical soma/AIS neuron. The Wilbers fitted Na+ conductance differs substantially from directly measured nucleated-patch conductance and must remain separately tagged.
- **Anatomical soma/AIS model:** requires AIS geometry and functional channel-density/gating evidence. Human NaV1.2/NaV1.6 immunolocalization is spatial subtype evidence only; it does not supply functional conductance or gating parameters. Eyal et al. provides human AP targets and fitted soma/axon conductances, but assumes rodent-like kinetics and does not fit active dendritic conductances.

### Wilbers human Na+/K+ mechanism runtime audit

The original pure human \`na_human.mod\` and \`k_human.mod\` files were retrieved from the CC0 DataverseNL deposit and compiled unchanged in NEURON 9.0.2. Direct compiled calls at exact \`trap0\` singularities return non-finite values. The active Na+ lookup table has 200 nodes over −120 to +100 mV; all nodes were finite, but disabling that table exposes non-finite rates at the exact singular voltages. The K+ mechanism has no active table; its direct singularities are non-finite and two opposite-sign branch triggers produce negative inactivation time constants. No source correction was applied.

The K+ pure mechanism matches Table S2 and the first optimizer result, but the fitting script's later final dictionary differs; it also assigns an undeclared \`h12factor_k_human\`. The paper's 14-parameter methods count remains unreconciled with the visible staged fit variables. The full Wilbers voltage-clamp fitting workflow was not rerun from raw traces; the deposited per-cell workbooks are fit summaries and the original NWB traces were not present in the Dataverse listing examined.

### Eyal canonical model source and execution audit

The official 139,316,573-byte ModelDB 238347 archive was retrieved and audited (SHA-256 \`12dfd8b8fb38b28136d6904da69aaf5e200fa5fb64cd03d845a96d972057354b\`). All six original HOC templates map to Table S4 parameter sets. The six spike models insert nine conductance mechanisms in soma/axon plus CaDynamics_E2. Ca_HVA is in the archive but not inserted by those six templates; NMDA.mod is used in separate synaptic workflows. The HOC templates replace the axon with a two-section 60 μm stub and leave dendrites passive. Table S4's fitted values are not direct measurements of channel abundance.

The ten mechanisms actually inserted by the six templates compiled with NEURON 9.0.2. A Python 3 runner reproduced the Figure 7A morphology, section construction, channel insertion, temperature, time-step, initial-voltage, current-step and recording procedure for all six cells, and compared first-spike metrics to released current-clamp repetitions. Several model/data metrics differ. This is a selected-stimulus source/model reproduction, not a model refit, exact trace match, or biological validation.

No AP-capable HumanJS mechanism should be added by copying the external model wholesale. The next admissible step is an independently specified, numerically stable human somatic-patch-equivalent mechanism using clearly tagged human measurements, fitted model values, and transferred functions. Validate voltage-clamp behavior and AP waveform features separately. AIS-resolved modeling remains a stricter separate evidence gate. Software tests and execution of published models do not establish biological validity or whole-brain functionality.
