---
id: lhs:chem.gibbs-free-energy
type: quantity
name: Gibbs Free Energy
domain: chemistry
status: draft
definition: >-
  A thermodynamic quantity, G = H − TS, that combines enthalpy and entropy to predict whether a
  process is spontaneous at constant temperature and pressure. A negative Gibbs free energy change
  indicates a spontaneous process.
symbol: G
unit: J
equation: "ΔG = ΔH − TΔS"
examples:
  - "Ice melting above 0 °C is spontaneous despite being endothermic because TΔS outweighs ΔH."
  - "A negative ΔG for rusting predicts that iron oxidizes spontaneously in air."
key_experiments:
  - "Mix solutions whose precipitate formation has known ΔG and observe spontaneity directly."
common_misconceptions:
  - A negative ΔH alone guarantees spontaneity (entropy and temperature also matter via TΔS).
  - Spontaneous means fast (spontaneous only refers to thermodynamic favorability, not reaction speed).
learning_objectives:
  - Relate Gibbs free energy to enthalpy, entropy, and temperature.
  - Predict spontaneity from the sign of ΔG.
  - Connect ΔG to the equilibrium constant and cell potential.
real_world_applications:
  - Predicting corrosion, metabolic feasibility, and phase stability.
  - Designing batteries and assessing the viability of chemical synthesis.
provenance:
  ai_drafted: true
  source_kind: textbook
  source: Atkins' Physical Chemistry
relationships:
  - type: mathematically_requires
    target: lhs:chem.enthalpy
  - type: mathematically_requires
    target: lhs:chem.entropy
  - type: related_to
    target: lhs:chem.equilibrium-constant
---