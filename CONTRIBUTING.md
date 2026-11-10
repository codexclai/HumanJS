# Contributing to HumanJS

HumanJS is an early-stage public scientific-software project. Contributions should improve genuine, testable capability and scientific defensibility.

## Before proposing a change

- Read docs/BOOT.md, docs/PROJECT-INSTRUCTIONS.md, docs/OWNER-REQUIREMENTS.md, and the architecture documents relevant to the change.
- Open or review an issue for substantial design changes so requirements and alternatives are recorded.
- Use only the approved active technologies: Rust, WGSL, Python, C, and C++.
- Do not add Node.js, JavaScript, TypeScript, npm, package.json, or JavaScript runtime dependencies.

## Code and science expectations

- Implement actual integrated behavior; do not submit disconnected placeholders or claim biological mechanisms through naming alone.
- Cite primary research where practical. Distinguish human from animal evidence and measured facts from estimates, model conventions, or hypotheses.
- State units, assumptions, parameter sources, limitations, and validation boundaries.
- Include tests for behavior, errors, persistence, resource safety, concurrency, and cross-language boundaries as relevant.
- Report exact test commands and results. Do not hide failing tests or claim unrun tests passed.
- Keep CPU behavior correct. GPU changes require device-backed correctness and measured performance before acceleration claims.

## Pull requests

- Keep changes focused and reviewable.
- Explain purpose, design, alternatives, risks, and owner requirements affected.
- Link relevant issues, decisions, research, and experiments.
- Update relevant docs and current status in the same change.
- Describe tests run, tests not run, and known limitations.
- Exclude secrets, personal data, unlicensed datasets, temporary build output, caches, and unexplained backups.

## Licensing and authorship

The project is licensed under Apache-2.0. Contributors retain copyright to their own original contributions and, by submitting work for inclusion, contribute under the repository license terms. Preserve existing copyright, license, patent, and attribution notices. No separate Contributor License Agreement is currently specified.