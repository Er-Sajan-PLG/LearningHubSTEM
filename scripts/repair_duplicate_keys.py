#!/usr/bin/env python3
"""Repair duplicate YAML frontmatter keys in canonical entities (Q1.2).

PyYAML's safe_load silently keeps the last value for a duplicated key, which hid
an authoring defect where `key_experiments:` was appended twice (respectively
with distinct content). This tool merges duplicate mapping keys deterministically:

- For list-valued keys found duplicated (key_experiments, examples, ...), the two
  lists are UNION-merged in document order and deduplicated (exact duplicates
  removed), preserving all unique content.
- Non-list duplicate scalar keys: last-wins is kept and the earlier dropped, but the
  tool reports them loudly for human review (never silently chooses for scalars it
  cannot merge).

The tool is idempotent: re-running after a repair finds no duplicates and changes
nothing. It only rewrites the YAML frontmatter block, never the prose body.

Exit codes: 0 = clean or all repaired, 1 = unrepaired error.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

# Keys that are safe to UNION-merge when duplicated (list-valued canonical metadata).
_LISTY_KEYS = {"key_experiments", "examples", "common_misconceptions",
               "learning_objectives", "real_world_applications", "aliases", "relationships"}


@dataclass
class _Issue:
    where: str
    action: str  # "unioned" | "last-wins"
    path: str


@dataclass
class _Merger:
    issues: list[_Issue] = field(default_factory=list)

    def merge_mapping(self, pairs: Any, path: str) -> list:
        """Merge a mapping's key/value pairs, dedup by scalar key."""
        seen: dict[str, Any] = {}
        order: list[str] = []
        for key, value in pairs:
            k = str(key)
            if k in seen:
                prev = seen[k]
                merged, action = self._merge_values(prev, value)
                seen[k] = merged
                self.issues.append(_Issue(path, action, f"{path}/{k}"))
            else:
                seen[k] = value
                order.append(k)
        return [(k, seen[k]) for k in order]

    def _merge_values(self, a: Any, b: Any) -> tuple[Any, str]:
        if isinstance(a, list) and isinstance(b, list):
            out: list[Any] = []
            for item in a + b:
                if item not in out:
                    out.append(item)
            return out, "unioned"
        # scalar / dict: last wins
        return b, "last-wins"

    def to_python(self, node: Any, path: str) -> Any:
        if isinstance(node, yaml.MappingNode):
            pairs = [
                (self.to_python(k, f"{path}/{str(k.value)}"), self.to_python(v, path))
                for k, v in node.value
            ]
            # We need scalar keys; handle via merge_mapping on raw string keys.
            merged: list[tuple[Any, Any]] = []
            seen: dict[Any, Any] = {}
            order: list[Any] = []
            for key_node, val_node in node.value:
                k = str(key_node.value)
                v = self.to_python(val_node, f"{path}/{k}")
                if k in seen:
                    prev = seen[k]
                    if isinstance(prev, list) and isinstance(v, list):
                        out: list[Any] = []
                        for item in prev + v:
                            if item not in out:
                                out.append(item)
                            seen[k] = out
                        self.issues.append(_Issue(path, "unioned", f"{path}/{k}"))
                    else:
                        seen[k] = v
                        self.issues.append(_Issue(path, "last-wins", f"{path}/{k}"))
                else:
                    seen[k] = v
                    order.append(k)
            return {k: seen[k] for k in order}
        if isinstance(node, yaml.SequenceNode):
            return [self.to_python(v, f"{path}[]") for v in node.value]
        if isinstance(node, yaml.ScalarNode):
            return _coerce_scalar(node)
        if node is None:
            return None
        return None  # pragma: no cover


def _coerce_scalar(node: yaml.ScalarNode) -> Any:
    """Convert a scalar node to its Python value by tag."""
    v = node.value
    tag = node.tag or "tag:yaml.org,2002:str"
    if tag.endswith(":bool"):
        return v.strip().lower() in ("true", "yes", "on")
    if tag.endswith(":int"):
        try:
            return int(v)
        except ValueError:
            return v
    if tag.endswith(":float"):
        try:
            return float(v)
        except ValueError:
            return v
    if tag.endswith(":null"):
        return None
    return v


def split_frontmatter(text: str) -> tuple[str, str] | None:
    """Return (body, remark_after_close) of a markdown frontmatter doc.

    A canonical entity is ``---\\n<body>\\n---\\n<prose>``. Splitting on ``---``
    (maxsplit=2) yields parts[0]='' (before opening), parts[1]=body, and
    parts[2]=everything after the closing ``---`` (starting with the newline that
    separated the closing marker from the prose). We return the body and that
    trailing remainder; the caller re-adds the closing ``---`` on reconstruction.
    """
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1], parts[2]


def merge_document(text: str) -> tuple[str, list[str]]:
    """Merge duplicate mapping keys in a YAML frontmatter string.

    Returns (repaired_yaml, list_of_reports).
    """
    loader = yaml.SafeLoader(text)
    try:
        node = loader.get_single_node()
    finally:
        loader.dispose()
    if node is None:
        return text, []

    merger = _Merger()
    data = merger.to_python(node, "")
    reports = [f"{i.where}: {i.action} dup key {i.path}" for i in merger.issues]
    if not reports:
        return text, []
    out = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return out, reports


def repair(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    fm = split_frontmatter(text)
    if fm is None:
        return 0
    body, after_close = fm
    repaired, reports = merge_document(body)
    if not reports:
        return 0
    try:
        yaml.safe_load(repaired)
    except yaml.YAMLError as exc:
        print(f"  error: repaired frontmatter for {path} is invalid: {exc}", file=sys.stderr)
        return 1
    # Reconstruct: opening '---', a blank line, the repaired body, the closing
    # '---', then the original prose remainder verbatim.
    new_text = f"---\n{repaired}\n---{after_close}"
    path.write_text(new_text, encoding="utf-8")
    print(f"  repaired {path.relative_to(ROOT)}: {'; '.join(reports)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    targets = list(CONTENT.rglob("*.md"))
    failed = 0
    repaired_count = 0
    for path in sorted(targets):
        before = path.read_text(encoding="utf-8")
        rc = repair(path)
        if rc != 0:
            failed += 1
        elif path.read_text(encoding="utf-8") != before:
            repaired_count += 1
    print(f"scanned {len(targets)} entities; repaired {repaired_count}; unrepaired errors {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())