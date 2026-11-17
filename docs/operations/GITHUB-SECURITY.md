# GitHub repository operations

**Canonical repository:** `codexclai/HumanJS`  
**Canonical branch:** `main`  
**Last inspected:** 2026-11-18

## Permanent main-only policy

`main` is the only branch permitted for project work, permanently.

- Never create, check out, update, merge, or otherwise use another repository branch, whether new or existing.
- Every authorized change must be committed directly to `main` **and pushed** to the canonical GitHub remote in the same task. Do not leave completed changes unpushed. Verify the live `refs/heads/main` SHA equals the new commit SHA after each push.
- Do not create project pull requests or enable automation that creates non-main update branches.
- Do not require or configure rulesets, branch-protection rules, deletion-prevention rules, or other branch governance settings.
- Force pushes are permitted but exceptional. Inspect the exact target and impact, document the reason, use an expected-head/lease check, and verify the result.

## Verified branch state

The live GitHub branch listing on 2026-11-18 returned exactly one branch (main); no non-main refs were present. Live HEAD at verification was f34fe03ebff65a7a35f0c52eb856f6f5ec7adabd, with a complete 127-entry recursive tree (truncated=false), zero open issues and zero open PRs. Exact-head workflow 43941574837 passed all 37 steps with no failures or skips. The new research/documentation update corrects the Wilbers K evidence inventory: data_fig4.xlsx supplies processed per-recording human fit data; raw K-current NWB sweeps and the separate group-mean K tau CSVs remain absent.

## Repository and delivery

GitHub `main` is the sole source of truth for code, docs, requirements, decisions, research, experiments, issues, workflows, and history. The ChatGPT Project Sources area may remain empty. Do not rely on uploaded files or a separately synchronized project archive.

Use Releases for intentional versioned distributions, Packages for actual distributable packages, and Deployments only when a real hosted service exists. These features are optional and do not replace the repository.

## Project configuration boundary

HumanJS has no requirement to store credentials, private user data, or secrets. Do not add authentication, secret storage, environment files, dotenv, or generic secret/configuration infrastructure without a specific approved product requirement.

## General repository hygiene

Keep workflow permissions minimal and pin third-party actions to reviewed immutable SHAs. Do not add automation that creates branches. Verify commits and workflow runs before reporting success. Public repository content is public under its license; do not add material that the project has no reason or right to publish.
