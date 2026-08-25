---
id: lhs:phys.force
type: concept
name: Force
domain: physics
status: draft
definition: >-
  An influence that can change the motion of a body — that is, accelerate it. In classical mechanics
  the net force on a body equals the rate of change of its momentum. Force is a vector quantity.
symbol: F
unit: newton (N)
equation: F = dp/dt ; F = m·a (constant mass)
examples:
  - "Pushing a shopping trolley makes it accelerate."
  - "A magnet pulls a pin toward it — a contact-free force."
key_experiments:
  - "Kick or push a dynamics cart and record its acceleration with a motion sensor (F∝a)."
common_misconceptions:
  - A constant net force produces constant speed (it produces constant acceleration).
  - Force is a property of an object (force acts between objects; it is not possessed by one).
  - Objects at rest have no forces acting on them (forces can balance to give zero net force).
  - Heavier objects require more force to move because they have more "inertia" (inertia is resistance to acceleration, not weight).
learning_objectives:
  - Define force as a vector quantity that causes acceleration.
  - Distinguish between contact and non-contact forces.
  - Draw free-body diagrams showing forces acting on an object.
  - Calculate net force from multiple forces acting on an object.
  - Apply F = m·a to calculate force, mass, or acceleration.
real_world_applications:
  - Pushing, pulling, and lifting objects.
  - Vehicle acceleration and braking.
  - Engineering structures (forces in bridges, buildings).
  - Spacecraft propulsion.
key_experiments:
  - "Measuring force using a spring balance."
  - "Investigating the relationship between force, mass, and acceleration using a trolley and ticker-timer."
provenance:
  ai_drafted: true
relationships:
  - type: mathematically_requires
    target: lhs:phys.mass
  - type: mathematically_requires
    target: lhs:phys.acceleration
  - type: mathematically_requires
    target: lhs:phys.vector
  - type: appears_in_law
    target: lhs:phys.newtons-first-law
  - type: appears_in_law
    target: lhs:phys.newtons-second-law
  - type: appears_in_law
    target: lhs:phys.newtons-third-law
  - type: related_to
    target: lhs:phys.momentum
  - type: related_to
    target: lhs:phys.weight
---

## Notes

Force is the central concept in mechanics. It is not energy, not motion, not momentum — it is
the interaction that changes motion. Every mechanics problem ultimately asks: what is the net force,
and therefore what is the acceleration? Force is the bridge between the geometry of motion
(displacement, velocity, acceleration) and its cause.
