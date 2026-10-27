#!/usr/bin/env python3
"""
Zero-Bleed Raster-to-SVG Vectorization Engine (`png-to-svg`)
============================================================
Converts raster artwork (PNG, JPG, BMP, WEBP) into high-precision, CAD-ready
vector SVGs optimized for 3D modeling, Bambu Studio multi-material AMS embossing,
and build123d extrusions.

Key Capabilities:
1. Option A (Multi-Color Jigsaw Cutout):
   - Rust-accelerated VTracer with strict `hierarchical="cutout"`.
   - Eliminates overlapping layer bleeding: shapes fit together seamlessly like puzzle pieces.
   - Dual curve modes: `spline` for organic curves (animals, figures) or `polygon` for sharp corners.
   - Pre-quantization filter to prevent continuous lighting gradients from generating hundreds of color layers.

2. Option B (Zero-Bleed Geometric Pixel-Boundary Contours):
   - OpenCV contour hierarchy extraction (`RETR_TREE`) + Ramer-Douglas-Peucker simplification.
   - Straight-edge invariant: Straight lines between corners (e.g. Star of David / Magen David,
     shield polygons, banners) remain mathematical straight lines, with zero wavy bezier distortion.
   - Standalone `svgwrite` compound path export with `fill-rule="evenodd"` for exact hole subtraction.

3. Physical CAD Scaling & Placement:
   - Sets exact physical dimensions in millimeters (`--width-mm`, `--height-mm`).
   - Origin centering (`--center`) for direct CAD placement at (0, 0).
   - Direct build123d bridge (`image_to_build123d_faces`) for instant 3D extrusions.
"""

import os
import re
import sys
import math
import argparse
import tempfile
from pathlib import Path
from typing import Optional, Tuple, List, Union, Dict, Any

import numpy as np
from PIL import Image

try:
    import vtracer
    HAS_VTRACER = True
except ImportError:
    HAS_VTRACER = False

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    import svgwrite
    HAS_SVGWRITE = True
except ImportError:
    HAS_SVGWRITE = False


# ==============================================================================
# 1. OPTION A: Multi-Color Cutout VTracer Vectorizer
# ==============================================================================

def clean_vectorize_vtracer(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    colormode: str = "color",
    smooth_curves: bool = True,
    speckle_filter: int = 4,
    color_precision: int = 6,
    layer_difference: int = 16,
    corner_threshold: int = 60,
    length_threshold: float = 4.0,
    splice_threshold: int = 45,
    max_colors: Optional[int] = None,
) -> Path:
    """
    Converts raster image to SVG using strict 'cutout' hierarchy to completely
    eliminate background bleed between adjacent colors.
    """
    if not HAS_VTRACER:
        raise RuntimeError("vtracer is required. Install via `pip install vtracer`.")

    in_p = Path(input_path).resolve()
    out_p = Path(output_path).resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)

    mode = "spline" if smooth_curves else "polygon"

    # Pre-quantize image palette if max_colors is specified (e.g. 2 to 8 colors for AMS)
    actual_input = str(in_p)
    temp_quantized = None
    if max_colors is not None and max_colors > 1:
        img = Image.open(in_p).convert("RGBA")
        # Separate alpha
        alpha = img.split()[-1]
        rgb = img.convert("RGB")
        # Quantize colors
        quantized = rgb.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT).convert("RGB")
        # Re-attach alpha
        quantized.putalpha(alpha)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            temp_quantized = tf.name
        quantized.save(temp_quantized)
        actual_input = temp_quantized

    try:
        vtracer.convert_image_to_svg_py(
            actual_input,
            str(out_p),
            colormode=colormode,
            hierarchical="cutout",  # CRITICAL: Non-overlapping jigsaw pieces, ZERO background bleed
            mode=mode,
            filter_speckle=speckle_filter,
            color_precision=color_precision,
            layer_difference=layer_difference,
            corner_threshold=corner_threshold,
            length_threshold=length_threshold,
            max_iterations=10,
            splice_threshold=splice_threshold,
            path_precision=3,
        )
    finally:
        if temp_quantized and os.path.exists(temp_quantized):
            os.remove(temp_quantized)

    return out_p


