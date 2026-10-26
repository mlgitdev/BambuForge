name: "Agent Skill / Toolset Enhancement"
description: "Propose an improvement or addition to BambuForge agent skills"
title: "feat(skill): "
labels: ["enhancement", "skills"]
body:
  - type: markdown
    attributes:
      value: "### Skill / Agent Workflow Enhancement"
  - type: textarea
    id: skill_target
    attributes:
      label: Target Skill / Agent
      description: Which skill is being enhanced? (e.g. 3d-print-modeling, bambu-studio-ai, self-learning-cad)
      placeholder: e.g. 3d-print-modeling
    validations:
      required: true
  - type: textarea
    id: proposed_capability
    attributes:
      label: Proposed Workflow & Automation
      description: Explain the automation script, CLI utility, or prompt workflow.
    validations:
      required: true
