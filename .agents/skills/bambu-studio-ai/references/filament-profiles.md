# Calibrated Filament & Process Profiles Catalog (Bambu Lab P2S — Local Workspace)

> **Catalog Policy (Specific Named Profiles, Never Forced Defaults):**
> This catalog stores **specific, named filament & process profiles** researched, tested, and tuned by the user for particular spools, layer heights, and projects.
> * **Never** treat any single custom profile below as a universal default across all models unless requested.
> * Whenever the user specifies a filament/profile name (e.g., *"use UJOYBIO Elite PLA+ 0.24mm"*), or when working on a project already configured with that profile, load the corresponding settings from this catalog.
> * Whenever the user shares new print feedback or researches a new filament spool with the agent, add or tune its entry here.
> * **Sync Status:** **PUBLIC (`BambuForge`)** — Synchronized with public repository alongside root `FILAMENTS.md` and `profiles/` catalog.

---

## 1. UJOYBIO Elite PLA+ (1kg Spool) — `0.24 mm` Layer Height Master Profile

This combined master profile pairs the **UJOYBIO Elite PLA+ (1kg Spool)** temperature range (`195–220 °C`) with the structural and volumetric flow requirements of a thicker **`0.24 mm` layer height** on the **Bambu Lab P2S (`0.4 mm` nozzle)**.

### A. 🧵 Filament Settings Profile
*(In Bambu Studio: click the pencil icon next to your selected filament)*

| Setting Category | Parameter | Recommended Value | Bambu Studio JSON Key | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Spool Spec** | **Spool Temp Range** | `195 – 220 °C` | `"nozzle_temperature_range_low": ["195"]`<br>`"nozzle_temperature_range_high": ["220"]` | Rated manufacturer range for UJOYBIO Elite PLA+ (1kg) |
| **Temperature** | **Nozzle (First Layer)** | **`210 °C`** | `"nozzle_temperature_initial_layer": ["210"]` | Optimal first-layer viscosity and bed tack |
| **Temperature** | **Nozzle (Other Layers)** | **`215 °C`** | `"nozzle_temperature": ["215"]` | Extra heat to fully melt thicker `0.24 mm` layers at speed |
| **Temperature** | **Bed (Textured PEI Plate)** | **`60 °C`** | `"textured_plate_temp": ["60"]`<br>`"textured_plate_temp_initial_layer": ["60"]` | Ensures zero warping and strong PEI grip |
| **Flow Limits** | **Max Volumetric Speed** | **`15 mm³/s`** | `"filament_max_volumetric_speed": ["15"]` | High-speed volumetric safety cap to prevent under-extrusion |
| **Flow Limits** | **Filament Diameter** | **`1.75 mm`** | `"filament_diameter": ["1.75"]` | Standard nominal diameter |
| **Flow Limits** | **Flow Ratio** | **`0.98`** | `"filament_flow_ratio": ["0.98"]` | Standard starting baseline |

---

### B. 🏎️ Process Speed & Layer Settings Profile (`0.24 mm` Layer Height)
*(In Bambu Studio: go to the **Process** panel on the left → **Quality** / **Speed** tab)*

| Print Feature | Recommended Value | Bambu Studio JSON Key | Engineering Rationale |
| :--- | :--- | :--- | :--- |
| **Layer Height** | **`0.24 mm`** | `"layer_height": "0.24"` | Balanced structural draft height (faster than `0.20 mm`, finer than `0.28 mm`) |
| **Initial Layer** | **`35 mm/s`** | `"initial_layer_speed": "35"` | Gives the thick line time to safely wet and stick to the Textured PEI bed |
| **Initial Layer Infill** | **`75 mm/s`** | `"initial_layer_infill_speed": "75"` | Fills the first layer quickly but safely |
| **Outer Wall** | **`150 mm/s`** | `"outer_wall_speed": "150"` | Caps visible walls to guarantee a consistent, glossy/uniform surface finish |
| **Inner Wall** | **`250 mm/s`** | `"inner_wall_speed": "250"` | Speeds up hidden structural perimeters |
| **Sparse Infill** | **`270 mm/s`** | `"sparse_infill_speed": "270"` | Maximizes high-speed printing inside the part (governed by the `15 mm³/s` volumetric cap) |
| **Internal Solid Infill** | **`200 mm/s`** | `"internal_solid_infill_speed": "200"` | Ensures strong, dense internal floors and ceilings |
| **Travel Speed** | **`300 – 500 mm/s`** | `"travel_speed": "400"` | Default printer capability for non-printing moves |

---

