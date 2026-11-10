# GitHub security and repository protection

**Repository visibility:** public.  
**Purpose:** protect account ownership, canonical history, contribution workflow, and secrets without pretending public code can be hidden.

## Public-repository limitation

Every committed file, commit, tag, release asset, issue, and archive in a public repository is publicly accessible. Public source can be cloned and forked under the license terms. GitHub forking restrictions for individual repositories apply to private repositories; do not expect a public setting to prevent copying.

The realistic protection goal is to secure the owner account, prevent unauthorized changes to main, detect accidental secret publication, review contributions, preserve attribution, and maintain recoverable history.

## Account controls

- Enable two-factor authentication or passkeys on the GitHub account.
- Store recovery codes securely outside the repository.
- Protect the primary email account and use unique credentials.
- Review authorized OAuth apps, GitHub Apps, deploy keys, SSH keys, and active sessions periodically.
- Use least-privilege tokens. Never paste tokens, private keys, recovery codes, or passwords into chat, issues, commits, or workflows.
- Revoke credentials immediately if exposed. Removing a secret from the latest commit does not remove it from Git history or public clones; rotate the credential first.

## Main branch rules

Create a branch protection rule or repository ruleset targeting main:

1. Require pull requests before merging.
2. Require the repository-policy workflow to pass once it is present and working.
3. Require all review conversations to be resolved.
4. Require linear history and use squash merging.
5. Block force pushes and branch deletion.
6. Disable bypass where practical. Keep a documented recovery route for the owner.
7. Require signed commits only after a verified signing setup exists and automation can produce verified signatures.
8. Require at least one approval only when a trusted reviewer is available. A solo owner must not configure a rule that makes merging impossible.
9. Restrict direct pushes to main where practical; feature branches and pull requests are preferred.

Official guidance: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches and https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets.

## Security features to enable/check

In repository Settings → Code security and analysis, check Dependabot alerts, secret scanning, push protection where available, code scanning/CodeQL once supported source code exists, and private vulnerability reporting. Verify actual setting state in GitHub; this document does not enable the settings.

Official guidance: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-security-and-analysis-settings-for-your-repository.

## Actions controls

- Set workflow permissions to read-only by default.
- Grant write permissions only to the specific job that needs them.
- Pin third-party actions to reviewed full commit SHAs and update pins deliberately.
- Prefer GitHub-hosted runners for ordinary CI. Do not run untrusted pull-request code on privileged self-hosted runners.
- Keep deployments and releases separate from validation workflows.
- Require successful CI before merging once branch protection is enabled.

## Observed state and connector limits

At baseline, main was observed as unprotected and the rulesets endpoint returned an empty list. The connected GitHub integration exposed repository and file operations but no repository-settings or branch-protection write action. Therefore the owner must apply and verify the branch and account security settings in the GitHub web UI. Do not mark any control enabled until it is observed in GitHub Settings or an authoritative read API.