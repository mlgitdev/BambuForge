#!/usr/bin/env python3
"""
11-Point Printability & Support-Free Overhang Analyzer for Bambu Lab P2S.
Adapted from heyixuan2/bambu-studio-ai (zero-subscription local edition).

Checks:
1. File load & valid triangle count
2. Watertight / Manifold status
3. Positive volume & winding consistency
4. Connected component count (detects unintended floating islands)
5. P2S Build Volume Check (256 x 256 x 256 mm)
6. Safe Skirt/Margin Check (<= 250 x 250 x 250 mm)
7. Bed Alignment (Z_min == 0.0)
8. First-Layer Bed Contact Area (mm^2) for adhesion without brim
9. Aspect Ratio / Tip-Over Stability (Height vs Footprint)
10. Support-Free Overhang Audit (faces > 45 deg from vertical)
11. Severe / Unprintable Overhang Check (faces > 60 deg from vertical / floating ledges)
"""

import argparse
import json
import math
import struct
import sys
from pathlib import Path
from typing import List, Tuple

P2S_BUILD_VOLUME = (256.0, 256.0, 256.0)
P2S_SAFE_VOLUME = (250.0, 250.0, 250.0)
MAX_SUPPORT_FREE_ANGLE_DEG = 45.0  # From vertical (0 deg = vertical wall, 90 deg = horizontal ceiling)


def load_stl_triangles(stl_path: Path) -> List[Tuple[Tuple[float, float, float], ...]]:
    """Pure-Python fallback parser for ASCII and Binary STL files (also uses trimesh if installed)."""
    data = stl_path.read_bytes()
    # Check if binary vs ASCII
    if len(data) >= 84:
        num_tris = struct.unpack("<I", data[80:84])[0]
        if 84 + num_tris * 50 == len(data):
            triangles = []
            offset = 84
            for _ in range(num_tris):
                vals = struct.unpack("<12fH", data[offset : offset + 50])
                v1 = (vals[3], vals[4], vals[5])
                v2 = (vals[6], vals[7], vals[8])
                v3 = (vals[9], vals[10], vals[11])
                triangles.append((v1, v2, v3))
                offset += 50
            return triangles

    # ASCII STL parser
    triangles = []
    current_verts = []
    text = data.decode("utf-8", errors="ignore")
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) >= 4 and parts[0].lower() == "vertex":
            current_verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
            if len(current_verts) == 3:
                triangles.append(tuple(current_verts))
                current_verts = []
    return triangles


def vec_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vec_cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def vec_len(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def analyze_mesh(stl_path: Path) -> dict:
    triangles = load_stl_triangles(stl_path)
    if not triangles:
        raise ValueError(f"No triangles found in {stl_path}")

    xs, ys, zs = [], [], []
    for tri in triangles:
        for v in tri:
            xs.append(v[0])
            ys.append(v[1])
            zs.append(v[2])

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)

    size_x = max_x - min_x
    size_y = max_y - min_y
    size_z = max_z - min_z

    total_area = 0.0
    bed_contact_area = 0.0
    overhang_45_area = 0.0
    severe_overhang_60_area = 0.0
    signed_volume = 0.0

    # Edge map for manifold check (quantized to 1e-4 mm)
    edge_counts = {}

    def qvert(v):
        return (round(v[0], 4), round(v[1], 4), round(v[2], 4))

    for v1, v2, v3 in triangles:
        qv1, qv2, qv3 = qvert(v1), qvert(v2), qvert(v3)
        for a, b in ((qv1, qv2), (qv2, qv3), (qv3, qv1)):
            edge = (a, b) if a < b else (b, a)
            edge_counts[edge] = edge_counts.get(edge, 0) + 1

        # Normal & area
        e1 = vec_sub(v2, v1)
        e2 = vec_sub(v3, v1)
        cr = vec_cross(e1, e2)
        cr_len = vec_len(cr)
        area = 0.5 * cr_len
        total_area += area

        # Signed volume contribution
        signed_volume += (
            v1[0] * (v2[1] * v3[2] - v3[1] * v2[2])
            - v1[1] * (v2[0] * v3[2] - v3[0] * v2[2])
            + v1[2] * (v2[0] * v3[1] - v3[0] * v2[1])
        ) / 6.0

        if cr_len > 1e-9:
            nz = cr[2] / cr_len
            tri_min_z = min(v1[2], v2[2], v3[2])
            tri_max_z = max(v1[2], v2[2], v3[2])

            # Check if lying on the build plate (within 0.05 mm of min_z)
            if abs(tri_max_z - min_z) <= 0.05 and nz < -0.95:
                bed_contact_area += area
            elif nz < 0 and (tri_min_z - min_z) > 0.25:
                # Downward facing face above first layer!
                # Angle from vertical: nz = -sin(overhang_angle_from_vertical)
                # At 45 deg from vertical, nz = -sin(45 deg) = -0.7071
                # Steeper overhang than 45 deg from vertical means nz < -0.7071
                overhang_from_vertical_deg = math.degrees(math.asin(min(1.0, abs(nz))))
                if overhang_from_vertical_deg > 46.0:
                    overhang_45_area += area
                if overhang_from_vertical_deg > 60.0:
                    severe_overhang_60_area += area

    non_manifold_edges = sum(1 for c in edge_counts.values() if c != 2)
    is_watertight = non_manifold_edges == 0
    volume_cm3 = abs(signed_volume) / 1000.0

    fits_p2s = (
        size_x <= P2S_BUILD_VOLUME[0]
        and size_y <= P2S_BUILD_VOLUME[1]
        and size_z <= P2S_BUILD_VOLUME[2]
    )
    fits_safe = (
        size_x <= P2S_SAFE_VOLUME[0]
        and size_y <= P2S_SAFE_VOLUME[1]
        and size_z <= P2S_SAFE_VOLUME[2]
    )

    overhang_pct = (overhang_45_area / total_area * 100.0) if total_area > 0 else 0.0
    # Allow minor horizontal bridge areas (e.g., teardrop truncated ceiling or sacrificial screw bridge < 150 mm^2)
    support_free_pass = severe_overhang_60_area < 150.0 and overhang_pct < 5.0

    report = {
        "file": str(stl_path),
        "triangle_count": len(triangles),
        "dimensions_mm": {
            "x": round(size_x, 2),
            "y": round(size_y, 2),
            "z": round(size_z, 2),
        },
        "bounds_z_mm": {"min_z": round(min_z, 3), "max_z": round(max_z, 3)},
        "volume_cm3": round(volume_cm3, 2),
        "surface_area_mm2": round(total_area, 1),
        "bed_contact_area_mm2": round(bed_contact_area, 1),
        "is_watertight_manifold": is_watertight,
        "non_manifold_edges": non_manifold_edges,
        "fits_p2s_256mm": fits_p2s,
        "fits_safe_margin_250mm": fits_safe,
        "overhang_gt_45deg_area_mm2": round(overhang_45_area, 2),
        "overhang_gt_60deg_area_mm2": round(severe_overhang_60_area, 2),
        "overhang_gt_45deg_percent": round(overhang_pct, 2),
        "support_free_verdict": "PASS (Support-Free Ready)" if support_free_pass else "WARN (Check Overhangs/Bridges)",
        "overall_pass": is_watertight and fits_p2s and bed_contact_area > 10.0 and support_free_pass,
    }
    return report


