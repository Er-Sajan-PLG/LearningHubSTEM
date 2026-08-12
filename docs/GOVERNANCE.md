# GOVERNANCE — STEM Ecosystem Workspace

**Status:** Cross-project governance for everything under `/Projects`.
**Applies to:** Humans and AI agents working in this workspace.
**Related:** `AGENTS.md` (routing), `docs/NORTHSTAR.md` (north star),
`docs/MASTER-VISION-LearningHubSTEM.md` (vision), `docs/LEARNINGHUBSTEM-SPECIFICATION.md`
(technical spec), `docs/LEARNINGHUBSTEM-ROADMAP.md` (phasing),
`docs/decisions/` (LearningHubSTEM decision records), `docs/REVIEW-RESPONSE.md`
(reconciliation record).

---

## 1. Governance precedence

```
LEVEL 1 — ECOSYSTEM INVARIANTS (non-overridable)
          ↓
LEVEL 2 — PROJECT / REPOSITORY GOVERNANCE
          ↓
LEVEL 3 — IMPLEMENTATION DETAILS
```

### Level 1 — Ecosystem invariants (never overridden)

- LearningHubSTEM is an **independent, open, structured, reusable STEM knowledge foundation**.
- LearningHubSTEM is **not** owned by, subordinate to, or a backend of any product.
- **Curriculum is external.** It is a consumer of the foundation, never a component of it.
- **Products are consumers.** STEM-TUITION, JARVIS, STEM-GAME, STEM Lab, and unknown future
  products all sit **below** LearningHubSTEM in the dependency direction.
- **Knowledge order ≠ curriculum order.** Relationships live in the knowledge layer;
  sequencing is a curriculum decision.
- Canonical knowledge cannot depend on a specific product, curriculum, database, or country.
- **AI output is not canonical** without appropriate human review.
- Derived artifacts are **regenerable** and are never the source of truth.

A repository's governance may refine how these apply, but may **not** silently redefine them.

### Level 2 — Project / repository governance

A repository decides its own framework, language, folder structure, testing, deployment,
internal APIs, and workflow. For example `STEM-TUITION/AGENTS.md` and
`STEM-TUITION/docs/CONSTITUTION.md` are authoritative inside that repository.

### Level 3 — Implementation details

Agent discretion: variable names, internal structure, test structure, small refactors,
non-breaking documentation, bug fixes within established boundaries.

---

## 2. The ecosystem view

LearningHubSTEM is the open foundation. Consumers build on top of it. There is **no**
"shared platform services" layer between the foundation and its consumers, and LearningHubSTEM
is **not** an application-services backend.

```
                    LEARNINGHUBSTEM
                 OPEN STEM FOUNDATION
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
     Consumer A       STEM-TUITION      Consumer C
     / Research       / Curriculum      / Future Tool
          │                │                │
          ▼                ▼                ▼
       Product          Product          Product
```

Dependency direction is always **consumer → foundation**. Nothing depends on LearningHubSTEM
from above; LearningHubSTEM depends on nothing.

### Status honesty

Distinguish **existing**, **planned**, and **possible** integrations. Today:

| Project | Status |
|---------|--------|
| `STEM-TUITION` | ACTIVE (flagship product; a consumer today by intent, not by code) |
| `JARVIS` | ACTIVE (AI platform; **planned** consumer) |
| `3D-Ludo` | PROTOTYPE (independent game; not a consumer) |
| `LearningHubSTEM` | SEED ONLY (minimal proof; full MVP **not** activated) |
| `STEM-GAME` | DEFERRED (empty folder; planned consumer) |
| STEM Lab | OUT OF SCOPE (referenced in STEM-TUITION constitution only) |

Do not describe planned integrations as existing ones.

---

## 3. Scope discipline

Classify every significant piece of work:

| Class | Meaning | Action |
|-------|---------|--------|
| **NOW** | Required by the current milestone | Implement |
| **SEAM** | Small interface/adapter/contract protecting a known future change | Implement only when inexpensive and useful |
| **LATER** | Described by the architecture but not required now | Document if useful; do not implement |
| **OUT OF SCOPE** | Not relevant now | Do not implement |

**Deferred / not current scope** unless the human explicitly activates it:

- STEM-GAME production, STEM Lab, JARVIS ↔ LearningHubSTEM integration
- Full LearningHubSTEM MVP (activation phrase: **"ACTIVATE LEARNINGHUBSTEM MVP"**)
- Microservices, cloud infrastructure, auth, payments, analytics, recommendation engines,
  vector/graph databases, generalized AI orchestration, shared platform services, cross-product
  identity or databases.

---

## 4. Canonical vs derived

```text
Canonical source (docs/LEARNINGHUBSTEM-SPECIFICATION.md defines the format)
      ↓
Derived artifacts: JSON exports, search indexes, embeddings, graph representations,
                   APIs, caches, recommendations
```

Rule: **derived artifacts are regenerable from canonical content and are never the source of truth.**

---

## 5. Rules that always apply

1. **Respect per-project governance** (Level 2 overrides within a repository).
2. Preserve the **Knowledge ≠ Curriculum ≠ Pedagogy ≠ Product** boundary.
3. **Build small.** Small verified increment + clean boundary + tests + docs beats speculative
   architecture.
4. **Do not expand scope silently.** When in doubt, ask the human.
5. **Products stay independent** — integration via explicit contracts/adapters, never embedding.
6. **AI output requires review** before becoming canonical.
7. **No secrets in code or docs.**
8. **Document decisions** (ADRs / decision records); leave a clear trail.
9. **Don't create infra just because a review suggested it** — verify against the workspace.

---

## 6. Definition of Done (canonical entity)

A canonical entity must have:

- stable ID (namespace + format per specification)
- valid schema
- required metadata
- provenance (source and/or reviewer record)
- valid relationships (whitelisted, no dangling targets)
- appropriate review status
- human review where required
- **no curriculum dependency, no product dependency**
- passing validation

---

## 7. Enforcement direction

Prose rules → schemas → validation → tests → CI enforcement.

Implement only what is justified **NOW** (see specification §15). Do not build a generalized
policy engine. Long-term candidate checks (documented, not built):

- no LearningHubSTEM → product dependency
- no product → LearningHubSTEM internal import coupling
- no curriculum-specific canonical entities
- no duplicate / dangling IDs, no content without provenance

---

## 8. Freeze rule (LearningHubSTEM foundation)

**Frozen does not mean "never change".** It means: foundational changes require an explicit
governance decision rather than accidental implementation drift.

The following require a documented decision record (in `docs/decisions/`) and, where the
human-decision list in the specification §16 says so, human approval:

- entity type changes
- relationship semantics changes
- ID rules changes
- canonical representation changes
- lifecycle semantics changes
- export contract changes
- schema version major bumps

Minor editorial / documentation improvements do **not** require a governance event.

---

## 9. Session protocol (cross-project)

1. Read `AGENTS.md`, `docs/NORTHSTAR.md`, and this file.
2. Read the affected repository's own governance.
3. Classify work NOW / SEAM / LATER / OUT OF SCOPE.
4. State a short plan before changing anything.
5. Run the affected repository's verification commands.
6. Finish with a short session summary and flag human decisions.

---

*If a rule must be violated, do not violate it silently — record the exception and get human
approval first.*