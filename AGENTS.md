# 3D-Automation — Bambu Lab P2S Modeling Workspace (build123d & FreeCAD Edition)

> **Active Printer:** Bambu Lab P2S
> **Build Volume:** `256 × 256 × 256 mm` (X × Y × Z)
> **Primary CAD Engine:** **build123d** (Python OpenCascade B-Rep CAD) + **FreeCAD Python API** compatible (`.step`, `.3mf`, `.stl`)
> **Primary Slicer:** Bambu Studio (`.step` & `.3mf` native arc slicing)
> **Core Mandate:** **Support-Free FDM Design** (`<= 45°` overhangs, teardrop horizontal holes, `Z = 0` bottom chamfers, sacrificial counterbore bridges) + **Continuous Self-Learning** from user feedback.

---

## 0. First-Run Agentic Onboarding Protocol (Automated Fine-Tuning)

When an AI agent (Antigravity, Cursor, Claude Code, Copilot, Windsurf, Codex, etc.) is asked:
* *"How do I use this repository?"*
* *"Help me get started"*
* *"Help me set up BambuForge for my printer"*
* Or when asked to generate any 3D model before the user's printer configuration has been confirmed:

The agent **MUST immediately ask the user**:
> **"What printer and model do you have?"**  
> *(e.g., Bambu Lab X1C / P1S / P2S / A1 / A1 Mini, Voron 2.4, Prusa MK4/XL, Creality Ender 3 / K1, Elegoo Neptune, etc., your nozzle size [0.4 mm default], and whether you have multi-material / AMS units).*

### Automated Fine-Tuning Execution:
Upon receiving the user's printer response, the agent must automatically complete the environment fine-tuning:
1. **Calibrate Section 2 (Hardware Profile & Constraints):** Update the `Build Volume (X × Y × Z)`, `Safe Volume`, and `Standard Nozzle` to match the user's specific printer.
2. **Clarify Print Speed & Quality Preference for Bulky Objects:**
   When modeling large/bulky objects (e.g. planters, bins, housings, structural frames) where miniature precision is not critical, proactively ask the user:
   > **"What print quality/speed do you prefer?"**
   > * **`0.20 mm Standard`**: Higher surface resolution, smoother layer lines; best for miniatures, detailed textures, and tight press-fits.
   > * **`0.28 mm Extra Draft`**: **~35–45% faster printing** with higher layer adhesion; ideal for bulky planters, pots, saucers, and storage boxes.
3. **Calibrate Material & Slicing Defaults:**
   - **Bambu Lab Printers (P2S / X1C / P1S / A1 / A1 Mini):** Set machine profile strings and configure AMS slots (`1..4` or `1..16`).
   - **Other FDM Printers (Prusa / Voron / Creality / Any FDM):** Configure `.step` / `.stl` multi-body exports and OrcaSlicer / PrusaSlicer settings.
4. **Persist & Confirm:** Update `AGENTS.md` and present the user with a tailored quick-start guide ready to accept their first model prompt.

---

## 1. Workspace Architecture

Every model request is isolated in its own dedicated folder under `models/`:

```text
<WORKSPACE_ROOT>\
├── AGENTS.md                          # Master rules, printer specs, model registry & learned preferences
├── build.ps1                          # Root task runner & worktree orchestrator
├── .gitignore                         # Excludes .venv/, .worktrees/, temp slicer files
├── .venv/                             # Dedicated Python 3.11 environment (build123d, trimesh, matplotlib)
├── .worktrees/                        # Isolated git worktrees for parallel agents & tasks
├── scripts/                           # Cross-platform automation scripts
│   ├── worktree.ps1                   # PowerShell worktree manager (new, list, remove, merge-back, sync)
│   └── worktree.sh                    # Bash worktree manager (macOS/Linux)
├── .agents/
│   └── skills/
│       ├── 3d-print-modeling/         # Parametric build123d / FreeCAD FDM design skill + helper library
│       ├── bambu-studio-ai/           # Local zero-subscription CAD-to-Bambu Studio pipeline & analyzer
│       ├── self-learning-cad/         # Continuous preference capture, tolerance tuning & gap-closing skill
│       ├── bambuforge-repo-sync/      # Automated bidirectional skill sync with public BambuForge repo
│       └── worktree/                  # Multi-agent task isolation & git worktree manager skill
└── models/
    └── <model-name>/                  # Dedicated directory per requested 3D model
        ├── <model-name>.py            # Parametric build123d / FreeCAD Python source
        ├── ASSEMBLY_GUIDE.md          # Illustrated step-by-step assembly & usage instructions
        ├── exports/                   # Ready-to-slice .step, .3mf, and .stl files for Bambu Studio
        ├── previews/                  # Rendered multi-angle PNG views, 3D assembly guide & viewer
        └── notes.md                   # Model dimensions, print settings, and post-print feedback
```

---

## 2. Bambu Lab P2S Hardware Profile & Constraints

