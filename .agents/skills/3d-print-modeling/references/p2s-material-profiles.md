# Bambu Lab P2S Material & Slicer Reference

## 1. Material Design Adjustments

| Material | Shrinkage / Hole Compensation | Max Safe Support-Free Overhang | Min Recommended Wall | Notes for CAD |
| :--- | :--- | :--- | :--- | :--- |
| **PLA / PLA Basic / Matte** | `+0.15 mm` radius on tight holes | `45°` (up to `50°` cosmetic) | `1.25 mm` (3 walls) | Stiff; make snap-fit cantilevers longer and thinner (`1.2–1.5 mm` thick) to avoid snapping. |
| **PETG / PETG-HF** | `+0.20 mm` radius on tight holes | `45°` strict (sticky bridging) | `1.65 mm` (4 walls) | More flexible and higher layer adhesion; great for snap-fits and compliant mechanisms. Avoid bridges `> 15 mm`. |
| **ABS / ASA** | `+0.25 mm` radius + `0.5%` scale | `45°` | `1.65–2.0 mm` | Always add `1.5 mm` bottom chamfers and avoid sharp internal corners to prevent thermal warping/cracking. |
| **TPU (95A)** | `+0.10 mm` (stretches to fit) | `40°` | `1.65 mm` | Design press-fits with `-0.1 mm` interference if you want a grippy friction boot/bumper. |

## 2. Standard Fastener Dimensions (Metric)

| Screw Size | Close Clearance Hole | Free Clearance Hole | Hex Nut Flat-to-Flat (`W`) | Hex Nut Height (`H`) | Socket Cap Head Dia |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **M2** | `2.25 mm` | `2.40 mm` | `4.15 mm` | `1.8 mm` | `4.0 mm` |
| **M2.5** | `2.75 mm` | `2.90 mm` | `5.15 mm` | `2.2 mm` | `4.7 mm` |
| **M3** | `3.25 mm` | `3.40 mm` | `5.65 mm` | `2.6 mm` | `5.8 mm` |
| **M4** | `4.30 mm` | `4.50 mm` | `7.15 mm` | `3.4 mm` | `7.4 mm` |
| **M5** | `5.30 mm` | `5.50 mm` | `8.15 mm` | `4.2 mm` | `8.9 mm` |
| **M6** | `6.35 mm` | `6.60 mm` | `10.20 mm` | `5.2 mm` | `10.4 mm` |

## 3. Layer Height & Speed Profiles (Standard vs. Draft for Bulky Prints)

| Slicing Profile | Layer Height | Outer/Inner Line Width | Print Time Factor | Recommended Application |
| :--- | :--- | :--- | :--- | :--- |
| **`0.20 mm Standard @BBL P2S`** | `0.20 mm` | `0.42 mm` / `0.45 mm` | Baseline (`100%`) | Detailed miniatures, tight sliding fits, threaded closures, and fine decorative textures. |
| **`0.28 mm Extra Draft @BBL P2S`** | `0.28 mm` | `0.42 mm` / `0.45 mm` | **~55–65% of baseline** (~35–45% faster) | Large, bulky structural objects (planters, saucers, stacking risers, bins, brackets). Higher thermal mass per layer yields superior interlayer adhesion and watertightness. |

### CAD Impact for `0.28 mm` Draft Printing:
1. **Sacrificial Bridges:** Size single-layer floating ceilings to match active profile (`0.28 mm` when drafting).
2. **Vertical Chamfers:** Bottom bed chamfers (`45°`) print cleanly at both `0.20 mm` and `0.28 mm`. Keep chamfer height `>= 1.12 mm` (at least 4 layers of `0.28 mm`).
3. **Wall Counts:** 3 walls at `0.28 mm` layer height (`~1.30 mm` thickness) provide excellent structural stiffness and watertight hydrostatic containment for planters.
