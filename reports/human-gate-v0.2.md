# Human Gate — Metadata Rework v0.2 Corrective Hardening

## Urgency Final (after Gates 1-16)
- **URGENT (implemented):** M2 polarity, M3 timestamps (created_at/updated_at null for migrated, validity optional), M6 source bibliographic (optional), M8 evidence type expanded, M9 stance (omitted for migrated unreviewed, supports for canonical), M11 locator_struct, M12 qualifiers, M19 lifecycle, M20 claim_signature derived, M23 rights, M25 entity version
- **IMPORTANT (deferred):** M4 evidence_considered, M5 activity timestamps, M7 source_role, M18 version, M24 external_ids
- **KEEP:** M15 confidence, M17 review/type separation
- **DEFER:** M1 proposition ID (claim_signature suffices), M10 quality, M13 assumptions, M14 qualifiers, M16 stats, M22 language, M21 content_hash
- **REJECT:** none wholesale

## Changed Fields
- Added `assertion.polarity` (positive default), `created_at/updated_at` (null for migrated), `validity{valid_from,valid_until}`, `lifecycle{reason,replaced_by}`, `context.qualifiers[]`, evidence `stance`+`locator_struct`, source bibliographic expansion, entity `updated_at/version/external_ids/rights`

## Removed Unsafe Defaults
- `created_at/updated_at` file mtime → null for 384 migrated + 128 entities (repaired)
- `evidence.stance=supports` for migrated unreviewed → omitted (42 evidence items repaired)

## New Invariants
- Polarity default positive, distinct from rejected/contradicts
- `valid_until >= valid_from`
- `claim_signature` derived, not canonical ID
- `review_history.at` is actual review time, not file mtime
- `evidence stance` absent = not established

## Migration Impact
- 384 connections timestamp repaired, 42 evidence stances repaired, 128 entities repaired
- 50 canonical preserved with stance supports and review_history intact
- Idempotent rerun: 0 repaired

## Remaining Gaps
- M1 proposition identity still defer (claim_signature sufficient for v0.2)
- M4/M5/M7/M10/M13/M14/M16/M18/M22/M24 deferred; none block trusted corpus
- M21 content_hash deferred (addition)

## Breaking Changes
- **No** — additive optional, `schema_version 0.2`, `export_version 0.1` retained. Validator allows missing.

## Human Approval Required
- Urgent semantics: polarity default, timestamp null policy, stance omission, source optional fields — all documented above.

