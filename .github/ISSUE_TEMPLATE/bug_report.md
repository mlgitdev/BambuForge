name: "Bug Report"
description: "Report a CAD geometry error, slicer artifact, or agent script bug"
title: "fix: "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: "### BambuForge Bug Report\nThank you for reporting an issue. Please provide detailed reproduction steps."
  - type: textarea
    id: description
    attributes:
      label: Problem Description
      description: What went wrong during CAD generation, slicing, or printing?
      placeholder: Describe the geometry defect, slicing error, or script failure...
    validations:
      required: true
  - type: textarea
    id: environment
    attributes:
      label: Environment & Tools
      description: Printer model, slicer version, filament material, OS.
      value: |
        - Printer: Bambu Lab P2S (or other)
        - Slicer: Bambu Studio / OrcaSlicer
        - Material: PLA / PETG / ABS / ASA
        - Python version: 3.10+
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: Steps to Reproduce
      placeholder: 1. Run script...\n2. Slice model in Bambu Studio...\n3. Observe error...
    validations:
      required: true