### C. CAD & Slicing Integration Notes for `0.24 mm` Layer Height
When generating models or `.3mf` files specifically targeted for the **UJOYBIO Elite PLA+ @ `0.24 mm`** profile:
1. **Sacrificial Bridges & Vertical Z-Steps:** Use `layer_height = 0.24 mm` for single-layer sacrificial counterbore bridges (`0.24 mm`) and design horizontal steps/inlay depths as clean multiples of `0.24 mm` (e.g., `1.68 mm` = 7 layers, `1.92 mm` = 8 layers).
2. **Programmatic `.3mf` Injection (`p2s_cad_helpers.py`):** Use `UJOYBIO_ELITE_PLA_PLUS_FILAMENT_OVERRIDES` and `UJOYBIO_ELITE_PLA_PLUS_024MM_PROCESS_OVERRIDES` in `.agents/skills/3d-print-modeling/scripts/p2s_cad_helpers.py`.

---

## 2. UJOYBIO / EjoyBio Elite PLA+ (1kg Spool) — `0.20 mm` Precision Master Profile

This profile tunes **UJOYBIO / EjoyBio Elite PLA+** for **high mechanical accuracy, tight snap/slide fits, razor-sharp debossed lettering, and smooth wall perimeters** on the Bambu Lab P2S (`0.4 mm` nozzle).

### A. 🏎️ Process Speed & Layer Settings Profile (`0.20 mm` Precision)
*(Process: `0.20mm Precision @BBL P2S - Ujoy PLA+`, Inherits: `0.20mm Standard @BBL P2S`, base_id: `GP155`)*

| Print Feature | Recommended Value | Bambu Studio JSON Key | Precision Rationale |
| :--- | :--- | :--- | :--- |
| **Layer Height** | **`0.20 mm`** | `"layer_height": "0.20"` | Standard precision layer height |
| **Initial Layer Height** | **`0.20 mm`** | `"initial_layer_print_height": "0.20"` | Flat, uniform first layer bed contact |
| **Wall Loops** | **`3` Walls** (`1.25 mm`) | `"wall_loops": "3"` | Increased from 2 for stiffness & dimensional stability |
| **Outer Wall Speed** | **`80 mm/s`** | `"outer_wall_speed": ["80", "nil", "nil"]` | Halved from `150 mm/s` to eliminate corner ringing, ghosting, and nozzle vibration |
| **Inner Wall Speed** | **`160 mm/s`** | `"inner_wall_speed": ["160", "nil", "nil"]` | Steady tracking for structural backing |
| **Sparse Infill Speed** | **`220 mm/s`** | `"sparse_infill_speed": ["220", "nil", "nil"]` | Reduced from `270 mm/s` to prevent bed vibration |
| **Internal Solid Infill Speed** | **`160 mm/s`** | `"internal_solid_infill_speed": ["160", "nil", "nil"]` | Smooth, flat internal floors |
| **Top Surface Speed** | **`80 mm/s`** | `"top_surface_speed": ["80", "nil", "nil"]` | Dense, glass-like top layer finish |
| **Initial Layer Speed** | **`30 mm/s`** | `"initial_layer_speed": ["30", "nil", "nil"]` | Maximizes initial layer bed adhesion on Textured PEI |
| **Initial Layer Infill** | **`60 mm/s`** | `"initial_layer_infill_speed": ["60", "nil", "nil"]` | Safe first-layer infill |
| **Outer Wall Acceleration** | **`3000 mm/s²`** | `"outer_wall_acceleration": ["3000", "nil", "nil"]` | Reduced from `5000` to eliminate corner bulging and overshoot |
| **Top Surface Acceleration** | **`2000 mm/s²`** | `"top_surface_acceleration": ["2000", "nil", "nil"]` | High-fidelity top cosmetic finish |
| **Precise Outer Wall** | **`1` (Enabled)** | `"precise_outer_wall": "1"` | Bambu Studio dedicated algorithm optimizing outer wall flow for tight fits |
| **Infill-Wall Overlap** | **`12%`** | `"infill_wall_overlap": "12%"` | Prevents infill telegraphing / bumps through the outer wall |
| **Seam Position & Gap** | **`Aligned` / `10%`** | `"seam_position": "aligned"`<br>`"seam_gap": "10%"` | Clean, tightly closed seam line |
| **Top / Bottom Shells** | **`5` Top / `4` Bottom** | `"top_shell_layers": "5"`<br>`"bottom_shell_layers": "4"` | Solid `1.0 mm` top skin / `0.8 mm` bottom skin |

---

## 3. UJOYBIO / EjoyBio Elite PLA+ (1kg Spool) — `0.16 mm` High Precision Master Profile

This profile tunes **UJOYBIO / EjoyBio Elite PLA+** for **ultra-fine miniature resolution, shallow overhangs, fine cursive script debossing, and thread fits** on the Bambu Lab P2S (`0.4 mm` nozzle).

