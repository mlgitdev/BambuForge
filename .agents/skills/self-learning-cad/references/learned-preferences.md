# Learned User Preferences & Calibrated CAD Rules

> **Purpose:** This file is the living memory of your personal 3D modeling workspace. As you provide fit feedback, dimensional tweaks, or aesthetic preferences, the `self-learning-cad` skill appends your personal rules here so the agent never repeats a mistake.
>
> **Universal FDM Rules:** General-purpose, community-applicable design standards live in [`fdm-design-principles.md`](../../3d-print-modeling/references/fdm-design-principles.md).

---

## 1. Core Baseline Preferences

* **Primary CAD Engine:** `build123d` (Python OpenCascade B-Rep) + FreeCAD-compatible `.step` / `.3mf` / `.stl`.
* **Support-Free Priority:** High (`<= 45°` overhangs, `Z = 0` chamfers, teardrop horizontal holes `> 5 mm`).
* **Infill Default:** `gyroid` sparse infill (`40–50%` for print-flat structural rods).

---

## 2. Personal Fine-Tuning Rules Log

| Date | Category | Model | Gap Identified | Permanent Rule Adopted |
| :--- | :--- | :--- | :--- | :--- |
