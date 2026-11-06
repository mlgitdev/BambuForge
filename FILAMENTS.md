# Calibrated 3D Printing Filament & Process Guide — Bambu Lab P2S

> **Target Printer:** Bambu Lab P2S (`0.4 mm` Hardened Steel Nozzle)  
> **Build Volume:** `256 × 256 × 256 mm`  
> **Print Surface:** Bambu Textured PEI Plate  
> **Profiles Location:** [`profiles/`](profiles/) and [`.agents/skills/bambu-studio-ai/resources/profiles/`](.agents/skills/bambu-studio-ai/resources/profiles/)

---

## 1. Quick Reference Master Catalog

| Filament Name | Material Type | Spool Rated Temp | First Layer Nozzle / Bed | Printing Nozzle / Bed | Calibrated Flow Ratio | Max Volumetric Speed | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **UJOYBIO Elite PLA+** *(EjoyBio)* | PLA+ / Pro (Toughened) | `195 – 220 °C` | **`210 °C` / `60 °C`** | **`204 – 215 °C` / `55 – 60 °C`** | **`0.98`** | **`15 mm³/s`** | Functional models, planters, Melitta dispenser, snap fits |
| **Kingroon PLA Basic** | Standard PLA | `190 – 220 °C` | **`220 °C` / `65 °C`** | **`225 °C` / `60 °C`** | **`0.98`** | **`15 mm³/s`** | General prototypes, fast decorative parts |
| **Kingroon PLA Matte** | Matte PLA | `190 – 220 °C` | **`215 °C` / `60 °C`** | **`220 °C` / `60 °C`** | **`0.98`** | **`14 mm³/s`** | Non-reflective satin finish prints |
| **Bambu PETG HF** | High-Flow PETG | `230 – 260 °C` | **`250 °C` / `70 °C`** | **`255 °C` / `70 °C`** | **`0.95`** | **`16 mm³/s`** | Watertight saucers, chemical & UV resistance, outdoor |
| **Bambu ASA** | ASA (UV Resistant) | `240 – 270 °C` | **`260 °C` / `90 °C`** | **`265 °C` / `90 °C`** | **`0.96`** | **`12 mm³/s`** | Direct outdoor sun, heat resistance (`> 95 °C`) |

---

## 2. In-Depth: UJOYBIO / EjoyBio Elite PLA+ (Hyper PLA+ / PLA Pro)

### A. Material Chemistry & Technical Specifications
* **Brand / Nomenclature:** UjoyBio (commonly searched or phonetically written as *EjoyBio* or *Ujoybio3d*).
* **Polymer Base:** Bio-sourced Poly-Lactic Acid (PLA) modified with core-shell acrylic impact elastomers.
* **Impact Resistance:** Up to **$2.5 – 3\times$ higher Charpy impact strength** than standard generic PLA, significantly reducing brittleness and snap-fit cracking.
* **Diameter & Accuracy:** `1.75 mm` with $\pm 0.02 - 0.03\text{ mm}$ automated laser-calibrated dimensional tolerance.
* **Specific Density:** `1.24 g/cm³`.
* **Volumetric Flow Capability:** Capable of sustained volumetric flow up to `15 - 18 mm³/s`, supporting print speeds up to `400 - 500 mm/s` on CoreXY machines like the Bambu Lab P2S.

---

### B. Calibrated Process Profiles for Bambu Lab P2S (`0.4 mm` Nozzle)

Depending on whether you are printing bulky structural objects (planters, bins) or precision functional parts (gears, shutters, debossed text, tight dowels), select the matching calibrated process profile:

| Process Profile Parameter | `0.24 mm Standard` *(Draft / Speed)* | `0.20 mm Precision` *(Tight Fits & Debossing)* | `0.16 mm High Precision` *(Miniature Resolution & Threads)* |
| :--- | :--- | :--- | :--- |
| **Bambu Studio Preset Name** | `0.24mm Standard @BBL P2S - Ujoy PLA+` | `0.20mm Precision @BBL P2S - Ujoy PLA+` | `0.16mm Precision @BBL P2S - Ujoy PLA+` |
| **Inherits From (System Base)** | `0.24mm Standard @BBL P2S` (`GP214`) | `0.20mm Standard @BBL P2S` (`GP155`) | `0.16mm Standard @BBL P2S` (`GP209`) |
| **Layer Height** | `0.24 mm` | **`0.20 mm`** | **`0.16 mm`** |
| **Initial Layer Print Height** | `0.24 mm` | **`0.20 mm`** | **`0.20 mm`** *(Guarantees robust PEI bed grip)* |
| **Nozzle Temp (First Layer)** | `210 °C` | **`210 °C`** | **`208 °C`** |
| **Nozzle Temp (Other Layers)** | `215 °C` | **`208 °C`** | **`204 °C`** |
| **Bed Temp (Textured PEI)** | `60 °C` | **`60 °C` initial / `55 °C` subsequent** | **`60 °C` initial / `55 °C` subsequent** |
| **Wall Loops** | `2` walls (`0.85 mm`) | **`3` walls** (`1.25 mm`) | **`3` walls** (`1.25 mm`) |
| **Top / Bottom Shells** | `4` Top / `3` Bottom | **`5` Top / `4` Bottom** (`1.0 mm` / `0.8 mm`) | **`6` Top / `5` Bottom** (`0.96 mm` / `0.80 mm`) |
| **Outer Wall Speed** | `150 mm/s` | **`80 mm/s`** *(Halved to eliminate corner ringing)* | **`60 mm/s`** *(Bambu Studio High Quality standard)* |
| **Inner Wall Speed** | `250 mm/s` | **`160 mm/s`** | **`120 mm/s`** |
| **Sparse Infill Speed** | `270 mm/s` | **`220 mm/s`** | **`200 mm/s`** |
| **Top Surface Speed** | `200 mm/s` | **`80 mm/s`** *(Glass-like top finish)* | **`60 mm/s`** *(Pristine cosmetic finish)* |
| **Initial Layer Speed** | `35 mm/s` | **`30 mm/s`** | **`30 mm/s`** |
| **Outer Wall Acceleration** | `5000 mm/s²` | **`3000 mm/s²`** *(Zero corner bulging)* | **`2000 mm/s²`** *(Razor-sharp edge transitions)* |
| **Top Surface Acceleration** | `2000 mm/s²` | **`2000 mm/s²`** | **`2000 mm/s²`** |
| **Precise Outer Wall** | `OFF` (`0`) | **`ON` (`1`)** *(Calibrated flow for tight tolerances)* | **`ON` (`1`)** *(Calibrated flow for tight tolerances)* |
| **Infill-Wall Overlap** | `15%` | **`12%`** *(Prevents infill telegraphing)* | **`10%`** *(Tighter overlap for zero surface artifacts)* |
| **Seam Position & Gap** | `Aligned` / `15%` | **`Aligned` / `10%`** | **`Aligned` / `10%`** |
| **Travel Speed** | `400 mm/s` | **`400 mm/s`** | **`400 mm/s`** |

---

### C. Why Nozzle & Bed Temperatures Are Lowered for Precision Prints
1. **Volumetric Melt Dynamics:**
   * At `0.24 mm` layer height and `150 mm/s`, the extruder pushes $\sim 16\text{ mm}^3/\text{s}$ of molten plastic. Higher nozzle heat (`215 °C`) is required to transfer thermal energy into the core of the filament.
   * At `0.16 mm` layer height and `60 mm/s`, the extruder only pushes $\sim 4\text{ mm}^3/\text{s}$. If the nozzle remains at `215 °C`, the filament is overcooked, leading to stringing, thermal oozing on non-print travel moves, and softened perimeter corners.
   * Lowering to **`204 – 208 °C`** freezes the extruded bead immediately upon exiting the nozzle, producing razor-sharp debossed letters and round circular holes.
2. **Bed Temperature Optimization:**
   * **`60 °C` on the Initial Layer:** Ensures the first layer adheres firmly to the Textured PEI plate with zero corner lifting.
   * **`55 °C` on Subsequent Layers:** Prevents heat creep into the lower layers of small precision parts, eliminating "elephant foot" thermal expansion at the base.

---

## 3. How Bambu Studio Profile Sync & Printer Presets Work

### Why Didn't New Presets Show Up Immediately in Bambu Studio or on the Printer?

There are three key mechanical and software reasons:

1. **Bambu Studio Preset Hot-Reload Limitation:**
   * Bambu Studio only scans and indexes disk profiles **when the application launches**.
   * If Bambu Studio is already open in the background, copying files directly to `AppData/Roaming/BambuStudio/user/<id>/` will **not** trigger a live GUI reload.
2. **Bambu Cloud Preset Sync (`sync_user_preset: true`):**
   * Bambu Studio features automatic Cloud Preset Synchronization. When cloud sync is active, Bambu Studio reconciles local files against your cloud account. Unregistered files dropped into disk folders while the app is running can be cleaned by the cloud sync reconciler.
3. **Physical Printer Screen vs. Bambu Studio Presets:**
   * The physical LCD screen on the Bambu Lab P2S and the AMS hardware **do not store custom vendor profiles**. The printer firmware only offers generic built-in choices (*Generic PLA*, *Generic PETG*, or RFID-detected *Bambu PLA*).
   * **You do not need to configure custom vendor names on the printer LCD!**
   * On the printer/AMS, select **"Generic PLA"**. When you slice and send the print job from Bambu Studio, Bambu Studio embeds the exact UJOYBIO Elite PLA+ temperatures (`210 °C / 208 °C`), bed temps (`60 °C / 55 °C`), flow ratio (`0.98`), and speeds directly into the G-code. The printer executes them with 100% fidelity.

---

## 4. How to Load and Permanently Sync Your New Presets in Bambu Studio

You have two simple ways to see and permanently save these presets:

### Method 1: The One-Click Starter Template (Recommended)
1. Open [`profiles/UjoyBio_Elite_PLA_Plus_Starter_Template.3mf`](profiles/UjoyBio_Elite_PLA_Plus_Starter_Template.3mf).
2. Bambu Studio opens with the **P2S printer**, the **UjoyBio Elite PLA+** filament profile, and the **0.20mm Precision** process settings pre-loaded.
3. Look at the **Filament** and **Process** dropdowns on the left panel:
   * Click the **Floppy Disk / Save icon** next to each dropdown.
   * Click **OK** to save.
4. **Result:** Bambu Studio saves both presets locally and immediately **syncs them to your Bambu Cloud account**, making them permanently available across all your projects and devices!

### Method 2: Manual Config Import via Bambu Studio Menu
1. In Bambu Studio, click **File → Import → Import Configs...**
2. Browse to the `profiles/` directory in the repository root.
3. Select any of the standalone preset files:
   * [`UjoyBio_Elite_PLA_Plus_Filament_P2S.json`](profiles/UjoyBio_Elite_PLA_Plus_Filament_P2S.json)
   * [`0.20mm_Precision_UjoyBio_PLA_Plus_P2S.json`](profiles/0.20mm_Precision_UjoyBio_PLA_Plus_P2S.json)
   * [`0.16mm_High_Precision_UjoyBio_PLA_Plus_P2S.json`](profiles/0.16mm_High_Precision_UjoyBio_PLA_Plus_P2S.json)
   * [`0.24mm_Standard_UjoyBio_PLA_Plus_P2S.json`](profiles/0.24mm_Standard_UjoyBio_PLA_Plus_P2S.json)
4. Click **Open** — Bambu Studio imports, registers, and syncs them automatically.

---

## 5. Python CAD Pipeline Integration (`p2s_cad_helpers.py`)

All three calibrated profiles are integrated into the automated workspace helper library at [`.agents/skills/3d-print-modeling/scripts/p2s_cad_helpers.py`](.agents/skills/3d-print-modeling/scripts/p2s_cad_helpers.py):

```python
from p2s_cad_helpers import apply_ujoybio_elite_pla_plus_profile

# 1. High-precision mechanical parts (snap fits, gears, debossed text)
f_cfg, p_cfg = apply_ujoybio_elite_pla_plus_profile(
    filament_dict, process_dict, layer_height="0.20"
)

# 2. Ultra-precision fine miniatures, cursive fonts & threads
f_cfg, p_cfg = apply_ujoybio_elite_pla_plus_profile(
    filament_dict, process_dict, layer_height="0.16"
)

# 3. Fast bulky structural prints (planters, saucers, large bins)
f_cfg, p_cfg = apply_ujoybio_elite_pla_plus_profile(
    filament_dict, process_dict, layer_height="0.24"
)
```