### A. 🏎️ Process Speed & Layer Settings Profile (`0.16 mm` High Precision)
*(Process: `0.16mm Precision @BBL P2S - Ujoy PLA+`, Inherits: `0.16mm Standard @BBL P2S`, base_id: `GP209`)*

| Print Feature | Recommended Value | Bambu Studio JSON Key | Precision Rationale |
| :--- | :--- | :--- | :--- |
| **Layer Height** | **`0.16 mm`** | `"layer_height": "0.16"` | High-resolution vertical step slicing |
| **Initial Layer Height** | **`0.20 mm`** | `"initial_layer_print_height": "0.20"` | Standard `0.20 mm` first layer guarantees robust PEI bed adhesion |
| **Wall Loops** | **`3` Walls** (`1.25 mm`) | `"wall_loops": "3"` | Solid perimeter containment |
| **Outer Wall Speed** | **`60 mm/s`** | `"outer_wall_speed": ["60", "nil", "nil"]` | Bambu Studio High Quality standard — maximum precision for fine details & threads |
| **Inner Wall Speed** | **`120 mm/s`** | `"inner_wall_speed": ["120", "nil", "nil"]` | Controlled inner perimeter deposition |
| **Sparse Infill Speed** | **`200 mm/s`** | `"sparse_infill_speed": ["200", "nil", "nil"]` | High-accuracy infill tracking |
| **Internal Solid Infill Speed** | **`140 mm/s`** | `"internal_solid_infill_speed": ["140", "nil", "nil"]` | Smooth, dense intermediate floors |
| **Top Surface Speed** | **`60 mm/s`** | `"top_surface_speed": ["60", "nil", "nil"]` | Flawless, mirror-smooth top surface |
| **Initial Layer Speed** | **`30 mm/s`** | `"initial_layer_speed": ["30", "nil", "nil"]` | Slow, reliable bed tracking |
| **Initial Layer Infill** | **`50 mm/s`** | `"initial_layer_infill_speed": ["50", "nil", "nil"]` | Uniform first-layer infill |
| **Outer Wall Acceleration** | **`2000 mm/s²`** | `"outer_wall_acceleration": ["2000", "nil", "nil"]` | Eliminates resonance on tiny curves, debossed fonts & pins |
| **Top Surface Acceleration** | **`2000 mm/s²`** | `"top_surface_acceleration": ["2000", "nil", "nil"]` | Crisp edge transitions on top faces |
| **Precise Outer Wall** | **`1` (Enabled)** | `"precise_outer_wall": "1"` | Bambu Studio precision perimeter flow |
| **Infill-Wall Overlap** | **`10%`** | `"infill_wall_overlap": "10%"` | Tighter overlap for zero surface artifacts |
| **Seam Position & Gap** | **`Aligned` / `10%`** | `"seam_position": "aligned"`<br>`"seam_gap": "10%"` | Minimal seam visibility |
| **Top / Bottom Shells** | **`6` Top / `5` Bottom** | `"top_shell_layers": "6"`<br>`"bottom_shell_layers": "5"` | Solid `0.96 mm` top skin / `0.80 mm` bottom skin |

---

## 4. Installed Locations & Programmatic Usage

1. **Live Bambu Studio User Directory (Installed & Ready in Slicer Dropdown):**
   - `<USER_HOME>\AppData\Roaming\BambuStudio\user\944859351\process\0.20mm Precision @BBL P2S - Ujoy PLA+.json`
   - `<USER_HOME>\AppData\Roaming\BambuStudio\user\944859351\process\0.16mm Precision @BBL P2S - Ujoy PLA+.json`
   - `<USER_HOME>\AppData\Roaming\BambuStudio\user\944859351\process\0.24mm Standard @BBL P2S - Ujoy PLA+.json`
2. **Workspace Profiles Resource Directory:**
   - `.agents/skills/bambu-studio-ai/resources/profiles/ujoybio_pla_plus_020mm_precision_project_settings.json`
   - `.agents/skills/bambu-studio-ai/resources/profiles/ujoybio_pla_plus_016mm_precision_project_settings.json`
   - `.agents/skills/bambu-studio-ai/resources/profiles/ujoybio_pla_plus_024mm_project_settings.json`
3. **Python CAD Pipeline (`p2s_cad_helpers.py`):**
   ```python
   from p2s_cad_helpers import apply_ujoybio_elite_pla_plus_profile

   # Apply 0.20mm Precision
   f_cfg, p_cfg = apply_ujoybio_elite_pla_plus_profile(filament_dict, process_dict, layer_height="0.20")

   # Apply 0.16mm High Precision
   f_cfg, p_cfg = apply_ujoybio_elite_pla_plus_profile(filament_dict, process_dict, layer_height="0.16")
   ```
