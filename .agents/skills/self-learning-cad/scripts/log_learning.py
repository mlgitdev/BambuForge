#!/usr/bin/env python3
"""
Logs a user fine-tuning request or post-print lesson into feedback-log.jsonl
and appends the new permanent design rule to learned-preferences.md.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Record a self-learning CAD lesson.")
    parser.add_argument(
        "--category",
        required=True,
        choices=[
            "tolerance_calibration",
            "support_free_geometry",
            "structural_strength",
            "ergonomics_aesthetics",
            "workflow_organization",
        ],
        help="Category of the learned preference",
    )
    parser.add_argument("--model", required=True, help="Model folder name where feedback occurred")
    parser.add_argument("--gap", required=True, help="What needed fine-tuning or correction")
    parser.add_argument("--rule", required=True, help="Permanent rule to apply to future models")
    args = parser.parse_args()

    refs_dir = Path(__file__).resolve().parent.parent / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = refs_dir / "feedback-log.jsonl"
    prefs_md_path = refs_dir / "learned-preferences.md"

    today = datetime.now().strftime("%Y-%m-%d")
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "date": today,
        "category": args.category,
        "model": args.model,
        "gap": args.gap,
        "rule": args.rule,
    }

    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    row = f"| `{today}` | `{args.category}` | `{args.model}` | {args.gap} | {args.rule} |\n"
    with prefs_md_path.open("a", encoding="utf-8") as f:
        f.write(row)

    print(f"[LEARNED] Recorded permanent rule in {prefs_md_path.name}: {args.rule}")


if __name__ == "__main__":
    main()
