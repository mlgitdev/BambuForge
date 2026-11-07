"""
generate_all_filament_and_process_profiles.py
=============================================
Generates and installs calibrated filament and process profiles for Bambu Lab P2S:
- 5 Filaments: UJOYBIO Elite PLA+, Kingroon PLA Basic, Kingroon PLA Matte,
               Inslogic Tri-Color Silk PLA, Kingroon Silk PLA.
- 6 Process Presets (0.4mm nozzle): 0.08mm, 0.12mm, 0.16mm, 0.20mm, 0.24mm, 0.28mm Extra Draft.
Outputs to:
  1. Local workspace `profiles/`
  2. Bambu Studio user presets (`AppData/Roaming/BambuStudio/user/944859351/`)
"""

import json
import time
import hashlib
from pathlib import Path

WORKSPACE = Path(r"<WORKSPACE_ROOT>")
PROFILES_DIR = WORKSPACE / "profiles"
USER_PRESET_DIR = Path(r"<USER_HOME>\AppData\Roaming\BambuStudio\user\944859351")
USER_FILAMENT_DIR = USER_PRESET_DIR / "filament"
USER_PROCESS_DIR = USER_PRESET_DIR / "process"

PROFILES_DIR.mkdir(parents=True, exist_ok=True)
USER_FILAMENT_DIR.mkdir(parents=True, exist_ok=True)
USER_PROCESS_DIR.mkdir(parents=True, exist_ok=True)

NOW = int(time.time())

def make_info_file(path: Path, setting_id: str, base_id: str = ""):
    content = f"sync_info = \nuser_id = 944859351\nsetting_id = {setting_id}\nbase_id = {base_id}\nupdated_time = {NOW}\n"
    path.write_text(content, encoding="utf-8")

def gen_id(prefix: str, seed: str) -> str:
    h = hashlib.md5(seed.encode("utf-8")).hexdigest()[:14]
    return f"{prefix}{h}"

# ==========================================
# 1. PROCESS PROFILES (0.08mm -> 0.28mm)
# ==========================================
PROCESSES = [
    {
        "name": "0.08mm Extra Fine @BBL P2S",
        "inherits": "0.08mm High Quality @BBL P2S",
        "base_id": "GP080",
        "layer_height": "0.08",
        "initial_layer_height": "0.16",
        "initial_layer_speed": "35",
        "initial_layer_infill_speed": "65",
        "outer_wall_speed": "50",
        "inner_wall_speed": "100",
        "sparse_infill_speed": "130",
        "internal_solid_infill_speed": "110",
        "top_surface_speed": "40",
        "outer_wall_acceleration": "1500",
        "travel_speed": "400",
        "description": "0.08mm Extra Fine for miniature figurines, ultra-fine threads, and jewel-grade curves."
    },
    {
        "name": "0.12mm Fine @BBL P2S",
        "inherits": "0.12mm High Quality @BBL P2S",
        "base_id": "GP081",
        "layer_height": "0.12",
        "initial_layer_height": "0.20",
        "initial_layer_speed": "40",
        "initial_layer_infill_speed": "80",
        "outer_wall_speed": "70",
        "inner_wall_speed": "140",
        "sparse_infill_speed": "180",
        "internal_solid_infill_speed": "150",
        "top_surface_speed": "60",
        "outer_wall_acceleration": "2000",
        "travel_speed": "450",
        "description": "0.12mm Fine quality for sharp debossed text, crisp logos, and detailed surface art."
    },
    {
        "name": "0.16mm Precision @BBL P2S",
        "inherits": "0.16mm Standard @BBL P2S",
        "base_id": "GP082",
        "layer_height": "0.16",
        "initial_layer_height": "0.20",
        "initial_layer_speed": "50",
        "initial_layer_infill_speed": "105",
        "outer_wall_speed": "80",
        "inner_wall_speed": "160",
        "sparse_infill_speed": "220",
        "internal_solid_infill_speed": "180",
        "top_surface_speed": "80",
        "outer_wall_acceleration": "2500",
        "travel_speed": "500",
        "description": "0.16mm High Precision for tight snap/slide mechanical fits and gear assemblies."
    },
    {
        "name": "0.20mm Precision @BBL P2S",
        "inherits": "0.20mm Standard @BBL P2S",
        "base_id": "GP083",
        "layer_height": "0.20",
        "initial_layer_height": "0.20",
        "initial_layer_speed": "50",
        "initial_layer_infill_speed": "105",
        "outer_wall_speed": "100",
        "inner_wall_speed": "180",
        "sparse_infill_speed": "250",
        "internal_solid_infill_speed": "200",
        "top_surface_speed": "90",
        "outer_wall_acceleration": "3000",
        "travel_speed": "500",
        "description": "0.20mm Calibrated Standard for general functional prints and balanced speed/quality."
    },
    {
        "name": "0.24mm Standard @BBL P2S",
        "inherits": "0.24mm Standard @BBL P2S",
        "base_id": "GP214",
        "layer_height": "0.24",
        "initial_layer_height": "0.20",
        "initial_layer_speed": "50",
        "initial_layer_infill_speed": "105",
        "outer_wall_speed": "120",
        "inner_wall_speed": "200",
        "sparse_infill_speed": "270",
        "internal_solid_infill_speed": "220",
        "top_surface_speed": "100",
        "outer_wall_acceleration": "4000",
        "travel_speed": "500",
        "description": "0.24mm Native Thick-Layer preset for faster printing of planters and housings."
    },
    {
        "name": "0.28mm Extra Draft @BBL P2S",
        "inherits": "fdm_process_single_0.28",
        "base_id": "GP006",
        "layer_height": "0.28",
        "initial_layer_height": "0.24",
        "initial_layer_speed": "50",
        "initial_layer_infill_speed": "105",
        "outer_wall_speed": "110",
        "inner_wall_speed": "180",
        "sparse_infill_speed": "220",
        "internal_solid_infill_speed": "180",
        "top_surface_speed": "100",
        "outer_wall_acceleration": "3500",
        "support_threshold_angle": "40",
        "top_shell_layers": "4",
        "bottom_shell_layers": "3",
        "travel_speed": "500",
        "description": "0.28mm Extra Draft for maximum throughput on bulky planters, saucers, and storage bins (~35-45% faster)."
    }
]

