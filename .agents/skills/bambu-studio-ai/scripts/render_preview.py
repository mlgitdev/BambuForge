#!/usr/bin/env python3
"""
Executes a build123d / FreeCAD Python CAD script (.py) to export .step, .3mf, and .stl
files into `exports/` and render 4 shaded CAD preview PNGs into `previews/`.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute a build123d Python CAD script to export STEP/3MF/STL and render previews."
    )
    parser.add_argument("model_script", type=Path, help="Path to the .py CAD script")
    args = parser.parse_args()

    script_path = args.model_script.resolve()
    if not script_path.exists():
        print(f"[ERROR] Model script not found: {script_path}", file=sys.stderr)
        return 1

    print(f"[BUILD123D] Running CAD script: {script_path}")
    res = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(script_path.parent),
        capture_output=True,
        text=True,
    )
    if res.stdout:
        print(res.stdout.strip())
    if res.returncode != 0:
        print(f"[ERROR] CAD build failed:\n{res.stderr}", file=sys.stderr)
        return res.returncode

    print("\n[SUCCESS] STEP, 3MF, STL exports and 4-view shaded previews generated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
