# HumanJS — repository structure

GitHub `main` is the authoritative project record. Create implementation directories only when they have real maintained content; do not add empty scaffolding.

## Current layout

| Path | Purpose | Status |
|---|---|---|
| `README.md` | Public project introduction and boundaries | Active |
| `LICENSE`, `NOTICE` | Apache-2.0 terms and attribution | Active |
| `SECURITY.md`, `CONTRIBUTING.md` | Security reporting and contribution rules | Active |
| `Cargo.toml`, `Cargo.lock` | Rust workspace definition and lockfile | Active |
| `crates/humanjs-core/` | Passive membrane and glutamatergic synapse CPU mechanisms and tests | Active |
| `docs/` | Owner requirements, architecture, specifications, decisions, roadmap, operations, status, current session handoff | Active |
| `research/` | Human passive membrane, glutamatergic synapse, and spike-initiation evidence notes | Active |
| `.github/scripts/` | Maintainer repository-policy validation | Active |
| `.github/workflows/` | Main-branch policy and Rust verification | Active |
| `python/` | Primary Python package and tests | Planned |
| `bindings/c/`, `bindings/cpp/` | C ABI headers, C++ wrappers and tests | Planned |
| `gpu/` | WGSL compute kernels and GPU resources | Planned |
| `models/` | Inspectable brain/model/IR definitions, JSON where appropriate | Planned |
| `experiments/` | Reproducible protocols, stimuli, configurations and results | Planned |
| `tests/` | Cross-layer integration and acceptance tests | Planned |
| `benchmarks/` | Reproducible performance workloads and measurement records | Planned |
| `tools/` | Maintainer tooling that is genuinely needed and maintained | Planned |

## Implementation boundaries

A future Rust workspace may contain focused crates such as core types/time, simulation engine, GPU execution backend, and C ABI. Exact boundaries must follow dependency, ownership, testing, and build requirements. Do not create one crate per brain region or per small file.

The Python distribution should be a normal installable Python package. A Rust-Python extension system is a candidate, subject to dependency review and packaging tests. C/C++ integration is backed by the Rust core. WGSL files are owned by the GPU layer.

## Separation and naming rules

- Current source, documentation, research, and reproducible experiments belong in their canonical paths; do not maintain duplicate project snapshots or general-purpose backup trees.
- Research evidence and reproducible experiment results are distinct from implementation and tests.
- Disposable outputs, build trees, local environments, caches, and scratch data are not tracked.
- Large binary evidence or generated output requires an explicit storage choice and an in-repository provenance record.
- HumanJS is the project name; `humanjs` is the lowercase identifier; `ajs` is the short identifier.
- Use descriptive, stable names and avoid unexplained abbreviations.
- Use `.rs`, `.wgsl`, `.py`, `.c`, `.h`, `.cpp`, and `.hpp` for the approved implementation surfaces.
- Use `.json` for inspectable model/IR data where appropriate.
- Markdown is the default for docs. Maintain one canonical current document per topic and link to it rather than copying it.
- Do not add discontinued runtime files, dependencies, or packaging formats.
