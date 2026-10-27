#!/usr/bin/env python3
"""
PNG-to-SVG Vectorization & CAD Transformation Engine
===================================================
Compatibility wrapper that exposes the zero-bleed vectorization engine from the
`png-to-svg` skill.

Supports:
- Option A: Multi-color cutout mosaic (hierarchical="cutout", zero overlap bleed)
- Option B: Zero-bleed geometric contouring with Douglas-Peucker straight-edge enforcement (Star of David)
- Physical CAD unit scaling (--width-mm, --height-mm, --center)
- Direct build123d Face import (image_to_build123d_faces)
"""

import sys
from pathlib import Path

# Resolve path to dedicated png-to-svg skill engine
_CURRENT_DIR = Path(__file__).resolve().parent
_SKILL_SCRIPTS = _CURRENT_DIR.parent.parent / "png-to-svg" / "scripts"

if _SKILL_SCRIPTS.exists() and str(_SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SKILL_SCRIPTS))

from vectorize import (
    clean_vectorize_vtracer,
    binary_png_to_svg_contour,
    extract_color_mask,
    normalize_and_scale_svg,
    vectorize_raster,
    image_to_build123d_faces,
    main,
)

# Backwards compatibility alias
convert_image_to_svg = vectorize_raster

if __name__ == "__main__":
    main()
