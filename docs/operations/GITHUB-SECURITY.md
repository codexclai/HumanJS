# GitHub security and repository protection

**Repository visibility:** public.  
**Owner's current preferences:** force pushes are permitted; branch deletion must never happen. Code security and analysis features are not a preparation requirement.

## Public-repository limitation

Every committed file, commit, tag, release asset, issue, and archive in a public repository is publicly accessible and can be cloned or forked under the license terms. No repository rule can make public source uncopyable.

The practical priorities are to protect account ownership, prevent branch deletion, preserve reviewable changes, and never publish secrets or private data.

## Branch policy — owner action required

**Observed on 2026-11-10:** the repository rulesets endpoint returned no rulesets, and the branch listing reported `main` as unprotected. The connected GitHub integration cannot create or edit repository rulesets.

The owner's explicit policy is:
- **Never delete any branch**, including feature, dependency-update, or historical branches. Do not use GitHub's automatic head-branch deletion after merging.
- **Force pushes are allowed.** Do not configure a rule that blocks force pushes. A force push can still rewrite shared history, so use it only intentionally after checking the target and impact.
- Keep the pull-request and CI workflow on `main` where practical.

In GitHub, open **Settings → Rules → Rulesets** and create an active branch ruleset that targets **all branches** and enables **Restrict deletions** (the deletion-prevention rule). Do not enable the rule that restricts force pushes. Verify the ruleset is Active and targets every branch, not only `main`. If the GitHub UI offers automatic deletion of head branches after PR merge, leave it disabled.

For `main`, retain the normal review/CI workflow if it remains practical:
- Require a pull request before merging.
- Require the `policy` status check from `.github/workflows/repository-policy.yml`.
- Require review conversations to be resolved.
- Do not require an approval count that prevents a solo owner from merging.
- Do not add a force-push restriction.

After saving, reload the ruleset page and verify that deletion restriction is active for all branches and force pushes are not restricted. Record the date and observed result in `docs/status/STATUS.md`.

## Secrets and Code security and analysis

The owner's stated policy is that secrets and credentials must never be stored in this public repository. This is the primary control, not a substitute for good handling:
- Never commit API keys, access tokens, passwords, private keys, recovery codes, session cookies, or private user data.
- Do not put real credentials in examples, test fixtures, logs, issues, pull requests, workflow output, archives, or history.
- Use clearly fake placeholders in examples. If a future workflow genuinely needs a secret, use GitHub Actions secrets or an appropriate external secret manager; never commit it.
- If a credential is exposed, revoke/rotate it immediately. Deleting it from the latest commit does not remove it from history or public clones.

Code security and analysis features (secret scanning, push protection, CodeQL, and similar controls) are **optional and not required to finish preparation** under the owner's current preference. They may be reconsidered if the project begins accepting outside contributions, uses credentials in automation, or gains a larger dependency/build surface. Do not claim they are enabled or required.

Dependabot's weekly GitHub Actions update configuration remains active. Review dependency updates rather than assuming every update is safe.

## Account and Actions hygiene

- Enable account two-factor authentication or passkeys and protect the primary email account.
- Keep recovery codes outside the repository.
- Periodically review collaborators, OAuth/GitHub Apps, deploy keys, SSH keys, webhooks, active sessions, and token permissions.
- Keep workflow permissions minimal. The current repository-policy workflow grants read-only `contents` access and pins third-party actions to full commit SHAs.
- Do not run untrusted pull-request code on privileged self-hosted runners.
- Keep deployments and releases separate from validation workflows.

## Capability boundary

The connected GitHub integration can read and write repository files and manage pull requests, but it cannot apply repository rulesets or account-level settings. The deletion-prevention ruleset and account security must be configured by the owner in GitHub and then verified there. The integration last observed no rulesets and `main` as unprotected on 2026-11-10.
