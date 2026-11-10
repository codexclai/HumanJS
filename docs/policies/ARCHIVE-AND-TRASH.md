# Archive, deferred work, backups, and temporary material

**Purpose:** preserve useful history without allowing obsolete or disposable material to contaminate the active project.

## 1. Classification

| Class | Meaning | Location |
|---|---|---|
| Active | Maintained code, current architecture, accepted requirements, reviewed research, reproducible tests | Normal project paths |
| Research archive | Unique papers, evidence notes, completed experiment protocols/results with provenance | research/ or experiments/ |
| Legacy | Superseded source, old APIs, obsolete architecture, historical snapshots | archive/legacy/ |
| Retired | Removed or rejected design kept for regression comparison or provenance | archive/retired/ |
| Deferred/useful later | Potentially useful but not currently accepted or scheduled | archive/deferred/ |
| Backup | Intentional recovery copy with a clear date, scope, and reason | archive/backups/ |
| Temporary | Build output, caches, scratch experiments, local logs, generated intermediates | Outside Git; ignored |
| Trash | Material confirmed unnecessary and safe to remove | Delete after review; do not keep mixed with active files |

## 2. Archive entry requirements

Every substantial archival addition must state original path/source, date or known time range, reason it is no longer active, classification, generated/third-party/sensitive-content review, retrieval/comparison purpose, and any integrity/provenance identifier.

Legacy code must be clearly marked non-active and must not be imported, built, tested as current behavior, or included in active packages by default. Research that remains relevant should be reviewed and promoted to the canonical research area with evidence provenance.

## 3. Backups and Git history

Git history is the ordinary record of source changes; do not create backup copies of every file or duplicate whole repositories in active paths. A backup is appropriate only for a distinct recovery purpose, must be dated and explained, and must not be mistaken for current source.

Prefer commits, tags, and well-described archive locations over ad hoc folders named old, backup, copy, final-final, or temp. **Never delete a Git branch.** Force pushes are permitted by owner preference, but only when intentional and after checking the target and impact; do not use them casually. Never rewrite published history merely to tidy it.

## 4. Trash and retired material

Material that is genuinely unnecessary may be removed after checking references, uniqueness, provenance, licensing, and reproducibility. If retention is useful, place it in archive/retired/ with a reason. Do not leave unexplained trash mixed with active files. Never commit secrets, credentials, personal data, malware, or third-party material without redistribution rights, even into an archive.

## 5. Useful-later work

Ideas or experiments that may be useful later belong in archive/deferred/ or a clearly identified research record. Record the reason for deferral and the condition that would justify reopening them. Do not silently present deferred proposals as accepted architecture.

## 6. Temporary output and ignore rules

Use local temporary locations or ignored directories for builds, test logs, caches, downloaded scratch files, temporary datasets, and generated intermediates. Do not commit temporary files merely because GitHub provides storage. The root `.gitignore` is a convenience for common generated/local files, not a security boundary; inspect it before relying on it and never place secrets in the repository.

## 7. Public repository rule

Anything committed to this public repository must be treated as publicly readable and clonable. An archive folder is not private or protected from copying. Never use Git history or a public archive as a hiding place for secrets, private data, or unlicensed material.

## 8. No ZIP deliverable

GitHub is the canonical project home. Do not recreate or require a HumanJSProject.zip output. If an old ZIP is supplied as a migration input, inspect it, record its provenance, selectively migrate permitted content, and do not treat that ZIP as the ongoing project database.
