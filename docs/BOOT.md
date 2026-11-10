# HumanJS — session boot

**Updated:** 2026-11-10  
**Canonical source:** public GitHub repository `codexclai/HumanJS`, branch `main`.

Read this file first whenever a new session begins. Do not assume prior chat context, Project Sources, uploads, local copies, archives, or remembered commits are current.

## Mandatory reading order

1. This file.
2. PROJECT-INSTRUCTIONS.md.
3. The preserved original owner prompt at archive/owner-inputs/Applys-everything-everywhere-everyway-maximumly-fully-completely.txt (historical input; current owner decisions control).
4. OWNER-REQUIREMENTS.md.
5. architecture/SYSTEM-ARCHITECTURE.md.
6. spec/BRAIN-SCOPE-AND-COMPLETENESS.md.
7. REPOSITORY-STRUCTURE.md.
8. policies/ARCHIVE-AND-TRASH.md.
9. decisions/DECISIONS.md.
10. roadmap/MASTER-ROADMAP.md.
11. status/STATUS.md.
12. operations/GITHUB-SECURITY.md.
13. Read research, experiment, API, implementation, and issue records relevant to the task.

## Current authoritative decisions

- Project: HumanJS; lowercase identifier: humanjs; short identifier: ajs.
- GitHub repository `codexclai/HumanJS`, branch `main`, is the sole source of truth.
- No HumanJSProject.zip is required, maintained, synchronized, or delivered. ChatGPT Project Sources may remain empty.
- GitHub Releases, Packages, and Deployments may be used when they serve a real versioned distribution, package, or hosted service; they do not replace the repository.
- Repository is public and licensed Apache-2.0.
- Approved stack: Rust (native core), WGSL (GPU compute), Python (developer interface), C (ABI), and C++ (interop).
- Node.js, JavaScript, TypeScript, npm, JavaScript runtimes, and .ajs implementation are retired.
- Scope is a scientifically defensible computational model of the human brain only, not a whole-body simulator or chatbot.
- Preserve correct save/restore, Rust-native multithreaded execution, and a configurable 10,000-spiking-neuron default. This is an engineering default, not a biological claim or hard maximum.
- **main is the only branch to use, permanently.** Never create, check out, update, merge, or otherwise use any other branch, existing or new. Make authorized changes directly on main. The intended repository state is main alone; inspect unique commits before deleting old non-main refs if deletion becomes available. Disclose limitations; never claim deletion without verification.
- Do not require or configure GitHub rulesets, branch protection, or deletion-prevention settings. Force pushes are permitted but exceptional and must be inspected and verified.
- HumanJS has no requirement to store credentials, private user data, or secrets. Do not add authentication/secret-management systems or .env/.env.example/dotenv infrastructure without a specific approved requirement.

## Project scope and evidence

HumanJS is not a whole-body simulator, chatbot, external-LLM wrapper, generic agent framework, or claim of consciousness, sentience, subjective experience, human-equivalent intelligence, clinical validity, or biological completeness. External hosts may supply peripheral/body/sensory/environment signals through explicit interfaces.

Build causal, interacting, evidence-grounded mechanisms. Avoid fact tables, fixed lexicons/grammar parsers, object-ID cognition, numbered goal slots, fixed task-switch penalties, capped sequence lookup, global scalar neuromodulators, simplistic sensory transforms, and unsupported anatomy. Distinguish human from animal evidence, measured values from estimates/model conventions, and evidence from hypotheses. Record provenance, methods, uncertainty, and validation limits.

## Current repository status

The live main HEAD and workflow state must be retrieved at each session start. Do not rely on checkpoint hashes as current. The repository has a documentation/governance foundation; inspect current files before claiming any implementation. No simulation mechanism, biological validation, GPU acceleration, or runtime save/restore capability is established merely by a specification.

The last verified repository inspection on 2026-11-10 found nine non-main branch references in addition to main. They are legacy leftovers and must not be used. The connected GitHub integration did not expose a branch-deletion action at that inspection; verify available capabilities before attempting cleanup. No ruleset or branch-protection configuration is required by the owner.

## Session procedure

1. Retrieve live repository metadata, default branch, main HEAD, recursive tree, open PRs/issues, workflow runs, and relevant CI status.
2. Read this file and the mandatory documents above from GitHub.
3. Inspect relevant implementation, interfaces, dependencies, tests, and history before editing.
4. Make changes directly on main; never create or use another branch.
5. Run relevant verification and report exact commands/results, failures, timeouts, and unrun checks.
6. Update canonical documentation, current status, and handoff.
7. Verify every GitHub operation and disclose capability limits.
8. End with changed paths, commit references, verification results, unresolved limitations, and the next concrete action.

## Implementation starting point

The preparation baseline is sufficient to begin the first Rust CPU implementation vertical slice. Establish a minimal Rust workspace and select module boundaries from real ownership/data flow. Define typed time/state/error/resource contracts, implement a causally testable CPU mechanism, and add numerical and behavioral tests. Add persistence and Rust-native concurrency as explicit tested capabilities. Bring in only the scientific evidence required for each mechanism, with provenance and validation limits.