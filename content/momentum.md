---
id: lhs:phys.momentum
type: quantity
name: Momentum
domain: physics
status: draft
definition: >-
  The product of a body's mass and velocity; a vector quantity that is conserved in closed
  systems.
symbol: p
unit: kilogram metre per second (kg·m/s)
equation: p = m·v
common_misconceptions:
  - Momentum and kinetic energy are the same kind of quantity (momentum is a vector measured in
    kg·m/s; kinetic energy is a scalar measured in joules).
provenance:
  ai_drafted: true
relationships:
  - type: mathematically_requires
    target: lhs:phys.mass
    note: p = m·v is defined using mass
  - type: appears_in_law
    target: lhs:phys.newtons-second-law
  - type: related_to
    target: lhs:phys.force
    note: F = dp/dt connects force and momentum
---

## Notes

Momentum's seed relationships deliberately stop at what the graph can support; velocity is not
yet an entity in the seed.
