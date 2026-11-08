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

## 8. Universal FDM Text & Inlay Orientation Law (Face-Down Bed Contact vs Face-Up Upright Surfaces)

When designing enclosures, lids, covers, or multi-color flush inlays that print **face-down on the build plate (`Z = 0`)** (such as on a textured PEI sheet for zero supports and a premium surface finish) versus **upright face-up surfaces (`Z > 0`)**:

### The Fundamental Physics & Spatial Mechanics:

1. **Case A: Face-Down Bed Contact ($Z = 0.00\text{ mm}$):**
   - **Physical Reality:** When a part is printed face-down on the build plate (e.g. top lid, faceplate, cover), the surface contacting the bed **is the exterior face of the finished part**.
   - **Viewing Direction:** When inspecting the first layer in Bambu Studio (bottom camera looking up from $-Z$) or when picking up the finished part after removing it from the bed, the horizontal view axis is inverted:
     $$\text{screen}_x = -X_{\text{cad}}$$
   - **Mandatory Bed Mirror Rule ($X_{\text{cad}} \to -X_{\text{cad}}$):**
     * When applying a 2D sketch, SVG, or font text directly onto a $Z = 0$ face-down surface in CAD, **$X_{\text{cad}}$ MUST be mirrored ($X_{\text{cad}} = -X_{\text{unmirrored}}$)**.
     * *(Equivalently, if the part was originally modeled face-up at $+Z$ and then rolled over $180^\circ$ around the Y-axis into $Z = 0$, the physical 3D rotation automatically transforms $(x, y, z) \to (-x, y, -z)$, inverting X).*
   - **The Result on the Exterior Face (Screen & Print):**
     $$\text{screen}_x = -(-X_{\text{unmirrored}}) = +X_{\text{unmirrored}}$$
     - English / Latin text reads naturally **Left-to-Right** (`COFFEE`, `PEGASUS`).
     - Hebrew / Arabic script reads naturally **Right-to-Left** (*איגרוף תאילנדי*, *קפה*).
     - Emblems and symbols (Star of David, crests, logos) are **100% un-mirrored**.
   - **Shared Transform Invariant:** The negative body cavity and the positive multi-material inlay mesh MUST use the identical mirrored transform so they mate with $0.0000\text{ mm}$ zero drift.

2. **Case B: Face-Up Upright Surfaces ($Z > 0.00\text{ mm}$):**
   - **Physical Reality:** When a part is printed upright (e.g. bottom basin floor, top surface of an upright container, standalone badge on its flat back), the exterior face faces skyward ($+Z$).
   - **Viewing Direction:** Viewed directly from above ($+Z$), $\text{screen}_x = +X_{\text{cad}}$.
   - **No Mirroring ($X_{\text{cad}} \to +X_{\text{cad}}$):** In CAD, text and inlays on an upright face MUST NOT be mirrored.

3. **Language Independence Invariant (English vs Hebrew):**
   - Script direction (English L-to-R vs Hebrew R-to-L) is already encoded in SVG vector coordinates and font metrics.
   - **The rule does NOT change between languages:** Face-down on bed ALWAYS requires CAD $X \to -X$ so that BOTH English and Hebrew read correctly on the finished exterior face. Face-up NEVER requires CAD $X \to -X$.
   - Tested and verified in [`tests/test-text-inlay-orientation/`](../../../tests/test-text-inlay-orientation/README.md).

4. **Standalone Artwork STLs Must Be Upright & Non-Mirrored:**
   - Standalone decorative STLs (e.g. `pegasus_horse_wings_only.stl`, standalone badges) meant for user placement in Bambu Studio must always be exported upright, sitting flat on their back at $Z = 0$ with the front detail facing $+Z$, reading normally from above (+Z).

5. **Flush Inlay & Engraving Depth Standard (`1.60 – 2.00 mm` / `8–10 Layers`):**
   - Never make multi-color flush inlays, debossed recesses, or standalone decorative badges shallow (`0.60 mm` / 3 layers), as light filaments (Yellow, Gold, Orange, White) over dark shells (Black, Charcoal) suffer from optical color bleed-through and fragile geometry. Always design inlays, recesses, and standalone badges at **`1.60 – 2.00 mm` depth (`8–10 layers` at `0.20 mm`)** (e.g. `1.80 mm` on a `3.00 mm` lid leaving `1.20 mm` backing; `1.60 mm` on a `2.40 mm` floor leaving `0.80 mm` / 4 solid waterproof layers).

---
## 9. Monolithic Blind Pockets (`45°–47°` Tilt) & 3D Kinematic Insertion Audits

1. **Eliminating Trapped Internal Supports via `45°–47°` Un-Engraved Wall Tilt:**
   - A monolithic blind slot (`3–5 mm` high, `50–80 mm` wide) printed at `0°` creates an unbridgeable ceiling that slicers pack with unremovable support material.
   - Instead of reverting to loose glued ramps, tilt the housing **`45°–47°` onto an un-engraved exterior wall** (adding a `2.0 mm` flat stabilization chamfer at `Z_print = 0.00 mm`), flare the internal pocket roof (`+5°..+17°`), and draft opposing vertical inner walls (`5°`) so every internal ceiling sits at **`>= 47°–54°` from horizontal**.
   - Set `support_type = "tree(auto)"`, `support_on_build_plate_only = "1"`, and `support_threshold_angle = "45"` in `Metadata/project_settings.config`. Supports touch **only** the plain exterior bed-facing side; internal pockets receive `0.0 g` support, and branded/text walls face upward or vertical.

2. **Decoupled Dual-Lock Snap Handle & 6-DOF Insertion Trajectory Verification:**
   - Split enclosed rotary/sliding shutters into:
     1. **Internal Slide-In Blade:** Inserts through the open hopper/top aperture (`0.000000 mm³` collision along a continuous 6-DOF keyframe path) and carries a planar XY elastic C-jaw female socket (`0.35 mm`/side jaw deflection).
     2. **External Snap-In Handle:** Pushes straight through the exterior wall slot into the C-jaw socket with dual anti-rotation key flats (`Snap Lock #1`).
     3. **Coaxial Flush Snap Pivot Pin:** Passes through both the housing bore and a coaxial eye inside the handle tang (`Positive Pin Lock #2`), physically preventing separation under load.

3. **360° Contour-Guided Hopper Slopes & Untwisted Explicit Wire Lofts:**
   - Surround quarter-circle rotary shutters (`R_blade`) with a continuous circular slider guide contour (`R_guide = R_blade + 0.85 mm` clearance) and sweep Front, Left, and Back funnel slopes all the way down to `R_guide` without vertical cut-offs or protruding internal pivot bosses (snap the coaxial pivot pin inside an internal counterbore in the handle tang instead).
   - Keep the blind shutter pocket roof beneath the funnel floor (`-2.0°` slope toward the tilted bed side + `4.5°` wall draft on opposing pocket walls) so `46°` tilted printing yields `0.0 g` internal support.
   - Build multi-vertex ruled lofts directly via `Face(Wire.make_polygon([Vector(x, y, z) for ...]))` and `loft([f_bot, f_top], ruled=True)` to prevent `BuildSketch` vertex re-indexing twists.

