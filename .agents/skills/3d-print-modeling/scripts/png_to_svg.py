#!/usr/bin/env python3
"""
PNG-to-SVG Vectorization & CAD Transformation Engine
===================================================
Converts raster images (PNG, JPG, BMP, WEBP) into clean, high-precision SVG vector
geometry optimized for 3D modeling, Bambu Studio modifier embossing, and CAD extrusions.

Key Features:
- Alpha channel transparency isolation (e.g. logos with transparent backgrounds)
- Intelligent foreground/background contrast detection (Otsu / adaptive / corner sampling)
- Dual vectorization engines:
    1. VTracer (Rust-accelerated, bezier spline fitting, sub-pixel smoothness)
    2. OpenCV + Douglas-Peucker (parametric contour simplification & hierarchy)
- Physical CAD unit scaling: `--width-mm`, `--height-mm` (1 SVG unit = 1.0 mm)
- Origin centering: `--center` (centers geometry at (0, 0) for direct CAD placement)
- Direct build123d integration (`image_to_build123d_faces`) for instant 3D extrusions
"""

import os
import sys
import math
import argparse
import tempfile
from pathlib import Path
from typing import Optional, Tuple, List, Union

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


def preprocess_raster_mask(
    image_path: Union[str, Path],
    channel: str = "auto",
    alpha_threshold: int = 128,
    luminance_threshold: Optional[int] = None,
    invert: bool = False,
    denoise_radius: int = 1,
) -> Tuple[np.ndarray, Tuple[int, int]]:
    """
    Loads an image, isolates foreground vs background, and returns a binary mask
    where foreground = 0 (black) and background = 255 (white).
    
    channel: 'auto', 'alpha' (isolate transparency), or 'luminance' (isolate dark/light figures).
    """
    img = Image.open(image_path)
    orig_w, orig_h = img.size

    # Check for alpha channel if requested or in auto mode
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    if (channel in ("auto", "alpha")) and has_alpha:
        img_rgba = img.convert("RGBA")
        alpha = np.array(img_rgba.split()[-1])
        # If user explicitly asked for alpha OR image has non-trivial transparency:
        if channel == "alpha" or (alpha.min() < 250 and alpha.max() > 10):
            is_fg = alpha >= alpha_threshold
            if invert:
                is_fg = ~is_fg
            mask = np.where(is_fg, 0, 255).astype(np.uint8)
            return mask, (orig_w, orig_h)

    # Greyscale luminance processing
    gray = np.array(img.convert("L"))

    if luminance_threshold is not None:
        thresh_val = luminance_threshold
    elif HAS_CV2:
        # Otsu automatic thresholding
        thresh_val, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        # Sample 4 corners to determine background luminance
        corners = [gray[0, 0], gray[0, -1], gray[-1, 0], gray[-1, -1]]
        bg_lum = float(np.mean(corners))
        thresh_val = 128 if bg_lum > 128 else 128

    # Determine if background is light or dark
    corners = [gray[0, 0], gray[0, -1], gray[-1, 0], gray[-1, -1]]
    bg_lum = float(np.mean(corners))
    bg_is_light = bg_lum >= thresh_val

    if bg_is_light:
        # Foreground is dark
        is_fg = gray < thresh_val
    else:
        # Foreground is light
        is_fg = gray >= thresh_val

    if invert:
        is_fg = ~is_fg

    mask = np.where(is_fg, 0, 255).astype(np.uint8)

    # Denoise / morphological cleanup if opencv is available
    if HAS_CV2 and denoise_radius > 0:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (denoise_radius * 2 + 1, denoise_radius * 2 + 1))
        mask_inv = cv2.bitwise_not(mask)
        mask_clean = cv2.morphologyEx(mask_inv, cv2.MORPH_OPEN, kernel)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)
        mask = cv2.bitwise_not(mask_clean)

    return mask, (orig_w, orig_h)


def vectorize_with_vtracer(
    mask_png_path: Union[str, Path],
    output_svg_path: Union[str, Path],
    mode: str = "spline",
    filter_speckle: int = 4,
    corner_threshold: int = 60,
    length_threshold: float = 4.0,
    splice_threshold: int = 45,
    path_precision: int = 3,
) -> None:
    """Uses Rust-accelerated VTracer to convert a binary mask into an SVG."""
    if not HAS_VTRACER:
        raise RuntimeError("vtracer is not installed. Install via `uv pip install vtracer`.")

    vtracer.convert_image_to_svg_py(
        str(mask_png_path),
        str(output_svg_path),
        colormode="binary",
        hierarchical="stacked",
        mode=mode,
        filter_speckle=filter_speckle,
        color_precision=6,
        layer_difference=16,
        corner_threshold=corner_threshold,
        length_threshold=length_threshold,
        max_iterations=10,
        splice_threshold=splice_threshold,
        path_precision=path_precision,
    )


