# GitHub repository operations

**Canonical repository:** `codexclai/HumanJS`  
**Canonical branch:** `main`  
**Last inspected:** 2026-11-10

## Permanent main-only policy

`main` is the only branch permitted for project work, permanently.

- Never create, check out, update, merge, or otherwise use another repository branch, whether new or existing.
- Commit authorized maintainer work directly to `main`; verify every resulting commit and remote HEAD.
- Do not create project pull requests or enable automation that creates non-main update branches.
- Existing non-main refs are unused leftovers. Inspect their unique commits before deletion; never use them for implementation.
- Do not require or configure rulesets, branch-protection rules, deletion-prevention rules, or other branch governance settings.
- Force pushes are permitted but exceptional. Inspect the exact target and impact, document the reason, use an expected-head/lease check, and verify the result.

## Current branch cleanup limitation

The live inspection found nine non-main refs in addition to `main`. GitHub comparisons showed one unique commit on each non-main ref and that each ref is 8–16 commits behind `main`. They are not used. The GitHub tools available during this inspection expose branch search/comparison and ref updates, but not branch deletion; no authenticated browser session was available to delete them. Do not claim the repository physically contains only `main` until a fresh branch listing verifies that state. Recheck deletion capability in a future session.

## Repository and delivery

GitHub `main` is the sole source of truth for code, docs, requirements, decisions, research, experiments, issues, workflows, and history. The ChatGPT Project Sources area may remain empty. Do not rely on uploaded files or a separately synchronized project archive.

Use Releases for intentional versioned distributions, Packages for actual distributable packages, and Deployments only when a real hosted service exists. These features are optional and do not replace the repository.

## Project configuration boundary

HumanJS has no requirement to store credentials, private user data, or secrets. Do not add authentication, secret storage, environment files, dotenv, or generic secret/configuration infrastructure without a specific approved product requirement.

## General repository hygiene

Keep workflow permissions minimal and pin third-party actions to reviewed immutable SHAs. Do not add automation that creates branches. Verify commits and workflow runs before reporting success. Public repository content is public under its license; do not add material that the project has no reason or right to publish.