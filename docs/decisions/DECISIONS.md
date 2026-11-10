# HumanJS — decision record

**Decision authority:** the project owner, Thamindu.  
**Updated:** 2026-11-10.

This is the canonical record of currently accepted decisions. Later explicit owner decisions may supersede these entries. Historical decisions from the legacy Node.js project are not automatically active.

## ADR-001 — Project identity and scope

**Status:** Accepted · **Date:** 2026-11-10

- Name: HumanJS; lowercase identifier: humanjs; short identifier: ajs.
- Scope: computational human brain only.
- Not a chatbot, external-LLM wrapper, whole-body simulator, or claim of consciousness, sentience, subjective experience, or human equivalence.

## ADR-002 — Replace the Node.js implementation stack

**Status:** Accepted · **Date:** 2026-11-10

Active implementation technologies are Rust, WGSL, Python, C, and C++. Rust is the native core; WGSL is for GPU compute; Python is the primary developer interface; C ABI and C++ provide interoperability. Node.js, JavaScript, TypeScript, npm, package.json distribution, and JS runtimes are discontinued. No compatibility port is required unless the owner explicitly requests one.

## ADR-003 — GitHub is the source of truth

**Status:** Accepted · **Date:** 2026-11-10

The HumanJS GitHub repository, branch main, is the sole canonical source for active code, docs, issues, decisions, research records, experiments, workflows, and history. ChatGPT sessions must refresh from GitHub at session start. No HumanJSProject.zip is required, maintained, or delivered. ChatGPT Project Sources may remain empty. Releases, Packages, and Deployments are optional delivery mechanisms only when an actual product need exists.

## ADR-004 — Public repository and Apache-2.0

**Status:** Accepted · **Date:** 2026-11-10

The repository is public and uses Apache License 2.0. The owner original contributions are attributed to Thamindu. Contributors retain copyright in their own contributions; those contributions are governed by the accepted contribution/license terms. Apache-2.0 permits compliant copying, modification, redistribution, and commercial use. Public source cannot be made uncopyable through repository settings or a license.

## ADR-005 — Preserve useful legacy work, isolate obsolete implementation

**Status:** Accepted · **Date:** 2026-11-10

Historical code, unique experiments, research notes, prompts, and results may be preserved for provenance and future comparison. They must be clearly classified and must not be treated as the active architecture. Old Node.js source is not to be ported line-by-line. Research findings require independent source/provenance review before reuse.

## ADR-006 — Data formats may be redesigned

**Status:** Accepted · **Date:** 2026-11-10

The former Artificial/.ajs and Node-specific persistence/API formats are not binding. Applicable inspectable brain/model/IR data should use .json. Model definitions, initial conditions, live state, learned state, and checkpoints are distinct. Choose runtime persistence representation after correctness, safety, size, inspectability, and performance testing.

## ADR-007 — Retained runtime requirements

**Status:** Accepted · **Date:** 2026-11-10

Save/restore remains required. Native worker/multi-threaded execution remains required and must use Rust-native concurrency, not Node worker_threads. A configurable default of 10,000 spiking neuron units remains required. Rate/mean-field units and state variables are counted separately. The default is an engineering choice, not a biological count or hard maximum.

## ADR-008 — Biological mechanisms, not software stand-ins

**Status:** Accepted · **Date:** 2026-11-10

Cognition and biological function must arise from causal, interacting, appropriately evidenced systems. Do not substitute fact/grammar tables, object-ID registries, goal slots, fixed switching timers, capped sequence tables, global scalar neuromodulators, or simplistic sensory transforms for biological mechanisms. Record uncertainty and evidence provenance.

## ADR-009 — Public-project safety and archival separation

**Status:** Accepted · **Date:** 2026-11-10

Active source, research, experiments, legacy snapshots, retired material, deferred work, backups, and temporary output must be separated. Preserve provenance and avoid unnecessary material. The latest owner decision is to use main only, never create or use other branches, and aim for main as the sole remaining branch; inspect unique commits before deleting existing non-main refs when deletion is available. Do not require rulesets or branch-protection settings. Force pushes are permitted but exceptional and must be inspected and verified.

## ADR-010 — Permanent main-only workflow and GitHub delivery

**Status:** Accepted · **Date:** 2026-11-10

The owner supersedes the earlier branch-preservation policy: main is the only branch to use permanently. Never create or use other branches, including existing non-main refs. The intended repository state is main alone; inspect unique commits before deleting old refs when deletion is available. Do not require or configure rulesets or branch protection. Force pushes remain permitted but exceptional and verified. No HumanJSProject.zip is required or maintained; GitHub Releases, Packages, and Deployments are optional when justified by a real distribution or hosted-service need. ChatGPT Project Sources may remain empty.