def vectorize_with_opencv(
    mask: np.ndarray,
    output_svg_path: Union[str, Path],
    tolerance_px: float = 1.0,
) -> None:
    """Alternative vectorizer using OpenCV contour hierarchy & Douglas-Peucker simplification."""
    if not HAS_CV2:
        raise RuntimeError("opencv-python is not installed. Install via `uv pip install opencv-python`.")

    h, w = mask.shape
    fg_binary = cv2.bitwise_not(mask)
    contours, hierarchy = cv2.findContours(fg_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

    svg_paths = []
    if hierarchy is not None:
        hierarchy = hierarchy[0]
        for idx, cnt in enumerate(contours):
            if cv2.contourArea(cnt) < 16.0:
                continue
            # Douglas-Peucker simplification
            approx = cv2.approxPolyDP(cnt, epsilon=tolerance_px, closed=True)
            if len(approx) < 3:
                continue

            pts = approx.reshape(-1, 2)
            d_str = f"M {pts[0][0]:.2f} {pts[0][1]:.2f} "
            for pt in pts[1:]:
                d_str += f"L {pt[0]:.2f} {pt[1]:.2f} "
            d_str += "Z"
            svg_paths.append(d_str)

    # Compose SVG document with fill-rule="evenodd" for correct hole subtraction
    svg_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
    ]
    for d in svg_paths:
        svg_content.append(f'  <path d="{d}" fill="#000000" fill-rule="evenodd"/>')
    svg_content.append("</svg>\n")

    Path(output_svg_path).write_text("\n".join(svg_content), encoding="utf-8")


def normalize_and_scale_svg(
    svg_path: Union[str, Path],
    target_width_mm: Optional[float] = None,
    target_height_mm: Optional[float] = None,
    center_origin: bool = False,
    flip_y: bool = False,
) -> None:
    """
    Transforms the SVG coordinate system so coordinates are in physical millimetres (mm)
    and optionally centered at (0, 0) for direct CAD placement.
    """
    import re
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

    # Calculate scale factor to target dimensions in mm
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

    trans_x = - (orig_x + orig_w / 2.0) * scale_x if center_origin else 0.0
    trans_y = - (orig_y + orig_h / 2.0) * scale_y if center_origin else 0.0
    sy = -scale_y if flip_y else scale_y

    # Wrap all children in a <g> tag with the geometric transform
    g_elem = ET.Element(f"{{{ns}}}g")
    g_elem.set("transform", f"translate({trans_x:.4f}, {trans_y:.4f}) scale({scale_x:.6f}, {sy:.6f})")

    children = list(root)
    for child in children:
        root.remove(child)
        g_elem.append(child)
    root.append(g_elem)

    # Set document properties
    root.set("width", f"{final_w:.2f}mm")
    root.set("height", f"{final_h:.2f}mm")
    if center_origin:
        root.set("viewBox", f"{-final_w/2.0:.4f} {-final_h/2.0:.4f} {final_w:.4f} {final_h:.4f}")
    else:
        root.set("viewBox", f"0 0 {final_w:.4f} {final_h:.4f}")

    tree.write(svg_file, encoding="utf-8", xml_declaration=True)


