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
12. Read research, experiment, API, implementation, and issue records relevant to the task.

## Current authoritative decisions

- Project name: HumanJS; lowercase identifier: humanjs; short identifier: ajs.
- Owner preferred name: Thamindu. The current GitHub login is transitional and may change.
- GitHub is the source of truth for current project work. No ZIP archive is a required source, output, or synchronization artifact.
- Repository visibility: public.
- License: Apache-2.0. Public source can be copied and forked under the license; no public-repository setting can make it uncopyable.
- Approved implementation technologies: Rust, WGSL, Python, C, and C++.
- Rust is the native computational core; WGSL is for GPU compute; Python is the primary developer interface; C ABI and C++ provide native interoperability.
- Node.js, JavaScript, TypeScript, npm, and JavaScript runtimes are discontinued. Do not restore them by habit or through legacy architecture.
- The target is a scientifically defensible computational model of the human brain only, not a whole-body simulator or chatbot.
- Preserve save/restore, native multi-threaded execution, and a configurable 10,000-spiking-neuron default. The 10,000 figure is an engineering default, not a biological claim.

## Current repository status

The repository was initially created as a public, empty project and contains its licensing foundation. A new Rust/Python/C/C++/WGSL implementation, full project documentation migration, and selective scientific-record migration remain to be completed. This status is intentionally explicit: do not claim that legacy source files, all experiments, or all research documents are already synchronized.

The uploaded legacy ZIP was inspected as a migration input. Its BOOT instructions describe the superseded Node.js project and are not active instructions. The prior snapshot had 379 files, 45 directories, 378 UTF-8 text files, one gzip historical artifact, and 25,838,671 extracted bytes. The exact snapshot hash and limitations are recorded in operations/LEGACY-SNAPSHOT-RECEIPT.md. Do not use the old ZIP as the active source or produce a replacement ZIP deliverable.

## Session procedure

1. Retrieve the current repository metadata, default branch, latest commit, file tree, open pull requests, issues, workflow runs, and relevant CI status.
2. Read this BOOT file and its linked current documents from GitHub before implementation work.
3. Classify material as active source, reviewed research, experiment, legacy, deferred, backup, or disposable temporary output.
4. Preserve owner decisions. Later explicit owner decisions supersede conflicting historical prompts and legacy documentation.
5. Inspect relevant files, dependencies, interfaces, tests, and historical changes before editing.
6. Make coherent changes, run appropriate verification, and update the canonical documentation and current status.
7. Use GitHub commits, branches, pull requests, issues, Actions, Dependabot, and security features where available. Verify every operation and disclose capability or permission limits.
8. Never silently discard or overwrite useful work. Never claim synchronization, tests, CI, or security settings succeeded unless verified.
9. End with exact changed paths, commit/PR references, verification results, unresolved limitations, and the next concrete action.

## Preparation checkpoint

The immediate task is repository migration and governance: establish canonical docs and security/automation policy, then migrate or selectively preserve valuable legacy research and experiment provenance while keeping the old runtime archived or excluded. Only after that baseline is complete should new implementation work begin from the target architecture. Do not port the old JavaScript implementation line-by-line.