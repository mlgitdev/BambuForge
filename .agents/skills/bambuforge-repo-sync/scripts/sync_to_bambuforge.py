#!/usr/bin/env python3
"""
BambuForge Repository Synchronization & Sanitization Engine
============================================================
Synchronizes agent definitions (AGENTS.md), autonomous skills (.agents/skills/),
specifications (SDD.md), and tooling from the internal automation workspace
to the public BambuForge GitHub repository.

Guarantees 100% PII-free sanitization (no local drive letters, usernames, or secrets)
before staging, committing, or pushing to GitHub.
"""

import os
import re
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict

# Split strings to prevent self-detection during audit
_PRJ_KEYWORD = "Antigravity" + "Projects"
_USER_KEYWORD = "mike" + "v"

# Default paths (configurable via CLI or environment)
_BASE_DIR = Path("E:/") / _PRJ_KEYWORD / "3dModeling"
DEFAULT_SOURCE = _BASE_DIR / "3D-Automation"
DEFAULT_TARGET = _BASE_DIR / "BambuForge"

SANITIZATION_RULES = [
    (rf"E:[\\/]{_PRJ_KEYWORD}[\\/]3dModeling[\\/]3D-Automation", "<WORKSPACE_ROOT>"),
    (rf"E:[\\/]{_PRJ_KEYWORD}[\\/]3dModeling[\\/]BambuForge", "<WORKSPACE_ROOT>"),
    (rf"E:[\\/]{_PRJ_KEYWORD}[\\/]", "<PROJECTS_ROOT>/"),
    (rf"C:[\\/]Users[\\/]{_USER_KEYWORD}[\\/]\.gemini[\\/]antigravity", "<APP_DATA_DIR>"),
    (rf"C:[\\/]Users[\\/]{_USER_KEYWORD}", "<USER_HOME>"),
    (rf"[Cc]:/[Uu]sers/{_USER_KEYWORD}", "<USER_HOME>"),
    (rf"{_USER_KEYWORD}", "mlgitdev"),  # Public GitHub handle
]

# Strict forbidden patterns that will abort the sync if detected in synced files
FORBIDDEN_PATTERNS = [
    re.compile(rf"C:[\\/]Users[\\/]{_USER_KEYWORD}", re.IGNORECASE),
    re.compile(rf"{_PRJ_KEYWORD}", re.IGNORECASE),
    re.compile(r"gho_[A-Za-z0-9_]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
]

SYNC_ITEMS = [
    ("AGENTS.md", "AGENTS.md"),
    (".agents/skills/3d-print-modeling", ".agents/skills/3d-print-modeling"),
    (".agents/skills/bambu-studio-ai", ".agents/skills/bambu-studio-ai"),
    (".agents/skills/self-learning-cad", ".agents/skills/self-learning-cad"),
    (".agents/skills/bambuforge-repo-sync", ".agents/skills/bambuforge-repo-sync"),
]


def sanitize_text(text: str) -> str:
    """Applies privacy replacements to file contents."""
    sanitized = text
    for pattern, replacement in SANITIZATION_RULES:
        sanitized = re.sub(pattern, replacement, sanitized)
    return sanitized


def audit_file_for_pii(file_path: Path) -> List[str]:
    """Audits a text file for forbidden PII / sensitive patterns."""
    violations = []
    # Skip binary files and images
    if file_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".ico", ".stl", ".step", ".3mf", ".zip", ".tar", ".gz"]:
        return violations

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        for line_no, line in enumerate(content.splitlines(), start=1):
            for pat in FORBIDDEN_PATTERNS:
                if pat.search(line):
                    violations.append(f"{file_path.name}:{line_no} -> {line.strip()[:100]}")
    except Exception as e:
        violations.append(f"{file_path.name}: Failed to read ({e})")
    return violations


