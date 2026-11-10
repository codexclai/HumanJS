# GitHub repository operations

**Canonical repository:** `codexclai/HumanJS`  
**Canonical branch:** `main`

## Owner's branch policy

`main` is the only branch permitted for all project work, permanently.

- Never create, check out, update, merge, or otherwise use another branch, whether new or existing.
- Commit authorized changes directly to `main`; verify each resulting commit and HEAD.
- The intended final repository state is `main` alone. Existing non-main references are legacy leftovers. Inspect their unique commits before deleting them when branch deletion is supported. If the available integration cannot delete branches, report that limitation and leave them unused.
- Do not require or configure GitHub rulesets, branch-protection rules, deletion-prevention rules, or other branch governance settings.
- Force pushes are permitted but exceptional. Inspect target and impact, explain why necessary, and verify the outcome.

The latest verified inspection on 2026-11-10 found nine non-main branches in addition to main. The connected GitHub integration exposed branch search and ref update but no branch-deletion operation. Do not claim the extra refs have been removed. Recheck current state and capabilities before any cleanup.

## Repository and delivery

GitHub is the sole source of truth for code, docs, requirements, decisions, research, experiments, issues, workflows, and history. No HumanJSProject.zip is required or maintained. ChatGPT Project Sources may remain empty.

Use Releases for intentional versioned source/binary distributions, Packages for actual distributable packages, and Deployments/Environments only when a real hosted service exists. These are optional and do not replace the repository.

## Project configuration boundary

HumanJS has no requirement to store credentials, private user data, or secrets. Do not add authentication, secret storage, `.env`, `.env.example`, `dotenv`, or generic env-file infrastructure without a specific approved product requirement. Do not add generic configuration boilerplate without a demonstrated need.

## General repository hygiene

Keep workflow permissions minimal and review dependency updates. Use GitHub features only when they support an actual project need. Verify commits, workflows, releases, packages, and deployments before reporting success. Public repository content is public under its license; do not add material that the project has no reason or right to publish.