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
| `2026-10-27` | `fit_tolerance_mechanics` | `01-oval-stadium-planter` | Stacking riser had conical column taper meeting flat base planter rim, blocking mating (+8.4mm air gap) and requiring sanding | Male locking rods must protrude from a flat planar landing shoulder; never use full-width conical taper without matching socket counterbore. Provide small root fillet ($\le 0.8\text{ mm}$) nesting in socket lead-in chamfer ($\ge 1.4\text{ mm}$), ensuring 100% flush planar contact with zero sanding. |
| `2026-10-27` | `toolchain_automation` | *All CAD Requests* | Raster graphics (PNG, JPG) in `imports/` needed manual tracing for CAD embossing & modifier integration | Developed `png_to_svg.py` with alpha/luminance isolation, Rust-accelerated `vtracer` sub-pixel spline fitting, mm physical scaling, origin centering, and direct `build123d.import_svg` integration. |
| `2026-10-27` | `fit_tolerance_mechanics` | `All Modular Stacking Models` | Stackable male parts had male skirt and Lego registration boss, but receiving bottom module was flat with no female receiving pockets | **Modular Stacking Snap-Fit Verification Rule:** Whenever designing stackable male parts (with male skirt and circular Lego boss), always design matching female receiving features (skirt pocket + circular Lego socket) in the receiving part with +0.5mm vertical clearance and +0.35mm lateral clearance. Before finalizing, execute a simulated boolean snapping test in `build123d` proving `0.000000 mm³` collision volume and generate a cross-section illustration showing zero seam gap. |
| `2026-10-27` | `workflow_organization` | `mouthguard-box-pegasus` | In Bambu Studio, legacy 3MF part matrices caused parts to overlap on plate, and parts without `<model_instance>` tags (e.g. hinge pin rod) were hidden from plate preview | In Bambu Studio multi-part projects: 1) Assign distinct, non-overlapping coordinates (>25 mm clearance) to every object on the bed; 2) Explicitly declare every printable part via a `<model_instance>` tag inside `<plate>` in `Metadata/model_settings.config` so it renders and slices; 3) Orient front latches with horizontal pivot axis and base containers upright ($Z = 0.00$ floor). |
| `2026-10-27` | `workflow_organization` | *All Future Models* | Previews previously diverged from 3MF exports (different coordinates, inverted parts, missing plate instances), burning conversation turns and tokens | **Interactive Exploded Viewer & Mandatory 1:1 Preview-to-3MF Correlation Invariant:** Standardized offline Three.js viewer with 0–100% Exploded Slider, AMS component toggles, camera presets, auto-spin strictly OFF by default. Programmatic audit (`audit_3mf_correlation`) must run before handoff, asserting 1:1 match with 3MF plate instances, zero bed collisions, and correct print orientations. |
| `2026-10-27` | `multi_part_slicing_orientation` | *All Multi-Part Sets* | Toolhead exclusion bubble collisions in "by object" mode; mirrored exterior text on face-down prints; missing auxiliary hardware in 3MF exports | **Tiered Plate Layout & Embedded Hardware Invariant:** Separate main enclosures (front tier: $Y \approx 65\text{ mm}$) and accessories (rear tier: $Y \approx 195\text{ mm}$) with $\ge 100\text{ mm}$ spacing in Y to prevent exclusion zone overlaps. Align all mating features along identical directional axes. Verify face-down text reads left-to-right from exterior. Embed auxiliary 3D hardware directly into primary recognized sub-models (e.g. `object_24.model`) with explicit `<part>` tags in config. |

* **Planter Drip Saucer Clearance & Full Corner Column Coverage Rule:**
  - Water collection saucers and drip plates must fully cover both the planter's nominal body profile AND any reinforced corner columns or architectural pilasters.
  - Clearance must be generous: **$\ge 4.5 - 5.0\text{ mm}$ per side** ($9.0 - 10.0\text{ mm}$ total gap), never razor-thin or "millimeter-to-millimeter" ($\le 1.0\text{ mm}$), ensuring effortless drop-in and lift-out without binding, jamming, or surface-tension sticking.
  - For oval / stadium planters, calibrate the saucer corner radius ($R \approx 50.0\text{ mm}$) so the corner does not aggressively cut into the diagonal corner columns, maintaining a uniform $4.8\text{ mm}$ clearance all around.
  - Outer dimensions must remain $\le 250\text{ mm}$ (e.g. $248 \times 198\text{ mm}$) to stay safely within the Bambu Lab P2S $256 \times 256\text{ mm}$ build envelope.
  - Internal raised aeration rails ($3.6\text{ mm}$ height) must elevate the planter above standing runoff water for root health.

