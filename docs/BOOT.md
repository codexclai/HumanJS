# HumanJS — session boot

**Updated:** 2026-11-10  
**Canonical source:** this GitHub repository, on its current default branch.

Read this file first whenever a new session begins. Do not assume that prior chat context, an uploaded archive, a local copy, or a remembered commit is current.

## Mandatory reading order

1. This file.
2. PROJECT-INSTRUCTIONS.md.
3. The preserved original owner prompt at archive/owner-inputs/Applys-everything-everywhere-everyway-maximumly-fully-completely.txt is historical input; current owner requirements and explicit later decisions control.
4. OWNER-REQUIREMENTS.md.
5. architecture/SYSTEM-ARCHITECTURE.md.
6. spec/BRAIN-SCOPE-AND-COMPLETENESS.md.
7. REPOSITORY-STRUCTURE.md.
8. policies/ARCHIVE-AND-TRASH.md.
9. decisions/DECISIONS.md.
10. status/STATUS.md.
11. operations/GITHUB-SECURITY.md.
12. Read research, experiment, API, implementation, and issue records relevant to the task when they exist.

## Current authoritative decisions

- Project name: HumanJS; lowercase identifier: humanjs; short identifier: ajs.
- Owner preferred name: Thamindu. The current GitHub login is transitional and may change.
- GitHub is the source of truth for current project work. No ZIP archive is a required source, output, backup, or synchronization artifact.
- Repository visibility: public.
- License: Apache-2.0. Public source can be copied and forked under the license; no public-repository setting can make it uncopyable.
- Approved implementation technologies: Rust, WGSL, Python, C, and C++.
- Rust is the native computational core; WGSL is for GPU compute; Python is the primary developer interface; C ABI and C++ provide native interoperability.
- Node.js, JavaScript, TypeScript, npm, and JavaScript runtimes are discontinued. Do not restore them by habit or through legacy architecture.
- The target is a scientifically defensible computational model of the human brain only, not a whole-body simulator or chatbot.
- Preserve save/restore, native multi-threaded execution, and a configurable 10,000-spiking-neuron default. The 10,000 figure is an engineering default, not a biological claim or hard maximum.

## What "migration complete" means

The current project's authority and accepted direction have moved to GitHub. The canonical owner requirements, original owner prompt, architecture boundaries, whole-brain scope/validation specification, decisions, roadmap, repository policy, and status are maintained here. No archive is needed to keep the active project synchronized.

This does **not** mean every byte of the former Node.js project was copied into the new repository. The old JavaScript runtime and its package layout are intentionally retired, not ported. Historical documentation, research notes, and experiment outputs are not automatically active requirements or validated neuroscience. They are not bulk-imported merely to reproduce the old tree. Revisit a specific historical item only when it is useful to a current mechanism or experiment, and then check provenance, licensing, species/method, and whether it actually supports the proposed claim. The legacy snapshot receipt is provenance only; it does not make an old ZIP a current source or deliverable.

## Current repository status

The GitHub-first governance and specification foundation is established on public repository `codexclai/HumanJS`, default branch `main`. The latest recorded main commit at this update is `2e0078ccaa5df0f10d9f7efc56a8b0e940a8c13f`. The repository-policy workflow passed on the post-merge push for that commit (run `42810467386`). Dependabot's reviewed `actions/checkout` update was merged in PR #2 and is pinned by full commit SHA.

The current tree is a documentation/governance foundation. It contains no Rust simulation core, Python package, C ABI, C++ wrapper, executable model definitions, or integrated WGSL backend. No brain mechanism should be described as implemented merely because it appears in the scope specification. No simulation, biological validation, GPU acceleration, or runtime save/restore capability is currently established by this repository.

The main branch is still reported as unprotected and the repository rulesets endpoint returned no rulesets in the latest repository check. The connected GitHub integration cannot write repository settings. Account controls and Code security and analysis settings also remain unverified. The owner-side steps are recorded in operations/GITHUB-SECURITY.md. Do not describe the public repository as fully hardened until those controls are applied and checked in GitHub.

## Session procedure

1. Retrieve current repository metadata, default branch, latest commit, recursive file tree, open pull requests, issues, workflow runs, and relevant CI status.
2. Read this BOOT file and its linked current documents from GitHub before implementation work.
3. Classify material as active source, reviewed research, experiment, legacy, deferred, backup, or disposable temporary output.
4. Preserve owner decisions. Later explicit owner decisions supersede conflicting historical prompts and legacy documentation.
5. Inspect relevant files, dependencies, interfaces, tests, and historical changes before editing.
6. Make coherent changes, run appropriate verification, and update canonical documentation and current status.
7. Use GitHub commits, branches, pull requests, issues, Actions, Dependabot, and security features where available. Verify every operation and disclose capability or permission limits.
8. Never silently discard or overwrite useful work. Never claim synchronization, tests, CI, or security settings succeeded unless verified.
9. End with exact changed paths, commit/PR references, verification results, unresolved limitations, and the next concrete action.

## Preparation checkpoint

The repository/documentation/CI preparation baseline is complete enough to begin the first Rust implementation vertical slice. Do not delay new implementation merely to copy the old JavaScript tree or bulk-import every historical document. Bring specific scientific evidence and prior experimental records into the active research area when the corresponding mechanism is designed, using traceable sources and explicit validation limits.

Before treating the public repository as hardened for broader collaboration, the owner must apply and verify the main-branch ruleset and the account/repository security controls in operations/GITHUB-SECURITY.md. This owner-side hardening item is distinct from the completed GitHub source-of-truth transition.
