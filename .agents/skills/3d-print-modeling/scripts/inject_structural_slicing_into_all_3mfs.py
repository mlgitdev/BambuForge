"""Inject global & per-zone structural slicing settings + 100% infill rod/socket modifiers into all .3mf files."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
import trimesh

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from p2s_cad_helpers import _inject_multicolor_assemblies_into_3mf

MODELS_DIR = Path(r"<WORKSPACE_ROOT>\models")
BAMBU_EXE = Path(r"C:\Program Files\Bambu Studio\bambu-studio.exe")

PLANTER_SPECS = [
    ("cherry-tomato-modular-planter", "cherry_tomato_modular_planter", True),
    ("01-oval-stadium-planter", "oval_stadium_planter", True),
    ("02-roman-fluted-column-planter", "roman_fluted_planter", True),
    ("03-origami-faceted-prism-planter", "origami_faceted_planter", True),
    ("04-self-watering-sip-wicking-planter", "self_watering_sip_planter", True),
    ("05-hexagonal-honeycomb-tessellation-planter", "hex_honeycomb_planter", False),
    ("06-zen-stepped-pagoda-wave-planter", "zen_pagoda_planter", True),
]


def _update_project_settings_in_zip(threemf_path: Path) -> None:
    tmp_zip = threemf_path.with_suffix(".projtmp.3mf")
    with zipfile.ZipFile(threemf_path, "r") as zin:
        files = {n: zin.read(n) for n in zin.namelist()}
    if "Metadata/project_settings.config" in files:
        proj = json.loads(files["Metadata/project_settings.config"].decode("utf-8"))
        proj["enable_support"] = 0
        proj["wall_loops"] = 3
        proj["sparse_infill_density"] = "20%"
        proj["sparse_infill_pattern"] = "gyroid"
        proj["top_shell_layers"] = 5
        proj["bottom_shell_layers"] = 5
        files["Metadata/project_settings.config"] = json.dumps(proj, indent=4).encode("utf-8")
    with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for k, v in files.items():
            zout.writestr(k, v)
    tmp_zip.replace(threemf_path)


def update_planter_3mf(folder_name: str, prefix: str, has_tray4: bool) -> None:
    model_dir = MODELS_DIR / folder_name
    exports_dir = model_dir / "exports"
    zones_dir = exports_dir / "color_zones"
    threemf_path = exports_dir / f"{prefix}_3_trays_multicolor.3mf"

    tray_defs = [
        (1, f"{prefix}_tray1_base_6color", [
            ("Color1_Lower_Box_Layer", 1),
            ("Color2_Middle_Box_Layer", 2),
            ("Color3_Upper_Box_Layer", 3),
            ("Color4_Connecting_Belts", 4),
            ("Color5_Top_Rim_Collar", 5),
            ("Color6_Corner_Columns", 6),
        ]),
        (2, f"{prefix}_tray2_saucer_1color", [
            ("Color1_Drip_Saucer_Tray", 1),
        ]),
        (3, f"{prefix}_tray3_riser_4color", [
            ("Color1_Riser_Lower_Panel", 1),
            ("Color2_Riser_Upper_Panel", 2),
            ("Color3_Riser_Belts_And_Rim", 4),
            ("Color4_Corner_Columns_And_Stacking_Rods", 6),
        ]),
    ]
    if has_tray4:
        tray_defs.append(
            (4, f"{prefix}_tray4_irrigation_straws_2color", [
                ("Color1_SubSoil_Straw_Arch_Tube", 4),
                ("Color2_Intake_Plugs_And_Root_Diffuser_Crown", 5),
            ])
        )

    tray_records = []
    for tray_idx, tray_name, z_specs in tray_defs:
        tray_stl = exports_dir / f"{tray_name}.stl"
        zone_meta = []
        for z_idx, (z_name, ext_id) in enumerate(z_specs, start=1):
            z_stl = zones_dir / f"{tray_name}_{z_idx}_{z_name}.stl"
            tm = trimesh.load_mesh(str(z_stl))
            zone_meta.append((z_name, ext_id, z_stl, tm))
        tray_records.append((tray_idx, tray_name, tray_stl, zone_meta))

    _update_project_settings_in_zip(threemf_path)
    _inject_multicolor_assemblies_into_3mf(threemf_path, tray_records)

    verified_3mf = threemf_path.with_suffix(".verified.3mf")
    subprocess.run(
        [str(BAMBU_EXE), "--export-3mf", str(verified_3mf), str(threemf_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    if verified_3mf.exists() and verified_3mf.stat().st_size > 0:
        verified_3mf.replace(threemf_path)

    if folder_name == "cherry-tomato-modular-planter":
        shutil.copy2(threemf_path, exports_dir / "cherry_tomato_complete_3_trays.3mf")

    print(f"[OK] Updated {threemf_path.name} with global & per-zone infill/wall settings + 100% rod modifiers")


def update_melitta_3mfs() -> None:
    exports_dir = MODELS_DIR / "melitta-coffee-bean-dispenser" / "exports"
    for fname in ["Melitta_Bean_Dispenser_60mm_Geared_1_Plate.3mf", "Melitta_Bean_Dispenser_60mm_Geared_3_Trays.3mf"]:
        fpath = exports_dir / fname
        if not fpath.exists():
            continue
        _update_project_settings_in_zip(fpath)
        tmp_zip = fpath.with_suffix(".mstmp.3mf")
        with zipfile.ZipFile(fpath, "r") as zin:
            files = {n: zin.read(n) for n in zin.namelist()}

        ms_str = files["Metadata/model_settings.config"].decode("utf-8")
        root = ET.fromstring(ms_str)
        for obj in root.findall("object"):
            oname = ""
            for md in obj.findall("metadata"):
                if md.attrib.get("key") == "name":
                    oname = md.attrib.get("value", "")
            for part in obj.findall("part"):
                pname = oname
                for md in part.findall("metadata"):
                    if md.attrib.get("key") == "name":
                        pname = md.attrib.get("value", "") or oname
                # Remove any prior wall_loops / sparse_infill_* tags
                for old_md in list(part.findall("metadata")):
                    if old_md.attrib.get("key") in ("wall_loops", "sparse_infill_density", "sparse_infill_pattern", "bottom_shell_layers", "top_shell_layers"):
                        part.remove(old_md)
                if "Shutter" in pname or "Thumbwheel" in pname:
                    ET.SubElement(part, "metadata", {"key": "wall_loops", "value": "4"})
                    ET.SubElement(part, "metadata", {"key": "sparse_infill_density", "value": "40%"})
                    ET.SubElement(part, "metadata", {"key": "sparse_infill_pattern", "value": "gyroid"})
                    ET.SubElement(part, "metadata", {"key": "bottom_shell_layers", "value": "5"})
                    ET.SubElement(part, "metadata", {"key": "top_shell_layers", "value": "5"})
                elif "Ramp" in pname:
                    ET.SubElement(part, "metadata", {"key": "wall_loops", "value": "3"})
                    ET.SubElement(part, "metadata", {"key": "sparse_infill_density", "value": "25%"})
                    ET.SubElement(part, "metadata", {"key": "sparse_infill_pattern", "value": "gyroid"})
                else:
                    ET.SubElement(part, "metadata", {"key": "wall_loops", "value": "3"})
                    ET.SubElement(part, "metadata", {"key": "sparse_infill_density", "value": "20%"})
                    ET.SubElement(part, "metadata", {"key": "sparse_infill_pattern", "value": "gyroid"})

        files["Metadata/model_settings.config"] = ('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")).encode("utf-8")
        with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for k, v in files.items():
                zout.writestr(k, v)
        tmp_zip.replace(fpath)

        verified_3mf = fpath.with_suffix(".verified.3mf")
        subprocess.run(
            [str(BAMBU_EXE), "--export-3mf", str(verified_3mf), str(fpath)],
            capture_output=True,
            text=True,
            check=True,
        )
        if verified_3mf.exists() and verified_3mf.stat().st_size > 0:
            verified_3mf.replace(fpath)
        print(f"[OK] Updated {fpath.name} with global & per-part infill/wall settings")


if __name__ == "__main__":
    for folder_name, prefix, has_tray4 in PLANTER_SPECS:
        update_planter_3mf(folder_name, prefix, has_tray4)
    update_melitta_3mfs()
