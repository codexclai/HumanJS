# HumanJS — owner requirements and accepted project direction

**Status:** current consolidated requirements, updated 2026-11-10.  
**Precedence:** explicit owner decisions in this conversation and later GitHub decisions supersede conflicting instructions in historical prompts and the legacy Node.js archive.

## 1. Identity and purpose

- Project name: HumanJS.
- Lowercase identifier: humanjs.
- Short identifier: ajs.
- Owner preferred name: Thamindu. The current GitHub account login may change; do not use it as the owner preferred name.
- Objective: a comprehensive, scientifically defensible computational model of a human brain.
- Scope is brain-only. HumanJS is not a whole-body simulator, chatbot, external-LLM wrapper, generic AI agent, or claim of consciousness, sentience, human-equivalent intelligence, or biological completeness.
- External physical, virtual, robotic, simulated, or other hosts may supply peripheral/body/environment signals and receive brain outputs through explicit interfaces. HumanJS does not silently absorb those external systems into its scope.

## 2. Approved implementation technologies

- Rust: native computational core, simulation/runtime, biological mechanisms, native APIs, scheduling, resource management, concurrency, and persistence.
- WGSL: GPU compute shaders.
- Python: primary developer-facing API, scientific workflows, experiments, analysis, tooling, and orchestration at the developer boundary.
- C: native interoperability through a deliberately designed C ABI.
- C++: native interoperability and ergonomic C++ wrappers.

Node.js, JavaScript, TypeScript, npm, package.json-based distribution, and JavaScript runtimes are discontinued. Do not introduce them in active source, workflows, tooling, packaging, examples, documentation instructions, or dependencies unless the owner explicitly changes this decision. Mentions may remain in clearly marked historical records.

Rust and Python are the primary implementation surfaces. C ABI and C++ are interoperability layers, not competing simulation cores. WGSL is compute code, not a replacement for the biological model or CPU implementation.

## 3. Architecture and interfaces

- The native Rust core owns simulation truth and state transitions.
- Python is the principal developer-facing surface. It should feel native, typed, discoverable, and documented. It must not be a thin remote wrapper around another AI or process.
- C ABI functions require explicit ownership, lifetime, error, buffer, and thread-safety contracts. Do not expose unstable Rust layout directly.
- C++ wrappers should build on the stable C ABI unless an evidence-backed reason warrants another boundary.
- GPU compute is an execution backend for measured workloads. CPU remains the correctness reference and a supported fallback.
- Hardware/backend selection must use actual capability discovery and correctness/performance tests, not assumptions.
- Architecture, data formats, extensions, folder layouts, and API boundaries may be redesigned when justified. Do not preserve old layouts merely for compatibility.

## 4. Brain data, model definitions, and persistence

- Applicable inspectable brain/model/IR definition files should use the .json extension.
- Brain architecture, model definitions, initial configuration, live runtime state, learned state, and save/restore checkpoints are separate concepts and must not be conflated.
- A model definition is not a pretrained or experienced brain. Do not ship a previously initialized brain as the default model.
- Document semantics, units, validation, provenance, integrity, compatibility boundaries, and resource-safety behavior.
- Save/restore is a retained owner requirement. Restoration must preserve enough information for correct continuation and reject malformed, truncated, inconsistent, or resource-exhausting input safely.
- Do not invent a file format, fixed schema, compatibility guarantee, or migration path before it is needed and designed.

## 5. Scale, concurrency, and runtime operation

- Retain a configurable default of 10,000 spiking neuron units. This is an owner-requested engineering starting point, not a biological neuron-count claim or hard maximum.
- Retain native multi-threaded/worker execution. Implement concurrency through Rust-native threads and scheduling, not Node.js worker_threads.
- Support save/restore, safe interruption, pausing/resuming where applicable, checkpointing, recovery, and observability.
- Avoid arbitrary product/input ceilings. Use streaming, backpressure, cancellation, hardware-aware resource budgets, and graceful degradation. Keep justified safety bounds against malformed data, memory exhaustion, runaway workloads, and denial of service.
- Support CPU-only execution. Integrated and discrete GPUs are candidate targets; hybrid CPU/GPU execution is an objective, not a current capability claim.
- Never claim GPU acceleration until a supported device executes the relevant WGSL path and reproducible measurements demonstrate the result.

## 6. Biological authenticity and cognitive boundaries

The goal is not to imitate cognition with generic software tables or manually scripted features. Biological mechanisms must be represented as causal interacting systems to the extent supported by evidence and computational feasibility.

