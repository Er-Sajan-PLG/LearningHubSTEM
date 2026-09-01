#!/usr/bin/env python3
"""B2: Human-review queue — prioritized, reviewable."""
import json
import pathlib
from collections import Counter, defaultdict

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONNECTIONS = ROOT / "connections"
REPORT_IN = ROOT / "reports" / "related-to-classification-v0.2.json"
REPORT_OUT_JSON = ROOT / "reports" / "review-queue-v0.2.json"
REPORT_OUT_MD = ROOT / "reports" / "review-queue-v0.2.md"


def load_entities():
    ents = {}
    for p in (ROOT / "content").rglob("*.md"):
        d = yaml.safe_load(p.read_text().split("---", 2)[1])
        if d.get("id"):
            ents[d["id"]] = d
    return ents


def main():
    entities = load_entities()
    # Degree centrality
    degree = Counter()
    for p in CONNECTIONS.glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        degree[d["source"]] += 1
        degree[d["target"]] += 1

    data = json.loads(REPORT_IN.read_text())
    proposals = data["proposals"]

    scored = []
    for pr in proposals:
        src, tgt = pr["source"], pr["target"]
        # Score components
        centrality = (degree[src] + degree[tgt]) / 2
        # Domain significance: physics core higher
        s_dom = entities.get(src, {}).get("domain", "")
        t_dom = entities.get(tgt, {}).get("domain", "")
        domain_sig = 2 if "physics" in (s_dom, t_dom) else 1
        if s_dom != t_dom:
            domain_sig += 1  # cross-domain more valuable
        # Educational importance: if either is a law/phenomenon
        edu = 0
        for eid in (src, tgt):
            et = entities.get(eid, {}).get("type")
            if et == "law":
                edu += 2
            elif et in ("phenomenon", "model"):
                edu += 1.5
        # Prerequisite path: proposed bridges/shared机制 could improve graph
        prereq = 1 if pr["proposed_relation"] in ("bridges", "shared_mechanism_with", "appears_in_law") else 0.5

        score = centrality * 0.5 + domain_sig * 2 + edu * 1.5 + prereq

        scored.append((score, pr))

    scored.sort(key=lambda x: -x[0])
    queue = []
    for score, pr in scored:
        queue.append({
            **pr,
            "priority_score": round(score, 2),
            "review_action": "accept / reject / remain related_to",
            "required_evidence": "source citation or experimental derivation; do not mark canonical without reviewer",
        })

    REPORT_OUT_JSON.write_text(json.dumps({"queue": queue, "count": len(queue)}, indent=2) + "\n", encoding="utf-8")
    REPORT_OUT_MD.write_text(
        "# Review Queue — v0.2 (prioritized)\n\n"
        + f"Total proposals: {len(queue)}\n\n"
        + "Scoring: centrality + domain significance + educational importance + prerequisite value.\n"
        + "All remain `proposed/unreviewed` until human review.\n\n"
        + "| Rank | Connection | Proposed | Score | Source → Target | Reason | Action |\n"
        + "|------|------------|----------|-------|---------------|--------|--------|\n"
        + "\n".join(
            f"| {i+1} | {q['connection_id']} | {q['proposed_relation']} | {q['priority_score']} | {q['source_name']} → {q['target_name']} | {q['reason']} | {q['review_action']} |"
            for i, q in enumerate(queue[:30])
        )
        + "\n\nFull: `reports/review-queue-v0.2.json`\n"
    )
    print(f"OK: queue {len(queue)} written to {REPORT_OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
