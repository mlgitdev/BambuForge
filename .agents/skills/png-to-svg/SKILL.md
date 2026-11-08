---
name: png-to-svg
description: High-precision zero-bleed raster-to-SVG vectorization engine for 3D printing and CAD. Eliminates color bleeding via Option A (VTracer cutout mosaic) and guarantees straight mathematical lines between corners on geometric features (Magen David, text banners, polygonal shields) via Option B (OpenCV Douglas-Peucker contour tracer). Directly outputs CAD-ready SVGs with millimeter scaling and build123d Face imports.
---

# Zero-Bleed Raster-to-SVG Vectorization Skill (`png-to-svg`)

This skill converts raster artwork (logos, crests, emblems, silhouettes, and scans) into high-precision, production-grade SVGs and direct 3D CAD solids for Bambu Studio multi-material AMS printing and `build123d` extrusions.

---

## 1. Core Mandates & Problem Solvers

| Issue in Standard Vectorization | Root Cause | Solution Implemented |
| :--- | :--- | :--- |
| **Color Bleeding / Fuzzy Boundaries** | Naive `stacked` hierarchy creates overlapping background polygons where lower layers bleed through outer borders. | **Option A (VTracer Cutout):** Uses `hierarchical="cutout"`. All shapes are sliced into non-overlapping planar mosaic tiles (like jigsaw puzzle pieces). Zero background bleed. |
| **Wavy / Curved Geometric Lines** *(e.g. fine geometric vectors / Magen David, text)* | Bezier `spline` curve fitting smooths straight polygon edges into wavy arcs due to raster pixel anti-aliasing. | **Option B (OpenCV Douglas-Peucker):** Simplifies pixel-boundary contours into exact linear polygonal vertices (`M... L... Z`). Straight edges between corners are guaranteed 100% straight lines. |
| **Palette Explosion on Gradients** | Continuous lighting gradients / gold foils generate 700+ micro-patches in SVG. | **Adaptive Palette Quantization:** Pre-quantizes images into discrete color bins (e.g. `--max-colors 4`) matching Bambu Lab AMS filament slots. |
| **Hole Inversion in CAD (build123d)** | Arbitrary wire vertex ordering causes OpenCascade to treat internal holes (letter centers, star core) as inverted solids. | **Mathematical Wire Orientation:** Enforces CCW outer boundaries and CW inner holes with `fill-rule="evenodd"`. |

---

## 2. When to Use Option A vs. Option B

### Use Option A (`--engine vtracer --colormode color`) When:
- The artwork contains **3 or more distinct colors** (e.g. full-color multi-material emblem).
- The artwork contains primarily **organic, flowing curves** (animals, horses, leaves, smoke, waves).
- You want automatic color grouping into separate SVG layers.

### Use Option B (`--engine contour --straight-edges`) When:
- The artwork contains **sharp geometric shapes** (fine geometric vectors, hexagons, shields, crisp typography).
- You need **absolute zero bleeding** on 2-color / dual-material inlays (e.g. Matte Black base + Vibrant Orange crest).
- You need direct target color extraction (e.g. `--color-target gold` to isolate the foreground emblem from a dark shield background).

---

## 3. CLI Usage & Examples

The tool is located at:
`scripts/vectorize.py` (or `.agents/skills/png-to-svg/scripts/vectorize.py`).

### 1. Zero-Bleed Geometric Inlay (Geometric Inlay & Emblem Crest)
```powershell
& "..\..\.venv\Scripts\python.exe" .agents\skills\png-to-svg\scripts\vectorize.py `
  "imports/brand_crest.png" `
  -o "exports/brand_crest_zero_bleed.svg" `
  --color-target gold `
  --straight-edges `
  --epsilon 1.5 `
  --width-mm 60.0 `
  --center
```

### 2. Multi-Color Cutout Mosaic (Option A - Zero Overlap)
```powershell
& "..\..\.venv\Scripts\python.exe" .agents\skills\png-to-svg\scripts\vectorize.py `
  "imports/logo.png" `
  -o "exports/logo_cutout.svg" `
  --engine vtracer `
  --colormode color `
  --max-colors 4 `
  --filter-speckle 4 `
  --width-mm 80.0
```

### 3. Pure Monochrome Silhouette from Alpha Transparency
```powershell
& "..\..\.venv\Scripts\python.exe" .agents\skills\png-to-svg\scripts\vectorize.py `
  "imports/silhouette.png" `
  -o "exports/silhouette.svg" `
  --channel alpha `
  --engine contour `
  --width-mm 50.0 `
  --center
```

---

## 4. Direct Python / `build123d` CAD Bridge

Import raster images directly into 3D printable solids:

```python
import build123d as b3d
from pathlib import Path
import sys

# Import vectorizer engine
sys.path.append(str(Path(".agents/skills/png-to-svg/scripts").resolve()))
from vectorize import image_to_build123d_faces

# Vectorize and convert directly to 2D CAD faces (scaled to 60 mm width, centered at origin)
faces = image_to_build123d_faces(
    image_path="imports/brand_crest.png",
    target_width_mm=60.0,
    center_origin=True,
    engine="contour",
    color_target="gold",
    smooth_curves=False,  # Enforces straight lines on fine geometric vectors
    epsilon_px=1.5,
)

# Extrude faces into a 0.60 mm solid inlay for the lid (layers 1..3 on 0.20 mm standard)
inlay_solid = b3d.extrude(faces, amount=0.60)

# Export for Bambu Studio AMS inlay
b3d.export_stl(inlay_solid, "exports/brand_gold_crest_inlay.stl")
```

---

## 5. Parameter Tuning Guide

- **`--epsilon` (default `1.5`):** Douglas-Peucker contour tolerance in pixels.
  - `0.8 - 1.2`: High detail, slight pixel step preservation.
  - `1.5 - 2.0`: **Optimal for geometric logos & fine geometric vectors**; merges stair-stepped raster edges into pure straight lines.
  - `2.5+`: Aggressive simplification.
- **`--color-target` (`gold`, `black`, `white`, `orange`):** Isolates specific color ranges before contour tracing, bypassing background artifacts.
- **`--max-colors` (e.g. `4`):** Reduces gradient noise to discrete filament steps.
- **`--filter-speckle` (default `4`):** Cleans up floating single-pixel artifacts.
