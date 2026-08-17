---
id: lhs:phys.work
type: quantity
name: Work
domain: physics
status: draft
definition: >-
  The product of the force applied to an object and the distance the object moves in the direction
  of the force. Work measures the transfer of energy by a mechanical force.
symbol: W
unit: joule (J)
equation: W = F·d·cos(θ)
common_misconceptions:
  - Holding a heavy object requires work (no displacement in the direction of force means no work by that force).
  - Work is a form of energy (work is the process of transferring energy; energy is the quantity).
  - More force always means more work (work depends on force, distance, AND the angle between them).
learning_objectives:
  - Define work as force × displacement in the direction of force.
  - Calculate work done by a constant force at various angles.
  - Distinguish between positive, negative, and zero work.
  - Explain when a force does no work.
real_world_applications:
  - Lifting objects against gravity.
  - Pushing a stalled car.
  - Work done by friction (always negative).
  - Energy billing (kWh is a unit of work/energy).
provenance:
  ai_drafted: true
relationships:
  - type: mathematically_requires
    target: lhs:phys.force
  - type: mathematically_requires
    target: lhs:phys.distance
  - type: related_to
    target: lhs:phys.energy
  - type: related_to
    target: lhs:phys.power
---

## Notes

Work is the mechanical means of transferring energy. It is defined precisely: force times
displacement in the direction of force. This precision matters — carrying a heavy suitcase
horizontally does no work against gravity, even though it feels tiring (the work is done by
muscles internally, not mechanically).
