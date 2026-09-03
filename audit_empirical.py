#!/usr/bin/env python3
"""Empirical audit of the STEMMA kernel: cycles, duplicate triples, dangling refs,
domain/range violations, projection drift, phenomenon/model usage."""
import json
import pathlib
import yaml
from collections import defaultdict, Counter

ROOT = pathlib.Path(__file__).resolve().parent
CONTENT = ROOT / "content"
CONNECTIONS = ROOT / "connections"
REGISTRY = ROOT / "schema" / "relation-registry.yaml"
EXPORT = ROOT / "exports" / "knowledge.json"

def load_entities():
    entities = {}
    for p in sorted(CONTENT.rglob("*.md")):
        text = p.read_text(encoding="utf-8")
        if not text.startswith("---"): continue
        fm = text.split("---", 2)[1]
        data = yaml.safe_load(fm)
        if isinstance(data, dict) and data.get("id"):
            entities[data["id"]] = data
    return entities

def load_connections():
    conns = []
    for p in sorted(CONNECTIONS.glob("*.yaml")):
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("id"):
            conns.append(data)
    return conns

def load_registry():
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    return data.get("relations", {})

def main():
    entities = load_entities()
    conns = load_connections()
    registry = load_registry()

    print(f"=== EMPIRICAL AUDIT ===")
    print(f"Entities: {len(entities)}")
    print(f"Connections: {len(conns)}")
    print(f"Registry relations: {len(registry)}")

    # 1. Cycles in prerequisite edges (requires, prerequisite_of, mathematically_requires, logically_requires, depends_on)
    dep_rels = {"requires", "prerequisite_of", "mathematically_requires", "logically_requires", "depends_on"}
    dep_edges = [(c["source"], c["target"]) for c in conns if c["relation"] in dep_rels]
    
    # Simple cycle detection (Tarjan)
    adj = defaultdict(list)
    for s, t in dep_edges:
        adj[s].append(t)
    
    def find_cycles():
        visited = set()
        rec_stack = set()
        path = []
        cycles = []
        def dfs(u):
            visited.add(u)
            rec_stack.add(u)
            path.append(u)
            for v in adj.get(u, []):
                if v not in visited:
                    dfs(v)
                elif v in rec_stack:
                    # cycle found
                    idx = path.index(v)
                    cycles.append(path[idx:] + [v])
            rec_stack.remove(u)
            path.pop()
        for u in adj:
            if u not in visited:
                dfs(u)
        return cycles
    
    cycles = find_cycles()
    print(f"\n1. PREREQUISITE CYCLES: {len(cycles)}")
    for c in cycles[:10]:
        print(f"   {' -> '.join(c)}")

    # 2. Duplicate (source, relation, target) triples
    by_triple = defaultdict(list)
    for c in conns:
        by_triple[(c["source"], c["relation"], c["target"])].append(c["id"])
    dupes = {t: ids for t, ids in by_triple.items() if len(ids) > 1}
    print(f"\n2. DUPLICATE TRIPLES: {len(dupes)}")
    for t, ids in list(dupes.items())[:10]:
        print(f"   {t[0]} --{t[1]}--> {t[2]}  ({len(ids)} times: {ids[:5]}{'...' if len(ids)>5 else ''})")

    # 3. Dangling references (connections pointing to non-existent entities)
    dangling = []
    for c in conns:
        if c["source"] not in entities:
            dangling.append(("source", c["id"], c["source"]))
        if c["target"] not in entities:
            dangling.append(("target", c["id"], c["target"]))
    print(f"\n3. DANGLING REFS: {len(dangling)}")
    for kind, cid, ref in dangling[:20]:
        print(f"   {cid}: {kind} -> {ref} (missing)")

    # 4. Relations in content but not in registry
    inline_rels = set()
    for e in entities.values():
        for rel in e.get("relationships", []) or []:
            inline_rels.add(rel.get("type"))
    unregistered = inline_rels - set(registry.keys())
    print(f"\n4. UNREGISTERED RELATIONS (in inline): {len(unregistered)}")
    for r in sorted(unregistered):
        print(f"   {r}")

    # 5. Relations in registry but never used in canonical connections
    used_rels = {c["relation"] for c in conns}
    unused = set(registry.keys()) - used_rels
    print(f"\n5. UNUSED REGISTRY RELATIONS: {len(unused)}")
    for r in sorted(unused):
        print(f"   {r}")

    # 6. Domain/range violations per registry
    violations = []
    for c in conns:
        rel = c.get("relation")
        info = registry.get(rel)
        if not info: continue
        src_type = entities.get(c["source"], {}).get("type")
        tgt_type = entities.get(c["target"], {}).get("type")
        domain = info.get("domain", [])
        range_ = info.get("range", [])
        if src_type and domain and src_type not in domain:
            violations.append(f"{c['id']}: relation '{rel}' domain {domain} excludes source type '{src_type}'")
        if tgt_type and range_ and tgt_type not in range_:
            violations.append(f"{c['id']}: relation '{rel}' range {range_} excludes target type '{tgt_type}'")
    print(f"\n6. DOMAIN/RANGE VIOLATIONS: {len(violations)}")
    for v in violations[:20]:
        print(f"   {v}")

    # 7. Projection drift: inline relationships[] vs canonical connections
    # For each entity, collect its inline relationships and compare to canonical connections
    drift = 0
    for eid, e in entities.items():
        inline = set()
        for rel in e.get("relationships", []) or []:
            inline.add((rel.get("type"), rel.get("target")))
        canonical = set()
        for c in conns:
            if c["source"] == eid:
                canonical.add((c["relation"], c["target"]))
        if inline != canonical:
            drift += 1
            missing_in_canonical = inline - canonical
            extra_in_canonical = canonical - inline
            if missing_in_canonical:
                print(f"   DRIFT {eid}: inline has {len(missing_in_canonical)} not in canonical: {missing_in_canonical}")
            if extra_in_canonical:
                print(f"   DRIFT {eid}: canonical has {len(extra_in_canonical)} not in inline: {extra_in_canonical}")
    print(f"\n7. PROJECTION DRIFT (inline vs canonical): {drift} entities")

    # 8. Phenomenon/model usage scan (types in registry but not in concept type enum)
    entity_types = Counter(e.get("type") for e in entities.values())
    print(f"\n8. ENTITY TYPES: {dict(entity_types)}")
    
    # Check which registry domain/range types are NOT in concept.type enum
    concept_types = {"concept", "quantity", "unit", "law", "equation", "misconception"}
    reg_types = set()
    for info in registry.values():
        reg_types.update(info.get("domain", []))
        reg_types.update(info.get("range", []))
    extra_reg_types = reg_types - concept_types
    print(f"\n9. REGISTRY TYPES NOT IN CONCEPT ENUM: {sorted(extra_reg_types)}")
    for t in sorted(extra_reg_types):
        rels_using = [r for r, info in registry.items() if t in info.get("domain", []) or t in info.get("range", [])]
        print(f"   {t}: used by {len(rels_using)} relations (e.g. {rels_using[:5]})")

    # 10. Self-loops
    self_loops = [c["id"] for c in conns if c["source"] == c["target"]]
    print(f"\n10. SELF-LOOPS: {len(self_loops)}")
    for cid in self_loops[:10]:
        print(f"   {cid}")

    # 11. Export contract check
    if EXPORT.exists():
        exp = json.loads(EXPORT.read_text())
        print(f"\n11. EXPORT CONTRACT:")
        print(f"   export_version: {exp.get('export_version')}")
        print(f"   schema_version: {exp.get('schema_version')}")
        print(f"   entity_count: {exp.get('entity_count')}")
        print(f"   connection_count: {exp.get('connection_count')}")
        print(f"   source_count: {exp.get('source_count')}")
        # Check for kernel version / content hash
        if "kernel_version" in exp or "content_hash" in exp:
            print(f"   HAS kernel_version/content_hash")
        else:
            print(f"   MISSING kernel_version/content_hash (audit finding)")

    print(f"\n=== AUDIT COMPLETE ===")

if __name__ == "__main__":
    main()
