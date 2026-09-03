#!/usr/bin/env python3
"""Deprecate materialized inverse-duplicate connections (ADR-0012/ADR-0021).

ADR-0012: inverse edges are DERIVED (computed from the registry), never stored
canonically. Eight connections materialized the inverse of another active
connection (e.g. `A generalizes B` AND `B special_case_of A`). This repair
deprecates the higher-ID member of each duplicate pair and points its
`lifecycle.replaced_by` at the survivor — connection IDs are immutable and
never reused, so the deprecated record stays in place, honestly marked.

Idempotent. Run scripts/validate.py and scripts/sync_relationships.py after:
deprecated connections drop out of the inline projection.
"""
from __future__ import annotations

import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONNECTIONS = ROOT / "connections"


def main() -> int:
    conns = []
    for p in sorted(CONNECTIONS.glob("*.yaml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        d["_path"] = p
        conns.append(d)

    reg = yaml.safe_load((ROOT / "schema" / "relation-registry.yaml").read_text())["relations"]
    active = [c for c in conns if c.get("assertion", {}).get("status") == "active"]

    # index over ALL connections (any status) so already-deprecated duplicates can
    # still resolve their survivor on re-runs (normalization pass below).
    index: dict[tuple[str, str], set[str]] = {}
    for c in conns:
        index.setdefault((c["source"], c["relation"]), set()).add(c["target"])

    to_deprecate: dict[str, str] = {}  # id -> survivor id
    for c in active:
        rel = c["relation"]
        inv = (reg.get(rel) or {}).get("inverse")
        if not inv:
            continue
        if c["source"] in index.get((c["target"], inv), set()):
            survivor = next(
                x["id"] for x in conns
                if x["source"] == c["target"] and x["relation"] == inv and x["target"] == c["source"]
            )
            # keep the numerically lower ID; deprecate the other direction
            loser, winner = sorted([c["id"], survivor])
            if loser != winner:
                to_deprecate[loser] = winner

    changed = 0
    for c in conns:
        if c["id"] in to_deprecate and c["assertion"]["status"] == "active":
            c["assertion"]["status"] = "deprecated"
            c["lifecycle"] = {
                "reason": "materialized inverse duplicate (ADR-0012: inverses are derived, "
                          "never stored canonically; repaired ADR-0021/plan v2 E2.1)",
                "replaced_by": to_deprecate[c["id"]],
            }
            text = c["_path"].read_text(encoding="utf-8")
            text = text.replace(
                "assertion:\n  status: active\n",
                "assertion:\n  status: deprecated\n",
                1,
            )
            if "\nlifecycle:" in text:
                # replace the existing null lifecycle block
                text = text.replace(
                    "lifecycle:\n  reason: null\n  replaced_by: null\n",
                    f"lifecycle:\n  reason: {c['lifecycle']['reason']}\n  replaced_by: {to_deprecate[c['id']]}\n",
                    1,
                )
            elif "\nvalidity: null\n" in text:
                text = text.replace(
                    "validity: null\n",
                    f"lifecycle:\n  reason: {c['lifecycle']['reason']}\n  replaced_by: {to_deprecate[c['id']]}\nvalidity: null\n",
                    1,
                )
            else:
                # old-format file without lifecycle/validity fields: append the block
                if not text.endswith("\n"):
                    text += "\n"
                text += (f"lifecycle:\n  reason: {c['lifecycle']['reason']}\n"
                         f"  replaced_by: {to_deprecate[c['id']]}\n")
            c["_path"].write_text(text, encoding="utf-8")
            changed += 1
            print(f"deprecated {c['id']} (inverse duplicate of {to_deprecate[c['id']]})")

    # Normalization pass: any connection already deprecated for inverse duplication
    # (e.g. by an older run against old-format files) must carry its lifecycle block.
    for c in conns:
        if c.get("assertion", {}).get("status") == "deprecated" and not c.get("lifecycle"):
            if c["id"] not in to_deprecate:
                continue
            text = c["_path"].read_text(encoding="utf-8")
            if not text.endswith("\n"):
                text += "\n"
            import json as _json
            reason = ("materialized inverse duplicate (ADR-0012: inverses are derived, "
                      "never stored canonically; repaired ADR-0021/plan v2 E2.1)")
            text += (f"lifecycle:\n  reason: {_json.dumps(reason)}\n"
                     f"  replaced_by: {to_deprecate[c['id']]}\n")
            c["_path"].write_text(text, encoding="utf-8")
            changed += 1
            print(f"normalized lifecycle pointer on {c['id']}")

    print(f"deprecated {changed} materialized-inverse duplicate(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
