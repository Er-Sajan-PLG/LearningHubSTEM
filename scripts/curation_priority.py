#!/usr/bin/env python3
"""E2: Curation priority index — composite, deterministic, not raw PageRank."""
import json, pathlib, collections
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load_entities():
    ents={}
    for p in (ROOT/"content").rglob("*.md"):
        d=yaml.safe_load(p.read_text().split("---",2)[1])
        if d.get("id"): ents[d["id"]]=d
    return ents

def main():
    ents=load_entities()
    conns=[yaml.safe_load(p.read_text()) for p in sorted((ROOT/"connections").glob("*.yaml"))]
    registry=yaml.safe_load((ROOT/"schema/relation-registry.yaml").read_text())["relations"]
    # Centrality from graph_analysis derived
    ext_path=ROOT/"exports/knowledge.extended.json"
    centrality={}
    if ext_path.exists():
        ext=json.loads(ext_path.read_text())
        centrality=ext["derived"]["centrality"]["all"]
    # Family reliability (higher = more reliable for canonical)
    family_reliability={"structural":5, "hierarchical":5, "dependency":4, "derivation":4, "measurement":4, "cross_domain":3, "model":3, "analogy":2, "associative":1, "causal":2, "explanatory":2, "conflict":1}
    # Domain coverage weight (ensure physics+chemistry+biology balanced)
    domain_counts=collections.Counter(c.get("context",{}).get("domain", ents.get(c["source"],{}).get("domain","unknown")) for c in conns if c["assertion"]["review"]["status"]=="canonical")
    # Score each unreviewed
    scored=[]
    for c in conns:
        if c["assertion"]["review"]["status"]!="unreviewed":
            continue
        fam=registry.get(c["relation"],{}).get("family","unknown")
        rel_rel=family_reliability.get(fam,2)
        # Educational relevance: dependency/structural higher
        edu=rel_rel
        # Evidence availability: has evidence already scores higher
        ev_avail=2 if c.get("evidence") else 1
        # Graph utility: centrality avg
        src,cen_tgt=centrality.get(c["source"],{}).get("pagerank",0), centrality.get(c["target"],{}).get("pagerank",0)
        cent=(src+cen_tgt)/2*1000  # scale
        # Dependency relevance: dependency family bonus
        dep_bonus=2 if fam=="dependency" else 0
        # Domain coverage: penalize over-represented domain
        dom=c.get("context",{}).get("domain","physics")
        dom_penalty=domain_counts.get(dom,0)*0.1
        # Entity importance: degree
        score= edu*2 + ev_avail*1.5 + cent*0.5 + dep_bonus*1.5 - dom_penalty
        # Round for determinism
        scored.append((round(score,3), c))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    # Produce reports
    out_json=ROOT/"reports/curation-priority-v0.2.json"
    payload=[{"id":c["id"],"relation":c["relation"],"family":registry.get(c["relation"],{}).get("family"),"source":c["source"],"target":c["target"],"score":s,"review":c["assertion"]["review"]["status"]} for s,c in scored]
    out_json.write_text(json.dumps({"total_unreviewed":len(scored),"priority":payload}, indent=2)+"\n")
    out_md=ROOT/"reports/curation-priority-v0.2.md"
    lines="\n".join(f"| {i+1} | {c['id']} | {c['relation']} | {s} | {c['source']}→{c['target']} |" for i,(s,c) in enumerate(scored[:30]))
    out_md.write_text(f"# Curation Priority — v0.2\n\nComposite priority (educational+reliability+evidence+centrality+dependency+domain). Not raw PageRank. Does not modify confidence/review.\n\n- Total unreviewed: {len(scored)}\n\n| Rank | ID | Relation | Score | Source→Target |\n|------|----|----------|-------|---------------|\n{lines}\n")
    print(f"OK: priority {len(scored)} unreviewed")
    return 0
if __name__=="__main__":
    import sys; sys.exit(main())
