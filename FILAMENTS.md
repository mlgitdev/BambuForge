# Calibrated 3D Printing Filament & Process Guide — Bambu Lab P2S

> **Target Printer:** Bambu Lab P2S (`0.4 mm` Hardened Steel Nozzle)  
> **Build Volume:** `256 × 256 × 256 mm`  
> **Print Surface:** Bambu Textured PEI Plate  
> **Profiles Location:** [`profiles/`](profiles/) and [`.agents/skills/bambu-studio-ai/resources/profiles/`](.agents/skills/bambu-studio-ai/resources/profiles/)  
> **User Slicer Presets:** `%APPDATA%\BambuStudio\user\<user-id>\` (`filament/` and `process/`)

---

## 1. Master Filament Specification Catalog

| Filament Brand & Name | Category / Chemistry | Spool Rated Temp | 1st Layer Nozzle / Bed | Print Nozzle / Bed | Flow Ratio | Max Volumetric Flow ($V_{max}$) | Max Outer Wall Speed | Primary Application |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **UJOYBIO Elite PLA+** *(EjoyBio)* | Toughened PLA Pro (High-Speed) | `195 – 220 °C` | **`204 °C` / `60 °C`** | **`212 – 218 °C` / `55 °C`** | **`0.98`** | **`17.0 mm³/s`** | `80 – 120 mm/s` | Mechanical snap fits, planters, dispensers, high impact |
| **Kingroon PLA Basic** | Standard Rapid Prototyping PLA | `190 – 220 °C` | **`215 °C` / `60 °C`** | **`220 – 225 °C` / `55 °C`** | **`0.98`** | **`16.0 mm³/s`** | `100 – 140 mm/s` | General rapid prototypes, brackets, decorative parts |
| **Kingroon PLA Matte** | Mineral-Dulled Low-Gloss PLA | `190 – 220 °C` | **`208 °C` / `60 °C`** | **`215 – 220 °C` / `55 °C`** | **`0.98`** | **`13.5 mm³/s`** | `70 – 90 mm/s` | Zero-glare satin parts; hides layer lines naturally |
| **Inslogic Tri-Color Silk PLA**| Co-Extruded 3-Color High-Luster | `200 – 230 °C` | **`210 °C` / `60 °C`** | **`218 – 225 °C` / `55 °C`** | **`0.97`** | **`12.0 mm³/s`** | **`40 – 55 mm/s`** *(Strict)* | Living room showcase planters, architectural silk models |
| **Kingroon Silk PLA** | High-Luster Modified Silk PLA | `195 – 230 °C` | **`210 °C` / `60 °C`** | **`215 – 222 °C` / `55 °C`** | **`0.97`** | **`11.0 mm³/s`** | **`35 – 50 mm/s`** *(Strict)* | Metallic sheen figurines, cosmetic accents |
| **Bambu PETG HF** | High-Flow Polyethylene Terephthalate | `230 – 260 °C` | **`250 °C` / `70 °C`** | **`255 °C` / `70 °C`** | **`0.95`** | **`16.0 mm³/s`** | `80 – 120 mm/s` | Watertight irrigation saucers, chemical/UV resistance |
| **Bambu ASA** | Acrylonitrile Styrene Acrylate | `240 – 270 °C` | **`260 °C` / `90 °C`** | **`265 °C` / `90 °C`** | **`0.96`** | **`12.0 mm³/s`** | `60 – 90 mm/s` | Direct outdoor sun, high heat resistance (`> 95 °C`) |

---

## 2. Dedicated Process Profile Matrix (5 Filaments × 6 Layer Heights = 30 Profiles)

Every profile is formatted as **`<layer_height> <Brand> <Type> @BBL P2S`**, pre-configured with speeds, accelerations, and shell thicknesses calibrated for that specific filament chemistry and layer resolution:

| Bambu Studio Process Preset Name | Layer Height | Outer Wall Speed | Inner Wall Speed | Sparse Infill Speed | Solid Infill Speed | Top Surface Speed | Outer Wall Accel | Normal Accel | Top / Bot Shells | Target Application |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`0.08mm UjoyBio PLA Plus @BBL P2S`** | `0.08 mm` | `45 mm/s` | `90 mm/s` | `120 mm/s` | `100 mm/s` | `40 mm/s` | `1,500 mm/s²` | `4,500 mm/s²` | `9` / `7` | Miniature figurines, micro-threads |
| **`0.12mm UjoyBio PLA Plus @BBL P2S`** | `0.12 mm` | `60 mm/s` | `120 mm/s` | `160 mm/s` | `140 mm/s` | `60 mm/s` | `2,000 mm/s²` | `5,000 mm/s²` | `7` / `5` | Fine debossed text, crisp logos |
| **`0.16mm UjoyBio PLA Plus @BBL P2S`** | `0.16 mm` | `70 mm/s` | `140 mm/s` | `200 mm/s` | `170 mm/s` | `80 mm/s` | `2,500 mm/s²` | `6,000 mm/s²` | `6` / `5` | Snap pins, sliding joints, gears |
| **`0.20mm UjoyBio PLA Plus @BBL P2S`** | `0.20 mm` | `90 mm/s` | `180 mm/s` | `250 mm/s` | `200 mm/s` | `90 mm/s` | `3,000 mm/s²` | `7,000 mm/s²` | `5` / `4` | General functional prototypes |
| **`0.24mm UjoyBio PLA Plus @BBL P2S`** | `0.24 mm` | `110 mm/s` | `200 mm/s` | `270 mm/s` | `220 mm/s` | `100 mm/s` | `3,500 mm/s²` | `8,000 mm/s²` | `4` / `3` | Coffee dispenser body, housings |
| **`0.28mm UjoyBio PLA Plus @BBL P2S`** | `0.28 mm` | `120 mm/s` | `180 mm/s` | `220 mm/s` | `180 mm/s` | `100 mm/s` | `3,500 mm/s²` | `8,000 mm/s²` | `4` / `3` | **Max Throughput:** Bulky planters |
| **`0.08mm Kingroon PLA Basic @BBL P2S`**| `0.08 mm` | `50 mm/s` | `100 mm/s` | `130 mm/s` | `110 mm/s` | `40 mm/s` | `1,500 mm/s²` | `5,000 mm/s²` | `9` / `7` | High-detail rapid prototypes |
| **`0.12mm Kingroon PLA Basic @BBL P2S`**| `0.12 mm` | `65 mm/s` | `130 mm/s` | `170 mm/s` | `150 mm/s` | `60 mm/s` | `2,000 mm/s²` | `6,000 mm/s²` | `7` / `5` | Fine cosmetic brackets |
| **`0.16mm Kingroon PLA Basic @BBL P2S`**| `0.16 mm` | `80 mm/s` | `160 mm/s` | `220 mm/s` | `180 mm/s` | `80 mm/s` | `2,500 mm/s²` | `7,000 mm/s²` | `6` / `5` | Fast mechanical assemblies |
| **`0.20mm Kingroon PLA Basic @BBL P2S`**| `0.20 mm` | `100 mm/s` | `190 mm/s` | `260 mm/s` | `210 mm/s` | `90 mm/s` | `3,000 mm/s²` | `8,000 mm/s²` | `5` / `4` | Daily fast printing |
| **`0.24mm Kingroon PLA Basic @BBL P2S`**| `0.24 mm` | `125 mm/s` | `210 mm/s` | `270 mm/s` | `230 mm/s` | `100 mm/s` | `4,000 mm/s²` | `10,000 mm/s²`| `4` / `3` | Fast enclosures, organizer trays |
| **`0.28mm Kingroon PLA Basic @BBL P2S`**| `0.28 mm` | `120 mm/s` | `190 mm/s` | `230 mm/s` | `190 mm/s` | `100 mm/s` | `3,500 mm/s²` | `8,000 mm/s²` | `4` / `3` | **Max Throughput:** Storage bins |
| **`0.08mm Kingroon PLA Matte @BBL P2S`**| `0.08 mm` | `40 mm/s` | `80 mm/s` | `110 mm/s` | `95 mm/s` | `40 mm/s` | `1,200 mm/s²` | `4,000 mm/s²` | `9` / `7` | Satin miniatures, architectural models |
| **`0.12mm Kingroon PLA Matte @BBL P2S`**| `0.12 mm` | `50 mm/s` | `100 mm/s` | `140 mm/s` | `120 mm/s` | `60 mm/s` | `1,800 mm/s²` | `5,000 mm/s²` | `7` / `5` | Matte logos, faceplates |
| **`0.16mm Kingroon PLA Matte @BBL P2S`**| `0.16 mm` | `65 mm/s` | `130 mm/s` | `180 mm/s` | `150 mm/s` | `80 mm/s` | `2,200 mm/s²` | `6,000 mm/s²` | `6` / `5` | Low-reflection mechanical casings |
| **`0.20mm Kingroon PLA Matte @BBL P2S`**| `0.20 mm` | `80 mm/s` | `150 mm/s` | `210 mm/s` | `175 mm/s` | `90 mm/s` | `2,500 mm/s²` | `7,000 mm/s²` | `5` / `4` | Satin planters, desk accessories |
| **`0.24mm Kingroon PLA Matte @BBL P2S`**| `0.24 mm` | `90 mm/s` | `170 mm/s` | `230 mm/s` | `190 mm/s` | `100 mm/s` | `3,000 mm/s²` | `8,000 mm/s²` | `4` / `3` | Large matte planters (zero layer lines)|
| **`0.28mm Kingroon PLA Matte @BBL P2S`**| `0.28 mm` | `95 mm/s` | `160 mm/s` | `190 mm/s` | `160 mm/s` | `100 mm/s` | `3,000 mm/s²` | `7,000 mm/s²` | `4` / `3` | **Max Throughput:** Bulky matte pots |
| **`0.08mm Inslogic Tri-Color Silk PLA @BBL P2S`**| `0.08 mm`| `35 mm/s` | `80 mm/s` | `120 mm/s` | `100 mm/s` | `40 mm/s` | `1,200 mm/s²` | `4,000 mm/s²` | `9` / `7` | Mirror-gloss fine sculptures |
| **`0.12mm Inslogic Tri-Color Silk PLA @BBL P2S`**| `0.12 mm`| `40 mm/s` | `100 mm/s` | `150 mm/s` | `125 mm/s` | `60 mm/s` | `1,500 mm/s²` | `5,000 mm/s²` | `7` / `5` | High-sheen jewelry, ribbons |
| **`0.16mm Inslogic Tri-Color Silk PLA @BBL P2S`**| `0.16 mm`| `45 mm/s` | `120 mm/s` | `180 mm/s` | `150 mm/s` | `80 mm/s` | `1,800 mm/s²` | `6,000 mm/s²` | `6` / `5` | Decorative vases, emblems |
| **`0.20mm Inslogic Tri-Color Silk PLA @BBL P2S`**| `0.20 mm`| `50 mm/s` | `140 mm/s` | `200 mm/s` | `170 mm/s` | `90 mm/s` | `2,000 mm/s²` | `7,000 mm/s²` | `5` / `4` | Showcase living room planters |
| **`0.24mm Inslogic Tri-Color Silk PLA @BBL P2S`**| `0.24 mm`| `55 mm/s` | `160 mm/s` | `220 mm/s` | `180 mm/s` | `100 mm/s` | `2,500 mm/s²` | `7,000 mm/s²` | `4` / `3` | Helical-ribbed silk planters |
| **`0.28mm Inslogic Tri-Color Silk PLA @BBL P2S`**| `0.28 mm`| `55 mm/s` | `150 mm/s` | `190 mm/s` | `160 mm/s` | `100 mm/s` | `2,500 mm/s²` | `7,000 mm/s²` | `4` / `3` | Fast silk exterior shells |
| **`0.08mm Kingroon Silk PLA @BBL P2S`** | `0.08 mm` | `30 mm/s` | `70 mm/s` | `110 mm/s` | `95 mm/s` | `40 mm/s` | `1,200 mm/s²` | `4,000 mm/s²` | `9` / `7` | High-gloss metallic miniatures |
| **`0.12mm Kingroon Silk PLA @BBL P2S`** | `0.12 mm` | `35 mm/s` | `90 mm/s` | `140 mm/s` | `120 mm/s` | `60 mm/s` | `1,500 mm/s²` | `5,000 mm/s²` | `7` / `5` | Glossy filigree, badges |
| **`0.16mm Kingroon Silk PLA @BBL P2S`** | `0.16 mm` | `40 mm/s` | `110 mm/s` | `170 mm/s` | `140 mm/s` | `80 mm/s` | `1,800 mm/s²` | `6,000 mm/s²` | `6` / `5` | Silk trim, accent collars |
| **`0.20mm Kingroon Silk PLA @BBL P2S`** | `0.20 mm` | `45 mm/s` | `130 mm/s` | `190 mm/s` | `160 mm/s` | `90 mm/s` | `2,000 mm/s²` | `7,000 mm/s²` | `5` / `4` | Sculptural decorative planters |
| **`0.24mm Kingroon Silk PLA @BBL P2S`** | `0.24 mm` | `50 mm/s` | `150 mm/s` | `210 mm/s` | `175 mm/s` | `100 mm/s` | `2,200 mm/s²` | `7,000 mm/s²` | `4` / `3` | Fast silk basins and saucers |
| **`0.28mm Kingroon Silk PLA @BBL P2S`** | `0.28 mm` | `50 mm/s` | `140 mm/s` | `180 mm/s` | `150 mm/s` | `100 mm/s` | `2,200 mm/s²` | `7,000 mm/s²` | `4` / `3` | High-volume shiny planters |

---

## 3. Technical Verification: Does the Bambu Lab P2S Support `0.28 mm`?
**Yes, 100% natively.**
1. **The FDM Rule of Thumb:** The maximum reliable layer height for an FDM nozzle is **$70\% - 75\%$ of the orifice diameter**:
   $$0.4\text{ mm} \times 0.70 = \mathbf{0.28\text{ mm}}$$
2. **System Inheritance:** Bambu Studio contains `fdm_process_single_0.28.json` in its core engine (`C:\Program Files\Bambu Studio\resources\profiles\BBL\process\`). While Bambu Lab omitted an official factory preset label specifically for the P2S (preferring 0.24mm as conservative stock), creating `0.28mm <Brand> <Type> @BBL P2S` linking to `fdm_process_single_0.28` activates it flawlessly.
3. **Volumetric Safety Throttling:** At $0.28\text{ mm}$ layer height and $0.45\text{ mm}$ line width:
   $$\text{Flow at 200 mm/s} = 0.28 \times 0.45 \times 200 = \mathbf{25.2\text{ mm}^3/\text{s}}$$
   Because the P2S hotend melts PLA at $16–18\text{ mm}^3/\text{s}$, the linear speed is automatically capped by the slicer to $\sim 140–160\text{ mm/s}$. However, because each layer deposits **40% more plastic than 0.20 mm**, total print duration drops by **~35% to 45%**.

---

## 4. In-Depth Filament Science & Installed Presets

### A. UJOYBIO Elite PLA+ (Hyper PLA+ / PLA Pro)
* **Chemistry:** Poly-Lactic Acid modified with core-shell elastomeric impact modifiers.
* **Thermal Sweet Spot:**
  * **First Layer:** `204 °C` nozzle, `60 °C` bed. *(Prevents prime line ooze whisker while ensuring strong PEI grip).*
  * **High-Speed Layers:** `215 – 218 °C` nozzle, `55 °C` bed.
  * **Precision 0.16mm Layers:** `204 – 208 °C` nozzle to prevent micro-stringing and soft corners.
* **Volumetric Flow ($V_{max}$):** `17.0 mm³/s`.
* **Installed Filament Preset:** `UjoyBio Elite PLA+ 0.4`

### B. Kingroon PLA Basic
* **Chemistry:** High-purity standard PLA optimized for rapid prototyping.
* **Thermal Sweet Spot:**
  * **First Layer:** `215 °C` nozzle, `60 °C` bed.
  * **Other Layers:** `220 – 225 °C` nozzle, `55 °C` bed.
* **Volumetric Flow ($V_{max}$):** `16.0 mm³/s`.
* **Installed Filament Preset:** `Kingroon PLA Basic 0.4`

### C. Kingroon PLA Matte
* **Chemistry:** PLA compounded with microscopic mineral dulling particles to produce a zero-glare, non-reflective surface.
* **Flow & Strength Warning:** Matte additives increase melt shear viscosity. **Never set $V_{max} > 13.5\text{ mm}^3/\text{s}$**, or interlayer bonding drops significantly.
* **Thermal Sweet Spot:**
  * **First Layer:** `208 °C` nozzle, `60 °C` bed.
  * **Other Layers:** `215 – 220 °C` nozzle, `55 °C` bed.
* **Installed Filament Preset:** `Kingroon PLA Matte 0.4`

### D. Inslogic Tri-Color Silk PLA (Co-Extruded 3-Color)
* **Chemistry:** Multi-polymer blend containing acrylic or polyester gloss-enhancement agents. Co-extruded with 3 color ribbons running longitudinally.
* **The Silk Golden Rule: Speed Dictates Luster:**
  * **Outer Wall Speed:** **Must be locked to `40 – 55 mm/s`** across all layer heights. Fast printing (> 80 mm/s) quenches the polymer before specular reflection aligns, turning the surface into dull, milky plastic.
  * **Inner Walls & Infill:** Can be pushed to `150 – 200 mm/s` with nozzle temp at `220 – 225 °C`.
* **Thermal Sweet Spot:**
  * **50 – 100 mm/s (Maximum Luster):** `208 – 212 °C` nozzle, `60 °C` bed.
  * **100 – 200 mm/s (Internal High Speed):** `218 – 225 °C` nozzle, `55 °C` bed.
* **Volumetric Flow ($V_{max}$):** `12.0 mm³/s`.
* **Installed Filament Preset:** `Inslogic Tri-Color Silk PLA 0.4`

### E. Kingroon Silk PLA
* **Chemistry:** Single-color high-luster silk PLA.
* **Thermal Sweet Spot:**
  * **First Layer:** `210 °C` nozzle, `60 °C` bed.
  * **Other Layers:** `218 – 222 °C` nozzle, `55 °C` bed.
* **Outer Wall Speed:** Strictly `35 – 50 mm/s`.
* **Volumetric Flow ($V_{max}$):** `11.0 mm³/s`.
* **Installed Filament Preset:** `Kingroon Silk PLA 0.4`
