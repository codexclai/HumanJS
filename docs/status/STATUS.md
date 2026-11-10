# HumanJS — current status

**As of:** 2026-11-10  
**Stage:** GitHub-first project foundation complete; ready to begin the first Rust CPU implementation slice. Owner has adopted a permanent main-only workflow; no branch-governance settings are required.

## Verified GitHub baseline

- Repository: `codexclai/HumanJS`.
- Visibility: public. Default branch: `main`.
- Preparation PR #8 was merged as `41fac9518a37f39d0f8aba8ddbe27cf5db14d03f`.
- The post-merge repository-policy workflow passed: run `42811770679`.
- Retrieve live `main` HEAD and current workflow status each session; this document is a checkpoint, not a substitute for querying GitHub.
- Preparation PRs #7 and #8 and Dependabot PR #2 are merged. No open pull requests were reported in the latest check.
- `.github/workflows/repository-policy.yml` runs on push, pull request, and manual dispatch. It grants read-only `contents` permission, pins `actions/checkout` by full commit SHA, and invokes the Python repository-policy validator.
- `.github/dependabot.yml` checks GitHub Actions dependencies weekly.
- The repository has documentation/governance, owner-input provenance, and repository automation; it does not yet contain the active simulation implementation.

## Completed preparation

- GitHub is the canonical project source of truth. No ZIP archive is required for active work, synchronization, or delivery.
- The short project instructions and mandatory boot sequence are in the repository.
- The complete original owner prompt is preserved verbatim in `archive/owner-inputs/`; current accepted requirements are consolidated in `docs/OWNER-REQUIREMENTS.md`.
- The target system architecture and stack boundaries are documented.
- The stack-independent whole-brain scope catalogue and validation ladder are documented in `docs/spec/BRAIN-SCOPE-AND-COMPLETENESS.md`.
- Accepted decisions, repository layout, archive/trash policy, roadmap, status, and continuity process are documented.
- Apache-2.0 licensing and the owner attribution notice are in the proper root files.
- Contribution guidance, security reporting guidance, PR template, Dependabot configuration, ignore/attribute rules, and the repository-policy workflow are present.
- The repository-policy workflow passed on the merged preparation PRs and on the post-merge main push. This validates repository policy only; it is not a Rust build, simulation test, or biological validation.

## Implementation state — not yet started

The new GitHub repository does not yet contain:
- A Rust workspace or executable brain/simulation mechanism.
- A Python developer package or its tests.
- A stable C ABI or C++ wrapper.
- An integrated WGSL GPU execution backend.
- Executable JSON brain/model/IR definitions.
- Runtime save/restore, native worker execution, or simulation integration tests.

The owner-required configurable default of 10,000 spiking neuron units, save/restore, and Rust-native multi-threaded execution remain requirements, not implemented capabilities. CPU execution is the first implementation target. GPU support is an objective and must not be claimed until implemented and measured on actual supported hardware.

## Legacy and research disposition

The source-of-truth transition is complete: current owner intent and the accepted target architecture are recorded in GitHub. The former Node.js/JavaScript runtime, package layout, and `.ajs` implementation are retired and must not be line-by-line ported. The old project snapshot receipt is retained only as provenance; no replacement archive is required.

The former project contained additional historical research notes, architecture documents, experiment scripts, result JSON, and old runtime test records. These have not been bulk-copied into active paths. That is intentional: old software results are not biological validation, and every research item must be screened for source provenance, species/method, relevance, and redistribution rights before promotion. Migrate a specific record when it supports a current design or reproducible experiment; do not make wholesale historical copying a prerequisite to starting the new implementation.

## Current branch and delivery policy

The owner now requires main to be the only branch used, permanently. No new or existing non-main branch may be used. The intended final repository state is main alone. The last verified branch listing (2026-11-10) contained nine non-main refs in addition to main. Inspect their unique commits before deleting them when branch deletion is available. The connected GitHub integration did not expose a branch-deletion operation at the last check; do not claim those refs have been removed. No rulesets, branch protection, or deletion-prevention settings are required.

No HumanJSProject.zip is required, maintained, or delivered. ChatGPT Project Sources may remain empty. GitHub Releases, Packages, and Deployments are optional and should be used only for actual distribution or hosted-service needs.

HumanJS has no requirement to store credentials, private user data, or secrets. Do not introduce authentication/secret-management features or generic .env/.env.example/dotenv infrastructure without an approved product requirement.

## Next implementation milestone

Start a minimal Rust workspace with one end-to-end, CPU-only simulation vertical slice. Select module boundaries from real ownership and data-flow requirements, not arbitrary brain-region crates. Define typed time/state/error/resource contracts, write numerical unit tests, and make the first integrated mechanism causally testable. Add persistence and native concurrency as explicit, tested capabilities rather than placeholders. Bring in only the scientific evidence required for the first mechanism and record its provenance.
