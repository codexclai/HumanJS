# HumanJS — repository hygiene policy

**Scope:** the public GitHub working tree, project documentation, source files, research records, experiments, and maintainer automation.

## 1. One current project tree

- GitHub `main` is the sole authoritative working tree.
- Keep the tracked tree focused on current project requirements, architecture, source, verified research, reproducible experiments, tests, and necessary tooling.
- Do not maintain duplicate project snapshots, copied input bundles, old implementation dumps, general-purpose backup directories, or empty placeholder directories.
- Git history is the normal record of project changes. Do not duplicate the repository inside itself.
- Remove confirmed temporary, obsolete, duplicate, generated, and unexplained files after checking references, provenance, licensing, and whether any active workflow depends on them.

## 2. Research and experiment records

- Add research notes only when they support a concrete design, parameter, or validation task.
- Record citations, source version/date, species, method, evidence class, uncertainty, and whether the value is measured, estimated, inferred, hypothesized, or an engineering convention.
- Keep reproducible protocols, configuration, raw results, and interpretation distinguishable under `experiments/`.
- Do not bulk-import unreviewed research, old runtime output, or third-party material. Check relevance, provenance, and redistribution rights before adding it.
- Do not treat software tests or results from an unrelated implementation as biological validation.

## 3. Temporary files, builds, and ignore rules

- Keep build output, caches, virtual environments, scratch files, local logs, and generated intermediates outside the tracked tree.
- `.gitignore` is a convenience, not a security boundary. Review tracked files before committing.
- Keep ignore rules tied to actual project artifacts; do not add generic environment-file patterns or configuration boilerplate without a demonstrated requirement.
- Never commit credentials, secrets, private user data, personal data, malware, or third-party material without redistribution rights.

## 4. Git and automation

- Use only `main`; do not create, check out, update, merge, or use other repository branches.
- Do not create pull requests or enable automation that generates non-main update branches.
- Do not require rulesets, branch protection, or branch-deletion-prevention settings.
- Force pushes are permitted but exceptional. Inspect the exact target and impact, document the reason, use a lease/expected-head check, and verify the result.
- Keep workflow permissions minimal. Pin third-party actions to reviewed immutable commit SHAs.
- Verify automation on the current `main` commit. A repository-policy pass validates only the checks in that workflow; it is not a code build, simulation test, or biological validation.

## 5. Public repository and licensing

All committed repository content is public and clonable under the repository's license. Do not use Git history or public files as a place to conceal or retain secrets, private information, or unlicensed material. Keep owner and third-party attribution notices intact.