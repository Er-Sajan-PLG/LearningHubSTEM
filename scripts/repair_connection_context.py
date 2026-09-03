#!/usr/bin/env python3
"""Repair connection context fields (plan v2 E2.3 + E6.2, ADR-0021).

Two honest-data repairs over connections/*.yaml, both surgical (line-level,
no whole-file YAML rewrite — keeps diffs reviewable):

  1. `context.domain: math` -> `mathematics` (audit F3/F11: connections used a
     domain name that contradicts schema/vocabularies/domains.yaml and every
     entity's `domain:` field).
  2. Regime de-fabrication (audit F9): connections produced by the v0.2
     migration carried boilerplate `context.regime: [classical]` — epistemic
     context stamped by a script, not by judgment. Migration-method connections
     get `regime: []` (honestly empty). Human-curated connections keep their
     declared regimes.

Idempotent. Run scripts/validate.py afterwards; the vocabulary gate enforces
the repaired state.
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONNECTIONS = ROOT / "connections"

REGIME_BLOCK = re.compile(r"(?m)^  regime:\n((?:  - .*\n)+)")


def surgical_edit(path: pathlib.Path, text: str) -> tuple[str, list[str]]:
    data = yaml.safe_load(text)
    notes: list[str] = []
    ctx = data.get("context") or {}

    # 1. domain naming
    if ctx.get("domain") == "math":
        text = text.replace("  domain: math\n", "  domain: mathematics\n")
        notes.append("domain math->mathematics")

    # 2. regime de-fabrication (migration-method connections only)
    method = (data.get("provenance") or {}).get("method", {}).get("type")
    if method == "migration" and ctx.get("regime"):
        new_text, n = REGIME_BLOCK.subn("  regime: []\n", text, count=1)
        if n:
            text = new_text
            notes.append(f"regime de-fabricated ({ctx.get('regime')})")

    return text, notes


def main() -> int:
    changed = 0
    for path in sorted(CONNECTIONS.glob("*.yaml")):
        original = path.read_text(encoding="utf-8")
        updated, notes = surgical_edit(path, original)
        if notes:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            if changed <= 5:
                print(f"{path.name}: {'; '.join(notes)}")
    print(f"repaired {changed} connection file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
