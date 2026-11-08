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

* **Printer:** Bambu Lab P2S (`256 × 256 × 256 mm`).
* **CAD & Visual Toolchain:**
  * **`build123d` (`0.13.0` / OpenCascade `8.0`)** in `.venv` for programmatic B-Rep solid generation, multi-color zone boolean partitioning, and `.step`/`.3mf`/`.stl` export.
  * **FreeCAD 1.1 (`<USER_HOME>\AppData\Local\Programs\FreeCAD 1.1\bin\freecad.exe`):** Installed in user space for visual B-Rep `.step` / `.FCStd` CAD inspection and editing.
  * **CADCraft (`C:\Program Files\CADCraft\cadcraft.exe` & `cadcraft-cli.exe`):** Pure-Rust AutoCAD-style 2D/drafting tool with built-in headless CLI (`cadcraft-cli run`), `.scr` scripting, and native MCP server (`cadcraft-cli mcp --launch`) for 2D `.dxf` profile drafting that `build123d` (`ezdxf`) can extrude into 3D models.
  * **Bambu Studio (`C:\Program Files\Bambu Studio\bambu-studio.exe`):** Target slicer and multi-plate `.3mf` packager.
* **Slicer & Multi-Plate `.3mf` Workflow:** Always pack multi-module sets onto **separate build plates (trays)** inside a single `.3mf` project pre-configured for the **Bambu Lab P2S (`0.4 mm` nozzle, Supports = OFF)** using Bambu Studio's **2-column plate grid** (`Plate 1 = (128, 128)`, `Plate 2 = (435.2, 128)`, `Plate 3 = (128, -179.2)`), 6 flattened filament JSON profiles (`--load-filaments`), and a final `bambu-studio.exe --export-3mf` verification round-trip.
* **Multi-Agent Task Isolation & Worktree Rule:** Whenever another agent is running or when developing a new model/feature, always work inside an isolated worktree under `.worktrees/` created via `.\scripts\worktree.ps1 new <branch>`. Inherit the root `.venv` without duplicating dependencies, and treat the sibling `../BambuForge` folder as remote `bambuforge` and GitHub as `origin`.
* **Planter Drip Saucer Clearance & Full Corner Column Coverage Rule:**
  - Water collection saucers and drip plates must fully cover both the planter's nominal body profile AND any reinforced corner columns or architectural pilasters.
  - Clearance must be generous: **$\ge 4.5 - 5.0\text{ mm}$ per side** ($9.0 - 10.0\text{ mm}$ total gap), never razor-thin or "millimeter-to-millimeter" ($\le 1.0\text{ mm}$), ensuring effortless drop-in and lift-out without binding, jamming, or surface-tension sticking.
  - For oval / stadium planters, calibrate the saucer corner radius ($R \approx 50.0\text{ mm}$) so the corner does not aggressively cut into the diagonal corner columns, maintaining a uniform $4.8\text{ mm}$ clearance all around.
  - Outer dimensions must remain $\le 250\text{ mm}$ (e.g. $248 \times 198\text{ mm}$) to stay safely within the Bambu Lab P2S $256 \times 256\text{ mm}$ build envelope.
  - Internal raised aeration rails ($3.6\text{ mm}$ height) must elevate the planter above standing runoff water for root health.

* **Operational Guardrail:** Never run slow, unmonitored `urllib` downloads for large multi-hundred-MB installers; always check installed binaries first or use fast CLI tools with explicit timeouts.
* **Multi-Color AMS Segmentation Rule:** Partition planter models into distinct, non-overlapping B-Rep color sub-parts inside the `.3mf` and `.step` assemblies:
  * **Base Planter (`6` Colors):** 3 structural wall layers + horizontal connecting strips/belts + top rim collar + 4 corner edge columns.
  * **Drip Saucer Tray (`1` Color):** Monolithic watertight saucer.
  * **Extension Riser (`4` Colors + Print-Orientation Optimization):** Lower wall layer + upper wall layer + connecting belt/rim + 4 corner columns with **integrated male locking rods**. Always orient the Extension Riser **inverted (`180°` on its flat top rim at `Z = 0`)** so the 4 integrated locking rods print pointing straight UP (`+Z`) with zero supports.
* **Project Organization & Read-Only `imports/` Rule:**
  * Every requested or modified model must reside in its own dedicated subdirectory under `models/<model-name>/` and be indexed in Section 8 below.
  * The `imports/` directory is **strictly read-only input** (for user-supplied MakerWorld / third-party `.3mf`, `.stl`, `.step` files). Never write output files back into `imports/`; always output modified models, previews, and `.3mf` packages to `models/<model-name>/exports/` and `previews/`.
  * When importing/modifying third-party `.3mf` or `.stl` assemblies, always assign clean, descriptive human-readable **object names** (`<metadata key="name" value="..."/>`) and **plate names** (`<metadata key="plater_name" value="..."/>`) inside `Metadata/model_settings.config`.
  * **Mandatory Illustrated Assembly & Usage Guide (`ASSEMBLY_GUIDE.md`):** Every model folder under `models/<model-name>/` must include an `ASSEMBLY_GUIDE.md` accompanied by rendered 3D exploded/cutaway assembly diagrams in `previews/` explaining step-by-step how all parts fit together, their recommended slicing settings (`wall_loops`, `sparse_infill_density`, `sparse_infill_pattern`, and `100%` infill modifiers), filament material guidance, and how any functional accessories (like wicking straws, cloths/cords, or shutters) are used. Write all documentation in a **clean, general, public-shareable product manual tone** (no personal references, user timelines, or chat-specific remarks).
* **Bulky Structural Model Speed Rule (`0.28 mm` Draft vs `0.20 mm` Standard):** For large or bulky functional objects (planters, saucers, storage bins, structural frames) where miniature resolution is not required, precision is secondary to throughput. Proactively ask the user their speed/quality preference during intake:
  - `0.20 mm Standard`: Fine surface finish.
  - `0.28 mm Extra Draft`: **~35–45% print time reduction** with stronger interlayer bonding. Ensure vertical dimensions, Z-chamfers, and sacrificial bridges match `0.28 mm` when selected. Document both print time estimates in `ASSEMBLY_GUIDE.md`.
* **Stackable Modular Pin & Socket Joint Rule (Flush Planar Contact):** When designing male alignment dowels or stacking locking rods on stackable modular modules (e.g. Extension Risers, stackable bins, interlocking tiers):
  - Male pins must always protrude directly from a **flat planar landing shoulder** that mates flush against the flat landing face of the receiving module.
  - **NEVER** introduce a full-width conical taper between the column shoulder and the pin unless the mating female socket has an identical, matching conical counterbore recess. A conical taper colliding with a flat rim creates an air gap (e.g. 8.4mm) that prevents snapping down and forces the user to manually sand out the connection.
  - Use only a small root stress-relief fillet or chamfer ($\le 0.8\text{ mm}$ 45°) that fits entirely inside the female socket's lead-in chamfer ($\ge 1.4\text{ mm}$ 45°).
  - Provide $0.3\text{ mm}$ diametral clearance (e.g. $\varnothing 6.20\text{ mm}$ male rod into $\varnothing 6.50\text{ mm}$ socket) and a $1.2\text{ mm}$ 45° self-centering lead-in tip chamfer for effortless slide-in fit.
