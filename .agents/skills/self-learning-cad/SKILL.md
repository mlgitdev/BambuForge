---
name: self-learning-cad
description: >-
  Continuous self-learning and preference-calibration skill for 3D modeling on the
  Bambu Lab P2S. Captures user feedback, dimensional corrections, fit adjustments,
  aesthetic preferences, and overhang/support lessons from conversation turns, closing
  the gap between initial CAD generation and the user's exact expectations. Activate
  whenever the user requests fine-tuning, corrects a design, reports post-print fit
  results, or states a modeling preference.
---

# Self-Learning CAD & Gap-Closing Skill

This skill ensures that **every fine-tuning request or correction you give teaches the workspace permanently**, closing the gap between what you ask for and the first-pass model I generate.

---

## 1. When to Trigger This Skill

Activate this workflow automatically whenever:
1. **Fine-Tuning / Iteration:** The user asks to tweak a generated model (e.g., *"make the walls thicker"*, *"the M3 hole was too tight"*, *"round the corners more"*, *"change that overhang to a 45° ramp"*).
2. **Post-Print Feedback:** The user reports how a part printed on the Bambu Lab P2S or sliced in Bambu Studio (e.g., *"Bambu Studio wanted supports under the clip"*, *"the snap lid was too loose in PETG"*).
3. **Explicit Preference Statement:** The user states a recurring design rule or preference.

---

## 2. The 4-Step Gap-Closing Loop

Whenever triggered, execute these four steps in order:

### Step 1: Diagnose the Root Cause ("Why was there a gap?")
Classify the user's adjustment into one of five categories:
* `tolerance_calibration` — Real-world P2S dimensional fit (press/snug/sliding/screw clearance).
* `support_free_geometry` — A feature that triggered slicer supports or sagged during bridging/overhangs.
* `structural_strength` — Wall thickness, fillet/chamfer stress relief, layer orientation, or gusset sizing.
* `ergonomics_aesthetics` — Corner radii, edge chamfer feel, proportions, or visual styling.
* `workflow_organization` — File naming, export format (`.3mf` vs `.stl`), parameter grouping, or preview angles.

### Step 2: Apply the Fix to the Active Model
Update `models/<model-name>/<model-name>.py` (or CAD script), re-run `render_preview.py` and `analyze.py`, and verify the fix visually and numerically.

### Step 3: Persist the Lesson via `scripts/log_learning.py`
Log the structured lesson so it is recorded in `references/feedback-log.jsonl` and `references/learned-preferences.md`:

```powershell
python ".agents\skills\self-learning-cad\scripts\log_learning.py" --category "<category>" --model "<model-name>" --gap "<what needed tuning>" --rule "<new permanent default rule>"
```

### Step 4: Promote Global Rules to `AGENTS.md` and `3d-print-modeling`
* If a tolerance changed (e.g., snug fit changed from `0.14 mm` to `0.18 mm`), update the **Calibrated Tolerances & Fit Table** in `AGENTS.md` and the default constants in `.agents/skills/3d-print-modeling/references/fdm-design-principles.md`.
* If a new reusable geometry pattern was invented during fine-tuning, add it as a reusable parametric module in `fdm-design-principles.md`.

### Step 5: Synchronize with Public Repository (`bambuforge-repo-sync`)
Once global rules or skills have been updated, propagate the improvements to the `BambuForge` GitHub repository:
```powershell
python ".agents\skills\bambuforge-repo-sync\scripts\sync_to_bambuforge.py" --bump patch --commit-msg "feat(learning): calibrate tolerances from physical print feedback"
```
This sanitizes any local environment references, audits 0 PII, and keeps public documentation aligned.
