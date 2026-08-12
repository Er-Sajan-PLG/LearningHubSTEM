---
id: lhs:phys.momentum
type: quantity
name: Momentum
domain: physics
status: draft
definition: >-
  The product of a body's mass and velocity; a conserved quantity in closed systems.
provenance:
  ai_drafted: true
relationships:
  - type: mathematically_requires
    target: lhs:phys.mass
  - type: related_to
    target: lhs:phys.force
    note: F = dp/dt connects force and momentum
  - type: related_to
    target: lhs:phys.newtons-second-law
    note: law is most generally stated as rate of change of momentum
---

## Notes

Momentum's seed relationships deliberately stop at what the graph can support; velocity is not
yet an entity in the seed.