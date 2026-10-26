#!/usr/bin/env python3
"""
Reusable build123d Support-Free & Multi-Color Helper Library for Bambu Lab P2S (256x256x256 mm).
Provides:
- P2STolerances: Calibrated fit constants
- make_teardrop_cylinder: Support-free horizontal hole cutter (45-deg roof)
- make_sacrificial_counterbore: Support-free Z=0 counterbore cutter (0.20mm 1-layer bridge)
- export_and_preview: Single-part export & preview
- export_multicolor_multiplate_3mf: Exports multi-tray (Plate 1, Plate 2, Plate 3) AND
  multi-color (6-color Base Planter, 1-color Drip Saucer, 4-color Extension Riser) native
  Bambu Studio `.3mf` and `.step` files pre-configured for Bambu Lab P2S (0.4mm nozzle).
"""

import base64
import json
import math
import shutil
import subprocess
import uuid
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh
from build123d import (
    Align,
    BuildPart,
    BuildSketch,
    Circle,
    Compound,
    Cylinder,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    Polygon,
    Rectangle,
    export_step,
    export_stl,
    extrude,
)

# Default 6-Color Architectural Planter Palette (Hex RGB + RGBA)
DEFAULT_6_PALETTE_HEX = [
    "#2D6A4F",  # Color 1: Deep Forest Green (Lower Box Layer)
    "#40916C",  # Color 2: Botanical Sage Green (Mid Box Layer)
    "#74C69D",  # Color 3: Mint Leaf Green (Upper Box Layer)
    "#E07A5F",  # Color 4: Terracotta Clay (Connecting Strips / Belts)
    "#F2CC8F",  # Color 5: Warm Sandstone Gold (Top & Base Rim Trim)
    "#2B2D42",  # Color 6: Architectural Charcoal Slate (4 Corner Columns & Rods)
]

DEFAULT_6_PALETTE_RGB = [
    np.array([0.18, 0.42, 0.31]),
    np.array([0.25, 0.57, 0.42]),
    np.array([0.45, 0.78, 0.62]),
    np.array([0.88, 0.48, 0.37]),
    np.array([0.95, 0.80, 0.56]),
    np.array([0.17, 0.18, 0.26]),
]


@dataclass(frozen=True)
class P2STolerances:
    """Calibrated Bambu Lab P2S tolerances (mm)."""
    layer_height: float = 0.20
    nozzle_dia: float = 0.40
    line_width: float = 0.42
    press_fit: float = 0.07
    snug_fit: float = 0.14
    sliding_fit: float = 0.22
    loose_fit: float = 0.40
    m3_clearance_d: float = 3.30
    m3_head_d: float = 6.20
    m4_clearance_d: float = 4.30
    m4_head_d: float = 7.60


def make_teardrop_cylinder(
    diameter: float,
    length: float,
    truncate: bool = True,
    axis_plane: Plane = Plane.XZ,
) -> Part:
    r = diameter / 2.0
    s45 = math.sin(math.radians(45))
    c45 = math.cos(math.radians(45))

    with BuildPart() as td_part:
        with BuildSketch(axis_plane):
            Circle(radius=r)
            Polygon(
                (-r * c45, r * s45),
                (r * c45, r * s45),
                (0.0, r * math.sqrt(2.0)),
                align=None,
            )
            if truncate:
                cap_h = r * 1.15
                with Locations((0, (cap_h - r) / 2.0)):
                    Rectangle(
                        width=diameter * 2.2,
                        height=r + cap_h,
                        mode=Mode.INTERSECT,
                    )
        extrude(amount=length / 2.0, both=True)
    return td_part.part


