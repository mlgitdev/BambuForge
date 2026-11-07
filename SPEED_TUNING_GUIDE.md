# 3D Benchy Speed & Quality Tuning Guide — Bambu Lab P2S

> **Target Printer:** Bambu Lab P2S (`0.4 mm` Hardened Steel Nozzle)  
> **Slicer:** Bambu Studio / OrcaSlicer  
> **Filaments Covered:** UJOYBIO Elite PLA+, Kingroon PLA Basic, Kingroon PLA Matte, Inslogic Tri-Color Silk PLA, Kingroon Silk PLA.  
> **Purpose:** Progressive speed calibration matrix with interactive test logging columns for post-print evaluation, failure diagnosis, and permanent profile optimization.

---

## 1. Physical Speed Governors & Safety Rules

Before increasing speeds, keep these 3 inviolable rules in mind:
1. **Never Touch the First Layer:** Keep Initial Layer Speed at `50 mm/s`, Infill at `105 mm/s`, Bed at `60 °C`, and Fan `OFF` for layers 1–3.
2. **Initial Layer Nozzle Temp (Prime Line Snap):** Set Initial Layer Nozzle Temp to **`202 – 205 °C`** (even if other layers run at `215 – 220 °C`). This prevents the prime line from dragging an elastic ooze string across the plate.
3. **The Volumetric Flow Ceiling ($V_{max}$):**
   $$\text{Actual Linear Speed (mm/s)} = \min\left(\text{Target Speed}, \frac{V_{max}}{\text{Layer Height} \times \text{Line Width}}\right)$$
   If $V_{max} = 15\text{ mm}^3/\text{s}$, at `0.20 mm` height and `0.42 mm` width, your maximum physical speed is **`178.5 mm/s`**. To print infill at `270 mm/s`, you must ensure $V_{max} \ge 23\text{ mm}^3/\text{s}$ and increase nozzle temperature so the hotend can melt plastic fast enough.

---

## 2. Progressive Benchy Speed-Tuning Matrix (With Test Note Columns)

Use this table to record settings and results as you dial in your printer.

| Tuning Parameter | Stage 1: Quality Baseline (Precision) | Stage 2: Balanced Sport (Fast Functional) | Stage 3: Ludicrous (Max Flow Limit) | Test 1 Notes & Settings | Test 2 Notes & Settings | Test 3 Notes & Settings | Final Dialed-In Profile |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Layer Height** | `0.08 mm` / `0.12 mm` / `0.16 mm` | `0.20 mm` / `0.24 mm` | `0.24 mm` / `0.28 mm` | | | | |
| **Initial Layer Height** | `0.20 mm` | `0.20 mm` | `0.20 mm` / `0.24 mm` | | | | |
| **Outer Wall Speed** | `60 mm/s` (Silk: `40 mm/s`) | `90 – 100 mm/s` (Silk: `50 mm/s`) | `120 – 140 mm/s` (Silk: N/A) | | | | |
| **Inner Wall Speed** | `120 mm/s` | `180 – 200 mm/s` | `240 – 260 mm/s` | | | | |
| **Sparse Infill Speed** | `180 mm/s` | `250 – 270 mm/s` | `300 – 330 mm/s` | | | | |
| **Internal Solid Infill** | `150 mm/s` | `200 – 220 mm/s` | `250 – 270 mm/s` | | | | |
| **Top Surface Speed** | `70 – 80 mm/s` | `90 – 100 mm/s` | `120 mm/s` | | | | |
| **Outer Wall Accel** | `2,000 mm/s²` | `3,000 mm/s²` | `4,000 mm/s²` | | | | |
| **Normal Accel** | `5,000 mm/s²` | `8,000 mm/s²` | `10,000 mm/s²` | | | | |
| **Nozzle Temp (1st Layer)** | `202 – 205 °C` | `204 – 206 °C` | `208 – 210 °C` | | | | |
| **Nozzle Temp (Other Layers)**| `204 – 208 °C` | `215 – 218 °C` | `222 – 228 °C` | | | | |
| **Bed Temp (1st / Others)** | `60 °C` / `55 °C` | `60 °C` / `55 °C` | `60 °C` / `55 °C` | | | | |
| **Max Volumetric Speed ($V_{max}$)**| `12 – 14 mm³/s` | `16 – 18 mm³/s` | `20 – 24 mm³/s` | | | | |
| **Observed Benchy Print Time**| `~28 – 35 min` | `~18 – 22 min` | `~13 – 16 min` | | | | |
| **Surface Finish (Gloss/Matte)**| Glossy / Uniform | Smooth satin | Matte patches / Ringing? | | | | |
| **Bow Overhang (60° Quality)** | Perfect, no sag | Clean, minor texture | Sagging or curling? | | | | |
| **Cabin Ceiling Bridge** | Zero droop | Flat, 1–2 loose strands | Drooping or gaps? | | | | |
| **Stern Text Legibility** | Sharp, crisp | Readable | Smudged or blurred? | | | | |
| **Chimney & Mast Rigidity** | Strong, solid | Strong | Delamination or brittle? | | | | |
| **Prime Line Whisker Result** | Clean snap (no hair) | Clean snap | Clean snap | | | | |

