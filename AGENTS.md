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
| **Standard Layer Height** | `0.20 mm` Standard<br>`0.28 mm` Extra Draft | Default is `0.20 mm`. For bulky structural objects (planters, boxes, frames) where fine precision is secondary, recommend **`0.28 mm Extra Draft`** (~35–45% faster print time). Design vertical Z-steps and sacrificial bridges to match active layer height (`0.20 mm` or `0.28 mm`). |
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

### 4. Merge-Back & Cleanup Lifecycle
- Once a model or feature is generated, verified, and committed:
  ```powershell
  # Merge back into main
  .\scripts\worktree.ps1 merge-back model/<descriptor> main

  # Safely remove the worktree
  .\scripts\worktree.ps1 remove model/<descriptor>
  ```
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


* **Face-Down Bed Printing & Inlay/Logo Chirality Principle (The Roll-Over Rule):**
  - **The Roll-Over Invariant:** When an enclosure top lid is oriented face-down on the textured PEI plate (`Z = 0`) for support-free flush multi-color inlay printing, the lid has undergone a 180° physical roll-over around the X or Y axis. Any 2D logo, text engraving, or multi-color inlay applied to that exterior face MUST undergo the **EXACT SAME rigid-body rotation** as the lid.
  - **Never Negate a Single Axis:** Inverting $X \to -X$ or $Y \to -Y$ creates an improper mirror reflection ($\\det(R) = -1$) rather than a physical 3D roll-over ($\\det(R) = +1$), reversing text direction and logo chirality.
  - **The Slicer Through-the-Back Illusion:** In Bambu Studio, looking from `+Z` looks down into the inside cavity of the lid; looking through the back of an un-mirrored part naturally looks reversed. Never mirror the logo to look readable from `+Z`, which guarantees it prints backwards on the bed!
  - **The Bottom Camera Invariant:** The definitive verification is to view the model from **`-Z` looking UP at the build plate**. In this view, exterior text MUST read left-to-right and emblems must face their intended directions.
  - **Standalone Artwork STLs:** Standalone badges and logos must be exported upright on their flat back at $Z = 0$ facing $+Z$ so the user can import, scale, and position them anywhere in Bambu Studio.
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


## 8. Model Registry

