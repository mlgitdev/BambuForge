"""
generate_all_custom_matrix_profiles.py
======================================
Generates the complete 30-profile matrix for Bambu Lab P2S (0.4 nozzle):
5 Filaments x 6 Layer Heights = 30 Tailored Process Profiles
Format: "<layer_height> <Brand> <Type> @BBL P2S"
e.g. "0.08mm UjoyBio PLA Plus @BBL P2S"
"""

import json
import time
import hashlib
from pathlib import Path

WORKSPACE = Path(r"<WORKSPACE_ROOT>")
PROFILES_DIR = WORKSPACE / "profiles"
USER_PRESET_DIR = Path(r"<USER_HOME>\AppData\Roaming\BambuStudio\user\944859351")
USER_PROCESS_DIR = USER_PRESET_DIR / "process"

PROFILES_DIR.mkdir(parents=True, exist_ok=True)
USER_PROCESS_DIR.mkdir(parents=True, exist_ok=True)

NOW = int(time.time())

def make_info_file(path: Path, setting_id: str, base_id: str = ""):
    content = f"sync_info = \nuser_id = 944859351\nsetting_id = {setting_id}\nbase_id = {base_id}\nupdated_time = {NOW}\n"
    path.write_text(content, encoding="utf-8")

def gen_id(prefix: str, seed: str) -> str:
    h = hashlib.md5(seed.encode("utf-8")).hexdigest()[:14]
    return f"{prefix}{h}"

# Base process specifications by layer height
LAYER_SPECS = {
    "0.08mm": {
        "lh": "0.08",
        "init_lh": "0.16",
        "inherits": "0.08mm High Quality @BBL P2S",
        "base_id": "GP080",
        "init_spd": "35",
        "init_infill_spd": "65",
        "top_shell": "9",
        "bot_shell": "7",
        "top_surf_spd": "40",
    },
    "0.12mm": {
        "lh": "0.12",
        "init_lh": "0.20",
        "inherits": "0.12mm High Quality @BBL P2S",
        "base_id": "GP081",
        "init_spd": "40",
        "init_infill_spd": "80",
        "top_shell": "7",
        "bot_shell": "5",
        "top_surf_spd": "60",
    },
    "0.16mm": {
        "lh": "0.16",
        "init_lh": "0.20",
        "inherits": "0.16mm Standard @BBL P2S",
        "base_id": "GP082",
        "init_spd": "50",
        "init_infill_spd": "105",
        "top_shell": "6",
        "bot_shell": "5",
        "top_surf_spd": "80",
    },
    "0.20mm": {
        "lh": "0.20",
        "init_lh": "0.20",
        "inherits": "0.20mm Standard @BBL P2S",
        "base_id": "GP083",
        "init_spd": "50",
        "init_infill_spd": "105",
        "top_shell": "5",
        "bot_shell": "4",
        "top_surf_spd": "90",
    },
    "0.24mm": {
        "lh": "0.24",
        "init_lh": "0.20",
        "inherits": "0.24mm Standard @BBL P2S",
        "base_id": "GP214",
        "init_spd": "50",
        "init_infill_spd": "105",
        "top_shell": "4",
        "bot_shell": "3",
        "top_surf_spd": "100",
    },
    "0.28mm": {
        "lh": "0.28",
        "init_lh": "0.24",
        "inherits": "fdm_process_single_0.28",
        "base_id": "GP006",
        "init_spd": "50",
        "init_infill_spd": "105",
        "top_shell": "4",
        "bot_shell": "3",
        "top_surf_spd": "100",
        "support_threshold_angle": "40",
    }
}

