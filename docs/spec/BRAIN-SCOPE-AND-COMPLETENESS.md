# HumanJS — brain scope and completeness specification

**Status:** accepted end-state scope; not an implementation claim.  
**Updated:** 2026-11-10.  
**Authority:** current owner decisions, docs/OWNER-REQUIREMENTS.md, and docs/decisions/DECISIONS.md.

## 1. Purpose and scope

This specification defines the breadth of the intended HumanJS model and the evidence required before any capability is called implemented or validated. HumanJS is a computational model of a human brain, not a whole-human or whole-body simulator. External biological, physical, digital, virtual, simulated, or robotic hosts may provide the body, peripheral transduction, environment, and effectors through explicit bidirectional interfaces.

The objective is broad generality across contexts, sensory modalities, tasks, languages, cultures, and compatible hosts. It is not a chatbot, external-LLM wrapper, task-specific controller, or claim that the software is conscious, sentient, or equivalent to a human.

## 2. Meaning of completeness, scalability, and limits

- Pursue the widest scientifically defensible set of neural systems and interactions; do not optimize only one narrow cognitive feature.
- Remove arbitrary fixed product limits where a resource-derived, configurable, validated design is practical.
- Derive engineering capacity from the declared model, actual memory/compute, detected hardware, and explicit resource budgets. Make these observable and configurable when safe.
- Preserve biologically meaningful constraints such as refractory periods, competition, interference, limited attention, fatigue, finite working memory, and homeostatic trade-offs.
- Never promise literal infinity, unlimited physical resources, unlimited simultaneous executive control, or complete reproduction of the biological brain.
- Retain a configurable default of 10,000 spiking neuron units as an engineering starting point only. Keep spiking units separate from rate/mean-field units and state variables; this is not a claim about the number of neurons in a human brain.

## 3. Completion and evidence states

| State | Required meaning |
|---|---|
| Not implemented | No meaningful runtime mechanism exists. |
| Specified/researched | Requirements and evidence exist; runtime behavior does not. |
| Structural proxy | A population, route, region label, or data structure exists; function is not established. |
| Implemented, unvalidated | Runtime behavior exists but lacks adequate causal or behavioral validation. |
| Experimental | Exploratory, opt-in, seed-sensitive, provisional, or failure-prone behavior. |
| Partially validated | Reproducible tests support a bounded claim, with important gaps remaining. |
| Validated within scope | Predeclared, reproducible tests support the exact computational claim and disclose external-validity limits. |

A region is not complete because it has a name. A pathway is not complete because a connection was declared. A cognitive function is not complete because an API accepts an input. A passing software test is not biological validation.

For each significant requirement, maintain a traceable record containing: stable requirement ID; biological scope; computational interpretation; evidence and species; uncertainty; parameter provenance; implementation paths; dependencies; tests/assays; known gaps; and reviewed status.

## 4. Whole-brain scope catalogue

Every category below is an intended area of coverage. The specification does not imply that every structure or mechanism is already resolved by neuroscience or can be modeled at full biological scale.

### 4.1 HB-ANAT — global anatomy, cell populations, and microcircuits

- Bilateral brain organization and hemispheric asymmetries where supported.
- Cerebral lobes, cortical areas, layers, laminar input/output patterns, areal boundaries, columns, and local recurrent circuits.
- Excitatory/inhibitory cell classes, interneuron diversity, projection classes, morphology-informed populations, and developmental lineages where evidence permits.
- Subcortical nuclei and subnuclei, cell classes, local circuits, input/output organization, and laterality.
- Synapses, receptor classes, short- and long-term plasticity, conduction, release dynamics, and neuromodulatory receptors.
- Astrocytes, oligodendrocytes, microglia, and other relevant glia with metabolic, myelination, immune, extracellular, and synaptic-support functions.
- Cellular excitability, ion channels, membrane dynamics, adaptation, refractory periods, stochasticity, homeostasis, and metabolic constraints.
- Vascular/metabolic coupling where needed to model state regulation or compare against human measurement modalities.

### 4.2 HB-CORTEX — cerebral cortex

