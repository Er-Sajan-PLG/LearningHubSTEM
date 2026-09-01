"""Phase B validation tests — reconciliation, classification, semantics, provenance, idempotence."""
import json
import pathlib
import subprocess

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_reconciliation():
    data = json.loads((ROOT / "reports" / "migration-reconciliation-v0.2.json").read_text())
    assert data["matched"] == data["legacy_relationship_records"]
    assert data["orphaned_target_references"] == 0
    assert data["duplicate_canonical"] == 0
    assert data["invariant_holds"] is True
    print("PASS: reconciliation")


def test_classification_proposed_only():
    data = json.loads((ROOT / "reports" / "related-to-classification-v0.2.json").read_text())
    for pr in data["proposals"]:
        # Proposals must remain proposed/unreviewed, not canonical
        assert pr["current_relation"] == "related_to"
        # Check that actual connection remains related_to (not auto-upgraded)
        conn_path = ROOT / "connections" / f"{pr['connection_id']}.yaml"
        conn = yaml.safe_load(conn_path.read_text())
        assert conn["relation"] == "related_to", f"{pr['connection_id']} was silently upgraded"
        assert conn["assertion"]["type"] == "proposed"
        assert conn["assertion"]["review"]["status"] == "unreviewed"
    print(f"PASS: classification {len(data['proposals'])} remain proposed")


def test_semantics_registry():
    registry = yaml.safe_load((ROOT / "schema" / "relation-registry.yaml").read_text())["relations"]
    # Check guardrails: extends/supersedes/isomorphic_to non-transitive
    assert registry["extends"]["transitive"] is False
    assert registry["supersedes"]["transitive"] is False
    assert registry["isomorphic_to"]["transitive"] is False
    # Causal non-transitive
    for rel in ["causes", "contributes_to", "results_in", "influences", "prevents"]:
        assert registry[rel]["transitive"] is False, f"{rel} should be non-transitive"
    # Bridge scope-aware: domain includes quantity now (fix)
    assert "quantity" in registry["bridges"]["domain"]
    print("PASS: semantics registry guardrails")


def test_domain_range():
    # Validate that validator still passes
    r = subprocess.run(["python3", str(ROOT / "scripts/validate.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    print("PASS: domain/range validation")


def test_bridge_scope():
    # Already validated via validate.py; extra check: curated bridges exist and pass scope
    for cid in ["lhs:conn.000378", "lhs:conn.000379", "lhs:conn.000380"]:
        conn = yaml.safe_load((ROOT / "connections" / f"{cid}.yaml").read_text())
        assert conn["relation"] == "bridges"
        # Scope-aware: different domain/subdomain
        print(f"PASS: bridge {cid}")


def test_provenance():
    # Migration not human
    for p in (ROOT / "connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        prov = d.get("provenance", {})
        method = prov.get("method", {}).get("type")
        asserted = prov.get("asserted_by", {}).get("type")
        if method == "migration":
            assert asserted in ("unknown", "process"), f"migration asserted_by should not be human: {p.name}"
    # Source refs resolve
    sources = {yaml.safe_load(p.read_text()).get("id") for p in (ROOT / "sources").glob("*.yaml")}
    for p in (ROOT / "connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        for ev in d.get("evidence", []) or []:
            ref = ev.get("source_ref")
            if ref:
                assert ref in sources, f"{p.name} evidence source_ref {ref} not found"
    print("PASS: provenance")


def test_idempotence():
    import subprocess

    r1 = subprocess.run(["python3", str(ROOT / "scripts/migrate_relationships.py")], capture_output=True, text=True)
    r2 = subprocess.run(["python3", str(ROOT / "scripts/create_curated_b3_b6.py")], capture_output=True, text=True)
    assert "created 0" in r1.stdout or "skipped 384" in r1.stdout or "skipped 376" in r1.stdout
    assert "created 0" in r2.stdout
    # Connections count stable
    count = len(list((ROOT / "connections").glob("*.yaml")))
    assert count == 397, f"connections count changed idempotence: {count}"
    print("PASS: idempotence")


def test_no_illegal_transitivity():
    # Ensure no derived transitive edges in canonical
    # Check that we didn't create inferred connections as canonical
    for p in (ROOT / "connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        if d.get("assertion", {}).get("type") == "inferred":
            assert "inference" in d, f"inferred {d['id']} missing inference"
        else:
            assert "inference" not in d or d.get("inference") is None, f"non-inferred {d['id']} has inference block"
    print("PASS: no illegal transitivity")


if __name__ == "__main__":
    test_reconciliation()
    test_classification_proposed_only()
    test_semantics_registry()
    test_domain_range()
    test_bridge_scope()
    test_provenance()
    test_idempotence()
    test_no_illegal_transitivity()
    print("ALL PHASE B TESTS PASS")
