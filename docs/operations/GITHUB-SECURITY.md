# GitHub repository operations

**Canonical repository:** `codexclai/HumanJS`  
**Canonical branch:** `main`  
**Last inspected:** 2026-11-15

## Permanent main-only policy

`main` is the only branch permitted for project work, permanently.

- Never create, check out, update, merge, or otherwise use another repository branch, whether new or existing.
- Every authorized change must be committed directly to `main` **and pushed** to the canonical GitHub remote in the same task. Do not leave completed changes unpushed. Verify the live `refs/heads/main` SHA equals the new commit SHA after each push.
- Do not create project pull requests or enable automation that creates non-main update branches.
- Do not require or configure rulesets, branch-protection rules, deletion-prevention rules, or other branch governance settings.
- Force pushes are permitted but exceptional. Inspect the exact target and impact, document the reason, use an expected-head/lease check, and verify the result.

## Verified branch state

The live GitHub branch listing on 2026-11-17 returned exactly one branch: main; no non-main refs were present. At the beginning of this documentation update, main HEAD was c781442b64d275b7d1642220df53936682692da4, its complete recursive tree had 127 entries and was not truncated, and there were zero open issues and PRs. The parent research commit 6c56ebeb55efab15556f3317bd5294bb65e62d14 passed exact-head workflow 43940242441 (37/37 steps). Workflow 43941344405 on c781442 was in progress when this update was prepared. Recheck live refs and exact-head CI at the end of the task.

## Repository and delivery

GitHub `main` is the sole source of truth for code, docs, requirements, decisions, research, experiments, issues, workflows, and history. The ChatGPT Project Sources area may remain empty. Do not rely on uploaded files or a separately synchronized project archive.

Use Releases for intentional versioned distributions, Packages for actual distributable packages, and Deployments only when a real hosted service exists. These features are optional and do not replace the repository.

## Project configuration boundary

HumanJS has no requirement to store credentials, private user data, or secrets. Do not add authentication, secret storage, environment files, dotenv, or generic secret/configuration infrastructure without a specific approved product requirement.

## General repository hygiene

Keep workflow permissions minimal and pin third-party actions to reviewed immutable SHAs. Do not add automation that creates branches. Verify commits and workflow runs before reporting success. Public repository content is public under its license; do not add material that the project has no reason or right to publish.
