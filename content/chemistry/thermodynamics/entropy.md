---
id: lhs:chem.entropy
type: quantity
name: Entropy
domain: chemistry
status: draft
definition: >-
  A thermodynamic quantity that measures the dispersal of energy or the number of microscopic
  arrangements (microstates) available to a system, expressed as a measure of disorder. The entropy
  of an isolated system tends to increase in spontaneous processes.
symbol: S
unit: J K⁻¹
equation: "ΔS = S_products − S_reactants"
examples:
  - "Melting ice increases entropy as the solid lattice gives way to mobile molecules."
  - "A gas expanding into a vacuum increases entropy because the molecules occupy more microstates."
key_experiments:
  - "Allow a gas to expand freely into an evacuated volume and reason about the increase in disorder."
common_misconceptions:
  - Entropy is the same as chaos or mess (it is a measure of energy dispersal and available microstates).
  - Entropy can never decrease locally (entropy can decrease in a system if the surroundings compensate).
learning_objectives:
  - Relate entropy to molecular disorder and the number of microstates.
  - Predict the sign of entropy change from states of matter and particle counts.
  - State the second law of thermodynamics in terms of entropy.
real_world_applications:
  - Predicting the feasibility of processes via entropy and free energy.
  - Understanding the direction of heat flow and energy conservation in engines.
provenance:
  ai_drafted: true
  source_kind: textbook
  source: Atkins' Physical Chemistry
relationships:
  - type: related_to
    target: lhs:chem.enthalpy
  - type: related_to
    target: lhs:chem.gibbs-free-energy
---