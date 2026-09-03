# STEMMA — Migrations log

**Status:** Active · **Related:** `docs/VERSIONING.md`, `schema/VERSION.yaml`,
`docs/decisions/`, `docs/STEMMA-IMPLEMENTATION-PLAN-v2.md` (E5.5)

Every change to a canonical schema, the relation registry, a controlled vocabulary, or the
export contract **appends a row here in the same PR that makes the change**. A schema edit
without a migration entry is an incomplete change (audit F6: governance by document kept
outrunning governance by mechanism).

Each entry answers four questions:

1. **What changed** in the schema/registry/contract.
2. **Is old data still valid** against the *old* schema? (Always yes — schemas are versioned,
   never retro-edited. Old exports remain readable at their stamped `schema_version`.)
3. **Is old data valid against the new schema** — and if not, what migrates it.
4. **Which script performed the migration**, so the transformation is reproducible.

## Conventions

- Schemas are **versioned, not rewritten**: data written under `schema_version: 0.2` continues to
  validate against the 0.2 schema forever. `schema_version` in `schema/VERSION.yaml` is the single
  source (ADR-0022).
- **Additive** changes (new optional field, new enum member, new relation marked `reserved`) do not
  bump `schema_version`; they bump the repository `VERSION` MINOR.
- **Breaking** changes (removed/renamed field, narrowed enum, new required field) bump
  `schema_version` (and `export_version` if the contract shape moves), require an ADR, and require a
  migration script plus a row below.
- Derived artifacts (`exports/`, `reports/`) are regenerated, never migrated.

## Log

| # | Date | Change | Version effect | Old data vs old schema | Old data vs new schema | Migration |
|---|------|--------|----------------|------------------------|------------------------|-----------|
| M1 | 2026-08-30 | First-class connections (ADR-0011): `connections/` + `connection.schema.json`; inline `relationships[]` retained | `schema_version` 0.1 → 0.2 | valid | valid (additive) | `scripts/migrate_relationships.py` |
| M2 | 2026-08-31 | Metadata rework (ADR-0016): `external_ids`, `version`, `updated_at`, `rights`, `lifecycle` | additive; `schema_version` 0.2 | valid | valid (all optional) | `scripts/migrate_metadata_urgent.py`, `scripts/repair_metadata.py` |
| M3 | 2026-09-03 | Registry integrity (ADR-0021): inverse coherence repaired, entity types `phenomenon`/`model`/`experiment` added, 37 unused relations marked `reserved` | `relation_registry_version` 0.2 → 0.3; type enum widened (additive) | valid | valid | `scripts/repair_registry.py` |
| M4 | 2026-09-03 | Context vocabularies enforced (ADR-0021): subdomain repairs, `math` → `mathematics`, illegal `scale` fixed | content-only | valid | valid after repair | `scripts/repair_connection_context.py` |
| M5 | 2026-09-03 | Connections-only truth (ADR-0020): inline `relationships[]` becomes a generated projection with a gate | contract-neutral | valid | valid | `scripts/sync_relationships.py` |
| M6 | 2026-09-03 | Single version source + deterministic exports (ADR-0022): `schema/VERSION.yaml`; `generated_at` → `content_hash` | `export_version` unchanged; exports reshaped (field swap) | valid | consumers reading `generated_at` must read `content_hash` | `scripts/validate.py` (regeneration) |
| M7 | 2026-09-04 | Export contract v1.0 (ADR-0023): `connections` + `sources` REQUIRED; `export.schema.json` enforced pre-write; `legacy_export_version` compat view | `export_version` 0.1 → **1.0**; repo `VERSION` 1.1.0 → 2.0.0 | valid | consumers pinned to `0.1` read `exports/knowledge.compat-0.1.json` during the co-release window | `scripts/validate.py`; `docs/EXPORT-VERSION-MIGRATION-Q3.md` |
| M8 | 2026-09-04 | Identity hardening (ADR-0023): `external_ids` format-checked; `schema/agent-registry.yaml` resolves every provenance agent | additive | valid | valid — but a new agent id must be registered in the same PR | none (validation only) |
| M9 | 2026-09-04 | Claim signatures + edit-in-place detection (plan v2 E4.3/E4.4) and connection-triple immutability (E4.5) | validation-only; no schema field added | valid | valid | `scripts/check_content_hashes.py` (ledger seed), `scripts/check_id_immutability.py` |

## Adding an entry

1. Make the schema/registry/contract change.
2. Write (or extend) the migration script under `scripts/`; it must be idempotent.
3. Append a row above with the four answers.
4. Record the ADR and land the enforcement code in the same PR (plan v2 §1).
5. Run `python3 scripts/verify_all.py` — exit 0 is required.
