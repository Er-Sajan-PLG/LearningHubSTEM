# LearningHubSTEM — Final Architecture Review & Canonical-Knowledge Agent Pipeline

**Version:** 0.3 (review)
**Status:** Architecture review — **defines the target; does not implement.**

This document inspects the actual LearningHubSTEM (LHSTEM) repository, evaluates its
existing decisions against the canonical-knowledge north star, and specifies the architecture —
**including a canonical-knowledge agent/curation pipeline** — that LHSTEM should adopt.

It honors the boundary this workstream repeatedly reinforces:

> **LHSTEM answers "what is the canonical STEM knowledge?"** — it generates neither stories,
> lessons, textbooks, animations, nor pedagogy. STEM-TUITION transforms knowledge into
> learning experiences; its *narration/story* pipeline is consumer-side and is **not** imported.

The agent system specified here is therefore a **curation, validation, and governance pipeline
over canonical knowledge** — the analog of STEM-TUITION's *content engine* (hard-gate pipeline,
targeted repair, LLM-agnostic seams), explicitly **not** the analog of its narration assembly
line (researcher → writer → reviewer → master-reviewer), which produces stories and is out of
scope for a canonical substrate.

---

## 0. How to read this review

Each section maps to the review brief. Every claim about current state was verified against the
repository on disk (files, schemas, scripts, tests, reports), not assumed. Where uncertain it is
flagged `[UNCERTAIN]`. Each problem is rated by **S**everity (0=cosmetic … 5=foundational) and
whether fixing it is **breaking** for consumers.

---

## A. Current-state assessment (what exists and how it actually works)

### A.1 Repository shape

```
LearningHubSTEM/
├── content/                        CANONICAL — 224 Markdown files, YAML frontmatter + prose
│   ├── physics, chemistry, biology, earth-space, engineering, math, scientific-practice/
├── connections/                    CANONICAL — 654 first-class relation assertions (lhs:conn.NNNNNN.yaml)
├── sources/                        CANONICAL — 3 citation objects (lhs:src.*.yaml)
├── schema/
│   ├── concept.schema.json          entity schema v0.2
│   ├── connection.schema.json       connection/assertion schema v0.2
│   ├── source.schema.json           source schema
│   ├── relation-registry.yaml       50 relations, 11 families, transitivity/domain/range
│   ├── extension-registry.yaml       adaptive metadata seam (ADR-0017)
│   └── vocabularies/                domains, subdomains, regimes (controlled terms)
├── scripts/                         22 scripts (~2,800 LOC)
├── tests/                           phase-b (semantic invariants), curation, metadata
├── reports/                         27 deterministic analysis reports (v0.2)
├── exports/knowledge.json           DERIVED export — entities only, NO connections
├── explorer/                        3D knowledge-graph consumer visual
├── docs/                            spec, governance, northstar, consumer-seam, 18 ADRs
├── .github/workflows/ci.yml         CI
├── LICENSE (CC BY 4.0) + LICENSE-CODE (MIT)
└── AGENTS.md, VERSION, opencode.json
```

### A.2 The canonical pipeline as it actually runs today

```
content/*.md  →  scripts/validate.py  →  exports/knowledge.json  (entities only)
                    │ (schema conformance, ID uniqueness, dangling targets,
                    │  applies_to/appears_in_law rules, extensions registry,
                    │  historical attribution, filename↔slug)
                    └─ copies same export into explorer/public/exports/ (auto-sync)
```