print("--- Generating Process Profiles ---")
for proc in PROCESSES:
    proc_dict = {
        "from": "User",
        "inherits": proc["inherits"],
        "name": proc["name"],
        "print_settings_id": proc["name"],
        "layer_height": proc["layer_height"],
        "initial_layer_print_height": proc["initial_layer_height"],
        "initial_layer_speed": [proc["initial_layer_speed"], "nil", "nil"],
        "initial_layer_infill_speed": [proc["initial_layer_infill_speed"], "nil", "nil"],
        "outer_wall_speed": [proc["outer_wall_speed"], "nil", "nil"],
        "inner_wall_speed": [proc["inner_wall_speed"], "nil", "nil"],
        "sparse_infill_speed": [proc["sparse_infill_speed"], "nil", "nil"],
        "internal_solid_infill_speed": [proc["internal_solid_infill_speed"], "nil", "nil"],
        "top_surface_speed": [proc["top_surface_speed"], "nil", "nil"],
        "outer_wall_acceleration": [proc["outer_wall_acceleration"], "nil", "nil"],
        "travel_speed": [proc["travel_speed"], "nil", "nil"],
        "compatible_printers": ["Bambu Lab P2S 0.4 nozzle"],
        "version": "2.6.0.5"
    }
    if "support_threshold_angle" in proc:
        proc_dict["support_threshold_angle"] = [proc["support_threshold_angle"]]
    if "top_shell_layers" in proc:
        proc_dict["top_shell_layers"] = [proc["top_shell_layers"]]

    setting_id = gen_id("PPUS", proc["name"])

    # 1. Write to profiles/
    clean_filename = proc["name"].replace(" ", "_").replace("@", "at") + ".json"
    (PROFILES_DIR / clean_filename).write_text(json.dumps(proc_dict, indent=4), encoding="utf-8")

    # 2. Write to Bambu Studio user directory
    user_json = USER_PROCESS_DIR / f"{proc['name']}.json"
    user_info = USER_PROCESS_DIR / f"{proc['name']}.info"
    user_json.write_text(json.dumps(proc_dict, indent=4), encoding="utf-8")
    make_info_file(user_info, setting_id, proc["base_id"])
    print(f"  [OK] Process: {proc['name']}")


