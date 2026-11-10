# Legacy migration plan

## Goal

Move the useful, permitted knowledge from the former Node.js project into the GitHub-first HumanJS repository without making the old runtime active again or publishing material that is not licensed for redistribution.

## Source classes

1. Owner decisions and requirements: migrate into docs/OWNER-REQUIREMENTS.md and docs/decisions/DECISIONS.md; preserve the verbatim original prompt separately.
2. Science and bibliography: review citations, evidence classes, species, methodology, parameter provenance, and redistribution rights. Promote validated evidence to research/ as curated records.
3. Experiments and results: retain unique, reproducible protocols and raw results with code revision, configuration, seed, environment, and limitations. Label all old results as observations of the former implementation.
4. Architecture and APIs: do not port old Node.js boundaries. Translate still-valid concepts into new Rust/Python/C/WGSL contracts after design review.
5. Implementation source: retire the old JavaScript runtime. Keep only selected code snippets or complete snapshots if useful for provenance, security-reviewed, licensed, and clearly inert.
6. Generated and temporary artifacts: exclude caches, local environments, package outputs, duplicate copies, stale logs, and disposable scratch files unless a unique result is needed to reproduce a finding.

## Review and disposition checklist

For every imported item, record source path, content hash where practical, date/commit, author/provenance, license/rights status, evidence/species/method where scientific, active or archived classification, destination, and reason for retention.

Do not infer redistribution permission merely from having received a file or because the repository is public. Do not import raw third-party papers, datasets, images, or proprietary material without rights. Link to them and record metadata instead.

## Current disposition

The old archive has been inventoried but not fully migrated. The current GitHub repository contains the new governance and architecture foundation, not the previous 379-file implementation and research collection. The old ZIP is no longer the project source of truth or a required output artifact. No replacement ZIP should be generated.

Next, inspect the old research index, primary-source bibliography, full-brain specification, cognitive-mechanism boundary register, known issues, roadmap, handoff, experiment registry, result metadata, and source-material provenance. Then promote only verified and relevant records to the canonical new repository.