- `validate.py` is the **only** CI-enforced gate (`.github/workflows/ci.yml`: "Run validator
  (content + connections + sources)" — but it reads **only** `content/*.md`). It exits 0 and
  regenerates the export when valid; exits 1 without writing otherwise.
- `verify_all.py` runs a **9-step local hook chain**: validate → epistemic_summary →
  integrity_anomalies → graph_analysis → export_review_aware → curation_status → three test
  suites. This is the ECC-style verify hook the repo already built.
- Semantic/relation invariants (provenance shapes, inference legality, transitivity
  guardrails, `related_to` not auto-upgraded) live in `tests/phase-b/` and are **not** run by CI
  — only by `verify_all.py` locally.

### A.3 Two relation models coexist

1. **Inline** `entity.relationships[]` — v0.1 model, still in `concept.schema.json`, still exported.
2. **First-class connections** `connections/*.yaml` — ADR-011 v0.2 model: qualified assertions
   (status/type/polarity/confidence/evidence/provenance/lifecycle/context). The richer model LHS
   adopted, but **not yet wired into the validator or the export**.

### A.4 Maturity vs. the roadmap's "SEED ONLY" label

Far more built-out than "SEED ONLY (minimal proof)" suggests: spec v0.1, 18 ADRs, two v0.2
schemas, 50-relation registry, 224 entities, 654 connections, 22 scripts, 27 reports. The gap
between implemented sophistication and the declared status is itself a thing to reconcile (C.9).

---

## B. Architectural strengths (preserve)

| # | Strength | Why it matters |
|---|----------|----------------|
| B.1 | **Canonical = Markdown + YAML frontmatter** | Human-readable, diffable, DB-free, independent of any product/DB/language. KEEP. |
| B.2 | **North-star boundary (Knowledge ≠ Curriculum ≠ Pedagogy ≠ Product)** | Level-1 invariants make the central discipline enforceable-by-document. KEEP. |
| B.3 | **Stable-ID discipline** (never reused, `deprecated_by`, `aliases`) | Backbone of reproducibility and downstream trust. KEEP. |
| B.4 | **First-class connection model** (ADR-011, connection.schema.json) | Correctly separates assertion from endpoints; carries qualified metadata. The right substrate. KEEP (finish wiring — C.1). |
| B.5 | **Relation registry with family/transitivity/domain/range** | Turns relationships into governed, typed, queryable knowledge. KEEP. |
| B.6 | **Canonical vs. derived + regeneration principle** | Exports/indexes regenerable, never authoritative. KEEP. |
| B.7 | **Three-track versioning** (schema/export/content) | Keeps contract consumption independent of content churn. KEEP. |
| B.8 | **Provenance vs. scientific history separation** (provenance = record source; `historical` = who first stated, ADR-0018) | Correct split of "where did the text come from" vs "who discovered the science". KEEP. |
| B.9 | **Extension registry** (ADR-0017) | Open metadata seam that remains validated. KEEP. |
| B.10 | **Consumer-seam discipline** (versioned export + one adapter) | LHSTEM stays consumer-agnostic. KEEP. |
| B.11 | **Governance freeze + enforcement direction** (prose → schema → validation → tests → CI) | Governs schema/relation/ID change. KEEP. |

---

## C. Problems and risks (prioritized)

Severity **S** = 0 (cosmetic) … 5 (foundational). **Breaking** = consumer-visible.

### C.1 — [S5][foundational][NOT breaking to add, breaking-core once relied upon]
**The connection model is not wired into the validator or the export.**
`connection.schema.json` (cross:S5) defines
a rich assertion model, and 654 files exist in `connections/`, but `validate.py` reads **only**
`content/*.md` (grep confirms zero references to `connections`/`sources` in validate.py). The CI
workflow's step says it validates "content + connections + sources" — **it does not**. And
`exports/knowledge.json` contains only `entities`, **never connections or sources**. So the
richest knowledge layer is both unenforced by the gate and invisible to consumers.

1. Why it is a problem: malformed/invalid connections pass CI; consumers cannot get relationship
   assertions from the canonical export, so the first-class relation model is effectively dead.
2. Worth fixing: **yes** — this is the central gap.
3. Smallest safe correction: extend `validate.py` (or add `validate_connections.py` invoked by
   it and by CI) to load `connections/*.yaml` + `sources/*.yaml`, validate against their schemas,
   enforce relation-registry domain/range and source_ref resolution, and append a `connections`
   and `sources` array to the export **behind the existing `export_version` contract** (bump only
   when the shape change is breaking).
4. Breaking: adding new top-level keys is additive; consumers pinning `export_version:"0.1"`
   would need a bump **only if** we make connections part of the core contract. Recommend bumping
   `export_version` to `0.2` with the connection addition, and updating the adapter seam
   accordingly.

### C.2 — [S4][high]
**Version drift between the schemas' v0.2 self-description and the export's v0.1.**
The schemas declare v0.2; `validate.py` writes `schema_version`/`export_version` = `0.1`. The
consumer seam (`lhs-adapter.ts`) hard-requires `export_version === "0.1"`. The metadata design
doc says "additive to v0.2, still export_version 0.1". This inconsistency makes "which version
did I consume" ambiguous.
1. Worth fixing: yes, low effort, high clarity.
2. Smallest fix: define one authoritative `export_version` constant, bump once (see C.1), and make
   the adapter read it from the export header rather than a magic literal.
3. Breaking: yes for the adapter if it hard-codes "0.1" (it does) — coordinate with C.1.

### C.3 — [S4][high]
**Two relation models coexist with no declared deprecation path.**
Inline `relationships[]` and first-class connections both carry relation statements. Nothing says
which is authoritative, whether inline is legacy, or how a consumer reconciles both (they can
double-report the same edge). This risks duplicated/contradictory canonical knowledge (a key smell).
1. Worth fixing: yes. Decide and document the migration (recommend: **connections become the
   canonical relation source; inline `relationships[]` are deprecated for new entries and
   eventually removed**, with a migration script `migrate_relationships.py` already present).
2. Smallest safe correction: a decision record (ADR) stating the deprecation + a validator rule
   that new entities do **not** add inline relationships.
3. Breaking: yes if we remove inline from the export; phase it (deprecate → migrate → remove).

### C.4 — [S4][high]
**CI gate and the local verify chain are disconnected.**
The only CI-visible check is a single `validate.py` run. `verify_all.py` (which runs the 9-step
chain incl. the semantic phase-b tests) is not in CI. So a change that breaks provenance shapes,
inference legality, or relation transitivity guardrails can merge if validate.py still exits 0.
1. Worth fixing: yes. The repo already declares "enforcement direction: prose → schema →
   validation → tests → CI". The tests exist; CI just doesn't run them.
2. Smallest safe correction: add a CI job running `verify_all.py` (or its deterministic subset)
   on main/PR; keep it fast.
3. Breaking: no (additive CI step).

### C.5 — [S3][medium]
**`tests/phase-b/test_phase_b.py::test_idempotence` asserts a stale connection count (397).**
The repo now has 654 connections; the test's `migrate_relationships.py` / `create_curated_b3_b6.py`
assertions ("skipped 384"/"skipped 376") are stale and fail. This is a test-that-validates-
implementation-detail smell (the invariant is "regeneration is idempotent", not a magic count).
1. Worth fixing: yes — it currently fails `verify_all.py`.
2. Smallest fix: assert idempotence (re-running changes nothing) rather than a hardcoded count.
3. Breaking: no.

### C.6 — [S3][medium]
**`schema/extension-registry.yaml` has three duplicate `version:` keys (lines 20/22/24).**
Probably the product of an idempotent writer re-inserting the header. Both a maintainability and
a potential parser-behavior smell.
1. Worth fixing: yes, trivial.
2. Smallest fix: collapse to one `version:` key; keep `register_extension.py` idempotent but
   not re-duplicating.
3. Breaking: no.

### C.7 — [S3][medium]
**Provenance model drift between the schema and the actual connection files.**
`connection.schema.json` `asserted_by.type` enum is `human|llm|process|unknown`; migrated
connections use values like `unknown:legacy-relationship` and `process:migration.relationships-v0.2`
(which are *id* strings, not allowed *type* values). The schema-vs-data mismatch means either the
schema is too strict or the migration didn't conform. This is metadata/identity conflation.
1. Worth fixing: yes — provenance is a core claim. Fix the migration or relax the schema
   deliberately (per ADR).
2. Smallest safe fix: decide the intended shape (I recommend keeping the enum strict and fixing
   the migrated ids to `type: process` / `type: unknown`), then reconcile via a script.
3. Breaking: no for consumers (provenance is internal-ish, though exported).

### C.8 — [S2][medium]
**`docs/grade12-curriculum-mapping.md` is correctly consumer-owned, but lives in the canonical**
**repo's docs/.** It is explicitly labeled "consumer-owned reference mapping (NOT canonical
content)" and references canonical IDs — architecturally correct boundary. The only question is
whether it belongs in LHSTEM docs at all vs. staying as a consumer-side example. This is a
documentation-hygiene item, not an architectural violation. **Worth keeping** (it documents how a
consumer maps), but move under `docs/integrations/` or mark it a canonical example of the seam.

