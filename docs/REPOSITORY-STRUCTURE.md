# HumanJS — repository structure

This repository is the authoritative project record. The structure below distinguishes current governance files from future implementation areas. A directory should be created only when it has real maintained content; do not add empty scaffolding.

## Current and planned layout

| Path | Purpose | Status |
|---|---|---|
| README.md | Public project introduction and boundaries | Active |
| LICENSE, NOTICE | Apache-2.0 terms and attribution | Active |
| SECURITY.md, CONTRIBUTING.md | Security reporting and contribution rules | Active |
| docs/ | Owner requirements, architecture, decisions, operations, status, continuity | Active |
| .github/workflows/ | Automated repository policy and future build/test workflows | Active |
| .github/dependabot.yml | GitHub Actions dependency update configuration | Active |
| crates/ | Rust workspace and native simulation crates | Planned |
| python/ | Primary Python package and tests | Planned |
| bindings/c/, bindings/cpp/ | C ABI headers, C++ wrappers and tests | Planned |
| gpu/ | WGSL compute kernels and GPU resources | Planned |
| models/ | Inspectable brain/model/IR definitions, JSON where appropriate | Planned |
| research/ | Curated scientific references, evidence records, parameter provenance | Planned |
| experiments/ | Reproducible protocols, stimuli, configurations and results | Planned |
| tests/ | Cross-layer integration and acceptance tests | Planned |
| benchmarks/ | Reproducible performance workloads and measurement records | Planned |
| tools/ | Maintainer tooling that is genuinely needed and maintained | Planned |
| archive/ | Legacy snapshots, retired material, deferred work, intentional backups | Active policy; populate selectively |

## Implementation boundaries

A future Rust workspace may contain focused crates such as core types/time, simulation engine, GPU execution backend, and C ABI. Exact boundaries must be selected after dependency and ownership analysis. Do not create one crate per brain region or per small file.

The Python distribution should be a normal installable Python package. A Rust-Python extension system is a candidate, subject to an explicit dependency decision and packaging tests. Do not add npm, Node.js, package.json, TypeScript, or JavaScript runtimes.

C/C++ integration is backed by the Rust core. WGSL files are owned by the GPU layer. Model JSON is not executable code and must not be confused with runtime save files.

## Separation rules

- Active code and current, reviewed research are not stored under archive/.
- Research evidence and reproducible experiment results are distinct from implementation and tests.
- Retired code is retained only for provenance or comparison and must not be imported by active build scripts.
- Deferred ideas are preserved with a reason and review trigger, not mixed into the active roadmap.
- Backups and historical snapshots are clearly dated and described.
- Disposable outputs, build trees, local environments, caches, and scratch data are not tracked.
- Large binary evidence or generated output requires an explicit storage choice; use release assets or Git LFS only where justified, with an in-repository provenance record.

## Naming and content conventions

- HumanJS is the product/project name; humanjs is the lowercase identifier; ajs is the short identifier.
- Use descriptive, stable names and avoid unexplained abbreviations.
- Use .rs, .wgsl, .py, .c, .h, .cpp, and .hpp for the approved implementation surfaces.
- Use .json for inspectable model/IR data where appropriate.
- Markdown is the default for docs. Maintain one canonical current document per topic and link to it rather than copying it.
- No active Node.js, JavaScript, TypeScript, npm, or .ajs implementation files.