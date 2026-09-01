#!/usr/bin/env python3
"""Migrate urgent metadata additions (additive, idempotent, no fabrication)."""
import pathlib, yaml
from datetime import datetime, timezone
import os

ROOT = pathlib.Path(__file__).resolve().parent.parent

def file_mtime_iso(p):
    ts = os.path.getmtime(p)
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

def migrate_connections():
    cnt=0
    for p in sorted((ROOT/"connections").glob("*.yaml")):
        d=yaml.safe_load(p.read_text())
        changed=False
        # polarity — safe structural default (Gate 12)
        if "polarity" not in d.get("assertion", {}):
            d["assertion"]["polarity"] = "positive"
            changed=True
        # timestamps — DO NOT fabricate from file mtime (Gate 1,13). Leave absent/null unless genuinely known.
        # For urgent migration, ensure fields exist as null if missing, not file mtime.
        for field in ("created_at", "updated_at"):
            if field not in d:
                d[field] = None
                changed=True
        # validity — optional, keep null if not known (Gate 5)
        if "validity" not in d:
            d["validity"] = None
            changed=True
        # lifecycle
        if "lifecycle" not in d:
            d["lifecycle"] = None
            changed=True
        # context qualifiers — safe structural default
        if "context" in d and isinstance(d["context"], dict) and "qualifiers" not in d["context"]:
            d["context"]["qualifiers"] = []
            changed=True
        # evidence stance — DO NOT default to supports for migrated (Gate 2,13). Omit stance (= not established)
        for ev in d.get("evidence", []) or []:
            # Only ensure locator_struct exists; stance remains absent if not explicitly known
            if "locator_struct" not in ev:
                ev["locator_struct"] = None
                changed=True
        # rights
        if "rights" not in d:
            d["rights"] = None
            changed=True
        if changed:
            p.write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True))
            cnt+=1
    print(f"migrated connections: {cnt}")

def migrate_sources():
    cnt=0
    for p in sorted((ROOT/"sources").glob("*.yaml")):
        d=yaml.safe_load(p.read_text())
        changed=False
        for field in ["title","publisher","journal","volume","doi","url","isbn","edition","language","source_role","accessed_at","publication_date"]:
            if field not in d:
                d[field]=None
                changed=True
        if "authors" not in d:
            d["authors"]=[]
            changed=True
        if "year" not in d:
            d["year"]=None
            changed=True
        if "rights" not in d:
            d["rights"]=None
            changed=True
        if changed:
            p.write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True))
            cnt+=1
    print(f"migrated sources: {cnt}")

def migrate_entities():
    cnt=0
    for p in sorted((ROOT/"content").rglob("*.md")):
        text=p.read_text()
        if not text.startswith("---"): continue
        front=yaml.safe_load(text.split("---",2)[1])
        changed=False
        # timestamps — DO NOT fabricate from file mtime (Gate 1). Leave null if unknown.
        if "updated_at" not in front:
            front["updated_at"]=None
            changed=True
        if "version" not in front:
            front["version"]=1
            changed=True
        if "external_ids" not in front:
            front["external_ids"]={}
            changed=True
        if "rights" not in front:
            front["rights"]=None
            changed=True
        if changed:
            body=text.split("---",2)[2]
            new_front=yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
            p.write_text(f"---\n{new_front}---{body}")
            cnt+=1
    print(f"migrated entities: {cnt}")

if __name__=="__main__":
    migrate_connections()
    migrate_sources()
    migrate_entities()
    print("OK urgent migration idempotent")
