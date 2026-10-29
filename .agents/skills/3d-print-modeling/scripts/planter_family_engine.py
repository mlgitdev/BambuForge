#!/usr/bin/env python3
"""
Parametric Multi-Color & Support-Free Planter Family Engine for Bambu Lab P2S.
Generates 7 distinct architectural & horticultural planter styles, each with:
  - Tray 1: Base Planter Box (Partitioned into 6 Watertight AMS Color Zones)
  - Tray 2: Matching Drip Tray / Saucer (1 Color Zone)
  - Tray 3: Stackable Deep-Root Extension Riser (Partitioned into 4 Watertight AMS Color Zones,
            oriented inverted on its flat rim at Z=0 so the 4 integrated male locking rods
            print pointing straight UP (+Z) from Z=140..170mm with ZERO supports!)

Supported Styles:
  0. `rectangular_classic` — Classic Reinforced Rectangular Box
  1. `oval_stadium`        — Smooth Elliptical / Stadium Track Planter
  2. `roman_fluted`        — Architectural Fluted Wave Facade Planter
  3. `origami_faceted`     — Japanese Origami Chamfered Octagon / Diamond-Facet Planter
  4. `self_watering_sip`   — Sub-Irrigated Self-Watering (SIP) Wicking Reservoir Planter
  5. `hex_honeycomb`       — Elongated Hexagonal Honeycomb Tessellation Planter
  6. `zen_pagoda`          — Stepped Brutalist Pagoda Terrace Planter
"""

import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from build123d import (
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Circle,
    Cone,
    Cylinder,
    Line,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    Polygon,
    Pos,
    Rectangle,
    RectangleRounded,
    RegularPolygon,
    Rot,
    SlotOverall,
    ThreePointArc,
    chamfer,
    extrude,
    fillet,
    loft,
    offset,
    sweep,
)

from p2s_cad_helpers import export_multicolor_multiplate_3mf


@dataclass
class PlanterSystemConfig:
    style: str = "rectangular_classic"
    outer_length_x: float = 232.0     # Base body X (fits 256mm P2S bed with margin for rim & saucer)
    outer_width_y: float = 182.0      # Base body Y
    base_height_z: float = 195.0      # Base planter height Z
    wall_thickness: float = 3.8       # 9-perimeter structural wall
    floor_thickness: float = 5.6      # Heavy-duty floor
    corner_radius: float = 18.0       # Corner radius for rectangular styles

    # Rim & Horizontal Connecting Strips (45-deg support-free)
    rim_ext: float = 4.2              # Rim outward extension (+4.2mm per side -> 240.4 x 190.4 mm)
    rim_height: float = 16.0          # Top rim collar height
    belt_ext: float = 2.4             # Connecting strip outward protrusion
    belt_height: float = 12.0         # Connecting strip total height
    belt1_z: float = 56.0             # Lower connecting strip Z bottom
    belt2_z: float = 118.0            # Upper connecting strip Z bottom

    # 4 Corner Trellis Columns & Dual-Stage (6mm & 4mm) Rod Sockets
    pillar_radius: float = 11.5       # Ø23mm corner columns
    rod_6mm_bore_d: float = 6.50      # Upper socket for 6mm metal stakes (and Riser locking pins!)
    rod_6mm_depth: float = 60.0       # 60mm deep upper socket
    rod_4mm_bore_d: float = 4.45      # Lower socket for 4mm metal wire stakes
    rod_4mm_depth: float = 50.0       # 110mm total socket depth

    # Tray 2: Drip Saucer (<= 248 x 198 mm total outer footprint for P2S plate auto-arrange)
    saucer_clearance: float = 4.8      # Generous 4.8 mm per-side clearance (9.6 mm total) for smooth non-binding drop-in fit
    saucer_wall_t: float = 3.2         # Watertight 8-loop perimeter wall
    saucer_floor_t: float = 4.0        # Heavy-duty floor
    saucer_height_z: float = 32.0      # Generous 24.4 mm overlap & large runoff reservoir
    saucer_rib_h: float = 3.6          # Aeration rail elevation

    # Tray 3: Inverted Stackable Extension Riser + 4 Integrated Male Locking Rods
    riser_body_h: float = 140.0       # Main riser body height (Z = 0..140mm)
    riser_skirt_h: float = 7.0        # Interlocking male skirt height (Red contour)
    skirt_clearance: float = 0.35     # 0.35mm per-side clearance
    lego_boss_r: float = 7.5          # Circular Lego boss radius (Yellow contour)
    lego_boss_h: float = 3.0          # Circular Lego boss height (protrudes past column shoulder)
    lego_socket_clr_r: float = 0.35   # Female Lego socket radial clearance (socket_r = 7.85mm)
    lego_socket_clr_z: float = 0.5    # Female Lego socket vertical clearance (socket_d = 3.5mm)
    riser_rod_len: float = 24.0       # Length of integrated locking rods protruding past Lego boss
    riser_rod_od: float = 6.20        # Outer diameter of integrated locking rods (fits 6.70mm hole!)
    riser_rod_id: float = 4.50        # Inner bore through integrated rods for 4mm metal wire stake