def make_sacrificial_counterbore(
    shaft_d: float = 3.30,
    head_d: float = 6.20,
    head_depth: float = 2.60,
    total_height: float = 15.0,
    layer_height: float = 0.20,
) -> Part:
    eps = 0.05
    with BuildPart() as cb:
        with Locations((0, 0, -eps)):
            Cylinder(
                radius=head_d / 2.0,
                height=head_depth + eps,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        upper_start_z = head_depth + layer_height
        upper_h = max(1.0, total_height - upper_start_z + eps)
        with Locations((0, 0, upper_start_z)):
            Cylinder(
                radius=shaft_d / 2.0,
                height=upper_h,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
    return cb.part


def render_shaded_previews(
    stl_path: Path,
    previews_dir: Path,
    stem: str,
    color_parts: List[Tuple[str, int, Path]] | None = None,
) -> None:
    """
    Renders 4 high-contrast shaded CAD preview PNGs (iso, front, right, top).
    If `color_parts` [(zone_name, extruder_id_1_to_6, zone_stl_path), ...] is supplied,
    each zone is rendered in its assigned multi-color palette!
    """
    light_dir = np.array([-0.45, -0.60, 0.66])
    light_dir /= np.linalg.norm(light_dir)

    all_polys = []
    all_colors = []
    all_verts_list = []

    if color_parts and len(color_parts) > 1:
        for zone_name, ext_id, z_stl in color_parts:
            m = trimesh.load_mesh(str(z_stl))
            if len(m.faces) == 0:
                continue
            v, f = trimesh.remesh.subdivide_to_size(m.vertices, m.faces, max_edge=14.0)
            sm = trimesh.Trimesh(vertices=v, faces=f, process=False)
            norms = sm.face_normals
            inten = np.clip(np.dot(norms, light_dir), 0.0, 1.0)
            base_rgb = DEFAULT_6_PALETTE_RGB[(ext_id - 1) % len(DEFAULT_6_PALETTE_RGB)]
            fc = np.zeros((len(f), 4))
            for i, it in enumerate(inten):
                shade = 0.32 + 0.68 * it
                fc[i, :3] = np.clip(base_rgb * shade, 0.0, 1.0)
                fc[i, 3] = 1.0
            all_polys.append(v[f])
            all_colors.append(fc)
            all_verts_list.append(v)
        polys = np.concatenate(all_polys, axis=0)
        face_colors = np.concatenate(all_colors, axis=0)
        verts = np.concatenate(all_verts_list, axis=0)
    else:
        mesh = trimesh.load_mesh(str(stl_path))
        verts, faces = trimesh.remesh.subdivide_to_size(mesh.vertices, mesh.faces, max_edge=14.0)
        sub_mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
        normals = sub_mesh.face_normals
        intensities = np.clip(np.dot(normals, light_dir), 0.0, 1.0)
        base_rgb = DEFAULT_6_PALETTE_RGB[4] if "saucer" in stem else DEFAULT_6_PALETTE_RGB[0]
        face_colors = np.zeros((len(faces), 4))
        for i, inten in enumerate(intensities):
            shade = 0.32 + 0.68 * inten
            face_colors[i, :3] = np.clip(base_rgb * shade, 0.0, 1.0)
            face_colors[i, 3] = 1.0
        polys = verts[faces]

    mins = verts.min(axis=0)
    maxs = verts.max(axis=0)
    center = (mins + maxs) / 2.0
    max_span = float((maxs - mins).max()) * 0.56

    n_colors = len(color_parts) if color_parts else 1
    views = {
        "iso": (32, -42, f"Isometric View ({n_colors} Color Zones)"),
        "front": (8, -90, f"Front View ({n_colors} Color Zones)"),
        "right": (8, 0, f"Right View ({n_colors} Color Zones)"),
        "top": (88, -90, f"Top View ({n_colors} Color Zones)"),
    }

    for view_key, (elev, azim, title) in views.items():
        fig = plt.figure(figsize=(8.5, 6.5), dpi=140)
        fig.patch.set_facecolor("#161920")
        ax = fig.add_subplot(111, projection="3d")
        ax.set_facecolor("#161920")

        coll = Poly3DCollection(
            polys,
            facecolors=face_colors,
            edgecolors=(0.08, 0.12, 0.16, 0.14),
            linewidths=0.18,
        )
        ax.add_collection3d(coll)

        ax.set_xlim(center[0] - max_span, center[0] + max_span)
        ax.set_ylim(center[1] - max_span, center[1] + max_span)
        ax.set_zlim(center[2] - max_span, center[2] + max_span)
        ax.set_box_aspect([1, 1, 1])
        ax.view_init(elev=elev, azim=azim)

        ax.set_xlabel("X (mm)", color="#9aa5b1", fontsize=8)
        ax.set_ylabel("Y (mm)", color="#9aa5b1", fontsize=8)
        ax.set_zlabel("Z (mm)", color="#9aa5b1", fontsize=8)
        ax.tick_params(colors="#7b8794", labelsize=7)
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.grid(True, color="#2d333b", linestyle="--", linewidth=0.4)

        dims = maxs - mins
        plt.title(
            f"{stem} — {title}\nDimensions: {dims[0]:.1f} × {dims[1]:.1f} × {dims[2]:.1f} mm (P2S Support-Free)",
            color="#e6edf3",
            fontsize=9.5,
            pad=10,
        )

        out_png = previews_dir / f"{stem}_{view_key}.png"
        plt.tight_layout()
        plt.savefig(out_png, facecolor=fig.get_facecolor(), dpi=140)
        plt.close(fig)
        print(f"  -> Rendered {out_png.name}")


def generate_interactive_html_viewer(
    stl_path: Path,
    previews_dir: Path,
    stem: str,
    color_parts: List[Tuple[str, int, Path]] | None = None,
) -> Path:
    """Generates an interactive Three.js 3D viewer supporting multi-color zones."""
    viewer_path = previews_dir / f"{stem}_viewer.html"
    zones_js = []
    if color_parts:
        for z_name, ext_id, z_stl in color_parts:
            b64 = base64.b64encode(z_stl.read_bytes()).decode("ascii")
            hex_c = DEFAULT_6_PALETTE_HEX[(ext_id - 1) % len(DEFAULT_6_PALETTE_HEX)]
            zones_js.append(f'{{ name: "{z_name}", color: "{hex_c}", b64: "{b64}" }}')
    else:
        b64 = base64.b64encode(stl_path.read_bytes()).decode("ascii")
        zones_js.append(f'{{ name: "{stem}", color: "#40916C", b64: "{b64}" }}')

    zones_array_str = ",\n      ".join(zones_js)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{stem} — Multi-Color 3D CAD Viewer (Bambu Lab P2S)</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #12151c; color: #e6edf3; font-family: system-ui, -apple-system, sans-serif; overflow: hidden; }}
    #hud {{
      position: absolute; top: 16px; left: 16px; z-index: 10;
      background: rgba(22, 27, 34, 0.92); border: 1px solid #30363d;
      border-radius: 10px; padding: 14px 18px; max-width: 400px;
      backdrop-filter: blur(8px); box-shadow: 0 8px 24px rgba(0,0,0,0.45);
    }}
    #hud h1 {{ font-size: 15px; font-weight: 600; color: #58a6ff; margin-bottom: 6px; }}
    #hud p {{ font-size: 12px; color: #8b949e; line-height: 1.45; margin-bottom: 6px; }}
    .controls {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }}
    button {{
      background: #21262d; color: #c9d1d9; border: 1px solid #30363d;
      border-radius: 6px; padding: 5px 10px; font-size: 12px; cursor: pointer;
    }}
    button:hover {{ background: #30363d; color: #fff; }}
    .badge {{ display: inline-block; background: #238636; color: #fff; font-size: 11px; padding: 2px 7px; border-radius: 12px; margin-bottom: 6px; }}
  </style>
  <script type="importmap">
    {{
      "imports": {{
        "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
        "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
      }}
    }}
  </script>
</head>
<body>
  <div id="hud">
    <span class="badge">Bambu Lab P2S (256×256×256 mm) — Multi-Color Support-Free</span>
    <h1>{stem}</h1>
    <p><b>Controls:</b> Left-Drag: Orbit | Right-Drag: Pan | Scroll: Zoom</p>
    <div class="controls">
      <button id="btnIso">Isometric</button>
      <button id="btnTop">Top View</button>
      <button id="btnBottom">Bottom View</button>
      <button id="btnWire">Toggle Wireframe</button>
      <button id="btnBed">Toggle P2S Bed Cage</button>
    </div>
  </div>
  <script type="module">
    import * as THREE from 'three';
    import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
    import {{ STLLoader }} from 'three/addons/loaders/STLLoader.js';

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x12151c);
    const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 1, 2500);
    camera.up.set(0, 0, 1);
    camera.position.set(340, -340, 290);

    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 0, 85);
    controls.update();

    scene.add(new THREE.AmbientLight(0xffffff, 0.58));
    const dir1 = new THREE.DirectionalLight(0xffffff, 0.9);
    dir1.position.set(250, -300, 400);
    scene.add(dir1);
    const dir2 = new THREE.DirectionalLight(0x90b4ff, 0.45);
    dir2.position.set(-250, 250, -150);
    scene.add(dir2);

    const bedGroup = new THREE.Group();
    const grid = new THREE.GridHelper(256, 16, 0x3fb950, 0x262c36);
    grid.rotation.x = Math.PI / 2;
    bedGroup.add(grid);
    const boxGeo = new THREE.BoxGeometry(256, 256, 256);
    const edges = new THREE.EdgesGeometry(boxGeo);
    const cage = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({{ color: 0x3fb950, transparent: true, opacity: 0.4 }}));
    cage.position.set(0, 0, 128);
    bedGroup.add(cage);
    scene.add(bedGroup);

    const zones = [
      {zones_array_str}
    ];
    const loader = new STLLoader();
    const mats = [];
    zones.forEach(z => {{
      const bin = atob(z.b64);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      const geo = loader.parse(bytes.buffer);
      geo.computeVertexNormals();
      const mat = new THREE.MeshStandardMaterial({{
        color: new THREE.Color(z.color), roughness: 0.38, metalness: 0.12, side: THREE.DoubleSide
      }});
      mats.push(mat);
      scene.add(new THREE.Mesh(geo, mat));
    }});

    document.getElementById('btnIso').onclick = () => {{ camera.position.set(340, -340, 290); controls.target.set(0, 0, 85); controls.update(); }};
    document.getElementById('btnTop').onclick = () => {{ camera.position.set(0, -1, 420); controls.target.set(0, 0, 85); controls.update(); }};
    document.getElementById('btnBottom').onclick = () => {{ camera.position.set(0, 1, -340); controls.target.set(0, 0, 0); controls.update(); }};
    document.getElementById('btnWire').onclick = () => {{ mats.forEach(m => m.wireframe = !m.wireframe); }};
    document.getElementById('btnBed').onclick = () => {{ bedGroup.visible = !bedGroup.visible; }};

    window.addEventListener('resize', () => {{
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }});

    function animate() {{ requestAnimationFrame(animate); renderer.render(scene, camera); }}
    animate();
  </script>