| Date | Model Folder | Description | Status | Print Feedback / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `2026-10-24` | [`models/p2s-support-free-calibration/`](file:///<WORKSPACE_ROOT>/models/p2s-support-free-calibration/) | Support-free P2S calibration & tool dock (`build123d` B-Rep `.step`/`.3mf`/`.stl`) | Verified & Exported | Ready to slice (Supports = OFF) |
| `2026-10-24` | [`models/cherry-tomato-modular-planter/`](file:///<WORKSPACE_ROOT>/models/cherry-tomato-modular-planter/) | **Style 0: Classic Rectangular Modular Planter** (4 Trays: 6-Color Base + 1-Color Saucer + 4-Color Inverted Riser + 2-Color Sub-Soil Irrigation Arch Straws) | Verified & Exported | 4-Tray Multi-Color `.3mf` |
| `2026-10-24` | [`models/01-oval-stadium-planter/`](file:///<WORKSPACE_ROOT>/models/01-oval-stadium-planter/) | **Style 1: Oval / Stadium Track Modular Planter** (4 Trays: 6-Color Base + 1-Color Saucer + 4-Color Inverted Riser + 2-Color Sub-Soil Irrigation Arch Straws) | Verified & Exported | Active physical print test; calibrated 0.28mm Extra Draft option for bulky planter speedups |
| `2026-10-24` | [`models/02-roman-fluted-column-planter/`](file:///<WORKSPACE_ROOT>/models/02-roman-fluted-column-planter/) | **Style 2: Roman Fluted Architectural Column Planter** (4 Trays: 6/1/4/2 Colors incl. Sub-Soil Irrigation Arch Straws) | Verified & Exported | 4-Tray Multi-Color `.3mf` |
| `2026-10-24` | [`models/03-origami-faceted-prism-planter/`](file:///<WORKSPACE_ROOT>/models/03-origami-faceted-prism-planter/) | **Style 3: Origami Geometric Faceted Prism Planter** (4 Trays: 6/1/4/2 Colors incl. Sub-Soil Irrigation Arch Straws) | Verified & Exported | 4-Tray Multi-Color `.3mf` |
| `2026-10-24` | [`models/04-self-watering-sip-wicking-planter/`](file:///<WORKSPACE_ROOT>/models/04-self-watering-sip-wicking-planter/) | **Style 4: Sub-Irrigated Self-Watering (SIP) Wicking Planter** (4 Trays: 6/1/4/2 Colors incl. Sub-Soil Irrigation Arch Straws) | Verified & Exported | 4-Tray Multi-Color `.3mf` |
| `2026-10-24` | [`models/05-hexagonal-honeycomb-tessellation-planter/`](file:///<WORKSPACE_ROOT>/models/05-hexagonal-honeycomb-tessellation-planter/) | **Style 5: Modular Elongated Hexagonal Honeycomb Planter** (3 Trays: 6/1/4 Colors, no arch straws per user request) | Verified & Exported | 3-Tray Multi-Color `.3mf` |
| `2026-10-24` | [`models/06-zen-stepped-pagoda-wave-planter/`](file:///<WORKSPACE_ROOT>/models/06-zen-stepped-pagoda-wave-planter/) | **Style 6: Zen Stepped-Terrace Pagoda Planter** (4 Trays: 6/1/4/2 Colors incl. Sub-Soil Irrigation Arch Straws) | Verified & Exported | 4-Tray Multi-Color `.3mf` |
| `2026-10-24` | [`models/melitta-coffee-bean-dispenser/`](file:///<WORKSPACE_ROOT>/models/melitta-coffee-bean-dispenser/) | **Melitta Caffeo Solo Coffee Bean Dispenser (`60 mm` Hopper + Geared Rotary Shutter)** — Mid-section `60 mm` height mod + `Ø30.00 mm` 17-tooth geared rotary shutter + named objects in 1-Plate & 3-Tray `.3mf` | Verified & Exported | Read from `imports/`, exported to `models/melitta-coffee-bean-dispenser/exports/` |
| `2026-10-26` | [`models/muay-thai-boxer-lamp/`](file:///<WORKSPACE_ROOT>/models/muay-thai-boxer-lamp/) | **Muay Thai Boxer E27 Desk Lamp (Option A — 1:1 Photo Match)** — Monolithic single-plate print ($123.2 \times 123.0 \times 223.9\text{ mm}$): Flared pedestal with E27 housing + Voronoi mesh globe + photo-matched fighter with high-guard left glove, forward punch right fist, tousled wet fringe, and hollow optical light chimney beaming through eyes | Verified & Exported | Ready to slice (`.step`, `.3mf`, `.stl` in `exports/`, 4 views in `previews/`) |
| `2026-10-27` | [`models/mouthguard-box-pegasus/`](file:///<WORKSPACE_ROOT>/models/mouthguard-box-pegasus/) | **Mouthguard / Aligner Travel Case (Pegasus Muay Thai Edition)** — Flush dual-material lid ($0.60\text{ mm}$ Orange crest `#FF6A00` + Matte Black shell), scaled $42\text{ mm}$ emblem ($>3.35\text{ mm}$ hole clearance, zero collision), standalone Horse & Wings assets (`.svg`, `.stl`, `.step`), dual-sided bottom debossing ($0.60\text{ mm}$ outside base + inside basin floor), custom 3D-printable snap hinge pin (zero screws needed), non-mirrored Z-axis $180^\circ$ orientation, and interactive exploded HTML viewer (auto-spin strictly OFF by default) | Verified & Exported | Ready to slice (`.3mf`, `.stl`, `.step` in `exports/`, interactive HTML viewer & diagrams in `previews/`) |

  - **Flush Inlay & Engraving Depth Standard (`1.60 – 2.00 mm` / `8–10 Layers`):** Never make multi-color flush inlays, debossed recesses, or standalone decorative badges shallow (`0.60 mm` / 3 layers), as light filaments (Yellow, Gold, Orange, White) over dark shells (Black, Charcoal) suffer from optical color bleed-through and fragile geometry. Always design inlays, recesses, and standalone badges at **`1.60 – 2.00 mm` depth (`8–10 layers` at `0.20 mm`)** (e.g. `1.80 mm` on a `3.00 mm` lid leaving `1.20 mm` backing; `1.60 mm` on a `2.40 mm` floor leaving `0.80 mm` / 4 solid waterproof layers).
