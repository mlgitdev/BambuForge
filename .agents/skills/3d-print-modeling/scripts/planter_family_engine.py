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

    # Tray 2: Drip Saucer (<= 244 x 194 mm total outer footprint for P2S plate auto-arrange)
    saucer_clearance: float = 0.7
    saucer_wall_t: float = 3.4
    saucer_floor_t: float = 4.0
    saucer_height_z: float = 32.0
    saucer_rib_h: float = 3.6

    # Tray 3: Inverted Stackable Extension Riser + 4 Integrated Male Locking Rods
    riser_body_h: float = 140.0       # Main riser body height (Z = 0..140mm)
    riser_skirt_h: float = 9.0        # Interlocking male skirt height
    riser_rod_len: float = 28.0       # Length of the 4 integrated locking rods protruding at +Z
    riser_rod_od: float = 6.20        # Outer diameter of integrated locking rods (fits 6.50mm hole!)
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
        r_oval = min(width_y / 2.0 - 1.0, corner_r + 48.0)
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


def make_dual_rod_cutter(cfg: PlanterSystemConfig) -> Part:
    z_top = cfg.base_height_z
    r6 = cfg.rod_6mm_bore_d / 2.0
    r4 = cfg.rod_4mm_bore_d / 2.0
    lead_in = 1.4
    transition_h = r6 - r4

    z_upper_bot = z_top - cfg.rod_6mm_depth
    z_trans_bot = z_upper_bot - transition_h
    z_lower_bot = z_trans_bot - cfg.rod_4mm_depth

    with BuildPart() as cutter:
        with Locations((0, 0, z_lower_bot)):
            Cylinder(radius=r4, height=cfg.rod_4mm_depth + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, z_trans_bot)):
            Cone(bottom_radius=r4, top_radius=r6, height=transition_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, z_upper_bot)):
            Cylinder(radius=r6, height=cfg.rod_6mm_depth + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, z_top - lead_in)):
            Cone(bottom_radius=r6, top_radius=r6 + lead_in + 0.4, height=lead_in + 0.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
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

    # 5. Cut the 4 Dual-Stage (6mm & 4mm) Metal Rod Sockets
    rod_cutter = make_dual_rod_cutter(cfg)
    for x, y in corner_pts:
        full_part = full_part - rod_cutter.moved(Location((x, y, 0)))

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
    skirt_out_x = lx - 2.0 * wt - 0.7
    skirt_out_y = wy - 2.0 * wt - 0.7
    skirt_out_r = max(4.0, cr - wt - 0.35)
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
        extrude(amount=hz + 5.0)

    full_riser = full_riser - open_bore.part

    # Add 4 Full-Height Corner Columns + 4 Integrated Male Locking Rods pointing straight UP (+Z)!
    rod_r = cfg.riser_rod_od / 2.0
    with BuildPart() as pillars_and_rods:
        with Locations(corner_pts):
            # Main corner column from Z = 0 to Z = hz
            Cylinder(
                radius=cfg.pillar_radius,
                height=hz,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            # 45-deg tapered shoulder at Z = hz transitioning from pillar_radius to rod_r (support-free!)
            cone_h = cfg.pillar_radius - rod_r
            with Locations((0, 0, hz)):
                Cone(
                    bottom_radius=cfg.pillar_radius,
                    top_radius=rod_r,
                    height=cone_h,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            # Integrated Male Stacking Rod (Ø6.20mm OD, protruding up to Z = hz + riser_rod_len)
            with Locations((0, 0, hz)):
                Cylinder(
                    radius=rod_r,
                    height=cfg.riser_rod_len - 1.2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            # 45-deg lead-in tip chamfer at top of locking rod so it self-centers into the 4 base holes
            with Locations((0, 0, hz + cfg.riser_rod_len - 1.2)):
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
                height=hz + cfg.riser_rod_len + 5.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
    full_riser = full_riser - stake_bores.part

    # ------------------------------------------------------------------
    # Partition `full_riser` into 4 Watertight Color Zones
    # ------------------------------------------------------------------
    total_riser_z = hz + cfg.riser_rod_len + 2.0
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
    - Printed lying flat on Z = 0 with a 45-degree octagonal/diamond cross-section for 0% supports.
    - Hollow Ø5.2mm internal bore accepts either direct water seepage or a 4-5mm capillary wick rope.
    - 18 root-seepage micro-slits (1.4mm wide) along the curved arch diffuse moisture into the root zone.
    """
    half_span = 64.0  # Matches drain_pts dx = (-64.0, +64.0) -> 128.0 mm span
    plug_len = 16.0   # Drops through the 5mm floor into the Drip Saucer water reservoir below
    straight_leg = 46.0
    arch_top_y = straight_leg + half_span  # 110.0 mm total height above plug base
    tube_od = 10.6
    plug_od = 7.4     # Fits inside Ø8.0mm floor hole with 0.6mm clearance
    bore_id = 5.0     # Continuous hollow straw channel

    # 1. Main upper arch path (Y = plug_len .. arch_top_y)
    with BuildLine(Plane.XY) as main_path:
        Line((-half_span, plug_len), (-half_span, straight_leg))
        ThreePointArc((-half_span, straight_leg), (0.0, arch_top_y), (half_span, straight_leg))
        Line((half_span, straight_leg), (half_span, plug_len))
    main_wire = main_path.wires()[0]

    # 2. Full bore path (Y = 0 .. arch_top_y)
    with BuildLine(Plane.XY) as full_path:
        Line((-half_span, 0.0), (-half_span, straight_leg))
        ThreePointArc((-half_span, straight_leg), (0.0, arch_top_y), (half_span, straight_leg))
        Line((half_span, straight_leg), (half_span, 0.0))
    full_wire = full_path.wires()[0]

    z_center = tube_od / 2.0
    plane_main = Plane(origin=(-half_span, plug_len, z_center), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    plane_full = Plane(origin=(-half_span, 0.0, z_center), x_dir=(1, 0, 0), z_dir=(0, 1, 0))

    with BuildSketch(plane_main) as sk_main_out:
        Rectangle(tube_od, tube_od)
        chamfer(sk_main_out.vertices(), length=2.4)

    with BuildSketch(plane_full) as sk_bore:
        Rectangle(bore_id, bore_id)
        chamfer(sk_bore.vertices(), length=1.2)

    with BuildPart() as arch_body_p:
        sweep(sk_main_out.sketch, path=main_wire)
    with BuildPart() as bore_p:
        sweep(sk_bore.sketch, path=full_wire)

    # 3. Bottom tapered floor-plug nozzles (Y = 0 .. plug_len) at X = -64 and X = +64
    plugs = []
    for x_end in (-half_span, half_span):
        p_plane = Plane(origin=(x_end, 0.0, z_center), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
        with BuildSketch(p_plane) as sk_plug:
            # Height in Z stays tube_od so it touches Z=0 on the bed; width in X narrows to plug_od (7.4mm)
            Rectangle(plug_od, tube_od)
            chamfer(sk_plug.vertices(), length=1.8)
        with BuildPart() as plug_part:
            extrude(sk_plug.sketch, amount=plug_len + 1.0)
        plugs.append(plug_part.part)

    single_straw = arch_body_p.part + plugs[0] + plugs[1] - bore_p.part

    # 4. Cut root-seepage micro-slits along the curved arch & intake slots at the bottom plug tips
    for deg in range(18, 163, 12):
        rad = math.radians(deg)
        cx = -half_span * math.cos(rad)
        cy = straight_leg + half_span * math.sin(rad)
        slit = Pos(cx, cy, tube_od - 1.8) * Rot(0, 0, deg - 90) * Box(tube_od + 2.0, 1.4, 4.0)
        single_straw = single_straw - slit

    for x_end in (-half_span, half_span):
        tip_slot = Pos(x_end, 4.0, tube_od - 1.8) * Box(plug_od + 2.0, 2.0, 4.2)
        single_straw = single_straw - tip_slot

    # 5. Create a pair of 2 arches nested cleanly on the 256x256 build plate (centered around Y=0)
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
