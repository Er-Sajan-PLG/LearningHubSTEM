# STEMMA — Implementation Plan v2 (Post-Audit E-Series)

**Status:** PROPOSED — AI-drafted 2026-09-03 from the external architecture audit.
**Not activated.** Per this repository's governance, no workstream here is authorized by
its mere existence: each requires an explicit human activation decision, and the gates in
§6 require explicit approval.

**Supersedes:** `docs/STEMMA-IMPLEMENTATION-PLAN.md` (Scope D) as the *forward plan*.
Its D1/D2 documentation-reconciliation items remain valid and are absorbed into **E0**;
its D3–D6 items are re-derived here where still open (traced to the audit). The prior plan
should be retained for history only.

**Implementation status:** E0.1/E0.4, E1.1–E1.4, E2.1–E2.7, E5.1/E5.2, E6.2 **implemented 2026-09-03**
(ADRs 0020/0021/0022; owner-directed activation "start implementing").
**2026-09-04:** gate **G-A decided** ("bump to 1.0 now") → E1.5 implemented (ADR-0023, contract
**v1.0**, co-release compat view); E4.1/E4.2 implemented (ADR-0023); E3.1 ADR **drafted** as
ADR-0024 (**gate G-C pending**); E6.1 campaign **tooling + 4 batch worksheets** generated
(`reports/e61-dependency-campaign/`) — review decisions themselves remain human work; E6.7
dependency-edge dashboard slice included.
**2026-09-05 (wave 5, ungated items only):** **E0.2** (ADR-0001 `decided`; "LICENSE DECISION PENDING"
retired repo-wide), **E0.3** (rename leftovers + docs map), **E1.6** (explorer graph builds from
`connections[]`, edges annotated + rendered by `review.status`), **E4.3** (claim signature +
duplicate-claim gate), **E4.4** (`reports/content-hash-ledger.json`; edit-in-place of a reviewed
object fails CI), **E4.5** (connection-triple immutability in `check_id_immutability.py`),
**E5.3** (`exports/release-manifest.json` + `docs/CONTENT-RELEASES.md`; tagging stays human),
**E5.5** (`docs/MIGRATIONS.md`) implemented. All other items unchanged and still gated as marked.

**Derived from:** `docs/ARCHITECTURE-AUDIT-v1.0.md` — **the latest architecture audit**
(supersedes `ARCHITECTURE-REVIEW-v0.3.md`). Every task below carries a traceability tag
**F#** (audit finding, Phase 15), **C#** (carried from the v0.3 review), or **R#** (Scope D
findings register) so nothing is proposed without evidence.

---

## 0. Evidence baseline (verified 2026-09-03, audit v1.0)

- 224 entities, **all `status: draft`, `ai_drafted: true`** — zero human-reviewed (F2).
- 654 connections: 50 `review.status: canonical` (7.6%), 604 unreviewed; 641 machine-migrated
  with `asserted_by: unknown:legacy-relationship` (F2); 653/654 `assertion.type: proposed`.
- **All 641 inline relationships duplicated 1:1 as connection files; 6 pairs connections-only;
  no generator; no consistency gate** (F1).
- Registry: **39 inverse-coherence defects** (35 relations name inverses that are undefined;
  `appears_in_law`↔`contains` incoherent pair; `part_of`/`has_part` asymmetric domain/range);
  phantom types `phenomenon`/`model`/`experiment`/`regime` in domain/range; 37/50 relations
  unused (F3).
- Vocabularies declared controlled, enforced by nothing: **194/654 connections violate the
  subdomain vocabulary; 142 use `context.domain: math` vs canonical `mathematics`;
  1 illegal `scale: microscopic`** (F3, F11).
- No inference-exclusivity, confidence↔basis, cycle, or `replaced_by`-resolution checks in the
  gate, despite ADR-0013/0014 ordering them (F6).
- ADR-0016 entity half (`external_ids`, `version`, `updated_at`, `rights`) — absent from
  `concept.schema.json` (F6).
- Math layer: `equation`/`unit`/`symbol` are unparseable display strings; dimensions exist on
  exactly 1 entity (a law); no symbol→quantity bindings; no dimensional validation (F4).
- Versioning: 4 disagreeing signals (`schema_version: "0.1"` literal vs v0.2 schemas vs
  `VERSION` 1.0.0 vs no git tags); exports churn on every validator run (`generated_at`)
  (F5, F8; R7, R9, R18).