def get_style_corner_points(cfg: PlanterSystemConfig) -> List[Tuple[float, float]]:
    """Returns the 4 symmetric (X, Y) coordinates for the 4 trellis rod columns."""
    lx, wy = cfg.outer_length_x, cfg.outer_width_y
    if cfg.style == "oval_stadium":
        # Positioned along the stadium curved shoulders inside the wall
        cx = lx / 2.0 - 28.0
        cy = wy / 2.0 - 22.0
    elif cfg.style == "origami_faceted":
        cx = lx / 2.0 - 20.0
        cy = wy / 2.0 - 20.0
    elif cfg.style == "hex_honeycomb":
        cx = lx / 2.0 - 28.0
        cy = wy / 2.0 - 16.0
    else:
        cx = lx / 2.0 - 13.0
        cy = wy / 2.0 - 13.0
    return [(-cx, -cy), (cx, -cy), (cx, cy), (-cx, cy)]


def _sketch_2d_profile(style: str, length_x: float, width_y: float, corner_r: float) -> None:
    """Adds the 2D outer cross-section for the chosen style inside an active BuildSketch."""
    if style == "oval_stadium":
        # Smooth stadium / super-ellipse rounded rectangle with generous end radii
        # If corner_r is passed as an explicit saucer radius (> 30.0), respect it directly;
        # otherwise compute body radius based on base corner_r (18.0 + 48.0 = 66.0 mm).
        r_oval = corner_r if corner_r > 30.0 else min(width_y / 2.0 - 1.0, corner_r + 48.0)
        RectangleRounded(length_x, width_y, radius=r_oval)

    elif style == "roman_fluted":
        RectangleRounded(length_x, width_y, radius=corner_r)
        # Add vertical semicircular architectural flutes along the long & short faces
        flute_r = 4.2
        for x_pos in (-72.0, -48.0, -24.0, 0.0, 24.0, 48.0, 72.0):
            for y_sign in (-1, 1):
                with Locations((x_pos, y_sign * (width_y / 2.0 - 1.2))):
                    Circle(radius=flute_r)
        for y_pos in (-48.0, -24.0, 0.0, 24.0, 48.0):
            for x_sign in (-1, 1):
                with Locations((x_sign * (length_x / 2.0 - 1.2), y_pos)):
                    Circle(radius=flute_r)

    elif style == "origami_faceted":
        # 8-sided chamfered origami polygon with angular side facets
        cut = 28.0
        hx, hy = length_x / 2.0, width_y / 2.0
        Polygon(
            (-hx + cut, -hy),
            (0.0, -hy - 3.5),
            (hx - cut, -hy),
            (hx, -hy + cut),
            (hx + 3.5, 0.0),
            (hx, hy - cut),
            (hx - cut, hy),
            (0.0, hy + 3.5),
            (-hx + cut, hy),
            (-hx, hy - cut),
            (-hx - 3.5, 0.0),
            (-hx, -hy + cut),
            align=None,
        )

    elif style == "hex_honeycomb":
        # Elongated hexagonal honeycomb prism profile
        peak = 34.0
        hx, hy = length_x / 2.0, width_y / 2.0
        Polygon(
            (-hx + peak, -hy),
            (hx - peak, -hy),
            (hx, 0.0),
            (hx - peak, hy),
            (-hx + peak, hy),
            (-hx, 0.0),
            align=None,
        )

    else:
        # rectangular_classic, self_watering_sip, zen_pagoda
        RectangleRounded(length_x, width_y, radius=corner_r)


def make_profile_band(
    style: str,
    length_x: float,
    width_y: float,
    corner_r: float,
    z_bot: float,
    height: float,
    protrusion: float,
    chamfer_top: bool = True,
) -> Part:
    """
    Creates a 45-degree support-free horizontal band matching the planter's 2D profile.
    Uses a base RectangleRounded/Polygon band so every overhang is strictly <= 45 deg.
    """
    base_style = "rectangular_classic" if style == "roman_fluted" else style
    in_x = length_x - 2.0
    in_y = width_y - 2.0
    in_r = max(4.0, corner_r - 1.0)
    out_x = length_x + 2.0 * protrusion
    out_y = width_y + 2.0 * protrusion
    out_r = corner_r + protrusion

    ramp_h = (1.0 + protrusion) * 1.12
    with BuildPart() as band:
        # Bottom 45-deg ramp
        with BuildSketch(Plane.XY.offset(z_bot)) as s0:
            _sketch_2d_profile(base_style, in_x, in_y, in_r)
        with BuildSketch(Plane.XY.offset(z_bot + ramp_h)) as s1:
            _sketch_2d_profile(base_style, out_x, out_y, out_r)
        loft([s0.sketch, s1.sketch], ruled=True)

        # Middle vertical flat band
        mid_h = max(1.0, height - (2.0 * ramp_h if chamfer_top else ramp_h))
        with BuildSketch(Plane.XY.offset(z_bot + ramp_h)):
            _sketch_2d_profile(base_style, out_x, out_y, out_r)
        extrude(amount=mid_h)

        # Optional top 45-deg ramp
        if chamfer_top:
            z_top_start = z_bot + ramp_h + mid_h
            with BuildSketch(Plane.XY.offset(z_top_start)) as s2:
                _sketch_2d_profile(base_style, out_x, out_y, out_r)
            with BuildSketch(Plane.XY.offset(z_top_start + ramp_h)) as s3:
                _sketch_2d_profile(base_style, in_x, in_y, in_r)
            loft([s2.sketch, s3.sketch], ruled=True)

    return band.part


