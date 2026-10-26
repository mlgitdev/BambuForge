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

---

## 4. Visual CAD & 2D-to-3D Handoff (FreeCAD 1.1 & CADCraft)

* **FreeCAD 1.1 (`<USER_HOME>\AppData\Local\Programs\FreeCAD 1.1\bin\freecad.exe`):** Launch via `bambu_handoff.py --app freecad --open <file.step>` to inspect/edit multi-body B-Rep `.step` assemblies.
* **CADCraft (`C:\Program Files\CADCraft\cadcraft.exe` & `cadcraft-cli.exe`):**
  * **Headless `.scr` / `.dxf` Runner:** `cadcraft-cli.exe run -i input.dxf -o output.svg --script-file commands.scr`
  * **Live MCP Server:** `cadcraft-cli.exe mcp --launch` starts CADCraft and bridges JSON-RPC 2.0 MCP tool calls to the live GUI (`127.0.0.1:44915`).
  * **2D-to-3D Bridge:** Import `.dxf` / `.svg` profiles drafted in CADCraft into `build123d` (`import_svg` / `ezdxf`) and extrude/loft them into support-free 3D B-Rep solids.