* **Automated Raster-to-Vector (PNG-to-SVG) CAD Transformation Capability:**
  - Raster artwork (logos, silhouettes, emblems, scans) supplied in `imports/` or via chat must be vectorized into precision scalable SVGs using the integrated `png_to_svg.py` engine (`.agents/skills/3d-print-modeling/scripts/png_to_svg.py`).
  - Supports automatic alpha mask isolation (`--channel alpha`), Otsu luminance thresholding (`--channel luminance`), and multi-color stacked vectorization (`--colormode color`).
  - Scales coordinates directly to physical millimetres (`--width-mm`, `--height-mm`) and centers at origin (`--center`) so `build123d.import_svg(svg_path)` directly produces clean 2D `Face` objects ready for 3D extrusion, embossing, and boolean subtraction.

---

* **Modular Stacking Snap-Fit Verification Rule (Skirt & Lego Boss Interlock with 0.000 mm³ Collision Simulation):**
  - **Male Skirt & Female Pocket:** The male alignment skirt (red contour) must extend into a matching receiving female pocket in the bottom module with $0.5	ext{ mm}$ vertical clearance ($7.5	ext{ mm}$ pocket vs $7.0	ext{ mm}$ skirt) and $0.35	ext{ mm}$ per-side clearance to ensure the skirt nests fully inside without bottoming out.
  - **Lego Boss & Socket Registration:** The circular Lego boss (yellow contour, e.g. $arnothing 15.0	ext{ mm} 	imes 3.0	ext{ mm}$) must nest into a matching female socket ($arnothing 15.7	ext{ mm} 	imes 3.5	ext{ mm}$) with $0.35	ext{ mm}$ radial clearance to provide tactile Lego-like registration and eliminate rotational twisting.
  - **Simulated Snapping Test:** Before finalizing any modular stacking design, the agent **MUST** run an automated boolean intersection test in `build123d` simulating the mated assembly. The collision volume must be exactly **`0.000000 mm³`** and the outer landing shoulders must meet with **`0.0 mm` air gap**.
  - **Visual Cross-Section Illustration:** Render an annotated cross-section or cutaway diagram proving flush seam contact and zero internal interference, embedding it in `ASSEMBLY_GUIDE.md`.

---

* **Bambu Studio Multi-Part Layout & Plate Visibility Rule:**
  - **Zero Part Overlap:** In multi-part single-plate `.3mf` projects, never inherit arbitrary nested assembly translation matrices. Assign explicit, discrete bed coordinates to each component in `3D/3dmodel.model` with $> 25\text{ mm}$ safety spacing on the $256 \times 256\text{ mm}$ build plate.
  - **Explicit Plate Model Instances:** Bambu Studio strictly requires an object to have an entry in `<build>` (`3D/3dmodel.model`), an entry in `<config>` (`Metadata/model_settings.config`), AND an explicit `<model_instance object_id="...">` inside `<plate>` in `Metadata/model_settings.config`. If `<model_instance>` is omitted, Bambu Studio hides the object from the plate view and will not slice it.
  - **Hinge & Latch Articulation Check:** Always orient latches with their pivot barrels aligned along the principal hinge axis (horizontal along X) and orient base containers upright with the solid floor at $Z = 0.00$ and open cavity facing $+Z$.

---

* **Interactive Multi-Part Exploded 3D Viewer Standard & Mandatory 1:1 Preview-to-3MF Correlation Invariant:**
  - **Standalone Interactive HTML Viewer:** Every multi-part model must generate an offline Three.js viewer (`previews/<model-name>_viewer.html`) with:
    1. **0% to 100% Exploded View Slider:** Smooth linear kinematic separation showing how components mate and assemble.
    2. **Component Isolation Checkboxes:** Toggles with AMS filament color swatches to inspect interior basins and sub-components.
    3. **Camera Presets:** `Isometric`, `Top`, `Bottom`, `Front`, `Rear`, and `Interior/Cutaway`.
    4. **Auto-Spin Strictly OFF by Default:** User maintains full manual orbit/pan/zoom control.
    5. **Bambu Lab P2S Bed Cage:** Toggleable $256 \times 256 \times 256\text{ mm}$ build volume outline.
  - **1:1 Preview-to-3MF Correlation Invariant (Zero-Mismatch Guardrail):** Previews must never diverge from 3MF exports. Before presenting any model to the user, the agent **MUST** run an automated programmatic audit (`audit_3mf_correlation` in `.agents/skills/bambu-studio-ai/scripts/generate_interactive_viewer.py`) asserting:
    1. Every component in the viewer is defined in `3D/3dmodel.model` and has an explicit `<model_instance>` tag in `<plate>` inside `Metadata/model_settings.config`.
    2. All bed-facing parts touch $Z = 0.00\text{ mm}$ and share the identical print orientation as the viewer.
    3. Discrete, collision-free plate positions ($> 25\text{ mm}$ clearance on the $256 \times 256\text{ mm}$ bed).
    4. Assembled components meet flush with $0.0\text{ mm}$ gap on mating shoulders and $0.000\text{ mm}^3$ unintended collision.

---

* **Tiered Plate Layout & "By Object" Sequence Exclusion Rule:**
  - **Toolhead Clearance Buffer ($\ge 100\text{ mm}$ $\Delta Y$):** When placing multiple components on a single Bambu Lab P2S build plate where "Print Sequence: By Object" may be active, arrange parts in discrete front/rear tiers:
    - **Front Tier ($Y \approx 50 - 80\text{ mm}$):** Main structural enclosures (Bottom Box, Top Lid).
    - **Rear Tier ($Y \approx 180 - 210\text{ mm}$):** Accessories and hardware (Drying Rack, Front Latch, Snap Hinge Pins).
    - Maintaining $\ge 100\text{ mm}$ spacing in Y completely eliminates toolhead clearance exclusion bubble overlaps in Bambu Studio.
  - **Face-Down Inlay Alignment & Non-Mirrored Exterior Text Invariant:**
    - When printing covers face-down at $Z = 0.00\text{ mm}$, all mating features (rear hinge knuckles and front latches) must be oriented along the identical directional axis as the base enclosure (both hinges at $+Y$).
    - The coordinate transformation must be engineered so that when looking directly at the exterior surface of the finished part (the face that contacted the bed), text reads left-to-right with zero mirroring.
  - **Embedded Auxiliary Hardware in Recognized 3MF Sub-Models:**
    - To guarantee auxiliary 3D printable hardware (snap hinge pins, collars, dowels) are never dropped by Bambu Studio, embed them directly as component objects inside primary recognized sub-models (e.g. `object_24.model`) with explicit `<part>` tags in `Metadata/model_settings.config`.

