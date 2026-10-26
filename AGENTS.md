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
├── .venv/                             # Dedicated Python 3.11 environment (build123d, trimesh, matplotlib)
├── .agents/
│   └── skills/
│       ├── 3d-print-modeling/         # Parametric build123d / FreeCAD FDM design skill + helper library
│       ├── bambu-studio-ai/           # Local zero-subscription CAD-to-Bambu Studio pipeline & analyzer
│       ├── self-learning-cad/         # Continuous preference capture, tolerance tuning & gap-closing skill
│       └── bambuforge-repo-sync/      # Automated bidirectional skill sync with public BambuForge repo
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

## 5. Self-Learning Loop & Continuous Adaptation

Whenever the user requests a fine-tuning adjustment, reports a print fit issue, or expresses a preference:
1. **Immediate Action:** Apply the change to the active model in `models/<model-name>/`.
2. **Gap Analysis & Persistence:** Update `.agents/skills/self-learning-cad/references/learned-preferences.md` and section **6. Learned User Preferences** below so the agent never repeats the same mistake and automatically applies the preference to all future models.
3. **Workflow Invocation:** Always consult `.agents/skills/3d-print-modeling/SKILL.md`, `.agents/skills/bambu-studio-ai/SKILL.md`, and `.agents/skills/self-learning-cad/SKILL.md` when designing, analyzing, or refining models.

---

## 6. Learned User Preferences (Auto-Updated)

* **Printer:** Bambu Lab P2S (`256 × 256 × 256 mm`).
* **CAD & Visual Toolchain:**
  * **`build123d` (`0.13.0` / OpenCascade `8.0`)** in `.venv` for programmatic B-Rep solid generation, multi-color zone boolean partitioning, and `.step`/`.3mf`/`.stl` export.
  * **FreeCAD 1.1 (`<USER_HOME>\AppData\Local\Programs\FreeCAD 1.1\bin\freecad.exe`):** Installed in user space for visual B-Rep `.step` / `.FCStd` CAD inspection and editing.
  * **CADCraft (`C:\Program Files\CADCraft\cadcraft.exe` & `cadcraft-cli.exe`):** Pure-Rust AutoCAD-style 2D/drafting tool with built-in headless CLI (`cadcraft-cli run`), `.scr` scripting, and native MCP server (`cadcraft-cli mcp --launch`) for 2D `.dxf` profile drafting that `build123d` (`ezdxf`) can extrude into 3D models.
  * **Bambu Studio (`C:\Program Files\Bambu Studio\bambu-studio.exe`):** Target slicer and multi-plate `.3mf` packager.
* **Slicer & Multi-Plate `.3mf` Workflow:** Always pack multi-module sets onto **separate build plates (trays)** inside a single `.3mf` project pre-configured for the **Bambu Lab P2S (`0.4 mm` nozzle, Supports = OFF)** using Bambu Studio's **2-column plate grid** (`Plate 1 = (128, 128)`, `Plate 2 = (435.2, 128)`, `Plate 3 = (128, -179.2)`), 6 flattened filament JSON profiles (`--load-filaments`), and a final `bambu-studio.exe --export-3mf` verification round-trip.
* **Operational Guardrail:** Never run slow, unmonitored `urllib` downloads for large multi-hundred-MB installers; always check installed binaries first or use fast CLI tools with explicit timeouts.
* **Multi-Color AMS Segmentation Rule:** Partition planter models into distinct, non-overlapping B-Rep color sub-parts inside the `.3mf` and `.step` assemblies:
  * **Base Planter (`6` Colors):** 3 structural wall layers + horizontal connecting strips/belts + top rim collar + 4 corner edge columns.
  * **Drip Saucer Tray (`1` Color):** Monolithic watertight saucer.
  * **Extension Riser (`4` Colors + Print-Orientation Optimization):** Lower wall layer + upper wall layer + connecting belt/rim + 4 corner columns with **integrated male locking rods**. Always orient the Extension Riser **inverted (`180°` on its flat top rim at `Z = 0`)** so the 4 integrated locking rods print pointing straight UP (`+Z`) with zero supports.
* **Project Organization & Read-Only `imports/` Rule:**
  * Every requested or modified model must reside in its own dedicated subdirectory under `models/<model-name>/` and be indexed in Section 7 below.
  * The `imports/` directory is **strictly read-only input** (for user-supplied MakerWorld / third-party `.3mf`, `.stl`, `.step` files). Never write output files back into `imports/`; always output modified models, previews, and `.3mf` packages to `models/<model-name>/exports/` and `previews/`.
  * When importing/modifying third-party `.3mf` or `.stl` assemblies, always assign clean, descriptive human-readable **object names** (`<metadata key="name" value="..."/>`) and **plate names** (`<metadata key="plater_name" value="..."/>`) inside `Metadata/model_settings.config`.
  * **Mandatory Illustrated Assembly & Usage Guide (`ASSEMBLY_GUIDE.md`):** Every model folder under `models/<model-name>/` must include an `ASSEMBLY_GUIDE.md` accompanied by rendered 3D exploded/cutaway assembly diagrams in `previews/` explaining step-by-step how all parts fit together, their recommended slicing settings (`wall_loops`, `sparse_infill_density`, `sparse_infill_pattern`, and `100%` infill modifiers), filament material guidance, and how any functional accessories (like wicking straws, cloths/cords, or shutters) are used. Write all documentation in a **clean, general, public-shareable product manual tone** (no personal references, user timelines, or chat-specific remarks).
* **Bulky Structural Model Speed Rule (`0.28 mm` Draft vs `0.20 mm` Standard):** For large or bulky functional objects (planters, saucers, storage bins, structural frames) where miniature resolution is not required, precision is secondary to throughput. Proactively ask the user their speed/quality preference during intake:
  - `0.20 mm Standard`: Fine surface finish.
  - `0.28 mm Extra Draft`: **~35–45% print time reduction** with stronger interlayer bonding. Ensure vertical dimensions, Z-chamfers, and sacrificial bridges match `0.28 mm` when selected. Document both print time estimates in `ASSEMBLY_GUIDE.md`.

---

## 7. Model Registry

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
