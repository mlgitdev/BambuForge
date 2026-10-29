# FDM Design Principles & Reusable `build123d` Patterns (Support-Free P2S Library)

All models in `3D-Automation` use **`build123d`** (OpenCascade B-Rep kernel, compatible with **FreeCAD** and **Bambu Studio** native `.step` & `.3mf` workflows).

---

## 1. Standard Imports & Helper Usage

Every model script in `models/<model-name>/<model-name>.py` can import the workspace helper module:

```python
import sys
from dataclasses import dataclass
from pathlib import Path
from build123d import *

# Import P2S Support-Free CAD Helpers
SKILL_SCRIPTS = Path(__file__).resolve().parents[2] / ".agents" / "skills" / "3d-print-modeling" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
from p2s_cad_helpers import (
    P2STolerances,
    make_teardrop_cylinder,
    make_sacrificial_counterbore,
    export_and_preview,
)
```

---

## 2. Topological Fillet & Bottom Chamfer Order (Crucial B-Rep Rule)

In B-Rep CAD (`build123d` / FreeCAD):
1. **Never Nest `BuildPart()` Contexts Inside Another `BuildPart()`:** Build helper `Part` solids (`belt`, `cutter`, `ribs`) in their own standalone `BuildPart()` blocks first, then combine them algebraically (`part = base_body.part + belt - cutter`).
2. **Use `extrude()` for Vertical Prisms, Not Multi-Stage `loft()`:** Multi-stage `loft()` with vertical collinear segments can degenerate when chamfered. Always `extrude()` vertical walls and attach `45°` bands/rims via boolean `+`.
3. **First**, fillet the **vertical edges** (`Axis.Z`) so the outer perimeter forms a smooth tangent loop:
   ```python
   vert_edges = part.edges().filter_by(Axis.Z)
   part = fillet(vert_edges, radius=3.0)
   ```
4. **Second**, chamfer the **bottom face loop** (`Z = 0`) at `45°` (`0.8 – 1.6 mm`) so the chamfer sweeps smoothly around the rounded corners without failing or creating overhang curl:
   ```python
   bottom_face = part.faces().sort_by(Axis.Z)[0]
   part = chamfer(bottom_face.edges(), length=1.0)
   ```

---

## 3. Support-Free Horizontal Holes (`make_teardrop_cylinder`)

Horizontal cylinders `> 5 mm` sag at the top (`90°` tangent overhang). `make_teardrop_cylinder(radius, length, truncate=True)` creates a horizontal cutter with a `45°` pointed/truncated crown that prints cleanly with zero supports.

---

## 4. Support-Free Counterbored Screw Holes (`make_sacrificial_counterbore`)

When a socket-head cap screw counterbore faces the build plate (`Z = 0`), a standard counterbore leaves a floating annular shelf in mid-air. `make_sacrificial_counterbore()` leaves a `0.20 mm` (single-layer) sacrificial bridge between the counterbore roof and the upper clearance shaft so the P2S bridges straight across the hole without supports.

---

## 5. Bulky Model Speed Optimization (`0.28 mm` Draft vs. `0.20 mm` Standard)

For large, volumetric models (planters, pots, saucers, stacking extensions, storage crates):
1. **Clarify Intent Early:** Proactively ask the user if they prioritize fine surface resolution (`0.20 mm Standard`) or high print speed (`0.28 mm Extra Draft`, saving 35–45% print time).
2. **Dimension Multiples:** When designing vertical steps, rebates, and interlocking male/female pins, ensure Z-heights align cleanly with both `0.20 mm` and `0.28 mm` (e.g., `2.8 mm`, `5.6 mm`, `8.4 mm`, or multiples of `1.4 mm`).
3. **Bridge Sizing:** Parameterize sacrificial bridges to match layer height:
   ```python
   layer_height = 0.28 if speed_draft else 0.20
   bridge_thickness = layer_height
   ```
4. **Mechanical Advantage:** `0.28 mm` layers provide thicker extruded beads with greater thermal retention, yielding superior layer-to-layer weld strength, impact resistance, and water retention for hydroponic and planter applications.

---

## 6. Stackable Modular Alignment Joints (Flush Planar Interface & Zero Sanding)