### C.9 — [S2][low]  [reconcile]
**Declared status ("SEED ONLY") lags implemented sophistication.** The roadmap still says "full
MVP inactive until 'ACTIVATE LEARNINGHUBSTEM MVP'". Either the status should be updated to reflect
foundation+phase-curation reality, or activation is genuinely pending. This is a governance/
communication alignment item.

### C.10 — [S1][low]
**`explorer/` is a consumer visual committed in the canonical repo.** It's the 3D graph consumer.
Precedent exists (skill: consumer-visualization-sync keeps it auto-synced from the validator).
Acceptable, but it is a consumer and should be treated as such (not part of the canonical model).

---

## D. Canonical knowledge definition (precise)

> **canonical** = a governed, stable, validated, source-traceable assertion of scientific
> meaning, independent of any curriculum, pedagogy, product, language, or year of teaching.

- **What makes an object canonical:** it lives in `content/` (entity) or `connections/`
  (assertion) or `sources/` (citation); passes schema + relationship validation; carries
  provenance (and, where relevant, `historical` attribution); and has attained an appropriate
  review status via a governed gate. Canonicality is **a governed property**, not a folder
  location — a file in the right folder that fails provenance or review is draft, not canonical.
- **What makes a source authoritative:** a governing decision + named reviewer, captured in
  `provenance.reviewer` / `reviewed_by`. Authority is human-governed, never algorithmic.
- **Who establishes canonical status:** the governance flow in section **O** — a human-gated
  release; AI proposes, humans decide.
- **Competing interpretations / disagreement:** represented as *multiple* assertions
  (`connection` objects) that may `contradict`/`competes_with`/`inconsistent_with`, each with
  evidence + confidence — not forced into a single binary truth. The `conflict` relation family
  exists for exactly this.
- **Uncertain claims:** `assertion.confidence` (0..1, null=unknown) + `confidence_basis`,
  and `assertion.type: proposed` for not-yet-accepted claims.
- **Obsolete / superseded claims:** `assertion.status: deprecated|superseded` + `lifecycle.
  replaced_by`; entities use `status: deprecated` + `deprecated_by`. Never silently deleted.
- **How historical versions are preserved:** git history + immutable IDs (`aliases`) +
  deprecated/`replaced_by` pointers. Do **not** invent a separate version store (over-engineering).
