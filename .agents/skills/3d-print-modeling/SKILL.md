---
name: 3d-print-modeling
description: >-
  Designs and generates parametric, FDM-print-optimized build123d (and FreeCAD-compatible
  OpenCascade B-Rep) 3D models tailored for the Bambu Lab P2S (256x256x256 mm). Exports
  native .step, .3mf, and .stl files for Bambu Studio arc-slicing. Enforces support-free
  geometry (<= 45 degree overhangs, teardrop holes, Z=0 bottom chamfers, sacrificial bridges),
  material-aware tolerances, and continuous self-learning from user feedback.
---

# 3D Print Modeling (`build123d` & FreeCAD B-Rep Edition for Bambu Lab P2S)

Based on the [3d-print-modeling](https://mcpmarket.com/tools/skills/3d-print-modeling) workflow, modernized from legacy OpenSCAD to **`build123d` (`0.13+` / OpenCascade `8.0`)** and **FreeCAD-compatible `.step` B-Rep CAD**, tailored for **Bambu Lab P2S (`256 × 256 × 256 mm`)**, **Zero-Support Design**, and **Continuous Self-Learning**.

---

## 1. Mandatory Pre-Design Checklist

Before writing any CAD code, ALWAYS perform these steps:

1. **Read Learned Preferences:**
   * Check `AGENTS.md` (Section 4 & 6) and [learned-preferences.md](../self-learning-cad/references/learned-preferences.md) so you apply all previously calibrated tolerances, chamfer preferences, and design habits learned from past conversations.
2. **Create Dedicated Model Folder:**
   * Every requested model **must** live in `<WORKSPACE_ROOT>\models\<model-name>\` with subdirectories `exports/` and `previews/`.
   * If modifying files from `<WORKSPACE_ROOT>\imports\`, treat `imports/` as **strictly read-only input**—never write generated files back into `imports/`.
3. **Select Print Orientation First (`Z = 0`):**
   * Decide which face sits on the build plate (`Z = 0`) to:
     * Maximize bed contact area (no brim/raft needed).
     * Place primary tensile/bending loads **along X/Y layer lines** (not pulling Z layers apart).
     * Eliminate overhangs `> 45°`.

---

## 2. Core FDM & Support-Free Engineering Rules (`build123d`)

Read [fdm-design-principles.md](./references/fdm-design-principles.md) and import [`p2s_cad_helpers.py`](./scripts/p2s_cad_helpers.py) in every model script. Every model must obey:

1. **P2S Build Envelope (`256 × 256 × 256 mm`):**
   * Keep single parts `<= 250 × 250 × 250 mm`. If a design exceeds this, split it into interlocking pieces using dovetails or alignment pins.
2. **Native `.step` + `.3mf` + `.stl` Exports:**
   * Always export **`.step`** (for true `G2`/`G3` circular arc slicing in Bambu Studio and direct editing in FreeCAD), **`.3mf`**, and **`.stl`**.
3. **Support-Free Angles (`<= 45°` Rule):**
   * Never create downward overhangs steeper than `45°` from vertical.
   * Support outward ledges using `45°` chamfered ramps or `loft()` gussets.
4. **Bottom Edges (`Z = 0`) Use Chamfers, Never Fillets:**
   * Apply `fillet()` to **vertical edges** (`part.edges().filter_by(Axis.Z)`) first, then apply a `0.8 mm – 1.5 mm` `45°` `chamfer()` to the bottom face perimeter (`part.faces().sort_by(Axis.Z)[0].edges()`) to eliminate elephant's foot and first-layer overhang curl.
5. **Horizontal Holes (`> 5 mm`) Use Teardrop or Diamond Ceilings:**
   * Use `teardrop_sketch(diameter)` from [`p2s_cad_helpers.py`](./scripts/p2s_cad_helpers.py) for any horizontal bore `> 5 mm` so the crown bridges cleanly at `45°` with zero sagging.
6. **Counterbored Screw Holes Facing Down (`Z = 0`):**
   * Never print a counterbore in mid-air. Use `sacrificial_counterbore()` (`0.20 mm` 1-layer bridge between counterbore ceiling and upper shaft hole).
7. **Nozzle-Multiple Wall Thicknesses (`0.4 mm` Nozzle):**
   * Light / cosmetic: `1.25 mm` (3 perimeters)
   * Standard functional: `1.65 mm – 2.0 mm` (4–5 perimeters)
   * Heavy-duty structural: `2.5 mm – 3.2 mm` (6+ perimeters)
8. **Stackable Modules with Integrated Locking Pins (Flush Planar Interface & Zero Sanding):**
   * When a stackable riser/module requires downward-pointing male alignment rods or pins that plug into a base below:
     * Design the receiving module with a flat top rim and cylindrical female sockets featuring a `1.4 mm` 45° lead-in chamfer.
     * Design the stackable module with a **flat planar landing shoulder** that seats 100% flush against the receiving rim (`0.0 mm` gap).
     * Orient the part **inverted (`180°` around X/Y so the top rim sits at `Z = 0`)** so the locking pins print pointing straight UP (`+Z`) directly on top of the column shoulders with **zero supports**.
     * **Never** add a full-width conical taper between the column and the pin unless the receiving socket has an identical matching counterbore. Use only a small root stress-relief fillet (`0.8 mm` 45°) that nests completely inside the socket's lead-in chamfer, and self-centering `1.2 mm` tip chamfers.
9. **`build123d` Builder Context Isolation:**
   * Never call a helper function that opens its own `with BuildPart():` inside an active `with BuildPart():` block (this resets the outer builder context). Construct helper `Part` solids outside the `with BuildPart():` block and combine them using explicit boolean operators (`+` union, `-` cut, `&` intersect).
10. **Multi-Color AMS Boolean Segmentation:**
   * Partition multi-color designs into non-overlapping `Part` solids using boolean intersection (`&`) and subtraction (`-`) against the master solid (e.g., 6 zones for Base Planters, 1 zone for Saucers, 4 zones for Risers), and export via `export_multicolor_multiplate_3mf()`.
11. **Monolithic Blind Pocket Tilted Print Orientation (`45°–47°` Un-Engraved Side Tilt):**
   * When a monolithic enclosure contains a wide, shallow internal pocket (such as a rotary shutter slot under a sloped hopper floor) whose `0°` roof would trap unremovable internal supports if printed flat, pre-orient the body tilted **`45°–47°` onto an un-engraved exterior wall** (with a `2.0 mm` bed-stabilization chamfer), flare internal pocket/slot roofs (`+5°..+17°`), and draft opposing inner walls (`5°`) so **100% of internal faces sit `> 45°` from horizontal** (`0.0 g` internal support). Configure `.3mf` project settings with `enable_support = 1`, `support_type = tree(auto)`, `support_on_build_plate_only = 1`, and `support_threshold_angle = 45` so tree supports touch **only** the plain exterior wall while keeping all branded/customizable faces vertical or skyward.
12. **Enclosed Mechanism 3D Kinematic Insertion Trajectory Audit & Dual-Lock Snap Handle:**
   * Split trapped internal sliders/shutters into a **slide-in internal member** (with a planar XY elastic C-jaw socket) + **snap-in keyed external handle** (pushed straight through the housing slot) + **coaxial locking pivot pin**. Run a continuous multi-step 3D B-Rep insertion trajectory check (`20+` 6-DOF poses from outside the housing to the seated position) asserting **`0.000000 mm³` boolean collision** at every step.

---

## 3. PNG-to-SVG Vectorization & CAD Importing Pipeline (`png_to_svg.py`)

When the user provides raster graphics (PNG, JPG, BMP) in `imports/` or requests logo/emblem embossing, engraving, or dual-material inlays:
1. **Transform Raster to Precision SVG:**
   ```powershell
   python ".agents\skills\3d-print-modeling\scripts\png_to_svg.py" "imports\sample_logo.png" -o "previews\sample_logo.svg" --width-mm 50 --center
   ```
   * **`--channel alpha`**: Isolates transparent background silhouettes (ideal for transparent logos).
   * **`--channel luminance`**: Automatically segments dark foreground graphics from light backgrounds (Otsu thresholding).
   * **`--colormode color`**: Generates full multi-color stacked SVG layers via Rust-accelerated `vtracer`.
   * **`--width-mm` / `--height-mm`**: Scales SVG geometry directly into physical CAD millimetres.
   * **`--center`**: Centers the geometry bounding box at `(0, 0)` for immediate alignment with CAD lids and faces.
2. **Direct Python CAD Integration (`build123d`):**
   ```python
   from png_to_svg import image_to_build123d_faces
   import build123d as b3d

   faces = image_to_build123d_faces("logo.png", target_width_mm=50.0, center_origin=True)
   logo_solid = b3d.extrude(faces[0], amount=1.2)  # 1.2mm 3D badge/inlay ready for booleans!
   ```

---


### Universal FDM Text & Inlay Orientation Law (Left-to-Right LTR vs Right-to-Left RTL Validation)
When engineering enclosures, faceplates, lids, or multi-color flush inlays:
- **Case A: Face-Down Bed Contact ($Z = 0.00\text{ mm}$):**
  * When a lid or panel is printed face-down flat on the textured PEI plate ($Z = 0$) for zero supports and a textured exterior finish, the surface contacting the bed **is the exterior face of the finished part**.
  * Looking at this exterior face (from underneath the bed via bottom camera $-Z$ looking up, or when holding the finished print) inverts the horizontal screen projection: $\text{screen}_x = -X_{\text{cad}}$.
  * **Mandatory Bed Mirror Rule ($X \to -X$):** In CAD, any 2D text, typography, or multi-color inlay placed on a $Z = 0$ face-down surface **MUST be mirrored across the X axis ($X_{\text{cad}} \to -X_{\text{cad}}$)**.
  * When mirrored in CAD, the finished exterior face yields $\text{screen}_x = -(-X_{\text{svg}}) = +X_{\text{svg}}$ (100% un-mirrored):
    - **Left-to-Right (LTR) Scripts:** Latin, Cyrillic, Greek (e.g. English `START`, `COFFEE`) read naturally from **Left to Right**.
    - **Right-to-Left (RTL) Scripts:** Semitic scripts like Hebrew and Arabic (e.g. Hebrew *שלום*, *קפה*, Arabic *سلام*) read naturally from **Right to Left**.
    - **Emblems & Graphics:** Asymmetrical icons, brand emblems, and direction arrows are **100% un-mirrored**.
  * Both the body cutout cavity and the positive inlay mesh MUST use the identical mirrored transform so they mate with $0.0000\text{ mm}$ zero drift.

- **Case B: Normal Face-Up Surfaces ($Z > 0.00\text{ mm}$):**
  * When a part is printed upright (e.g. bottom basin floor, top surface of an upright container, standalone badge on its flat back), the exterior face faces skyward ($+Z$).
  * Viewed directly from above ($+Z$), $\text{screen}_x = +X_{\text{cad}}$.
  * **No Mirroring ($X \to +X$):** In CAD, text and inlays on an upright face MUST NOT be mirrored. Both LTR and RTL scripts read naturally directly in CAD and slicer top views.

- **Case C: Angled & Sloped Overhangs ($0^\circ < \theta < 90^\circ$, e.g. $45^\circ$):**
  * Angled faces with a positive vertical normal component ($n_z > 0$) point upward and outward toward the viewer: **No Mirroring ($X \to +X$)**.

- **Language Independence Invariant:**
  * Script direction is handled automatically by the font shaping engine (HarfBuzz / FreeType BiDi).
  * Face-down on bed ALWAYS requires CAD $X \to -X$ so that BOTH LTR and RTL scripts read correctly on the finished exterior face. Face-up and angled overhangs NEVER require CAD $X \to -X$.

- **Standalone Artwork Badges:** Standalone decorative emblems/badges must be exported upright on their flat back at $Z = 0$ facing $+Z$ so the user can import, scale, and position them freely in Bambu Studio.

## 4. Modifying Imported Third-Party `.3mf` / `.stl` Models (`imports/` Workflow)

When the user provides downloaded MakerWorld / Printables files in `imports/<folder>/`:

1. **Read-Only `imports/` Rule:**
   * Never write modified meshes, `.3mf` files, or previews into `imports/`. Create a dedicated `models/<model-name>/` directory for all scripts, `exports/`, `previews/`, and `ASSEMBLY_GUIDE.md`.
2. **Feature-Preserving Mid-Section Dimension Adjustment (Piecewise-Linear Z-Map):**
   * When changing the height of a part that has mechanical features at the bottom (`Z <= Z_low`) and a snap-fit/lid rebate at the top (`Z >= Z_high`), **never scale uniformly or slice off the top**.
   * First split mesh faces across `Z = Z_low` and `Z = Z_high` (`trimesh.intersections.slice_faces_plane`), then apply a piecewise-linear mapping that leaves `Z <= Z_low` unchanged, linearly compresses/stretches `Z_low < Z < Z_high`, and shifts `Z >= Z_high` rigidly by `delta_H`.
3. **Inspect Both `.3mf` Objects and `.stl` Files:**
   * Always inspect every sub-object inside `3D/Objects/object_*.model` of an imported `.3mf` alongside any sibling `.stl` files—sometimes the `.3mf` contains a simplified/smooth sub-part where the `.stl` (or B-Rep rebuild) has full detail.

---

## 4. Execution, Verification & Mandatory Assembly Guide Pipeline

Always use the project's dedicated Python environment (`<WORKSPACE_ROOT>\.venv\Scripts\python.exe`):

1. **Write Parametric `build123d` Script:**
   * Place all user-tunable dimensions in a `@dataclass` config block at the top of `models/<model-name>/<model-name>.py`.
2. **Build, Export (`.step`/`.3mf`/`.stl`), & Render Previews:**
   ```powershell
   & "<WORKSPACE_ROOT>\.venv\Scripts\python.exe" "<WORKSPACE_ROOT>\.agents\skills\bambu-studio-ai\scripts\render_preview.py" "<WORKSPACE_ROOT>\models\<model-name>\<model-name>.py"
   ```
3. **Run Printability & Overhang Analysis:**
   ```powershell
   & "<WORKSPACE_ROOT>\.venv\Scripts\python.exe" "<WORKSPACE_ROOT>\.agents\skills\bambu-studio-ai\scripts\analyze.py" "<WORKSPACE_ROOT>\models\<model-name>\exports\<model-name>.stl"
   ```
4. **Inspect Previews & Self-Correct:**
   * View the generated PNG previews in `models/<model-name>/previews/` using `read_file`.
5. **Generate Mandatory Illustrated Assembly & Usage Guide (`ASSEMBLY_GUIDE.md`):**
   * Every model folder (`models/<model-name>/`) **must** include an `ASSEMBLY_GUIDE.md` and a rendered 3D cutaway/exploded diagram (`previews/*_assembly_guide.png`, see [`generate_assembly_guides.py`](./scripts/generate_assembly_guides.py)) explaining step-by-step how printed parts orient (including any `180°` flip from print orientation), how they assemble, recommended slicing & per-zone infill settings, filament material options, and how any household accessories (such as a cotton wick cloth/rope inside a 3D-printed arch straw) are installed. Always write `ASSEMBLY_GUIDE.md` in a **general, neutral, public-shareable product manual tone** with zero personal timelines or chat-based remarks.
6. **Update Registry & Self-Learning:**
   * Log the model in `AGENTS.md` (Section 7) and record any user fine-tuning feedback via `self-learning-cad`.
7. **360° Contour-Guided Hopper Funnels & Untwisted `Face(Wire.make_polygon)` Lofts:**
   * For granular hoppers with rotary quarter-circle shutters (`R_blade`), maintain an unbroken circular slider housing guide contour (`R_guide = R_blade + 0.85 mm`) and sweep Front, Left, and Back slopes continuously down to that contour with zero cut-off cliffs.
   * Keep internal blind pockets strictly beneath the sloped floor (`-2°` ceiling pitch + `4.5°` wall draft for `0.0 g` internal supports at `46°` tilt).
   * Always build multi-vertex ruled lofts from explicit `Face(Wire.make_polygon([Vector(x, y, z) ...]))` wires rather than `BuildSketch` `Polygon` objects so OpenCascade preserves 1:1 vertex correspondence without twisting.
8. **Mandatory Atomic Local Git Commit & Branch Hygiene:**
   * Every completed model, CAD revision, profile update, or skill change **must** be committed locally on `main` in the `3D-Automation` repository (`git add ... && git commit -m "feat(models): ..."`) before finishing the task (keep `3D-Automation` commits local—never push un-sanitized `3D-Automation` commits directly to `origin`).
   * If a temporary worktree/branch was used, run `.\scripts\worktree.ps1 finish <branch> main` so the worktree is merged, removed, and its temporary agent branch is deleted (never leave agent-created branches behind; never delete user-created branches).

  - **Flush Inlay & Engraving Depth Standard (`1.60 – 2.00 mm` / `8–10 Layers`):** Never make multi-color flush inlays, debossed recesses, or standalone decorative badges shallow (`0.60 mm` / 3 layers), as light filaments (Yellow, Gold, Orange, White) over dark shells (Black, Charcoal) suffer from optical color bleed-through and fragile geometry. Always design inlays, recesses, and standalone badges at **`1.60 – 2.00 mm` depth (`8–10 layers` at `0.20 mm`)** (e.g. `1.80 mm` on a `3.00 mm` lid leaving `1.20 mm` backing; `1.60 mm` on a `2.40 mm` floor leaving `0.80 mm` / 4 solid waterproof layers).
  - **UJOYBIO Elite PLA+ (`1 kg` Spool, `195–220 °C`) @ `0.24 mm` Layer Height Profile (Local Test Profile — Do Not Sync to `bambuforge` Yet):**
    * **Filament Settings:** First Layer Nozzle `210 °C`, Other Layers Nozzle `215 °C`, Textured PEI Bed `60 °C`, Max Volumetric Speed `15 mm³/s`, Diameter `1.75 mm`, Flow Ratio `0.98`.
    * **Process Speed Settings (`0.24 mm` Layer Height):** Initial Layer `35 mm/s`, Initial Layer Infill `75 mm/s`, Outer Wall `150 mm/s`, Inner Wall `250 mm/s`, Sparse Infill `270 mm/s`, Internal Solid Infill `200 mm/s`, Travel Speed `300 – 500 mm/s` (`400 mm/s`).
    * See full specification in [`../bambu-studio-ai/references/filament-profiles.md`](../bambu-studio-ai/references/filament-profiles.md) and programmatic helper `apply_ujoybio_elite_pla_plus_profile()` in [`scripts/p2s_cad_helpers.py`](./scripts/p2s_cad_helpers.py).