</body>
</html>
"""
    viewer_path.write_text(html, encoding="utf-8")
    return viewer_path


def _flatten_bambu_json(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    if "inherits" in d and d["inherits"]:
        parent_p = path.parent / f"{d['inherits']}.json"
        if parent_p.exists():
            p = _flatten_bambu_json(parent_p)
            p.update(d)
            d = p
    d.pop("inherits", None)
    d.pop("include", None)
    return d


def _mesh_to_3mf_object_xml(obj_id: int, mesh: trimesh.Trimesh) -> str:
    """Serializes a trimesh object into a 3MF <object><mesh>...</mesh></object> block."""
    v_lines = [
        f'     <vertex x="{v[0]:.5f}" y="{v[1]:.5f}" z="{v[2]:.5f}"/>'
        for v in mesh.vertices
    ]
    t_lines = [
        f'     <triangle v1="{f[0]}" v2="{f[1]}" v3="{f[2]}"/>'
        for f in mesh.faces
    ]
    return (
        f'  <object id="{obj_id}" p:UUID="{uuid.uuid4()}" type="model">\n'
        f'   <mesh>\n'
        f'    <vertices>\n' + "\n".join(v_lines) + "\n    </vertices>\n"
        f'    <triangles>\n' + "\n".join(t_lines) + "\n    </triangles>\n"
        f'   </mesh>\n'
        f'  </object>'
    )


def export_multicolor_multiplate_3mf(
    trays: List[Tuple[str, List[Tuple[str, int, Part]]]],
    model_file: Path,
    combined_3mf_name: str,
) -> dict:
    """
    Exports a Multi-Tray (Plate 1, Plate 2, Plate 3) AND Multi-Color Bambu Studio .3mf project!
    `trays` format:
      [
        ("tray1_base_planter", [("Zone1_Lower_Wall", 1, part1), ("Zone2_Mid_Wall", 2, part2), ...]),
        ("tray2_drip_saucer",  [("Saucer_Body", 1, saucer_part)]),
        ("tray3_riser",        [("Zone1_Riser_Lower", 1, r1), ..., ("Zone4_Corner_Rods", 4, r4)]),
      ]
    """
    model_dir = Path(model_file).resolve().parent
    exports_dir = model_dir / "exports"
    previews_dir = model_dir / "previews"
    zones_dir = exports_dir / "color_zones"
    exports_dir.mkdir(parents=True, exist_ok=True)
    previews_dir.mkdir(parents=True, exist_ok=True)
    zones_dir.mkdir(parents=True, exist_ok=True)

    tray_records = []

    for tray_idx, (tray_name, zone_list) in enumerate(trays, start=1):
        print(f"[Tray {tray_idx}] Exporting Multi-Color Assembly '{tray_name}' ({len(zone_list)} color zones)...")
        # Compute combined bounding box of the tray assembly so all sub-parts shift together by the same -min_z
        all_solids = []
        for _, _, zp in zone_list:
            all_solids.extend(zp.solids())
        comp = Compound(children=all_solids)
        bbox = comp.bounding_box()
        z_shift = -bbox.min.Z if abs(bbox.min.Z) > 1e-5 else 0.0

        # Export multi-body STEP assembly
        shifted_children = []
        zone_meta: List[Tuple[str, int, Path, trimesh.Trimesh]] = []
        combined_meshes = []

        for z_idx, (zone_name, ext_id, zp) in enumerate(zone_list, start=1):
            zp_shifted = zp.moved(Location((0, 0, z_shift))) if z_shift != 0.0 else zp
            zp_shifted.label = zone_name
            shifted_children.append(zp_shifted)

            z_stl = zones_dir / f"{tray_name}_{z_idx}_{zone_name}.stl"
            export_stl(zp_shifted, str(z_stl), tolerance=0.012, angular_tolerance=0.08)
            tm = trimesh.load_mesh(str(z_stl))
            zone_meta.append((zone_name, ext_id, z_stl, tm))
            combined_meshes.append(tm)

        tray_comp = Compound(children=shifted_children)
        tray_step = exports_dir / f"{tray_name}.step"
        tray_stl = exports_dir / f"{tray_name}.stl"
        export_step(tray_comp, str(tray_step))

        merged_mesh = trimesh.util.concatenate(combined_meshes)
        merged_mesh.export(str(tray_stl))

        color_parts_info = [(zn, eid, zpath) for (zn, eid, zpath, _) in zone_meta]
        render_shaded_previews(tray_stl, previews_dir, tray_name, color_parts=color_parts_info)
        generate_interactive_html_viewer(tray_stl, previews_dir, tray_name, color_parts=color_parts_info)

        tray_records.append((tray_idx, tray_name, tray_stl, zone_meta))

    # First generate a valid P2S 3-plate skeleton .3mf via Bambu Studio CLI
    multi_3mf_path = exports_dir / f"{combined_3mf_name}.3mf"
    bambu_exe = Path(r"C:\Program Files\Bambu Studio\bambu-studio.exe")
    prof_dir = Path(r"C:\Program Files\Bambu Studio\resources\profiles\BBL")

    if bambu_exe.exists() and prof_dir.exists():
        m_flat = _flatten_bambu_json(prof_dir / "machine" / "Bambu Lab P2S 0.4 nozzle.json")
        p_flat = _flatten_bambu_json(prof_dir / "process" / "0.20mm Standard @BBL P2S.json")
        # Ensure support-free & structural defaults in the process settings:
        # 3 walls (1.29 mm), 20% Gyroid infill, 5 top/bottom shells (1.0 mm watertight)
        p_flat["enable_support"] = "0"
        p_flat["wall_loops"] = "3"
        p_flat["sparse_infill_density"] = "20%"
        p_flat["sparse_infill_pattern"] = "gyroid"
        p_flat["top_shell_layers"] = "5"
        p_flat["bottom_shell_layers"] = "5"
        f_flat = _flatten_bambu_json(prof_dir / "filament" / "Bambu PETG HF @BBL P2S 0.4 nozzle.json")

        tmp_m = zones_dir / "_p2s_machine.json"
        tmp_p = zones_dir / "_p2s_process.json"
        tmp_m.write_text(json.dumps(m_flat), encoding="utf-8")
        tmp_p.write_text(json.dumps(p_flat), encoding="utf-8")

        fila_paths = []
        for f_idx, hex_col in enumerate(DEFAULT_6_PALETTE_HEX, start=1):
            fd = dict(f_flat)
            fd["default_filament_colour"] = [hex_col]
            fd["filament_colour"] = [hex_col]
            fp = zones_dir / f"_p2s_filament_{f_idx}.json"
            fp.write_text(json.dumps(fd), encoding="utf-8")
            fila_paths.append(str(fp))

        stl_args = [str(tr[2]) for tr in tray_records]
        cmd = [
            str(bambu_exe),
            "--load-settings", f"{tmp_m};{tmp_p}",
            "--load-filaments", ";".join(fila_paths),
            "--arrange", "1",
            "--orient", "0",
            "--export-3mf", str(multi_3mf_path),
            *stl_args,
        ]
        subprocess.run(cmd, capture_output=True, text=True)

    # Now enrich the .3mf archive so each Tray object contains its multi-color sub-parts
    # and the project contains the 6-color filament palette!
    _inject_multicolor_assemblies_into_3mf(multi_3mf_path, tray_records)

    # Run a final round-trip pass through Bambu Studio CLI so it validates all 3 plates
    # and renders OpenGL multi-color plate thumbnails (plate_1.png, plate_2.png, plate_3.png)
    if bambu_exe.exists() and multi_3mf_path.exists():
        verified_3mf = multi_3mf_path.with_suffix(".verified.3mf")
        subprocess.run(
            [str(bambu_exe), "--export-3mf", str(verified_3mf), str(multi_3mf_path)],
            capture_output=True,
            text=True,
        )
        if verified_3mf.exists() and verified_3mf.stat().st_size > 0:
            verified_3mf.replace(multi_3mf_path)

    print(f"[SUCCESS] Multi-Plate (3 Trays) + Multi-Color (6/1/4 Colors) 3MF saved to: {multi_3mf_path}")

    return {"multi_plate_3mf": str(multi_3mf_path)}


def _get_part_slicing_overrides_xml(z_name: str) -> str:
    """Returns per-part Bambu Studio process overrides (wall_loops, sparse_infill_density, sparse_infill_pattern)."""
    zn = z_name.lower()
    if "straw" in zn or "plug" in zn or "diffuser" in zn:
        # Sub-soil irrigation arch straws & intake plugs: 3 walls + 100% solid infill
        return (
            '      <metadata key="wall_loops" value="3"/>\n'
            '      <metadata key="sparse_infill_density" value="100%"/>\n'
            '      <metadata key="sparse_infill_pattern" value="rectilinear"/>\n'
        )
    if "corner" in zn or "rod" in zn:
        # 4 Corner trellis columns & riser corner columns: 4 walls + 40% Gyroid infill
        return (
            '      <metadata key="wall_loops" value="4"/>\n'
            '      <metadata key="sparse_infill_density" value="40%"/>\n'
            '      <metadata key="sparse_infill_pattern" value="gyroid"/>\n'
        )
    if "belt" in zn or "rim" in zn or "collar" in zn:
        # Horizontal structural reinforcing belts & top rim collar: 3 walls + 35% Gyroid infill
        return (
            '      <metadata key="wall_loops" value="3"/>\n'
            '      <metadata key="sparse_infill_density" value="35%"/>\n'
            '      <metadata key="sparse_infill_pattern" value="gyroid"/>\n'
        )
    if "saucer" in zn:
        # Watertight drip saucer: 4 walls + 25% Gyroid infill + 5 bottom/top shell layers
        return (
            '      <metadata key="wall_loops" value="4"/>\n'
            '      <metadata key="sparse_infill_density" value="25%"/>\n'
            '      <metadata key="sparse_infill_pattern" value="gyroid"/>\n'
            '      <metadata key="bottom_shell_layers" value="5"/>\n'
            '      <metadata key="top_shell_layers" value="5"/>\n'
        )
    # Standard box wall layers: 3 walls + 20% Gyroid infill
    return (
        '      <metadata key="wall_loops" value="3"/>\n'
        '      <metadata key="sparse_infill_density" value="20%"/>\n'
        '      <metadata key="sparse_infill_pattern" value="gyroid"/>\n'
    )


def _inject_multicolor_assemblies_into_3mf(
    threemf_path: Path,
    tray_records: List[Tuple[int, str, Path, List[Tuple[str, int, Path, trimesh.Trimesh]]]],
) -> None:
    """
    Rewrites `3D/Objects/object_N.model`, `3D/3dmodel.model`, `Metadata/model_settings.config`,
    and `Metadata/project_settings.config` inside the Bambu Studio .3mf archive so each Tray
    is a multi-part assembly with pre-assigned filament colors (1..6) AND per-zone structural
    slicing overrides (40% corner infill, 100% locking-rod/socket modifier infill, 20% wall infill).
    """
    if not threemf_path.exists():
        return

    tmp_zip = threemf_path.with_suffix(".tmp.3mf")
    with zipfile.ZipFile(threemf_path, "r") as zin:
        existing_files = {name: zin.read(name) for name in zin.namelist()}

    resources_xml = []
    build_xml = []
    model_settings_objects_xml = []
    model_settings_plates_xml = []

    next_sub_id = 1
    for tray_idx, tray_name, _, zone_meta in tray_records:
        assembly_obj_id = 100 + tray_idx
        obj_model_path = f"3D/Objects/object_{tray_idx}.model"
        sub_objs_xml = []
        comp_xml = []
        parts_cfg_xml = []
        total_faces = 0

        for z_name, ext_id, _, tm in zone_meta:
            sub_id = next_sub_id
            next_sub_id += 1
            n_faces = len(tm.faces)
            total_faces += n_faces

            sub_objs_xml.append(_mesh_to_3mf_object_xml(sub_id, tm))
            comp_xml.append(
                f'    <component p:path="/{obj_model_path}" objectid="{sub_id}" '
                f'p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>'
            )
            overrides_xml = _get_part_slicing_overrides_xml(z_name)
            parts_cfg_xml.append(
                f'    <part id="{sub_id}" subtype="normal_part">\n'
                f'      <metadata key="name" value="{z_name}"/>\n'
                f'      <metadata key="extruder" value="{ext_id}"/>\n'
                + overrides_xml
                + f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
                f'      <mesh_stat face_count="{n_faces}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n'
                f'    </part>'
            )

            # If this part is the Riser Corner Columns + Stacking Rods OR Base Corner Columns,
            # also attach a 100%-Infill Modifier Mesh covering the rod/socket connection zone!
            if "Corner_Columns" in z_name:
                mod_id = next_sub_id
                next_sub_id += 1
                bounds = tm.bounds
                min_x, min_y, min_z = bounds[0]
                max_x, max_y, max_z = bounds[1]
                span_x = (max_x - min_x) + 4.0
                span_y = (max_y - min_y) + 4.0
                if "Stacking_Rods" in z_name or "riser" in tray_name.lower():
                    # Top 44 mm of inverted riser (covers the 20 mm locking rods + 24 mm root joint)
                    mod_h = 44.0
                    mod_cz = max_z - mod_h / 2.0
                    mod_name = "Modifier_Locking_Rods_And_Root_Joint_100pct_Infill"
                else:
                    # Top 28 mm of base planter corners (covers the top socket where riser rods & stakes lock in)
                    mod_h = 28.0
                    mod_cz = max_z - mod_h / 2.0
                    mod_name = "Modifier_Top_Rod_Sockets_100pct_Infill"

                mod_box = trimesh.creation.box(extents=[span_x, span_y, mod_h])
                mod_box.apply_translation([(min_x + max_x) / 2.0, (min_y + max_y) / 2.0, mod_cz])
                sub_objs_xml.append(_mesh_to_3mf_object_xml(mod_id, mod_box))
                comp_xml.append(
                    f'    <component p:path="/{obj_model_path}" objectid="{mod_id}" '
                    f'p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>'
                )
                parts_cfg_xml.append(
                    f'    <part id="{mod_id}" subtype="modifier_part">\n'
                    f'      <metadata key="name" value="{mod_name}"/>\n'
                    f'      <metadata key="wall_loops" value="4"/>\n'
                    f'      <metadata key="sparse_infill_density" value="100%"/>\n'
                    f'      <metadata key="sparse_infill_pattern" value="rectilinear"/>\n'
                    f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
                    f'      <mesh_stat face_count="12" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n'
                    f'    </part>'
                )

        obj_model_content = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<model unit="millimeter" xml:lang="en-US" '
            'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
            'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
            'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" '
            'requiredextensions="p">\n'
            ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
            ' <resources>\n'
            + "\n".join(sub_objs_xml)
            + "\n </resources>\n</model>\n"
        )
        existing_files[obj_model_path] = obj_model_content.encode("utf-8")

        resources_xml.append(
            f'  <object id="{assembly_obj_id}" p:UUID="{uuid.uuid4()}" type="model">\n'
            f'   <components>\n'
            + "\n".join(comp_xml)
            + "\n   </components>\n  </object>"
        )

        # Bambu Studio spaces 256x256 plates in a 2-column grid (307.2 mm stride):
        # Plate 1 (col 0, row 0): X = 128.0, Y = 128.0
        # Plate 2 (col 1, row 0): X = 435.2, Y = 128.0
        # Plate 3 (col 0, row 1): X = 128.0, Y = -179.2
        col = (tray_idx - 1) % 2
        row = (tray_idx - 1) // 2
        plate_center_x = 128.0 + col * 307.2
        plate_center_y = 128.0 - row * 307.2
        build_xml.append(
            f'  <item objectid="{assembly_obj_id}" p:UUID="{uuid.uuid4()}" '
            f'transform="1 0 0 0 1 0 0 0 1 {plate_center_x:.1f} {plate_center_y:.1f} 0" printable="1"/>'
        )

        model_settings_objects_xml.append(
            f'  <object id="{assembly_obj_id}">\n'
            f'    <metadata key="name" value="{tray_name}"/>\n'
            f'    <metadata key="extruder" value="1"/>\n'
            f'    <metadata face_count="{total_faces}"/>\n'
            + "\n".join(parts_cfg_xml)
            + "\n  </object>"
        )

        model_settings_plates_xml.append(
            f'  <plate>\n'
            f'    <metadata key="plater_id" value="{tray_idx}"/>\n'
            f'    <metadata key="plater_name" value="Tray {tray_idx} - {tray_name}"/>\n'
            f'    <metadata key="locked" value="false"/>\n'
            f'    <metadata key="filament_map_mode" value="Auto For Flush"/>\n'
            f'    <model_instance>\n'
            f'      <metadata key="object_id" value="{assembly_obj_id}"/>\n'
            f'      <metadata key="instance_id" value="0"/>\n'
            f'      <metadata key="identify_id" value="{10 + tray_idx * 20}"/>\n'
            f'    </model_instance>\n'
            f'  </plate>'
        )

    root_3dmodel = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
        'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" '
        'requiredextensions="p">\n'
        ' <metadata name="Application">BambuStudio-02.06.00.51</metadata>\n'
        ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
        ' <metadata name="CreationDate">2026-10-24</metadata>\n'
        ' <metadata name="ModificationDate">2026-10-24</metadata>\n'
        ' <resources>\n'
        + "\n".join(resources_xml)
        + '\n </resources>\n'
        f' <build p:UUID="{uuid.uuid4()}">\n'
        + "\n".join(build_xml)
        + '\n </build>\n</model>\n'
    )
    existing_files["3D/3dmodel.model"] = root_3dmodel.encode("utf-8")

    rels_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    for tray_idx, _, _, _ in tray_records:
        rels_lines.append(
            f' <Relationship Target="/3D/Objects/object_{tray_idx}.model" '
            f'Id="rel-{tray_idx}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        )
    rels_lines.append("</Relationships>")
    existing_files["3D/_rels/3dmodel.model.rels"] = "\n".join(rels_lines).encode("utf-8")

    model_settings_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n'
        + "\n".join(model_settings_objects_xml)
        + "\n"
        + "\n".join(model_settings_plates_xml)
        + "\n  <assemble>\n  </assemble>\n</config>\n"
    )
    existing_files["Metadata/model_settings.config"] = model_settings_content.encode("utf-8")

    with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for fname, data in existing_files.items():
            zout.writestr(fname, data)
    shutil.move(str(tmp_zip), str(threemf_path))


def export_and_preview(part: Part, model_file: Path) -> dict:
    model_dir = Path(model_file).resolve().parent
    stem = Path(model_file).stem
    exports_dir = model_dir / "exports"
    previews_dir = model_dir / "previews"
    exports_dir.mkdir(parents=True, exist_ok=True)
    previews_dir.mkdir(parents=True, exist_ok=True)

    bbox = part.bounding_box()
    if abs(bbox.min.Z) > 1e-5:
        part = part.moved(Location((0, 0, -bbox.min.Z)))

    step_path = exports_dir / f"{stem}.step"
    stl_path = exports_dir / f"{stem}.stl"
    threemf_path = exports_dir / f"{stem}.3mf"

    export_step(part, str(step_path))
    export_stl(part, str(stl_path), tolerance=0.01, angular_tolerance=0.08)
    mesh = trimesh.load_mesh(str(stl_path))
    mesh.export(str(threemf_path))
    render_shaded_previews(stl_path, previews_dir, stem)
    viewer_html = generate_interactive_html_viewer(stl_path, previews_dir, stem)

    return {
        "step": str(step_path),
        "stl": str(stl_path),
        "3mf": str(threemf_path),
        "viewer_html": str(viewer_html),
    }