---

## 3. Dedicated Process Profile Matrix (Installed in Bambu Studio)

You can select any of the **30 custom-calibrated process profiles** directly from Bambu Studio's **Process** dropdown. They follow the naming pattern:
`"<layer_height> <Brand> <Type> @BBL P2S"`

| Layer Height | UjoyBio PLA Plus | Kingroon PLA Basic | Kingroon PLA Matte | Inslogic Tri-Color Silk | Kingroon Silk PLA |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0.08 mm** | `0.08mm UjoyBio PLA Plus @BBL P2S` | `0.08mm Kingroon PLA Basic @BBL P2S` | `0.08mm Kingroon PLA Matte @BBL P2S` | `0.08mm Inslogic Tri-Color Silk PLA @BBL P2S` | `0.08mm Kingroon Silk PLA @BBL P2S` |
| **0.12 mm** | `0.12mm UjoyBio PLA Plus @BBL P2S` | `0.12mm Kingroon PLA Basic @BBL P2S` | `0.12mm Kingroon PLA Matte @BBL P2S` | `0.12mm Inslogic Tri-Color Silk PLA @BBL P2S` | `0.12mm Kingroon Silk PLA @BBL P2S` |
| **0.16 mm** | `0.16mm UjoyBio PLA Plus @BBL P2S` | `0.16mm Kingroon PLA Basic @BBL P2S` | `0.16mm Kingroon PLA Matte @BBL P2S` | `0.16mm Inslogic Tri-Color Silk PLA @BBL P2S` | `0.16mm Kingroon Silk PLA @BBL P2S` |
| **0.20 mm** | `0.20mm UjoyBio PLA Plus @BBL P2S` | `0.20mm Kingroon PLA Basic @BBL P2S` | `0.20mm Kingroon PLA Matte @BBL P2S` | `0.20mm Inslogic Tri-Color Silk PLA @BBL P2S` | `0.20mm Kingroon Silk PLA @BBL P2S` |
| **0.24 mm** | `0.24mm UjoyBio PLA Plus @BBL P2S` | `0.24mm Kingroon PLA Basic @BBL P2S` | `0.24mm Kingroon PLA Matte @BBL P2S` | `0.24mm Inslogic Tri-Color Silk PLA @BBL P2S` | `0.24mm Kingroon Silk PLA @BBL P2S` |
| **0.28 mm** | `0.28mm UjoyBio PLA Plus @BBL P2S` | `0.28mm Kingroon PLA Basic @BBL P2S` | `0.28mm Kingroon PLA Matte @BBL P2S` | `0.28mm Inslogic Tri-Color Silk PLA @BBL P2S` | `0.28mm Kingroon Silk PLA @BBL P2S` |

---

## 4. Filament-Specific Master Reference Cards

### Card A: UJOYBIO Elite PLA+ (Hyper PLA+ / Toughened Pro)
* **Optimal Flow Sweet Spot:** `16 – 18 mm³/s`
* **Characteristics:** High impact resistance, smooth layer blending, fast melting.
* **Speed Recommendation:**
  * **0.16 mm Precision:** Outer wall `60 mm/s`, Infill `180 mm/s`, Temp `205 °C` (prevents oozing/stringing).
  * **0.20 mm Standard:** Outer wall `80 mm/s`, Infill `250 mm/s`, Temp `212 °C`.
  * **0.24 mm Speed:** Outer wall `100 mm/s`, Infill `270 mm/s`, Temp `218 °C`.
  * **0.28 mm Extra Draft:** Outer wall `110 mm/s`, Infill `220 mm/s`, Temp `220 °C`.

