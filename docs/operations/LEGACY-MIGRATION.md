# Legacy material disposition and selective migration policy

## Purpose

The active project has moved to GitHub. This record explains how the former Node.js-era material was evaluated conceptually and how any individually useful historical material may be reused without reviving the retired software architecture.

## What is migrated into the current project

The current accepted project definition and owner direction are maintained in GitHub:
- The verbatim owner prompt is preserved in `archive/owner-inputs/`.
- Current owner requirements and later clarifications are consolidated in `docs/OWNER-REQUIREMENTS.md`.
- Current architecture boundaries are in `docs/architecture/SYSTEM-ARCHITECTURE.md`.
- The stack-independent whole-brain target and validation ladder are in `docs/spec/BRAIN-SCOPE-AND-COMPLETENESS.md`.
- Current decisions, roadmap, status, repository policy, and session handoff instructions are in their canonical `docs/` locations.

That is the migration needed to establish GitHub as the authoritative project record. No HumanJSProject ZIP or other archive is required to use, synchronize, or deliver the current project.

## What is intentionally not carried forward

- The former Node.js/JavaScript/TypeScript/npm implementation and package layout are retired. Do not port them line-by-line or reactivate their dependencies.
- The old `Artificial/.ajs` model-definition layout is not binding. Current inspectable brain/model/IR definitions should use JSON where appropriate.
- The old runtime's tests, benchmarks, and experimental outputs establish only what that former software did under its recorded conditions. They do not establish biological validity or capability in the new architecture.
- Historical documentation and research outputs are not copied wholesale into active documentation. Relevance and evidence quality must be assessed at the point of reuse.
- Duplicate prompts, stale handoffs, generated artifacts, caches, and temporary output are not copied merely to recreate the historic archive's file count.

## How to promote an individual historical item

Before copying a prior research note, experiment, result, data file, source excerpt, or code fragment into the active repository, record:
1. Its original path and known date/revision.
2. Its author/provenance and content hash where useful.
3. Whether it contains third-party text, figures, datasets, or code, and whether redistribution is permitted.
4. For science: species, sample, preparation, method, evidence class, uncertainty, and whether the cited source supports the claim.
5. Whether it is a measured result, model output, engineering convention, hypothesis, or unvalidated interpretation.
6. Its new canonical destination, validation status, and reason for retention.

Research records should go to `research/`; reproducible protocols and generated results should go to `experiments/`. Keep raw results distinct from interpretation. Mark results from the retired implementation as historical/legacy. Do not move them into active tests or use them as evidence that the new runtime passes.

## Current disposition

- GitHub is the only current source of truth.
- No ZIP archive is a required synchronization file, source, release, or deliverable.
- The legacy snapshot receipt is a provenance note, not a dependency.
- The former implementation is retired rather than migrated as active software.
- The current project definition and accepted requirements are in the repository.
- Further research/experiment migration is selective and task-driven, not a blocker to the new Rust implementation.

Do not claim that every historical byte from the former project was copied. Do not request or regenerate a replacement archive. The current project's migration is complete at the level of active authority and accepted direction; historical implementation artifacts remain intentionally non-active.
