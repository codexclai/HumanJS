# HumanJS — current status

**As of:** 2026-11-10  
**Stage:** GitHub-first governance foundation merged; implementation has not started.

## Verified GitHub baseline

- Correct connected repository: codexclai/HumanJS.
- Public repository; default branch: main.
- Repository initially contained only LICENSE and NOTICE.
- LICENSE and NOTICE now attribute the owner original contributions to Thamindu.
- Main was observed as unprotected; no repository rulesets were returned.
- The connected GitHub integration exposes repository and Git-object/file reads and writes, but does not expose repository-settings or branch-protection mutation.

## Completed in the governance foundation

Pull request #1 established the initial GitHub-first foundation (22 files, 850 lines). Pull request #3 preserved the original owner prompt and added the migration plan and roadmap. Pull request #4 corrected the status and attribution record. Pull request #5 added the stack-independent whole-brain scope catalogue and validation ladder. All four pull requests were merged into main on 2026-11-10. The resulting foundation includes:

- Canonical README and /docs/BOOT.md.
- Short Project Instructions.
- Consolidated owner requirements and target architecture.
- Repository structure and archive/trash policy.
- Decision record and current status.
- GitHub security, contribution, and vulnerability guidance.
- GitHub Actions repository-policy workflow and its Python validator.
- Dependabot configuration for GitHub Actions updates.
- .gitignore and .gitattributes.
- Current personal copyright attribution to Thamindu.

The Repository policy workflow passed on the pull requests and on the post-merge main push. The latest verified main push is run 17, ID 42785862936, conclusion success. This verifies only the repository-governance checks in that workflow. It is not a software build, simulation test, or biological validation.

## Not yet implemented or migrated

- No Rust workspace or biological simulation implementation has been migrated to this GitHub repository.
- No Python package, C ABI, C++ wrapper, WGSL runtime, executable model JSON definitions, or biological simulation tests exist here.
- No GPU backend exists or has been measured on real hardware.
- Save/restore and native concurrency remain owner requirements, not implemented capabilities in the new repository.
- The legacy snapshot contains 379 files, including 315 documentation files and a large research/experiment record. The complete source tree and research collection have not been bulk-migrated into GitHub. The hash, inventory, and scope are documented in operations/LEGACY-SNAPSHOT-RECEIPT.md.
- The verbatim owner prompt is preserved in archive/owner-inputs/Applys-everything-everywhere-everyway-maximumly-fully-completely.txt. Its SHA-256 is documented in archive/owner-inputs/README.md. It is historical provenance, not a second active instruction source.
- The stack-independent whole-brain catalogue and validation ladder are in docs/spec/BRAIN-SCOPE-AND-COMPLETENESS.md.
- Repository policy workflow passed both the PR-triggered checks and the post-merge main-branch push run (run ID 42784823933, conclusion success).
- Branch protection, signed-commit enforcement, push protection, Dependabot alerts, and CodeQL settings still require GitHub settings access and verification.

## Immediate next milestone

Finish review and migration of valuable legacy research and experiment evidence. Decide which legacy artifacts are historically useful, scientifically relevant, legally redistributable, or disposable. Keep retired Node.js code out of active paths. Then establish a minimal Rust workspace and one tested Python-facing CPU simulation vertical slice. Do not restore the old JavaScript architecture.