- Primary sensory cortices for vision, audition, somatosensation, gustation, olfaction, vestibular and interoceptive representations.
- Secondary and association sensory cortices; visual dorsal/ventral streams; auditory association; multisensory integration.
- Posterior parietal, intraparietal, temporoparietal, spatial, and body-centered representations.
- Distinct prefrontal subdivisions including dorsolateral, ventrolateral, orbitofrontal, medial, frontopolar, and related territories.
- Premotor, supplementary motor, cingulate motor, and primary motor territories.
- Insular cortex, anterior/mid/posterior cingulate, retrosplenial, posterior-medial, temporal association, and language-related networks.
- Cortical layers, feedforward/feedback organization, recurrent dynamics, lateral interactions, oscillations, and state-dependent gain.

### 4.3 HB-DIENCEPHALON — thalamus and diencephalon

- Sensory relay nuclei and modality-specific subdivisions.
- Higher-order thalamic nuclei, mediodorsal subdivisions, pulvinar, intralaminar and midline nuclei, and thalamic reticular nucleus.
- Thalamocortical/corticothalamic loops and state-dependent relay dynamics.
- Hypothalamic nuclei and subnuclei for homeostasis, endocrine regulation, feeding, thirst, temperature, stress, circadian timing, reproduction, and sleep/wake control.
- Epithalamus, habenula, pineal/circadian interfaces, and other diencephalic structures.
- Explicit separation of direct human evidence, cross-species inference, and model assumptions.

### 4.4 HB-BASALGANGLIA — basal ganglia, valuation, and action selection

- Caudate, putamen, ventral striatum, pallidal divisions, subthalamic nucleus, substantia nigra, ventral pallidum, and related territories.
- Direct, indirect, and hyperdirect pathways and cortico-striato-pallido-thalamo-cortical loops.
- Limbic, associative, and motor territories; dopamine-dependent plasticity and other neuromodulatory influences.
- Action initiation/suppression, arbitration, vigor, habits, reinforcement learning, goal-directed behavior, and uncertainty-sensitive choice.
- Action selection must arise from interacting neural dynamics and learning, not a host-managed task-slot registry.

### 4.5 HB-MEMORY — hippocampal formation and memory

- Entorhinal cortex, dentate gyrus, CA fields, subiculum, and relevant parahippocampal/perirhinal interactions.
- Pattern separation/completion, recurrent dynamics, episodic binding, spatial/context representations, consolidation, replay, reconsolidation, interference, forgetting, and retrieval.
- Distributed working, episodic, semantic, procedural, autobiographical, and spatial memory systems with distinct mechanisms and evidence boundaries.
- Memory must not be implemented as a fact database, answer table, preloaded semantic store, or a discrete capped sequence lookup.

### 4.6 HB-LIMBIC — amygdala, motivation, affect, and valuation

- Amygdalar subdivisions and interactions with hippocampal, sensory, cortical, hypothalamic, and brainstem systems.
- Threat/safety learning, reward, aversion, salience, motivation, affective regulation, and value updating.
- Distinguish directly modeled neural mechanisms from external labels used for experiment scoring or observability.

### 4.7 HB-BRAINSTEM — brainstem, cerebellum, and cranial systems

- Midbrain, pons, medulla, reticular formation, cranial motor/sensory nuclei, and relevant monoaminergic/cholinergic nuclei.
- Cerebellar cortex, deep nuclei, Purkinje/granule/interneuron/UBC cell classes where supported, and cerebellar afferent/efferent loops.
- Autonomic, respiratory, cardiovascular, arousal, orienting, posture, balance, eye/head movement, and cranial motor-related brain circuits.
- Rhythm generation, reflexes, state regulation, and descending pathways require causal physiology; a nucleus label is not a functioning circuit.
- Body organs, muscles, and peripheral mechanics remain outside HumanJS and connect through explicit external interfaces.

### 4.8 HB-SENSORY — sensory transduction and perception

- Visual processing must include retina-related neural circuitry or an explicitly external transducer that actually implements retinal mechanisms and delivers corresponding neural signals.
- Auditory processing must include evidence-bounded cochlear/auditory-nerve transduction or an explicitly external transducer that actually implements it.
- Somatosensory touch, pain, temperature, proprioception, vestibular, olfactory, gustatory, interoceptive, and relevant visceral inputs require anatomically and physiologically qualified pathways.
- Multisensory binding, spatial/temporal integration, attention, prediction, adaptation, noise, and uncertainty must arise from integrated neural processing.
- Numeric feature vectors, generic FFT/Goertzel analysis, or caller-supplied stable object IDs must never be described as biological sensory transduction or perception.

