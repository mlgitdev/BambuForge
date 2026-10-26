---
name: bambuforge-repo-sync
description: >-
  Synchronizes agent definitions (AGENTS.md), autonomous skills (.agents/skills/),
  specifications (SDD.md), and tooling from the internal 3D-Automation workspace
  to the public BambuForge GitHub repository. Enforces zero-PII sanitization, version
  bumping, PR generation, and branch protection compliance. Activate whenever
  self-learning-cad logs new rules, when skills or agents are modified, or when
  preparing a public release.
---

# BambuForge Repository Synchronization Skill

This skill synchronizes internal CAD agent improvements, design rules, and skill updates into the public **BambuForge** GitHub repository (`https://github.com/mlgitdev/BambuForge`), while strictly enforcing privacy sanitization and repository governance.

---

## 1. When to Trigger This Skill

Activate this workflow automatically whenever:
1. **Self-Learning CAD Promotion:** The `self-learning-cad` skill updates `AGENTS.md` or design rules (`fdm-design-principles.md`).
2. **Tool / Skill Upgrades:** A script or instruction inside `.agents/skills/` is added, fixed, or enhanced.
3. **Architecture / SDD Updates:** The Spec-Driven Design document or system prompt is revised.
4. **Release Preparation:** Bumping the version (`VERSION`) and packaging release distribution archives (`.zip` and `.tar.gz`).

---

## 2. Synchronization Architecture

```
+---------------------------------------+
|  Internal Workspace: 3D-Automation   |
|  - AGENTS.md                          |
|  - .agents/skills/                    |
|    - 3d-print-modeling/               |
|    - bambu-studio-ai/                 |
|    - self-learning-cad/               |
|    - bambuforge-repo-sync/            |
+---------------------------------------+
                   |
                   | python sync_to_bambuforge.py
                   v
+---------------------------------------+
|  Sanitization & Privacy Audit Filter  |
|  - Replace local user profiles        |
|  - Replace absolute drive paths       |
|  - Audit 0 PII & 0 secrets            |
+---------------------------------------+
                   |
                   v
+---------------------------------------+
|  Public GitHub: BambuForge (main)     |
|  - VERSION, README.md, SDD.md         |
|  - .github/ (workflows, templates)    |
|  - Protected Branch (Only @mlgitdev)  |
+---------------------------------------+
```

---

## 3. Usage & Execution Commands

### Dry-Run Verification (Sanitization & PII Audit Only)
```powershell
python ".agents\skills\bambuforge-repo-sync\scripts\sync_to_bambuforge.py" --dry-run
```

### Full Synchronization with Patch Version Bump
```powershell
python ".agents\skills\bambuforge-repo-sync\scripts\sync_to_bambuforge.py" --bump patch --commit-msg "feat(skills): sync self-learning and cad improvements"
```

### Pull Request & Governance Rules
- All changes submitted to `BambuForge` must target `main` via PR.
- PR titles must follow Conventional Commits (e.g., `feat(cad): ...`, `fix(slicer): ...`).
- Only **`@mlgitdev`** can approve, merge, or force merge (`gh pr merge --admin --squash`).