- 3 skeleton source records vs 149 `provenance.source` strings — several citing curriculum
  bodies ("NCTM / ICSE Mathematics Curriculum") inside canonical entities (F2, F10).
- `regime: ["classical"]` stamped by migration on 650/654 connections (F9).
- Colon filenames block Windows checkouts; connection triples have no immutability guard;
  schema `$id`s are placeholders (F11, F13; R11, R12, R19).

`python3 scripts/verify_all.py` exits 0 on the audited tree — all work below preserves that.

---

## 1. Constraints that do not move (restated from governance)

North star and three boundaries; `content/` + `connections/` + `sources/` only as canonical;
derived = regenerable, never authoritative; `lhs:` IDs frozen and never reused (ADR-0003,
ADR-0019); AI output never canonical without human review; curriculum/pedagogy/product never
in canonical content; scope discipline NOW/SEAM/LATER/OUT. No vector/graph databases,
microservices, auth, analytics — all remain OUT OF SCOPE. **Addition from the audit:** every
ADR must land with its enforcement code (validator rule + test) in the same PR — governance
by document must stop outrunning governance by mechanism (fixes F6 systemically).

---

## 2. Workstreams

Sizes: S ≤ 1h · M ≤ half day · L ≤ 2 days · X = ongoing cadence.

### E0 — Status truth & doc reconciliation (absorbs Scope D D1/D2 remainders) — M

| Task | Detail | Fixes | Size |
|------|--------|-------|------|
| E0.1 | One status story: README/GOVERNANCE/roadmap all say "**live foundation in early curation — 224 draft entities; 50 canonical assertions; zero reviewed entities**" until E6 changes the numbers | F2, R5, R15 | S |
| E0.2 | ✅ Licensing record reconciliation: set ADR-0001 `decided` with the human approval date; fix GLOSSARY/consumer-seam "pending" lines | R4 | S |
| E0.3 | ✅ Remaining rename leftovers (R1 list) + docs/README.md map refresh (this plan adds the audit + v2 plan rows) | R1, R6 | S |
| E0.4 | ✅ **CI doc-status gate:** a script asserts the README status line matches `reports/epistemic-summary` counts (entity counts, reviewed %) — status claims become mechanically checkable | F2 (systemic) | S |

### E1 — Single source of truth for relationships (the pivot) — L

The audit's #1 finding. Declared by ADR-0011, never mechanized.

| Task | Detail | Fixes | Size |
|------|--------|-------|------|
| E1.1 | **ADR-0020 — connections-only truth (DONE 2026-09-03):** `connections/` is the sole canonical relationship source; entity `relationships[]` becomes a *generated compatibility projection* with a deprecation window; removal tied to contract v1.0 | F1, C.3 | S + gate G-A |
| E1.2 | ✅ `scripts/sync_relationships.py`: regenerate inline `relationships[]` from `connections/` (idempotent, deterministic); run once to close the 6-pair gap | F1, R8 | M |
| E1.3 | ✅ Validator consistency gate: inline block must equal the projection — drift = exit 1 | F1 | M |
| E1.4 | ✅ Contribution rule: new/edited relationships enter via `connections/` only; validator rejects new inline entries not present in connections | F1 | S |
| E1.5 | ✅ (ADR-0023) **Export contract v1.0:** `connections` + `sources` become required members; version constants read from the single source (E5.1); coordinate LearningHub adapter (`SUPPORTED_EXPORT_VERSION`) co-release per `EXPORT-VERSION-MIGRATION-Q3.md` | F1, F5, C.2 | M + gate G-A |
| E1.6 | ✅ Explorer graph builds from `connections[]` (inline only as fallback; `collectEdges`); edges carry `reviewStatus` and a trust-graded opacity (`REVIEW_OPACITY`) rendered by `graph-view.ts` | F1, R8 | M |
| E1.7 | (Gated by G-A completion) Remove `relationships[]` from `concept.schema.json` and the export; retire the projection | F1 | M |

### E2 — Registry & vocabulary integrity — L

