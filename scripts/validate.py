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
CONNECTIONS = ROOT / "connections"
SOURCES = ROOT / "sources"
SCHEMA = ROOT / "schema"
SCHEMA_ = SCHEMA / "concept.schema.json"
CONN_SCHEMA = SCHEMA / "connection.schema.json"
SOURCE_SCHEMA = SCHEMA / "source.schema.json"
RELATION_REGISTRY = SCHEMA / "relation-registry.yaml"
EXPORT = ROOT / "exports" / "knowledge.json"

ID_RE = re.compile(r"^lhs:[a-z][a-z0-9-]*\.[a-z0-9][a-z0-9-]*$")
CONN_ID_RE = re.compile(r"^lhs:conn\.[0-9]{6}$")
SRC_ID_RE = re.compile(r"^lhs:src\.[a-z0-9][a-z0-9-]*$")
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
EXTENSION_REGISTRY = ROOT / "schema" / "extension-registry.yaml"


def load_extension_registry() -> dict:
    """Load the extension registry (ADR-0017), tolerating absence."""
    if not EXTENSION_REGISTRY.exists():
        return {"extensions": []}
    try:
        data = yaml.safe_load(EXTENSION_REGISTRY.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else {"extensions": []}
    except yaml.YAMLError:
        return {"extensions": []}


def check_extensions(data: dict, object_kind: str, errors: list, here: str) -> None:
    """Enforce that `extensions` keys are registered (ADR-0017).

    The schema leaves the map open so new dimensions never hard-fail; this gate is
    where governance lives. Every key must be a registered dimension applicable to
    this object kind, and any controlled enum must be respected.
    """
    extensions = data.get("extensions")
    if not extensions:
        return
    if not isinstance(extensions, dict):
        errors.append(f"{here} extensions must be an object/map")
        return

    registry = load_extension_registry()
    by_name = {e.get("name"): e for e in registry.get("extensions", []) if isinstance(e, dict)}

    for key, value in extensions.items():
        dim = by_name.get(key)
        if dim is None:
            errors.append(
                f"{here} extension '{key}' is not registered. Register it with: "
                "python3 scripts/register_extension.py add --name ... (see ADR-0017)"
            )
            continue
        if object_kind not in dim.get("applies_to", []):
            errors.append(
                f"{here} extension '{key}' applies to {dim.get('applies_to')}, "
                f"not '{object_kind}'"
            )
        enum = dim.get("enum")
        if enum and value not in enum:
            errors.append(
                f"{here} extension '{key}' value {value!r} not in controlled "
                f"vocabulary {enum}"
            )
        vtype = dim.get("value_type")
        if vtype == "string" and not isinstance(value, str):
            errors.append(f"{here} extension '{key}' must be a string")
        elif vtype == "number" and not isinstance(value, (int, float)):
            errors.append(f"{here} extension '{key}' must be a number")
        elif vtype == "boolean" and not isinstance(value, bool):
            errors.append(f"{here} extension '{key}' must be a boolean")


def check_historical(data: dict, errors: list, here: str) -> None:
    """Validate optional historical-attribution field (ADR-0018).

    When `historical` is present it must carry stated_by (str) and year (int);
    optional `where`/`context`/`note` strings; optional ordered `timeline[]` of
    {year:int, event:str, by?:str}. Absent-field is fine (unknown origin is not
    fabricated). Fields are additive and never required at the entity level.
    """
    hist = data.get("historical")
    if hist is None:
        return
    if not isinstance(hist, dict):
        errors.append(f"{here} historical must be an object")
        return

    sb = hist.get("stated_by")
    if not isinstance(sb, str) or not sb.strip():
        errors.append(f"{here} historical.stated_by is required and must be a non-empty string")

    y = hist.get("year")
    if not isinstance(y, int) or isinstance(y, bool):
        errors.append(f"{here} historical.year must be an integer")
    for key in ("where", "context", "note"):
        v = hist.get(key)
        if v is not None and not isinstance(v, str):
            errors.append(f"{here} historical.{key} must be a string")

    timeline = hist.get("timeline")
    if timeline is not None:
        if not isinstance(timeline, list):
            errors.append(f"{here} historical.timeline must be an array")
        else:
            for ev in timeline:
                if not isinstance(ev, dict):
                    errors.append(f"{here} historical.timeline entries must be objects")
                    continue
                if not isinstance(ev.get("year"), int):
                    errors.append(f"{here} historical.timeline[] requires an integer year")
                if not isinstance(ev.get("event"), str) or not ev.get("event"):
                    errors.append(f"{here} historical.timeline[] requires an event string")
                if ev.get("by") is not None and not isinstance(ev.get("by"), str):
                    errors.append(f"{here} historical.timeline[].by must be a string")


def load_schema() -> Any:
    if not HAVE_JSONSCHEMA or not SCHEMA_.exists():
        return None
    raw = json.loads(SCHEMA_.read_text(encoding="utf-8"))
    cast(Any, Draft202012Validator).check_schema(raw)  # raises on invalid schema
    return raw


def parse_entity(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("missing opening frontmatter marker '---'")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("frontmatter not closed with '---'")
    data = load_yaml_strict(parts[1], where=str(path.relative_to(ROOT)))
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a single YAML mapping")
    data["_file"] = str(path.relative_to(ROOT))
    return data


def load_yaml_strict(text: str, where: str = "<yaml>") -> Any:
    """Parse YAML and deterministically reject duplicate mapping keys.

    PyYAML's safe_load silently keeps the last value for a duplicated key, which
    hides authoring errors (Q1.2). We walk the composed node tree and raise a
    ValueError naming the exact duplicate path so the gate can surface it.
    """
    loader = yaml.SafeLoader(text)
    try:
        node = loader.get_single_node()
    finally:
        loader.dispose()

    if node is None:
        return None  # empty document

    dups: list[str] = []
    _collect_duplicate_keys(node, dups, "")
    if dups:
        raise ValueError(f"{where}: duplicate YAML key(s): {', '.join(sorted(set(dups)))}")
    return yaml.safe_load(text)


def _collect_duplicate_keys(node: Any, dups: list[str], path: str) -> None:
    """Recursively find duplicate mapping keys in a composed YAML node."""
    if isinstance(node, yaml.MappingNode):
        seen: set[str] = set()
        for key_node, value_node in node.value:
            key = key_node.value if key_node is not None else ""
            key_path = f"{path}/{key}"
            if key in seen:
                dups.append(key_path)
            else:
                seen.add(key)
            _collect_duplicate_keys(value_node, dups, key_path)
    elif isinstance(node, yaml.SequenceNode):
        for value_node in node.value:
            _collect_duplicate_keys(value_node, dups, f"{path}[]")


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


def load_relation_registry() -> dict:
    """Load the relation registry (authoritative relation vocabulary)."""
    if not RELATION_REGISTRY.exists():
        return {"relations": {}}
    try:
        data = yaml.safe_load(RELATION_REGISTRY.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else {"relations": {}}
    except yaml.YAMLError:
        return {"relations": {}}


def _relation_semantics(raw: Any, info: dict) -> tuple[list, list]:
    """Best-effort domain/range lists from a relation descriptor.

    The vocabulary may encode domain/range as either YAML list syntax used here
    (a plain list) or the '|-' block style, both of which parse to a list under
    safe_load. Defensive fallback to [] keeps the check lenient for exotic forms.
    """
    domain = info.get("domain")
    range_ = info.get("range")
    return (
        [str(x) for x in domain] if isinstance(domain, list) else [],
        [str(x) for x in range_] if isinstance(range_, list) else [],
    )


def validate_connection(conn: dict, entities: dict, sources: dict, errors: list) -> None:
    """Validate a first-class connection (ADR-011 / connection.schema.json)."""
    here = f"{conn.get('_file', '<connection>')}:"
    cid = conn.get("id")
    if cid is None:
        errors.append(f"{here} missing required 'id'")
    elif not isinstance(cid, str) or not CONN_ID_RE.fullmatch(cid):
        errors.append(f"{here} invalid connection ID: {cid!r} (expected lhs:conn.NNNNNN)")

    if conn.get("type") != "connection":
        errors.append(f"{here} connection type must be 'connection' (found {conn.get('type')!r})")

    src = conn.get("source")
    tgt = conn.get("target")
    if not isinstance(src, str) or src not in entities:
        errors.append(f"{here} source does not resolve to a canonical entity: {src!r}")
    if not isinstance(tgt, str) or tgt not in entities:
        errors.append(f"{here} target does not resolve to a canonical entity: {tgt!r}")

    rel = conn.get("relation")
    registry = load_relation_registry().get("relations", {})
    info = registry.get(rel) if isinstance(rel, str) else None
    if rel is None:
        errors.append(f"{here} missing required 'relation'")
    elif not isinstance(rel, str) or info is None:
        errors.append(f"{here} relation not in relation-registry.yaml: {rel!r}")

    # Domain/range: only when both endpoint types and the registry allow-list are known.
    if info and isinstance(src, str) and isinstance(tgt, str):
        stype = entities.get(src, {}).get("type")
        ttype = entities.get(tgt, {}).get("type")
        domain, range_ = _relation_semantics(None, info)
        if stype and domain and stype not in domain:
            errors.append(f"{here} relation '{rel}' domain excludes source type '{stype}'")
        if ttype and range_ and ttype not in range_:
            errors.append(f"{here} relation '{rel}' range excludes target type '{ttype}'")

    # Assertion must be present (required by schema); enforce provenance presence.
    prov = conn.get("provenance")
    if not isinstance(prov, dict):
        errors.append(f"{here} connection requires a provenance object")
    else:
        if not prov.get("asserted_by"):
            errors.append(f"{here} provenance.asserted_by is required")
        if not prov.get("generated_by"):
            errors.append(f"{here} provenance.generated_by is required")
        if not prov.get("method"):
            errors.append(f"{here} provenance.method is required")

    # Evidence source_ref must resolve to a canonical source.
    for idx, ev in enumerate(conn.get("evidence", []) or []):
        if not isinstance(ev, dict):
            errors.append(f"{here} evidence[{idx}] must be an object")
            continue
        ref = ev.get("source_ref")
        if ref is not None and ref not in sources:
            errors.append(f"{here} evidence.source_ref does not resolve to a source: {ref!r}")

    check_extensions(conn, "connection", errors, here)


def validate_source(src: dict, errors: list) -> None:
    """Validate a canonical source object (source.schema.json)."""
    here = f"{src.get('_file', '<source>')}:"
    sid = src.get("id")
    if sid is None:
        errors.append(f"{here} missing required 'id'")
    elif not isinstance(sid, str) or not SRC_ID_RE.fullmatch(sid):
        errors.append(f"{here} invalid source ID: {sid!r} (expected lhs:src.<slug>)")
    check_extensions(src, "source", errors, here)


def load_canonical_yaml_dir(directory: Path, schema_path: Path, errors: list,
                            entities: dict, sources: dict) -> dict:
    """Load + validate all canonical YAML objects in a directory (connections/sources).

    Returns a dict keyed by object id. Each object is validated against (a) its
    JSON schema and (b) the custom checks in validate_connection/validate_source.
    Only objects that parse are collected; unparsable files are reported.
    """
    out: dict[str, dict] = {}
    if not directory.exists():
        return out
    schema = None
    if HAVE_JSONSCHEMA and schema_path.exists():
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            cast(Any, Draft202012Validator).check_schema(schema)
        except Exception as exc:  # noqa: BLE001 - schema misconfiguration is fatal
            errors.append(f"invalid schema {schema_path}: {exc}")
            schema = None
    validator = cast(Any, Draft202012Validator)(schema) if schema else None

    for path in sorted(directory.glob("*.yaml")):
        try:
            data = load_yaml_strict(path.read_text(encoding="utf-8"), where=str(path.relative_to(ROOT)))
        except ValueError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path.relative_to(ROOT)}: expected a YAML mapping")
            continue
        data["_file"] = str(path.relative_to(ROOT))
        if validator:
            obj = {k: v for k, v in data.items() if not k.startswith("_")}
            for err in validator.iter_errors(obj):
                errors.append(f"{data['_file']}: schema violation: {err.message}")
        # kind-specific deep checks
        kind = data.get("type")
        if kind == "connection":
            validate_connection(data, entities, sources, errors)
        else:
            validate_source(data, errors)
        _id = data.get("id")
        if isinstance(_id, str):
            if _id in out:
                errors.append(f"duplicate {kind} id {_id!r} in {out[_id]['_file']} and {data['_file']}")
            out[_id] = data
    return out


def main() -> int:
    errors: list = []
    entities: dict[str, dict] = {}

    if not CONTENT.exists():
        print(f"error: content directory not found: {CONTENT}", file=sys.stderr)
        return 1

    for path in sorted(CONTENT.rglob("*.md")):
        try:
            entity = parse_entity(path)
        except ValueError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        validate_entity(entity, errors, filename_slug=path.stem)
        check_extensions(entity, "entity", errors, f"{entity['_file']}:")
        check_historical(entity, errors, f"{entity['_file']}:")
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

    # Q2: load + validate first-class connections and sources (ADR-011). These are
    # first-class canonical inputs — the gate now covers content/ + connections/ + sources/.
    sources = load_canonical_yaml_dir(SOURCES, SOURCE_SCHEMA, errors, entities, {})
    connections = load_canonical_yaml_dir(CONNECTIONS, CONN_SCHEMA, errors, entities, sources)

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
        "connection_count": len(connections),
        "source_count": len(sources),
        "entities": [
            {k: v for k, v in entities[i].items() if not k.startswith("_")}
            for i in sorted(entities)
        ],
        "connections": [
            {k: v for k, v in connections[i].items() if not k.startswith("_")}
            for i in sorted(connections)
        ],
        "sources": [
            {k: v for k, v in sources[i].items() if not k.startswith("_")}
            for i in sorted(sources)
        ],
    }
    EXPORT.parent.mkdir(parents=True, exist_ok=True)
    EXPORT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"OK: {len(entities)} entities valid; export written to {EXPORT.relative_to(ROOT)}")

    # Auto-sync the derived export into the explorer (3D visual) so the explorer
    # never drifts from canonical content. The explorer builds/loads from
    # explorer/public/exports/knowledge.json; keeping it in sync here means any
    # content change that runs the validator propagates to the visual.
    explorer_target = ROOT / "explorer" / "public" / "exports" / "knowledge.json"
    if explorer_target.parent.is_dir() or (ROOT / "explorer").is_dir():
        explorer_target.parent.mkdir(parents=True, exist_ok=True)
        explorer_target.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"OK: explorer export synced to {explorer_target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())