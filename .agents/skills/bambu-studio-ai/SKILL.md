---
name: bambu-studio-ai
description: >-
  Local, zero-subscription adaptation of heyixuan2/bambu-studio-ai for Bambu Lab P2S.
  Converts natural language text/sketch requests directly into 3D printable B-Rep models
  via Antigravity + local build123d / FreeCAD Python API (no paid cloud text-to-3D APIs
  required), exports .step, .3mf, and .stl files, renders shaded multi-angle previews,
  runs 11-point printability and support-free overhang analysis, and hands off files
  to Bambu Studio.
---

# Bambu Studio AI (Local Zero-Subscription `build123d` & FreeCAD Edition)

Adapted from [`heyixuan2/bambu-studio-ai`](https://github.com/heyixuan2/bambu-studio-ai).
Instead of requiring paid third-party cloud Text-to-3D API subscriptions (like Meshy/Tripo), this skill uses **Antigravity + `build123d` (OpenCascade 8.0 B-Rep kernel, FreeCAD-compatible)** inside `<WORKSPACE_ROOT>\.venv` as your direct Text-to-3D engine, combined with local mesh printability verification, support-free overhang auditing, shaded multi-angle preview rendering, and **Bambu Studio** handoff.

---

## 1. Core Safety & Workflow Rules

1. **Zero Paid Subscriptions:** All Text-to-3D and parametric B-Rep generation runs 100% locally using `.venv\Scripts\python.exe` (`build123d`, `bd-warehouse`, `trimesh`, `lib3mf`).
2. **True B-Rep `.step` + `.3mf` + `.stl` Exports:** Every model exports a native `.step` solid (for arc-based slicing in Bambu Studio and direct editing in FreeCAD) alongside `.3mf` and `.stl`.
3. **Pre-Handoff Verification Mandate:** Every generated or edited model **must** pass `scripts/analyze.py` (checking P2S `256 × 256 × 256 mm` build volume, watertight manifold geometry, bed contact area at `Z = 0`, and `<= 45°` support-free overhang budget) before handoff to Bambu Studio.
4. **Dedicated Model Folder:** Every model lives in `<WORKSPACE_ROOT>\models\<model-name>\`.

---

## 2. Pipeline Scripts & CLI Commands

### A. Build, Export (`.step` / `.3mf` / `.stl`), & Shaded Preview (`scripts/render_preview.py`)
Executes a `build123d` Python CAD script `models/<model-name>/<model-name>.py` to generate `.step`, `.3mf`, and `.stl` inside `models/<model-name>/exports/` and renders 4 shaded CAD PNG views (`iso.png`, `front.png`, `right.png`, `top.png`) into `models/<model-name>/previews/`.

```powershell
& "<WORKSPACE_ROOT>\.venv\Scripts\python.exe" "<WORKSPACE_ROOT>\.agents\skills\bambu-studio-ai\scripts\render_preview.py" "<WORKSPACE_ROOT>\models\<model-name>\<model-name>.py"
```

### B. 11-Point Printability & Support-Free Overhang Analyzer (`scripts/analyze.py`)
Inspects an `.stl` or `.3mf` mesh against the **Bambu Lab P2S** profile:
* Bounding box vs. P2S `256 × 256 × 256 mm` volume.
* Watertight / Manifold verification.
* `Z = 0` bed adhesion contact footprint check.
* **Support-Free Overhang Audit:** Calculates the percentage and area of downward-facing triangles exceeding `45°` from vertical (excluding the `Z = 0` build plate base) and flags any region that would require supports in Bambu Studio.
* Saves a JSON/Markdown printability report in `models/<model-name>/previews/analysis_report.md`.

```powershell
& "<WORKSPACE_ROOT>\.venv\Scripts\python.exe" "<WORKSPACE_ROOT>\.agents\skills\bambu-studio-ai\scripts\analyze.py" "<WORKSPACE_ROOT>\models\<model-name>\exports\<model-name>.stl"
```

### C. Bambu Studio Handoff (`scripts/bambu_handoff.py`)
Locates the local **Bambu Studio** installation and launches it with the verified `.step`, `.3mf`, or `.stl` file (when `--open` is passed), or prints the exact ready-to-slice path.

```powershell
& "<WORKSPACE_ROOT>\.venv\Scripts\python.exe" "<WORKSPACE_ROOT>\.agents\skills\bambu-studio-ai\scripts\bambu_handoff.py" "<WORKSPACE_ROOT>\models\<model-name>\exports\<model-name>.step"
```

---

## 3. Multi-Plate & Multi-Color `.3mf` Packaging Invariants (Bambu Studio CLI)

Whenever packing multiple trays/modules and multi-color AMS sub-parts into a single `.3mf` file via `export_multicolor_multiplate_3mf()` in [`p2s_cad_helpers.py`](../3d-print-modeling/scripts/p2s_cad_helpers.py):

1. **Always Flatten JSON Profiles (`"inherits"`):**
   * Bambu Studio CLI (`--load-settings` / `--load-filaments`) does **not** resolve `"inherits"` automatically. Always recursively merge parent JSONs (`fdm_bbl_3dp_001_common.json`) via `_flatten_bambu_json()` so `printable_area` resolves to `256 × 256 mm`.
2. **Bambu Studio 2-Column Plate Grid (`307.2 mm` Stride):**
   * Bambu Studio arranges `256 × 256 mm` build plates in a **2-column grid** (`m_plate_cols = 2`):
     * **Plate 1 (`tray_idx = 1`):** `col = 0, row = 0` → center `(128.0, 128.0, 0.0)`
     * **Plate 2 (`tray_idx = 2`):** `col = 1, row = 0` → center `(435.2, 128.0, 0.0)`
     * **Plate 3 (`tray_idx = 3`):** `col = 0, row = 1` → center `(128.0, -179.2, 0.0)`
     * **General Formula:** `col = (tray_idx - 1) % 2`, `row = (tray_idx - 1) // 2`, `X = 128.0 + col * 307.2`, `Y = 128.0 - row * 307.2`.
   * Never place Plate 3 at `(742.4, 128.0)`—Bambu Studio assigns objects to plates by 2D bounding-box containment during `reload_all_objects()`.
3. **Multi-Filament Array Consistency:**
   * Never manually overwrite `filament_colour` in `Metadata/project_settings.config` with a 6-element list while leaving other per-filament arrays at length 1 (causes CLI crash `0xC0000005`). Instead, pass 6 flattened filament JSON files via `--load-filaments "f1.json;f2.json;...;f6.json"`.
4. **Mandatory CLI Round-Trip Verification:**
   * Always run a final `bambu-studio.exe --export-3mf verified.3mf stage1.3mf` pass (via Python `subprocess.run()` so execution waits for GUI-subsystem exit) to verify all plates populate (`reload_all_objects`) and to generate native OpenGL multi-color plate thumbnails (`Metadata/plate_1..N.png`).
5. **Descriptive Object & Plate Names in `Metadata/model_settings.config`:**
   * Especially when repackaging imported `.3mf`/`.stl` parts, always overwrite generic or foreign object names (`object_1.model`, `Ursprüngliches Modell`) with clear, descriptive English names (`<metadata key="name" value="Melitta_Bean_Hopper_Box_60mm"/>`) and name every build plate (`<metadata key="plater_name" value="Tray 1 - ..."/>`). Export both a **1-Plate `.3mf`** (all parts on Plate 1) and a **Multi-Tray `.3mf`** (each part on its own plate).
6. **3D Exploded & Cutaway Assembly Diagrams (`computed_zorder=False`):**
   * When rendering 3D exploded/cutaway assembly guides with Matplotlib `Axes3D`, always create subplots with `computed_zorder=False` (`fig.add_subplot(..., projection="3d", computed_zorder=False)`) and set `zorder=100` on `ax.text2D(...)` callout badges so 3D `Poly3DCollection` meshes (`zorder=1..6`) never occlude text labels.
7. **Interactive Exploded Multi-Part 3D HTML Viewer Standard (`scripts/generate_interactive_viewer.py`):**
   * Every multi-part model must generate an offline, standalone Three.js HTML viewer (`previews/<model-name>_viewer.html`) with:
     * **0% to 100% Exploded View Slider:** Smooth linear kinematic separation showing how components assemble and separate.
     * **Component Isolation Checkboxes:** Individual toggles with filament color swatches to view internal cavities and sub-parts.
     * **Camera Presets:** One-click presets (`Isometric`, `Top`, `Bottom`, `Front`, `Rear`, `Side/Interior`).
     * **Auto-Spin Strictly OFF by Default:** User retains full manual orbit/pan/zoom control without fighting turntable movement.
     * **Bambu Lab P2S Bed Cage:** Toggleable $256 \times 256 \times 256\text{ mm}$ build boundary.
8. **Mandatory 1:1 Preview-to-3MF Correlation Audit Invariant:**
   * Every model pipeline **must** execute `audit_3mf_correlation(project_3mf_path)` before presenting results to the user.
   * Prevents discrepancies between preview renders and slicer plate layouts:
     * **Explicit Plate Instancing:** Asserts every object in `3D/3dmodel.model` has a corresponding `<model_instance>` tag in `<plate>` inside `Metadata/model_settings.config` (prevents parts from disappearing in Bambu Studio).
     * **Collision & Clearance Verification:** Asserts $> 10\text{ mm}$ (typically $> 25\text{ mm}$) safety clearance between distinct plate items on the $256 \times 256\text{ mm}$ bed.
     * **Bed Contact & Coordinate Integrity:** Asserts that bed-printed parts touch $Z = 0.00\text{ mm}$ and share the identical orientation as the interactive viewer components. Include `<metadata name="Application">BambuStudio-02.06.00.51</metadata>` in `3D/3dmodel.model` so CLI round-trips preserve custom `> 25 mm` plate spacing without triggering auto-arrange.
9. **Tilted Exterior-Only Tree Support Packaging (`support_on_build_plate_only = 1`):**
   * When a model with an enclosed internal pocket cannot bridge flat at `0°` without internal supports, pre-orient the mesh tilted `45°–47°` onto an **un-engraved exterior wall** so all internal cavity faces exceed `45°` from horizontal (`0.0 g` internal support). Persist `"enable_support": "1"`, `"support_type": "tree(auto)"`, `"support_on_build_plate_only": "1"`, and `"support_threshold_angle": "45"` inside `Metadata/project_settings.config` (and `<metadata key="enable_support" value="0"/>` on flat companion parts) after the `bambu-studio.exe --export-3mf` CLI round-trip.

---


- **Face-Down Inlay & Logo Chirality Verification (Check 12):**
  When an enclosure lid or cover is placed face-down on the build plate (`Z = 0.00 mm`) for flush multi-color inlay printing:
  1. Inspect the model using a bottom camera view (`-Z` looking UP at the build plate).
  2. Confirm that exterior text reads normally from left to right and that directional graphics face their intended orientation on the bed contact plane.
  3. Recognize that looking down from `+Z` in Bambu Studio shows the inside cavity of the part, which naturally looks reversed through the back; never apply an axis inversion ($X \to -X$) to make it readable from `+Z`, which would cause it to print reversed on the PEI bed!

## 4. Visual CAD & 2D-to-3D Handoff (FreeCAD 1.1 & CADCraft)

* **FreeCAD 1.1 (`<USER_HOME>\AppData\Local\Programs\FreeCAD 1.1\bin\freecad.exe`):** Launch via `bambu_handoff.py --app freecad --open <file.step>` to inspect/edit multi-body B-Rep `.step` assemblies.
* **CADCraft (`C:\Program Files\CADCraft\cadcraft.exe` & `cadcraft-cli.exe`):**
  * **Headless `.scr` / `.dxf` Runner:** `cadcraft-cli.exe run -i input.dxf -o output.svg --script-file commands.scr`
  * **Live MCP Server:** `cadcraft-cli.exe mcp --launch` starts CADCraft and bridges JSON-RPC 2.0 MCP tool calls to the live GUI (`127.0.0.1:44915`).
  * **2D-to-3D Bridge:** Import `.dxf` / `.svg` profiles drafted in CADCraft into `build123d` (`import_svg` / `ezdxf`) and extrude/loft them into support-free 3D B-Rep solids.

  - **Flush Inlay & Engraving Depth Standard (`1.60 – 2.00 mm` / `8–10 Layers`):** Never make multi-color flush inlays, debossed recesses, or standalone decorative badges shallow (`0.60 mm` / 3 layers), as light filaments (Yellow, Gold, Orange, White) over dark shells (Black, Charcoal) suffer from optical color bleed-through and fragile geometry. Always design inlays, recesses, and standalone badges at **`1.60 – 2.00 mm` depth (`8–10 layers` at `0.20 mm`)** (e.g. `1.80 mm` on a `3.00 mm` lid leaving `1.20 mm` backing; `1.60 mm` on a `2.40 mm` floor leaving `0.80 mm` / 4 solid waterproof layers).

---

## 5. Specific Named Filament & Process Profiles Catalog (Local Workspace — Not Global Defaults)

* **Catalog Architecture:** Custom filament and process profiles are stored in [`references/filament-profiles.md`](./references/filament-profiles.md) and `.agents/skills/bambu-studio-ai/resources/profiles/` as **specific, named profiles** (never forced as global defaults across unrelated projects).
* When the user requests a specific filament profile by name, or provides an imported `.3mf` using it, apply that profile; when the user reports test results or researches a new filament type, add or refine its entry in [`references/filament-profiles.md`](./references/filament-profiles.md).

### Master Profile: **UJOYBIO Elite PLA+ (`1 kg` Spool, `195–220 °C`) @ `0.24 mm` Layer Height**

#### 🧵 Filament Settings Profile
| Setting Category | Parameter | Recommended Value |
| :--- | :--- | :--- |
| **Temperature** | **Nozzle (First Layer)** | **`210 °C`** |
| **Temperature** | **Nozzle (Other Layers)** | **`215 °C`** *(Extra heat for thick `0.24 mm` layers)* |
| **Temperature** | **Bed (Textured PEI Plate)** | **`60 °C`** *(Ensures zero warping)* |
| **Flow Limits** | **Max Volumetric Speed** | **`15 mm³/s`** *(High-speed safety cap)* |
| **Flow Limits** | **Filament Diameter** | **`1.75 mm`** |
| **Flow Limits** | **Flow Ratio** | **`0.98`** *(Standard generic starting point)* |

#### 🏎️ Process Speed Settings Profile (`0.24 mm` Layer Height)
| Print Feature | Recommended Speed | Why This Value? |
| :--- | :--- | :--- |
| **Initial Layer** | **`35 mm/s`** | Gives the thick line time to safely stick to the bed. |
| **Initial Layer Infill** | **`75 mm/s`** | Fills the first layer quickly but safely. |
| **Outer Wall** | **`150 mm/s`** | Caps visible walls to guarantee a beautiful surface finish. |
| **Inner Wall** | **`250 mm/s`** | Speeds up hidden structural walls. |
| **Sparse Infill** | **`270 mm/s`** | Maximizes high-speed printing inside the part. |
| **Internal Solid Infill** | **`200 mm/s`** | Ensures strong, dense internal floors/ceilings. |
| **Travel Speed** | **`300 – 500 mm/s`** | Default printer capability for non-printing moves. |