# Filament tuning profiles: specific speed and acceleration parameters across layer heights
# Order of speeds: [outer_wall, inner_wall, sparse_infill, internal_solid, outer_accel, normal_accel]
FILAMENT_SPECS = {
    "UjoyBio PLA Plus": {
        "0.08mm": ("45", "90", "120", "100", "1500", "4500"),
        "0.12mm": ("60", "120", "160", "140", "2000", "5000"),
        "0.16mm": ("70", "140", "200", "170", "2500", "6000"),
        "0.20mm": ("90", "180", "250", "200", "3000", "7000"),
        "0.24mm": ("110", "200", "270", "220", "3500", "8000"),
        "0.28mm": ("120", "180", "220", "180", "3500", "8000"),
    },
    "Kingroon PLA Basic": {
        "0.08mm": ("50", "100", "130", "110", "1500", "5000"),
        "0.12mm": ("65", "130", "170", "150", "2000", "6000"),
        "0.16mm": ("80", "160", "220", "180", "2500", "7000"),
        "0.20mm": ("100", "190", "260", "210", "3000", "8000"),
        "0.24mm": ("125", "210", "270", "230", "4000", "10000"),
        "0.28mm": ("120", "190", "230", "190", "3500", "8000"),
    },
    "Kingroon PLA Matte": {
        "0.08mm": ("40", "80", "110", "95", "1200", "4000"),
        "0.12mm": ("50", "100", "140", "120", "1800", "5000"),
        "0.16mm": ("65", "130", "180", "150", "2200", "6000"),
        "0.20mm": ("80", "150", "210", "175", "2500", "7000"),
        "0.24mm": ("90", "170", "230", "190", "3000", "8000"),
        "0.28mm": ("95", "160", "190", "160", "3000", "7000"),
    },
    "Inslogic Tri-Color Silk PLA": {
        "0.08mm": ("35", "80", "120", "100", "1200", "4000"),
        "0.12mm": ("40", "100", "150", "125", "1500", "5000"),
        "0.16mm": ("45", "120", "180", "150", "1800", "6000"),
        "0.20mm": ("50", "140", "200", "170", "2000", "7000"),
        "0.24mm": ("55", "160", "220", "180", "2500", "7000"),
        "0.28mm": ("55", "150", "190", "160", "2500", "7000"),
    },
    "Kingroon Silk PLA": {
        "0.08mm": ("30", "70", "110", "95", "1200", "4000"),
        "0.12mm": ("35", "90", "140", "120", "1500", "5000"),
        "0.16mm": ("40", "110", "170", "140", "1800", "6000"),
        "0.20mm": ("45", "130", "190", "160", "2000", "7000"),
        "0.24mm": ("50", "150", "210", "175", "2200", "7000"),
        "0.28mm": ("50", "140", "180", "150", "2200", "7000"),
    }
}

count = 0
print("--- Generating 30 Specific Process Profiles ---")
for fil_brand, layer_map in FILAMENT_SPECS.items():
    for lh_key, speeds in layer_map.items():
        ls = LAYER_SPECS[lh_key]
        outer_w, inner_w, sp_infill, int_solid, out_acc, norm_acc = speeds

        # Strict profile naming format:
        # e.g.: "0.08mm UjoyBio PLA Plus @BBL P2S"
        profile_name = f"{lh_key} {fil_brand} @BBL P2S"

        proc_dict = {
            "from": "User",
            "inherits": ls["inherits"],
            "name": profile_name,
            "print_settings_id": profile_name,
            "layer_height": ls["lh"],
            "initial_layer_print_height": ls["init_lh"],
            "initial_layer_speed": [ls["init_spd"], "nil", "nil"],
            "initial_layer_infill_speed": [ls["init_infill_spd"], "nil", "nil"],
            "outer_wall_speed": [outer_w, "nil", "nil"],
            "inner_wall_speed": [inner_w, "nil", "nil"],
            "sparse_infill_speed": [sp_infill, "nil", "nil"],
            "internal_solid_infill_speed": [int_solid, "nil", "nil"],
            "top_surface_speed": [ls["top_surf_spd"], "nil", "nil"],
            "outer_wall_acceleration": [out_acc, "nil", "nil"],
            "default_acceleration": [norm_acc, "nil", "nil"],
            "top_shell_layers": [ls["top_shell"]],
            "bottom_shell_layers": [ls["bot_shell"]],
            "travel_speed": ["500", "nil", "nil"],
            "compatible_printers": ["Bambu Lab P2S 0.4 nozzle"],
            "version": "2.6.0.5"
        }
        if "support_threshold_angle" in ls:
            proc_dict["support_threshold_angle"] = [ls["support_threshold_angle"]]

        setting_id = gen_id("PPUS", profile_name)

        # 1. Save to profiles/
        safe_fname = profile_name.replace(" ", "_").replace("@", "at") + ".json"
        (PROFILES_DIR / safe_fname).write_text(json.dumps(proc_dict, indent=4), encoding="utf-8")

        # 2. Save to Bambu Studio user directory
        user_json = USER_PROCESS_DIR / f"{profile_name}.json"
        user_info = USER_PROCESS_DIR / f"{profile_name}.info"
        user_json.write_text(json.dumps(proc_dict, indent=4), encoding="utf-8")
        make_info_file(user_info, setting_id, ls["base_id"])

        count += 1
        print(f"[{count:02d}/30] Installed: {profile_name}")

print(f"\n[SUCCESS] Successfully generated and installed all {count} custom process profiles!")
