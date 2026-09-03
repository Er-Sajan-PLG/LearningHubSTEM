# STEMMA Versioning

**Version:** 2.0.0
**Status:** Active
**Owner:** Governance
**Applies To:** This repository (canonical knowledge foundation)
**Related:** `schema/concept.schema.json`, `exports/knowledge.json`, `scripts/validate.py`,
  workspace `docs/WORKSPACE-VERSIONING.md`, `docs/decisions/0008-versioning.md`

---

## 1. Purpose

Versioning in STEMMA distinguishes three separate, never-collapsed tracks (per
decision 0008), plus a release tracker for content:

- **`schema_version`** — version of `schema/concept.schema.json` (field set, enums, constraints).
- **`export_version`** — version of the `exports/knowledge.json` consumer contract (shape/semantics).
- **Content release** — new/edited/deprecated entities (any content change; does not imply a contract bump).
- **`VERSION` (this file's `**Version:**`)** — the repository's semantic release tracker used
  by the workspace versioning system to keep docs fresh and coordinate cross-repo releases.

---

## 2. Source of truth

| Track | Source | Where recorded |
|-------|--------|----------------|
| Schema | `schema_version` | `exports/knowledge.json`, `schema/concept.schema.json` |
| Export contract | `export_version` | `exports/knowledge.json` |
| Content release | content changes + `VERSION` bump | git history; release semver |
| Repo release | `VERSION` file | this file's `**Version:**` + workspace `version_bump.py` |

---

## 3. Bumping rules

- **Schema / contract change (breaking):** bump `schema_version` / `export_version` by the
  documented rule (breaking → major) and record an ADR. See decision 0008.
- **Content addition / curation:** bump `VERSION` MINOR (new knowledge) or PATCH
  (correction/review), using `version_bump.py` so doc markers stay in sync.
- Additive schema/metadata extension (ADR-0017/0018): leave `schema_version`/`export_version`
  unchanged; bump `VERSION` MINOR.

The workspace tool keeps doc `**Version:**` markers fresh:

```bash
python3 ../scripts/version_bump.py bump minor --scope STEMMA   # 1.0.0 -> 1.1.0
python3 ../scripts/version_bump.py check --scope STEMMA        # must exit 0
```

---

## 4. Derived artifacts

`exports/*.json` are **derived and regenerable** — never hand-edited. Regenerate with
`python3 scripts/validate.py`. They are validated before the export is written; a consumer
never handles a dangling reference.

---

## 4a. Contract history

| `export_version` | Date | Change | Record |
|------------------|------|--------|--------|
| 0.1 | 2026-08 | entities-only contract; `connections`/`sources` additive (ADR-0011) | ADR-0007, `EXPORT-VERSION-MIGRATION-Q3.md` |
| **1.0** | 2026-09-04 | `connections` + `sources` **required**; shape in `schema/export.schema.json`; `relationships[]` deprecated projection; compat `0.1` view during co-release | ADR-0023 (repo `VERSION` 1.1.0 → 2.0.0) |
| 2.0 (planned) | after consumer reads `connections[]` | remove `entities[].relationships` (plan v2 E1.7) | gate |

---

## 5. Enforcement

- `scripts/validate.py` validates schema/status/relationships/provenance/extensions/historical.
- The workspace pre-commit `check-doc-versions` hook (and per-repo CI mirror) verifies doc
  version markers match `VERSION` before merge.
- Content is curriculum/grade-agnostic (NORTHSTAR): grade semantics live only in consumer
  mapping docs.

---

*Derived from workspace `docs/WORKSPACE-VERSIONING.md` and decision 0008.*