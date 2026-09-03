#!/usr/bin/env python3
"""E5.3 — content-release manifest (audit F5; R18).

A "content release" is a named, verifiable state of the canonical knowledge:
`content/` + `connections/` + `sources/` plus the schemas and version source that give
them meaning. Until now the only release signal was a `VERSION` file nobody could check
a checkout against.

This script writes `exports/release-manifest.json`: a deterministic, sorted list of
every canonical file with its SHA-256, the aggregate `content_hash` that the export
stamps (identical algorithm to `scripts/validate.py`, so the two can never disagree),
the version triple from `schema/VERSION.yaml`, and headline counts. Anyone can verify a
downloaded release byte-for-byte without trusting the publisher.

Determinism: no wall-clock time, no git state — the same tree always produces the same
manifest, so the tracked artifact never churns and CI's `git diff --exit-code` step
catches a stale one.

Tagging itself stays a **human** action (a release is a claim about reviewed knowledge,
not something a script may assert). Run with `--tag-command` to print the exact git
commands for the current manifest.

Usage:
    python3 scripts/release_manifest.py              # regenerate + verify
    python3 scripts/release_manifest.py --check      # fail if the tracked manifest is stale
    python3 scripts/release_manifest.py --tag-command
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    print("error: PyYAML is required (python3 -m pip install pyyaml)", file=sys.stderr)
    raise SystemExit(2)

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANONICAL_DIRS = ("content", "connections", "sources")
# Files that define the *meaning* of canonical data; a release pins them too.
CONTRACT_FILES = (
    "schema/VERSION.yaml",
    "schema/concept.schema.json",
    "schema/connection.schema.json",
    "schema/source.schema.json",
    "schema/export.schema.json",
    "schema/relation-registry.yaml",
    "schema/agent-registry.yaml",
    "schema/extension-registry.yaml",
)
MANIFEST = ROOT / "exports" / "release-manifest.json"


def sha256_file(path: pathlib.Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_files() -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for name in CANONICAL_DIRS:
        directory = ROOT / name
        if directory.is_dir():
            out.extend(sorted(p for p in directory.rglob("*") if p.is_file()))
    return out


def aggregate_content_hash(paths: list[pathlib.Path]) -> str:
    """Same algorithm as scripts/validate.py so manifest and export always agree."""
    hasher = hashlib.sha256()
    for path in paths:
        hasher.update(str(path.relative_to(ROOT)).encode("utf-8"))
        hasher.update(b"\x00")
        hasher.update(path.read_bytes())
        hasher.update(b"\x00")
    return f"sha256:{hasher.hexdigest()}"


def build_manifest() -> dict:
    versions = yaml.safe_load((ROOT / "schema" / "VERSION.yaml").read_text(encoding="utf-8")) or {}
    paths = canonical_files()
    files = {str(p.relative_to(ROOT)): sha256_file(p) for p in paths}
    for rel in CONTRACT_FILES:
        path = ROOT / rel
        if path.exists():
            files[rel] = sha256_file(path)
    counts = {
        "entities": sum(1 for p in paths if p.suffix == ".md" and p.is_relative_to(ROOT / "content")),
        "connections": sum(1 for p in paths if p.is_relative_to(ROOT / "connections")),
        "sources": sum(1 for p in paths if p.is_relative_to(ROOT / "sources")),
    }
    return {
        "note": "DERIVED (plan v2 E5.3). Regenerate with scripts/release_manifest.py. "
                "Deterministic: no timestamps, no git state.",
        "release": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "schema_version": versions.get("schema_version"),
        "export_version": versions.get("export_version"),
        "relation_registry_version": versions.get("relation_registry_version"),
        "content_hash": aggregate_content_hash(paths),
        "counts": counts,
        "file_count": len(files),
        "files": dict(sorted(files.items())),
    }


def render(manifest: dict) -> str:
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if the tracked manifest differs from a fresh build")
    parser.add_argument("--tag-command", action="store_true",
                        help="print the git commands a human runs to tag this release")
    args = parser.parse_args()

    manifest = build_manifest()
    text = render(manifest)

    if args.check:
        if not MANIFEST.exists() or MANIFEST.read_text(encoding="utf-8") != text:
            print("FAIL: exports/release-manifest.json is stale — run "
                  "`python3 scripts/release_manifest.py` and commit the result", file=sys.stderr)
            return 1
        print("OK: release manifest is current")
        return 0

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(text, encoding="utf-8")
    print(f"OK: release manifest v{manifest['release']} "
          f"({manifest['counts']['entities']} entities, {manifest['counts']['connections']} "
          f"connections, {manifest['counts']['sources']} sources; {manifest['file_count']} files) "
          f"-> {MANIFEST.relative_to(ROOT)}")

    if args.tag_command:
        tag = f"content-v{manifest['release']}"
        print("\n# Human action — a release is a claim about reviewed knowledge:")
        print(f"git tag -a {tag} -m 'STEMMA content release {manifest['release']} "
              f"({manifest['content_hash'][:19]}…)'")
        print(f"git push origin {tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
