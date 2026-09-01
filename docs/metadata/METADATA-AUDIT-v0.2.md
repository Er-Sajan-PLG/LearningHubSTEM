# Metadata Audit — v0.2

**Scope:** Inventory of actual repository metadata vs mature association/provenance practice (Biolink, PROV, RDF 1.2). No wholesale ontology copy.

## Part I — Inventory (inspected actual files)

### Entity (`content/**/*.md` frontmatter, 128 entities)
| Field | Present | Notes |
|-------|---------|-------|
| `id` | yes | `lhs:<domain>.<slug>`, stable, validated |
| `type` | yes | `concept,quantity,unit,law,equation,misconception,phenomenon,model` |
| `name` | yes | canonical label |
| `domain` | yes | physics/chemistry/biology/earth-space/engineering/scientific-practice |
| `status` | yes | draft/machine_validated/human_reviewed/canonical/deprecated/superseded |
| `definition` | yes | curriculum-agnostic |
| `aliases`, `deprecated_by` | partial | present but rarely used |
| `examples, equation, symbol, unit, common_misconceptions, learning_objectives, real_world_applications, key_experiments` | yes | optional knowledge-layer |
| `provenance {ai_drafted, source_kind, source, reviewer, reviewed_at}` | yes | thin |
| `relationships[]` | yes | legacy compatibility; canonical is `connections/` |
| `created_at, updated_at, version, external_ids, language, license` | **missing** | No timestamps/version/external mapping |
| `subdomain` | derived | From path, not frontmatter |

### Connection (`connections/lhs:conn.*.yaml`, 397)
| Field | Present | Notes |
|-------|---------|-------|
| `id` | yes | `lhs:conn.000001` sequential opaque |
| `type` | yes | `connection` |
| `source, relation, target` | yes | relation validated vs registry (55 relations, 11 families) |
| `assertion {status, type, review{status}, confidence, confidence_basis}` | yes | `status active/deprecated/superseded`, `type proposed/asserted/inferred`, `review unreviewed/reviewed/canonical` |
| `context {domain,subdomain,regime[],scale,assumptions}` | partial | regime multi-valued controlled, scale/assumptions text |
| `evidence[] {type, source_ref, locator, description}` | partial | `type` enum 6 values, `source_ref` resolves to `sources/` |
| `provenance {asserted_by, generated_by, reviewed_by[], method, review_history[]}` | yes | `human/llm/process/unknown`, `method manual/llm_inference/migration` |
| `inference {rule,path}` | partial | only when `type inferred` |
| `polarity/negated` | **missing** | No positive/negative distinction |
| `created_at, updated_at` | **missing** | No lifecycle timestamps |
| `valid_from/valid_until` | **missing** | No validity period |
| `claim_signature` | **missing** | No deterministic duplicate detection (derived) |
| `content_hash` | **missing** | No integrity fingerprint |
| `lifecycle {reason, replaced_by}` | **missing** | No deprecation target |
| `language, rights/license` | **missing** | No rights metadata |
| `qualifiers` beyond context | **missing** | No extensible qualifier array |

### Source (`sources/lhs:src.*.yaml`, 3)
| Field | Present | Notes |
|-------|---------|-------|
| `id, type, citation, locator_authority` | yes | `type textbook/academic-paper/standard/institutional/other` |
| `authors, year, title, publisher, journal, DOI, URL, ISBN, edition, language, license, version, accessed_at` | **missing** | Thin bibliographic |
| `source_role (primary/aggregator/retrieval)` | **missing** | No lineage distinction |

### Evidence (inside connection)
- `type` enum coarse (6 values); no `stance` (supports/contradicts); no `quality` (direct/indirect); `locator` free-text only.

### Export (`exports/knowledge.json`)
- `schema_version 0.2, export_version 0.1, generated_at, entity_count, connection_count, source_count, entities[], connections[], sources[], relation_registry` — canonical trusted/reviewed filtered via `graph_policy`.

### Provenance Activity
- Distinguishes `asserted_by` (who), `generated_by` (process), `method` (how), `reviewed_by` (who reviewed), `review_history` (when/reason) — but no distinct `activity` with `started_at/ended_at/used/generated`.

## Summary
- **Present:** Stable IDs, typed relations, families, evidence/provenance/review/context separation, derived graph isolation.
- **Partial:** Source bibliographic, evidence typing, context qualifiers.
- **Missing:** Polarity, lifecycle timestamps, validity, claim signature, content hash, lifecycle reason, rights, external IDs, structured locators, stance, language.