### 4.9 HB-MOTOR — motor planning and external action interface

- Motor planning, premotor and motor cortical dynamics, basal-ganglia/cerebellar interactions, brainstem descending systems, and relevant spinal/peripheral host interfaces.
- Distinguish neural motor commands and predictions from external muscle activation, body mechanics, movement, and environment simulation.
- Any behavioral claim must specify the host plant/effector model and measure the brain-host closed-loop behavior separately from internal neural activity.

### 4.10 HB-EXECUTIVE — attention, control, and multitasking

- Distributed frontoparietal, cingulo-opercular, thalamic, basal-ganglia, and other evidence-supported interactions.
- Selection, maintenance, switching, interruption, resumption, prioritization, conflict, and resource competition.
- Multiple concurrent environmental inputs may be processed through shared neural resources; do not imply unlimited independent executive capacity.
- Task-switch costs and interference must emerge from the modeled dynamics rather than fixed hand-authored delays.
- Externally specified tasks/goals may serve as experimental stimuli, but they must not be mistaken for the brain internal goal representation.

### 4.11 HB-LANGUAGE — language and communication

- Language should emerge from learned perception, action, social interaction, memory, prediction, and distributed neural representations.
- Support generalization across languages, symbol systems, contexts, and modalities without hard-coded English-only grammar, lexicons, or templates.
- Grounded semantic/syntactic behavior must be tested on held-out examples and interventions, with cognitive boundaries explicitly reported.
- Do not substitute an English grammar parser or built-in factual ontology for neural language learning.

### 4.12 HB-COGNITION — learning, reasoning, and general cognition

- Generalization, abstraction, concept learning, prediction, causal inference, counterfactual reasoning, compositionality, planning, and adaptive behavior.
- Integrate reinforcement, supervised/social learning, unsupervised structure learning, and learning from action/outcome where biologically justified.
- Concepts and symbols must be grounded through repeatable links to perceptual, action, outcome, internal-state, or episodic experience.
- Distinguish internal neural mechanisms from external test decoders, host APIs, and evaluator convenience.

### 4.13 HB-REGULATION — neuromodulation and homeostasis

- Dopaminergic, noradrenergic, serotonergic, cholinergic, histaminergic, orexinergic, and other relevant modulatory systems.
- Anatomically sourced nuclei, spatially meaningful release/transport/clearance, receptor-specific effects, and distinct timescales where evidence supports them.
- Homeostatic regulation of energy, temperature, fluid balance, stress, arousal, and internal state through brain circuits and external body interfaces.
- A single global scalar per transmitter is not an adequate replacement for spatially and temporally structured chemistry.

### 4.14 HB-SLEEP — sleep, dreaming, and offline processing

- Circadian timing, sleep pressure, arousal, NREM/REM-related network and regulatory dynamics, and state transitions.
- Memory replay/consolidation, synaptic/homeostatic processes, and interactions with learning and plasticity.
- Do not present one tuned sleep setting or a coarse threshold as complete sleep physiology. Do not claim subjective dreaming.

### 4.15 HB-DEVELOPMENT — development, aging, and plasticity

- Developmental constraints, critical periods, maturation, experience-dependent circuit refinement, homeostasis, aging, and plasticity across timescales.
- Separate fixed innate/anatomical priors from learned state and from optional developmental simulations.
- Model only mechanisms with an explicit evidence boundary and meaningful computational purpose.

### 4.16 HB-HOST — brain/body interface with external body

- A bidirectional, typed, documented integration contract for sensory input, interoceptive state, motor output, timing, synchronization, and errors.
- Host capabilities must be discoverable; optional channels must be explicit; units, rates, timestamps, coordinate frames, provenance, and backpressure must be documented.
- Host integrations may represent physical, biological, digital, virtual, robotic, or simulated environments.
- Do not embed body simulation into the brain core merely to simplify interfaces.

### 4.17 HB-SOCIAL — social, affective, and cultural cognition

- Learn from interaction, communication, observation, imitation, social feedback, and environmental regularities.
- Support social inference, attachment-related processes, empathy-related behavior, norms, and culture-dependent learning only as evidence-bounded targets.
- Do not hard-code a cultural/factual knowledge base and present it as cognition.

### 4.18 HB-CONSCIOUSNESS — claims and research boundary