When designing male alignment rods or stacking pins for stackable modular parts (e.g. extension risers, interlocking tiers):
1. **Flat Planar Shoulder Rule:** Male pins must protrude from a flat planar landing shoulder that meets the receiving module's top rim with 100% planar contact (`0.0 mm` gap).
2. **Never Add Full-Width Conical Transitions:** Do not taper the entire column down to the pin radius. In an inverted print orientation, a smaller pin on top of a larger column is already 100% supported by the column beneath it and requires zero supports. Adding a full-width cone causes severe mating collisions against flat rims.
3. **Root Stress-Relief Fillet:** Provide a small `0.8 mm` 45° chamfer/fillet at the pin root. This eliminates notch stress without colliding, because the receiving socket incorporates a `1.4 mm` lead-in chamfer.
4. **Clearance & Self-Centering:** Provide `0.30 mm` diametral clearance (e.g. `Ø6.20 mm` pin in `Ø6.50 mm` hole) and a `1.2 mm` 45° self-centering lead-in tip chamfer for effortless insertion.

---

## 7. PNG-to-SVG Vectorization for 3D Emblems & Bambu Modifiers (`png_to_svg.py`)

Raster images (PNG logos, silhouettes, scans) can be imported into CAD scripts using `png_to_svg.py`:
- **CLI Usage:** `python .agents/skills/3d-print-modeling/scripts/png_to_svg.py input.png -o output.svg --width-mm 50 --center`
- **Build123d Direct API:**
  ```python
  from png_to_svg import image_to_build123d_faces
  import build123d as b3d

  faces = image_to_build123d_faces("emblem.png", target_width_mm=50.0, center_origin=True)
  solid_inlay = b3d.extrude(faces[0], amount=0.8)
  ```
- **Mask Control:** Use `--channel alpha` for transparent PNGs, `--channel luminance` for dark/light figure extraction, and `--colormode color` for multi-color stacked vectorization.

---

## 8. Face-Down Printing & Inlay/Logo Chirality Principle (The Roll-Over Rule)

When designing enclosures, lids, covers, or multi-color flush inlays that print **face-down on the build plate (`Z = 0`)** (such as on a textured PEI sheet for zero supports and a premium surface finish):

### The Fundamental Physics & Spatial Mechanics:
1. **The Rigid-Body Roll-Over Invariant (Part & Logo Share 100% of Transforms):**
   - In CAD, an object is modeled right-side up in its functional assembled orientation (exterior face normal $\vec{n} = +Z$).
   - When preparing the part for 3D printing face-down at $Z = 0$, the part is **rolled over** (rotated $180^\circ$ around the X or Y axis).
   - Any 2D artwork (logo, text, emblem) applied to that exterior face MUST undergo the **EXACT SAME rigid-body rotation** as the part ($\\det(R) = +1$).
   - **NEVER negate a single axis ($X \to -X$ or $Y \to -Y$) independently.** Negating one axis creates an improper reflection (mirroring, $\\det(R) = -1$) rather than a physical 3D rotation, corrupting text direction and emblem chirality.

2. **The "Slicer Looking-Through-The-Back" Optical Illusion:**
   - In Bambu Studio or any slicer, the default 3D camera looks from $+Z$ downwards toward the bed plate.
   - When a lid is lying face-down on the bed at $Z = 0$, looking down from $+Z$ means looking at the **INSIDE CAVITY** (the back of the lid) towards the bed.
   - Looking through the rear of a face-down part at the bed-facing artwork naturally appears reversed/mirrored from $+Z$—exactly like looking at text on a storefront glass window from inside the shop!
   - An AI agent must **NEVER** "fix" this view by mirroring the text to look readable from $+Z$, because doing so guarantees that the 3D printer will lay down reversed text on the PEI plate, producing a backwards print.

3. **The Bottom-Camera Verification Invariant (Bed Contact View):**
   - The definitive mathematical proof that a face-down print is oriented correctly is to inspect the model with a virtual camera positioned at **$-Z$ looking UP (+Z) directly at the build plate** (or viewing the isolated 2D contact layer at $Z = 0$ from the outside).
   - In this Bottom View (looking at the face that touches the PEI plate):
     - Text MUST read normally from Left to Right.
     - Directional emblems (e.g. crest, shield, stallion) MUST face their intended directions.
     - Features must align with their mating geometry (e.g. hinge at $+Y$, latch at $-Y$).

4. **Standalone Artwork STLs Must Be Upright & Non-Mirrored:**
   - Standalone decorative STLs (e.g. `pegasus_horse_wings_only.stl`, standalone badges) meant for user placement in Bambu Studio must always be exported upright, sitting flat on their back at $Z = 0$ with the front detail facing $+Z$, reading normally from above (+Z).
