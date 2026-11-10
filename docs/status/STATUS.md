# HumanJS — current status

**As of:** 2026-11-10  
**Stage:** GitHub-first project foundation complete; ready to begin the first Rust CPU implementation slice. Branch-deletion prevention is the remaining owner-side repository setting.

## Verified GitHub baseline

- Repository: `codexclai/HumanJS`.
- Visibility: public. Default branch: `main`.
- Latest main commit: `be2dc07d2503f590473757f67526f1024c3322a5`.
- Repository-policy workflow passed on the post-merge push for that commit: run `42810969518`.
- Preparation PR #7 and Dependabot PR #2 are merged. No open pull requests were reported in the latest check.
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

## Owner-side GitHub setting — branch deletion prevention

The latest repository check reported `main` as unprotected and returned an empty repository-rulesets list. The connected integration cannot create repository rulesets. The owner's policy is to **never delete any branch**. Force pushes are permitted and should not be blocked by the ruleset.

The owner must create an active branch ruleset targeting all branches with deletion restriction enabled, and force-push restriction disabled. Leave GitHub's automatic deletion of merged head branches disabled. For `main`, require PRs and the `policy` status check if practical, without requiring a second approval that blocks the solo owner. Exact steps are in `docs/operations/GITHUB-SECURITY.md`.

Code security and analysis features are not required by the owner's current preference. The repository must still never contain secrets, credentials, private data, or unlicensed third-party material. Account 2FA/passkey state remains unverified and should be maintained independently.

## Next implementation milestone

Start a minimal Rust workspace with one end-to-end, CPU-only simulation vertical slice. Select module boundaries from real ownership and data-flow requirements, not arbitrary brain-region crates. Define typed time/state/error/resource contracts, write numerical unit tests, and make the first integrated mechanism causally testable. Add persistence and native concurrency as explicit, tested capabilities rather than placeholders. Bring in only the scientific evidence required for the first mechanism and record its provenance.