---

* **Planter Sub-Soil Irrigation Straw Geometry & Round Floor Hole Invariant:**
  - **Nominal Floor Hole Profile:** Planter drainage and sub-irrigation floor holes are round cylinders (nominal $\varnothing 8.00\text{ mm}$).
  - **True Round Circular Plug Cross-Section ($\varnothing 7.20\text{ mm}$):** Irrigation arch straws and bottom insertion plugs must be true round cylinders with a continuous circular cross-section ($\varnothing 7.20\text{ mm}$ outer diameter with continuous hollow $\varnothing 5.00\text{ mm}$ capillary wicking bore).
  - **Zero Oblong/Oval Distortion:** **NEVER** stretch, taper, or sweep a straw plug with unequal X/Z dimensions (e.g. $7.4 \times 10.6\text{ mm}$) to meet the bed, as this turns the plug into an oblong oval that physically jams and cannot enter the $\varnothing 8.00\text{ mm}$ round hole.
  - **Support-Free Planar Bed Contact Strip:** To ensure 100% support-free bed adhesion when printed lying flat on $Z = 0$, keep the straw circular and add a small planar bed flat facet ($0.30\text{ mm}$) along the underside, providing a continuous $2.8\text{ mm}$ wide bed contact strip without altering the circular insertion profile.
  - **Wide Landing Collar Stop ($14.0\text{ mm}$):** Provide a wide ($14.0\text{ mm}$) horizontal landing collar stop at the floor insertion line ($Y = 16.0\text{ mm}$) so the straw rests firmly on the planter floor with zero wobble, and add a $1.5\text{ mm}$ $45^\circ$ self-centering lead-in tip chamfer for smooth slide-in fit.
  - **Provide Standalone Single-Straw STL:** Alongside the 2-straw multi-plate tray (`tray4_irrigation_straws_2color.stl`), always export a standalone single-straw STL (`tray4_irrigation_straw_single.stl`) for convenient single replacement printing.

---


* **Universal FDM Text & Inlay Orientation Law (Face-Down Bed Contact vs Face-Up Upright Surfaces):**
  - **Case A: Face-Down Bed Contact ($Z = 0.00\text{ mm}$):**
    * When printing lids, covers, or panels face-down directly on the build plate (textured PEI plate at $Z = 0$) for zero supports and a premium finish, the surface contacting the bed **is the exterior face of the finished part**.
    * Looking at this exterior face (from underneath the bed in Bambu Studio via bottom camera $-Z$ looking up, or when picking up the finished print) mathematically inverts the horizontal screen projection: $\text{screen}_x = -X_{\text{cad}}$.
    * **Mandatory Bed Mirror Rule ($X \to -X$):** In CAD, any 2D text, logo, or multi-color inlay placed on a $Z = 0$ face-down surface **MUST be mirrored across the X axis ($X_{\text{cad}} \to -X_{\text{cad}}$)**.
    * When mirrored in CAD, the finished exterior face yields $\text{screen}_x = -(-X_{\text{svg}}) = +X_{\text{svg}}$:
      - Latin/English text reads naturally **Left-to-Right**.
      - Hebrew/Arabic script reads naturally **Right-to-Left** (e.g. *איגרוף תאילנדי* / *קפה*).
      - Emblems and symbols (Star of David, crests, logos) are **100% un-mirrored**.
    * **Both Body Cavity and Inlay Share Exact Transform:** The negative cavity in the lid shell and the positive multi-material inlay mesh MUST use the identical mirrored transform so they mate with $0.0000\text{ mm}$ zero drift.

  - **Case B: Face-Up Upright Surfaces ($Z > 0.00\text{ mm}$):**
    * When printing upright parts (e.g. bottom basin floor, top surface of an upright container, standalone badge on its flat back), the exterior face faces skyward ($+Z$).
    * The user views the part directly from above ($+Z$): $\text{screen}_x = +X_{\text{cad}}$.
    * **No Mirroring ($X \to +X$):** In CAD, text and inlays on an upright face MUST NOT be mirrored ($X_{\text{cad}} \to +X_{\text{cad}}$).

  - **Language Independence Invariant:**
    * Script direction (English L-to-R vs Hebrew R-to-L) is already encoded in SVG vector coordinates and font metrics.
    * **The rule does NOT change between languages:** Face-down on bed ALWAYS requires CAD $X \to -X$ so that BOTH English and Hebrew read correctly on the finished exterior face. Face-up NEVER requires CAD $X \to -X$.
    * Tested and verified in [`tests/test-text-inlay-orientation/`](tests/test-text-inlay-orientation/README.md).

  - **Standalone Artwork STLs:** Standalone badges, collectible medallions, and logos must be exported upright on their flat back at $Z = 0$ facing $+Z$ so the user can import, scale, and reposition them freely in Bambu Studio.

* **Calibrated Snap Hinge Pin Dimensions (Ø3.00mm Knuckles):**
  - Pin shaft diameter: **Ø2.75 mm** (total clearance $0.25\text{ mm}$ / $0.125\text{ mm}$ per side in Ø3.00mm knuckle), delivering a snug, smooth sliding fit without wobble or relaxed slack.
  - Split snap barb: **Ø3.05 mm** with $0.75\text{ mm}$ flex slot, compressing easily through Ø3.00mm knuckle.
  - Retaining collar ring: **Ø4.80 mm OD x 1.80 mm height**, inner bore **Ø2.85 mm** with **Ø3.15 mm x 0.70 mm counterbore detent**.
  - Flat-bottom lay-down orientation: $0.20\text{ mm}$ planar bed contact facet extends along underside for 100% bed adhesion and zero supports (5x layer line strength), plus vertical print option.
* **Retrofit Snap Adapter Coupler for Modular Planters:**
  - For previously printed base planters lacking the female interlocking rim, provide a compact $18.0\text{ mm}$ tall transition adapter (`oval_planter_retrofit_snap_adapter.stl` & `.step`).
  - Bottom face glues flush to the old base rim; top face provides the standard 3-tier Lego interlocking joint ($7.5\text{ mm}$ skirt pocket, Ø15.7 x $3.5\text{ mm}$ Lego boss sockets, Ø6.7mm through-bores).
  - Includes 4 concentric locator dowels (Ø6.0 x $16.0\text{ mm}$) for 100% concentric alignment during gluing.
  - Guaranteed **0.0 mm seam gap** and **0.000000 mm³ collision volume** against new Extension Risers!