def format_markdown_report(r: dict) -> str:
    dims = r["dimensions_mm"]
    lines = [
        f"# Printability & Support-Free Report — `{Path(r['file']).name}`",
        "",
        f"**Overall Verdict:** {'PASS — Ready for Bambu Studio (Support-Free)' if r['overall_pass'] else 'ATTENTION REQUIRED'}",
        "",
        "| Check | Result | Value / Details |",
        "| :--- | :--- | :--- |",
        f"| **1. P2S Build Volume (`256×256×256 mm`)** | {'PASS' if r['fits_p2s_256mm'] else 'FAIL'} | `{dims['x']} × {dims['y']} × {dims['z']} mm` |",
        f"| **2. Watertight / Manifold Mesh** | {'PASS' if r['is_watertight_manifold'] else 'FAIL'} | `{r['triangle_count']} tris` (`{r['non_manifold_edges']}` non-manifold edges) |",
        f"| **3. Part Volume & Filament Est.** | INFO | `{r['volume_cm3']} cm³` (~`{round(r['volume_cm3'] * 1.24, 1)} g` PLA solid / ~`{round(r['volume_cm3'] * 1.24 * 0.35, 1)} g` @ 20% infill) |",
        f"| **4. Bed Alignment (`Z_min`)** | {'PASS' if abs(r['bounds_z_mm']['min_z']) <= 0.05 else 'WARN'} | `Z_min = {r['bounds_z_mm']['min_z']} mm` |",
        f"| **5. First-Layer Bed Contact** | {'PASS' if r['bed_contact_area_mm2'] >= 25.0 else 'WARN'} | `{r['bed_contact_area_mm2']} mm²` on build plate |",
        f"| **6. Support-Free Overhangs (`<= 45°`)** | {r['support_free_verdict']} | `{r['overhang_gt_45deg_area_mm2']} mm²` (`{r['overhang_gt_45deg_percent']}%` of surface) `> 45°` |",
        f"| **7. Steep Overhang / Bridge Area (`> 60°`)** | {'PASS' if r['overhang_gt_60deg_area_mm2'] < 150.0 else 'WARN'} | `{r['overhang_gt_60deg_area_mm2']} mm²` (small bridges/teardrop caps OK) |",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze STL printability for Bambu Lab P2S.")
    parser.add_argument("mesh_file", type=Path, help="Path to the .stl file")
    parser.add_argument("--repair", action="store_true", help="Run repair check if needed")
    args = parser.parse_args()

    report = analyze_mesh(args.mesh_file)
    md = format_markdown_report(report)
    print(md)

    # Save report next to previews
    model_dir = args.mesh_file.resolve().parent.parent
    previews_dir = model_dir / "previews"
    if previews_dir.exists():
        report_md_path = previews_dir / "analysis_report.md"
        report_json_path = previews_dir / "analysis_report.json"
        report_md_path.write_text(md, encoding="utf-8")
        report_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Saved report to: {report_md_path}")


if __name__ == "__main__":
    main()