| Parameter | Value | Design Impact |
| :--- | :--- | :--- |
| **Build Volume (X × Y × Z)** | `256 × 256 × 256 mm` | Keep single-piece parts `<= 250 mm` per axis for safe skirt/brim margin; split larger parts with dovetails/dowels. |
| **Standard Nozzle** | `0.4 mm` | Design wall thicknesses as multiples of extrusion width (`0.42 mm` outer / `0.45 mm` inner): `0.85 mm` (2 walls), `1.25 mm` (3 walls), `1.65 mm` (4 walls), `2.0+ mm` (structural). |
| **Standard Layer Height** | `0.20 mm` Standard<br>`0.24 mm` Standard (`@BBL P2S`) | Default is `0.20 mm`. On the Bambu Lab P2S (`0.4 mm` nozzle), Bambu Studio's stock thick-layer preset is **`0.24mm Standard @BBL P2S`** (note: Bambu Studio does not ship a stock `0.28 mm` preset for P2S `0.4 mm`). Design vertical Z-steps, thin drip floors (`1.20 mm`), short raised ribs (`0.96 mm`), and sacrificial bridges as exact multiples of `0.24 mm` (or `0.20 mm`). |
| **Preferred Export Formats** | `.step`, `.3mf`, `.stl` | Always export **`.step`** alongside `.3mf`/`.stl`—Bambu Studio slices `.step` files with true circular arcs (`G2`/`G3`) and zero facet artifacts, and `.step` files open directly in **FreeCAD** as editable solids. |

---

## 3. Mandatory Support-Free Design Rules (Zero-Support Priority)

All models created in this workspace **must** be engineered to print with **zero supports** (or minimal built-in breakaway features only when physically unavoidable):

1. **The 45° Overhang Invariant:**
   * All outward-sloping walls, brackets, and gussets must stay at **`<= 45°` from vertical** (`>= 45°` from the build plate).
   * Never create floating cantilevers; support ledges from below with a `45°` chamfered ramp or lofted gusset.
2. **Bottom Edge Treatment (`Z = 0` Chamfer, Never Fillet):**
   * Any edge touching `Z = 0` or facing downward must use a **`45°` chamfer** (e.g., `0.8 mm – 1.5 mm` via `chamfer(part.faces().sort_by(Axis.Z)[0].edges(), length=1.0)`), **never** a downward-facing radius/fillet (which starts at nearly `90°` overhang on the first layers).
   * Use `fillet()` on **vertical edges** (`edges().filter_by(Axis.Z)`) and **top edges**.
3. **Horizontal Holes & Tunnels:**
   * Holes `<= 5 mm` diameter can print circular.
   * Horizontal holes `> 5 mm` diameter **must** use a **teardrop profile** (45° pointed/truncated roof) or **diamond/hexagonal top** so the ceiling bridges cleanly without sagging.
4. **Counterbored Screw Holes (Floating Ceilings):**
   * When a screw head recess is on the bottom (`Z = 0`) and the shaft hole is above it, never leave a floating annular ring. Add a **`0.20 mm` (single-layer) sacrificial bridge** across the bore (punched through easily by the screw).
5. **Bridging Limits:**
   * Keep unsupported horizontal bridges **`<= 15 mm`** for functional accuracy (`<= 25 mm` cosmetic max on P2S). For wider spans, arch or chamfer the ceiling at `45°`.
6. **Print Orientation (`Z = 0` Ready):**
   * Always export models pre-oriented in their optimal print orientation sitting flat on `Z = 0` (`min_z = 0.0`), centered in X/Y.

---

## 4. Calibrated Tolerances & Fit Table (Bambu Lab P2S Default)

*(Updated automatically by the Self-Learning Skill as we test prints on your specific P2S and filaments)*

| Fit Type | Per-Side Clearance | Diameter / Total Gap | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **Press / Interference Fit** | `0.05 – 0.08 mm` | `0.10 – 0.15 mm` | Bearings, magnets, permanent dowels (always add `0.5 mm` lead-in chamfer) |
| **Snug / Snap Fit** | `0.12 – 0.15 mm` | `0.25 – 0.30 mm` | Snap-fit enclosure lids, friction-fit caps |
| **Sliding / Clearance Fit** | `0.20 – 0.25 mm` | `0.40 – 0.50 mm` | Drawers, sliding rails, removable covers, print-in-place joints |
| **Loose / Free Fit** | `0.35 – 0.50 mm` | `0.70 – 1.00 mm` | Hinges, cable pass-throughs, quick-drop organizers |
| **Horizontal Fastener Holes** | `+0.15 mm` radius | `+0.30 mm` diameter | M3 hole = `3.3 mm`, M4 = `4.3 mm`, M5 = `5.3 mm` |
| **Heat-Set Inserts (Ruthex/CNC)** | Standard taper | Nominal spec | M3 = `4.0 mm` hole w/ `4.4 mm` top counterbore |