* **Flush Inlay & Engraving Depth Standard (`1.60 – 2.00 mm` / `8–10 Layers`):**
  - Never make multi-color flush inlays, debossed recesses, or standalone decorative badges shallow (`0.60 mm` / 3 layers), as light filaments (Yellow, Gold, Orange, White) over dark shells (Black, Charcoal) suffer from optical color bleed-through and fragile geometry. Always design inlays, recesses, and standalone badges at **`1.60 – 2.00 mm` depth (`8–10 layers` at `0.20 mm`)** (e.g. `1.80 mm` on a `3.00 mm` lid leaving `1.20 mm` backing; `1.60 mm` on a `2.40 mm` floor leaving `0.80 mm` / 4 solid waterproof layers).
* **UJOYBIO / EjoyBio Elite PLA+ (`1 kg` Spool, `195–220 °C`) Master Profiles (`0.24 mm`, `0.20 mm`, `0.16 mm`):**
  - **Filament Settings Profile:**
    - **Nozzle (First Layer):** `210 °C`
    - **Nozzle (Other Layers):** `215 °C` *(Extra heat for thick `0.24 mm` layers)*
    - **Bed (Textured PEI Plate):** `60 °C` *(Ensures zero warping)*
    - **Max Volumetric Speed:** `15 mm³/s` *(High-speed safety cap)*
    - **Filament Diameter:** `1.75 mm`
    - **Flow Ratio:** `0.98` *(Standard generic starting point)*
  - **Process Speed Settings Profile (`0.24 mm` Layer Height):**
    - **Initial Layer:** `35 mm/s` *(Gives the thick line time to safely stick to the bed)*
    - **Initial Layer Infill:** `75 mm/s` *(Fills the first layer quickly but safely)*
    - **Outer Wall:** `150 mm/s` *(Caps visible walls to guarantee a beautiful surface finish)*
    - **Inner Wall:** `250 mm/s` *(Speeds up hidden structural walls)*
    - **Sparse Infill:** `270 mm/s` *(Maximizes high-speed printing inside the part)*
    - **Internal Solid Infill:** `200 mm/s` *(Ensures strong, dense internal floors/ceilings)*
    - **Travel Speed:** `300 – 500 mm/s` *(Default printer capability for non-printing moves)*
  - **Calibrated Precision Profiles (`0.20 mm` & `0.16 mm`):**
    - **`0.20mm Precision @BBL P2S - Ujoy PLA+` (`GP155`):** Outer wall `80 mm/s`, inner wall `160 mm/s`, outer wall accel `3000 mm/s²`, `precise_outer_wall = 1`, `infill_wall_overlap = 12%`, `3` walls (`1.25 mm`), `5` top / `4` bottom shells. Optimized for tight snap/slide mechanical fits, sharp debossing, and smooth perimeter finish.
    - **`0.16mm Precision @BBL P2S - Ujoy PLA+` (`GP209`):** Outer wall `60 mm/s`, inner wall `120 mm/s`, outer wall accel `2000 mm/s²`, `precise_outer_wall = 1`, `infill_wall_overlap = 10%`, `3` walls (`1.25 mm`), `6` top / `5` bottom shells, `0.20 mm` initial layer for robust PEI adhesion. Optimized for fine miniature detail, shallow overhangs, fine cursive script, and precision threads.
    - **Installed in Slicer:** Available directly in Bambu Studio Process dropdown (`%APPDATA%\BambuStudio\user\<user-id>\process\`).
  - **Reference & Code Integration:** Stored in [`.agents/skills/bambu-studio-ai/references/filament-profiles.md`](.agents/skills/bambu-studio-ai/references/filament-profiles.md) and [`apply_ujoybio_elite_pla_plus_profile()`](.agents/skills/3d-print-modeling/scripts/p2s_cad_helpers.py).
* **Bambu Lab P2S Stock `0.24 mm` Layer Preset & Multi-Plate Grid Scaling (`> 4` Plates):**
  - **Native P2S Thick-Layer Preset:** Bambu Studio ships **`0.24mm Standard @BBL P2S.json`** (`setting_id = GP214`) as the official thick-layer preset for the Bambu Lab P2S `0.4 mm` nozzle (no stock `0.28 mm` P2S `0.4 mm` profile exists). Pair with **`Bambu PLA Basic @BBL P2S.json`** (`Supports = OFF`) unless a custom filament profile (such as `UJOYBIO Elite PLA+`) is requested.
  - **Multi-Plate Column Formula:** Bambu Studio computes plate grid columns as `n_cols = max(2, math.ceil(math.sqrt(num_plates)))` (`2` columns for `2..4` plates; **`3` columns** for `5..9` plates, stride `307.2 mm`). Always strip cached `Metadata/plate_*.png`, `top_*.png`, and `pick_*.png` files from CLI skeleton `.3mf` archives before staging real models so Plate 1 thumbnails regenerate cleanly.
* **Material-Saving Thin Drip Plates & Leak-Proof Modular Drip-Tray Seam Architecture:**
  - **Thin-Wall Material Economy (`~1.0 mm` Short Ribs):** Keep drip plates lightweight (`1.20 mm` floor, `1.26–1.44 mm` walls, and **`0.96 mm` [`~1.0 mm`]** short raised aeration ribs) to cut filament usage by `~60%` while maintaining full watertightness.
  - **Zero Wet Floor Seams:** Never split a modular drip plate with a seam below water level (`0.2 mm` FDM capillary gaps leak onto indoor surfaces). Keep each tray an unbroken monolithic basin (`>= 4.3–4.5 mm` standing water depth), place dry sliding dovetail lugs strictly outside the wet perimeter resting flat on `Z = 0.00 mm`, and shield the inter-tray seam from above using either a **One-Piece `45°` Roof-Shingle Overlap Weir** (`Model 09`) or a **Snap-Over Peaked Saddle Roof Cap** (`Model 08`).
* **Conus (Conical) Storage-Stackable Planters & Anti-Jam Nesting Lug Rule:**
  - When designing simple cylindrical/round planters and saucers for multi-pot gardening, taper the walls into a **Conus (truncated-cone) frustum** with the base smaller than the top (e.g. `Ø125 mm` top → `Ø103 mm` base on planters; `Ø128 mm` top → `Ø118.4 mm` base on saucers) so unused planters and drip plates nest deeply (`~67–88%`) for compact storage.
  - **Mandatory Anti-Jam Floor Lugs:** Never allow nested smooth cones to wedge wall-on-wall (which causes friction/vacuum jamming). Always add narrow vertical anti-jam stacking stop lugs seated directly on the inner floor (`Z = floor_t`, `0.0%` overhang) calibrated to stop the upper pot with **`+0.25 to +0.45 mm` radial air gap** between the conical walls (`0.000000 mm³` boolean collision).


* **Indoor Silk Showcase Planters & Deep Capillary Wicking Reservoir Architecture:**
  - **Single-Color Silk 3D Relief Strings:** When optimizing sculptural planters for Silk PLA / Dual-Color Silk PLA in an indoor living-room setting, omit external irrigation ports for a clean architectural crown collar (`r = r_wall`). Increase string density (`24–28` strings) with narrow (`1.20–1.35 mm`) crests and deep (`3.60–4.20 mm`) radial projection to catch ambient room lighting and cast pronounced 3D luster ribbons without breaking.
  - **Deep Twist-Lock Wicking Reservoir (`2.3×` Deeper + Tall Support Ribs):** Expand bottom reservoir depth to **`32.2 – 38.4 mm`** (`~340 – 690 mL` submerged capacity), and elevate the planter floor with **`13.44 – 16.80 mm` tall outer radial support ribs**. Keep the central basin completely rib-free as a **wide-open, snag-free central wicking pool (`Ø86 – Ø112 mm`)** directly beneath enlarged floor holes (`1× Ø12–14 mm` center + `4× Ø11–12 mm` inner ring) for threading capillary wicking cloth strips or cotton ropes with a craft wire needle.
  - **Submergence Clearance Invariant (`z_str_start`):** When a planter base is submerged `~20 mm` inside a deep twist-lock reservoir, helical strings must NOT start near `Z = 0`. The lower submerged section (`Z = 0 .. z_str_start`, where `z_str_start = 19.2 – 21.6 mm`) must remain a smooth vertical cylinder of radius `r_wall` (`+7.46 mm` radial clearance from the plate wall), beginning the 3D Silk strings cleanly `~1.8 mm` above the reservoir rim to guarantee `0.000000 mm³` bayonet drop-in and lock collision.
  - **Monolithic Multi-Section Star-Loft Invariant:** Never construct interwoven or multi-rib helical arrays by performing `N` intersecting 3D boolean solid unions (`fuse()`), which cause OpenCASCADE non-manifold topology failures (`vol: 0 solids: 0`). Construct all helical, diamond, and sinusoidal profiles monolithically as single multi-section star-polygon lofts (`Polygon(*_star_pts(z)) -> loft(ruled=True)`), yielding 100% manifold solids in `< 6 seconds` with exact `< 10°` support-free overhangs.

* **Granular Media Hopper Monolithic Slopes & Knife-Edge Anti-Pinching Rotary Shutter Rule:**
  - **Monolithic Gravity Feed Slopes (Zero Loose Inserts, Zero Glue):** For coffee beans, dry pellets, and seed dispensers, eliminate separate glued ramp inserts. Integrate compound sloped floors directly into the monolithic solid (`9°–12°` front-to-back slope, `25°–30°` lateral wing slope). All internal slopes print layer-by-layer over solid/gyroid infill with **`100% support-free FDM printing`**.
  - **Machine Recess Inbound & Lid Rebate Outbound Invariants:**
    - Bottom machine intake step (`81.0 × 154.0 × 4.0 mm`) must be strictly preserved (`X = [-82, -1]`, `Y = [-94, 60]`) with a `0.8 mm` `45°` bottom chamfer for elephant-foot-free insertion into machine wells.
    - Top lid rebate shelf (`81.0 × 154.0 × 5.0 mm`) shifts forward synchronously with any front body expansion (e.g. `+20 mm` forward to `Y = [-74, 80]`), leaving an exact matching solid closed deck at the rear (`Y = -96 .. -74 mm`, `22.0 mm`).
    - **Preserved `2.0 mm` Internal Lid Contour Shelf:** At `Z = 45.0 mm` (`5.0 mm` below the top rim), an unbroken **`2.0 mm` wide flat horizontal contour ledge** (`77.0 × 150.0 mm` inner window) must run continuously along all 4 sides (Right, Left, Front, Rear). The original Melitta transparent lid drops into the 5.0 mm recess and **sits flat and securely on top of this contour shelf**, visible from within the model exactly as in the original and 60 mm models. Internal gravity slopes and cavity cutters must strictly respect this inner boundary so the contour shelf is never cut away.
  - **Rotary Shutter Anti-Pinching & Low-Friction Mechanics:**
    - **`30°` Leading Knife-Edge Bevel:** The leading blade edge sweeping across the drop chute must feature a `30°` bevel on the top face to push beans gently upward into the hopper rather than pinching, crunching, or wedging against the chute rim.
    - **Low-Friction Radial Gliding Runners:** Add `3` thin radial runners (`0.35 mm` height, `1.2 mm` width) on the underside of the shutter blade to provide line contact, reducing surface contact area by `> 85%` and preventing binding from fine coffee dust.
    - **Flush Snap Pivot Pin (`0.0 mm` Base Protrusion):** Bottom pivot pin features a flat head (`Ø7.8 mm × 1.1 mm`) counterbored flush inside `Z = 0.0 .. 1.3 mm` (`0.000 mm` protrusion beneath base), a `Ø3.90 mm` shaft (`0.30 mm` running clearance inside `Ø4.20 mm` shutter hole), and dual flexible cantilever snap barbs (`Ø4.4 mm` outer barb, `0.8 mm` flex slot) snapping captive into an internal retention cavity (`Z = 8.2 .. 11.2 mm`). Completely toolless, zero-glue, 5-second assembly, easily pressed out for hygienic cleaning.
  - **Exterior Branding Deboss & Typography Standard:**
    - Official vector script logos debossed `1.0 mm` deep into target walls (`clean=False`) with exact normal alignment (`z -> -Y` for front wall).
    - Match typography style: For cursive / script brandmarks (such as Melitta), use matching formal cursive fonts (`Script MT Bold`, `C:\Windows\Fonts\SCRIPTBL.TTF`) scaled prominently ($\ge 11.0\text{ mm}$ font size).
    - Exterior Viewer Orientation Invariant: Text must always read left-to-right when viewed from outside:
      - Front Wall ($Y = +82.0\text{ mm}$, normal $+Y$): Looking in $-Y$, viewer's left is $+X$, right is $-X$. Use `rotate(Axis.Z, 180.0).rotate(Axis.X, -90.0)`.
      - Right Wall ($X = -84.0\text{ mm}$, normal $-X$): Looking in $+X$, viewer's left is $+Y$, right is $-Y$. Use `rotate(Axis.Z, 270.0).rotate(Axis.Y, -90.0)`. Slogans spanning the right wall must be scaled prominently ($\ge 14.0 - 15.0\text{ mm}$ font size, bold) centered across the full length ($Y \approx -7.0\text{ mm}$, $\ge 130\text{ mm}$ span) with balanced margins, elevated safely above bottom slots ($Z \ge 12.0\text{ mm}$) and below lid shelves.
  - **High-Resolution Visual Assembly Guide Standard (Zero Swiss-Cheese):**
    - High-resolution visual assembly guides (`previews/<model-name>_assembly_guide.png`) must feature true 3D shaded polygon meshes across all panels.
    - Never downsample meshes with naive face slicing (`faces[::step]`), which deletes triangles and leaves open swiss-cheese holes. Always render the full mesh with directional key + fill lighting.
    - For multi-part exploded assemblies, always compute the collective bounding box of all translated components (`np.concatenate([p.vertices for p in parts])`) so all parts remain framed with generous margin without zooming in on a tiny sub-pin.
  - **Bambu Studio Plate 1 Aspect-Ratio Bed Calibration:**
    - For long rectangular parts ($> 150\text{ mm}$ length), rotate the largest component $90^\circ$ around $Z$ on Plate 1 so the length aligns along $X$ ($X \in [39..217\text{ mm}]$), keeping $Y$ within $[18..118\text{ mm}]$. This leaves a generous rear zone ($Y \in [148..236\text{ mm}]$) for accessories and hardware with $> 30\text{ mm}$ clearance and $> 18\text{ mm}$ bed margins.
    - Local mesh coordinates in `3D/3dmodel.model` must strictly normalize $Z_{\min} = 0.00\text{ mm}$ so parts sit 100% flush on the bed at $Z = 0.0\text{ mm}$.

* **Bambu Lab P2S Maximum Build Height (`250 mm`) Modular Planter Scaling Rule:**
  - **Dual Height Profiles:** Provide both the standard balanced height profile (`168.0 mm`, `~2.3–2.7 L` soil per module) and a **Max-Height `250.0 mm` Profile** (`Z = 250.00 mm`, `~3.5–4.2 L` soil per module, **+52–55% extra root depth** for deep-rooting hot peppers like Habanero, Jalapeño, and Ghost Pepper).
  - **Shared Drip Base Invariant (Zero Re-Prints):** Stackable drip plates and seam caps must remain the **exact same physical footprint and profile (`104 × 172 mm` pitch, `14.4 mm` height, `0.96 mm` short ribs)** so a grower can swap between 168 mm standard and 250 mm tall modules using the exact same drip plate base.
  - **Horizontal Locking Key Bed Layout (`239.8 mm` Bowtie Keys):** Print full-height locking keys flat horizontally on the bed rotated `90°` around Z (`X = 128 mm`, `Y = 216` & `238 mm` in the rear tier). The `239.8 mm` length spans `X = [8.1, 247.9] mm`, leaving safe `8.1 mm` bed margins, zero supports (`11.9°` side angle), and continuous filament strands running along the entire `240 mm` wall seam.
  - **Multi-Plate Packaging:** Provide both a **Master multi-plate `.3mf`** (containing both 168 mm and 250 mm sets) and a **Dedicated 250mm `.3mf`** (e.g. 6-plate for Model 08, 4-plate for Model 09) using `n_cols = max(2, math.ceil(math.sqrt(num_plates)))`.

* **Monolithic Blind Pocket Tilted Print Orientation & Un-Engraved Support-Side Rule (`45°–47°` Tilt + `support_on_build_plate_only = 1`):**
  - When a monolithic enclosure contains a wide, shallow internal pocket (e.g. rotary shutter pocket beneath a sloped hopper floor) whose `0°` ceiling would trap unremovable internal supports when printed flat, **pre-orient the body tilted `45°–47°` onto an un-engraved exterior wall** (with a `2.0 mm` planar bed-stabilization chamfer at `Z = 0.00 mm`).
  - Flare internal pocket/slot roofs (`+5°..+17°`) and draft opposing inner walls (`5°`) so **100% of internal surfaces sit `> 45°` from horizontal (`0.0 g` internal support)**.
  - Enforce `"enable_support": "1"`, `"support_type": "tree(auto)"`, `"support_on_build_plate_only": "1"`, and `"support_threshold_angle": "45"` in `Metadata/project_settings.config` (with `<metadata key="enable_support" value="0"/>` on flat companion parts) so exterior Tree Supports touch **only** the plain un-engraved side while all branded/customizable text faces remain vertical or skyward.
* **Enclosed Mechanism 3D Kinematic Insertion Trajectory Audit & Dual-Lock Snap-Handle Rule:**
  - Never design a 1-piece internal slider + external handle for an enclosed monolithic pocket without verifying assembly kinematics.
  - Decouple trapped mechanisms into: (1) a **slide-in internal member** with a planar XY elastic C-jaw female socket (`0.35 mm`/side jaw deflection, `< 1.5%` strain), (2) a **keyed external handle** pushed straight through the housing slot (`Snap Lock #1`), and (3) a **coaxial flush snap pivot pin** passing through both the housing bore and the handle's coaxial eye (`Positive Pin Lock #2`).
  - **Mandatory Pre-Handoff Trajectory Audit:** Simulate a continuous multi-step 6-DOF B-Rep insertion path (`20+` interpolated poses from outside the housing to the seated position) asserting **`0.000000 mm³` boolean collision** with the housing at every step.

* **Bambu Studio 2.6 `"include"` G-Code Template Resolution, Native Presets & `"gyroid"` Infill Rule:**
  - **Valid Infill Enum (`"gyroid"`):** Never write `"rectilinear"` to `sparse_infill_pattern` in Bambu Studio `.3mf` configs (Bambu Studio 2.6 rejects `"rectilinear"` for sparse infill with a replacement popup to `"cubic"`). Always use **`"gyroid"`** as the default structural sparse infill pattern.
  - **Recursive `"inherits"` + `"include"` Flattening (Zero G-Code Security Popup):** Bambu Studio 2.6 machine profiles (e.g. `Bambu Lab P2S 0.4 nozzle.json`) pull their full `machine_start_gcode` and `machine_end_gcode` from `"include"` array templates (such as `fdm_bbl_3dp_001_common_gcode.json`), not just `"inherits"`. `_flatten_bambu_json()` must recursively resolve both `"inherits"` and `"include"` templates before invoking `bambu-studio.exe --load-settings "<machine>;<process>" --load-filaments "<filament>" --export-3mf` so `different_settings_to_system[1..2]` remain empty (`""`), eliminating `"Customized Preset"` G-code security dialogs and preserving clean system dropdown names (`Bambu Lab P2S 0.4 nozzle`, `Textured PEI Plate`, `Bambu PLA Basic @BBL P2S`, and installed user fine-print process presets such as `0.16mm Precision @BBL P2S - Ujoy PLA+`).

* **360° Contour-Guided Hopper Funnel, Sub-Slope Pocket Ceiling (`-2°`), & Untwisted Explicit `Face(Wire.make_polygon)` Loft Rule:**
  - **Continuous 360° Slopes Around Circular Slider Guide Contour:** When a granular hopper feeds a quarter-circle rotary shutter (`R_blade`), preserve an unbroken circular slider housing guide contour (`R_guide = R_blade + 0.85 mm`) around the shutter arc and sweep **Front, Left, and Back** slopes continuously down to that guide contour (`Z_guide`) with zero vertical cut-off steps or protruding internal pivot chimneys.
  - **Sub-Slope Blind Pocket Ceiling (`0.0 g` Internal Support at `46°` Tilt):** Keep internal shutter pockets strictly beneath the sloped hopper floor (`>= 1.6 mm` solid roof web) with a slight downward `-2.0°` ceiling pitch toward the bed-tilted side and `4.5°` wall draft on opposing pocket walls so `100%` of internal surfaces exceed `45°` when tilted `46°` (`0.0 g` internal support).
  - **Untwisted Multi-Vertex Polygon Lofting:** Never pass arbitrary 2D `Polygon(*pts)` sketches through `BuildSketch` into `loft(ruled=True)`, as `BuildSketch` can re-index starting vertices between sections and twist the loft into vertical cliff cuts. Construct `Face(Wire.make_polygon([Vector(x, y, z) for ...]))` wires directly with identical vertex ordering and call `loft([f_bot, f_top], ruled=True)`.

* **Atomic Local Git Commits & Zero Leftover Agent Branches Rule:**
  - **Dual-Repo Commit Discipline:** Synchronizing to `BambuForge` commits only inside `../BambuForge`; the agent **MUST ALSO** record an atomic local `git commit` on `main` in the `3D-Automation` workspace after every completed task (or pass `--commit-source` to `sync_to_bambuforge.py`), while never pushing raw `3D-Automation` commits directly to public `origin`.
  - **Clean Branch Table (`main` Only Unless User-Created):** Whenever an agent creates a temporary branch/worktree (`model/*`, `feat/*`, `fix/*`, `sub/*`, `docs/*`), it must merge into `main`, remove `.worktrees/<folder>`, and delete the temporary branch (`.\scripts\worktree.ps1 finish <branch> main`). Never leave agent-created branches behind, and never delete branches created by the user.

---

## 8. Model Registry

| Date | Model Folder | Description | Status | Print Feedback / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `2026-10-24` | [`models/p2s-support-free-calibration/`](models/p2s-support-free-calibration/) | Support-free P2S calibration & tool dock (`build123d` B-Rep `.step`/`.3mf`/`.stl`) | Verified & Exported | Ready to slice (Supports = OFF) |
| `2026-10-24` | [`models/cherry-tomato-modular-planter/`](models/cherry-tomato-modular-planter/) | **Style 0: Classic Rectangular Modular Planter** (4 Trays: 6-Color Base + 1-Color Saucer + 4-Color Inverted Riser + 2-Color Sub-Soil Irrigation Arch Straws) | Verified & Exported | 4-Tray Multi-Color `.3mf` |
| `2026-10-24` | [`models/01-oval-stadium-planter/`](models/01-oval-stadium-planter/) | **Style 1: Oval / Stadium Track Modular Planter** (4 Trays: 6-Color Base + 1-Color Saucer + 4-Color Inverted Riser + 2-Color Sub-Soil Irrigation Arch Straws) | Verified & Exported | Active physical print test; calibrated 0.28mm Extra Draft option for bulky planter speedups |
| `2026-10-24` | [`models/02-roman-fluted-column-planter/`](models/02-roman-fluted-column-planter/) | **Style 2: Roman Fluted Architectural Column Planter** (4 Trays: 6/1/4/2 Colors incl. Sub-Soil Irrigation Arch Straws) | Verified & Exported | 4-Tray Multi-Color `.3mf` |
| `2026-10-24` | [`models/03-origami-faceted-prism-planter/`](models/03-origami-faceted-prism-planter/) | **Style 3: Origami Geometric Faceted Prism Planter** (4 Trays: 6/1/4/2 Colors incl. Sub-Soil Irrigation Arch Straws) | Verified & Exported | 4-Tray Multi-Color `.3mf` |
| `2026-10-24` | [`models/04-self-watering-sip-wicking-planter/`](models/04-self-watering-sip-wicking-planter/) | **Style 4: Sub-Irrigated Self-Watering (SIP) Wicking Planter** (4 Trays: 6/1/4/2 Colors incl. Sub-Soil Irrigation Arch Straws) | Verified & Exported | 4-Tray Multi-Color `.3mf` |
| `2026-10-24` | [`models/05-hexagonal-honeycomb-tessellation-planter/`](models/05-hexagonal-honeycomb-tessellation-planter/) | **Style 5: Modular Elongated Hexagonal Honeycomb Planter** (3 Trays: 6/1/4 Colors, no arch straws per user request) | Verified & Exported | 3-Tray Multi-Color `.3mf` |
| `2026-10-24` | [`models/06-zen-stepped-pagoda-wave-planter/`](models/06-zen-stepped-pagoda-wave-planter/) | **Style 6: Zen Stepped-Terrace Pagoda Planter** (4 Trays: 6/1/4/2 Colors incl. Sub-Soil Irrigation Arch Straws) | Verified & Exported | 4-Tray Multi-Color `.3mf` |
| `2026-10-24` | [`models/melitta-coffee-bean-dispenser/`](models/melitta-coffee-bean-dispenser/) | **Melitta Caffeo Solo Coffee Bean Dispenser (`60 mm` Hopper + Geared Rotary Shutter)** — Mid-section `60 mm` height mod + `Ø30.00 mm` 17-tooth geared rotary shutter + named objects in 1-Plate & 3-Tray `.3mf` | Verified & Exported | Read from `imports/`, exported to `models/melitta-coffee-bean-dispenser/exports/` |
| `2026-11-06` | [`models/melitta-coffee-bean-dispenser/`](models/melitta-coffee-bean-dispenser/) | **Melitta Caffeo Solo 50mm Wide Bean Dispenser (Monolithic Slopes + Debossed Logo + Upgraded Shutter)** — `50.0 mm` height, `100.0 mm` width (`+15 mm` left wing), `178.0 mm` length (`+20 mm` front extension), preserved machine step (`81 × 154 × 4 mm`) & lid rebate (`81 × 154 × 5 mm` with unbroken `2.0 mm` internal contour shelf), monolithic gravity-feed slopes (`9.3°` front, `29.2°` left), debossed official "Melitta" script logotype + "Uliel Family" (`Script MT Bold`, `11.0 mm`), prominent 2-row full-wall slogan (*"It's Coffee Time / While AI is working"*, `15.0 mm` bold font, spanning `136.0 mm` across the right wall), upgraded shutter with `30°` knife-edge + `3` gliding runners + thumb tab, and flush bottom snap pivot pin (`0.0 mm` protrusion) | Verified & Exported | Master 1-Plate & 3-Tray `.3mf` (`0.24mm Standard @BBL P2S`, `0.000000 mm³` collision, 1:1 correlation PASS, interactive 3D HTML viewer & 4-panel guide with real 3D shaded polygon meshes) |
| `2026-10-26` | [`models/muay-thai-boxer-lamp/`](models/muay-thai-boxer-lamp/) | **Muay Thai Boxer E27 Desk Lamp (Option A — 1:1 Photo Match)** — Monolithic single-plate print ($123.2 \times 123.0 \times 223.9\text{ mm}$): Flared pedestal with E27 housing + Voronoi mesh globe + photo-matched fighter with high-guard left glove, forward punch right fist, tousled wet fringe, and hollow optical light chimney beaming through eyes | Verified & Exported | Ready to slice (`.step`, `.3mf`, `.stl` in `exports/`, 4 views in `previews/`) |
| `2026-10-27` | [`models/mouthguard-box-pegasus/`](models/mouthguard-box-pegasus/) | **Mouthguard / Aligner Travel Case (Pegasus Muay Thai Edition)** — Deep `1.80 mm` / `1.60 mm` flush multi-color emblem inlays & debossing, custom 3D-printable snap hinge pin, and 4-Plate `.3mf` | Verified & Exported | Preserved user plates + full `.3mf` in `exports/` |
| `2026-11-05` | [`models/simple-cylindrical-planter/`](models/simple-cylindrical-planter/) | **Simple Conus Stackable Planter + Conus Thin Stackable Drip Plates (`66–70%` Material Saved)** — 4-Plate Bambu `.3mf` (`UJOYBIO Elite PLA+ @ 0.24 mm`), remade Conus profile (`Ø125→103 mm` `100%` & `Ø100→82.4 mm` `80%`) + anti-jam storage-stacking lugs (`87.5%` nesting, `0.000 mm³` collision) + matching Conus stackable thin drip plates | Verified & Exported | 4-Plate `.3mf` (`24.7 g` `100%` / `12.6 g` `80%` drip plates, `0.0%` overhang) |
| `2026-11-05` | [`models/07-helical-string-self-drip-planter/`](models/07-helical-string-self-drip-planter/) | **Style 7: Large Hot-Pepper (`7.6 L`) Helical-String Self-Dripping Planter** — Thin `1.26 mm` shell reinforced by `8` sparse steep (`~67°`, `90°`-swivel) diagonal strings + `4`-way `12 mm` diamond top drip-hose ports + twist-lock self-dripping bottom plate (`0.96 mm` short ribs) | Verified & Exported | 2-Plate `.3mf` (`0.24mm Standard @BBL P2S`, `0.000 mm³` collision, Support-Free PASS) |
| `2026-11-05` | [`models/08-modular-dovetail-pin-expandable-planter/`](models/08-modular-dovetail-pin-expandable-planter/) | **Style 8: Expandable Side-by-Side Rectangular Planter (`6` Dovetail + Blind Pin Joins)** — `168 mm` Standard (`~2.7 L`/mod) and **Max-Height `250 mm` Profile** (`~4.2 L`/mod, +55% root depth) + `100%` identical `180°`-symmetric Left/Right Ends + `$N$` stackable Middles + Solid/Slotted dividers + `4`-way `12 mm` ports + Saddle-Cap `0.96 mm`-rib drip plates (shared 1:1) | Verified & Exported | Master 10-Plate & Dedicated 6-Plate `.3mf` (`0.24mm Standard @BBL P2S`, `0.000000 mm³` collision, 1:1 correlation PASS) |
| `2026-11-05` | [`models/09-modular-wedge-rail-spillway-planter/`](models/09-modular-wedge-rail-spillway-planter/) | **Style 9: Researched Expandable Closed-Cell Planter (Top-Drop Bowtie Keys + One-Piece Roof-Shingle Drip Plates)** — `168 mm` Standard (`~2.3 L`/cell) and **Max-Height `250 mm` Profile** (`~3.5 L`/cell, +52% root depth) + live-swappable `4`-wall diagonal-string cells + `161 mm` & `240 mm` horizontal-printed bowtie rail keys + zero-loose-part shingle-weir `0.96 mm`-rib drip plates (shared 1:1) | Verified & Exported | Master 6-Plate & Dedicated 4-Plate `.3mf` (`0.24mm Standard @BBL P2S`, `0.000000 mm³` collision, 1:1 correlation PASS) |
| `2026-11-06` | [`models/10-indoor-silk-helical-wicking-planter/`](models/10-indoor-silk-helical-wicking-planter/) | **Style 10: Indoor Living-Room Silk Helical Planter & Deep Twist-Lock Wicking Reservoir** — 3 distinct Silk styles (Type A Swirl, Type B Diamond Helix, Type C S-Wave) in 3 separate 4-Plate `.3mf` projects (`0.24mm Standard @BBL P2S`) across Large (`~7.4 L`) and Medium (`~3.3 L`) + deep self-watering reservoir (`38.4 / 32.2 mm`, `~690 / ~340 mL`) with `16.8 / 13.4 mm` tall ribs, wide-open central wicking pool (`Ø112 / Ø86 mm`), and `Ø14 / Ø12 mm` cord-threading holes | Verified & Exported | 3 Dedicated 4-Plate `.3mf` projects (`0.000000 mm³` collision, `100%` Support-Free PASS, interactive 3D HTML viewer & 4-panel guide) |
| `2026-11-07` | [`models/melitta-coffee-bean-dispenser/`](models/melitta-coffee-bean-dispenser/) | **Melitta Caffeo Solo 50mm Wide Bean Dispenser (v3 — 360° Front+Left+Back Hopper Slopes + `R = 72.85 mm` Circular Slider Guide Contour + `46°` Left-Side Tilt + Native P2S/Gyroid `.3mf`)** — Continuous 360° Front, Left, and Back slopes wrapping smoothly around an unbroken `R = 72.85 mm` (`0.85 mm` clearance) circular slider housing guide contour with zero cut-off cliffs; `46.0°` Left-Side Tilt (`0.0 g` internal pocket support, `support_on_build_plate_only = 1`); 2-piece slide-in `R = 72.0 mm` Quarter Blade + Snap-In Geared Thumb Handle + coaxial Flush Snap Pivot Pin; native `Bambu Lab P2S 0.4 nozzle` + `Bambu PLA Basic @BBL P2S` + `0.16mm Precision @BBL P2S - Ujoy PLA+` (`gyroid` infill, zero G-code popup) | Verified & Exported | 1-Plate & 4-Trays `.3mf` (`0.16mm Precision Ujoy PLA+`, `gyroid`, `0.000000 mm³` mated & 3D trajectory collision, `audit_3mf_correlation` PASS, 6-panel shaded PNG guide & interactive 3D HTML viewer) |
