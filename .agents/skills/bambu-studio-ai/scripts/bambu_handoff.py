#!/usr/bin/env python3
"""
Handoff script to launch or stage a verified .3mf, .step, .stl, or .dxf model
in Bambu Studio, FreeCAD 1.1, or CADCraft.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_bambu_studio() -> str | None:
    candidates = [
        Path(r"C:\Program Files\Bambu Studio\bambu-studio.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Bambu Studio" / "bambu-studio.exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return shutil.which("bambu-studio")


def find_freecad() -> str | None:
    candidates = [
        Path.home() / "AppData" / "Local" / "Programs" / "FreeCAD 1.1" / "bin" / "freecad.exe",
        Path.home() / "AppData" / "Local" / "Programs" / "FreeCAD 1.0" / "bin" / "freecad.exe",
        Path(r"C:\Program Files\FreeCAD 1.1\bin\freecad.exe"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return shutil.which("freecad")


def find_cadcraft() -> str | None:
    candidates = [
        Path(r"C:\Program Files\CADCraft\cadcraft.exe"),
        Path(r"C:\Program Files\CADCraft\cadcraft-cli.exe"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return shutil.which("cadcraft")


def main():
    parser = argparse.ArgumentParser(description="Hand off 3D/CAD file to Bambu Studio, FreeCAD, or CADCraft.")
    parser.add_argument("model_file", type=Path, help="Path to .3mf, .step, .stl, or .dxf file")
    parser.add_argument("--app", choices=["bambu", "freecad", "cadcraft"], default="bambu")
    parser.add_argument("--open", action="store_true", help="Launch the selected application with the file")
    args = parser.parse_args()

    model_path = args.model_file.resolve()
    if not model_path.exists():
        print(f"[ERROR] File not found: {model_path}", file=sys.stderr)
        sys.exit(1)

    exe_map = {
        "bambu": find_bambu_studio(),
        "freecad": find_freecad(),
        "cadcraft": find_cadcraft(),
    }
    exe = exe_map.get(args.app)
    print(f"[READY FOR {args.app.upper()}] {model_path}")
    if exe:
        print(f"[{args.app.upper()} FOUND] {exe}")
        if args.open:
            subprocess.Popen([exe, str(model_path)])
            print(f"[LAUNCHED] Opened {model_path.name} in {args.app}.")


if __name__ == "__main__":
    main()
