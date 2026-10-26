# Contributing to BambuForge

Thank you for your interest in contributing to **BambuForge**! We welcome parametric CAD contributions, slicing profile enhancements, agent skill expansions, and documentation improvements.

---

## 1. Governance & Strict Merge Permissions

- **Branch Protection**: The `main` branch is strictly protected. Direct pushes to `main` are blocked.
- **Single Approver Gatekeeper**: All contributions must be submitted via Pull Requests. Explicit code ownership across all components is governed by [`.github/CODEOWNERS`](.github/CODEOWNERS). Only the repository maintainer (**`@mlgitdev`**) has permission to review, approve, and merge PRs into `main`.
- **Force PR Merge Authority**: Only `@mlgitdev` possesses administrative override / force PR merge authority (`gh pr merge --admin --squash`).
- **Required Automated Checks**:
  1. `PR Validation Bot`: Conventional commit title standard and complete template checklist.
  2. `Secret Scanning & Privacy Audit`: Zero PII (personal file paths or usernames) and zero high-entropy secrets.
  3. `Multi-OS CI`: Python compilation across Ubuntu, Windows, and macOS.
- **Post-Merge Release Automation**: Merges into `main` that bump `VERSION` automatically trigger the release pipeline, packaging `BambuForge-vX.Y.Z.zip` and `.tar.gz` distribution archives.

---

## 2. Issue-First Protocol

Before writing code or parametric geometry, **every contribution must have an active GitHub Issue**:
1. **Search Existing Issues**: Run `gh issue list` or search the repository to confirm your proposal isn't already in flight.
2. **Open an Issue**: Use one of the structured templates:
   - **Bug Report** (`fix:`): For geometry intersections, slicer crashes, or script errors.
   - **3D Model Request** (`feat(cad):`): For new parametric parts, planters, or mechanical assemblies.
   - **Skill Enhancement** (`feat(skill):`): For updates to autonomous agent prompts or workflow scripts.
3. **Reference in PR**: The resolving PR must explicitly cite the issue (`Resolves #<issue-number>`).

---

## 3. Development Workflow

### Step 1: Clone the repository
```bash
git clone https://github.com/mlgitdev/BambuForge.git
cd BambuForge
```

### Step 2: Create a dedicated feature branch
```bash
git checkout -b feat/your-feature-name
```

### Step 3: Set up virtual environment
```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### Step 4: Verify CAD geometry & scripts
Run syntax checks and test CAD generation scripts:
```powershell
# Compile all scripts
python -m compileall .

# Run test slicing / geometry generator
python .agents/skills/3d-print-modeling/scripts/planter_family_engine.py
```

### Step 5: Verify Zero-PII Policy
Ensure no local system usernames, absolute user directories, or private tokens exist in any committed files:
```powershell
python .agents/skills/bambuforge-repo-sync/scripts/sync_to_bambuforge.py --dry-run
```

### Step 6: Commit and Open Pull Request
Follow Conventional Commits format:
```bash
git add .
git commit -m "feat(planter): add parametric chamfer reinforcement"
git push -u origin feat/your-feature-name
gh pr create
```

---

## 4. Commit Message Conventions

Commit titles must strictly conform to [Conventional Commits](https://www.conventionalcommits.org/):
`type(scope): description`

- `feat`: New parametric models, skills, or slicing capabilities.
- `fix`: Bug fixes, manifold repairs, clearance calibrations.
- `docs`: Documentation updates (`README.md`, `SDD.md`).
- `refactor`: Restructuring Python CAD scripts without changing output geometry.
- `chore`: Dependency updates, `.gitignore`, or repository configuration.

---

## 5. Security & Privacy Policy

- **Zero Hardcoded Paths**: Never hardcode paths containing personal usernames or absolute drive letters. Use relative paths or `<WORKSPACE_ROOT>`.
- **No Slicer Cache / Credentials**: Never commit `.gcode`, Bambu Studio cloud credentials, or API keys.
