"""Claim integrity tests — plan v2 E4.3 / E4.4 / E4.5 (audit F5, F7, F11).

Property-based over the real tree where cheap, and pure-function based where the
interesting cases (a duplicate claim, an edit in place, a rewritten triple) do not exist
in the repository yet and must be constructed.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import validate as v  # noqa: E402
import check_content_hashes as cch  # noqa: E402
import check_id_immutability as cid  # noqa: E402


def _conn(cid_="lhs:conn.900001", source="lhs:phys.force", relation="related_to",
          target="lhs:phys.mass", polarity="positive", qualifiers=None):
    return {
        "_file": f"connections/{cid_}.yaml",
        "id": cid_,
        "source": source,
        "relation": relation,
        "target": target,
        "assertion": {"status": "active", "polarity": polarity, "review": {"status": "unreviewed"}},
        "context": {"qualifiers": qualifiers or []},
    }


# --- E4.3 claim signature ---------------------------------------------------

def test_signature_ignores_file_and_provenance():
    a = _conn("lhs:conn.900001")
    b = _conn("lhs:conn.900002")
    b["provenance"] = {"asserted_by": {"id": "human:x"}}
    assert v.claim_signature(a) == v.claim_signature(b)
    print("PASS: claim signature depends on the claim, not the file or provenance")


def test_signature_is_qualifier_order_insensitive_but_content_sensitive():
    a = _conn(qualifiers=["low-speed", "vacuum"])
    b = _conn(qualifiers=["vacuum", "low-speed"])
    c = _conn(qualifiers=["vacuum"])
    d = _conn(polarity="negative")
    assert v.claim_signature(a) == v.claim_signature(b)
    assert v.claim_signature(a) != v.claim_signature(c)
    assert v.claim_signature(a) != v.claim_signature(d)
    print("PASS: signature normalises qualifier order; polarity and qualifiers are significant")


def test_duplicate_claims_detected_and_qualifier_disambiguates():
    dupes = {"a": _conn("lhs:conn.900001"), "b": _conn("lhs:conn.900002")}
    errors = []
    v.check_duplicate_claims(dupes, errors)
    assert len(errors) == 1 and "duplicate claim" in errors[0], errors

    dupes["b"]["context"]["qualifiers"] = ["in-vacuum"]
    errors = []
    v.check_duplicate_claims(dupes, errors)
    assert not errors, errors
    print("PASS: duplicate claims fail the gate; a distinguishing qualifier clears it")


def test_retracted_duplicates_are_exempt():
    conns = {"a": _conn("lhs:conn.900001"), "b": _conn("lhs:conn.900002")}
    conns["b"]["assertion"]["status"] = "retracted"
    errors = []
    v.check_duplicate_claims(conns, errors)
    assert not errors, errors
    print("PASS: a retracted twin is history, not a duplicate claim")


def test_repository_has_no_duplicate_claims():
    errors: list = []
    entities = {}
    for path in sorted((ROOT / "content").rglob("*.md")):
        try:
            e = v.parse_entity(path)
        except ValueError:
            continue
        entities[e["id"]] = e
    connections = v.load_canonical_yaml_dir(ROOT / "connections", v.CONN_SCHEMA, errors, entities, {})
    dupes: list = []
    v.check_duplicate_claims(connections, dupes)
    assert not dupes, dupes
    print(f"PASS: {len(connections)} connections carry {len({v.claim_signature(c) for c in connections.values()})} distinct claim signatures")


# --- E4.4 edit-in-place -----------------------------------------------------

def test_content_hash_ignores_provenance_churn():
    entity = {"id": "lhs:phys.force", "definition": "a push or a pull", "status": "reviewed"}
    other = dict(entity, provenance={"reviewer": "human:a"}, updated_at="2026-01-01")
    assert v.object_content_hash(entity) == v.object_content_hash(other)
    changed = dict(entity, definition="something else")
    assert v.object_content_hash(entity) != v.object_content_hash(changed)
    print("PASS: content hash tracks substance, not review bookkeeping")


def test_edit_in_place_fails_but_rereview_passes():
    prev = {"lhs:conn.000001": {"kind": "connection", "review_status": "canonical",
                                "content_hash": "sha256:aaa", "review_events": 3}}
    silent = {"lhs:conn.000001": dict(prev["lhs:conn.000001"], content_hash="sha256:bbb")}
    assert cch.detect(prev, silent), "silent edit must be reported"
    rereviewed = {"lhs:conn.000001": dict(prev["lhs:conn.000001"],
                                          content_hash="sha256:bbb", review_events=4)}
    assert not cch.detect(prev, rereviewed)
    newly = {"lhs:conn.000002": {"kind": "connection", "review_status": "reviewed",
                                 "content_hash": "sha256:ccc", "review_events": 1}}
    assert not cch.detect(prev, newly)
    print("PASS: edit-in-place fails; edit + new review event, and newly reviewed objects, pass")


# --- E4.5 connection triple immutability ------------------------------------

def test_triple_rewrite_and_deletion_detected():
    history = {"lhs:conn.000001": [
        {"commit": "aaaaaaaaa", "source": "lhs:a", "relation": "part_of", "target": "lhs:b",
         "assertion_status": "active"},
        {"commit": "bbbbbbbbb", "source": "lhs:a", "relation": "part_of", "target": "lhs:c",
         "assertion_status": "active"},
    ]}
    live = {"lhs:conn.000001": {"id": "lhs:conn.000001", "source": "lhs:a",
                                "relation": "part_of", "target": "lhs:c"}}
    out = cid.detect_connection_violations(history, live)
    assert any("[triple-rewritten]" in o for o in out), out

    stable = {"lhs:conn.000001": [history["lhs:conn.000001"][0]]}
    assert not cid.detect_connection_violations(stable, {"lhs:conn.000001": live["lhs:conn.000001"]})
    assert any("[deleted-connection]" in o for o in cid.detect_connection_violations(stable, {})), \
        "deleting a connection must be reported"
    print("PASS: rewritten triples and deleted connections are violations; stable triples pass")


def test_connection_parser_reads_the_real_files():
    sample = sorted((ROOT / "connections").glob("*.yaml"))[0]
    parsed = cid.parse_connection(sample.read_text(encoding="utf-8"))
    for key in ("id", "source", "relation", "target", "assertion_status"):
        assert parsed.get(key), (key, parsed)
    print(f"PASS: connection parser extracts the triple from {sample.name}")


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except AssertionError as exc:
                failures += 1
                print(f"FAIL: {name}: {exc}")
    if failures:
        raise SystemExit(1)
    print("ALL CLAIM-INTEGRITY (E4.3/E4.4/E4.5) TESTS PASS")