Do not substitute software conveniences for biological mechanisms, including:
- Fact, answer, truth, or preloaded semantic tables as memory or knowledge.
- English-only grammar parsers or built-in lexicons as biological language processing.
- Integer object-ID trackers as perceptual identity or object continuity.
- Numbered software goal slots or host-managed goal registries as executive cognition.
- Fixed 80 ms task-switch costs.
- Capped exact-sequence lookup tables as temporal memory.
- Fixed signed-current synapses without appropriate receptor, transmitter, release, and postsynaptic mechanisms.
- Global scalar dopamine, orexin, histamine, or other neuromodulator values as substitutes for spatially and temporally structured chemistry.
- Arbitrary regional proportions or pathways presented as measured human anatomy.
- A generic FFT/Goertzel transform presented as a cochlea or biological hearing.
- Numeric image-feature input presented as a retina or biological vision.
- Coarse light reset, a single sleep setting, or unvalidated recall routines presented as complete circadian, sleep, or hippocampal mechanisms.
- Brainstem nucleus labels without corresponding causal physiology.

Retinal neural circuitry and evidence-bounded cochlear/auditory-nerve transduction must be represented at the sensory boundary, or an explicit external transducer must actually implement those mechanisms and deliver causal neural outputs. HumanJS is not required to simulate the entire eye, ear, body, peripheral nerves, or environment.

Generalized learning and interacting neural systems should produce language, symbols, semantic knowledge, object continuity, goals, prediction, planning, memory, and behavior. Innate structure may encode evidence-supported anatomy, cell classes, receptor types, developmental constraints, and connectivity priors with provenance and uncertainty; it must not preload cultural, lexical, or factual knowledge.

## 7. Evidence and validation

- Prefer primary literature, human evidence, and authoritative technical documentation.
- Label species, preparation, method, anatomical resolution, sample/measurement limits, and whether a claim is direct human evidence, animal evidence, imaging/tractography, postmortem histology, computational inference, or engineering convention.
- Record source citations, parameter provenance, uncertainty, disputed evidence, and alternative interpretations.
- Distinguish measured values from estimates, model parameters, experimental hypotheses, and convenience defaults.
- Tests establish only the properties they actually exercise. A passing software test is not biological validation.
- Never claim consciousness, sentience, subjective experience, human-equivalent intelligence, biological completeness, clinical validity, or full-human behavior without appropriate evidence.

## 8. Engineering quality and maintenance

- Build real, integrated, testable functionality. Names, schemas, diagrams, region inventories, API declarations, and placeholders are not completed mechanisms.
- Design for modularity, portability, explicit contracts, maintainability, reliability, observability, resource safety, and reproducibility.
- Detect and report actual hardware, OS, architecture, CPU/GPU features, memory, and resource limits before selecting execution strategies.
- Keep Python, Rust, C ABI, C++, and WGSL interfaces consistent and test interoperation.
- Use dependencies only when they solve a justified need. Record dependency rationale and security posture.
- Run focused checks for every change and broad suites at appropriate milestones. Never hide, weaken, or delete a failing test to manufacture a pass.
- Record exact test commands, environment, results, timeouts, failures, and unrun tests. Never claim an unrun test passed.

## 9. Documentation, history, and organization

- GitHub is the source of truth for current source, documentation, decisions, issues, experiments, workflows, and history.
- Keep the repository organized and non-duplicative. Maintain one canonical owner-requirements document and one canonical current status/handoff.
- Preserve useful original prompts, source material, research, unique experiment records, and meaningful history in clearly separated archival locations.
- Separate active project material, research, experiments, legacy material, deferred work, backups, and disposable temporary artifacts.
- Every substantive change or owner decision must have an appropriate record with reason, impact, provenance, verification, and follow-up.
- Do not manufacture folders, files, tests, workflows, or architecture merely to look comprehensive.

## 10. Explicitly superseded legacy requirements

Former Node.js requirements are no longer active: Node.js runtime/version targets; JavaScript/TypeScript implementation; npm or private npm packaging; package.json distribution allowlists; Node.js worker_threads APIs; Artificial/ with .ajs-only definitions; legacy single-file/five-file package constraints; Generation 1 compatibility tied to that runtime; and the old ZIP as the required deliverable.

The original Applys text is preserved in the legacy input record only as historical provenance. Where it conflicts with this current document and later explicit owner decisions, this current document controls.