# Global Grade-12 Curriculum Mapping (consumer-owned)

**Status:** consumer-owned reference mapping (NOT canonical content)
**Date:** 2026-09-01
**Related:** `docs/STEMMA-CONSUMER-SEAM.md`, `docs/NORTHSTAR.md`,
  `docs/decisions/0017-adaptive-metadata-extensions.md`

> **Boundary statement.** Per the NORTHSTAR and the canonical-knowledge pattern, **no
> grade, curriculum, or course tag appears in `content/`**. This document is a
> **consumer-owned mapping**: it references canonical entity IDs and groups them by the
> depth/coverage expectations of global grade-12 curricula (IB DP, A-Level, AP, CBSE Class
> 12, and similar). It is a bridge for consumers who sequence or filter by grade — it is
> **not** authoritative knowledge. The canonical IDs it references are the source of truth.

## What "global grade-12 depth" means here

A learner exiting an international grade-12 (age ~17–18) STEM program is expected to reason
with, compute with, and connect the following canonical entities. The mapping below groups
canonical IDs that a grade-12 curriculum typically covers, at "extended/advanced"
depth — not a fixed order (Knowledge order ≠ Curriculum order).

## Mathematics — grade-12 depth

| Canonical ID | Type | Grade-12 expectation |
|--------------|------|----------------------|
| `lhs:math.limit` | concept | Concept of limit, evaluate basic limits |
| `lhs:math.continuity` | concept | Identify continuity/differentiability conditions |
| `lhs:math.derivative` | quantity | Differentiation rules, rates of change, tangents |
| `lhs:math.integral` | quantity | Antiderivatives, indefinite integrals |
| `lhs:math.fundamental-theorem-of-calculus` | law | Relates differentiation and integration |
| `lhs:math.exponential-function` | concept | Growth/decay, natural exponent |
| `lhs:math.logarithmic-function` | concept | Inverse of exponential; rules |
| `lhs:math.matrix` | concept | Matrices, basic operations |
| `lhs:math.determinant` | quantity | 2×2 / 3×3 determinants, invertibility |
| `lhs:math.complex-number` | concept | Complex plane, arithmetic, conjugates |
| `lhs:math.sequence`, `arithmetic-sequence`, `geometric-sequence` | concept | Series, sums to n terms, limits |
| `lhs:math.standard-deviation` | quantity | Spread of data, normal-adjacent reasoning |
| `lhs:math.permutation`, `lhs:math.combination` | concept | Counting, binomial context |

**Anchor prerequisites already in depth:** `lhs:math.function`, `linear-function`,
`quadratic-function`, `polynomial`, `algebraic-expression`, `variable`,
`trigonometric-ratio`, `pythagorean-theorem`.

## Physics — grade-12 depth

| Canonical ID | Type | Grade-12 expectation |
|--------------|------|----------------------|
| `lhs:phys.simple-harmonic-motion` | concept | SHM, periodicity, energy |
| `lhs:phys.wave-interference` | concept | Superposition, constructive/destructive |
| `lhs:phys.doppler-effect` | concept | Frequency shift for moving source/observer |
| `lhs:phys.electromagnetic-wave` | concept | EM wave nature (transverse) |
| `lhs:phys.electric-field` | concept | Field lines, E = F/q |
| `lhs:phys.capacitor` | concept | Charge storage, capacitance |
| `lhs:phys.magnetic-force` | concept | Force on charge/current in a field |
| `lhs:phys.half-life` | quantity | Radioactive decay half-life |
| `lhs:phys.nuclear-binding-energy` | quantity | Mass–energy, fission/fusion energy |
| `lhs:phys.quantized-energy-levels` | concept | Atomic energy quantization |
| `lhs:phys.heat-capacity`, `lhs:phys.phase-change` | quantity/concept | Thermal energy transfer, latent heat |

**Anchor prerequisites already in depth:** Newton's laws, momentum/impulse, work–energy,
waves (wavelength/frequency/amplitude/sound/light), electromagnetism (charge, current,
voltage, resistance, Ohm's law, induction), radioactivity, photoelectric effect.

## Chemistry — grade-12 depth

| Canonical ID | Type | Grade-12 expectation |
|--------------|------|----------------------|
| `lhs:chem.hydrocarbon`, `alkane`, `alkene` | concept | Organic families, structure, IUPAC naming |
| `lhs:chem.functional-group`, `alcohol`, `carboxylic-acid` | concept | Functional chemistry |
| `lhs:chem.polymer`, `lhs:chem.isomer` | concept | Polymerization, structural isomerism |
| `lhs:chem.chemical-equilibrium`, `equilibrium-constant` | concept/quantity | Dynamic equilibrium, K expression |
| `lhs:chem.le-chateliers-principle` | law | Shifts with concentration/pressure/temperature |
| `lhs:chem.reaction-rate`, `activation-energy`, `catalyst` | quantity/concept | Kinetics, factors, catalysis |
| `lhs:chem.oxidation-reduction`, `oxidation-number` | concept/quantity | Redox, oxidation states |
| `lhs:chem.electrochemical-cell`, `electrolysis` | concept | Voltaic/electrolytic cells |
| `lhs:chem.enthalpy`, `entropy`, `gibbs-free-energy` | quantity | Thermochemistry, spontaneity |

**Anchor prerequisites already in depth:** atom, element, compound, periodic table,
electron/proton, ionic/covalent bonds, acids/bases, salts, neutralization, pH.

## Biology — grade-12 depth

| Canonical ID | Type | Grade-12 expectation |
|--------------|------|----------------------|
| `lhs:bio.dna-replication`, `transcription`, `translation` | concept | Central dogma mechanics |
| `lhs:bio.allele`, `chromosome`, `inheritance-patterns` | concept | Mendelian/quantitative inheritance |
| `lhs:bio.meiosis`, `mitosis` | concept | Cell division, gamete formation |
| `lhs:bio.mutation`, `protein-synthesis` | concept | Variation and expression |
| `lhs:bio.speciation`, `adaptation`, `population-dynamics` | concept | Evolution and ecology |
| `lhs:bio.food-chain`, `energy-flow-ecosystem` | concept | Trophic energy transfer |
| `lhs:bio.glycolysis` | concept | Cellular respiration pathway |
| `lhs:bio.immune-system`, `nervous-system`, `hormone`, `neuron` | concept | Systems physiology |

**Anchor prerequisites already in depth:** cell, animal/plant cell, nucleus, DNA, gene,
enzyme, homeostasis, osmosis, photosynthesis, cellular respiration, natural selection,
ecosystem.

## How consumers use this mapping

This mapping is **consumer-owned** and lives outside `content/`. A consumer (e.g. LearningHub
Phase 8+, PROFESSOR-J `lhs_adapter`) may:

1. Import `exports/knowledge.json` (contract `export_version 0.1`).
2. Resolve every canonical ID above to its entity.
3. Sequence or tag lessons by "grade-12 coverage" using this table — the grade is a
   **consumer-side concern**, never embedded into canonical entities.

It is intentionally curriculum-agnostic upstream: STEMMA keeps the definitions; consumers own
the grade/sequence. If a canonical ID in this table is missing from a future export, the
consumer adapter must fail loudly (dangling reference) rather than silently skip — per the
consumer-seam contract.

## Why this is not in `content/`

Encoding "grade 12" into a canonical definition would (a) violate the NORTHSTAR boundary,
(b) couple the knowledge foundation to one curriculum scale, and (c) break the
curriculum-agnostic principle. The mapping document keeps the separation:
**canonical IDs in `content/`, grade semantics in `docs/`, owned by consumers.**