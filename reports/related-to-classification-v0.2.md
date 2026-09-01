# related_to Classification — v0.2

Conservative pipeline (deterministic, no embedding-based auto-upgrade).

- Total `related_to`: 213
- Proposals generated: 36
- Remain `related_to`: 177

All proposals are `assertion.type: proposed, review: unreviewed` — **not canonical**.
Stronger relations (causes, requires, mathematically_requires, contradicts, explains) are never auto-applied.

## Proposal sample (first 20)

- `lhs:conn.000004`: `lhs:bio.cell` —related_to→ `lhs:chem.compound` → **bridges** — cross-domain biology↔chemistry; possible bridge/shared mechanism
- `lhs:conn.000008`: `lhs:bio.cellular-respiration` —related_to→ `lhs:phys.energy` → **bridges** — cross-domain biology↔physics; possible bridge/shared mechanism
- `lhs:conn.000011`: `lhs:bio.homeostasis` —related_to→ `lhs:phys.temperature` → **bridges** — cross-domain biology↔physics; possible bridge/shared mechanism
- `lhs:conn.000015`: `lhs:bio.osmosis` —related_to→ `lhs:phys.pressure` → **bridges** — cross-domain biology↔physics; possible bridge/shared mechanism
- `lhs:conn.000022`: `lhs:bio.ecosystem` —related_to→ `lhs:phys.energy` → **bridges** — cross-domain biology↔physics; possible bridge/shared mechanism
- `lhs:conn.000026`: `lhs:bio.dna` —related_to→ `lhs:chem.covalent-bond` → **bridges** — cross-domain biology↔chemistry; possible bridge/shared mechanism
- `lhs:conn.000031`: `lhs:bio.enzyme` —related_to→ `lhs:chem.compound` → **bridges** — cross-domain biology↔chemistry; possible bridge/shared mechanism
- `lhs:conn.000050`: `lhs:chem.atom` —related_to→ `lhs:phys.atomic-structure` → **bridges** — cross-domain chemistry↔physics; possible bridge/shared mechanism
- `lhs:conn.000067`: `lhs:chem.diffusion` —related_to→ `lhs:phys.temperature` → **bridges** — cross-domain chemistry↔physics; possible bridge/shared mechanism
- `lhs:conn.000068`: `lhs:chem.diffusion` —related_to→ `lhs:bio.osmosis` → **bridges** — cross-domain chemistry↔biology; possible bridge/shared mechanism
- `lhs:conn.000070`: `lhs:chem.matter` —related_to→ `lhs:phys.density` → **bridges** — cross-domain chemistry↔physics; possible bridge/shared mechanism
- `lhs:conn.000080`: `lhs:chem.chemical-reaction` —related_to→ `lhs:phys.energy` → **bridges** — cross-domain chemistry↔physics; possible bridge/shared mechanism
- `lhs:conn.000082`: `lhs:chem.combustion` —related_to→ `lhs:phys.energy` → **bridges** — cross-domain chemistry↔physics; possible bridge/shared mechanism
- `lhs:conn.000083`: `lhs:chem.combustion` —related_to→ `lhs:phys.our-environment` → **bridges** — cross-domain chemistry↔physics; possible bridge/shared mechanism
- `lhs:conn.000086`: `lhs:earth.atmosphere` —related_to→ `lhs:phys.gravitation` → **bridges** — cross-domain earth-space↔physics; possible bridge/shared mechanism
- `lhs:conn.000087`: `lhs:earth.atmosphere` —related_to→ `lhs:chem.acid` → **bridges** — cross-domain earth-space↔chemistry; possible bridge/shared mechanism
- `lhs:conn.000088`: `lhs:earth.atmosphere` —related_to→ `lhs:bio.cellular-respiration` → **bridges** — cross-domain earth-space↔biology; possible bridge/shared mechanism
- `lhs:conn.000092`: `lhs:earth.greenhouse-effect` —related_to→ `lhs:phys.thermal-energy` → **bridges** — cross-domain earth-space↔physics; possible bridge/shared mechanism
- `lhs:conn.000098`: `lhs:earth.water-cycle` —related_to→ `lhs:phys.heat` → **bridges** — cross-domain earth-space↔physics; possible bridge/shared mechanism
- `lhs:conn.000100`: `lhs:earth.earth-system` —related_to→ `lhs:bio.cell` → **bridges** — cross-domain earth-space↔biology; possible bridge/shared mechanism

Full list: `reports/related-to-classification-v0.2.json` (36 entries)

## Invariant

All proposals remain `proposed/unreviewed`. Ambiguous cases remain `related_to`.