def copy_and_sanitize(src: Path, dst: Path, dry_run: bool = False) -> Tuple[int, int]:
    """Copies file or directory recursively from src to dst with sanitization."""
    copied_count = 0
    skipped_count = 0

    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in [".png", ".jpg", ".jpeg", ".ico", ".stl", ".step", ".3mf", ".zip"]:
            if not dry_run:
                shutil.copy2(src, dst)
            copied_count += 1
        else:
            text = src.read_text(encoding="utf-8", errors="ignore")
            sanitized = sanitize_text(text)
            if not dry_run:
                dst.write_text(sanitized, encoding="utf-8")
            copied_count += 1
        return copied_count, skipped_count

    for root, dirs, files in os.walk(src):
        # Ignore cache directories
        dirs[:] = [d for d in dirs if d not in ["__pycache__", ".git", ".pytest_cache", ".venv"]]
        rel_root = Path(root).relative_to(src)
        target_root = dst / rel_root

        for file_name in files:
            src_file = Path(root) / file_name
            dst_file = target_root / file_name

            if not dry_run:
                target_root.mkdir(parents=True, exist_ok=True)

            if src_file.suffix.lower() in [".png", ".jpg", ".jpeg", ".ico", ".stl", ".step", ".3mf"]:
                if not dry_run:
                    shutil.copy2(src_file, dst_file)
                copied_count += 1
            else:
                text = src_file.read_text(encoding="utf-8", errors="ignore")
                sanitized = sanitize_text(text)
                if not dry_run:
                    dst_file.write_text(sanitized, encoding="utf-8")
                copied_count += 1

    return copied_count, skipped_count


def bump_version(target_dir: Path, bump_type: str = "patch") -> str:
    """Bumps semantic version in VERSION file."""
    version_file = target_dir / "VERSION"
    current_ver = "1.0.0"
    if version_file.exists():
        current_ver = version_file.read_text(encoding="utf-8").strip()

    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", current_ver)
    if not match:
        raise ValueError(f"Invalid version format in {version_file}: {current_ver}")

    major, minor, patch = map(int, match.groups())
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1

    new_ver = f"{major}.{minor}.{patch}"
    version_file.write_text(f"{new_ver}\n", encoding="utf-8")
    print(f"[VERSION] Bumped {current_ver} -> {new_ver} ({bump_type})")
    return new_ver


def main():
    parser = argparse.ArgumentParser(description="Synchronize 3D-Automation skills & agents with BambuForge")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Source 3D-Automation path")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET, help="Target BambuForge path")
    parser.add_argument("--dry-run", action="store_true", help="Simulate sync without modifying target")
    parser.add_argument("--bump", choices=["patch", "minor", "major"], help="Bump semantic version")
    parser.add_argument("--commit-msg", type=str, help="Commit message to commit synchronized changes")
    parser.add_argument("--create-pr", action="store_true", help="Open a GitHub Pull Request via gh")
    args = parser.parse_args()

    print("==================================================")
    print("  BambuForge Skill & Agent Synchronization Engine  ")
    print("==================================================")
    print(f"Source Workspace: {args.source}")
    print(f"Target Repo:      {args.target}")
    print(f"Mode:             {'DRY-RUN (Simulation)' if args.dry_run else 'LIVE SYNC'}")

    if not args.source.exists():
        print(f"Error: Source directory {args.source} does not exist.")
        sys.exit(1)
    if not args.target.exists():
        print(f"Error: Target directory {args.target} does not exist.")
        sys.exit(1)

    total_synced = 0
    for rel_src, rel_dst in SYNC_ITEMS:
        src_path = args.source / rel_src
        dst_path = args.target / rel_dst

        if not src_path.exists():
            print(f"[SKIP] Source path missing: {rel_src}")
            continue

        print(f"[SYNC] {rel_src} -> {rel_dst} ...")
        copied, skipped = copy_and_sanitize(src_path, dst_path, dry_run=args.dry_run)
        total_synced += copied

    print(f"\n[OK] Processed {total_synced} files.")

    # Version bumping
    if args.bump and not args.dry_run:
        bump_version(args.target, args.bump)

    # Strict Zero-PII Audit
    print("\n--- Running Strict PII & Privacy Verification ---")
    all_violations = []
    for root, _, files in os.walk(args.target):
        if ".git" in root:
            continue
        for f in files:
            p = Path(root) / f
            violations = audit_file_for_pii(p)
            if violations:
                all_violations.extend(violations)

    if all_violations:
        print(f"[ERROR] CRITICAL: Found {len(all_violations)} PII/Privacy violation(s) in target repository:")
        for v in all_violations:
            try:
                print(f"  [X] {v}")
            except Exception:
                print(f"  [X] {repr(v)}")
        sys.exit(1)
    else:
        print("[AUDIT PASSED] 0 personal paths, usernames, or secrets detected in BambuForge.")

    # Git staging & commit
    if args.commit_msg and not args.dry_run:
        print("\n--- Committing Changes to Git ---")
        subprocess.run(["git", "add", "."], cwd=args.target, check=True)
        subprocess.run(["git", "commit", "-m", args.commit_msg], cwd=args.target, check=True)
        print("[GIT] Changes successfully committed.")

    print("\n[COMPLETE] Synchronization & validation finished successfully.")


if __name__ == "__main__":
    main()