* **Planter Sub-Soil Irrigation Straw Geometry & Round Floor Hole Invariant:**
  - **Nominal Floor Hole Profile:** Planter drainage and sub-irrigation floor holes are round cylinders (nominal $\varnothing 8.00\text{ mm}$).
  - **True Round Circular Plug Cross-Section ($\varnothing 7.20\text{ mm}$):** Irrigation arch straws and bottom insertion plugs must be true round cylinders with a continuous circular cross-section ($\varnothing 7.20\text{ mm}$ outer diameter with continuous hollow $\varnothing 5.00\text{ mm}$ capillary wicking bore).
  - **Zero Oblong/Oval Distortion:** **NEVER** stretch, taper, or sweep a straw plug with unequal X/Z dimensions (e.g. $7.4 \times 10.6\text{ mm}$) to meet the bed, as this turns the plug into an oblong oval that physically jams and cannot enter the $\varnothing 8.00\text{ mm}$ round hole.
  - **Support-Free Planar Bed Contact Strip:** To ensure 100% support-free bed adhesion when printed lying flat on $Z = 0$, keep the straw circular and add a small planar bed flat facet ($0.30\text{ mm}$) along the underside, providing a continuous $2.8\text{ mm}$ wide bed contact strip without altering the circular insertion profile.
  - **Wide Landing Collar Stop ($14.0\text{ mm}$):** Provide a wide ($14.0\text{ mm}$) horizontal landing collar stop at the floor insertion line ($Y = 16.0\text{ mm}$) so the straw rests firmly on the planter floor with zero wobble, and add a $1.5\text{ mm}$ $45^\circ$ self-centering lead-in tip chamfer for smooth slide-in fit.
  - **Provide Standalone Single-Straw STL:** Alongside the 2-straw multi-plate tray (`tray4_irrigation_straws_2color.stl`), always export a standalone single-straw STL (`tray4_irrigation_straw_single.stl`) for convenient single replacement printing.

* **Face-Down Bed Inlay & Logo Chirality Rule (The Roll-Over Invariant):**
  - When an enclosure top lid is printed face-down on the PEI bed (`Z = 0`), the lid has been rolled over $180^\circ$ from its upright CAD orientation.
  - The logo, text, or inlay MUST undergo the exact same rigid-body $180^\circ$ rotation as the lid.
  - Never invert/negate X independently; negating X creates a mirror reflection rather than a physical roll-over.
  - In slicer 3D view from `+Z`, the user sees the inside cavity; looking through the back of an un-mirrored part naturally appears reversed. Never "fix" the `+Z` view by flipping the logo, which makes it print backwards on the plate!
  - Always verify from the **Bottom View (`-Z` looking UP at the build plate)**: text must read left-to-right.
  - Standalone artwork STLs (`pegasus_horse_wings_only.stl`, badges) must be exported upright on their flat back at `Z = 0` facing `+Z`.
* **Calibrated Snap Pin Dimensions for Ø3.00mm Knuckles:**
  - Pin shaft diameter: **Ø2.75 mm** (total clearance $0.25\text{ mm}$ / $0.125\text{ mm}$ per side in Ø3.00mm knuckle), providing a snug, smooth sliding fit without wobble or relaxed slack.
  - Split cantilever snap barb: **Ø3.05 mm** with $0.75\text{ mm}$ flex slot, $1.50\text{ mm}$ conical lead-in ramp, compressing effortlessly through Ø3.00mm hole.
  - Snap retaining collar ring: **Ø4.80 mm OD x 1.80 mm height**, inner bore **Ø2.85 mm** with **Ø3.15 mm x 0.70 mm counterbore detent** that snaps permanently over the barb.
  - Dual print orientations provided: Horizontal flat-bottom pin with $0.20\text{ mm}$ bed contact facet for 100% bed adhesion and zero supports (5x layer line strength), plus vertical concentric pin.
* **Retrofit Snap Adapter Coupler for Modular Planters:**
  - For previously printed base planters that lack the 3-tier Lego interlocking rim, provide a compact $18.0\text{ mm}$ tall Retrofit Snap Adapter Coupler (`oval_planter_retrofit_snap_adapter.stl` & `.step`).
  - Sits flat on $Z = 0$ for support-free printing. Bottom face glues flush to the old base planter rim.
  - Top face features the standard 3-tier female receiving joint (female skirt pocket $7.5\text{ mm}$ deep, circular Lego boss sockets Ø15.7 x $3.5\text{ mm}$, through-bores Ø6.7mm).
  - Includes 4 concentric locator dowels (Ø6.0 x $16.0\text{ mm}$) that drop into base corner holes for 100% concentric, foolproof alignment while adhesive cures.
  - Enables new Extension Risers to snap onto old printed planters with **0.0 mm seam gap** and **0.000000 mm³ collision volume**!
