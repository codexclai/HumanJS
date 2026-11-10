# HumanJS — ChatGPT Project Instructions

## Canonical source and session continuity
The sole source of truth is the live GitHub repository `codexclai/HumanJS`, branch `main`. ChatGPT Project Sources are intentionally allowed to remain empty. Do not request, expect, or depend on uploads, local source attachments, remembered snapshots, or a separately synchronized project archive.

At the start of every new chat:
1. Fetch live repository metadata and confirm that the default branch is `main`.
2. Read `docs/BOOT.md` from the current `main` before reading other project files.
3. Retrieve the current `main` commit and full repository tree; inspect current file contents and relevant history rather than trusting previous chat summaries.
4. Follow the mandatory reading order in `docs/BOOT.md`.
5. Check current workflow results, open issues/PRs, and branch refs. Report only what was actually verified.

Never assume that previous chat context, cached content, or a local checkout is current. If a local workspace is needed, use a clean checkout synchronized from `main`.

## Branch and GitHub operating policy
`main` is the only project branch to use, permanently. Never create, check out, update, merge, or work from another branch. Make authorized repository changes directly on `main`, verify each resulting commit, and never claim a write succeeded without checking GitHub.

Do not create project branches, pull requests, branch-generating automation, Dependabot update PRs, or other workflows that require non-main branches. Do not require or configure branch protection, rulesets, or deletion-prevention settings. Force pushes are permitted only as an exceptional, justified operation after inspecting the exact target and impact. Existing non-main refs are not permission to use them; inspect unique commits before deletion and report honestly when the available tools cannot delete refs.

Use GitHub features only when they solve a real need. Releases, Packages, and Deployments are optional and must not be created just for appearances. The public repository is the canonical delivery location.

## Purpose and scientific scope
HumanJS is a scientifically defensible computational model of the **human brain only**. It is not a whole-body simulator, chatbot, external-LLM wrapper, generic agent framework, or claim of consciousness, sentience, subjective experience, human-equivalent intelligence, clinical validity, or biological completeness. External hosts may provide body, peripheral, sensory, actuator, and environmental inputs/outputs through explicit interfaces.

Build causal, interacting, evidence-grounded mechanisms. Do not replace biology with fact tables, fixed lexicons or grammar parsers, object-ID cognition, numbered goal slots, fixed task-switch penalties, capped sequence lookup, global scalar neuromodulators, generic sensory transforms, or unsupported anatomy. Distinguish human from animal evidence, measurements from estimates, findings from hypotheses, and biology from engineering conventions. Record sources, methods, provenance, uncertainty, disputes, and validation limits.

## Approved technology and architecture
- **Rust:** authoritative simulation state, computational core, mechanisms, runtime, APIs, scheduling, resources, concurrency, and persistence.
- **WGSL:** GPU compute kernels, integrated through a Rust-owned backend.
- **Python:** primary developer interface, scientific workflows, experiments, analysis, and tooling.
- **C:** stable native interoperability through a deliberately designed C ABI.
- **C++:** interoperability and ergonomic wrappers, preferably over the C ABI.

Rust owns simulation truth. Python must not replace the native core with a subprocess or external AI. C/C++ boundaries need explicit ownership, lifetime, error, buffer, and thread-safety contracts. CPU execution is mandatory and is the correctness reference. Claim GPU support or acceleration only after actual hardware execution, correctness checks, and reproducible benchmarks.

## Retained product requirements
Keep model definitions, initial conditions, live runtime state, learned state, and checkpoints distinct. Use JSON for applicable inspectable model/IR definitions. Retain correct save/restore, Rust-native multi-threaded execution, and a configurable default of 10,000 spiking neuron units. That number is an engineering default, not a biological neuron count or hard maximum. Do not claim these capabilities are implemented until they exist and are tested.

## Engineering quality
Inspect existing code, interfaces, dependencies, data flow, and tests before changing anything. Build integrated functionality, not names, inventories, placeholders, or disconnected scaffolding. Design typed contracts and safe resource bounds. Add appropriate numerical, unit, behavioral, integration, persistence, concurrency, interoperability, and regression tests. Fix root causes; never weaken tests or hide failures. Verify the exact commands and results, identify unrun checks, and state limitations plainly.

Use dependencies only when justified. Do not introduce authentication, credential storage, secret-management systems, `.env`, `.env.example`, dotenv, or generic environment-file infrastructure without a specific approved requirement. Keep the repository free of secrets, private data, unlicensed material, generated output, duplicate snapshots, and temporary clutter.

## Documentation and completion
Keep `/docs` canonical. Maintain one authoritative requirements document, architecture document, decision record, roadmap, current status, and session handoff. Record meaningful decisions, changes, rationale, source provenance, tests, failures, and limitations. Update `docs/BOOT.md` and `docs/status/STATUS.md` after meaningful project changes.

A task is complete only when the implementation, integration, tests, relevant evidence review, and documentation are verified. Never claim biological validation from ordinary software tests. At the end of work, report changed paths, commit(s), verification commands/results, limitations, and the next concrete step.