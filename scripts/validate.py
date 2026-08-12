#!/usr/bin/env python3
"""LearningHubSTEM validator + export generator (v0.1).

Validates canonical content under content/ against schema/concept.schema.json,
then regenerates exports/knowledge.json (a derived artifact — never the source of truth).

Exit codes
    0  valid; export regenerated
    1  validation errors
    2  missing dependency

Dependencies: PyYAML (required). jsonschema (optional — used when importable).
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

try:
    import yaml
except ImportError:  # pragma: no cover
    print("error: PyYAML is required (python3 -m pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

try:
    from jsonschema import Draft202012Validator

    HAVE_JSONSCHEMA = True
except ImportError:  # pragma: no cover
    Draft202012Validator = None
    HAVE_JSONSCHEMA = False

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
SCHEMA = ROOT / "schema" / "concept.schema.json"
EXPORT = ROOT / "exports" / "knowledge.json"

ID_RE = re.compile(r"^lhs:[a-z][a-z0-9-]*\.[a-z0-9][a-z0-9-]*$")
TYPES = {"concept", "quantity", "unit", "law", "equation", "misconception"}
STATUSES = {"draft", "machine_validated", "human_reviewed", "canonical", "deprecated", "superseded"}
REL_TYPES = {
    "logically_requires", "mathematically_requires", "part_of", "derived_from",
    "special_case_of", "generalizes", "equivalent_to", "applies_to",
    "appears_in_law", "related_to",
}
REQUIRED = ["id", "type", "name", "domain", "status", "definition", "provenance"]

SOURCE_KINDS = {
    "human-authored", "textbook", "academic-or-research", "institutional",
    "standards-or-specification", "ai-assisted-draft", "other",
}
REVIEWED_STATUSES = {"human_reviewed", "canonical"}


def load_schema():
    if not HAVE_JSONSCHEMA or not SCHEMA.exists():
        return None
    raw = json.loads(SCHEMA.read_text(encoding="utf-8"))
    cast(Any, Draft202012Validator).check_schema(raw)  # raises on invalid schema
    return raw


def parse_entity(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("missing opening frontmatter marker '---'")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("frontmatter not closed with '---'")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a single YAML mapping")
    data["_file"] = str(path.relative_to(ROOT))
    return data


def validate_entity(entity: dict, errors: list, filename_slug: str | None = None) -> None:
    here = f"{entity['_file']}:"

    # Required fields present and non-empty strings
    for field in REQUIRED:
        value = entity.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"{here} missing/empty required field '{field}'")

    # ID format
    _id = entity.get("id")
    if isinstance(_id, str) and not ID_RE.fullmatch(_id):
        errors.append(f"{here} invalid stable ID format: {_id!r} (expected lhs:<domain>.<slug>)")

    # Filename must equal the final ID slug (canonical representation rule)
    if isinstance(_id, str) and filename_slug:
        slug = _id.rsplit(".", 1)[-1]
        if filename_slug != slug:
            errors.append(
                f"{here} filename '{filename_slug}.md' does not match id slug '{slug}'"
            )

    # Enums (schema would catch these too; keep checks independent of jsonschema)
    if entity.get("type") not in TYPES:
        errors.append(f"{here} unknown type: {entity.get('type')!r}")
    if entity.get("status") not in STATUSES:
        errors.append(f"{here} unknown status: {entity.get('status')!r}")

    # Provenance shape
    prov = entity.get("provenance")
    if isinstance(prov, dict) and not isinstance(prov.get("ai_drafted"), bool):
        errors.append(f"{here} provenance.ai_drafted must be a boolean")
    if isinstance(prov, dict) and prov.get("source_kind") is not None:
        if prov.get("source_kind") not in SOURCE_KINDS:
            errors.append(f"{here} provenance.source_kind not in vocabulary: {prov.get('source_kind')!r}")
    if isinstance(prov, dict) and prov.get("ai_drafted") is False:
        if not (prov.get("source") or prov.get("reviewer")):
            errors.append(f"{here} provenance needs source or reviewer when not AI-drafted")

    # Reviewed/canonical status requires a named reviewer
    if entity.get("status") in REVIEWED_STATUSES:
        if not (isinstance(prov, dict) and prov.get("reviewer")):
            errors.append(f"{here} status {entity.get('status')!r} requires provenance.reviewer")

    # Aliases must be valid IDs and not equal the entity's own id
    for alias in entity.get("aliases", []) or []:
        if not isinstance(alias, str) or not ID_RE.fullmatch(alias):
            errors.append(f"{here} alias is not a valid stable ID: {alias!r}")
        elif alias == _id:
            errors.append(f"{here} alias must not equal the entity's own id: {alias!r}")

    # Relationships
    for rel in entity.get("relationships", []) or []:
        if not isinstance(rel, dict):
            errors.append(f"{here} relationship must be an object")
            continue
        rtype = rel.get("type")
        if rtype not in REL_TYPES:
            errors.append(f"{here} relationship type not in whitelist: {rtype!r}")
        target = rel.get("target")
        if not isinstance(target, str) or not target.startswith("lhs:"):
            errors.append(f"{here} relationship target must be an 'lhs:' ID: {target!r}")

    # Deprecation hygiene
    if entity.get("status") in ("deprecated", "superseded") and not entity.get("deprecated_by"):
        errors.append(f"{here} status is {entity.get('status')} but no deprecated_by set")


def main() -> int:
    errors: list = []
    entities: dict[str, dict] = {}

    if not CONTENT.exists():
        print(f"error: content directory not found: {CONTENT}", file=sys.stderr)
        return 1

    for path in sorted(CONTENT.glob("*.md")):
        try:
            entity = parse_entity(path)
        except ValueError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        validate_entity(entity, errors, filename_slug=path.stem)
        _id = entity.get("id")
        if isinstance(_id, str):
            if _id in entities:
                errors.append(f"duplicate id {_id!r} in {entities[_id]['_file']} and {entity['_file']}")
            entities[_id] = entity

    # Schema conformance (optional dependency)
    schema = load_schema()
    if schema is not None:
        validator = cast(Any, Draft202012Validator)(schema)
        for _id, entity in entities.items():
            data = {k: v for k, v in entity.items() if not k.startswith("_")}
            for err in validator.iter_errors(data):
                errors.append(f"{entity['_file']}: schema violation: {err.message}")

    # Dangling relationship targets + semantic type rules
    for _id, entity in entities.items():
        etype = entity.get("type")
        for rel in entity.get("relationships", []) or []:
            target = rel.get("target")
            if isinstance(target, str) and target not in entities:
                errors.append(f"{entity['_file']}: dangling relationship target: {target} (from {_id})")
                continue
            rtype = rel.get("type")
            target_type = entities.get(target, {}).get("type")
            # Core semantic rules (specification §5.1)
            if rtype == "applies_to" and etype != "law":
                errors.append(f"{entity['_file']}: applies_to requires a 'law' source (found {etype})")
            if rtype == "appears_in_law" and target_type != "law":
                errors.append(f"{entity['_file']}: appears_in_law target must be a 'law' (found {target_type})")

    # Report
    if errors:
        print(f"FAIL: {len(errors)} problem(s) found", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        return 1

    # Regenerate derived export (sorted for determinism)
    payload = {
        "export_version": "0.1",
        "schema_version": "0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "content/",
        "entity_count": len(entities),
        "entities": [
            {k: v for k, v in entities[i].items() if not k.startswith("_")}
            for i in sorted(entities)
        ],
    }
    EXPORT.parent.mkdir(parents=True, exist_ok=True)
    EXPORT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"OK: {len(entities)} entities valid; export written to {EXPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())