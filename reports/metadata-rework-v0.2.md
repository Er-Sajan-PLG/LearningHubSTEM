# Metadata Rework — v0.2

## Current dimensions
- Entity: id/type/name/domain/status/definition/provenance/relationships (+updated_at/version/external_ids/rights after urgent)
- Connection: id/type/source/relation/target/assertion(context, evidence, provenance, inference) + polarity/created_at/updated_at/validity/lifecycle/qualifiers/rights
- Source: id/type/citation (+title/authors/year/doi/url/source_role/rights)

## Urgent additions (implemented)
- M2 polarity, M3 timestamps+validity, M6 source bibliographic, M8 evidence type expanded, M9 stance, M11 locator_struct, M12 qualifiers, M19 lifecycle, M20 claim_signature (derived), M23 rights, M25 entity updated_at/version

## Important (deferred to v0.2.x)
- M4 evidence_considered, M5 activity timestamps, M7 source_role, M18 version, M24 external_ids

## Future / Deferred / Rejected
- M1 proposition ID (defer), M10 quality, M13 assumption ontology, M14 qualifiers, M16 statistics, M22 language, M21 content_hash (addition, not urgent)

## Schema changes
- connection.schema.json: +polarity, +created_at/updated_at, +validity{valid_from,valid_until}, +lifecycle{reason,replaced_by}, +context.qualifiers[], evidence.stance+locator_struct, rights; all optional, keeps schema_version 0.2
- source.schema.json: +title/authors/year/publisher/journal/doi/url/isbn/edition/language/source_role/rights
- concept.schema.json: +updated_at, version, external_ids, rights

## Migration changes
- scripts/migrate_metadata_urgent.py: adds polarity positive, timestamps=file mtime, stance supports, qualifiers [], validity/lifecycle/rights null, idempotent

## Validator changes
- Polarity enum, timestamps ISO8601, validity range, stance enum, lifecycle replaced_by resolves, source_role, rights; allows missing

## Before/After
- Before: 397 connections without polarity/timestamps/stance; 3 sources thin
- After: 397 with polarity positive, created_at/updated_at, stance supports, qualifiers []

## New invariants
- Polarity default positive; rejected != negated
- valid_until >= valid_from if both set
- claim_signature derived (not canonical)
- review_history ordered

## Warnings/Errors
- Warning: canonical without evidence; Error: invalid polarity/stance/superseded_by self

## Table (Field | Object | Meaning | Owner | Required? | Controlled? | C/D | Phase)
| Field | Object | Meaning | Owner | Required | Controlled | C/D | Phase |
| polarity | connection | positive/negative | assertion | no (default positive) | yes | C | urgent |
| created_at | connection/entity | lifecycle creation | lifecycle | no (migrated file mtime) | ISO8601 | C | urgent |
| validity | connection | scientific validity period | context | no | no | C | urgent |
| evidence.stance | evidence | supports/contradicts | evidence | no (default supports) | yes | C | urgent |
| context.qualifiers | connection | extensible conditions | context | no | yes type | C | urgent |
| claim_signature | integrity | hash(source|relation|target|polarity) | integrity | no | no | D | urgent |
