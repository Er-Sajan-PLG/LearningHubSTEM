# Relationship-Model Coexistence — Settled by ADR-0011 (documentation)

**Status:** Investigation complete. **Not a new decision** — [ADR-0011 — Connection as
first-class canonical assertion](../docs/decisions/0011-connection-assertion-model.md) already
settles the relationship-model question. This document records the ground truth and how the
Q1/Q2 work implements it.

---

## 1. The governing decision (ADR-0011)

> **First-class `connections/` are the single source of truth for relationships.**
> Inline `entity.relationships[]` is retained as a **compatibility projection** regenerated
> from canonical `connections/` — it is NOT a second, independent truth.

Key ADR-0011 lines (verified):
- *"Legacy `relationships[]` = derived compatibility; single source of truth is `connections/`."*
- *"Entity's `relationships[]` is retained during v0.2 as a compatibility projection regenerated
   from canonical `connections/` (not a second truth)."*
- The migration tool (`scripts/migrate_relationships.py`) converts legacy inline relationships
  to first-class connections while keeping `relationships[]` for backward compatibility.

This is the pre-existing architectural ruling — no new decision is required.

## 2. What Q2 did to implement it

- `scripts/validate.py` now **validates first-class connections** (schema conformance, relation
  registry conformance incl. domain/range, source/target resolution, evidence→source resolution,
  provenance presence, extension membership) and **includes `connections` + `sources` in the
  derived export**. The relation source of truth is now enforced and consumable.
- The gate now covers content/ + connections/ + sources/ (was content-only).

## 3. Curated ground truth (current state)

- **641** inline relationships across 224 entities.
- **654** first-class connections.
- Pairwise overlap: **637** entity-pairs present in both inline and connections; **0** pairs only
  in inline; **6** pairs only in connections (a small projection-sync gap — connections ahead of
  the inline compatibility projection).

This confirms the ADR model: inline `relationships[]` is derived from `connections/` (nothing is
only-inline), with a minor 6-pair projection lag.

## 4. Residual (does not change the model)

- **Projection sync:** the inline `relationships[]` mirror should be regenerated from canonical
  connections so the compatibility projection is exactly current (bring the 6 only-in-connections
  pairs into the inline mirror). This is a data-sync task, not a model change.
- **Deprecation timing:** ADR-0011 keeps `relationships[]` as a compatibility projection for
  backward compatibility. Its eventual removal is a consumer-migration decision (consumers that
  read `entities[].relationships` would need to read `connections` instead). This is governed and
  out of scope for this phase.

## 5. Consumers of each model

| Consumer | Reads |
|----------|-------|
| `content/*.md` inline `relationships[]` | legacy consumers (backward-compat projection) |
| `exports/knowledge.json` `connections[]` | NEW (this phase) — the canonical relation source |
| STEM-TUITION `lhs-adapter.ts` `getRelatedEntities` | reads `entities[].relationships` today; should migrate to `connections` when ready (follow-up) |
| `explorer` graph | builds graph; can use `connections[]` now (they are exported) |

## 6. Recommendation / follow-up

1. Treat `connections/` as canonical (done by ADR-0011 + this phase's validation).
2. Add a projection-sync step so `entities[].relationships` mirrors connections exactly (or
   stop emitting inline and migrate consumers — a governed consumer-facing decision).
3. Future: consider a decision record to deprecate inline `relationships[]` once all consumers
   read `connections[]`.

The relationship model is **not** duplicated in a way that compromises canonicality — the
coexistence is the ADR-sanctioned projection pattern, now enforced by the validator.