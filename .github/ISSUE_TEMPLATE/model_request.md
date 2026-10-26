name: "3D Model / Parametric Feature Request"
description: "Request a new functional 3D printable model or parametric feature"
title: "feat(cad): "
labels: ["enhancement", "cad"]
body:
  - type: markdown
    attributes:
      value: "### Parametric Model / Feature Proposal"
  - type: textarea
    id: overview
    attributes:
      label: Model Concept & Use Case
      description: What functional object or planter is needed?
      placeholder: Describe the geometry, functional requirements, and assembly structure...
    validations:
      required: true
  - type: textarea
    id: specifications
    attributes:
      label: Key Dimensions & Tolerances
      description: Target printer envelope, critical clearances, and wall thickness.
      value: |
        - Max Outer Dimensions (X, Y, Z mm): 
        - Clearance / Fit Requirements:
        - Wall Thickness: 2.8mm - 3.2mm
        - Filament Type: PLA / PETG / ABS
    validations:
      required: true
