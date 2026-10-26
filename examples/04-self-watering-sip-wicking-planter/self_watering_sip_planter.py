#!/usr/bin/env python3
"""
Style 4: Sub-Irrigated Self-Watering (SIP) Wicking Cone Modular Tomato Planter System
- Elevated sub-irrigation floor with 5 support-free 45-degree capillary soil wicking cones
- Tray 1: 6-Color Self-Watering SIP Base Planter
- Tray 2: 1-Color Deep-Capacity Wicking Water Reservoir Tray
- Tray 3: 4-Color Inverted SIP Riser with 4 Integrated Male Locking Rods (Support-Free!)
"""
import sys
from pathlib import Path

SKILL_SCRIPTS = Path(__file__).resolve().parents[2] / ".agents" / "skills" / "3d-print-modeling" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
from planter_family_engine import PlanterSystemConfig, generate_complete_planter_project

if __name__ == "__main__":
    cfg = PlanterSystemConfig(style="self_watering_sip", saucer_height_z=42.0)
    generate_complete_planter_project(cfg, Path(__file__), "self_watering_sip_planter")