# ==============================================================================
# 2. OPTION B: Zero-Bleed Monochromatic & Straight-Edge Contour Vectorizer
# ==============================================================================

def extract_color_mask(
    image_path: Union[str, Path],
    channel: str = "auto",
    alpha_threshold: int = 128,
    luminance_threshold: Optional[int] = None,
    color_target: Optional[str] = None,
    invert: bool = False,
    denoise_radius: int = 1,
) -> Tuple[np.ndarray, Tuple[int, int]]:
    """
    Extracts a binary mask from an image where foreground is 255 (white) and background is 0 (black).
    Supports auto detection, alpha channel, luminance thresholding, or color targeting (e.g. 'gold', 'black').
    """
    img = Image.open(image_path)
    orig_w, orig_h = img.size

    # Check for targeted color segmentation (e.g. Gold/Orange graphics vs Black background)
    if color_target:
        img_rgba = img.convert("RGBA")
        arr = np.array(img_rgba)
        alpha = arr[:, :, 3]
        r, g, b = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)

        if color_target.lower() in ("gold", "yellow", "orange"):
            # High red/green, low blue, non-transparent
            is_fg = (alpha > alpha_threshold) & ((r + g) > 160) & (b < 180)
        elif color_target.lower() in ("black", "dark"):
            # Dark foreground, non-transparent
            is_fg = (alpha > alpha_threshold) & ((r + g + b) < 120)
        elif color_target.lower() in ("white", "light"):
            is_fg = (alpha > alpha_threshold) & ((r + g + b) > 500)
        else:
            raise ValueError(f"Unknown color_target: {color_target}")

        mask = np.where(is_fg, 255, 0).astype(np.uint8)
        if invert:
            mask = cv2.bitwise_not(mask)
        return mask, (orig_w, orig_h)

    # Transparency alpha channel
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    if channel in ("auto", "alpha") and has_alpha:
        img_rgba = img.convert("RGBA")
        alpha = np.array(img_rgba.split()[-1])
        if channel == "alpha" or (alpha.min() < 250 and alpha.max() > 10):
            is_fg = alpha >= alpha_threshold
            if invert:
                is_fg = ~is_fg
            mask = np.where(is_fg, 255, 0).astype(np.uint8)
            return mask, (orig_w, orig_h)

    # Greyscale luminance processing
    gray = np.array(img.convert("L"))

    if luminance_threshold is not None:
        thresh_val = luminance_threshold
    elif HAS_CV2:
        thresh_val, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        corners = [gray[0, 0], gray[0, -1], gray[-1, 0], gray[-1, -1]]
        thresh_val = 128 if float(np.mean(corners)) > 128 else 128

    corners = [gray[0, 0], gray[0, -1], gray[-1, 0], gray[-1, -1]]
    bg_is_light = float(np.mean(corners)) >= thresh_val

    if bg_is_light:
        is_fg = gray < thresh_val
    else:
        is_fg = gray >= thresh_val

    if invert:
        is_fg = ~is_fg

    mask = np.where(is_fg, 255, 0).astype(np.uint8)

    if HAS_CV2 and denoise_radius > 0:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (denoise_radius * 2 + 1, denoise_radius * 2 + 1))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask, (orig_w, orig_h)


def signed_area(pts: np.ndarray) -> float:
    """Calculates signed area using the Shoelace formula."""
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2.0


def orient_pts(pts: np.ndarray, is_hole: bool = False) -> np.ndarray:
    """
    In SVG screen coordinates (Y down):
    Outer boundary wire should have signed_area < 0 (translates to CCW in Cartesian Y-up).
    Hole wire should have signed_area > 0 (translates to CW in Cartesian Y-up).
    """
    sa = signed_area(pts)
    want_negative = not is_hole
    if (sa < 0) != want_negative:
        pts = pts[::-1]
    return pts


