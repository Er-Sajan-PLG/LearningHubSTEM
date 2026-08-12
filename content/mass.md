---
id: lhs:phys.mass
type: quantity
name: Mass
domain: physics
status: draft
definition: >-
  A property of a body that quantifies its resistance to acceleration in Newtonian mechanics.
provenance:
  ai_drafted: true
relationships:
  - type: related_to
    target: lhs:phys.force
    note: force scales with mass at fixed acceleration
  - type: appears_in_law
    target: lhs:phys.newtons-second-law
  - type: mathematically_requires
    target: lhs:phys.acceleration
    note: acceleration is defined as rate of change of velocity, not of mass
---

## Notes

This seed describes mass only as involved in force and acceleration relationships within the
Newtonian model. Further relationships (gravitation, inertia, energy) are future content.