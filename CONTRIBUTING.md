# Contributing to HumanJS

HumanJS is an early-stage public scientific-software project. Contributions should improve genuine, testable capability and scientific defensibility.

## Before proposing a change

- Read `docs/BOOT.md`, `docs/PROJECT-INSTRUCTIONS.md`, `docs/OWNER-REQUIREMENTS.md`, and the architecture/specification documents relevant to the change.
- Open or review a GitHub issue for substantial design changes so requirements, evidence, and alternatives are recorded before implementation.
- Use only the approved active technologies: Rust, WGSL, Python, C, and C++.
- Keep all maintainer project work on `main`; do not create or use repository branches or pull requests. The owner integrates accepted changes directly on `main`.

## Code and science expectations

- Implement actual integrated behavior; do not submit disconnected placeholders or claim biological mechanisms through naming alone.
- Cite primary research where practical. Distinguish human from animal evidence and measured facts from estimates, model conventions, or hypotheses.
- State units, assumptions, parameter sources, limitations, and validation boundaries.
- Include tests for behavior, errors, persistence, resource safety, concurrency, and cross-language boundaries as relevant.
- Report exact test commands and results. Do not hide failing tests or claim unrun tests passed.
- Keep CPU behavior correct. GPU changes require device-backed correctness and measured performance before acceleration claims.

## Repository hygiene

- Keep commits focused and descriptive.
- Update relevant docs and current status in the same change.
- Exclude secrets, private data, unlicensed datasets, temporary build output, caches, duplicate snapshots, and unexplained backups.
- Do not add automation that creates update branches or pull requests.

## Licensing and authorship

The project is licensed under Apache-2.0. Contributors retain copyright to their own original contributions, which are distributed under the repository license terms. Preserve existing copyright, license, patent, and attribution notices. No separate Contributor License Agreement is currently specified.