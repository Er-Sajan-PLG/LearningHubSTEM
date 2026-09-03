# Q3 — Export Contract Version: Migration Impact Analysis

> **Superseded 2026-09-04 by ADR-0023:** gate G-A decided — `export_version` is now **`1.0`**
> with `connections`/`sources` required (`schema/export.schema.json`). The co-release path this
> document asked for is implemented as the `exports/knowledge.compat-0.1.json` view. Kept for
> history and for the consumer checklist in §4.

**Status:** Investigation complete. **Decision: do NOT bump `export_version` in this phase**
(the Q1/Q2 change is additive and backward-compatible). This documents the full impact so a
future contract migration (adding connections/sources as a *required* part of the canonical
consumer contract) is governed and coordinated.

**Related:** `docs/ARCHITECTURE-REVIEW-v0.3.md` §C.2 (version-drift), §J (versioning),
ADR-0008 (versioning), ADR-0007 (export contract), `docs/STEMMA-CONSUMER-SEAM.md`.

---

## 1. What changed in Q1/Q2 (this phase)

`scripts/validate.py` now validates first-class `connections/` and `sources/` and includes them
in the derived export. The export gained **additive top-level keys**:

```diff
 export_version: "0.1"          # unchanged
 schema_version:  "0.1"         # unchanged
 generated_at, source           # unchanged
 entity_count:   224            # unchanged
+connection_count: 654
+source_count:     3
 entities:[...]                 # unchanged (still the required member)
+connections:[...]              # NEW (additive)
+sources:[...]                  # NEW (additive)
```

The **schema_version** is left at `"0.1"` here. The JSON schemas themselves self-describe as
v0.2 (see §4) — reconciling that *schema* version tag to match the schema content is a separate,
documented follow-up (§5).

## 2. Producers of the export contract

| Producer | File | Writes `export_version`? |
|----------|------|--------------------------|
| `scripts/validate.py` | `exports/knowledge.json` | Yes — currently hardcodes `"0.1"` |
| `scripts/export_review_aware.py` | `exports/knowledge.{all,reviewed,canonical,proposed,rejected,trusted}.json` | Yes — derived view exports |
| `scripts/graph_analysis.py` | `exports/knowledge.extended.json` | Yes — derived analytics export |

These all emit `export_version`; a version bump must be coordinated across them.

## 3. Consumers of the export contract

| Consumer | Path | Reads | Version enforcement |
|----------|------|-------|---------------------|
| STEM-TUITION adapter | `STEM-TUITION/apps/shell/src/lib/lhs-adapter.ts` | `entities` only | **Hard**: `SUPPORTED_EXPORT_VERSION='0.1'`; throws `LhsUnsupportedVersionError` on `!== '0.1'`. Does NOT read connections/sources. No `additionalProperties:false`. |
| LHS explorer | `explorer/src/services/knowledge-export-loader.ts` | `entities` only | Reads `export_version`/`schema_version`/`entities` types; tolerates extra keys. |
| AI agents / future consumers | (planned) | contract-dependent | n/a |

**Compatibility conclusion:** because both current consumers read only `entities` and neither
rejects unexpected top-level keys, the additive `connections`/`sources`/counts keys are
**backward-compatible**. Bumping `export_version` to `0.2` would *break* the STEM-TUITION
adapter today.

## 4. Version declarations and fixture/docs to update on any future bump

- `STEM-TUITION/apps/shell/src/lib/lhs-adapter.ts` — `SUPPORTED_EXPORT_VERSION = '0.1'`.
- `STEMMA/docs/STEMMA-CONSUMER-SEAM.md` — documents `export_version: 0.1`.
- `STEMMA/docs/STEMMA-SPECIFICATION.md` §10/§11 — three-track versioning rules.
- `docs/decisions/0007-export-contract.md`, `0008-versioning.md` — contract/versioning ADRs.
- `scripts/validate.py` + `scripts/export_review_aware.py` + `scripts/graph_analysis.py` — the
  literal `"0.1"` producers.
- Any test asserting the exact export shape (currently none assert literal `additionalProperties`).
- `explorer/public/exports/knowledge.json` + `explorer/dist/exports/knowledge.json` (derived).

**Schema self-description drift (separate follow-up):** `concept.schema.json`,
`connection.schema.json`, and `relation-registry.yaml` carry `v0.2` in their headers while the
export writes `schema_version: "0.1"`. Reconcile by aligning one authoritative source of truth
for `schema_version` (e.g. from `schema/` files) when a contract migration is authorized.

## 5. Recommendation

- **Now (this phase):** keep `export_version: "0.1"`. The Q2 change is additive.
- **Future (governed decision):** when connections/sources become a *required* part of the
  canonical consumer contract (so consumers can rely on relationship assertions from the
  export), file a decision record and bump `export_version: "0.2"`, updating BOTH the LHS
  producer script(s) AND the STEM-TUITION adapter's `SUPPORTED_EXPORT_VERSION` in the same
  release. Coordinate across §3/§4 so the adapter keeps working.
- Do **not** bump casually; the only hard consumer rejects any version other than `0.1`.

## 6. Traceability

| Finding | Evidence |
|---------|----------|
| Adapter hard-requires 0.1 | `lhs-adapter.ts:21,69` |
| Explorer tolerates extra keys | `knowledge-export-loader.ts:70-75` |
| Export is additive in this phase | `scripts/validate.py` payload (this branch) |
| ADR-0008 governs versioning | `docs/decisions/0008-versioning.md` |
| Consumer seaim claims 0.1 | `docs/STEMMA-CONSUMER-SEAM.md:23` |