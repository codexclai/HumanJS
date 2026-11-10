# HumanJS — session boot

**Updated:** 2026-11-10  
**Canonical source:** public GitHub repository `codexclai/HumanJS`, branch `main`.

Read this file first whenever a new session begins. GitHub `main` is authoritative. The ChatGPT Project Sources area is expected to be empty; no upload or local snapshot is a project dependency.

## Mandatory reading order

1. This file.
2. `docs/PROJECT-INSTRUCTIONS.md`.
3. `docs/OWNER-REQUIREMENTS.md`.
4. `docs/architecture/SYSTEM-ARCHITECTURE.md`.
5. `docs/spec/BRAIN-SCOPE-AND-COMPLETENESS.md`.
6. `docs/REPOSITORY-STRUCTURE.md`.
7. `docs/decisions/DECISIONS.md`.
8. `docs/roadmap/MASTER-ROADMAP.md`.
9. `docs/status/STATUS.md`.
10. `docs/operations/GITHUB-SECURITY.md`.
11. `docs/policies/REPOSITORY-HYGIENE.md`.
12. `docs/status/SESSION-HANDOFF.md`.
13. Read only the research, experiment, API, implementation, and issue records relevant to the current task.

Do not search for or request old uploads or copied source snapshots. If evidence or a design detail is missing, research or generate the needed current record from reliable sources when the task requires it.

## Current authoritative decisions

- Repository `codexclai/HumanJS`, branch `main`, is the sole source of truth for current code, documentation, requirements, decisions, research, experiments, issues, workflows, and history.
- ChatGPT Project Sources may remain empty. No project ZIP or separate source synchronization artifact is maintained or delivered.
- Keep the working tree focused on current project files. Do not add legacy source archives, duplicate inputs, general backup trees, or unreviewed historical project dumps.
- Repository is public and licensed Apache-2.0.
- Approved stack: Rust (native core), WGSL (GPU compute), Python (developer interface), C (ABI), and C++ (interop).
- Node.js, JavaScript, TypeScript, npm, JavaScript runtimes, and `.ajs` implementation are discontinued.
- Scope is a scientifically defensible computational model of the human brain only, not a whole-body simulator or chatbot.
- Preserve correct save/restore, Rust-native multi-threaded execution, and a configurable 10,000-spiking-neuron-unit default. This is an engineering default, not a biological count or hard maximum.
- CPU execution must work. GPU support is not a capability claim until actual hardware integration, correctness checks, and reproducible benchmarks succeed.
- Keep model definitions, initial conditions, live state, learned state, and checkpoints distinct.
- HumanJS has no requirement to store credentials, private user data, or secrets. Do not introduce authentication or generic secret/configuration infrastructure without an approved requirement.

## Branch policy and verified branch state

`main` is the only branch to use, permanently. Never create, check out, update, merge, or otherwise use another branch. Make authorized changes directly on `main`. Do not create branches, PRs, or automation that opens non-main update branches. No branch protection, rulesets, or deletion-prevention settings are required. Force pushes are permitted but exceptional and must be inspected and verified.

The live branch listing on 2026-11-10 returned exactly one branch: `main`. No non-main refs remained. Recheck the live branch list at the start of every session; do not rely on this historical check.

## Session procedure

1. Retrieve repository metadata and verify the owner/repository, public/private state, and default branch.
2. Fetch the live `main` HEAD and inspect the entire tracked tree. When using a local checkout, clone/fetch from GitHub and verify the checked-out commit equals the live `main` HEAD.
3. Inspect recent commits, open issues/PRs, the latest main workflow runs, and relevant CI checks. Do not use non-main refs.
4. Read this file and follow the mandatory reading order.
5. Inspect relevant source, interfaces, dependencies, data flow, and tests before editing.
6. Commit authorized changes directly to `main`; verify the commit and resulting remote HEAD.
7. Run relevant checks and report exact commands/results, failures, timeouts, and unrun checks.
8. Update canonical documentation, current status, and handoff after meaningful work.
9. Verify all GitHub operations and disclose capability limits.

## Current implementation starting point

The Rust workspace now contains two integrated CPU mechanisms in `crates/humanjs-core`.

The passive-membrane model represents one lumped compartment with capacitance, leak conductance, an effective zero-current equilibrium, initial voltage, injected current, and integer-nanosecond simulation time. Constant-current steps use the analytic passive RC solution. Its physical quantities use validated SI wrappers, and model parameters, initial conditions, and live state are distinct.

The glutamatergic synapse model adds AMPA- and NMDA-like normalized biexponential conductance waveforms, voltage-dependent NMDA magnesium unblock, and deterministic short-term depression/recovery. A presynaptic spike event scales the effective conductance response by available resources. The synaptic state is coupled to the passive membrane using interval-mean conductances and a midpoint magnesium-block approximation. The coupled membrane and synapse states are committed together only when a simulation step succeeds.

The scientific record `research/HUMAN-CORTICAL-GLUTAMATERGIC-SYNAPSE.md` separates human L2/L3 paired-recording observations from model-fitted conductance/kinetic parameters and from engineering abstractions. The current mechanism does not include stochastic vesicle fusion, explicit cleft glutamate dynamics/uptake, molecular receptor Markov states, spines/dendritic cable, active channels, action potentials, or neuron populations.

The current spike-initiation evidence review is recorded in research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md. It separates direct human nucleated-somatic-patch Na+/K+ measurements (Wilbers et al. 2023), fitted single-compartment channel parameters, human AIS NaV1.2/NaV1.6 immunolocalization (Tian et al. 2014), and the Eyal et al. (2018) soma/axon model with transferred rodent-like kinetics. The original pure human na_human.mod and k_human.mod files were retrieved from the CC0 DataverseNL deposit and their equations, parameter values, units, Q10 rules, and protocol helpers were inspected. The source files set Rb equal to Ra. The K+ mechanism file contains values matching Table S2/its first optimizer output, while the fit script's final printed dictionary differs. Both files have a questionable trap0 singularity fallback that has not been reproduced in compiled NEURON. The paper's stated 14-parameter count also does not match the visible fit parameter lists after Ra=Rb. Per-cell author workbooks were parsed and human sample counts/summary fits checked. No spike-generating code has been added: source/numerical discrepancies and lack of NEURON reproduction remain a hard implementation gate. A somatic-patch-equivalent mechanism and an anatomical soma/AIS model remain distinct targets.

See `docs/status/SESSION-HANDOFF.md` for the current verified commit, test results, scientific boundaries, and next research steps. Checkpointing, Rust-native concurrency, Python, C/C++, JSON model loading, and WGSL remain future work. Do not claim these capabilities until implemented and tested.
