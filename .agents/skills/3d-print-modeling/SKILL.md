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
8. **Stackable Modules with Integrated Locking Pins (Print-Orientation Inversion):**
   * When a stackable riser/module requires downward-pointing male alignment rods or pins that plug into a base below, design its top rim completely flat and **orient the part inverted (`180°` around X/Y so the top rim sits at `Z = 0`)** with a `45°` conical transition under each pin. This allows the integrated locking rods to print pointing straight UP (`+Z`) with **zero supports**.
9. **`build123d` Builder Context Isolation:**
   * Never call a helper function that opens its own `with BuildPart():` inside an active `with BuildPart():` block (this resets the outer builder context). Construct helper `Part` solids outside the `with BuildPart():` block and combine them using explicit boolean operators (`+` union, `-` cut, `&` intersect).
10. **Multi-Color AMS Boolean Segmentation:**
   * Partition multi-color designs into non-overlapping `Part` solids using boolean intersection (`&`) and subtraction (`-`) against the master solid (e.g., 6 zones for Base Planters, 1 zone for Saucers, 4 zones for Risers), and export via `export_multicolor_multiplate_3mf()`.

---

## 3. Modifying Imported Third-Party `.3mf` / `.stl` Models (`imports/` Workflow)

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
