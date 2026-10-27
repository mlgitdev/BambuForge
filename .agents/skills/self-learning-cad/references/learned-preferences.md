# Learned User Preferences & Calibrated CAD Rules

> **Purpose:** This file is the living memory of our 3D modeling partnership. Before designing any new model, the agent reads this file to apply all accumulated lessons from past conversations and prints.

---

## 1. Core Baseline Preferences (Established 2026-10-24)

* **Target Printer:** Bambu Lab P2S (`256 × 256 × 256 mm` build volume).
* **Primary CAD Engine:** **`build123d` (Python OpenCascade B-Rep CAD)** & **FreeCAD Python API** compatibility (exporting native `.step`, `.3mf`, and `.stl`). Do **not** use legacy OpenSCAD (`2021.01`).
* **Target Slicer:** Bambu Studio (`.step` for true `G2`/`G3` circular arc slicing + `.3mf` and `.stl` exports).
* **Support-Free Priority:** **High.** Always design angles (`<= 45°` from vertical), bottom chamfers (`45°`), teardrop horizontal holes (`> 5 mm`), and sacrificial 1-layer counterbore bridges (`0.20 mm`) so models slice in Bambu Studio with **Support = OFF**.
* **Project Structure:** Every requested model gets its own folder under `models/<model-name>/` with `exports/` and `previews/` subdirectories, and is tracked in `AGENTS.md`.
* **Parametric Transparency:** Keep key dimensions in a clean `@dataclass` block at the top of each `.py` model file so fine-tuning is instantaneous.

---

## 2. Learned Fine-Tuning Rules Log

| Date | Category | Model | Gap Identified | Permanent Rule Adopted |
| :--- | :--- | :--- | :--- | :--- |
| `2026-10-24` | `support_free_geometry` | *Baseline* | User prefers minimal/zero supports on P2S prints | Default all overhangs to `<= 45°`, use `45°` bottom chamfers (`1.0 mm`), and use `make_teardrop_cylinder()` on horizontal bores `> 5 mm`. |
| `2026-10-24` | `workflow_organization` | *Toolchain* | OpenSCAD stable release is >5 years old and lacks modern B-Rep features | Replaced OpenSCAD with **`build123d` (OpenCascade 8.0 B-Rep)** + FreeCAD-compatible `.step`/`.3mf`/`.stl` exports inside `.venv`. |
| `2026-10-24` | `workflow_organization` | `cherry-tomato-modular-planter` | User prefers multi-part modular sets saved in a single `.3mf` file across separate trays (build plates) | Always use `export_bambu_multiplate_3mf()` (`bambu-studio --arrange 1 --export-3mf`) with the P2S `0.4 mm` profile to pack multi-module assemblies onto separate trays in one `.3mf` project. |
| `2026-10-24` | `support_free_geometry` | `cherry-tomato-modular-planter` | Extension riser needs integrated printed rods to lock into the 4 base holes without supports | Model 4 hollow male alignment rods on the riser and **invert print orientation (`180°` on flat top rim at `Z = 0`)** so the 4 locking rods print pointing straight up (`+Z`) with zero supports. |
| `2026-10-24` | `ergonomics_aesthetics` | *All Planter Models* | User wants multi-color AMS segmentation: 6 color zones on Base Planter, 1 color on Drip Saucer, 4 color zones on Extension Riser | Export multi-body `Compound` `.step` assemblies where each structural layer, connecting strip/belt, rim, and corner edge column is a distinct sub-part for 1-click multi-color assignment in Bambu Studio. |
| `2026-10-24` | `workflow_organization` | *All Multi-Plate `.3mf` Exports* | Plate 3 was empty in `.3mf` when placed at `X=742.4, Y=128.0` because Bambu Studio uses a 2-column grid for 3+ plates | Always place Plate `N` using `col = (N-1) % 2`, `row = (N-1) // 2` (`Plate 3 = 128.0, -179.2`), pass 6 flattened filament JSONs via `--load-filaments`, and round-trip through `bambu-studio.exe --export-3mf` to verify all plates and generate OpenGL thumbnails. |
| `2026-10-24` | `workflow_organization` | *Environment / Installers* | Large installer download via Python `urllib` hung for an hour | Never use unmonitored single-stream `urllib` for large installers; prefer existing user installations (`FreeCAD 1.1`, `CADCraft`) or native package managers with strict timeouts. |
| `2026-10-24` | `workflow_organization` | `melitta-coffee-bean-dispenser` | `imports/` folder should only be used as read-only input, and imported objects in `.3mf` need clean descriptive names | Treat `imports/` as strictly read-only input; generate all outputs in `models/<model-name>/`, and always rename imported `.3mf` objects and plates in `Metadata/model_settings.config` to descriptive names. |
| `2026-10-24` | `workflow_organization` | *All Models* | Multi-part models and functional accessories (like the sub-soil arch straw) need visual assembly & usage instructions | Always generate an illustrated `ASSEMBLY_GUIDE.md` with rendered 3D exploded/cutaway assembly images (`previews/*_assembly_guide.png`) inside every `models/<model-name>/` directory. |
| `2026-10-26` | `workflow_organization` | `04-self-watering-sip-wicking-planter` | Bulky objects like planters defaulted to 0.20mm layer height without offering 0.28mm draft speed option, causing unnecessarily long print times when fine precision is not critical. | For bulky structural designs (planters, trays, bins), proactively clarify layer height preference (0.20mm Standard vs 0.28mm Extra Draft) during intake; ensure vertical Z-steps and sacrificial bridges are compatible with 0.28mm, and document draft speed print estimates. |
