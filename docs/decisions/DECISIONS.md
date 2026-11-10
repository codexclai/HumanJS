# HumanJS — decision record

**Decision authority:** project owner.  
**Updated:** 2026-11-10.

This is the canonical record of currently accepted decisions. Later explicit owner decisions may supersede these entries.

## ADR-001 — Project identity and scope

**Status:** Accepted · **Date:** 2026-11-10

- Name: HumanJS; lowercase identifier: humanjs; short identifier: ajs.
- Scope: computational human brain only.
- Not a chatbot, external-LLM wrapper, whole-body simulator, or claim of consciousness, sentience, subjective experience, or human equivalence.

## ADR-002 — Approved implementation stack

**Status:** Accepted · **Date:** 2026-11-10

Active implementation technologies are Rust, WGSL, Python, C, and C++. Rust is the native core; WGSL is for GPU compute; Python is the primary developer interface; C ABI and C++ provide interoperability. Node.js, JavaScript, TypeScript, npm, package.json distribution, and JavaScript runtimes are discontinued. No compatibility port is required.

## ADR-003 — GitHub is the sole source of truth

**Status:** Accepted · **Date:** 2026-11-10

The HumanJS GitHub repository, branch `main`, is the sole canonical source for current code, docs, requirements, decisions, research, experiments, issues, workflows, and history. Each ChatGPT session refreshes from live GitHub at startup. The ChatGPT Project Sources area may remain empty; no uploaded or separately synchronized project source is required. Releases, Packages, and Deployments are optional and used only when a real distribution or hosted-service need exists.

## ADR-004 — Public repository and Apache-2.0

**Status:** Accepted · **Date:** 2026-11-10

The repository is public and uses Apache License 2.0. Owner original contributions are attributed in `NOTICE`. Contributors retain copyright in their own contributions; the repository license governs redistribution and use. Public source cannot be made uncopyable through repository settings or a license.

## ADR-005 — Keep the working tree current and minimal

**Status:** Accepted · **Date:** 2026-11-10

The working tree contains current accepted requirements, architecture, source, reviewed research, reproducible experiments, tests, and necessary tooling. Do not maintain duplicate input bundles, retired project snapshots, unreviewed implementation dumps, or general-purpose backup trees. Git history provides the ordinary record of project and code changes. Promote research or experimental material only when relevant to a concrete task and after provenance, evidence quality, and redistribution review.

## ADR-006 — Data formats may be redesigned

**Status:** Accepted · **Date:** 2026-11-10

Former Node-specific persistence and API formats are not binding. Applicable inspectable brain/model/IR data should use JSON. Model definitions, initial conditions, live state, learned state, and checkpoints are distinct. Choose runtime persistence representation after correctness, safety, size, inspectability, and performance testing.

## ADR-007 — Retained runtime requirements

**Status:** Accepted · **Date:** 2026-11-10

Save/restore remains required. Native worker/multi-threaded execution remains required and must use Rust-native concurrency. A configurable default of 10,000 spiking neuron units remains required. Rate/mean-field units and state variables are counted separately. The default is an engineering choice, not a biological count or hard maximum.

## ADR-008 — Biological mechanisms, not software stand-ins

**Status:** Accepted · **Date:** 2026-11-10

Cognition and biological function must arise from causal, interacting, appropriately evidenced systems. Do not substitute fact/grammar tables, object-ID registries, goal slots, fixed switching timers, capped sequence tables, global scalar neuromodulators, or simplistic sensory transforms for biological mechanisms. Record uncertainty and evidence provenance.

## ADR-009 — Public-project safety and repository hygiene

**Status:** Accepted · **Date:** 2026-11-10

The repository is public. Keep credentials, secrets, private data, temporary output, duplicate snapshots, and unlicensed material out of the working tree and Git history. Use canonical paths for current research and experiments. Keep workflows read-only unless a specific write permission is necessary, pin external actions to reviewed immutable SHAs, and verify results.

## ADR-010 — Permanent main-only workflow

**Status:** Accepted · **Date:** 2026-11-10

`main` is the only branch to use permanently. Never create, check out, update, merge, or otherwise use another branch. Make authorized changes directly to `main`. Do not create project pull requests or branch-generating automation. Do not require or configure rulesets, branch protection, or branch-deletion-prevention settings. Force pushes are permitted but exceptional, inspected, and verified. Existing non-main refs are unused leftovers; inspect unique commits before deletion and report tool limitations honestly.

## ADR-011 — No unnecessary credential or environment infrastructure

**Status:** Accepted · **Date:** 2026-11-10

HumanJS has no requirement to store credentials, private user data, or secrets. Do not add authentication, secret-management systems, `.env`, `.env.example`, dotenv, or generic environment-file infrastructure without a specific approved product requirement.

## ADR-012 — First CPU mechanism is a bounded passive membrane patch