- **How downstream systems know the version they consumed:** the export header
  (`export_version`, `schema_version`, `generated_at`) + entity lifecycle status. Consumers
  record the header they ingested.
- **"trusted"** = passed the governed validation + human-review gates for its status.
- **"verified"** = machine- and/or human-verified *for a specific claim/status*; it never
  implies universal scientific truth.
- **canonical is NOT:** pedagogy, curriculum placement, a product's wording, a search result,
  an AI draft, or a fastest-path answer.

---

## E. Domain model (recommended core objects)

Starting from the **smallest coherent model** — do not add objects without need.

| Object | File | Responsibility | Fields (minimal) |
|--------|------|----------------|-------------------|
| **Entity** | `content/<domain>/<slug>.md` | A thing LHSTEM knows about: concept, quantity, unit, law, equation, misconception (existing six types — KEEP). | id, type, name, domain, status, definition, provenance, optional symbol/unit/equation, aliases, deprecated_by, historical |
| **Connection** | `connections/lhs:conn.NNNNNN.yaml` | A first-class assertion: source · relation · target + qualifiers. *(Make canonical relation source per C.3.)* | id, source, relation, target, assertion{status,type,polarity,confidence,review}, context, evidence[], provenance, lifecycle, validity, inference |
| **Source** | `sources/lhs:src.<slug>.yaml` | A citation object referenced by evidence.source_ref. Only 3 today; grows with provenance rigor (G.3). | id, type, title, authors, date, kind, location, access, rights |
| **Relations** | `schema/relation-registry.yaml` | The controlled relation vocabulary (semantics, family, transitivity, domain/range). | — |
| **Extension registry** | `schema/extension-registry.yaml` | Governed additive metadata dimensions. | — |
| **Curriculum mapping** | (consumer-owned) | Maps canonical IDs into a curriculum/grade — **never in `content/`**. | canonicalId, curriculumRef, sequence, depth |

**Explicitly NOT domain objects** (out of scope for a canonical substrate): stories, lessons,
animations, interactive activities, pedagogical sequences, tests-for-a-learner, teaching scripts,
motivational content, arbitrary AI explanations. (These are consumer artifacts, e.g. STEM-TUITION's
`narrative-lesson` format.)

**Uncertainty:** `[UNCERTAIN]` whether `phenomenon`, `model`, `experiment`, `substance`,
`material`, `process`, `mechanism` should become new entity types or remain tags/relations. The
relation registry already references `phenomenon`/`model` in domain/range, suggesting they are
types-in-intent but not yet in the entity `type` enum. **Recommendation:** keep the six entity
types for now and express `phenomenon`/`model` as either (a) new entity types added deliberately
via the governed freeze flow, or (b) typed via relationships. Decide with an ADR before adding —
do not expand silently. (See future-extensibility R.)

---

## F. Relationship model (recommended architecture)

**Preserve** the relation registry's design (family / inverse / symmetric / transitive /
domain / range) — it is already SOTA-class and not over-built. **Derive from it** the rules:

- **First-class connections are the canonical relation source** (C.3): an edge is a `connection`
  object, never an inline `relationships[]` entry (deprecate inline for new content).
- **Relationships carry context:** domain, subdomain, regime, scale, assumptions, qualifiers —
  already in `connection.context`. This is what keeps a relation meaningful across regimes
  (e.g. F=ma within classical regime; Newtonian vs relativistic).
- **Transitivity is governed, not assumed:** enforce the registry's flags in validation
  (C.1). `requires`/`part_of`/hierarchy are transitive; causal/conflict/model families are
  explicitly non-transitive (guardrails already encoded and tested).
- **Directionality is explicit:** every relation declares domain→range; inverses are derived
  (not stored) per the registry `inverse` field.
- **No uncontrolled free-for-all:** the registry is the whitelist; validation rejects unknown
  relation names and domain/range violations (C.1 wires this for connections).
- **Relationship families already present and appropriate:** structural, hierarchical,
  dependency, causal, explanatory, model, conflict, measurement, engineering, analogy,
  cross-domain, derivation, associative. This list is **derived from the registry**, not imposed.

**What consumers can rely on:** typed, directional, validated relations with resolvable targets,
filterable by domain/regime, and versioned through the connection lifecycle.

---

## G. Metadata / provenance model (clear separation)

The repo already separates these correctly; sharpen and enforce.

