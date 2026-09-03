# STEMMA — TECHNICAL SPECIFICATION

**Version:** 0.1 (minimal foundation)
**Status:** Specifies the canonical STEMMA foundation. **Phase 1 — Foundation
Definition & Freeze.** This is the technical "how"; it is **not** activation of a full MVP.
**Scope:** `STEMMA/` repository.
**Related:** `AGENTS.md`, `docs/NORTHSTAR.md`, `docs/GOVERNANCE.md`,
`docs/MASTER-VISION.md`, `docs/decisions/` (decision records).

---

## 1. Goal of v0.1 / Phase 1

Phase 1 makes the minimum foundational decisions to stabilize STEMMA:

- a working schema, stable IDs, relationships, provenance, validation, and export
- **and** an explicit freeze on foundational decisions so future change is governed, not drift

The seed proves the architecture. It does **not** mean the MVP is activated. The full project
stays inactive until a human says **"ACTIVATE STEMMA MVP"**.

---

## 2. Canonical representation

### Decision: Markdown + YAML frontmatter

Each canonical entity is one `Markdown` file with a `YAML` frontmatter block and one or more
`##` prose sections.

```text
STEMMA/
├── content/                  ← canonical (source of truth)
│   ├── physics/
│   │   └── mechanics/
│   │       ├── force.md
│   │       ├── mass.md
│   │       └── acceleration.md
│   ├── math/ …
│   ├── chemistry/ …
│   ├── biology/ …
│   ├── earth-space/ …
│   ├── engineering/ …
│   └── scientific-practice/ …
├── connections/              ← first-class assertions (lhs:conn.*)
├── sources/                  ← canonical source records (lhs:src.*)
├── schema/
│   └── concept.schema.json   ← schema contract
├── scripts/
│   └── validate.py           ← validator + export generator
└── exports/
    └── knowledge.json        ← DERIVED artifact (regenerable)
```

Rationale: human-readable prose for `definition`/`examples`; machine-readable metadata in
frontmatter; diffable in git; independent of any database, product, or language; validated with
PyYAML + JSON Schema (both present in this workspace).

### Format rules (precise)

- The frontmatter is the **first** thing in the file, delimited by `---` on its own lines.
- Frontmatter is a single YAML mapping (the "entity object").
- Prose `##` sections follow the frontmatter; the frontmatter is the canonical machine data.
- Filenames equal the final ID slug (`lhs:phys.force` → `content/physics/mechanics/force.md`).
- Entity files live under `content/<domain>/<subdomain>/<slug>.md`.

### Minimal valid entity template

```markdown
---
id: lhs:phys.example
type: concept
name: Example Concept
domain: physics
status: draft
definition: >-
  A curriculum-agnostic definition of the concept.
symbol: X          # optional knowledge-layer metadata
unit: null         # optional; SI unit for quantities
equation: null     # optional; canonical form using defined symbols
common_misconceptions: []  # optional; false beliefs learners hold
provenance:
  ai_drafted: true
  source: null
  reviewer: null
  reviewed_at: null
relationships:
  - type: related_to
    target: lhs:phys.some-other
    note: optional
---

## Notes

Optional prose body.
```

**Optional metadata fields** (decision 0010): `equation`, `symbol`, `unit`,
`common_misconceptions` are knowledge-layer metadata — never curriculum or pedagogy. They let a
consumer render `name · statement · equation · related entities` directly from the export without
parsing prose. `equation` is a display form of an existing relationship; it is not a new entity
type and not a second authoring source.

**Canonical files are the source of truth. Derived artifacts must be regenerable. Derived
artifacts must never become authoritative merely because they are operationally convenient.**

No database is the canonical source. No RDF/OWL/JSON-LD stack is required (see §15).

---

## 3. Stable identity

### Namespace

```text
lhs:<domain>.<slug>
```

- `lhs` = STEMMA
- `<domain>` = one lowercase ASCII word (e.g. `phys`, `chem`, `math`, `bio`)
- `<slug>` = lowercase `[a-z0-9-]`, the final segment of the ID

### Rules

- IDs are **globally unique** within STEMMA.
- IDs are **stable**: they do not change with rename, refactor, or reordering.
- IDs are **never silently reassigned**.
- IDs are **never reused** for a different concept.
- IDs are **machine-readable** (ASCII, delimited, regex-validated) and **human-readable**.
- IDs are **independent of file paths, curriculum, products, and database-generated numbers**.
- **Renaming an entity does not change its ID.**
- **Deprecated IDs remain historically meaningful** — they are reserved forever.

