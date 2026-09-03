#!/usr/bin/env python3
"""D13: Review-aware exports — all/reviewed/canonical/proposed/rejected/trusted.

Uses graph_policy.should_include_connection as single source.
Preserves backward compatibility of exports/knowledge.json (all active).
"""
import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXPORT_BASE = ROOT / "exports" / "knowledge.json"

from graph_policy import should_include_connection  # type: ignore


def main():
    import yaml as _yaml

    conns = [yaml.safe_load(p.read_text()) for p in sorted((ROOT / "connections").glob("*.yaml"))]
    base = json.loads(EXPORT_BASE.read_text()) if EXPORT_BASE.exists() else {}
    for policy in ["all", "reviewed", "canonical", "trusted", "proposed", "rejected"]:
        if policy == "proposed":
            filtered = [c for c in conns if c["assertion"]["review"]["status"] == "unreviewed" and c["assertion"]["type"] == "proposed"]
        elif policy == "rejected":
            filtered = [c for c in conns if c["assertion"]["status"] == "rejected" or c["assertion"]["review"]["status"] == "rejected"]
        else:
            filtered = [c for c in conns if should_include_connection(c, policy)]

        out = {
            "export_version": base.get("export_version", "0.1"),
            "schema_version": base.get("schema_version", "0.2"),
            "content_hash": base.get("content_hash", "sha256:unknown"),
            "policy": policy,
            "count": len(filtered),
            "connections": sorted(filtered, key=lambda x: x["id"]),
        }
        path = ROOT / f"exports/knowledge.{policy}.json"
        path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
        print(f"OK: {policy} -> {len(filtered)} connections -> {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