| Task | Detail | Fixes | Size |
|------|--------|-------|------|
| E2.1 | ✅ **Repair the 39 inverse-coherence defects:** one canonical inverse table; every used relation's inverse is either a defined relation or the `inverse:` field is dropped; generate `has_part`-style missing inverses; regenerate registry programmatically | F3 | M |
| E2.2 | ✅ **ADR-0021 — entity types:** add `phenomenon`, `model`, `experiment`; remove `regime` from relation ranges; give `misconception` relation participation (`misconception_of`) or constrain its use; align registry domain/range with the type enum (no phantom types) | F3, R20 | M + gate G-B |
| E2.3 | ✅ **Vocabulary enforcement in the gate:** validate `context.domain/subdomain/regime/scale` against `schema/vocabularies/`; repair the 194 subdomain violations, unify `math` → `mathematics`, fix `scale: microscopic` | F3, F11 | M |
| E2.4 | ✅ **Cycle detection** for dependency + hierarchy families in `validate.py` (ADR-0012 promised it; graph_analysis assumes it exists) | F3, F11 | M |
| E2.5 | ✅ **Implement the orphaned ADR rules:** inference mutual-exclusivity (ADR-0014), confidence↔basis pairing (ADR-0013), `lifecycle.replaced_by` / `deprecated_by` resolution, entity-side ADR-0016 fields (`external_ids`, `version`, `updated_at`, `rights`) | F6, F7 | M |
| E2.6 | ✅ Enforce registry coherence (mutual/mirrored/symmetric) in tests (property-based checks, not hardcoded counts) | F3, C.5 | S |
| E2.7 | ✅ Prune speculative vocabulary: mark the 37 never-used relations `status: reserved` (or remove); deprecate duplicate pairs (`broader_than`/`narrower_than` vs `generalizes`/`special_case_of`; `contains`/`composed_of` vs `part_of`/`has_part`) | F3 | S |

### E3 — STEM math layer (the subject-matter gap) — L

| Task | Detail | Fixes | Size |
|------|--------|-------|------|
| E3.1 | 📝 drafted as ADR-0024 (gate G-C) — **math ADR — canonical math representation:** entity-level `math` object: `equation {latex: <canonical LaTeX>}`, `symbol_bindings: [{symbol, quantity: lhs:…}]`, quantities gain `dimensions` (MLTQΘNIJ vector in `extensions.dimensions` — promoted to schema for type `quantity` only); `unit` becomes a reference to a unit entity, display strings demoted to derived | F4 | M + gate G-C |
| E3.2 | Backfill: symbol bindings + LaTeX for the 54 quantities and 11 laws (highest-value subset first: mechanics); fix the type-inconsistent `dimensions` on `phys.newtons-second-law` | F4 | L |
| E3.3 | **Unit registry:** real `unit` entities with QUDT/UCUM codes via `external_ids` (E4.1); `metre per second squared (m/s²)` → `lhs:unit.metre-per-second-squared` + derived display | F4 | M |
| E3.4 | **Dimensional-consistency validator:** symbol→quantity→dimension bindings must type-check declared equations; quantity `unit` must reduce to its `dimensions` | F4 | L |
| E3.5 | Derived rendering: MathML Core + pretty-string generation in the export (never canonical) | F4 | M |
| E3.6 | Derivation sketch (SEAM): `derivation {from: [connection ids], assumptions: []}` on `derived_from` connections — represent "how", defer full proof checking | F4 | M |

### E4 — Identity & provenance hardening — L (spread)

| Task | Detail | Fixes | Size |
|------|--------|-------|------|
| E4.1 | ✅ (ADR-0023) `external_ids` first-class (complete ADR-0016): namespaced multi-valued (`wd:`, `orcid:`, `doi:`, `isbn:`, `qudt:`, `ucum:`); seed with Wikidata QIDs for the mechanics batch | F6, R24 | M |
| E4.2 | ✅ (ADR-0023; `schema/agent-registry.yaml`) agent registry (id, class, external_id, display name); validator resolves every `human:`/`process:`/`llm:`/`unknown:` agent ID against it | F2 | M |
| E4.3 | ✅ **Claim signature** (derived; `validate.claim_signature` + `check_duplicate_claims`): `hash(source|relation|target|polarity|qualifiers)`; duplicate-claim detection in the gate (ADR-0016 completion) | F7 | S |
| E4.4 | ✅ Object `content_hash` + edit-in-place detection (`scripts/check_content_hashes.py`, ledger tracked): a `human_reviewed`/`canonical` object whose content changed without a lifecycle transition fails CI | F5 | M |
| E4.5 | ✅ Connection-triple immutability guard — `check_id_immutability.py` walks `connections/` history; rewriting a triple or deleting a connection fails | F11, R12 | M |
| E4.6 | Colon-filename migration (`conn.000001.yaml`, `src.<slug>.yaml`; IDs untouched) | F11, R11 | M + gate G-E |
| E4.7 | HTTPS URIs + real schema `$id`s (replace `learninghubstem.example`) — gated with publication | F13, R19 | S + gate G-F |

