# HumanJS — current status

**As of:** 2026-11-10  
**Stage:** repository/governance foundation; new implementation has not started.

## Live repository baseline at preparation start

- Correct connected repository identified: codexclai/HumanJS.
- Repository visibility: public; default branch: main.
- Repository initially contained only LICENSE and NOTICE.
- Apache-2.0 license present; owner attribution is being updated to Thamindu.
- Main branch was observed as unprotected and no repository rulesets were returned.
- Connected GitHub tooling supports repository and Git-object/file reads/writes, but does not expose repository-settings/branch-protection mutation.

## Preparation work

The preparation pass establishes canonical project identity, owner requirements, technology policy, target architecture, documentation entry points, archive separation policy, GitHub security guidance, and bounded repository automation. This documentation is a specification, not an implementation.

## Not yet implemented or migrated

- No Rust workspace or biological simulation implementation has been migrated to this GitHub repository.
- No Python package, C ABI, C++ wrapper, WGSL runtime, executable model JSON definitions, or tests exist here.
- No GPU backend exists or has been measured on real hardware.
- Save/restore and concurrency are requirements, not implemented capabilities in this new repository.
- The legacy ZIP contains 379 files. Its complete source tree and research collection have not yet been bulk-migrated into GitHub. The snapshot hash, inventory, and caveats are documented separately.
- Repository policy workflow results must be observed on GitHub Actions before being reported as passing.
- Branch protection, signed-commit enforcement, push protection, Dependabot alerts, and CodeQL settings require GitHub settings access and verification.

## Immediate next milestone after repository foundation

Review legacy research and experiment evidence, select what is valuable and legally suitable, and migrate its text records into GitHub under canonical research/experiments/archive paths. Then establish a minimal Rust workspace and a tested Python-facing CPU simulation slice. Do not restore the old JavaScript architecture.