"""Inline-projection invariant tests (plan v2 E1.2/E1.3, ADR-0020; audit F1)."""
import pathlib
import subprocess

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _projection():
    proj = {}
    for p in sorted((ROOT / "connections").glob("*.yaml")):
        c = yaml.safe_load(p.read_text())
        if c.get("assertion", {}).get("status") != "active":
            continue
        proj.setdefault(c["source"], set()).add((c["relation"], c["target"]))
    return proj


def test_inline_equals_connection_projection():
    proj = _projection()
    drift = []
    for p in sorted((ROOT / "content").rglob("*.md")):
        e = yaml.safe_load(p.read_text().split("---", 2)[1])
        actual = {(r["type"], r["target"]) for r in (e.get("relationships") or [])}
        expected = proj.get(e["id"], set())
        if actual != expected:
            drift.append((e["id"], sorted(expected - actual), sorted(actual - expected)))
    assert not drift, f"inline != projection for {drift[:5]}; run scripts/sync_relationships.py"
    print(f"PASS: inline relationships equal the connections projection "
          f"({sum(len(v) for v in proj.values())} edges)")


def test_sync_is_idempotent():
    r = subprocess.run(["python3", str(ROOT / "scripts" / "sync_relationships.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "synced 0" in r.stdout, f"sync not idempotent:\n{r.stdout}"
    print("PASS: sync_relationships is idempotent (0 changes on second run)")


def test_no_materialized_inverse_pairs():
    # ADR-0012: inverse edges are DERIVED, never stored canonically. Two active
    # connections that are exact inverses of each other (A -R-> B plus B -inv(R)-> A)
    # are a materialization violation. Individual inverse-NAMED relations are fine
    # when independently meaningful (e.g. special_case_of).
    registry = yaml.safe_load((ROOT / "schema" / "relation-registry.yaml").read_text())["relations"]
    edges = set()
    for p in (ROOT / "connections").glob("*.yaml"):
        c = yaml.safe_load(p.read_text())
        if c.get("assertion", {}).get("status") == "active":
            edges.add((c["source"], c["relation"], c["target"]))
    violations = []
    for (src, rel, tgt) in edges:
        inv = (registry.get(rel) or {}).get("inverse")
        if inv and (tgt, inv, src) in edges:
            violations.append((src, rel, tgt, inv))
    assert not violations, f"materialized inverse pairs in canonical: {violations[:5]}"
    print("PASS: no materialized inverse pairs stored canonically")



# --- E1.6: the explorer builds its graph from connections[], not the inline projection ---

EXPLORER_SRC = ROOT / "explorer" / "src" / "services"


def test_explorer_edges_come_from_connections():
    src = (EXPLORER_SRC / "graph-projection.ts").read_text(encoding="utf-8")
    assert "export function collectEdges" in src, "collectEdges (the connections-first edge source) is missing"
    assert "exportData.connections" in src, "graph projection must read connections[] (ADR-0020 / E1.6)"
    # The inline projection may appear ONLY inside the documented fallback.
    fallback = src.split("// Fallback: deprecated inline projection", 1)
    assert len(fallback) == 2, "the inline projection must be confined to a documented fallback"
    body_after_collect = src.split("export function projectKnowledgeGraph", 1)[1]
    assert "relationships" not in body_after_collect, \
        "projectKnowledgeGraph must not read entities[].relationships directly"
    print("PASS: explorer graph projection builds from connections[] (inline only as fallback)")


def test_explorer_annotates_edges_by_review_status():
    src = (EXPLORER_SRC / "graph-projection.ts").read_text(encoding="utf-8")
    for token in ("reviewStatus", "REVIEW_OPACITY", "canonical", "unreviewed"):
        assert token in src, f"missing trust annotation token: {token}"
    view = (ROOT / "explorer" / "src" / "components" / "graph-view.ts").read_text(encoding="utf-8")
    assert "link.opacity" in view, "graph-view must render the trust-graded edge opacity (E1.6)"
    print("PASS: explorer edges are annotated and rendered by review status")


def test_concept_details_use_canonical_edges():
    src = (EXPLORER_SRC / "concept-data.ts").read_text(encoding="utf-8")
    assert "collectEdges" in src, "concept details must resolve prerequisites from canonical edges"
    assert "relationships ?? []" not in src, "concept details must not read the deprecated inline projection"
    print("PASS: concept prerequisites/dependents resolve from canonical connections")


if __name__ == "__main__":
    test_inline_equals_connection_projection()
    test_sync_is_idempotent()
    test_no_materialized_inverse_pairs()
    test_explorer_edges_come_from_connections()
    test_explorer_annotates_edges_by_review_status()
    test_concept_details_use_canonical_edges()
    print("ALL PROJECTION SYNC TESTS PASS")