def convert_image_to_svg(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    target_width_mm: Optional[float] = None,
    target_height_mm: Optional[float] = None,
    center_origin: bool = False,
    flip_y: bool = False,
    invert: bool = False,
    channel: str = "auto",
    alpha_threshold: int = 128,
    luminance_threshold: Optional[int] = None,
    colormode: str = "binary",
    engine: str = "auto",
    mode: str = "spline",
    filter_speckle: int = 4,
) -> Path:
    """
    Full pipeline to convert any raster image into a vectorized SVG.
    """
    in_p = Path(input_path).resolve()
    if not in_p.exists():
        raise FileNotFoundError(f"Input image not found: {in_p}")

    if output_path is None:
        out_p = in_p.with_suffix(".svg")
    else:
        out_p = Path(output_path).resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)

    use_vtracer = (engine in ("vtracer", "auto")) and HAS_VTRACER

    if colormode == "color" and use_vtracer:
        # Direct full-color vectorization
        vtracer.convert_image_to_svg_py(
            str(in_p),
            str(out_p),
            colormode="color",
            hierarchical="stacked",
            mode=mode,
            filter_speckle=filter_speckle,
            color_precision=6,
            layer_difference=16,
            corner_threshold=60,
            length_threshold=4.0,
            max_iterations=10,
            splice_threshold=45,
            path_precision=3,
        )
    else:
        # Binary monochrome / silhouette vectorization
        mask, (w, h) = preprocess_raster_mask(
            in_p,
            channel=channel,
            alpha_threshold=alpha_threshold,
            luminance_threshold=luminance_threshold,
            invert=invert,
        )

        if use_vtracer:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
                temp_mask_path = tf.name
            try:
                Image.fromarray(mask).save(temp_mask_path)
                vectorize_with_vtracer(
                    temp_mask_path,
                    out_p,
                    mode=mode,
                    filter_speckle=filter_speckle,
                )
            finally:
                if os.path.exists(temp_mask_path):
                    os.remove(temp_mask_path)
        elif HAS_CV2:
            vectorize_with_opencv(mask, out_p, tolerance_px=1.0)
        else:
            raise RuntimeError("Neither vtracer nor opencv-python is available to vectorize images.")

    # Postprocess: scale and center if requested
    if target_width_mm or target_height_mm or center_origin or flip_y:
        normalize_and_scale_svg(
            out_p,
            target_width_mm=target_width_mm,
            target_height_mm=target_height_mm,
            center_origin=center_origin,
            flip_y=flip_y,
        )

    return out_p


def image_to_build123d_faces(
    image_path: Union[str, Path],
    target_width_mm: Optional[float] = None,
    target_height_mm: Optional[float] = None,
    center_origin: bool = True,
    channel: str = "auto",
    invert: bool = False,
):
    """
    Direct bridge to build123d CAD geometry.
    Converts raster image directly to 2D build123d Face(s) ready for extrusion.
    """
    try:
        import build123d as b3d
    except ImportError:
        raise RuntimeError("build123d is required for image_to_build123d_faces.")

    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tf:
        temp_svg = tf.name

    try:
        convert_image_to_svg(
            image_path,
            temp_svg,
            target_width_mm=target_width_mm,
            target_height_mm=target_height_mm,
            center_origin=center_origin,
            channel=channel,
            invert=invert,
        )
        faces = b3d.import_svg(temp_svg)
        return faces
    finally:
        if os.path.exists(temp_svg):
            os.remove(temp_svg)


def main():
    parser = argparse.ArgumentParser(
        description="Convert PNG/raster images to CAD-ready SVG vector files."
    )
    parser.add_argument("input", type=str, help="Path to input raster image (PNG, JPG, BMP, etc.)")
    parser.add_argument("-o", "--output", type=str, default=None, help="Path to output SVG file")
    parser.add_argument("--width-mm", type=float, default=None, help="Target physical width in mm")
    parser.add_argument("--height-mm", type=float, default=None, help="Target physical height in mm")
    parser.add_argument("--center", action="store_true", help="Center geometry at origin (0, 0)")
    parser.add_argument("--flip-y", action="store_true", help="Flip Y-axis to match CAD coordinates")
    parser.add_argument("--invert", action="store_true", help="Invert foreground and background")
    parser.add_argument("--channel", choices=["auto", "alpha", "luminance"], default="auto", help="Mask isolation channel")
    parser.add_argument("--colormode", choices=["binary", "color"], default="binary", help="Vector color mode (binary silhouette or full color)")
    parser.add_argument("--engine", choices=["auto", "vtracer", "opencv"], default="auto", help="Vectorization engine")
    parser.add_argument("--mode", choices=["spline", "polygon", "none"], default="spline", help="Curve fitting mode")
    parser.add_argument("--filter-speckle", type=int, default=4, help="Speckle noise filter radius in px")
    parser.add_argument("--alpha-thresh", type=int, default=128, help="Alpha channel cutoff (0..255)")

    args = parser.parse_args()

    out = convert_image_to_svg(
        input_path=args.input,
        output_path=args.output,
        target_width_mm=args.width_mm,
        target_height_mm=args.height_mm,
        center_origin=args.center,
        flip_y=args.flip_y,
        invert=args.invert,
        channel=args.channel,
        colormode=args.colormode,
        alpha_threshold=args.alpha_thresh,
        engine=args.engine,
        mode=args.mode,
        filter_speckle=args.filter_speckle,
    )
    print(f"SUCCESS: Vectorized SVG written to: {out}")


if __name__ == "__main__":
    main()