| Concern | Model | Coupling rule |
|---------|-------|----------------|
| **Knowledge** (the STEM meaning) | `definition`, `equation`, relation assertions | Never mutated by presentation or curriculum. |
| **Metadata** (describing knowledge) | `symbol`, `unit`, `common_misconceptions`, `learning_objectives`, `real_world_applications`, `key_experiments`, `extensions` | Knowledge-layer metadata allowed; **no grade/curriculum/product fields** in canonical objects. |
| **Provenance** (where it came from) | `provenance` (ai_drafted, source_kind, source, reviewer, reviewed_at) + evidence.source_ref → `sources/` | Required on every object; machine-checked. |
| **Context / conditions** (when a claim holds) | `connection.context` (regime, scale, assumptions, qualifiers) + `validity` | Kept on the assertion, not on the entity. |
| **Governance** (why it's accepted/superseded) | lifecycle status + `review_history` + ADRs | Driven by the O pipeline; recorded, auditable. |
| **Presentation** (how a consumer shows it) | consumer-side only | Never stored on canonical objects. |

**Provenance essentials (D/§10):** source identity, type, location, citation, author/org,
publication, access, claim→source link (evidence), confidence, verification state, conflicting
and updated sources, superseded sources. These map onto `provenance` + `evidence[]` +
`connection.assertion.confidence` + lifecycle. Enforce them deterministically (C.1/C.7).

---

## H. Curriculum model (must not become the ontology)

**Preserve** the invariant from NORTHSTAR: curriculum mappings are **consumer-owned** and never
in `content/`. The existing `docs/grade12-curriculum-mapping.md` is correctly labeled a
consumer-owned reference (C.8).

- A concept participates in many curricula/levels/subjects **without duplication** — one
  canonical ID shared across consumer mapping tables.
- **Knowledge order ≠ curriculum order:** `requires`/`logically_requires` are in the knowledge
  layer; sequencing/depth/grade targeting are consumer decisions.
- **No grade/curriculum tag is a canonical invariant.** A concept stays meaningful if a
  curriculum, country, or school system changes. (The `extensions` registry must reject any
  proposal that intends to add grade/curriculum tags to canonical objects — add a Guardrail.)

**Architectural rule:** if a change would store a curriculum/grade/course tag in `content/` or
`connections/`, it is **rejected by governance**, not merely discouraged.

---

## I. Validation architecture (deterministic vs. semantic vs. human)

Reproduce STEM-TUITION's separation of **deterministic gates vs. LLM/judgment gates**, applied
to a canonical knowledge substrate.

### I.1 Deterministic (LLM-free, must be enforced in CI)
- Schema conformance (`concept.schema.json`, `connection.schema.json`, `source.schema.json`).
- ID format + uniqueness + filename↔slug consistency.
- Relation-registry conformance: allowed names, domain/range, transitivity flags.
- Dangling targets (source/target resolve; evidence.source_ref resolves to a source).
- Extension-registry membership (no unregistered `extensions` key).
- Provenance presence + shape; historical attribution shape (ADR-0018).
- Lifecycle legality (forward-only transitions; `deprecated` has `deprecated_by` where required).
- Orphan detection, duplicate IDs, broken refs, manifest consistency.
- Idempotence of derived artifacts (regeneration is a pure function of canonical content).

### I.2 Semantic (needs judgment — can be LLM-assisted, never auto-canonical)
- Scientific correctness, conceptual consistency, internal contradiction between assertions.
- Source interpretation fidelity (does the entity mean what the source says).
- Misleading simplification / missing conditions / overgeneralization.
- Ambiguity analysis.

These are **proposals/review inputs**. They produce findings and review signals, never a direct
`canonical` promotion.

### I.3 Human (the final authority)
- Named `human:reviewer.*` accepts a draft → `human_reviewed`; a governance gate promotes →
  `canonical` (spec 8.2, ADR-0006). Records `review_history`.

> **Rule from the north star:** an LLM is never used where a deterministic validator suffices;
> deterministic validation never asserts scientific truth. The repo's existing phase-b tests are
> the semantic layer; wire them into CI (C.4).

---

## J. Versioning model

**Preserve** three-track versioning (spec §10) — do not build a package manager.

| Track | Identifier | Change rule |
|-------|-----------|--------------|
| **Schema** | `schema_version` | breaking field/type/enum change → major bump |
| **Export contract** | `export_version` | breaking shape semantics → major bump (and update consumer adapter) |
| **Content release** | (repository release / changelog) | any content add/edit/deprecation; never implies contract change |

Semantics: a consumer may state "I consume export contract X" and be unaffected by content
releases; **object identity is version-agnostic** (IDs never encode version). Historical versions
are preserved by git + immutable IDs + deprecated/replaced_by pointers. Migrations are governed
(freeze rule) and validated by migration tests.

**Recommendation (with C.1):** surface `schema_version`/`export_version` from a single source
(not magic literals), and record them identically in the export header and consumer adapter.

---

## K. Repository architecture (recommended organization)

Preserve the current layout; it is already sound. Recommended adjustments:

```
content/<domain>/<slug>.md          CANONICAL entities (unchanged)
connections/                        CANONICAL assertions (now really validated + exported — C.1)
sources/                            CANONICAL citations (validated + exported — C.1)
schema/                             unchanged (KEEP)
scripts/                            unchanged (KEEP); add validate_connections.py step
tests/                              unchanged (KEEP); fix C.5, wire into CI (C.4)
reports/                            unchanged (KEEP, derived)
exports/                            unchanged (KEEP, derived; now includes connections/sources)
explorer/                           consumer visual (KEEP as consumer; not part of canonical model — C.10)
docs/                               KEEP; add ADRs (C.3 relation deprecation), move consumer mapping example (C.8)
```

No filesystem reorganization for aesthetics — only where it serves the C.1/C.3 invariants.

---

## L. API/adapter architecture

**Preserve** the export-contract seam: consumer reads `exports/knowledge.json`, never the
canonical files. Recommended:

- **Public contract:** versioned export with entities + connections + sources (C.1), stable IDs,
  lifecycle status, validated relations, provenance, `historical` where present.
- **Internal:** `content/`, `connections/`, `sources/`, `schema/`, `scripts/` — consumers never
  touch these.
- **Consumer adapter:** the *only* cross-seam importer; validates the export version and throws
  (never silently skips) on dangling refs (already the pattern in STEM-TUITION `lhs-adapter.ts`).
- **No new API layer needed.** The brief's "API" is the versioned file export; do not build a REST
  microservice (spec §11 says exactly this; KEEP).

Boundary: `presentation` lives in consumer adapters; canonical objects carry only knowledge +
metadata + provenance.

---

## M. Search/retrieval architecture

> **Search is a way to retrieve knowledge, not the source of truth.**

- Canonical repository/data model remains authoritative. Any search index is **derived** and
  rebuildable from (a) the canonical files or (b) the export (which now includes connections).
- **Supported retrieval modes (all derivable, none authoritative):**
  - lexical (subset match on names/definitions);
  - structured (by type/domain/status/extension);
  - relationship traversal (follow validated connections — the graph the explorer already builds);
  - dependency traversal (transitive `requires`/`part_of`);
  - semantic (embedding index — built from the export, never canonical);
  - curriculum lookup (consumer-owned mapping tables).
- **No coupling to a vector DB / embeddings as canonical storage.** Do not introduce `chromadb` or
  an embedding store as the substrate. The explorer is a consumer that renders the export.

---

## N. AI integration boundary

> AI assists maintenance; **never silently redefines truth.**

| Purpose | Allowed? | Gate |
|---------|----------|------|
| Draft candidate entities/connections/definitions | Yes | must enter `status: draft`; AI flagged in provenance |
| Research / source discovery | Yes | output is a candidate dossier, not canonical |
| Contradiction / ambiguity detection | Yes | produces review signals only |
| Validation assistance (semantic) | Yes | feeds the I.2 layer; never a final gate |
| Deterministic validation | No (use code) | — |
| Auto-promotion to canonical | **No** | requires human `reviewed_by` + governance |
| Rewriting canonical definition on its own | **No** | governed change flow (O) |

Enforce with: `status: draft` default for AI prose; provenance `ai_drafted: true`; review gate
required before `human_reviewed`/`canonical`; no AI key capable of writing `content/` or
`connections/` outside the staged pipeline.

---

## O. Governance model (how canonical knowledge changes)

Preserve GOVERNANCE.md. Operationalize with the agent pipeline (section **P**). Key rules:

- **Who changes canonical knowledge:** staged pipeline + human gate. AI agents may propose
  (intake stage), never publish.
- **How changes are proposed:** a PR/branch that adds/modifies an entity/connection/source as
  `draft` with provenance.
- **Validation requirements:** deterministic (I.1) must pass; semantic (I.2) reviewed.
- **Review requirements:** a named human (`human:reviewer.*`) for promotion to
  `human_reviewed`/`canonical`; recorded in `review_history`.
- **Source requirements:** every canonical change references a source or a documented
  governance basis.
- **Conflict resolution:** via the `conflict` relation family + evidence; stakeholders surface,
  governance decides.
- **Deprecation / correction:** forward-only lifecycle; never in-place mutation of a released
  object.
- **Schema / relation / breaking changes:** freeze rule → ADR → human approval (spec §16).
- **Auditability:** `review_history`, ADRs, git history, `reports/`.
- **Enforcement:** prose → schema → validation → tests → CI, with the semantic tests wired into
  CI (C.4).

---

## P. The LHSTEM agent/curation pipeline (canonical-knowledge stages)

This is the deliverable the review brief's "add agent system like in STEM-TUITION" asks for,
**refined to a canonical-knowledge substrate** — mirroring STEM-TUITION's *engine* (hard-gate
pipeline, targeted repair, LLM-agnostic seams) and **filtering out all narration/story/pedagogy**.

