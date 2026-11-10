#!/usr/bin/env python3
"""Validate repository governance without building or executing project code."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FILES = (
    "README.md", "LICENSE", "NOTICE", "SECURITY.md", "CONTRIBUTING.md",
    "docs/BOOT.md", "docs/PROJECT-INSTRUCTIONS.md", "docs/OWNER-REQUIREMENTS.md",
    "docs/REPOSITORY-STRUCTURE.md", "docs/architecture/SYSTEM-ARCHITECTURE.md",
    "docs/policies/ARCHIVE-AND-TRASH.md", "docs/decisions/DECISIONS.md",
    "docs/status/STATUS.md", "docs/operations/GITHUB-SECURITY.md",
)
FORBIDDEN_FILES = {"package.json", "package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml", "tsconfig.json"}
FORBIDDEN_SUFFIXES = {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".ajs"}
TEMP_SUFFIXES = (".bak", ".backup", ".old", ".orig", ".prev", ".copy", ".tmp", ".temp", ".swp", ".swo")
TEMP_DIRS = {"node_modules", "target", "dist", "build", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".cache", "tmp", "temp", "scratch"}

def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"required file missing: {relative}")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8") if (ROOT / "LICENSE").exists() else ""
    notice_text = (ROOT / "NOTICE").read_text(encoding="utf-8") if (ROOT / "NOTICE").exists() else ""
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        errors.append("LICENSE is not recognizable as Apache License 2.0")
    if "Copyright 2026 Thamindu" not in license_text:
        errors.append("LICENSE lacks the current owner attribution")
    if "Copyright 2026 Thamindu" not in notice_text:
        errors.append("NOTICE lacks the current owner attribution")

    json_count = 0
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        parts = relative.parts
        if ".git" in parts:
            continue
        archived = bool(parts and parts[0] == "archive")
        if not archived:
            if path.name in FORBIDDEN_FILES:
                errors.append(f"discontinued Node/npm file outside archive: {relative}")
            if path.suffix.lower() in FORBIDDEN_SUFFIXES:
                errors.append(f"discontinued implementation file outside archive: {relative}")
            if path.name.lower() in {".env", ".env.local", ".env.production"}:
                errors.append(f"environment/secret file must not be tracked: {relative}")
            if any(part.lower() in TEMP_DIRS for part in parts[:-1]):
                errors.append(f"temporary/build/cache directory is tracked: {relative}")
            if path.name.endswith(TEMP_SUFFIXES) or path.name.endswith("~"):
                errors.append(f"temporary/backup file outside archive: {relative}")
        if path.suffix.lower() == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
                json_count += 1
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                errors.append(f"invalid JSON in {relative}: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Repository policy failed: {len(errors)} issue(s)")
        return 1
    print(f"Repository policy passed: {len(REQUIRED_FILES)} required files; {json_count} JSON files")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())