---

## 5. Git Worktree Protocol & Multi-Agent Task Isolation (Mandatory)

The repository root checkout on `main` is considered **clean and stable**. When multiple AI agents are operating concurrently or when developing separate models/features:

### 1. Mandatory Worktree for Concurrent or Isolated Work
- If another agent is actively working in the workspace (or to isolate any new model, CAD engine modification, or experiment), **never work directly in the root checkout**.
- Always spawn a dedicated git worktree under `.worktrees/`:
  ```powershell
  # Windows PowerShell
  .\scripts\worktree.ps1 new model/<descriptor>
  # Or via task runner:
  .\build.ps1 -Task worktree-new -Branch model/<descriptor>
  ```
  ```bash
  # Linux / macOS
  ./scripts/worktree.sh new model/<descriptor>
  ```

### 2. Dual-Remote Topology
- **Local Working Studio (`3D-Automation`):** Contains the primary Python `.venv`, `models/`, and local worktrees.
- **Sibling Remote (`bambuforge`):** Points to local sibling repo `../BambuForge`. Fetch anytime with:
  ```powershell
  .\scripts\worktree.ps1 sync-remote bambuforge
  ```
- **Upstream GitHub (`origin`):** Points to `https://github.com/mlgitdev/BambuForge.git` for PRs and issue correlation.

### 3. Shared Environment & Toolchain Inheritance
- Worktrees do **NOT** duplicate `.venv/`.
- Every worktree automatically inherits the root Python environment at `..\..\.venv\Scripts\python.exe` (build123d 0.13, OpenCascade 8.0, Trimesh, Matplotlib).
- All CAD generators and slicing scripts must run using this shared interpreter.

### 4. Mandatory Atomic Local Commits & Zero Leftover Agent Branches
- **Atomic Local Git Commit Per Task (Mandatory):** Every completed 3D model, CAD revision, slicer profile update, or skill refinement **MUST** be committed locally to `main` in the `3D-Automation` workspace using Conventional Commits (`feat(models): ...`, `fix(cad): ...`, `chore(skills): ...`) before concluding the task. *(Keep `3D-Automation` commits strictly local; never `git push origin` raw `3D-Automation` commits directly to the public `BambuForge` GitHub remote—only sanitized updates go upstream via `sync_to_bambuforge.py`.)*
- **One-Command Merge-Back, Worktree Removal & Agent Branch Deletion:** Never leave temporary agent-created branches (`model/*`, `feat/*`, `fix/*`, `sub/*`, `docs/*`) or `.worktrees/*` folders dangling after task completion:
  ```powershell
  # Merge back into main
  .\scripts\worktree.ps1 finish model/<descriptor> main

  # Safely remove the worktree
  .\scripts\worktree.ps1 remove model/<descriptor> -DeleteBranch
  ```
- **User-Created Branch Protection:** Never leave agent-created branches behind, and **never delete branches explicitly created by the user** unless requested.
- For full operational workflows, consult the [`worktree` skill](.agents/skills/worktree/SKILL.md).

---

## 6. Self-Learning Loop & Continuous Adaptation

Whenever the user requests a fine-tuning adjustment, reports a print fit issue, or expresses a preference:
1. **Immediate Action:** Apply the change to the active model in `models/<model-name>/`.
2. **Gap Analysis & Persistence:** Update `.agents/skills/self-learning-cad/references/learned-preferences.md` and section **7. Learned User Preferences** below so the agent never repeats the same mistake and automatically applies the preference to all future models.
3. **Workflow Invocation:** Always consult `.agents/skills/3d-print-modeling/SKILL.md`, `.agents/skills/bambu-studio-ai/SKILL.md`, and `.agents/skills/self-learning-cad/SKILL.md` when designing, analyzing, or refining models.

---

## 7. Learned User Preferences (Auto-Updated)

> *This section is automatically populated by the `self-learning-cad` skill as you calibrate your specific printer, filaments, and design preferences. Universal FDM engineering patterns live in [`.agents/skills/3d-print-modeling/references/fdm-design-principles.md`](.agents/skills/3d-print-modeling/references/fdm-design-principles.md).*

* **Printer:** Configure via First-Run Onboarding (Section 0).
* **Default Slicing Philosophy:** Support-free (`<= 45°` overhangs, `Z = 0` chamfers), `gyroid` sparse infill, native `.step` + `.3mf` multi-plate exports, and non-destructive versioned `.3mf` iterations.
* **Multi-Color Strategy:** Offer both flush AMS inlay (`1.60–2.00 mm` depth) and zero-waste single-color clip-together lattice/comb assemblies (`0` filament swaps) when appropriate.

---

## 8. Model Registry

| Date | Model Folder | Description | Status | Print Feedback / Notes |
| :--- | :--- | :--- | :--- | :--- |
| *(auto)* | `models/<model-name>/` | *New models generated in this workspace are indexed here automatically.* | — | — |
