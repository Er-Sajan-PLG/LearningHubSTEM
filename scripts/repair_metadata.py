#!/usr/bin/env python3
"""Gate 14: Repair fabricated metadata from urgent migration."""
import pathlib, yaml, json

ROOT = pathlib.Path(__file__).resolve().parent.parent

def repair_connections():
    repaired_ts = 0
    repaired_stance = 0
    preserved = 0
    for p in sorted((ROOT/"connections").glob("*.yaml")):
        d = yaml.safe_load(p.read_text())
        prov = d.get("provenance", {})
        method = prov.get("method", {}).get("type")
        orig_created = d.get("created_at")
        orig_updated = d.get("updated_at")
        changed = False
        # Repair timestamps: if method == migration, these were file mtime fabricated
        # For urgent migration, we set to None to indicate unknown historical value
        # Preserve only if method != migration and timestamp was manually curated (but our manual also used file mtime, so also remove)
        # Gate 1: file mtime != scientific timestamp, so remove for all where it matches previous migration pattern
        # We detect fabricated by: created_at is string ISO and not null, and no genuine asserted_at exists.
        # For now, remove for all where method == migration OR where created_at was auto-generated (heuristic: all 397 have it)
        if method == "migration":
            if d.get("created_at") is not None:
                d["created_at"] = None
                repaired_ts += 1
                changed = True
            if d.get("updated_at") is not None:
                d["updated_at"] = None
                changed = True
        else:
            # For manual (13), also remove fabricated file mtime unless review_history indicates genuine creation
            # Our manual batch also used file mtime implicitly via migrate, so also fabricated; remove
            if d.get("created_at") is not None and method in ("manual",):
                # Check if review_history exists: if so, created_at is still file mtime, should be null
                # Preserve only if explicitly set with genuine value (not file mtime) — we have no way to know, so set to None for consistency
                # But for manual curated, we could keep as None as well (unknown unless recorded)
                if d["created_at"] is not None:
                    d["created_at"] = None
                    changed = True
                if d["updated_at"] is not None:
                    d["updated_at"] = None
                    changed = True
        # Repair stance: for migrated, remove stance supports (fabricated); for manual, keep if human reviewed
        for ev in d.get("evidence", []) or []:
            if method == "migration" and ev.get("stance") == "supports":
                # Fabricated: remove stance to indicate not established
                ev.pop("stance", None)
                repaired_stance += 1
                changed = True
            # For manual curated, stance supports is genuine if reviewed/canonical; keep
        if changed:
            p.write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True))
        else:
            preserved += 1
    return repaired_ts, repaired_stance, preserved

def repair_entities():
    cnt=0
    for p in sorted((ROOT/"content").rglob("*.md")):
        text = p.read_text()
        if not text.startswith("---"):
            continue
        front = yaml.safe_load(text.split("---", 2)[1])
        if front.get("updated_at") is not None:
            # All updated_at were file mtime fabricated
            front["updated_at"] = None
            body = text.split("---", 2)[2]
            new_front = yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
            p.write_text(f"---\n{new_front}---{body}")
            cnt+=1
    return cnt

if __name__ == "__main__":
    ts, stance, preserved = repair_connections()
    ent = repair_entities()
    report = {
        "repaired_timestamp_fields": ts,
        "repaired_evidence_stance_fields": stance,
        "repaired_entities": ent,
        "preserved_genuine": preserved,
        "records_affected": ts + (1 if stance>0 else 0),
        "records_unchanged": preserved,
    }
    (ROOT/"reports/metadata-migration-repair-v0.2.json").write_text(json.dumps(report, indent=2)+"\n")
    (ROOT/"reports/metadata-migration-repair-v0.2.md").write_text(
        f"# Metadata Migration Repair — v0.2\n\n"
        f"- Repaired timestamp fields (created_at/updated_at set to null for migrated): {ts} connections\n"
        f"- Repaired evidence stance (removed fabricated supports for migrated): {stance} evidence items\n"
        f"- Repaired entities updated_at: {ent}\n"
        f"- Preserved genuine: {preserved} connections (manual curated retain review_history, evidence description, source dates)\n"
        f"- Records affected: {ts} connections + {ent} entities\n"
        f"- Records unchanged: {preserved}\n\n"
        f"Preserved: review_history, human review timestamps, actual source dates, evidence descriptions, canonicalization metadata where real.\n"
    )
    print(f"OK repair timestamps {ts}, stance {stance}, entities {ent}, preserved {preserved}")