### Card B: Kingroon PLA Basic
* **Optimal Flow Sweet Spot:** `14 – 16 mm³/s`
* **Characteristics:** Standard reliable rapid prototyping PLA.
* **Speed Recommendation:**
  * Outer wall: `80 – 100 mm/s`
  * Infill: `220 – 250 mm/s`
  * Nozzle temp: `210 – 220 °C`
  * Bed temp: `60 °C` / `55 °C`

### Card C: Kingroon PLA Matte
* **Optimal Flow Sweet Spot:** `12 – 14 mm³/s`
* **Characteristics:** Matte additives hide layer lines naturally, but have lower interlayer shear strength.
* **Speed Recommendation:**
  * Do not exceed `14 mm³/s` flow.
  * Outer wall: `70 – 80 mm/s`
  * Infill: `180 – 200 mm/s`
  * Nozzle temp: `210 – 215 °C`

### Card D: Inslogic Tri-Color Silk PLA
* **Optimal Flow Sweet Spot:** `10 – 12 mm³/s` *(for mirror sheen)*, `14 mm³/s` *(structural)*
* **The Silk Golden Rule:** **Speed dictates reflectivity.** Faster printing cools into a dull matte plastic; slow printing yields deep metallic luster.
* **Speed Recommendation:**
  * **Outer Wall:** Strictly **`40 – 50 mm/s`** across ALL layer heights.
  * **Inner Wall:** `120 – 150 mm/s`
  * **Infill:** `180 – 200 mm/s`
  * **Nozzle Temp:** `215 – 225 °C` (higher temp keeps luster during internal high speeds).
  * **Bed Temp:** `55 – 60 °C`

### Card E: Kingroon Silk PLA
* **Optimal Flow Sweet Spot:** `10 – 12 mm³/s`
* **Speed Recommendation:**
  * **Outer Wall:** Strictly **`35 – 45 mm/s`**
  * **Inner Wall:** `100 – 120 mm/s`
  * **Infill:** `160 – 180 mm/s`
  * **Nozzle Temp:** `212 – 220 °C`
  * **Bed Temp:** `55 – 60 °C`

---

## 4. Benchy Diagnostic Defect & Correction Cheat Sheet

| Symptom on Benchy | Root Cause | Immediate Slicer Fix |
| :--- | :--- | :--- |
| **Ghosting / Ringing Waves** on hull near anchor hole | Excessive outer wall acceleration vibrating toolhead | Reduce **Outer Wall Acceleration** from `4,000` to `2,500 – 3,000 mm/s²`. |
| **Loose Sagging Strands** under cabin roof bridge | Bridge speed too fast or cooling inadequate | Set **Bridge Speed** to `25 – 30 mm/s` and ensure Auxiliary/Part Fan is `100%`. |
| **Curling / Upturned Edges** on bow overhang ($60^\circ$) | Plastic staying molten too long on shallow overhang | Under Speed -> Overhang Speed: set $50-75\%$ overhangs to `30 mm/s` and $75-100\%$ to `15 mm/s`. |
| **Prime Line Whisker** stretching to model brim | High nozzle temp causing ooze during initial travel | Set **Initial Layer Nozzle Temp** to `202 – 205 °C` (keep other layers at `215 °C`). |
| **Extruder Clicking / Under-extrusion** during infill | Volumetric flow limit exceeded by linear speed demand | Increase nozzle temp by `5 °C` OR reduce Infill Speed by `30 mm/s` OR reduce $V_{max}$ to `16 mm³/s`. |
| **Silk Filament Turning Dull / Chalky** | Printing outer wall too fast | Lock Outer Wall Speed to `40 – 50 mm/s`. |
| **Brittle Layers / Snapping at Z seam** | Inadequate melt fusion at high speed | Raise nozzle temperature by `5 – 8 °C`. |
