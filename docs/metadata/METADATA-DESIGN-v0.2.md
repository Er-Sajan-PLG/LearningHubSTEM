# Metadata Design — v0.2 (Post-Audit)

## Conceptual Layers (Part III)

```
1. Identity       — id, type, claim_signature (derived)
2. Semantics      — source, relation, target, polarity, qualifiers
3. Context        — domain, subdomain, regime[], scale, assumptions, qualifiers[]
4. Evidence       — evidence[] {type, stance, source_ref, locator{}}, supporting text not duplicated
5. Provenance     — asserted_by, generated_by, method, reviewed_by, activity timestamps
6. Review/Curation— assertion {type, status, review{status}, polarity}, review_history[]
7. Lifecycle      — assertion.status active/deprecated/superseded + lifecycle{reason, replaced_by} + version/updated_at
8. Temporal       — created_at, updated_at, review_history.at, source year/publication_date, validity{valid_from,valid_until}
9. Integrity      — content_hash (derived), claim_signature (derived), inverse/transitive (derived)
10. Rights        — rights{license, attribution, rights_holder} for sources/entities
```

## Urgent Additions — Minimal Schema (Part V)

### Connection (additive to v0.2, still export_version 0.1)
```yaml
id: lhs:conn.000001
type: connection
source: lhs:phys.force
relation: causes
target: lhs:phys.acceleration

assertion:
  status: active            # active|deprecated|superseded
  type: proposed            # proposed|asserted|inferred
  polarity: positive        # positive|negative (NEW, default positive)
  review: {status: unreviewed} # unreviewed|reviewed|canonical
  confidence: null
  confidence_basis: null

lifecycle:                  # NEW, optional
  reason: null
  replaced_by: null         # lhs:conn.* if superseded

context:
  domain: physics
  subdomain: mechanics
  regime: [classical]       # controlled multi-valued
  scale: macroscopic
  qualifiers: []            # NEW extensible [{type, value, unit}]
  assumptions: []

evidence:                   # existing, reworked
  - type: textbook          # expanded controlled vocab (NEW values)
    stance: supports        # NEW: supports|weakly_supports|contradicts|qualifies
    source_ref: lhs:src.halliday-resnick
    locator: "Ch. 5"        # keep free-text for compat
    locator_struct:         # NEW structured
      page: null
      section: "5.1"
      equation: "5.1"
    description: "..."

provenance:
  asserted_by: {type: human, id: human:reviewer.physics-001}
  generated_by: {type: process, id: process:migration.relationships-v0.2}
  reviewed_by: []
  method: {type: manual}
  review_history: []        # existing, add evidence_considered optional

created_at: 2026-08-30T00:00:00+00:00   # NEW
updated_at: 2026-08-30T00:00:00+00:00   # NEW
validity: null               # NEW optional {valid_from, valid_until}

integrity:                   # NEW derived, not authored
  claim_signature: sha256(source|relation|target|polarity)
  content_hash: sha256(canonical fields)

rights: null                 # NEW optional {license, attribution}
```

### Source (additive)
```yaml
id: lhs:src.halliday-resnick
type: textbook
citation: "Halliday..."
title: "Fundamentals of Physics"      # NEW optional
authors: ["Halliday", "Resnick"]       # NEW
year: 2020                              # NEW
publisher: Wiley                        # NEW
doi: null
url: null
isbn: null
edition: "12th"
language: en                            # NEW (defer multilingual but field exists)
license: null
source_role: primary                    # NEW optional primary|secondary|aggregator|retrieval
rights: null
```

### Entity (additive)
```yaml
id: lhs:phys.force
type: concept
# existing fields...
updated_at: 2026-08-30T00:00:00+00:00   # NEW
version: 1                              # NEW
external_ids: {}                        # NEW optional
rights: null                            # NEW
```

## Derived vs Canonical
- `claim_signature`, `content_hash`, `inverse`, `transitive_closure`, `centrality` — **derived** (in `exports/knowledge.extended.json`, not in `connections/`).
- All new urgent fields above are **canonical authored** (except integrity hashes).

## Migration Policy (Part VI)
- Existing 397 objects: add `polarity: positive` (default), `created_at/updated_at` = file mtime or `generated_at` if unavailable (explicit `not_recorded` not needed — use actual file time), `lifecycle` null, `evidence[].stance: supports` default, `rights` null, `validity` null.
- Preserve IDs, provenance, review_history, origin.
- Do not fabricate timestamps/authors/evidence where missing — use deterministic file mtime or `null` with reason.

## Validator Extensions (Part VIII)
- Polarity `positive|negative` (default positive)
- Timestamps ISO8601, `valid_until >= valid_from`
- `claim_signature` uniqueness warning (duplicate triple+polarity)
- `lifecycle.replaced_by` resolves, not self
- `review_history` ordered by `at`
- Controlled vocabs: `evidence.type` expanded, `stance` enum, `source_role`
- `rights.license` free-text but validated non-empty if present
- Warnings for incomplete but not invalid (e.g., canonical without DOI)

## Urgency Implementation Order (Part V)
1. Urgent: polarity, timestamps, source bibliographic, evidence type+stance, locator_struct, qualifiers, lifecycle, claim_signature (derived), rights (optional), entity updated_at/version — **implement now** (additive, keeps schema_version 0.2, export_version 0.1)
2. Important: review_history evidence_considered, source_role, external_ids — defer to v0.2.x
3. Defer: proposition ID, statistics, language, assumption ontology

## Table: Field | Object | Meaning | Owner | Required? | Controlled? | Canonical/Derived | Phase
| Field | Object | Meaning | Owner | Required | Controlled | C/D | Phase |
|-------|--------|---------|-------|----------|------------|-----|-------|
| `polarity` | connection | positive/negative claim | assertion | no (default positive) | yes | C | urgent |
| `created_at, updated_at` | entity/connection/source | lifecycle timestamps | lifecycle | yes for new, null for migrated (file mtime) | no (ISO8601) | C | urgent |
| `validity{valid_from,valid_until}` | connection | scientific validity period | context | no | no | C | urgent |
| `evidence.type` expanded | evidence | precise category | evidence | yes | yes | C | urgent |
| `evidence.stance` | evidence | supports/contradicts | evidence | no (default supports) | yes | C | urgent |
| `locator_struct` | evidence | structured page/section/equation | evidence | no | no | C | urgent |
| `context.qualifiers` | connection | extensible conditions | context | no | yes (type) | C | urgent |
| `lifecycle{reason,replaced_by}` | connection | deprecation target | lifecycle | no | no | C | urgent |
| `claim_signature` | integrity | hash(source|relation|target|polarity) | integrity | no | no | D | urgent |
| `rights{license}` | source/entity | rights/license | rights | no | no | C | urgent |
| `updated_at, version` | entity | revision | lifecycle | no | no | C | urgent |
| `title, authors, year, DOI, etc.` | source | bibliographic | source | no | no | C | urgent |