### Concept lifecycle within identity

| Event | Handling |
|-------|----------|
| **renamed** (label changed) | `name` changes; `id` unchanged. |
| **split** (one concept → two) | new IDs for both parts; old entity `status: deprecated` with `deprecated_by` pointing to the primary part (or left null if ambiguous — ambiguity is documented, not hidden). |
| **merged** (two → one) | surviving entity keeps its ID; the other gets `status: deprecated`, `deprecated_by` = survivor. |
| **replaced** (corrected understanding) | new ID; old entity `status: deprecated`, `deprecated_by` = new ID; new entity lists the old ID in `aliases`. |
| **deprecated** | `status: deprecated`; `deprecated_by` = successor if any. |
| **misdefined** | deprecated (never mutated in place); a corrected entity gets a new ID or reuses the same ID **only** if the meaning is identical (documented). |

- **Aliases**: the `aliases` array on an entity lists historical IDs it is known by. Aliases must
  be valid `lhs:` IDs and must not equal the entity's own `id`.
- **ID reuse**: **never.** A deprecated identifier may never silently be assigned to a different
  concept.

### Assertion (connection) identity — ADR-0026

A connection (`lhs:conn.NNNNNN`, §ADR-0011) is an assertion, and what it *means* is the triple
`(source, relation, target)` plus `polarity` and `context.qualifiers`:

- **Claim signature (derived).** `sha256(source | relation | target | polarity | sorted qualifiers)`
  identifies the *proposition*, not the record. It is never stored in canonical YAML; the export
  emits it as `connections[].claim_signature` so consumers can detect duplicate or changed claims
  without recomputing. Two **active** connections with the same signature are a validation error.
- **The triple is immutable.** Correcting a claim is a supersession, never an in-place edit:
  `assertion.status: superseded` + `lifecycle.replaced_by`, with the corrected claim asserted
  under a **new** connection ID. Evidence, review status, confidence and context metadata may
  change freely — only the claim itself is frozen.
- **Removal requires retirement.** A connection that disappears from `connections/` without having
  been `superseded` (or `deprecated`) is a gate failure, because consumers may still hold its ID.

Enforced by `scripts/validate.py` (duplicate-claim gate) and `scripts/check_id_immutability.py`
(git-history triple guard); see `docs/decisions/0026-claim-identity.md`.

---

## 4. Entity model

Six entity types. All share the same required fields (§2 template). Type is an enum.

### 4.1 Concept

- **Purpose:** a general idea or notion.
- **Represents:** a category of phenomena or ideas (e.g. Force).
- **Does not represent:** a specific measurement, a unit, a law statement, a formula, or a belief.
- **Relationship participation:** any core relationship.
- **May be deprecated:** yes. **Type changes:** not permitted; a different type is a new entity.

### 4.2 Quantity

- **Purpose:** a measurable property.
- **Represents:** a property that takes numerical values (e.g. Mass, Acceleration, Momentum).
- **Does not represent:** the unit of measurement (that is Unit), the measurement of a specific
  object, or a law.
- **Relationship participation:** any core relationship; common target of `mathematically_requires`.
- **May be deprecated:** yes. **Type changes:** not permitted.

### 4.3 Unit

- **Purpose:** a standard for measuring a quantity.
- **Represents:** e.g. kilogram, metre per second squared.
- **Does not represent:** the quantity itself.
- **Relationship participation:** `mathematically_requires`/`related_to`/`appears_in_law` (as an
  entity appearing in a law); not a source of `applies_to`.
- **May be deprecated:** yes. **Type changes:** not permitted.
- *Not present in the seed; defined now for a stable vocabulary.*

### 4.4 Law