### E5 — Versioning & release discipline — M

| Task | Detail | Fixes | Size |
|------|--------|-------|------|
| E5.1 | ✅ **Single version source** (`schema/VERSION.yaml`): `schema_version`, `export_version`, content-release tag read by every exporter; kill all literals (0.1/0.2/1.0.0 disagreement) | F5, R7 | M |
| E5.2 | ✅ **Deterministic exports:** stamp content-hash instead of `generated_at`; CI step `validate && git diff --exit-code exports/` (stale export fails the build) | F8, R9 | S |
| E5.3 | ✅ **Content releases:** `scripts/release_manifest.py` (per-file + aggregate hashes, deterministic) + `docs/CONTENT-RELEASES.md` changelog/verification recipe; the git tag itself remains a human action | F5, R18 | M |
| E5.4 | Decide: stop tracking `exports/` (publish as release assets) or keep tracked-but-bit-identical with the E5.2 gate | F8 | S + gate G-E |
| E5.5 | ✅ `MIGRATIONS.md` log (M1–M9); every schema change appends (old-data-validates-against-old-schema note) | F6 | S |

### E6 — Epistemic activation (the core value; continuous cadence) — X

Aligned with Scope D D4; reordered by the audit's trust-first logic.

| Task | Detail | Fixes | Size |
|------|--------|-------|------|
| E6.1 | 🔄 started (tooling + batches 01–04 in `reports/e61-dependency-campaign/`; 34/188 reviewed) **Dependency-edge review campaign:** all 188 `mathematically_requires`/`logically_requires` edges in weekly batches of 25–50 (prioritised by centrality), per CURATION-PROTOCOL | F2, R14 | X |
| E6.2 | ✅ **Regime de-fabrication:** regenerate migrated connections' `context.regime` honestly (`regime: null` + policy note); epistemic fields stop being boilerplate | F9 | M |
| E6.3 | **Sources growth:** 3 → coverage of the 149 `provenance.source` strings; **re-classify curriculum-body citations** (NCTM/ICSE/NCDC) out of canonical `provenance.source` into consumer-side mapping docs or `source_kind` with explicit role | F2, F10 | X |
| E6.4 | Entity review pilot → cadence (mechanics first, 41 entities), `provenance.reviewer` + `reviewed_at` set | F2 | M then X |
| E6.5 | Reviewer identity policy: recommend ORCID-backed IDs (pseudonymous display allowed); amend spec §8.2 | F2, R13 | S + gate G-D |
| E6.6 | **Competing-claim semantics (next free number):** adopt Wikidata-style `rank` on assertions (preferred/normal/deprecated) or document consumer resolution rule (review status + confidence); define when `contradicts` is a relation vs two ranked assertions | F7 | S + gate G-H |
| E6.7 | Epistemic dashboard: report entity-review % and dependency-edge review % per domain (extends existing scripts) | F2 | S |

### E7 — AI/API surface (SEAM) — M

| Task | Detail | Fixes | Size |
|------|--------|-------|------|
| E7.1 | Formalize the **policy-graded query contract** (`all/reviewed/canonical/trusted`) in `STEMMA-CONSUMER-SEAM.md`: every AI-facing view/query carries a trust floor | Audit Phase 11 | S |
| E7.2 | **MCP server (minimal):** `get_entity`, `get_assertions(policy)`, `get_prerequisites(transitive, policy)`, `search` — reads the export, returns provenance + review status inline; local stdio server, no hosting | Audit Phase 11 | M + gate G-F |
| E7.3 | Deterministic **context packs:** subgraph→text projection with per-assertion attribution lines; derived artifact | Audit Phase 11 | M |
| E7.4 | Move the explorer out of `content/`-coupling: validator stops writing into `explorer/`; sync via build script only (full relocation to its own repo at G-G) | F12 | S |

### E8 — Publication & interop (LATER; gated) — L

JSON-LD 1.1 projection with SKOS/Biolink predicate mapping (regenerable); `schema.org DefinedTerm`
emission; MathML rendering (E3.5); HTTPS `/id/` redirect service (E4.7); external publication.
Activation phrase proposal: **"ACTIVATE STEMMA PUBLICATION"**. Nothing here starts before E1–E5
land and E6 shows a reviewed core.

---

## 3. Sequencing

