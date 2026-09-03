# Curation Status — v0.2

- Total connections: 654 (canonical objects)
- Canonical assertions (`review.status==canonical`): 50
- Reviewed-only: 0, Canonical: 50, Unreviewed: 604 (total reviewed inc. canonical: 50)
- Proposed: 653, Inferred: 0
- Migrated: 641, Human-authored: 13, LLM: 0
- Rejected: 0, Deprecated: 4
- Semantics: `reviewed-only` vs `canonical` (terminal); canonical implies reviewed

## By relation
{'special_case_of': 14, 'related_to': 371, 'logically_requires': 90, 'part_of': 24, 'derived_from': 3, 'mathematically_requires': 98, 'applies_to': 24, 'appears_in_law': 11, 'bridges': 6, 'analogous_to': 3, 'approximates': 3, 'generalizes': 7}

## By family
{'hierarchical': 21, 'associative': 371, 'dependency': 188, 'structural': 24, 'derivation': 38, 'cross_domain': 6, 'analogy': 3, 'model': 3}

## By domain
{'biology': 80, 'chemistry': 94, 'earth-space': 33, 'engineering': 1, 'physics': 302, 'scientific-practice': 2, 'mathematics': 142}

## By review
{'canonical': 50, 'unreviewed': 604}

## By origin
{'migrated': 641, 'human-authored': 13}

## Top reviewed (canonical)
- lhs:conn.000001: special_case_of lhs:bio.animal-cell -> lhs:bio.cell
- lhs:conn.000005: logically_requires lhs:bio.cellular-respiration -> lhs:bio.cell
- lhs:conn.000012: part_of lhs:bio.nucleus -> lhs:bio.cell
- lhs:conn.000014: logically_requires lhs:bio.osmosis -> lhs:chem.diffusion
- lhs:conn.000025: part_of lhs:bio.dna -> lhs:bio.cell
- lhs:conn.000048: logically_requires lhs:chem.atom -> lhs:chem.matter
- lhs:conn.000049: logically_requires lhs:chem.atom -> lhs:phys.electric-charge
- lhs:conn.000053: logically_requires lhs:chem.element -> lhs:chem.atom
- lhs:conn.000060: logically_requires lhs:chem.compound -> lhs:chem.atom
- lhs:conn.000069: logically_requires lhs:chem.matter -> lhs:phys.mass
- lhs:conn.000130: mathematically_requires lhs:phys.current -> lhs:phys.electric-charge
- lhs:conn.000131: mathematically_requires lhs:phys.current -> lhs:phys.time
- lhs:conn.000165: mathematically_requires lhs:phys.voltage -> lhs:phys.electric-charge
- lhs:conn.000173: logically_requires lhs:phys.measurement -> lhs:phys.unit
- lhs:conn.000177: logically_requires lhs:phys.time -> lhs:phys.measurement

## Remaining highest priority
- lhs:conn.000214: appears_in_law
- lhs:conn.000080: bridges
- lhs:conn.000008: bridges
- lhs:conn.000283: appears_in_law
- lhs:conn.000022: bridges
- lhs:conn.000258: appears_in_law
- lhs:conn.000086: bridges
- lhs:conn.000353: bridges
- lhs:conn.000082: bridges
- lhs:conn.000137: appears_in_law

## Gaps
- Evidence gaps: 599 (sample ['lhs:conn.000002', 'lhs:conn.000003', 'lhs:conn.000004'])
- Provenance gaps (no reviewed_by): 604

## Note
Schema correctness != semantic acceptance. Canonical objects (397) include 382 proposed/unreviewed.
