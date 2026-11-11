# HumanJS — target system architecture

**Status:** accepted direction, with two foundational CPU mechanisms and one exploratory spike-capable CPU mechanism present.  
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


## 13. Intrinsic spike-initiation boundary — exploratory code, not scientific acceptance

The Rust core now contains `HumanL23SingleCompartmentModel`, an exploratory single-compartment Na+/K+ conductance model that can generate an action potential under a specified current-clamp pulse. Its presence supersedes earlier documentation stating that no spike-generating code exists. It does **not** supersede ADR-014's scientific acceptance gate: the implementation is provisional, its source choices are not fully reconciled, and its tests establish software behavior rather than biological validity.

The model uses:
- Human Na+ activation/inactivation gate parameters transcribed from the pure Wilbers `na_human.mod` source.
- Human K+ activation and fast/slow inactivation parameters from the pure Wilbers `k_human.mod` file and the matching Table S2 / first optimizer result.
- The current-clamp fitted maximum conductance densities (114.48 pS/μm² Na+ and 29.05 pS/μm² K+), which are optimization outputs against cross-species mean AP features, not direct human channel-density measurements.
- The deposited current-clamp setup: a 10 μm × 10 μm cylindrical compartment, 34°C, −10 mV channel voltage shift, +15 mV reversal-potential offsets, 1 μF/cm² capacitance, leak density corresponding to Rm=10,000 Ω·cm², and a 20 μs maximum integration step.
- A fixed-step RK4 integrator, explicit gate states, finite/bounded state checks, and transactional state updates.

The Rust `trap0` implementation uses a stable expression with the analytic limit at the mathematical singularity. This is a deliberate numerical reinterpretation of a problematic source function, not an exact reproduction of its branch behavior. The K+ fit script's trailing alternate six-parameter dictionary is a bare literal and is never assigned or applied; the executed sequence applies the first optimizer result, which matches Table S2 and the pure mechanism. Its `h12factor_k_human=10.5` assignment is unused in the deposited variants: the pure and two hybrid K+ NMODL files contain only a commented-out `h2tau = h1tau * h12factor` line, with no active declaration or use, and the protocol helper does not read the Python attribute. The article's 14-parameter description includes two inactivation steady-state values assigned from experimental fits and an independent `Rb`; the deposited scripts fix the former and set `Rb = Ra`, so they optimize 11 independent values. The pure Na+/K+ NMODL files explicitly annotate rate prefactors as `/ms`, matching Table S2, but the source `trap0` expression multiplies them by a voltage-valued numerator. Dimensional consistency requires `mV^-1 ms^-1`; HumanJS retains the numeric values and uses that equation-consistent internal unit without rescaling. This source-declared/equation-derived unit mismatch and the limited fit workflow require protocol-level verification.

The model is a single electrically lumped compartment. It has no spatially resolved soma, AIS, axon, dendrites, cable propagation, channel subtype gradients, or neuron-population interactions. Do not describe it as an intact human pyramidal neuron, an anatomical soma/AIS model, or a biological reproduction. The test pulse and waveform-scale assertions are software regression fixtures, not independent validation against the full human voltage-clamp protocols.

The original evidence review remains in `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`; the external Eyal source/model reproduction remains in `experiments/HUMAN-L23-SPIKE-MODEL-REPRODUCTION.md`. Eyal's six-cell soma/60 μm axon models use transferred rodent-like kinetics and are not a human gating-parameter source.

## 14. Validation status and acceptance gate for the exploratory spike model

Before this mechanism is promoted from exploratory code:
1. Preserve the now-traced deposited K+ execution path (first optimizer result applied; trailing dictionary unused), and independently reproduce the fast/slow K+ voltage-clamp and recovery protocols. Confirm whether any separate mechanism variant consumes `h12factor_k_human` before treating it as a no-op globally.
2. Retain the distinction between the article's 14-parameter parameterization and the deposited 11-variable optimizer workflow (two inactivation steady states fixed from experiments; `Rb = Ra`); verify the corresponding K+ constraints in a protocol reproduction.
3. Resolve the source-declared `/ms` versus equation-derived `mV^-1 ms^-1` rate-prefactor dimensional mismatch against the original NEURON unit-checking contract before describing the internal reinterpretation as source-faithful.
3. Audit every transcribed parameter's unit and temperature convention against the original NMODL source, including rate-prefactor dimensional interpretation and the difference between pure voltage-clamp and hybrid current-clamp variants.
4. Compare Na+ and K+ steady-state curves and time constants over the published voltage ranges against the deposited mechanisms and human experimental summaries, including singularity neighborhoods and the full K+ fast/slow recovery behavior.
5. Reproduce the authors' voltage-clamp protocols at their stated temperatures and time steps, or clearly state why the available public summary data cannot support a full trace-level reproduction.
6. Verify the current-clamp conductance-fit setup, including the human/mouse averaging objective, geometry, reversal offsets, leak, channel shifts, and the relationship between reported AP targets and the Rust fixture.
7. Add independent tests for gate steady states, time constants, recovery trajectories, current balance, pulse timing, step-size convergence, and comparison with published human targets. Keep software verification distinct from biological validation.

The current code's tests cover selected rate-function stability, positive finite time constants over a bounded voltage scan, Q10 factors, one-spike waveform scale, approximate step-size convergence, reset, and transactional failure. They do not yet satisfy the above validation gate. No AIS conductance may be inferred from immunostaining. No biological validation, clinical validity, whole-brain functionality, or consciousness claim is made.