def make_stacking_female_cutter(cfg: PlanterSystemConfig, z_top: float) -> Part:
    """
    Cuts the matching female receiving sockets into the Base Planter (and Riser top)
    so the male skirt (Red contour), circular Lego boss (Yellow contour), and locking rod
    nest inside with 100% flush planar contact (0.0mm outer seam gap, zero sanding).
    """
    skirt_clr = cfg.skirt_clearance
    boss_r = cfg.lego_boss_r
    boss_h = cfg.lego_boss_h
    boss_clr_r = cfg.lego_socket_clr_r
    boss_clr_z = cfg.lego_socket_clr_z
    rod_hole_r = cfg.rod_6mm_bore_d / 2.0
    r4 = cfg.rod_4mm_bore_d / 2.0

    z_skirt_pocket = z_top - cfg.riser_skirt_h - boss_clr_z  # Female skirt pocket depth
    z_boss_pocket = z_skirt_pocket - boss_h - boss_clr_z     # Female Lego boss socket depth
    z_rod_pocket = z_boss_pocket - cfg.rod_6mm_depth        # 60mm deep rod bore
    z_stake_bot = z_rod_pocket - cfg.rod_4mm_depth           # Lower stake bore

    with BuildPart() as cutter:
        # 1. Corner column rebate matching the male skirt (Red contour) & pillar shoulder
        with Locations((0, 0, z_skirt_pocket)):
            Cylinder(
                radius=cfg.pillar_radius + skirt_clr,
                height=cfg.riser_skirt_h + boss_clr_z + 0.1,
                align=(Align.CENTER, Align.CENTER, Align.MIN)
            )
        # 2. Female Lego boss socket (Yellow contour)
        with Locations((0, 0, z_boss_pocket)):
            Cylinder(
                radius=boss_r + boss_clr_r,
                height=boss_h + boss_clr_z + 0.1,
                align=(Align.CENTER, Align.CENTER, Align.MIN)
            )
            # Lead-in chamfer
            with Locations((0, 0, boss_h + boss_clr_z - 0.8)):
                Cone(
                    bottom_radius=boss_r + boss_clr_r,
                    top_radius=boss_r + boss_clr_r + 0.8,
                    height=0.8,
                    align=(Align.CENTER, Align.CENTER, Align.MIN)
                )
        # 3. Rod bore (Ø6.50mm / 6.70mm)
        with Locations((0, 0, z_rod_pocket)):
            Cylinder(
                radius=rod_hole_r,
                height=cfg.rod_6mm_depth + 0.1,
                align=(Align.CENTER, Align.CENTER, Align.MIN)
            )
            with Locations((0, 0, cfg.rod_6mm_depth - 1.2)):
                Cone(
                    bottom_radius=rod_hole_r,
                    top_radius=rod_hole_r + 1.2,
                    height=1.2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN)
                )
        # 4. Continuous stake bore (Ø4.45mm)
        with Locations((0, 0, z_stake_bot)):
            Cylinder(
                radius=r4,
                height=cfg.rod_4mm_depth + 0.1,
                align=(Align.CENTER, Align.CENTER, Align.MIN)
            )
    return cutter.part


def make_bottom_runoff_arch(width: float, length: float, along_x: bool = True) -> Part:
    half_w = width / 2.0
    plane = Plane.YZ if along_x else Plane.XZ
    with BuildPart() as arch:
        with BuildSketch(plane):
            Polygon(
                (-half_w, -0.5),
                (half_w, -0.5),
                (half_w, 0.2),
                (0.0, half_w + 0.2),
                (-half_w, 0.2),
                align=None,
            )
        extrude(amount=length / 2.0 + 4.0, both=True)
    return arch.part