def binary_png_to_svg_contour(
    mask: np.ndarray,
    output_path: Union[str, Path],
    epsilon_px: float = 1.5,
    min_area_px: float = 16.0,
    min_hole_area_px: float = 64.0,
    fill_color: str = "#000000",
) -> Path:
    """
    Traces absolute pixel-perfect boundaries for pure black/white images using
    OpenCV Douglas-Peucker polygonal simplification.
    
    Guarantees:
    - 100% straight lines between corners for geometric shapes (e.g. Star of David / Magen David).
    - Individual <path> per disconnected root shape with nested holes.
    - Proper wire orientation (CCW outer, CW inner) for clean OpenCascade / build123d CAD face extrusion.
    - Zero overlapping layers and zero color bleeding.
    """
    if not HAS_CV2:
        raise RuntimeError("opencv-python is required. Install via `pip install opencv-python`.")

    h, w = mask.shape
    out_p = Path(output_path).resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1)

    if hierarchy is None:
        out_p.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"/>\n', encoding="utf-8")
        return out_p

    tree = hierarchy[0]
    roots = {}
    for i, cnt in enumerate(contours):
        if cv2.contourArea(cnt) < min_area_px:
            continue
        parent = tree[i][3]
        if parent == -1:
            roots[i] = []

    for i, cnt in enumerate(contours):
        if cv2.contourArea(cnt) < min_hole_area_px:
            continue
        parent = tree[i][3]
        if parent != -1 and parent in roots:
            roots[parent].append(i)

    def pts_to_d(pts):
        return "M " + " ".join(f"{float(p[0]):.2f} {float(p[1]):.2f}" for p in pts) + " Z"

    svg_paths = []
    for root_idx, hole_indices in roots.items():
        cnt = contours[root_idx]
        approx = cv2.approxPolyDP(cnt, epsilon=epsilon_px, closed=True)
        if len(approx) < 3:
            continue
        pts = orient_pts(approx.reshape(-1, 2), is_hole=False)
        d = pts_to_d(pts)

        for h_idx in hole_indices:
            h_cnt = contours[h_idx]
            h_approx = cv2.approxPolyDP(h_cnt, epsilon=epsilon_px, closed=True)
            if len(h_approx) < 3:
                continue
            h_pts = orient_pts(h_approx.reshape(-1, 2), is_hole=True)
            d += " " + pts_to_d(h_pts)

        svg_paths.append(f'  <path d="{d}" fill="{fill_color}" fill-rule="evenodd"/>')

    svg_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
    ] + svg_paths + ["</svg>\n"]

    out_p.write_text("\n".join(svg_content), encoding="utf-8")
    return out_p


# ==============================================================================
# 3. Physical Scaling & Origin Centering
# ==============================================================================