- HumanJS may study neural correlates, state transitions, and computational theories of consciousness if scientifically justified.
- Do not claim that the software is conscious, sentient, has subjective experience, or is human-equivalent.
- A behavioral demonstration or language output is not evidence of subjective experience.

### 4.19 HB-INTEGRATION — system architecture and operation

- Integrate cell, synapse, circuit, region, network, memory, regulation, cognition, sensory, and host-interface dynamics into one causally interacting system.
- Maintain CPU-only execution and graceful fallback. GPU acceleration is a measured backend objective implemented through Rust-owned execution and WGSL kernels.
- Preserve safe pause/resume, interruption, checkpointing, save/restore, recovery, observability, resource budgets, and native multi-threaded operation.
- Keep Rust as the core, Python as primary developer interface, C ABI as stable native boundary, C++ as wrapper/interoperability, and WGSL for GPU compute.

## 5. Evidence and parameter provenance

For each anatomical or physiological claim, record where applicable:

- Species, age/developmental stage, health status, sample/donor count, preparation, and tissue or measurement method.
- Direct human anatomy/histology, human imaging/tractography, human functional/lesion evidence, comparative animal anatomy, comparative animal physiology, computational inference, or engineering convention.
- Spatial resolution, limitations, conflicting evidence, uncertainty, and the difference between connectivity association and synapse-resolved direction/sign/efficacy.
- Whether a parameter is directly measured, inferred, estimated, fitted, experimentally calibrated, or chosen as an engineering default.

Do not treat tractography as proof of monosynaptic direction, sign, efficacy, or delay. Do not treat population-allocation percentages as human cell census data. Do not invent universal human parameters.

## 6. Validation ladder

1. **Software integrity:** unit/numerical tests, serialization correctness, memory/resource safety, determinism within defined conditions, and API contracts.
2. **Cell/mechanism behavior:** membrane, channel, receptor, release, plasticity, and state-variable response assays against appropriate literature or data.
3. **Circuit causality:** predeclared input/output behavior, interventions, ablations, matched controls, and alternative pathway checks.
4. **Network behavior:** multi-seed robustness, held-out generalization, realistic competition/interference, and relevant temporal dynamics.
5. **Integrated system behavior:** cross-region, cross-modal, learning/memory, state regulation, and external host loop validation.
6. **Human correspondence:** appropriately matched empirical comparisons with explicit measurement and model-resolution limits.

Passing a level supports only the scope tested. A failure, timeout, unrun test, or unavailable hardware must remain visible. A focused software pass does not imply biological validation.

## 7. Progress accounting

Do not report a single percentage for the completeness of a real human brain. Maintain separate measures for software implementation coverage, requirement traceability, and biological validation depth. Each measure must state its denominator, date, exclusions, evidence, and limitations.

## 8. Change control

Update this specification when owner requirements, scientific evidence, model mechanisms, or validation results change. Record substantive decisions in docs/decisions/DECISIONS.md and current progress in docs/status/STATUS.md. Keep evidence details and experiment records in the canonical research/ and experiments/ areas as they are migrated. Never silently promote a structural proxy or an experimental result to a validated mechanism.

## 9. Current state

This specification defines intended scope; it is not a claim that all catalogue items are implemented. The current Rust repository contains a typed CPU passive-membrane mechanism and an effective human L2/L3 glutamatergic synapse mechanism integrated with that membrane. Their software-level verification and scientific boundaries are recorded in \`docs/status/STATUS.md\` and the corresponding research notes.

The external NEURON experiment under \`experiments/\` audits the canonical Eyal et al. six-cell soma/axon model source and selected Figure 7A spike responses. It is an external model reproduction and parameter/source audit, not a HumanJS intrinsic spike mechanism. The Wilbers pure human somatic Na+/K+ channel source files have been compiled and their numerical edge cases inspected in NEURON, but parameter discrepancies remain unresolved. Human somatic nucleated-patch and anatomical soma/AIS models remain distinct evidence targets.

The exploratory `HumanL23SingleCompartmentModel` can generate an action potential in its checked-in software fixture, but it is not accepted or biologically validated. No whole-neuron, AIS-resolved, population, network, cognitive, or whole-brain mechanism listed elsewhere in this specification should be treated as implemented until integrated code and scoped validation exist. The configurable 10,000-unit spiking population, multi-compartment morphology, network integration, save/restore, Rust-native concurrency, JSON model loading, Python package, C ABI, C++ wrapper, and integrated WGSL backend remain unimplemented.