```
E0 ─┐
E1 ─┼─ correctness first: E1/E2 are the pivot; E5.1+5.2 are quick wins inside this wave
E2 ─┘
E3 ─── after E2 (needs phenomenon/quantity/type alignment); E3.1 ADR can draft in parallel
E4 ─── independent; E4.1/E4.2 unblock E3.3
E6 ─── starts immediately (cadence) and never stops; E6.2 after E2.3 (vocabularies enforced)
E5.3 ── first tagged release after E1 contract v1.0
E7 ─── after E1 (needs connections in the export)
E8 ─── gated; after E6 shows a reviewed core
```

Suggested first PRs:
1. E0 (status truth) + E5.2 (deterministic exports) — credibility + hygiene in one day.
2. E1.1–E1.4 (connections-only truth, generator, gate) + E2.5 (orphaned ADR rules).
3. E2.1–E2.4 (registry repair + vocabulary enforcement + cycles) + E2.7.
4. E3.1 ADR + E4.1/E4.2 (external_ids + agents).
5. E6.1 batch 1 + E6.2 + E6.7.

## 4. Success metrics (mechanically checkable)

- Inline↔connection drift: 0 (gate-enforced).
- Registry inverse-coherence defects: 0 (CI check added).
- Vocabulary violations: 0; `math`/`mathematics` unified.
- Dimensional validation: 100% of symbol-bound equations type-check.
- Deterministic export: `git diff --exit-code exports/` green in CI.
- One git tag + manifest per content release (manifest ✅ mechanised; tag = human action).
- Duplicate claim signatures: 0 (gate-enforced); reviewed objects edited in place: 0.
- Connection triples rewritten in history: 0.
- Reviewed dependency edges: 188 → 100%; entities human_reviewed ≥ mechanics batch.
- Connections without evidence: 599 → ≤ 300 in the first cycle.
- No `asserted_by: unknown` on any newly created assertion; agents resolve in the registry.

## 5. Explicitly deferred (audit Phase 17 DEFER — do not pull forward)

OWL/reasoning; SHACL (until a JSON-LD projection exists); RDF 1.2 triple-term migration (until
Rec + tooling); Wikibase software; any DB in the canonical path (derived SQLite mirror
permitted); embedding-model/vector-index commitments; multilingual *content* (keep
language-independent identity); assumption ontology; nanopublication tooling; CAS-level
equation semantics beyond dimensional checking; REST/GraphQL services; event sourcing/CRDTs;
automated entity resolution.

## 6. Human decision gates

| Gate | Decision | Unblocks |
|------|----------|----------|
| G-A | ✅ decided 2026-09-04 (ADR-0023): contract **v1.0** now; compat `0.1` view during LearningHub co-release | E1.5 ✅; E1.6–E1.7 open |
| G-B | Entity-type expansion ADR (`phenomenon`, `model`, `experiment`; `misconception_of`) | E2.2 |
| G-C | Math-layer ADR (canonical LaTeX + symbol bindings + QUDT/UCUM) — **draft ready: ADR-0024** | E3 |
| G-D | Reviewer identity policy (ORCID-backed recommended) | E6.5 |
| G-E | Colon-filename migration + exports tracking model | E4.6, E5.4 |
| G-F | Publication track (HTTPS URIs, `$id`s, MCP server) | E4.7, E7.2, E8 |
| G-H | Competing-claim rank semantics | E6.6 |

## 7. Risks

| Risk | Mitigation |
|------|------------|
| Contract v1.0 breaks the one live consumer | Co-release with adapter per EXPORT-VERSION-MIGRATION-Q3; projection fallback during window |
| Registry pruning invalidates curated connections | Only 12 relations are used; pruning touches zero existing edges; `reserved` status, not deletion |
| Math backfill stalls | Type-check only what is bound; partial coverage degrades gracefully (no binding = no check, warning only) |
| Review bottleneck (single reviewer) | Batch cadence + dashboard; dependency edges first because consumers actually use them |
| Scope creep toward E8 before trust exists | E8 hard-gated on reviewed-core metrics; OUT-OF-SCOPE list restated in every PR template |
| Docs drift again | E0.4 mechanical status gate + "ADR lands with its enforcement" rule |

---

*Prepared 2026-09-03 from `docs/ARCHITECTURE-AUDIT-v1.0.md` (the latest architecture audit).
All file:line-level claims were verified against the working tree at `2a3ce9c`; `verify_all`
exit 0. This document is AI-drafted: it becomes canonical only through the repository's
decision-record process and explicit human activation.*
