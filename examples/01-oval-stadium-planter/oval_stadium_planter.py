#!/usr/bin/env python3
"""
Style 1: Oval / Stadium Track Modular Cherry Tomato Planter System
- Smooth elliptical/stadium cross-section (232 x 182 mm base, eliminates corner stress points)
- Tray 1: 6-Color Base Planter
- Tray 2: 1-Color Oval Drip Saucer
- Tray 3: 4-Color Inverted Oval Riser with 4 Integrated Male Locking Rods (Support-Free!)
"""
import sys
from pathlib import Path

SKILL_SCRIPTS = Path(__file__).resolve().parents[2] / ".agents" / "skills" / "3d-print-modeling" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
from planter_family_engine import PlanterSystemConfig, generate_complete_planter_project

if __name__ == "__main__":
    cfg = PlanterSystemConfig(style="oval_stadium")
    generate_complete_planter_project(cfg, Path(__file__), "oval_stadium_planter")
