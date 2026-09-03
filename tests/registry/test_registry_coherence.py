"""Registry integrity tests (plan v2 E2.1/E2.2; audit F3)."""
import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _registry():
    return yaml.safe_load((ROOT / "schema" / "relation-registry.yaml").read_text())["relations"]


def _entity_types():
    schema = json.loads((ROOT / "schema" / "concept.schema.json").read_text())
    return set(schema["properties"]["type"]["enum"])


def test_inverse_mutual_and_mirrored():
    rels = _registry()
    for name, meta in rels.items():
        inv = meta.get("inverse")
        if inv is None:
            continue
        assert inv in rels, f"{name}: inverse '{inv}' not defined"
        assert rels[inv].get("inverse") == name, f"{name}: inverse not mutual with {inv}"
        assert sorted(meta.get("domain") or []) == sorted(rels[inv].get("range") or []), \
            f"{name}.domain != {inv}.range"
        assert sorted(meta.get("range") or []) == sorted(rels[inv].get("domain") or []), \
            f"{name}.range != {inv}.domain"
    print("PASS: every inverse is mutual and domain/range mirrored")


def test_symmetric_relations_have_no_inverse():
    for name, meta in _registry().items():
        assert not (meta.get("symmetric") and meta.get("inverse")), \
            f"{name}: symmetric relation must not declare an inverse"
    print("PASS: symmetric relations carry no inverse field")


def test_domain_range_reference_known_types():
    known = _entity_types()
    for name, meta in _registry().items():
        for side in ("domain", "range"):
            for t in meta.get(side) or []:
                assert t in known, f"{name}: {side} references unknown entity type '{t}'"
    print("PASS: registry domain/range reference known entity types only")


def test_guardrails_preserved():
    rels = _registry()
    for name in ("extends", "supersedes", "isomorphic_to"):
        assert rels[name]["transitive"] is False, f"{name} must stay non-transitive"
    for name in ("causes", "contributes_to", "results_in", "influences", "prevents"):
        assert rels[name]["transitive"] is False, f"{name} must stay non-transitive"
    print("PASS: ADR-0012 non-transitivity guardrails preserved")


def test_adopted_relations_are_used_and_used_are_adopted():
    rels = _registry()
    used = set()
    for p in (ROOT / "connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        used.add(d["relation"])
    for name, meta in rels.items():
        status = meta.get("status")
        assert status in ("adopted", "reserved"), f"{name}: missing adopted/reserved status"
        if name in used:
            assert status == "adopted", f"{name} is used canonically but marked {status}"
    print(f"PASS: adopted/reserved discipline holds ({len(used)} relations in use)")


def test_new_inverses_derive_legally():
    # The derived graph engine names inverse edges from these entries; they must exist.
    rels = _registry()
    for fwd, inv in [
        ("mathematically_requires", "mathematically_required_by"),
        ("logically_requires", "logically_required_by"),
        ("derived_from", "is_basis_of"),
        ("applies_to", "governed_by"),
        ("approximates", "approximated_by"),
    ]:
        assert inv in rels, f"missing inverse relation {inv}"
        assert rels[fwd]["inverse"] == inv
    print("PASS: adopted relations have legal derived inverse names")


if __name__ == "__main__":
    test_inverse_mutual_and_mirrored()
    test_symmetric_relations_have_no_inverse()
    test_domain_range_reference_known_types()
    test_guardrails_preserved()
    test_adopted_relations_are_used_and_used_are_adopted()
    test_new_inverses_derive_legally()
    print("ALL REGISTRY COHERENCE TESTS PASS")