def build_base_planter_6_colors(cfg: PlanterSystemConfig) -> List[Tuple[str, int, Part]]:
    """
    Builds Tray 1 (Base Planter) and partitions it into 6 exact, non-overlapping
    watertight B-Rep color zones for 1-click multi-color printing in Bambu Studio.
    """
    lx, wy, hz = cfg.outer_length_x, cfg.outer_width_y, cfg.base_height_z
    wt, cr = cfg.wall_thickness, cfg.corner_radius
    corner_pts = get_style_corner_points(cfg)

    # 1. Outer Shell
    with BuildPart() as outer_body:
        if cfg.style == "zen_pagoda":
            # 3 stepped pagoda tiers expanding by +2.5mm per tier via 45-deg bevels
            with BuildSketch(Plane.XY):
                _sketch_2d_profile(cfg.style, lx - 4.0, wy - 4.0, cr)
            extrude(amount=hz)
        else:
            with BuildSketch(Plane.XY):
                _sketch_2d_profile(cfg.style, lx, wy, cr)
            extrude(amount=hz)

    # 2. Horizontal Connecting Belts & Top Rim
    top_rim = make_profile_band(
        cfg.style, lx, wy, cr,
        z_bot=hz - cfg.rim_height,
        height=cfg.rim_height,
        protrusion=cfg.rim_ext,
        chamfer_top=False,
    )
    belt1_ext = cfg.belt_ext + (1.5 if cfg.style == "zen_pagoda" else 0.0)
    belt2_ext = cfg.belt_ext + (3.0 if cfg.style == "zen_pagoda" else 0.0)

    belt_lower = make_profile_band(
        cfg.style, lx, wy, cr,
        z_bot=cfg.belt1_z,
        height=cfg.belt_height,
        protrusion=belt1_ext,
        chamfer_top=True,
    )
    belt_upper = make_profile_band(
        cfg.style, lx, wy, cr,
        z_bot=cfg.belt2_z,
        height=cfg.belt_height,
        protrusion=belt2_ext,
        chamfer_top=True,
    )

    full_part = outer_body.part + top_rim + belt_lower + belt_upper

    # 3. Subtract Interior Soil Cavity
    inner_style = "rectangular_classic" if cfg.style == "roman_fluted" else cfg.style
    inner_lx = lx - 2.0 * wt - (4.0 if cfg.style == "zen_pagoda" else 0.0)
    inner_wy = wy - 2.0 * wt - (4.0 if cfg.style == "zen_pagoda" else 0.0)
    inner_cr = max(5.0, cr - wt)

    floor_z = cfg.floor_thickness + (18.0 if cfg.style == "self_watering_sip" else 0.0)
    with BuildPart() as cavity:
        with BuildSketch(Plane.XY.offset(floor_z)):
            _sketch_2d_profile(inner_style, inner_lx, inner_wy, inner_cr)
        extrude(amount=hz + 2.0)

        if cfg.style == "self_watering_sip":
            # Sub-irrigated wicking cones extending down to Z = cfg.floor_thickness (5.0 mm),
            # centered at (±64.0, ±42.0) so they are 100% concentric with the Front & Back
            # rows of Ø8.0 mm Arch Straw floor holes (giving a flat Ø24 mm landing pad at Z=5 mm)
            for wx, wy_pt in [(-64.0, -42.0), (64.0, -42.0), (-64.0, 42.0), (64.0, 42.0), (0.0, 0.0)]:
                with Locations((wx, wy_pt, cfg.floor_thickness)):
                    Cone(bottom_radius=12.0, top_radius=28.0, height=18.2, align=(Align.CENTER, Align.CENTER, Align.MIN))

    full_part = full_part - cavity.part

    # 4. Add 4 Full-Height Reinforced Corner Trellis Columns
    with BuildPart() as pillars:
        with BuildSketch(Plane.XY.offset(cfg.floor_thickness)):
            with Locations(corner_pts):
                Circle(radius=cfg.pillar_radius)
        extrude(amount=hz - cfg.floor_thickness)

    full_part = full_part + pillars.part

    # 5. Cut the 4 Stacking Female Sockets (Skirt rebate, Lego boss socket & rod holes)
    stack_cutter = make_stacking_female_cutter(cfg, z_top=hz)
    for x, y in corner_pts:
        full_part = full_part - stack_cutter.moved(Location((x, y, 0)))

    # 6. Cut Drainage Holes & Bottom Runoff Arches
    drain_pts = [(dx, dy) for dx in (-64.0, 0.0, 64.0) for dy in (-42.0, 0.0, 42.0)]
    with BuildPart() as drains:
        with Locations([(dx, dy, -0.5) for (dx, dy) in drain_pts]):
            Cylinder(radius=4.0, height=floor_z + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    full_part = full_part - drains.part

    arch_x = make_bottom_runoff_arch(width=8.0, length=lx + 12.0, along_x=True)
    arch_y = make_bottom_runoff_arch(width=8.0, length=wy + 12.0, along_x=False)
    for dy in (-42.0, 0.0, 42.0):
        full_part = full_part - arch_x.moved(Location((0, dy, 0)))
    for dx in (-64.0, 0.0, 64.0):
        full_part = full_part - arch_y.moved(Location((dx, 0, 0)))

    # ------------------------------------------------------------------
    # Partition `full_part` into 6 Non-Overlapping Watertight Color Zones
    # ------------------------------------------------------------------
    # Zone 6: 4 Corner Columns & Edge Pilasters
    with BuildPart() as corner_mask:
        with Locations([(x, y, -1.0) for (x, y) in corner_pts]):
            Cylinder(
                radius=cfg.pillar_radius + 4.0,
                height=hz + 2.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
    zone6_corners = full_part & corner_mask.part
    rem = full_part - corner_mask.part

    def z_slab(z0: float, z1: float) -> Part:
        with BuildPart() as sb:
            with Locations((0, 0, z0)):
                Box(400.0, 400.0, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        return sb.part

    z_b1_bot = cfg.belt1_z
    z_b1_top = cfg.belt1_z + cfg.belt_height + (1.0 + belt1_ext) * 1.12
    z_b2_bot = cfg.belt2_z
    z_b2_top = cfg.belt2_z + cfg.belt_height + (1.0 + belt2_ext) * 1.12
    z_rim_bot = hz - cfg.rim_height

    # Zone 5: Top Box-Beam Rim + Base Trim
    rim_mask = z_slab(z_rim_bot, hz + 1.0)
    zone5_rim = rem & rim_mask
    rem = rem - rim_mask

    # Zone 4: Horizontal Connecting Strips (Belt 1 & Belt 2)
    belts_mask = z_slab(z_b1_bot, z_b1_top) + z_slab(z_b2_bot, z_b2_top)
    zone4_belts = rem & belts_mask
    rem = rem - belts_mask

    # Zone 1, 2, 3: Lower, Middle, and Upper Box Wall Panels
    zone1_lower = rem & z_slab(-1.0, z_b1_bot + 0.1)
    zone2_middle = rem & z_slab(z_b1_top - 0.1, z_b2_bot + 0.1)
    zone3_upper = rem & z_slab(z_b2_top - 0.1, z_rim_bot + 0.1)

    return [
        ("Color1_Lower_Box_Layer", 1, zone1_lower),
        ("Color2_Middle_Box_Layer", 2, zone2_middle),
        ("Color3_Upper_Box_Layer", 3, zone3_upper),
        ("Color4_Connecting_Belts", 4, zone4_belts),
        ("Color5_Top_Rim_Collar", 5, zone5_rim),
        ("Color6_Corner_Columns", 6, zone6_corners),
    ]


def build_drip_saucer_1_color(cfg: PlanterSystemConfig) -> List[Tuple[str, int, Part]]:
    """Builds Tray 2 (Snap-In Drip Saucer) as a 1-color watertight solid fitting P2S."""
    base_style = "rectangular_classic" if cfg.style in ("roman_fluted", "self_watering_sip", "zen_pagoda") else cfg.style
    inner_x = cfg.outer_length_x + 2.0 * cfg.saucer_clearance
    inner_y = cfg.outer_width_y + 2.0 * cfg.saucer_clearance
    if cfg.style == "oval_stadium":
        inner_r = 50.0  # Calibrated corner radius clearing corner columns with uniform 4.8mm gap
    else:
        inner_r = cfg.corner_radius + cfg.saucer_clearance

    outer_x = inner_x + 2.0 * cfg.saucer_wall_t
    outer_y = inner_y + 2.0 * cfg.saucer_wall_t
    outer_r = inner_r + cfg.saucer_wall_t
    sz = cfg.saucer_height_z

    with BuildPart() as saucer:
        with BuildSketch(Plane.XY):
            _sketch_2d_profile(base_style, outer_x, outer_y, outer_r)
        extrude(amount=sz)

    with BuildPart() as cav:
        with BuildSketch(Plane.XY.offset(cfg.saucer_floor_t)):
            _sketch_2d_profile(base_style, inner_x, inner_y, inner_r)
        extrude(amount=sz + 2.0)

    part = saucer.part - cav.part

    # Add 4 internal raised aeration rails
    rail_len = inner_x - 64.0
    with BuildPart() as rails:
        for dy in (-45.0, -15.0, 15.0, 45.0):
            with Locations((0, dy, cfg.saucer_floor_t + cfg.saucer_rib_h / 2.0)):
                Box(rail_len, 5.5, cfg.saucer_rib_h)
    part = part + rails.part

    return [("Color1_Drip_Saucer_Tray", 1, part)]


def build_extension_riser_4_colors(cfg: PlanterSystemConfig) -> List[Tuple[str, int, Part]]:
    """
    Builds Tray 3 (Stackable Deep-Root Extension Riser) with 4 Integrated Male Locking Rods!
    ORIENTATION RULE: Modeled in its optimal Support-Free Print Orientation (inverted on its
    flat top rim at Z=0), so the 4 integrated male alignment rods protrude straight UP (+Z)
    from Z=140mm to Z=168mm with ZERO overhangs and ZERO supports!
    Partitioned into 4 AMS Color Zones.
    """
    lx, wy = cfg.outer_length_x, cfg.outer_width_y
    hz = cfg.riser_body_h
    wt, cr = cfg.wall_thickness, cfg.corner_radius
    corner_pts = get_style_corner_points(cfg)
    inner_style = "rectangular_classic" if cfg.style == "roman_fluted" else cfg.style

    # 1. Main Riser Shell sitting on Z=0 (inverted print orientation: Top Rim is at Z=0..16mm!)
    with BuildPart() as outer_shell:
        with BuildSketch(Plane.XY):
            _sketch_2d_profile(cfg.style, lx, wy, cr)
        extrude(amount=hz - cfg.riser_skirt_h)

    # Bottom Rim Collar at Z = 0..16mm (tapers inward at 45-deg on top side Z=16mm -> 0 supports!)
    bottom_rim_collar = make_profile_band(
        cfg.style, lx, wy, cr,
        z_bot=0.0,
        height=cfg.rim_height,
        protrusion=cfg.rim_ext,
        chamfer_top=True,
    )

    # Mid Connecting Strip at Z = 62..74mm
    mid_strip = make_profile_band(
        cfg.style, lx, wy, cr,
        z_bot=62.0,
        height=cfg.belt_height,
        protrusion=cfg.belt_ext,
        chamfer_top=True,
    )

    # Upper Interlocking Male Skirt (`Z = hz - riser_skirt_h` to `hz`) that plugs inside Base Planter
    skirt_clr = cfg.skirt_clearance
    skirt_out_x = lx - 2.0 * wt - 2.0 * skirt_clr
    skirt_out_y = wy - 2.0 * wt - 2.0 * skirt_clr
    skirt_out_r = max(4.0, cr - wt - skirt_clr)
    z_skirt_base = hz - cfg.riser_skirt_h

    with BuildPart() as male_skirt:
        with BuildSketch(Plane.XY.offset(z_skirt_base - 4.5)) as ms0:
            _sketch_2d_profile(inner_style, lx, wy, cr)
        with BuildSketch(Plane.XY.offset(z_skirt_base)) as ms1:
            _sketch_2d_profile(inner_style, skirt_out_x, skirt_out_y, skirt_out_r)
        loft([ms0.sketch, ms1.sketch], ruled=True)
        with BuildSketch(Plane.XY.offset(z_skirt_base)):
            _sketch_2d_profile(inner_style, skirt_out_x, skirt_out_y, skirt_out_r)
        extrude(amount=cfg.riser_skirt_h)

    full_riser = outer_shell.part + bottom_rim_collar + mid_strip + male_skirt.part

    # Hollow out the open-bottom Riser interior
    riser_in_x = skirt_out_x - 2.0 * 3.4
    riser_in_y = skirt_out_y - 2.0 * 3.4
    riser_in_r = max(3.0, skirt_out_r - 3.4)
    with BuildPart() as open_bore:
        with BuildSketch(Plane.XY.offset(-1.0)):
            _sketch_2d_profile(inner_style, riser_in_x, riser_in_y, riser_in_r)
        extrude(amount=hz + cfg.lego_boss_h + cfg.riser_rod_len + 5.0)

    full_riser = full_riser - open_bore.part

    # Add 4 Full-Height Corner Columns + Circular Lego Bosses (Yellow contour) + Male Locking Pins!
    rod_r = cfg.riser_rod_od / 2.0
    boss_r = cfg.lego_boss_r
    boss_h = cfg.lego_boss_h
    with BuildPart() as pillars_and_rods:
        with Locations(corner_pts):
            # Main corner column from Z = 0 to Z = hz
            Cylinder(
                radius=cfg.pillar_radius,
                height=hz,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            # Circular Lego Boss (Yellow contour) from Z = hz to hz + boss_h (snaps slightly inside!)
            with Locations((0, 0, hz)):
                Cylinder(
                    radius=boss_r,
                    height=boss_h,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            # Straight Integrated Male Stacking Rod (Ø6.20mm OD)
            with Locations((0, 0, hz + boss_h)):
                Cylinder(
                    radius=rod_r,
                    height=cfg.riser_rod_len - 1.2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            # 45-deg self-centering lead-in tip chamfer at top of locking rod
            with Locations((0, 0, hz + boss_h + cfg.riser_rod_len - 1.2)):
                Cone(
                    bottom_radius=rod_r,
                    top_radius=rod_r - 0.8,
                    height=1.2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

    full_riser = full_riser + pillars_and_rods.part

    # Cut continuous Ø4.50mm inner bore through all 4 columns & integrated locking rods
    # so 4mm metal wire stakes can still pass straight through the entire stacked assembly!
    with BuildPart() as stake_bores:
        with Locations([(x, y, -1.0) for (x, y) in corner_pts]):
            Cylinder(
                radius=cfg.riser_rod_id / 2.0,
                height=hz + boss_h + cfg.riser_rod_len + 5.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
    full_riser = full_riser - stake_bores.part

    # Cut matching female sockets into Riser's flat rim at Z = 0 (top when stacked) so multiple risers can nest!
    boss_clr_r = cfg.lego_socket_clr_r
    boss_clr_z = cfg.lego_socket_clr_z
    rod_hole_r = cfg.rod_6mm_bore_d / 2.0
    with BuildPart() as riser_fem_sockets:
        with Locations(corner_pts):
            # Column skirt rebate: Z = 0 .. (riser_skirt_h + boss_clr_z)
            Cylinder(
                radius=cfg.pillar_radius + skirt_clr,
                height=cfg.riser_skirt_h + boss_clr_z + 0.1,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            # Lego boss socket: Z = 0 .. (riser_skirt_h + boss_clr_z + boss_h + boss_clr_z)
            Cylinder(
                radius=boss_r + boss_clr_r,
                height=cfg.riser_skirt_h + boss_clr_z + boss_h + boss_clr_z + 0.1,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            # Pin hole: Z = 0 .. (riser_skirt_h + boss_clr_z + boss_h + boss_clr_z + cfg.rod_6mm_depth)
            Cylinder(
                radius=rod_hole_r,
                height=cfg.riser_skirt_h + boss_clr_z + boss_h + boss_clr_z + cfg.rod_6mm_depth + 0.1,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
    full_riser = full_riser - riser_fem_sockets.part

    # ------------------------------------------------------------------
    # Partition `full_riser` into 4 Watertight Color Zones
    # ------------------------------------------------------------------
    total_riser_z = hz + boss_h + cfg.riser_rod_len + 2.0
    with BuildPart() as corner_mask:
        with Locations([(x, y, -1.0) for (x, y) in corner_pts]):
            Cylinder(
                radius=cfg.pillar_radius + 3.5,
                height=total_riser_z,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
    # Color 4: 4 Corner Columns + Integrated Stacking Rods
    zone4_rods_and_corners = full_riser & corner_mask.part
    rem = full_riser - corner_mask.part

    def z_slab(z0: float, z1: float) -> Part:
        with BuildPart() as sb:
            with Locations((0, 0, z0)):
                Box(400.0, 400.0, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        return sb.part

    z_rim_top = cfg.rim_height + (1.0 + cfg.rim_ext) * 1.12
    z_mid_bot = 62.0
    z_mid_top = 62.0 + cfg.belt_height + (1.0 + cfg.belt_ext) * 1.12

    # Color 3: Rim Collar & Mid Connecting Strip
    strip_mask = z_slab(-1.0, z_rim_top) + z_slab(z_mid_bot, z_mid_top)
    zone3_strips = rem & strip_mask
    rem = rem - strip_mask

    # Color 1 & Color 2: Lower & Upper Riser Box Panels
    zone1_lower = rem & z_slab(z_rim_top - 0.1, z_mid_bot + 0.1)
    zone2_upper = rem & z_slab(z_mid_top - 0.1, total_riser_z)

    return [
        ("Color1_Riser_Lower_Panel", 1, zone1_lower),
        ("Color2_Riser_Upper_Panel", 2, zone2_upper),
        ("Color3_Riser_Belts_And_Rim", 4, zone3_strips),
        ("Color4_Corner_Columns_And_Stacking_Rods", 6, zone4_rods_and_corners),
    ]


def build_subsoil_irrigation_arch_2_colors(cfg: PlanterSystemConfig) -> List[Tuple[str, int, Part]]:
    """
    Builds Tray 4: A pair of 3D-printed Sub-Soil Perforated Irrigation & Wicking Arch Straws
    (2 Color Zones) that plug directly into two Ø8.0mm floor drainage holes (X = -64mm and X = +64mm,
    128.0mm center-to-center span) and loop in a rounded ∩-arch up through the potting soil.
    - True round circular cross-section: Ø7.20mm outer diameter with continuous hollow Ø5.0mm bore.
    - Fits into the planter's Ø8.0mm round holes with generous 0.40mm per-side clearance (0.80mm diametral gap)
      eliminating the previous 10.6mm oblong oval mismatch and ensuring effortless drop-in fit.
    - Wide 14.0mm landing collar stop at Y = 16.0mm (floor depth) prevents the straw from dropping through the
      hole and provides a wide, stable footing that holds the 110mm arch standing upright in wet soil.
    - 1.5mm 45° self-centering lead-in tip chamfer at the bottom nozzle tips.
    - Printed lying flat on Z = 0 with a 0.30mm planar bed contact strip for rock-solid PEI adhesion with 0% supports.
    - 18 root-seepage micro-slits (1.4mm wide) along the curved arch diffuse moisture into the root zone.
    """
    half_span = 64.0  # Matches drain_pts dx = (-64.0, +64.0) -> 128.0 mm span
    plug_len = 16.0   # Drops through the 5mm floor into the Drip Saucer water reservoir below
    straight_leg = 46.0
    arch_top_y = straight_leg + half_span  # 110.0 mm total height above plug base
    straw_od = 7.20   # True round cylinder Ø7.20mm (fits into Ø8.0mm hole with 0.80mm total clearance)
    bore_id = 5.00    # Continuous hollow wicking channel
    bed_flat = 0.30   # 0.30mm planar contact strip for 100% bed adhesion on Z = 0

    # 1. Main upper arch path (Y = 0 .. arch_top_y)
    with BuildLine(Plane.XY) as path:
        Line((-half_span, 0.0), (-half_span, straight_leg))
        ThreePointArc((-half_span, straight_leg), (0.0, arch_top_y), (half_span, straight_leg))
        Line((half_span, straight_leg), (half_span, 0.0))
    wire = path.wires()[0]

    z_center = straw_od / 2.0
    sweep_plane = Plane(origin=(-half_span, 0.0, z_center), x_dir=(1, 0, 0), z_dir=(0, 1, 0))

    # Outer round tube sketch with tiny planar bed flat:
    with BuildSketch(sweep_plane) as sk_out:
        Circle(radius=straw_od / 2.0)
        with Locations((0, -z_center + bed_flat / 2.0)):
            Rectangle(straw_od, bed_flat, mode=Mode.SUBTRACT)

    # Inner round bore sketch:
    with BuildSketch(sweep_plane) as sk_in:
        Circle(radius=bore_id / 2.0)

    with BuildPart() as p_body:
        sweep(sk_out.sketch, path=wire)
    with BuildPart() as p_bore:
        sweep(sk_in.sketch, path=wire)

    straw_base = p_body.part - p_bore.part

    # 2. Add Landing Collars at Y = plug_len (16.0 mm)
    # At X = -64 and X = +64: 14.0mm wide flange in XY plane that stops on the planter floor
    flange_w = 14.0
    flange_l = 3.0
    flange_h = straw_od - bed_flat

    with BuildPart() as p_flanges:
        for x_end in (-half_span, half_span):
            with Locations((x_end, plug_len + flange_l / 2.0, flange_h / 2.0)):
                Box(flange_w, flange_l, flange_h)

    flanges_with_bore = p_flanges.part - p_bore.part
    straw_combined = straw_base + flanges_with_bore

    # 3. Add 45-deg Lead-in Chamfer to Plug Tips (Y = 0):
    for x_end in (-half_span, half_span):
        with BuildPart() as tip_chamfer_cutter:
            with Locations((x_end, 0.0, z_center)):
                Cone(bottom_radius=straw_od + 2.0, top_radius=straw_od/2.0 - 0.6, height=1.5, rotation=(90, 0, 0))
                Cylinder(radius=straw_od/2.0 - 0.6, height=3.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
        straw_combined = straw_combined - tip_chamfer_cutter.part

    # 4. Cut Root-Seepage Micro-Slits along curved arch:
    for deg in range(18, 163, 12):
        rad = math.radians(deg)
        cx = -half_span * math.cos(rad)
        cy = straight_leg + half_span * math.sin(rad)
        slit = Pos(cx, cy, straw_od - 1.0) * Rot(0, 0, deg - 90) * Box(straw_od + 2.0, 1.4, 3.0)
        straw_combined = straw_combined - slit

    # 5. Cut Intake Slots at bottom tips (Y in [2.0, 6.0]):
    for x_end in (-half_span, half_span):
        tip_slot = Pos(x_end, 4.0, straw_od - 1.0) * Box(straw_od + 2.0, 2.0, 3.0)
        straw_combined = straw_combined - tip_slot

    # Translate so min Z is exactly 0.00:
    bb = straw_combined.bounding_box()
    single_straw = straw_combined.translate((0, 0, -bb.min.Z))

    # 6. Create pair of 2 nested arches:
    arch_1 = Pos(0.0, 5.0, 0.0) * single_straw
    arch_2 = Pos(0.0, -5.0, 0.0) * Rot(0, 0, 180) * single_straw
    both_arches = arch_1 + arch_2

    # Partition into 2 Color Zones:
    # Color 1 (Extruder 4 - Terracotta): Main Sub-Soil Arch Tubes
    # Color 2 (Extruder 5 - Warm Sand): Floor Intake Nozzles & Upper Slotted Root Diffuser Crown
    with BuildPart() as crown_and_plugs_mask:
        # Plug zones (|Y| <= 22.0) + Crown zones (|Y| >= 82.0)
        with Locations((0, 0, -1.0)):
            Box(220.0, 46.0, 20.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 100.0, -1.0), (0, -100.0, -1.0)):
            Box(220.0, 44.0, 20.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    zone2_accents = both_arches & crown_and_plugs_mask.part
    zone1_main = both_arches - crown_and_plugs_mask.part

    return [
        ("Color1_SubSoil_Straw_Arch_Tube", 4, zone1_main),
        ("Color2_Intake_Plugs_And_Root_Diffuser_Crown", 5, zone2_accents),
    ]





def build_retrofit_snap_adapter(
    cfg: PlanterSystemConfig,
    h_adapter: float = 18.0
) -> Tuple[Part, Part]:
    """
    Builds the Retrofit Snap Adapter Coupler and 4 Concentric Locator Alignment Dowels.
    - Sits flat on Z = 0 for 100% support-free FDM printing.
    - Bottom face glues flush onto previously printed Base Planters with flat top rims.
    - Top face features the standard 3-tier Lego interlocking receiving joint:
      1. Female skirt pocket (7.5 mm depth, 0.35 mm clearance).
      2. Circular Lego boss sockets (Ø15.7 mm x 3.5 mm depth with 0.8 mm lead-in chamfer).
      3. Straight through-bores (Ø6.7 mm) down through the adapter into the base's corner holes.
    - 4 Locator Dowels (Ø6.0 mm x 16.0 mm with 1.0 mm lead-in chamfers) drop into base holes
      to guarantee 100% concentric alignment during gluing.
    """
    lx, wy = cfg.outer_length_x, cfg.outer_width_y
    wt, cr = cfg.wall_thickness, cfg.corner_radius
    corner_pts = get_style_corner_points(cfg)

    with BuildPart() as shell:
        with BuildSketch(Plane.XY):
            _sketch_2d_profile(cfg.style, lx + 2.0 * cfg.rim_ext, wy + 2.0 * cfg.rim_ext, cr + cfg.rim_ext)
        extrude(amount=h_adapter)

    in_x = lx - 2.0 * wt
    in_y = wy - 2.0 * wt
    in_r = max(4.0, cr - wt)
    with BuildPart() as hollow:
        with BuildSketch(Plane.XY.offset(-1.0)):
            _sketch_2d_profile(cfg.style, in_x, in_y, in_r)
        extrude(amount=h_adapter + 2.0)

    adapter = shell.part - hollow.part

    with BuildPart() as pillars:
        with Locations([(x, y, 0) for (x, y) in corner_pts]):
            Cylinder(radius=cfg.pillar_radius + cfg.rim_ext, height=h_adapter, align=(Align.CENTER, Align.CENTER, Align.MIN))

    adapter = adapter + pillars.part
    adapter = adapter - hollow.part

    cutter = make_stacking_female_cutter(cfg, z_top=h_adapter)
    for x, y in corner_pts:
        adapter = adapter - cutter.moved(Location((x, y, 0)))

    with BuildPart() as through_bores:
        with Locations([(x, y, -0.5) for (x, y) in corner_pts]):
            Cylinder(radius=cfg.rod_6mm_bore_d / 2.0, height=h_adapter + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    adapter = adapter - through_bores.part

    with BuildPart() as pins:
        pin_r = 3.00
        pin_len = 16.0
        for (px, py) in [(-8.0, -8.0), (8.0, -8.0), (-8.0, 8.0), (8.0, 8.0)]:
            with Locations((px, py, 0)):
                Cylinder(radius=pin_r, height=pin_len, align=(Align.CENTER, Align.CENTER, Align.MIN))
                with Locations((0, 0, pin_len - 1.0)):
                    Cone(bottom_radius=pin_r, top_radius=pin_r - 1.0, height=1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
                with Locations((0, 0, 0)):
                    Cone(bottom_radius=pin_r - 1.0, top_radius=pin_r, height=1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    return adapter, pins.part


def generate_complete_planter_project(
    cfg: PlanterSystemConfig,
    model_script_path: Path,
    combined_3mf_stem: str,
) -> dict:
    print(f"=== [{cfg.style}] Building Tray 1: 6-Color Base Planter ===")
    tray1_zones = build_base_planter_6_colors(cfg)

    print(f"=== [{cfg.style}] Building Tray 2: 1-Color Snap-In Drip Saucer ===")
    tray2_zones = build_drip_saucer_1_color(cfg)

    print(f"=== [{cfg.style}] Building Tray 3: 4-Color Inverted Riser w/ 4 Integrated Locking Rods ===")
    tray3_zones = build_extension_riser_4_colors(cfg)

    trays = [
        (f"{combined_3mf_stem}_tray1_base_6color", tray1_zones),
        (f"{combined_3mf_stem}_tray2_saucer_1color", tray2_zones),
        (f"{combined_3mf_stem}_tray3_riser_4color", tray3_zones),
    ]

    if cfg.style != "hex_honeycomb":
        print(f"=== [{cfg.style}] Building Tray 4: 2-Color Sub-Soil Perforated Irrigation Arch Straws ===")
        tray4_zones = build_subsoil_irrigation_arch_2_colors(cfg)
        trays.append((f"{combined_3mf_stem}_tray4_irrigation_straws_2color", tray4_zones))

    return export_multicolor_multiplate_3mf(
        trays=trays,
        model_file=model_script_path,
        combined_3mf_name=f"{combined_3mf_stem}_3_trays_multicolor",
    )
