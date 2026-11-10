# GitHub security and repository protection

**Repository visibility:** public.  
**Purpose:** protect account ownership, canonical history, contribution workflow, and secrets without pretending public code can be hidden.

## Public-repository limitation

Every committed file, commit, tag, release asset, issue, and archive in a public repository is publicly accessible. Public source can be cloned and forked under the license terms. No repository rule or license can make a public repository uncopyable.

The realistic protection goal is to secure the owner account, prevent unauthorized changes to `main`, detect accidental secret publication, review contributions, preserve attribution, and maintain recoverable history.

## Account controls

- Enable two-factor authentication or passkeys on the GitHub account.
- Store recovery codes securely outside the repository.
- Protect the primary email account and use unique credentials.
- Review authorized OAuth apps, GitHub Apps, deploy keys, SSH keys, and active sessions periodically.
- Use least-privilege tokens. Never paste tokens, private keys, recovery codes, or passwords into chat, issues, commits, or workflows.
- Revoke credentials immediately if exposed. Removing a secret from the latest commit does not remove it from Git history or public clones; rotate the credential first.

## Main branch ruleset — owner action required

**Observed on 2026-11-10:** the repository branch listing reported `main.protected = false`; the repository rulesets endpoint returned an empty list. The connected GitHub integration has no repository-settings or branch-protection write operation. A branch-protection read request was denied to the integration. Do not say protection is enabled until the owner applies the ruleset and verifies it in GitHub.

In the repository web UI:

1. Open **Settings → Rules → Rulesets → New ruleset → New branch ruleset**.
2. Name it `Protect main`, set enforcement to **Active**, and target the branch `main`.
3. Require a pull request before merging.
4. Require the status check named `policy` (the job ID in `.github/workflows/repository-policy.yml`). Re-check this exact name in the ruleset picker.
5. Require all review conversations to be resolved.
6. Block force pushes and branch deletion. Require linear history if using squash merges as the normal merge method.
7. Do not set a required approval count that makes a solo-owner repository impossible to merge. Add an approval requirement only after a separate trusted reviewer is available.
8. Keep the bypass list empty unless the owner consciously chooses a documented emergency bypass. A pull request can still be authored and merged by the owner without a second reviewer when no approval count is required.

After saving, reload Settings → Rulesets and verify the ruleset is Active, targets `main`, and contains the expected rules. Also verify the main branch is reported as protected. Record the verification date in `docs/status/STATUS.md`.

## Repository security features

Open **Settings → Code security and analysis** and enable/verify, where available:
- Dependabot alerts.
- Dependabot security updates (the weekly Actions dependency update configuration is already committed separately).
- Secret scanning and push protection.
- Private vulnerability reporting.
- Code scanning/CodeQL when supported source languages are present and the workflow is configured.

The connected integration could not verify the settings endpoint. This document is configuration guidance, not evidence that these features are active. After enabling them, verify each control in the GitHub UI and update `docs/status/STATUS.md`.

## Actions controls

- Workflow permissions are read-only by default; the current policy workflow grants only `contents: read`.
- Third-party actions are pinned to reviewed full commit SHAs. Dependabot PR #2 updated `actions/checkout` to v7.0.1 and was merged after both push and pull-request policy runs passed.
- Grant write permissions only to the specific job that needs them.
- Prefer GitHub-hosted runners for ordinary CI. Do not run untrusted pull-request code on privileged self-hosted runners.
- Keep deployments and releases separate from validation workflows.
- Require successful CI before merging through the `main` ruleset once it is enabled.

## Routine maintenance

- Review repository collaborators and outside collaborators.
- Review installed GitHub Apps, OAuth authorizations, deploy keys, webhooks, secrets, and Actions permissions.
- Review Dependabot PRs; do not auto-merge major action updates without inspecting their diff and required workflow results.
- Keep recovery codes and a separate owner-controlled account recovery method.
- Never store credentials, private user data, or unlicensed third-party content in this public repository, including under `archive/`.

## Status and capability boundary

The repository policy workflow is active and has passed on the current main commit. That is not equivalent to branch protection or secret scanning. Account 2FA/passkey state and Code security and analysis state remain unverified. The connected GitHub integration can read and write repository files and PRs, but it cannot apply repository rulesets or account security settings. Those steps must be completed and verified by the owner in GitHub.