- **Purpose:** a principle or rule (e.g. Newton's Second Law).
- **Represents:** a general proposition that holds under stated conditions.
- **Does not represent:** a mere formula (that is Equation), a concept, or a quantity.
- **Relationship participation:** canonical source of `applies_to`; canonical target of
  `appears_in_law`.
- **May be deprecated:** yes. **Type changes:** not permitted.

### 4.5 Equation

- **Purpose:** a mathematical relation between quantities.
- **Represents:** e.g. F = m·a.
- **Does not represent:** the law's prose statement (Law) or the quantities (Quantity).
- **Relationship participation:** target of `applies_to`; related to its quantities.
- **May be deprecated:** yes. **Type changes:** not permitted.
- *Not present in the seed; defined now for a stable vocabulary.*

### 4.6 Misconception

- **Purpose:** a common erroneous belief.
- **Represents:** a specific false belief learners commonly hold.
- **Does not represent:** the correct concept, a curriculum error, or product-specific guidance.
- **Relationship participation:** `related_to` the correct concept. Pedagogical links
  (`commonly_misunderstood_as`) are **LATER** (see §7).
- **May be deprecated:** yes (when the belief becomes rare). **Type changes:** not permitted.
- *Not present in the seed; defined now for a stable vocabulary.*

---

## 5. Relationship vocabulary

Three layers. Only **core knowledge** relationships are canonical in v0.1.

### 5.1 Core knowledge relationships

| Relationship | Meaning | Direction | Symmetric | Inverse | Transitive | Allowed types |
|--------------|---------|-----------|-----------|---------|-----------|---------------|
| `logically_requires` | this entity cannot be correctly understood without that one | from → target | no | (converse) `logically_requires` | yes | concept, quantity |
| `mathematically_requires` | this entity is formally defined or derived from that one | from → target | no | (converse) `mathematically_requires` | yes | concept, quantity, unit |
| `part_of` | this entity is a component of that one | from → target | no | `has_part` (not stored) | yes | any |
| `derived_from` | this entity follows from that one | from → target | no | `is_basis_of` (not stored) | yes* | concept, law |
| `special_case_of` | this entity is narrower than that one | from → target | no | `generalizes` | yes | concept, law |
| `generalizes` | this entity is broader than that one | from → target | no | `special_case_of` | yes | concept, law |
| `equivalent_to` | same thing, different presentation | bidirectional | yes | itself | yes | any |
| `applies_to` | this law/rule applies to that entity | from → target | no | (converse, not stored) | no | source: law; target: concept/quantity/equation |
| `appears_in_law` | this entity appears in that law | from → target | no | (converse, not stored) | no | target: law |
| `related_to` | meaningful connection, otherwise unspecified | bidirectional | yes | itself | no | any |

\* `derived_from` is transitive only along derivation chains, never composition.

**Distinguishing `requires` from `related_to`:** `logically_requires` / `mathematically_requires`
assert a necessity — the target is part of the definition of the source. `related_to` asserts only
a meaningful connection with no necessity. **Never encode an ambiguity as `related_to` when a
specific relationship is known.**

### 5.2 Pedagogical relationships — LATER (not canonical in v0.1)

```text
commonly_taught_before
commonly_misunderstood_as
scaffolds
```

These describe how knowledge is taught/learned and belong to a pedagogy layer, not canonical core.

### 5.3 Curriculum relationships — consumer-owned, never canonical

```text
mapped_to_curriculum
included_in_unit
assessed_by
```

These belong to consumers entirely and must never appear in `content/`.

**Do not use an ambiguous `teaches` as a core-knowledge relationship.**

---

## 6. Knowledge ≠ Curriculum

STEMMA owns **knowledge**; it does not own curriculum decisions, even when a curriculum
references its concepts.

- STEMMA may define: *Newton's Second Law.*
- A curriculum may define: *Newton's Second Law appears in Grade 10 Physics Unit X.*

The second statement is **curriculum information** and does not belong in canonical content.

The same knowledge entity must be able to participate in — without duplication — the Nepal
curriculum, another national curriculum, an international curriculum (CBSE/GCSE/A-Level/IB),
university education, self-directed learning, and professional education.

A curriculum mapping is **consumer-owned** and is never a canonical STEMMA artifact.

---

## 7. Knowledge ≠ Pedagogy

STEMMA may expose knowledge relationships (`logically_requires`, `derived_from`,
`related_to`). It must **not** dictate, for any product:

- lesson order
- UI, animation, quiz style
- teaching strategy
- adaptive-learning algorithms
- tutoring personality
- any product-specific pedagogy

Those belong to consumers.

---

## 8. Provenance and review lifecycle

### 8.1 Principle

> **AI assistance is provenance information, not authority.**

Machine validation establishes syntax, schema conformity, valid IDs, valid references, and
allowed relationship structures. Machine validation **cannot** establish scientific truth,
pedagogical quality, correctness of interpretation, or human approval.

AI-generated content **never** automatically becomes canonical.

### 8.2 Lifecycle states

| State | Meaning | To enter |
|-------|---------|----------|
| `draft` | AI or human wrote it; not authoritative | creation |
| `machine_validated` | passes schemas/validation; still not authoritative | validation |
| `human_reviewed` | a named human accepted it (`provenance.reviewer`) | human review |
| `canonical` | reviewed and released; authoritative within scope | release |
| `deprecated` / `superseded` | no longer active | §3 identity rules |

Transitions are forward-only; a released entity is **never edited in place** (it is deprecated and
replaced).

### 8.3 `provenance` object

```yaml
provenance:
  ai_drafted: true            # boolean (required)
  source_kind: <optional>     # controlled vocabulary below
  source: <citation or null>
  reviewer: <name or null>    # required before human_reviewed/canonical
  reviewed_at: <nullable ISO date>
```

**Source classes** (`source_kind`, controlled vocabulary):

```text
human-authored            — written directly by a person
textbook                  — from a textbook
academic-or-research      — from a paper/study
institutional             — from an institution (e.g. NIST, NCDN)
standards-or-specification — from a standard/specification
ai-assisted-draft         — drafted with AI assistance
other                     — any other explicitly identified source
```

Objective is traceability, not a citation database. Nonessential fields are optional.

### 8.4 Historical attribution (who + when) — ADR-0018

`provenance` records **where the entity text came from** (the record source). A separate,
optional `historical` field records **who first stated the scientific claim and when** (the
scientific origin). Shape:

```yaml
historical:
  stated_by: "Isaac Newton"    # required — person/group who first stated/discovered
  year: 1687                   # required — CE integer; negative for BCE
  where: "Philosophiæ ..."      # optional — the work it was stated in
  context: "Classical mechanics" # optional domain note
  note: "..."                  # optional — contested/multiple-origin caveat
  timeline:                    # optional ordered milestones
    - year: 1687
      by: "Isaac Newton"
      event: "Second law stated in Principia"
```

Rules: optional and backward-compatible; `stated_by`+`year` required when present; be
**truth-conservative** (do not fabricate a single first origin where contested/independent —
say so in `note`); never curriculum/grade. See ADR-0018 and `docs/SOURCES.md`.

---

## 9. Canonical vs derived

```text
Canonical source (content/)  →  Derived artifacts (exports/, future indexes)
```

Derived artifacts (JSON export, search indexes, embeddings, graph forms, APIs, caches) are
**regenerable** and are **never** the source of truth. The v0.1 derived artifact is
`exports/knowledge.json`, regenerated by `scripts/validate.py`.

---

## 10. Versioning

Three **distinct** version tracks — never collapsed into one number:

| Track | Identifier | Meaning | Change rule |
|-------|-----------|---------|-------------|
| **Schema version** | `schema_version` | version of `schema/concept.schema.json` (field set, enums, constraints) | breaking change to entity fields/types → major bump |
| **Export / contract version** | `export_version` | version of the `exports/knowledge.json` file contract (shape, semantics) | breaking shape change → major bump |
| **Content release** | (LATER) | the knowledge set itself (entities added/updated/deprecated) | any content change; does **not** imply a contract bump |

Compatibility principle: a consumer may state **"I consume export contract version X"** without
implying every future knowledge release requires a rewrite. Adding entities, editing definitions,
or deprecating entities is a content release, not a contract change.

Both `schema_version` and `export_version` are recorded in the export. Content release tracking is
documented as LATER — do not build a package manager or release pipeline now.

---

## 11. Export / consumer contract

The canonical source is consumed through a versioned, machine-readable export:

```text
STEMMA canonical source (content/)
             ↓
validator / exporter (scripts/validate.py)
             ↓
versioned machine-readable export (exports/knowledge.json)
             ↓
consumer adapter (consumer-owned)
             ↓
consumer application
```

The export contract guarantees:

- **export version + schema version** fields (§10)
- **entity representation** — one JSON object per entity mirroring the canonical frontmatter
- **stable IDs** — `lhs:` IDs, never reassigned
- **lifecycle status** per entity
- **relationships** — whitelisted core relationships with resolvable targets
- **provenance representation** — `ai_drafted`/`source`/`reviewer` as in canonical content
- **deprecated entities** — still exported, `status: deprecated` (+ `deprecated_by`), so consumers
  can migrate; they are never silently deleted
- **regeneration principle** — the export is always regenerated from `content/`; a stale export is
  a bug, not a source of truth

Consumers never need access to internal canonical implementation details. This contract is useful
to a future consumer such as LearningHub **without** making LearningHub a dependency of
STEMMA.

Do **not** build a REST API, GraphQL, microservice, authentication, or cloud infrastructure to
demonstrate this. A documented file/export contract is sufficient for Phase 1.

---

## 12. Multilingual principle

**Not implemented in Phase 1.** The principle is:

> **Concept identity is language-independent.**

`lhs:phys.force` may have representations: English *Force*, Nepali *बल*, Hindi *बल*. Languages do
not create separate conceptual identities.

Multilingual content is a future implementation phase. Open questions (all **LATER**): canonical
language (if any), translation provenance, human vs AI translation, translation review,
locale-specific terminology.

---

## 13. Validation

Lightweight, standalone (PyYAML + JSON Schema, both present):

- schema conformance against `concept.schema.json`
- ID format and uniqueness
- required-field presence
- type / status / relationship whitelists
- dangling-target detection
- provenance presence
- filename ↔ ID slug consistency
- `aliases` validity (valid `lhs:` IDs, not equal to own `id`)
- `human_reviewed`/`canonical` require `provenance.reviewer`
- semantic type rules: `applies_to` source is a `law`; `appears_in_law` target is a `law`

Long-term enforcement direction (documented, not built):

```text
prose rules → schemas → validation → tests → CI enforcement
```

---

## 14. Standards alignment (SOTA, future)

For v0.1: **simple + interoperable + testable.** Possible future alignment (documented only):

- JSON-LD / SKOS for graph export
- schema.org `definedTerm` for web publication
- LRMI for resource metadata
- CASE / OpenSALT for curriculum packaging (consumer-side)
- stable HTTPS URIs for IDs when published

Do not build a semantic-web stack for v0.1.

---

## 15. Licensing

**Decided 2026-09-02 (ADR-0001).** STEMMA is licensed on two tracks, matching the content/code
distinction:

| Track | License | Scope |
|-------|---------|-------|
| Knowledge / content | **CC BY 4.0** | `content/`, `connections/`, `sources/`, `docs/` — see `LICENSE` |
| Code / tooling | **MIT** | `scripts/`, `schema/`, tests — see `LICENSE-CODE` |

Attribution is required for the knowledge content; the tooling is permissive. No contradictory
license claim may be added without a decision record (see `docs/decisions/0001-license.md`).

---

## 16. HUMAN DECISIONS REQUIRED

| # | Decision | Status |
|---|----------|--------|
| 1 | Knowledge/content license (CC BY 4.0 vs CC0) | DECIDED 2026-09-02 — CC BY 4.0 (ADR-0001) |
| 2 | Code/tooling license (MIT vs Apache-2.0) | DECIDED 2026-09-02 — MIT (ADR-0001) |
| 3 | Initial domain scope | PENDING |
| 4 | Phase 1 foundation freeze activation | PENDING (recommend: approve) |
| 5 | Final canonical format approval (Markdown + YAML) | DOCUMENTED — approval PENDING |
| 6 | Entity vocabulary approval (6 types) | DOCUMENTED — approval PENDING |
| 7 | Relationship vocabulary approval (10 core) | DOCUMENTED — approval PENDING |
| 8 | Multilingual policy approval | PENDING (default: language-independent identity) |

No approval is fabricated. Once approved, update the corresponding decision record to `decided`.

---

## 17. Freeze rule

**Frozen does not mean "never change".** It means:

> Foundational changes require an explicit governance decision rather than accidental
> implementation drift.

The following changes require a documented decision (a decision record, and human approval where
listed in §16):

- an entity **type** change
- **relationship semantics** changes
- **ID rules** changes
- **canonical representation** changes
- **lifecycle semantics** changes
- **export contract** changes
- **schema version** major bumps

**Minor editorial / documentation improvements do not require a governance event** (fixing typos,
clarifying prose, adding optional notes).

---

## 18. Out of scope (v0.1 / Phase 1)

Full ontology, broad knowledge coverage, multilingual content, external publication
infrastructure, formal semantic-web stack, large CI policy system, consumer APIs, production
STEMMA ecosystem, any source of truth outside `content/`, and — always — microservices,
cloud, auth, payments, analytics, vector/graph databases, recommendation engines, and shared
platform services.
