#!/usr/bin/env python3
"""Sync inline relationships[] from canonical connections/ (plan v2 E1.2, ADR-0020).

ADR-0011 made `connections/` the single source of truth for relationships and
demoted `entity.relationships[]` to a compatibility projection. This script is
the missing mechanization (audit F1): it REGENERATES the inline block of every
entity from the canonical connections so the two can never meaningfully drift.

Projection rule (deterministic):
  entity.relationships := [ {type: c.relation, target: c.target}
                            for active connections c with c.source == entity.id ],
  sorted by (type, target). Notes/qualifiers do not exist on connections and
  are not projected.

The canonical graph is NEVER modified. Editing the inline block by hand is
pointless: scripts/validate.py fails when it differs from this projection
(run this script to fix). When the export contract bumps to v1.x (gate G-A),
the inline block is removed from the schema and the export entirely.

Idempotent: running twice changes nothing.
"""
from __future__ import annotations

import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
CONNECTIONS = ROOT / "connections"


def load_projection() -> dict[str, list[dict]]:
    proj: dict[str, list[dict]] = {}
    for p in sorted(CONNECTIONS.glob("*.yaml")):
        c = yaml.safe_load(p.read_text(encoding="utf-8"))
        if c.get("assertion", {}).get("status") != "active":
            continue
        proj.setdefault(c["source"], []).append(
            {"type": c["relation"], "target": c["target"]}
        )
    for edges in proj.values():
        edges.sort(key=lambda r: (r["type"], r["target"]))
    return proj


def items_text(edges: list[dict]) -> str:
    """Render the list items of a top-level relationships block (indent 0)."""
    if not edges:
        return "  []\n"
    return yaml.safe_dump(
        edges, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100,
    )


def replace_block(text: str, edges: list[dict]) -> tuple[str, bool]:
    """Replace (or insert) the top-level `relationships:` block in frontmatter."""
    parts = text.split("---", 2)
    fm = parts[1]
    lines = fm.splitlines(keepends=True)
    start = end = None
    for i, line in enumerate(lines):
        if line.startswith("relationships:"):
            start = i
            end = i + 1
            while end < len(lines):
                line = lines[end]
                if line.startswith(" ") or line.startswith("-"):
                    end += 1
                elif line.strip() == "":
                    # blank continues the block only if the next non-blank line is indented
                    j = end + 1
                    while j < len(lines) and lines[j].strip() == "":
                        j += 1
                    if j < len(lines) and (lines[j].startswith(" ") or lines[j].startswith("-")):
                        end = j
                        continue
                    break
                else:
                    break
            break
    new_items = items_text(edges)
    if start is None:
        # no existing block: insert `relationships:` + items before the frontmatter close
        insert_at = len(lines)
        while insert_at > 0 and lines[insert_at - 1].strip() == "":
            insert_at -= 1
        lines.insert(insert_at, "relationships:\n" + new_items)
        parts[1] = "".join(lines)
        return "---".join(parts), True
    # keep the `relationships:` key line, replace its items
    if edges:
        lines[start + 1:end] = [new_items]
    else:
        lines[start:end] = ["relationships: []\n"]
    parts[1] = "".join(lines)
    return "---".join(parts), True


def main() -> int:
    proj = load_projection()
    changed = 0
    checked = 0
    for path in sorted(CONTENT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        entity = yaml.safe_load(text.split("---", 2)[1])
        eid = entity.get("id")
        expected = proj.get(eid, [])
        checked += 1
        current = [
            {"type": r["type"], **({"note": r["note"]} if r.get("note") is not None else {}), "target": r["target"]}
            if False else {"type": r["type"], "target": r["target"]}
            for r in (entity.get("relationships") or [])
        ]
        current_sorted = sorted(current, key=lambda r: (r["type"], r["target"]))
        if current_sorted != expected:
            new_text, _ = replace_block(text, expected)
            # sanity: reparses and equals expectation
            reparsed = yaml.safe_load(new_text.split("---", 2)[1])
            got = sorted(
                ({"type": r["type"], "target": r["target"]} for r in (reparsed.get("relationships") or [])),
                key=lambda r: (r["type"], r["target"]),
            )
            assert got == expected, f"{path}: sync produced wrong projection for {eid}"
            path.write_text(new_text, encoding="utf-8")
            changed += 1
            if changed <= 8:
                added = [e for e in expected if e not in current_sorted]
                removed = [e for e in current_sorted if e not in expected]
                print(f"{path.relative_to(ROOT)}: {eid} synced (+{len(added)} -{len(removed)})"
                      + (f" e.g. +{added[:2]}" if added else ""))
    print(f"checked {checked} entities; synced {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
