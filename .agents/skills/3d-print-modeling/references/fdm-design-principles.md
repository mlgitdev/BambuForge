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