# ==========================================
# 2. FILAMENT PROFILES
# ==========================================
FILAMENTS = [
    {
        "name": "UjoyBio Elite PLA+ 0.4",
        "inherits": "Generic PLA @BBL P2S",
        "base_id": "GFSL99_01",
        "nozzle_temp": "215",
        "nozzle_temp_init": "204",  # Cool first layer eliminates ooze whisker!
        "bed_temp": "55",
        "bed_temp_init": "60",
        "flow_ratio": "0.98",
        "max_volumetric_speed": "17.0",
        "fan_min_speed": "100",
        "fan_max_speed": "100",
        "filament_type": "PLA",
        "description": "UJOYBIO / EjoyBio Elite PLA+ Toughened Hyper PLA. Calibrated 204C 1st layer, 215C high speed."
    },
    {
        "name": "Kingroon PLA Basic 0.4",
        "inherits": "Generic PLA @BBL P2S",
        "base_id": "GFSL99_01",
        "nozzle_temp": "222",
        "nozzle_temp_init": "215",
        "bed_temp": "55",
        "bed_temp_init": "60",
        "flow_ratio": "0.98",
        "max_volumetric_speed": "16.0",
        "fan_min_speed": "100",
        "fan_max_speed": "100",
        "filament_type": "PLA",
        "description": "Kingroon PLA Basic high-speed standard PLA for fast prototyping."
    },
    {
        "name": "Kingroon PLA Matte 0.4",
        "inherits": "Generic PLA @BBL P2S",
        "base_id": "GFSL99_01",
        "nozzle_temp": "215",
        "nozzle_temp_init": "208",
        "bed_temp": "55",
        "bed_temp_init": "60",
        "flow_ratio": "0.98",
        "max_volumetric_speed": "13.5",
        "fan_min_speed": "100",
        "fan_max_speed": "100",
        "filament_type": "PLA",
        "description": "Kingroon PLA Matte. Mineral-dulled satin finish. Capped at 13.5 mm3/s for strong layer fusion."
    },
    {
        "name": "Inslogic Tri-Color Silk PLA 0.4",
        "inherits": "Generic PLA Silk @BBL P2S",
        "base_id": "GFSL96_03",
        "nozzle_temp": "222",
        "nozzle_temp_init": "210",
        "bed_temp": "55",
        "bed_temp_init": "60",
        "flow_ratio": "0.97",
        "max_volumetric_speed": "12.0",  # High gloss sweet spot
        "fan_min_speed": "100",
        "fan_max_speed": "100",
        "filament_type": "PLA",
        "description": "Inslogic Co-Extruded Tri-Color Silk PLA. 222C core melt with 12 mm3/s flow for brilliant metallic luster."
    },
    {
        "name": "Kingroon Silk PLA 0.4",
        "inherits": "Generic PLA Silk @BBL P2S",
        "base_id": "GFSL96_03",
        "nozzle_temp": "220",
        "nozzle_temp_init": "210",
        "bed_temp": "55",
        "bed_temp_init": "60",
        "flow_ratio": "0.97",
        "max_volumetric_speed": "11.0",
        "fan_min_speed": "100",
        "fan_max_speed": "100",
        "filament_type": "PLA",
        "description": "Kingroon High-Luster Silk PLA. Capped at 11 mm3/s to ensure rich reflective shine without milkiness."
    }
]

print("\n--- Generating Filament Profiles ---")
for fil in FILAMENTS:
    fil_dict = {
        "from": "User",
        "inherits": fil["inherits"],
        "name": fil["name"],
        "filament_settings_id": [fil["name"]],
        "nozzle_temperature": [fil["nozzle_temp"], "nil", "nil"],
        "nozzle_temperature_initial_layer": [fil["nozzle_temp_init"], "nil", "nil"],
        "textured_plate_temp": [fil["bed_temp"], "nil", "nil"],
        "textured_plate_temp_initial_layer": [fil["bed_temp_init"], "nil", "nil"],
        "filament_flow_ratio": [fil["flow_ratio"]],
        "filament_max_volumetric_speed": [fil["max_volumetric_speed"], "nil", "nil"],
        "fan_min_speed": [fil["fan_min_speed"]],
        "fan_max_speed": [fil["fan_max_speed"]],
        "close_fan_the_first_x_layers": ["3"],
        "compatible_printers": ["Bambu Lab P2S 0.4 nozzle"],
        "version": "2.6.0.5"
    }

    setting_id = gen_id("PFUS", fil["name"])

    # 1. Write to profiles/
    clean_filename = fil["name"].replace(" ", "_").replace("@", "at") + ".json"
    (PROFILES_DIR / clean_filename).write_text(json.dumps(fil_dict, indent=4), encoding="utf-8")

    # 2. Write to Bambu Studio user directory
    user_json = USER_FILAMENT_DIR / f"{fil['name']}.json"
    user_info = USER_FILAMENT_DIR / f"{fil['name']}.info"
    user_json.write_text(json.dumps(fil_dict, indent=4), encoding="utf-8")
    make_info_file(user_info, setting_id, fil["base_id"])
    print(f"  [OK] Filament: {fil['name']}")

print("\n[SUCCESS] All 6 process presets and 5 filament profiles generated and installed!")
