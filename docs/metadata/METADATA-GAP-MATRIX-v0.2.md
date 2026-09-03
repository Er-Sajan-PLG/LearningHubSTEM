# Metadata Gap Matrix — v0.2

Assessment against Biolink, PROV, RDF 1.2, assertion/evidence practice.

| ID | Dimension | STEMMA Status | Assessment | Urgency |
|----|-----------|------------|------------|---------|
| M1 | Proposition vs assertion identity | `connection.id` identifies assertion record; no separate proposition ID | Defensible for v0.2; proposition is `source+relation+target` triple; derived claim_signature sufficient. **Do not create second object.** | **DEFER** |
| M2 | Negation/polarity | missing | `rejected/contradicts` not equivalent to "A does not cause B". Need `assertion.polarity: positive|negative` (default positive). Urgent for public trust (avoid implying affirmation). | **URGENT** |
| M3 | Temporal — created/updated/review/source pub/validity | partially present (`review_history.at` only) | Need `entity.updated_at`, `connection.created_at/updated_at`, `source.year/publication_date`, optional `validity{valid_from,valid_until}`. Keep repository lifecycle vs provenance activity vs scientific validity separate. | **URGENT** |
| M4 | Review history | present `review_history[{reviewer,decision,at,reason,from,to}]` | Add `evidence_considered` optional; do not duplicate whole assertion. Current shape sufficient with one addition. | **IMPORTANT** |
| M5 | Provenance activity (who/what/when/using/from/producing) | partial (`asserted_by, generated_by, method, reviewed_by, review_history`) | Keep PROV distinction: entity/activity/agent. Add `activity {started_at, ended_at}` only if needed; current `review_history.at` + `method` covers v0.2. | **IMPORTANT** |
| M6 | Source bibliographic | thin (`citation` only) | Add optional `title, authors[], year, publisher, journal, volume, DOI, URL, ISBN, edition, language` — keep `sources/` canonical, connections use `source_ref`. | **URGENT** |
| M7 | Primary vs aggregator/retrieval | missing | Add optional `source_role: primary|secondary|aggregator|retrieval` — important for public release but can defer if aggregator not yet used. | **IMPORTANT** |
| M8 | Evidence type granularity | coarse (6) | Expand to `definition, axiom, mathematical_derivation, empirical_measurement, experiment, observation, simulation, review, textbook, standard, dataset, expert_assessment` — controlled, compact. | **URGENT** |
| M9 | Evidence stance | missing | Add `evidence[].stance: supports|weakly_supports|contradicts|qualifies` (default `supports`). Separate evidence existence from direction. Urgent for disputed claims. | **URGENT** |
| M10 | Evidence quality/directness | missing | Defer categorical `direct|indirect|derived|contextual`; can infer from type+stance for v0.2. | **DEFER** |
| M11 | Locator structure | free-text `locator` | Add optional structured `locator {page, section, equation, figure, table, dataset, code, url_fragment}` + keep free-text `locator` for backward compat. | **URGENT** |
| M12 | Context qualifiers | partial (`domain/subdomain/regime/scale/assumptions`) | Add extensible `context.qualifiers[] {type, value, unit}` for conditions/scope/system/boundary (temperature, pressure, etc.); keep domain/subdomain/regime controlled. | **URGENT** |
| M13 | Assumptions qualified | plain strings | Keep plain text for v0.2; evolution path to `lhs:assumption.*` stable refs (defer ontology). | **DEFER** |
| M14 | Relation qualifiers | missing (instance-level degree/mechanism/role) | Defer; current `context` + future `qualifiers` covers v0.2. Keep registry metadata separate from instance qualifiers. | **DEFER** |
| M15 | Confidence model | present `confidence + basis` | Keep single confidence + `confidence_basis`; do not add multiple 0-1 scores. Sufficient. | **KEEP** |
| M16 | Statistical evidence | missing | Defer — document extension pattern `evidence.statistics{p_value,effect_size,sample_size}` for future; not urgent for 50 canonical (no stats-backed yet). | **DEFER** |
| M17 | Review vs epistemic status | present (`assertion.type` vs `review.status`) | Keep orthogonal dimensions; `rejected≠disputed≠deprecated≠superseded`; defer `disputed`/`superseded` until needed. | **KEEP** |
| M18 | Object version/revision | missing | Add optional `version: 1`, `updated_at` for entities/connections/sources; content version via `review_history`. Important for public release. | **IMPORTANT** |
| M19 | Lifecycle targets | missing (`replaced_by`) | Add `assertion.lifecycle{reason, replaced_by}` for `deprecated/superseded`; validate no self-reference/dangling. Urgent for public release. | **URGENT** |
| M20 | Claim signature | missing | Add **derived** `integrity.claim_signature = hash(source|relation|target|polarity|qualifiers)` for duplicate/conflict detection; canonical remains `connection.id`. | **URGENT** |
| M21 | Content hash | missing | Add **derived** `integrity.content_hash` (hash of canonical fields, excluding `generated_at`); not semantic identity. | **ADDITION** |
| M22 | Language | missing | English-only by policy for v0.2; defer `language` field. | **DEFER** |
| M23 | License/rights | missing | Add `rights {license, attribution, rights_holder}` optional for sources/entities; important for public release. | **URGENT** |
| M24 | External IDs | missing | Add optional `external_ids {doi,isbn,standard_id}` for sources/entities; use `maps_to` not `same_as` for equivalence. | **IMPORTANT** |
| M25 | Entity metadata | partial | Add `updated_at, version, external_ids, rights` to entity; keep human-readable. | **URGENT** (subset) |
| M26 | Normalization | some duplication | Owner table: `source` owns bibliographic, `evidence` owns stance/locator, `provenance` owns who/when/how, `review_history` owns decision trail; avoid duplication. | **REWORK** (documentation) |

## Urgency Summary (Part IV)
- **URGENT (before public release / trusted corpus):** M2 polarity, M3 timestamps+validity, M6 source bibliographic, M8 evidence type, M9 stance, M11 locator, M12 qualifiers, M19 lifecycle, M20 claim signature, M23 license, M25 entity updated_at/version/rights (subset) — 11 dimensions.
- **IMPORTANT:** M4 review evidence_considered, M5 activity timestamps, M7 source role, M18 version, M24 external IDs.
- **KEEP:** M15 confidence, M17 review/type separation.
- **DEFER/REJECT:** M1 proposition ID, M10 quality, M13 assumption ontology, M14 relation qualifiers, M16 statistics, M22 language, M21 content hash (addition).