**Status:** Accepted · **Date:** 2026-11-10

Start the native Rust implementation with a single-compartment passive membrane patch. It solves the lumped RC equation for a piecewise-constant injected current using its analytic exponential solution. This establishes typed SI quantities, integer simulation time, separation of model parameters/initial conditions/live state, and testable CPU behavior without claiming a complete neuron.

No universal human parameter defaults are introduced. Where input resistance and membrane time constant are supplied, the model may derive lumped total leak conductance and capacitance through `G = 1/R` and `C = tau/R`. The effective zero-current equilibrium is a reduced-model operating point, not necessarily a measured single-channel reversal potential.

The initial slice omits active currents, synaptic transmission, dendritic cable structure, spike initiation, populations, networks, persistence, concurrency, Python/C/C++ bindings, JSON loading, and GPU execution. Numerical tests validate the declared equation and software implementation only; they are not biological validation.

## ADR-013 — First glutamatergic synapse is an evidence-bounded effective conductance model

**Status:** Accepted · **Date:** 2026-11-10

Implement the first excitatory synaptic component as an AMPA/NMDA conductance input to the existing passive membrane, scoped to adult human L2/L3 pyramidal-to-pyramidal cortical connections. Use receptor-specific normalized biexponential conductance waveforms, voltage-dependent NMDA magnesium unblock, and a deterministic short-term resource model using fitted connection-level utilization/recovery parameters.

The literature-derived AMPA/NMDA waveform and peak-conductance parameters are fitted/effective parameters, not direct measurements of molecular receptor transition rates at an individual synapse. The short-term-depression utilization and recovery parameters are fitted to human paired-recording responses; applying connection-level dynamics to one effective contact is an explicit computational reduction. Keep these parameters explicit in model construction and evidence records; do not use them as universal defaults.

The first implementation deliberately excludes stochastic vesicle fusion, explicit presynaptic calcium/docking/release-site machinery, synaptic-cleft glutamate dynamics and uptake, molecular receptor Markov/desensitization states, dendritic spines/cable morphology, and inhibitory synapses. It integrates interval-mean synaptic conductances and evaluates NMDA magnesium unblock at an estimated midpoint voltage. Software tests support only these computational equations and interfaces; they do not establish biological validation.


## ADR-014 — Intrinsic spike initiation is evidence-gated and soma/AIS scopes remain distinct

**Status:** Accepted · **Date:** 2026-11-10

Do not add a threshold-only spike generator or generic rodent Hodgkin–Huxley mechanism and label it a human cortical neuron. The first possible spike-generation increment is a clearly named human somatic nucleated-patch equivalent, using a reproduced human Na+/K+ model and retaining the distinction between direct nucleated-patch measurements and fitted AP-model conductances. It must not claim anatomical AIS resolution, dendritic propagation, or intact whole-neuron behavior.

An anatomical soma/AIS model is a separate milestone. Human NaV1.2/NaV1.6 immunolocalization may constrain subtype position qualitatively but does not supply functional channel density or gating kinetics. Do not convert staining intensity or peak position into conductance parameters.

The pure human na_human.mod and k_human.mod files have now been retrieved and inspected from the CC0 DataverseNL dataset, including their checksums, gate equations, parameter values, conductance expressions and Q10/reference-temperature settings. Both files explicitly tie Rb to Ra. The K+ file itself contains the Table S2/first-optimizer parameter values, whereas the fitting script's final printed dictionary contains a different six-parameter set. The paper's stated 14 free parameters do not match the 13/11 explicit fit/assignment parameters visible in the deposited scripts after Ra=Rb is treated as one parameter. Both files also contain a trap0 branch test/fallback that does not obviously match the removable singularity in the rate equation. Its behavior under the original NEURON lookup table remains untested. The K+ fitting script assigns h12factor_k_human although that symbol is not declared in the inspected pure K+ mechanism.

The per-cell author workbooks corroborate 19 human Na+ activation records, with one lower-quality inactivation record whose exclusion reproduces the reported n=18 summary, and 13 human K+ activation / 11 K+ inactivation records. The workbook summaries are not raw current traces. The original NWB trace files were not present in the 65-file version-3.0 deposit listing examined.

**Implementation gate:** no intrinsic spike-generating code is approved until the trap0 behavior is tested in the original NEURON mechanism, the K+ parameter and 14-count discrepancies are reconciled, and the fit is reproduced against published human somatic voltage-clamp/current-clamp targets. A first somatic-patch-equivalent model must remain separate from an anatomical soma/AIS model. Do not infer AIS conductance or gating from NaV immunostaining. Before reproducing Eyal et al. (2018), reconcile Table S4 and the canonical ModelDB mechanism/compartment mapping; keep transferred rodent kinetics distinct from human-fitted conductances.

The evidence review and exact source provenance are recorded in research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md. No spike-generating code has been added, and no biological validation is claimed.