It is a staged pipeline where each stage is a small deterministic **or** judgment-gated step, an
LLM-agnostic seam (injected callbacks like STEM-TUITION's `RunnerCallbacks`), and a **hard-gate**
release decision. It produces a **publication decision** (propose / candidate / reviewed /
canonical / hold / reject) over `content/` + `connections/` + `sources/` — never a story.

### P.1 The stages (LHS analog of STEM-TUITION engine stages)

```
Intake Request → Curation Blueprint → Draft Generator → Deterministic Gates → Semantic Review
        → Hard-Gate evaluate → Targeted Repair → Publish(s) / Hold / Reject
```

| LHS Stage | Analog (STEM-TUITION engine) | Responsibility here | Deterministic or judgment |
|-----------|------------------------------|----------------------|---------------------------|
| **1. Intake Request** | `ContentRequest` | A proposed change: create/update/deprecate an entity/connection/source, with a requested intent and source. | data |
| **2. Curation Blueprint** | `Blueprint` (plan) | Deterministically plan the change: which files, which relations, required sources, target status. Enforces "no curriculum/pedagogy in content". | deterministic |
| **3. Draft Generator** | `FormatGenerator` (LLM seam) | Produce a candidate `draft` entity/connection/source from the blueprint + grounded LHS context. AI-drafted, `provenance.ai_drafted`. | judgment (LLM seam) |
| **4. Deterministic Gates** | schema/coverage gates | schema conformance, ID/uniqueness, relation-registry domain/range, dangling targets, extension membership, provenance shape, filename↔slug, lifecycle legality, source_ref resolution. | deterministic |
| **5. Semantic Review** | LLM verifiers | factual fidelity to sources, internal-consistency/contradiction, conditions-of-validity, ambiguity; produces findings, never a direct publish. | judgment (LLM seam) |
| **6. Hard-Gate evaluate** | `evaluateGates` | Every applicable gate must PASS before progression. No averaged score overrides a FAIL. | deterministic combine |
| **7. Targeted Repair** | `repairOrders` | Map each failed gate to the responsible stage (e.g. schema fail → draft; coverage fail → blueprint; source fidelity → intake); repair just the gap, not a whole regenerate (unless plan is wrong). | deterministic + seam |
| **8. Publish / Hold / Reject** | `publication` | All-gates-pass, human-gated → promote to `human_reviewed`/`canonical` (or leave `draft`/`machine_validated` if human gate optional). Plan-fatal → reject; needs human attention → hold. | governance |

### P.2 Hard gates (adapted from STEM-TUITION `verification.ts`, LHS-renamed)

```
GateId: schema | identity | relations | provenance | resolution | conditions | intent
(intent = "does this change accomplish the requested canonical-change intent?" —
 conceptually the analog of STEM-TUITION's intent-essence, but for knowledge curation,
 NOT for an experience.)
```

Mapping gates → repair stage (`routeRepair`):

| Failed gate | Responsible stage |
|-------------|-------------------|
| `schema` | draft-generator |
| `identity` (id/slug/dup) | intake/blueprint |
| `relations` (registry/domain-range / dangling) | blueprint |
| `provenance` | intake |
| `resolution` (source_ref, deprecated_by resolve) | intake |
| `conditions` (context/validity/conflict) | blueprint |
| `intent` (request not met) | intake (forces regeneration) |

### P.3 Roles (deterministic stages become tooling; judgment stages become seams)

The brief's "different stages of work" maps to **agents/roles** exactly as STEM-TUITION's engine
does, minus the storytellers:

- **Curator/Intaker** (stage 1–2): turns a request into a governed blueprint. Deterministic.
- **Draft Agent** (stage 3): LLM seam producing candidate canonical prose/assertions. Never
  publishes.
- **Validator** (stage 4): the `validate.py`-style deterministic checks (now including
  connections/sources). Tooling, not an agent.
- **Reviewer** (stage 5): semantic/fidelity gate. LLM seam + human override.
- **Governance Gate** (stage 6–8): human decision point promoting to `canonical`, or holding
  for attention. Human-in-the-loop by design.

### P.4 What the pipeline NEVER produces

- Stories, lessons, narratives, teaching scripts, animations, interactive activities.
- pedagogical sequences or learner-targeted quizzes.
- Arbitrary AI explanations appended to canonical objects.

Those live downstream (STEM-TUITION `content-engine`/narration). The LHS pipeline ends at a
governed, validated canonical object.

### P.5 Implementation note (LATER, not this phase)

Per the brief's "do not implement yet", **P is a design, not code.** When activated, build it as:
- a small `scripts/curation_pipeline.py` reusing existing tools (`validate.py`, `review.py`,
  `curation_state.py`, `graph_policy.py`, `migrate_relationships.py`) with the hard-gate +
  repair router from this design;
- an LLM-agnostic callback seam (mirror `RunnerCallbacks`);
- wire `verify_all.py` into CI (C.4);
- add the connections/sources validation + export (C.1).

---

## Q. Migration plan (from current to recommended)

Order by safety, smallest-step-first:

1. **Q1 (NOW, low risk):** Fix `test_idempotence` stale count (C.5); collapse duplicate
   `version:` keys (C.6). No consumer impact.
2. **Q2 (NOW):** Add connections/sources validation to the gate (C.1) as an *additive* check
   (report, don't yet export) so nothing breaks; wire `verify_all.py` into a CI job (C.4).
3. **Q3 (SEAM):** Bump `export_version` to `0.2` and include `connections` + `sources` in the
   export (C.1/C.2); update the consumer adapter seam to read the version from the header.
4. **Q4 (refactor):** Declare inline `relationships[]` deprecated; migrate to connections
   (C.3); add an ADR.
5. **Q5 (governance):** Reconcile declared status vs. capability (C.9); finalize provenance
   shape reconciliation (C.7).
6. **Q6 (LATER, needs activation):** Build the curation pipeline (P) behind the "ACTIVATE
   LEARNINGHUBSTEM MVP" trigger.

Each step is verified by the deterministic + semantic validators and by the consumer-seam test.

---

## R. Future extensibility (without premature complexity)

- **New domains/subjects:** add a `content/<domain>/` directory + a `domain` vocabulary entry +
  relations; no schema change needed (schema is domain-agnostic).
- **Richer object types** (phenomenon, model, experiment, material, process): add deliberately
  via the governed freeze flow, not ad hoc.
- **Multilingual** (spec §12): identity is language-independent; add parallel
  `definition_lang`/`name_lang` fields via the extension registry or a dedicated multilingual
  phase — never new IDs per language.
- **New consumers** (research, assessment, simulation, teacher tools): all consume the same
  export; none reads internals.
- **Uncertainty/competing models:** already representable via conflict connections +
  confidence + evidence (no new machinery).
- **What to explicitly NOT add:** RDF/OWL/GraphDB/vector-DB-as-canonical, microservices, event
  buses, plugin systems, "AI generates canonical" shortcuts, or a pedagogy layer.

---

## S. Stress-test (brief §30) — summarized

- Elementary math concept, advanced QM derivation, chemical reaction, biological mechanism,
  materials property, engineering principle, computational concept: all are **entities** +
  **connections**; schema is domain-agnostic. PASS.
- Concept with multiple definitions / disputed understanding: multiple `connection` assertions
  with `confidence` + `conflict` relations + evidence. PASS.
- Concept in multiple curricula: one canonical ID, many consumer mappings. PASS.
- Concept reused by multiple products: one export, many adapters. PASS.
- Canonical source changes: update `provenance.source`/`source_ref`; add a new source; govern the
  change. PASS.
- Deprecated concept: `status: deprecated` + `deprecated_by`, still exported. PASS.
- Newly introduced concept: intake → draft → validation → review → canonical (pipeline P). PASS.
- Schema migration: three-track versioning + governed freeze + migration tests. PASS.
- AI-assisted proposed change: draft + `ai_drafted` + human gate. PASS.

The architecture holds across subjects, grades, curricula, and content formats **without tying
any system invariant to a single subject/grade/product**, and it never generates pedagogy or
stories — it only curates canonical knowledge.

---

## T. Downstream compatibility with STEM-TUITION

- **LHSTEM provides:** concepts, relationships (first-class connections), definitions,
  evidence/provenance, canonical prerequisites (`requires`/`logically_requires`), scientific
  constraints (context/validity), source info, version info.
- **STEM-TUITION decides:** explanation, sequence, examples, story, activity, grade/level,
  language, lesson length, assessment, interactivity.
- **Boundary rule:** do not pull pedagogical responsibilities back into LHSTEM to make
  STEM-TUITION easier. The LHSTEM agent pipeline (P) ends at canonical objects; STEM-TUITION's
  narration/story pipeline consumes those objects downstream.
- **Contract:** STEM-TUITION's `lhs-adapter.ts` is the seam; it reads the versioned export and
  throws on drift. Both repositories stay independent.

---

## U. Summary verdict (brief §28 classification)

| Item | Class |
|------|-------|
| Markdown+YAML canonical, stable IDs, three-track versioning, north-star boundary, governance, relation registry, consumer seam, extension registry, provenance/historical split | **KEEP** |
| `validate.py` as the gate; 9-step `verify_all.py`; phase-b/curation/metadata tests | **KEEP** — wire verify_all into CI (C.4) |
| Connections + sources + richer provenance | **IMPROVE** — validate + export (C.1), reconcile shapes (C.7) |
| Inline `relationships[]` as a relation source | **REFACTOR/DEPRECATE** — migrate to connections (C.3) |
| Duplicate `version:` keys; stale `test_idempotence` count; export/schema version literals | **REFACTOR** — C.5/C.6/C.2 |
| Declared "SEED ONLY" label vs. implemented capability | **RECONCILE** (C.9) |
| MBA agent pipeline (P) | **ADD (design now; implement behind activation)** |
| RDF/GraphDB/vector-DB-canonical, microservices, story/narration in canonical | **REMOVE / DO NOT ADD** |

---

## The design principle (restated)

> **Trustworthy canonical knowledge + stable semantics + strong provenance + controlled
> evolution + simple consumption.**
> Not: maximum abstraction, maximum agents, maximum infrastructure.

**LHSTEM curates canonical STEM knowledge; it does not generate stories.** The agent pipeline
above is a staged, hard-gated curation/validation/governance pipeline that mirrors STEM-TUITION's
*engine* in structure but **never** its narration/pedagogy — because LHSTEM is not a content
generator, and this review keeps the boundary clean.