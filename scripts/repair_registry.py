#!/usr/bin/env python3
"""Repair relation-registry.yaml inverse coherence (plan v2 E2.1/E2.7, ADR-0021).

Fixes the 39 inverse-coherence defects found by the external architecture audit
(docs/ARCHITECTURE-AUDIT-v1.0.md, F3):

  1. Relations whose `inverse:` names a relation that is not defined in the
     registry lose the `inverse:` field (a derived edge must never carry an
     illegal relation name).
  2. `appears_in_law` loses its bogus `inverse: contains` pairing (contains is a
     structural relation whose own inverse is contained_in — the pair was not
     mutual and its domain/range did not mirror).
  3. Symmetric relations never declare `inverse` (self-inverse fields are noise).
  4. `part_of.range` gains `quantity` so the part_of/has_part pair mirrors.
  5. `limited_by.range` loses `regime` (a vocabulary value, not an entity type).
  6. Relations used by zero canonical connections are marked `status: reserved`;
     relations in active use are marked `status: adopted`.
  7. Missing inverse relations for adopted relations are ADDED as first-class
     registry entries (mutual + domain/range mirrored), so the derived graph
     engine emits only legal relation names:
       mathematically_requires -> mathematically_required_by
       logically_requires      -> logically_required_by
       derived_from            -> is_basis_of
       applies_to              -> governed_by
       approximates            -> approximated_by
  8. `related_to` gains `misconception` in domain/range (specification §4.6:
     a Misconception participates via `related_to`).

Idempotent: running twice changes nothing. `scripts/validate.py` enforces the
coherence invariants (mutual inverse, mirrored domain/range, no symmetric
inverse, known entity types) so the registry can never drift back.
"""
from __future__ import annotations

import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "schema" / "relation-registry.yaml"
CONNECTIONS = ROOT / "connections"

# Explicit repair decisions (documented in ADR-0021).
DROP_INVERSE = {"appears_in_law"}  # bogus `contains` pairing


def load() -> dict:
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))


def used_relations() -> set[str]:
    used: set[str] = set()
    for p in sorted(CONNECTIONS.glob("*.yaml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        if isinstance(d, dict) and d.get("relation"):
            used.add(d["relation"])
    return used


def mirrored(meta: dict) -> dict:
    """Inverse descriptor: mirrored domain/range, same family/transitivity."""
    out = dict(meta)
    out["domain"] = list(meta.get("range") or [])
    out["range"] = list(meta.get("domain") or [])
    return out


def main() -> int:
    data = load()
    relations: dict = data.get("relations") or {}
    adopted = used_relations()

    # 7. Add missing inverse relations for adopted relations (before status pass).
    new_inverses: dict[str, tuple[str, dict]] = {}
    for name in sorted(adopted):
        meta = relations.get(name) or {}
        inv = meta.get("inverse")
        if not inv or inv in relations:
            continue
        inv_meta = mirrored(meta)
        inv_meta["inverse"] = name
        new_inverses[name] = (inv, inv_meta)

    # Rebuild ordered dict, inserting each new inverse right after its forward relation.
    rebuilt: dict = {}
    for name, meta in relations.items():
        rebuilt[name] = meta
        if name in new_inverses:
            inv_name, inv_meta = new_inverses[name]
            rebuilt[inv_name] = inv_meta
            print(f"added inverse relation: {inv_name} (inverse of {name})")
    relations = rebuilt

    changes = 0
    for name, meta in relations.items():
        meta["status"] = "adopted" if name in adopted else "reserved"
        if meta.get("symmetric") and "inverse" in meta:
            del meta["inverse"]  # 3. symmetric relations carry no inverse field
            changes += 1
        inv = meta.get("inverse")
        if name in DROP_INVERSE and "inverse" in meta:
            del meta["inverse"]  # 2. explicit de-pairing
            changes += 1
        elif inv is not None and inv not in relations:
            del meta["inverse"]  # 1. undefined inverse names
            changes += 1
            print(f"dropped undefined inverse on {name}: {inv!r}")
        if name == "part_of" and "quantity" not in (meta.get("range") or []):
            meta["range"] = list(meta.get("range") or []) + ["quantity"]  # 4.
            changes += 1
        if name == "limited_by" and "regime" in (meta.get("range") or []):
            meta["range"] = [t for t in meta["range"] if t != "regime"]  # 5.
            changes += 1
        if name == "related_to":  # 8. spec §4.6 misconception participation
            for side in ("domain", "range"):
                if "misconception" not in (meta.get(side) or []):
                    meta[side] = list(meta[side]) + ["misconception"]
                    changes += 1

    data["relations"] = relations
    data["version"] = "0.3"

    header = (
        "# Relation Registry — authoritative source for relation semantics\n"
        "# ADR-012; integrity-repaired by ADR-0021 (plan v2 E2.1/E2.7; audit F3).\n"
        "# Validator enforces: registry membership, family, inverse/symmetric,\n"
        "# transitive, domain/range, INVERSE COHERENCE (mutual + mirrored),\n"
        "# and that domain/range reference known entity types only.\n"
        "#\n"
        "# status: adopted  — relation is used by canonical connections today.\n"
        "#         reserved — defined for future use, zero canonical uses;\n"
        "#                    do not introduce into canonical content without an ADR.\n"
        "# Inverses are DERIVED (never stored canonically) but MUST be defined here\n"
        "# so derived graph projections emit only legal relation names.\n"
        "#\n"
        "# Guardrails: extends/supersedes/isomorphic_to non-transitive; causal\n"
        "# non-transitive; is_a = class/subclass only.\n"
    )
    body = yaml.safe_dump(data, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)
    REGISTRY.write_text(header + body, encoding="utf-8")

    n_adopted = sum(1 for m in relations.values() if m.get("status") == "adopted")
    print(f"registry v{data['version']}: {len(relations)} relations "
          f"({n_adopted} adopted, {len(relations) - n_adopted} reserved); {changes} in-place repairs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