def normalize_and_scale_svg(
    svg_path: Union[str, Path],
    target_width_mm: Optional[float] = None,
    target_height_mm: Optional[float] = None,
    center_origin: bool = False,
    flip_y: bool = False,
) -> None:
    """
    Scales SVG coordinates to physical millimetres (mm) and optionally centers geometry
    at (0, 0) for direct placement in CAD models.
    """
    import xml.etree.ElementTree as ET

    svg_file = Path(svg_path)
    ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", ns)

    tree = ET.parse(svg_file)
    root = tree.getroot()

    orig_x, orig_y = 0.0, 0.0
    orig_w, orig_h = None, None

    if "viewBox" in root.attrib:
        vals = [float(x) for x in re.split(r"[\s,]+", root.attrib["viewBox"].strip())]
        orig_x, orig_y, orig_w, orig_h = vals[0], vals[1], vals[2], vals[3]
    elif "width" in root.attrib and "height" in root.attrib:
        orig_w = float(re.sub(r"[^\d.]", "", root.attrib["width"]))
        orig_h = float(re.sub(r"[^\d.]", "", root.attrib["height"]))

    if not orig_w or not orig_h:
        return

    scale_x, scale_y = 1.0, 1.0
    if target_width_mm and target_height_mm:
        scale_x = target_width_mm / orig_w
        scale_y = target_height_mm / orig_h
    elif target_width_mm:
        scale_x = target_width_mm / orig_w
        scale_y = scale_x
    elif target_height_mm:
        scale_y = target_height_mm / orig_h
        scale_x = scale_y

    final_w = orig_w * scale_x
    final_h = orig_h * scale_y

    trans_x = -(orig_x + orig_w / 2.0) * scale_x if center_origin else 0.0
    trans_y = -(orig_y + orig_h / 2.0) * scale_y if center_origin else 0.0
    sy = -scale_y if flip_y else scale_y

    g_elem = ET.Element(f"{{{ns}}}g")
    g_elem.set("transform", f"translate({trans_x:.4f}, {trans_y:.4f}) scale({scale_x:.6f}, {sy:.6f})")

    children = list(root)
    for child in children:
        root.remove(child)
        g_elem.append(child)
    root.append(g_elem)

    root.set("width", f"{final_w:.2f}mm")
    root.set("height", f"{final_h:.2f}mm")
    if center_origin:
        root.set("viewBox", f"{-final_w/2.0:.4f} {-final_h/2.0:.4f} {final_w:.4f} {final_h:.4f}")
    else:
        root.set("viewBox", f"0 0 {final_w:.4f} {final_h:.4f}")

    tree.write(svg_file, encoding="utf-8", xml_declaration=True)


# ==============================================================================
# 4. Master Unified Vectorization Pipeline
# ==============================================================================

def vectorize_raster(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    engine: str = "auto",
    colormode: str = "binary",
    color_target: Optional[str] = None,
    channel: str = "auto",
    smooth_curves: bool = True,
    epsilon_px: float = 1.5,
    speckle_filter: int = 4,
    color_precision: int = 6,
    max_colors: Optional[int] = None,
    target_width_mm: Optional[float] = None,
    target_height_mm: Optional[float] = None,
    center_origin: bool = False,
    flip_y: bool = False,
    invert: bool = False,
) -> Path:
    """
    Unified high-level entrypoint to vectorize any raster image with zero bleed.
    
    engine:
        'auto': Selects 'contour' if straight-edge / monochrome is desired, or 'vtracer' for multi-color.
        'vtracer': Option A — multi-color cutout mosaic (zero overlapping layers).
        'contour': Option B — OpenCV Douglas-Peucker geometric boundary tracer.
    """
    in_p = Path(input_path).resolve()
    if not in_p.exists():
        raise FileNotFoundError(f"Input image not found: {in_p}")

    if output_path is None:
        out_p = in_p.with_suffix(".svg")
    else:
        out_p = Path(output_path).resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)

    # Determine engine
    selected_engine = engine
    if selected_engine == "auto":
        if colormode == "color":
            selected_engine = "vtracer"
        elif not smooth_curves or color_target is not None:
            selected_engine = "contour"
        elif HAS_VTRACER:
            selected_engine = "vtracer"
        else:
            selected_engine = "contour"

    if selected_engine == "vtracer":
        if not HAS_VTRACER:
            raise RuntimeError("vtracer is not installed.")
        clean_vectorize_vtracer(
            input_path=in_p,
            output_path=out_p,
            colormode=colormode,
            smooth_curves=smooth_curves,
            speckle_filter=speckle_filter,
            color_precision=color_precision,
            max_colors=max_colors,
        )
    elif selected_engine == "contour":
        mask, _ = extract_color_mask(
            image_path=in_p,
            channel=channel,
            color_target=color_target,
            invert=invert,
        )
        binary_png_to_svg_contour(
            mask=mask,
            output_path=out_p,
            epsilon_px=epsilon_px,
        )
    else:
        raise ValueError(f"Unknown engine: {selected_engine}")

    # Scale & Center if requested
    if target_width_mm or target_height_mm or center_origin or flip_y:
        normalize_and_scale_svg(
            out_p,
            target_width_mm=target_width_mm,
            target_height_mm=target_height_mm,
            center_origin=center_origin,
            flip_y=flip_y,
        )

    return out_p


