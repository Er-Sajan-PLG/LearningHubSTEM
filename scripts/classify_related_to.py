#!/usr/bin/env python3
"""B1: Conservative related_to classification pipeline.

Generates candidate reclassifications as proposals (never auto-converts to
stronger semantics). Deterministic, evidence-required.

Rules (deterministic, no embeddings):
 - Only obvious type/domain patterns generate proposals.
 - Stronger relations (causes, requires, mathematically_requires, contradicts, explains)
   NEVER auto-proposed without evidence -> remain related_to.
 - Output goes to review queue (proposed/unreviewed), not canonical.
"""
from __future__ import annotations

import json
import pathlib
import collections

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONNECTIONS = ROOT / "connections"
CONTENT = ROOT / "content"


def load_entities():
    ents = {}
    for p in (ROOT / "content").rglob("*.md"):
        d = yaml.safe_load(p.read_text().split("---", 2)[1])
        if isinstance(d, dict) and d.get("id"):
            ents[d["id"]] = d
    return ents


def simple_heuristics(source_id, target_id, entities):
    s = entities.get(source_id, {})
    t = entities.get(target_id, {})
    s_type, t_type = s.get("type"), t.get("type")
    s_dom, t_dom = s.get("domain"), t.get("domain")
    s_name, t_name = (s.get("name") or "").lower(), (t.get("name") or "").lower()

    proposals = []

    # Obvious: quantity appears in law
    if s_type == "quantity" and t_type == "law":
        proposals.append(("appears_in_law", "quantity likely appears in law; verify law definition/equation"))
    if s_type == "concept" and t_type == "law" and "law" in s_name:
        proposals.append(("appears_in_law", "concept appears in law context"))

    # Measurement: quantity/concept -> unit
    if t_type == "unit" or "unit" in t_name:
        proposals.append(("has_unit", "target is a unit; relation may be has_unit/expressed_in"))
    if "measurement" in s_name and t_type == "quantity":
        proposals.append(("measures", "measurement entity likely measures quantity"))

    # Part_of pattern: e.g., nucleus part_of cell (but keep conservative -> propose part_of only if name contains)
    if s_type in ("concept", "phenomenon") and t_type in ("concept", "phenomenon"):
        if t_name in s_name or s_name in t_name:
            pass  # too weak, skip

    # Cross-domain: different domains -> candidate bridges/shared_mechanism_with (but only as proposal)
    if s_dom != t_dom and s_dom in ("physics", "chemistry", "biology", "earth-space"):
        # Only propose bridges if both are concepts/phenomena (not generic related_to dumping)
        if s_type in ("concept", "phenomenon", "quantity") and t_type in ("concept", "phenomenon", "quantity"):
            proposals.append(("bridges", f"cross-domain {s_dom}↔{t_dom}; possible bridge/shared mechanism"))
            # Do not also propose shared_mechanism_with automatically; reviewer decides

    # Engineering: physics concept related_to engineering
    if s_dom == "physics" and t_dom == "engineering":
        proposals.append(("applied_to", "physics principle possibly applied in engineering context"))

    # Analogy candidate: both quantities with similar flavor (e.g., current/pressure)
    analog_pairs = {
        ("current", "pressure"),
        ("voltage", "pressure"),
        ("electric current", "fluid flow"),
        ("thermal", "electrical"),
    }
    for a, b in analog_pairs:
        if a in s_name and b in t_name or a in t_name and b in s_name:
            proposals.append(("analogous_to", f"lexical analogy candidate: {a} ↔ {b}; needs mapping justification"))

    return proposals


def main():
    entities = load_entities()
    proposals = []
    remain = []
    for p in sorted(CONNECTIONS.glob("*.yaml")):
        d = yaml.safe_load(p.read_text())
        if d.get("relation") != "related_to":
            continue
        src, tgt = d.get("source"), d.get("target")
        cands = simple_heuristics(src, tgt, entities)
        if not cands:
            remain.append((d["id"], src, tgt))
            continue
        # Take first candidate (deterministic sorted)
        cands_sorted = sorted(cands)
        best_rel, reason = cands_sorted[0]
        proposals.append({
            "connection_id": d["id"],
            "source": src,
            "source_name": entities.get(src, {}).get("name"),
            "target": tgt,
            "target_name": entities.get(tgt, {}).get("name"),
            "current_relation": "related_to",
            "proposed_relation": best_rel,
            "reason": reason,
            "context": d.get("context"),
            "provenance": d.get("provenance"),
            "risk": "proposed/unreviewed; requires evidence and reviewer acceptance",
            "action": "review queue — do not auto-apply",
        })

    # Deterministic sort
    proposals.sort(key=lambda x: x["connection_id"])
    out_json = ROOT / "reports" / "related-to-classification-v0.2.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    # Dynamic count from actual connections
    total_related = len([p for p in CONNECTIONS.glob("*.yaml") if yaml.safe_load(p.read_text()).get("relation") == "related_to"])
    out_json.write_text(json.dumps({
        "total_related_to": total_related,
        "proposals": proposals,
        "proposal_count": len(proposals),
        "remain_related_to": len(remain),
        "remain_ids": [r[0] for r in remain],
        "note": "All proposals are type: proposed, review: unreviewed; similarity not used to establish stronger semantics"
    }, indent=2) + "\n", encoding="utf-8")

    out_md = ROOT / "reports" / "related-to-classification-v0.2.md"
    total_related = len([p for p in CONNECTIONS.glob("*.yaml") if yaml.safe_load(p.read_text()).get("relation") == "related_to"])
    out_md.write_text(
        f"""# related_to Classification — v0.2

Conservative pipeline (deterministic, no embedding-based auto-upgrade).

- Total `related_to`: {total_related}
- Proposals generated: {len(proposals)}
- Remain `related_to`: {len(remain)}

All proposals are `assertion.type: proposed, review: unreviewed` — **not canonical**.
Stronger relations (causes, requires, mathematically_requires, contradicts, explains) are never auto-applied.

## Proposal sample (first 20)

"""
        + "\n".join(
            f"- `{p['connection_id']}`: `{p['source']}` —{p['current_relation']}→ `{p['target']}` → **{p['proposed_relation']}** — {p['reason']}"
            for p in proposals[:20]
        )
        + f"""

Full list: `reports/related-to-classification-v0.2.json` ({len(proposals)} entries)

## Invariant

All proposals remain `proposed/unreviewed`. Ambiguous cases remain `related_to`.
"""
    )
    total_related = len([p for p in CONNECTIONS.glob("*.yaml") if yaml.safe_load(p.read_text()).get("relation") == "related_to"])
    print(f"OK: related_to {total_related} -> proposals {len(proposals)}, remain {len(remain)}")
    print(f"Wrote {out_json.relative_to(ROOT)} and {out_md.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
