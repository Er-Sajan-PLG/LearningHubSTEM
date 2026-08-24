---
id: lhs:phys.magnetic-flux
type: quantity
name: Magnetic Flux
domain: physics
status: draft
definition: >-
  A measure of the total magnetic field passing through a given surface area, calculated as the product of
  magnetic field strength perpendicular to the surface and the surface area.
symbol: Φ
unit: weber (Wb)
equation: Φ = B · A · cos(θ)
common_misconceptions:
  - Magnetic flux and magnetic field strength are identical (flux accounts for total area and orientation).
  - A stationary coil in a constant magnetic field has changing flux (flux only changes when field, area, or angle changes).
learning_objectives:
  - Define magnetic flux and calculate its value for a surface perpendicular to a uniform field.
  - State the SI unit of magnetic flux (weber).
  - Relate rate of change of magnetic flux to induced electromotive force.
real_world_applications:
  - Electric power transformers and induction cooktops.
  - Magnetic field sensors and hall-effect probes.
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: IUPAP Symbols, Units, Nomenclature in Physics
relationships:
  - type: logically_requires
    target: lhs:phys.magnetic-field
  - type: related_to
    target: lhs:phys.electromagnetic-induction
---

## Notes

1 Weber = 1 Tesla · meter squared. Changing magnetic flux induces voltage according to Faraday's law.
