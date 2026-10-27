#!/usr/bin/env python3
"""
Style 0: Classic Rectangular Modular Cherry Tomato Planter System
- Tray 1: 6-Color Base Planter (3 Box Layers + Connecting Strips + Top Rim + 4 Corner Columns)
- Tray 2: 1-Color Snap-In Drip Saucer
- Tray 3: 4-Color Inverted Extension Riser with 4 Integrated Male Locking Rods (Support-Free!)
"""
import shutil
import sys
from pathlib import Path

SKILL_SCRIPTS = Path(__file__).resolve().parents[2] / ".agents" / "skills" / "3d-print-modeling" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
from planter_family_engine import PlanterSystemConfig, generate_complete_planter_project

if __name__ == "__main__":
    cfg = PlanterSystemConfig(style="rectangular_classic")
    res = generate_complete_planter_project(cfg, Path(__file__), "cherry_tomato_modular_planter")
    exports_dir = Path(__file__).resolve().parent / "exports"
    src = Path(res["multi_plate_3mf"])
    if src.exists():
        shutil.copy2(src, exports_dir / "cherry_tomato_complete_3_trays.3mf")
        shutil.copy2(src, exports_dir / "cherry_tomato_modular_planter.3mf")
