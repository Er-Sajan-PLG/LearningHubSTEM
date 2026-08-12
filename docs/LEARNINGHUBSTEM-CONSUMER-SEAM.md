# LearningHubSTEM ↔ STEM-TUITION — Consumer Seam (Phase 2)

> **Consumer proof, not a platform.** LearningHubSTEM publishes a versioned export. STEM-TUITION
> consumes it through one adapter. One direction. Nothing else.

## The pipeline

```
LearningHubSTEM canonical files  (content/*.md — YAML frontmatter)
        │  python3 LearningHubSTEM/scripts/validate.py
        ▼
  exports/knowledge.json         (DERIVED — regenerable, never edited by hand)
        │  import (build/test/dev time)
        ▼
  apps/shell/src/lib/lhs-adapter.ts   (STEM-TUITION consumer boundary)
        │
        ▼
  apps/shell/src/lib/lhs-demo.ts  →  index.html #lhs-demo
```

## Export contract

- **File:** `LearningHubSTEM/exports/knowledge.json`, contract **`export_version: 0.1`**,
  schema **`schema_version: 0.1`**.
- **Shape:** top-level `export_version`, `schema_version`, `generated_at`, `source`,
  `entity_count`, and `entities[]`. Each entity carries `id`, `type`, `name`, `domain`,
  `status`, `definition`, optional `symbol` / `unit` / `equation` / `common_misconceptions`,
  `provenance`, `relationships[]`.
- **Versioning:** a consumer may state "I consume export contract version X". Breaking changes to
  the shape bump `export_version`. Content edits are a content release and do **not** bump the
  contract. (Specification §10, decision 0008.)
- **Validation:** the validator rejects dangling relationship targets and enforces the entity and
  relationship vocabularies before the export is written. A consumer never needs to handle a
  dangling target in practice — but the adapter throws rather than silently skipping if one
  appears (defense in depth).

## Adapter location and API

- **`apps/shell/src/lib/lhs-adapter.ts`** — the only file that imports across the seam.
- **`apps/shell/src/lib/lhs-types.ts`** — LHS types, kept separate from STEM-TUITION models.
- API: `loadKnowledge()` (validates the contract version and indexes entities),
  `getEntity(id)`, `getRelatedEntities(id)`.
- **Version enforcement:** `loadKnowledge()` rejects any `export_version !== "0.1"` with
  `LhsUnsupportedVersionError` (message includes found and supported versions). Lookups fail with
  `LhsEntityNotFoundError` / `LhsDanglingReferenceError` — never silently.

## Ownership

| Concern | Owner |
|---------|-------|
| What things mean (`definition`, `equation`, `symbol`, `unit`, relationships) | **LearningHubSTEM** (`content/`) |
| Common false beliefs (knowledge layer) | **LearningHubSTEM** (`common_misconceptions`) |
| Worked examples, questions, explanations, sequence | **STEM-TUITION** (`apps/shell/src/lib/lhs-demo.ts`) |
| The adapter and LHS types | **STEM-TUITION** (consumer) |
| The export file | **derived** — owned by the validator, regenerated from `content/` |

## Canonical vs derived vs pedagogical

- **Canonical:** `LearningHubSTEM/content/*.md`. Source of truth. Never generated.
- **Derived:** `LearningHubSTEM/exports/knowledge.json`. Regenerable from canonical; never
  authoritative and never hand-edited.
- **Pedagogical:** anything that teaches (worked examples, questions, ordering). Lives in the
  consumer. The boundary is kept legible in the demo UI: sections labeled
  *KNOWLEDGE — imported from LearningHubSTEM* vs *LEARNING — authored by STEM-TUITION*.

## How to regenerate the export

```bash
python3 LearningHubSTEM/scripts/validate.py        # from workspace root
# or:  cd LearningHubSTEM && python3 scripts/validate.py
```

Exit `0` writes a fresh `exports/knowledge.json`; exit `1` prints validation errors and writes
nothing. Regeneration is reflected by the consumer automatically (the adapter imports the file;
re-run tests/build to pick it up).

## How to run the demo and tests

```bash
# Consumer unit tests (includes the LHS adapter + demo slices)
pnpm --filter @stem-tuition/shell test

# Type-check the consumer (note: pre-existing acl breakage in cosmic-background.ts,
# unrelated to this seam, currently fails this step)
pnpm --filter @stem-tuition/shell typecheck

# Lint that covers the new files
pnpm lint:state && pnpm lint:dom && pnpm lint:arch && pnpm lint:circular

# View the demo
pnpm --filter @stem-tuition/shell dev        # http://localhost:5173/#lhs-demo
```

## Deferred for Phase 3

- Full MVP activation of LearningHubSTEM (content authoring, review workflow, multilingual).
- Additional consumer adapters (JARVIS, STEM-GAME, future products) — this seam is the template.
- A second vertical slice (more laws, quantities, equations) in the STEM-TUITION UI.
- Real export piping (published artifact / package) instead of a direct file import.
- Schema/export version bumping policy when a second contract version exists.
- License files for both repos (human decision pending).