# ==============================================================================
# 5. Direct build123d CAD Integration
# ==============================================================================

def image_to_build123d_faces(
    image_path: Union[str, Path],
    target_width_mm: Optional[float] = None,
    target_height_mm: Optional[float] = None,
    center_origin: bool = True,
    engine: str = "contour",
    color_target: Optional[str] = None,
    smooth_curves: bool = False,
    epsilon_px: float = 1.5,
):
    """
    Direct bridge to build123d CAD geometry.
    Vectorizes image with zero bleed and imports directly into 2D Face objects.
    """
    try:
        import build123d as b3d
    except ImportError:
        raise RuntimeError("build123d is required for image_to_build123d_faces.")

    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tf:
        temp_svg = tf.name

    try:
        vectorize_raster(
            input_path=image_path,
            output_path=temp_svg,
            engine=engine,
            color_target=color_target,
            smooth_curves=smooth_curves,
            epsilon_px=epsilon_px,
            target_width_mm=target_width_mm,
            target_height_mm=target_height_mm,
            center_origin=center_origin,
        )
        faces = b3d.import_svg(temp_svg)
        return faces
    finally:
        if os.path.exists(temp_svg):
            os.remove(temp_svg)


# ==============================================================================
# 6. CLI Interface
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Zero-Bleed Raster-to-SVG Vectorization Engine for CAD & 3D Printing."
    )
    parser.add_argument("input", type=str, help="Input raster image file (PNG, JPG, BMP, etc.)")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output SVG file path")
    parser.add_argument("--engine", choices=["auto", "vtracer", "contour"], default="auto",
                        help="Vectorization engine ('vtracer' for cutout mosaic, 'contour' for geometric straight lines)")
    parser.add_argument("--colormode", choices=["binary", "color"], default="binary",
                        help="Color mode: 'binary' for solid silhouettes, 'color' for multi-color cutout mosaic")
    parser.add_argument("--color-target", choices=["gold", "black", "white", "orange"], default=None,
                        help="Target specific color layer from multi-color artwork")
    parser.add_argument("--channel", choices=["auto", "alpha", "luminance"], default="auto",
                        help="Channel extraction mode")
    parser.add_argument("--straight-edges", action="store_true",
                        help="Enforce mathematical straight lines between corners (e.g. Star of David / Magen David, text, polygons)")
    parser.add_argument("--epsilon", type=float, default=1.5,
                        help="Contour simplification tolerance in pixels (higher = straighter/simpler, default=1.5)")
    parser.add_argument("--filter-speckle", type=int, default=4,
                        help="Ignore isolated noise pixels smaller than N pixels")
    parser.add_argument("--max-colors", type=int, default=None,
                        help="Palette reduction limit (e.g. 2, 4, 8) to eliminate lighting gradient patches")
    parser.add_argument("--width-mm", type=float, default=None, help="Target physical width in mm")
    parser.add_argument("--height-mm", type=float, default=None, help="Target physical height in mm")
    parser.add_argument("--center", action="store_true", help="Center geometry at origin (0, 0)")
    parser.add_argument("--flip-y", action="store_true", help="Flip Y-axis to match CAD coordinates")
    parser.add_argument("--invert", action="store_true", help="Invert foreground and background")

    args = parser.parse_args()

    smooth_curves = not args.straight_edges

    out = vectorize_raster(
        input_path=args.input,
        output_path=args.output,
        engine=args.engine,
        colormode=args.colormode,
        color_target=args.color_target,
        channel=args.channel,
        smooth_curves=smooth_curves,
        epsilon_px=args.epsilon,
        speckle_filter=args.filter_speckle,
        max_colors=args.max_colors,
        target_width_mm=args.width_mm,
        target_height_mm=args.height_mm,
        center_origin=args.center,
        flip_y=args.flip_y,
        invert=args.invert,
    )
    print(f"SUCCESS: Zero-bleed SVG generated at: {out}")


if __name__ == "__main__":
    main()
