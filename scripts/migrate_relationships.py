#!/usr/bin/env python3
"""Migrate legacy entity.relationships[] to first-class connections/.

Guardrails:
 - Sequential opaque lhs:conn.NNNNNN (never reuse, idempotent)
 - confidence: null (no fabricated epistemic metadata)
 - assertion.type: proposed, review: unreviewed
 - asserted_by: unknown:legacy-relationship, generated_by: process:migration.relationships-v0.2
 - Backward compat: keep relationships[] in entities; connections/ is truth
 - Idempotent: running twice produces no duplicates (checks existing connections/)

Usage: python3 scripts/migrate_relationships.py [--dry-run]
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
CONNECTIONS = ROOT / "connections"


def entity_domain_subdomain(path: Path) -> tuple[str, str]:
    # Infer from path: content/<domain>/<subdomain>/file.md
    parts = path.relative_to(ROOT).parts
    try:
        ci = parts.index("content")
        dom = parts[ci + 1] if len(parts) > ci + 1 else ""
        sub = parts[ci + 2] if len(parts) > ci + 2 else ""
        return dom, sub
    except ValueError:
        return "", ""


def next_conn_id(existing: set[str]) -> int:
    max_n = 0
    for cid in existing:
        if cid.startswith("lhs:conn."):
            try:
                n = int(cid.split(".")[-1])
                max_n = max(max_n, n)
            except ValueError:
                continue
    return max_n + 1


def main() -> int:
    dry = "--dry-run" in sys.argv
    # Load existing connections for idempotence
    existing_ids: set[str] = set()
    existing_pairs: set[tuple[str, str, str]] = set()
    if CONNECTIONS.exists():
        for p in CONNECTIONS.rglob("*.yaml"):
            try:
                data = yaml.safe_load(p.read_text(encoding="utf-8"))
                if isinstance(data, dict) and data.get("id"):
                    existing_ids.add(data["id"])
                    existing_pairs.add((data.get("source", ""), data.get("relation", ""), data.get("target", "")))
            except Exception:
                pass

    next_n = next_conn_id(existing_ids)
    created = 0
    skipped = 0

    for path in sorted(CONTENT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        data = yaml.safe_load(parts[1])
        if not isinstance(data, dict):
            continue
        src_id = data.get("id")
        domain, subdomain = entity_domain_subdomain(path)
        for rel in data.get("relationships", []) or []:
            if not isinstance(rel, dict):
                continue
            rtype = rel.get("type")
            target = rel.get("target")
            if not rtype or not target or not src_id:
                continue
            key = (src_id, rtype, target)
            if key in existing_pairs:
                skipped += 1
                continue
            cid = f"lhs:conn.{next_n:06d}"
            # Guard against reuse
            while cid in existing_ids:
                next_n += 1
                cid = f"lhs:conn.{next_n:06d}"
            existing_ids.add(cid)
            existing_pairs.add(key)

            conn = {
                "id": cid,
                "type": "connection",
                "source": src_id,
                "relation": rtype,
                "target": target,
                "assertion": {
                    "status": "active",
                    "type": "proposed",
                    "review": {"status": "unreviewed"},
                    "confidence": None,
                    "confidence_basis": None,
                },
                "context": {
                    "domain": domain,
                    "subdomain": subdomain,
                    "regime": ["classical"],
                    "scale": "macroscopic",
                    "assumptions": [],
                },
                "evidence": [],
                "provenance": {
                    "asserted_by": {"type": "unknown", "id": "unknown:legacy-relationship"},
                    "generated_by": {"type": "process", "id": "process:migration.relationships-v0.2"},
                    "method": {"type": "migration"},
                },
            }
            # Add note as description in evidence if present
            if rel.get("note"):
                conn["evidence"].append({
                    "type": "other",
                    "description": rel["note"],
                })

            dest = CONNECTIONS / f"{cid}.yaml"
            if dry:
                print(f"DRY: would create {dest.relative_to(ROOT)}: {src_id} --{rtype}--> {target}")
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(yaml.safe_dump(conn, sort_keys=False, allow_unicode=True), encoding="utf-8")
                print(f"created {dest.relative_to(ROOT)}: {src_id} --{rtype}--> {target}")
            next_n += 1
            created += 1

    action = "would create" if dry else "created"
    print(f"Done: {action} {created}, skipped {skipped} (existing).")
    print("Guardrail: confidence=null, type=proposed, asserted_by=unknown:legacy-relationship")
    return 0


if __name__ == "__main__":
    sys.exit(main())
