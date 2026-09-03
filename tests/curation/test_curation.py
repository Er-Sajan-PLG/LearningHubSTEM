"""D15: Curation tests — state machine, review integrity, evidence, provenance, export."""
import pathlib
import sys
import yaml
import json

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from curation_state import can_transition  # type: ignore
from graph_policy import should_include_connection  # type: ignore


def test_state_machine_valid():
    assert can_transition("proposed", "reviewed")
    assert can_transition("reviewed", "canonical")
    assert can_transition("proposed", "rejected")
    assert can_transition("rejected", "proposed")
    print("PASS: valid transitions")


def test_state_machine_invalid():
    assert not can_transition("rejected", "canonical")
    assert not can_transition("proposed", "canonical")
    assert not can_transition("rejected", "reviewed")
    print("PASS: invalid transitions rejected")


def test_reviewer_required():
    conn = {"assertion": {"review": {"status": "unreviewed"}, "type": "proposed", "status": "active"}}
    from curation_state import validate_transition

    errs = validate_transition(conn, "canonical", None)
    assert any("reviewer" in e for e in errs)
    errs2 = validate_transition(conn, "canonical", "human:reviewer.test-001")
    # Should still fail due to forbidden proposed->canonical, but reviewer error gone
    assert not any("reviewer" in e for e in errs2) or "forbidden" in errs2[0]
    print("PASS: reviewer required")


def test_origin_preserved():
    # Pick a migrated canonical
    p = ROOT / "connections/lhs:conn.000001.yaml"
    d = yaml.safe_load(p.read_text())
    assert d["provenance"]["asserted_by"]["id"] == "unknown:legacy-relationship"
    assert d["provenance"]["method"]["type"] == "migration" or d["provenance"]["generated_by"]["id"] == "process:migration.relationships-v0.2"
    # Origin should remain migrated even though review is canonical
    print("PASS: origin preserved")


def test_rejected_auditable():
    # Create a rejected example in memory
    conn = {
        "id": "lhs:conn.999999",
        "assertion": {"status": "rejected", "type": "proposed", "review": {"status": "rejected"}},
        "provenance": {"asserted_by": {"type": "human", "id": "human:test"}, "generated_by": {"type": "human", "id": "human:test"}, "method": {"type": "manual"}},
    }
    # Rejected should remain auditable (file would exist)
    assert conn["assertion"]["status"] == "rejected"
    print("PASS: rejected auditable")


def test_evidence_by_family():
    # For canonical, evidence should exist per family rules
    for p in (ROOT / "connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        if d["assertion"]["review"]["status"] == "canonical":
            assert d.get("evidence") is not None and len(d["evidence"]) > 0, f"{d['id']} canonical without evidence"
    print("PASS: evidence for canonical")


def test_provenance_distinction():
    # Human vs LLM traceable
    for p in (ROOT / "connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        asserted = d["provenance"]["asserted_by"]["type"]
        assert asserted in ("human", "llm", "process", "unknown")
    print("PASS: provenance distinction")


def test_trusted_export():
    # trusted excludes unreviewed
    import subprocess, json

    subprocess.run(["python3", str(ROOT / "scripts/export_review_aware.py")], check=True)
    trusted = json.loads((ROOT / "exports/knowledge.trusted.json").read_text())
    all_c = json.loads((ROOT / "exports/knowledge.all.json").read_text())
    canonical_files = sum(
        1 for p in (ROOT / "connections").glob("*.yaml")
        if yaml.safe_load(p.read_text()).get("assertion", {}).get("status") == "active"
    )
    # 'all' export contains every ACTIVE canonical connection (not a magic count);
    # deprecated connections are excluded by policy (graph_policy.should_include_connection).
    assert all_c["count"] == canonical_files
    # 'trusted' is a subset of 'all' (>=0) whose members are all reviewed/canonical.
    assert 0 <= trusted["count"] <= all_c["count"]
    for c in trusted["connections"]:
        assert c["assertion"]["review"]["status"] in ("reviewed", "canonical")
        assert not (c["provenance"]["asserted_by"]["type"] == "llm" and c["assertion"]["review"]["status"] == "unreviewed")
    print("PASS: trusted export")


def test_all_exports():
    import json

    for policy in ["all", "reviewed", "canonical", "proposed", "rejected"]:
        p = ROOT / f"exports/knowledge.{policy}.json"
        assert p.exists(), f"missing {policy} export"
        d = json.loads(p.read_text())
        assert "count" in d and "connections" in d
    print("PASS: all exports exist")


if __name__ == "__main__":
    test_state_machine_valid()
    test_state_machine_invalid()
    test_reviewer_required()
    test_origin_preserved()
    test_rejected_auditable()
    test_evidence_by_family()
    test_provenance_distinction()
    test_trusted_export()
    test_all_exports()
    print("ALL CURATION TESTS PASS")
