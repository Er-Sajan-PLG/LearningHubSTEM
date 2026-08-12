---
id: lhs:phys.acceleration
type: quantity
name: Acceleration
domain: physics
status: draft
definition: >-
  The rate of change of velocity with respect to time.
provenance:
  ai_drafted: true
relationships:
  - type: mathematically_requires
    target: lhs:phys.force
    note: a = F/m in Newtonian mechanics
  - type: mathematically_requires
    target: lhs:phys.mass
    note: a = F/m
  - type: appears_in_law
    target: lhs:phys.newtons-second-law
---

## Notes

Acceleration is a derived quantity in classical mechanics; its relationship to force and mass
encodes the Newtonian model without prescribing any curriculum sequence.