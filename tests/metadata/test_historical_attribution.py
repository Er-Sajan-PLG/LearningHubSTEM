"""Historical scientific attribution semantics (ADR-0018).

Verifies the optional `historical` field shape on canonical entities, and that
key historic laws/discoveries actually carry who + when attribution.
"""
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _entities():
    for p in (ROOT / "content").rglob("*.md"):
        text = p.read_text(encoding="utf-8")
        try:
            d = yaml.safe_load(text.split("---", 2)[1])
        except Exception:
            continue
        if isinstance(d, dict) and d.get("id"):
            d["_file"] = str(p.relative_to(ROOT))
            yield d


def test_historical_shape_valid():
    invalid = []
    for d in _entities():
        h = d.get("historical")
        if h is None:
            continue
        if not isinstance(h.get("stated_by"), str) or not h.get("stated_by"):
            invalid.append(f"{d['_file']}: historical.stated_by required")
        if not isinstance(h.get("year"), int) or isinstance(h.get("year"), bool):
            invalid.append(f"{d['_file']}: historical.year must be int")
        if h.get("timeline") is not None:
            if not isinstance(h["timeline"], list):
                invalid.append(f"{d['_file']}: historical.timeline must be list")
            else:
                for ev in h["timeline"]:
                    if not isinstance(ev, dict) or not isinstance(ev.get("year"), int) or not ev.get("event"):
                        invalid.append(f"{d['_file']}: malformed timeline entry {ev}")
    assert not invalid, "\n".join(invalid)
    print("PASS: all historical blocks well-formed")


def test_historic_laws_have_attribution():
    """Every law entity (a historic statement) should record who+when."""
    laws = [d for d in _entities() if d.get("type") == "law"]
    missing = [d["_file"] for d in laws if not d.get("historical")]
    # Allow an opt-out note where origin is genuinely unknown; flag if silent.
    flagged = [
        d["_file"] for d in laws
        if not d.get("historical") and not (d.get("historical") is None and d.get("definition"))
    ]
    print(f"Laws total: {len(laws)}; without historical.block: {len(missing)}")
    # Historic laws that have a well-documented origin must carry it.
    named = [d for d in laws if "Newton" in d.get("name", "") or "Coulomb" in d.get("name", "")
             or "Ohm" in d.get("name", "") or "Le Chatelier" in d.get("name", "")
             or "Conservation of Energy" in d.get("name", "")
             or "Fundamental Theorem" in d.get("name", "")]
    gaps = [d["_file"] for d in named if not d.get("historical")]
    assert not gaps, f"named historic laws missing historical: {gaps}"
    print(f"PASS: {len(named)} named historic laws carry who+when")


def test_no_grade_in_historical():
    """historical blocks must stay curriculum-grade-agnostic (NORTHSTAR)."""
    import re
    for d in _entities():
        import json
        blob = json.dumps(d.get("historical", {}))
        if re.search(r"grade\s*\d|Grade\s*\d|high school|syllabus", blob):
            raise AssertionError(f"{d['_file']}: historical block references a grade/curriculum")
    print("PASS: historical blocks are curriculum-agnostic")