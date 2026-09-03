# STEMMA — Implementation Plan (Scope D: post-rename reconciliation & epistemic activation)

> **STATUS: SUPERSEDED AS THE FORWARD PLAN (2026-09-03)** by
> **[`STEMMA-IMPLEMENTATION-PLAN-v2.md`](STEMMA-IMPLEMENTATION-PLAN-v2.md)**, derived from the
> latest audit [`ARCHITECTURE-AUDIT-v1.0.md`](ARCHITECTURE-AUDIT-v1.0.md). D1/D2 documentation
> items remain valid and are absorbed into plan v2 **E0**; D3–D6 items still open are re-derived
> and re-traced there (E1–E6). Retained for history and for its R-number findings register,
> which plan v2 references.

**Status:** PROPOSED — agent-drafted 2026-09-03 from the full repository review. **Not
activated.** Like the roadmap rule, this plan is not authorization to implement: each phase
requires an explicit human activation decision, and the human gates in §5 require explicit
approval.

**Related:** `docs/ARCHITECTURE-REVIEW-v0.3.md` (findings C.1–C.10),
`docs/HISTORY-RENAME.md`, `docs/decisions/0019-rename-and-freeze.md`,
`.plan/A0-baseline.json` (Scopes A–C), `docs/EXPORT-VERSION-MIGRATION-Q3.md`,
`docs/RELATIONSHIP-MODEL-ADR-0011-note.md`, `docs/curation/CURATION-PROTOCOL-v0.2.md`,
`docs/STEMMA-ROADMAP.md` (stale; D2 rewrites it).

---

## 0. Evidence baseline (verified 2026-09-03)

Verified by running `python3 scripts/validate.py` and `python3 scripts/verify_all.py`
(both exit 0) and reading `reports/` and `content/` directly:

- **224 entities** (physics 95, math 43, chemistry 40, biology 33, earth-space 10,
  engineering 1, scientific-practice 2) at `content/<domain>/<subdomain>/*.md`.
- **654 connections**: 50 canonical (7.6%), 604 unreviewed, 641 migrated from legacy
  inline relationships, 13 human-authored; 599 without evidence; 1 with a confidence value.
- **All 224 entities are `status: draft`, `ai_drafted: true`** — zero human-reviewed entities.
- 3 source records; 50-relation registry; extension registry (ADR-0017); 19 ADRs;
  3D explorer; ingestion + curation pipeline; CI-enforced ID-immutability guard.
- Consumers: LearningHub (typed adapter), PROFESSOR-J (adapter; code renamed), explorer.
- Rename Scope A closed contract-safe (881 `lhs:` IDs unchanged, A9 gate);
  Scope B (open-source hardening) merged; Scope C (review gate) half-built:
  the state machine and review tooling exist, but the PR-enforced human merge path
  (`docs/INGESTION.md` §"Review gate") is still procedural.

### Findings register (R-numbers; this plan's traceability)

| # | Finding | Severity |
|---|---------|----------|
| R1 | ~13 old-brand leftovers in current STEMMA docs (`AGENTS.md:37` broken pointer; stale H1 titles in SPECIFICATION/ROADMAP/MASTER-VISION; `GOVERNANCE.md:17,59`; `CURATION-PROTOCOL-v0.2.md:3`; `decisions/README.md:1`; `explorer/package.json` name; `ci.yml:10` concurrency group; "LHS" prose in 3 script docstrings + 2 docs) | high (cheap fixes) |
| R2 | Activation phrase "ACTIVATE LEARNINGHUBSTEM MVP" survives in 3 governing docs | high (governance string) |
| R3 | Consumer-name drift: ~67 "STEM-TUITION" refs in current docs while the product is LearningHub with `@learninghub/*` packages (`STEMMA-CONSUMER-SEAM.md:81-91` commands now stale in both directions) | medium |
| R4 | Licensing contradiction: `LICENSE` (CC BY 4.0) + `LICENSE-CODE` (MIT) exist, but ADR-0001 is "PENDING", spec §15 says no license chosen, `GLOSSARY.md:25` and `STEMMA-CONSUMER-SEAM.md:101` still say pending | high (record integrity) |
| R5 | Three contradictory status claims: README "active canonical foundation" vs `GOVERNANCE.md:84` "SEED ONLY" vs workspace AGENTS project map | medium |
| R6 | Doc drift: roadmap Phase 3+ "LATER" is where all work happened; `docs/README.md` map missing ~15 current docs; spec §2 says entities live flat under `content/` vs real subdomain tree; `REVIEW-RESPONSE.md:52` claims STEMMA is not a git repo; ADR-0018 says 149 entities | medium |
| R7 | Version drift (C.2 open): schemas self-describe v0.2; export writes `schema_version: "0.1"` | medium |
| R8 | Inline↔connections projection drift (C.3 open): 6 entity-pairs only in connections; no consistency gate; no projection generator; explorer + LearningHub adapter read the legacy inline projection | high (data hygiene) |
| R9 | Tracked derived exports churn on every validate run (`generated_at`); no freshness check in either CI | medium |
| R10 | `scripts/curation_status.py:120` hardcodes a stale note (397/382) contradicting the live counts (654/654) in the same generated report | low |
| R11 | Colons in tracked filenames (`connections/lhs:conn.*.yaml`, `sources/lhs:src.*.yaml`) — repository cannot be checked out on Windows | medium (open-source readiness) |
| R12 | Connection identity (source/relation/target) has no immutability guard; `check_id_immutability.py` walks `content/` only | medium |
| R13 | Reviewer identity is pseudonymous (`human:reviewer.biology-001`) vs spec §8.2 "named human"; policy undocumented | low |
| R14 | `related_to` = 371/654 (57%); the prerequisite graph is 188 dependency edges, mostly unreviewed; evidence layer mostly axiomatic placeholders; 3 source records total | high (core value) |
| R15 | Zero human-reviewed entities while the README claims a canonical foundation | **highest** |
| R16 | Workspace-level rename unfinished: workspace `README.md`; `docs/umbrella/CONTRACTS.md` and `authority/exports-manifest.yaml` point at the dead `LearningHubSTEM/exports/knowledge.json` path; `docs/WORKSPACE-ARCHITECTURE.md:71` broken filename; `docs/WORKSPACE-CICD.md:24` + workspace CI job key `validate-learninghubstem`; `docs/WORKSPACE-DEV-TASKS.md` examples; `.agents/skills/learninghubstem-knowledge/` (its validate command runs a nonexistent path — actively misleads agents) | high |
| R17 | PROFESSOR-J docs corpus: 79 old-name refs + broken relative links (`README.md:112`, `PRD.md:190-191` → `../LearningHubSTEM`) | medium (their repo) |
| R18 | No git tags/releases despite `VERSION` 1.0.0 | medium |
| R19 | Placeholder `$id` URIs (`learninghubstem.example`) + frozen schema titles carry the dead brand — publication checklist items per ADR-0019 | medium (gated) |
| R20 | Relation registry domain/range references `phenomenon`/`model`; entity type enum lacks both (architecture review's own `[UNCERTAIN]`) | medium |

---

## 1. Constraints that do not move (restated)

North star, three boundaries, `content/`-only canonical, derived = regenerable, `lhs:` IDs
frozen (ADR-0003), schema/export contracts frozen pending ADR (ADR-0019), AI output never
canonical without human review, curriculum/pedagogy/product never in canonical, scope
discipline NOW/SEAM/LATER/OUT. This plan proposes **no** `lhs:` change, **no** schema
semantics change without an ADR, **no** auto-canonicalization, **no** infrastructure
(vector/graph DB, microservices, auth, analytics — all remain OUT OF SCOPE).

---

## 2. Phases

Classification: D1–D3 = NOW (correctness debt), D4 = NOW (core value, cadence-based),
D5 = SEAM (contracts + cross-repo), D6 = LATER (gated by explicit activation).
Sizes: S ≤ 1h · M ≤ half day · L ≤ 2 days · X = ongoing cadence.

### D1 — Rename reconciliation inside STEMMA (fixes R1, R2, R3) — M

| Task | Detail | Size |
|------|--------|------|
| D1.1 | Fix `AGENTS.md:37` → `docs/STEMMA-SPECIFICATION.md` | S |
| D1.2 | Fix stale H1/labels: `STEMMA-SPECIFICATION.md:1`, `STEMMA-ROADMAP.md:1`, `MASTER-VISION.md:1,73,91,268`, `GOVERNANCE.md:17,59`, `decisions/README.md:1,3`, `curation/CURATION-PROTOCOL-v0.2.md:3`, `integrations/ECC-INSPIRATION-v0.2.md:1` | S |
| D1.3 | Re-point activation phrase to **"ACTIVATE STEMMA MVP"** in SPECIFICATION:20, ROADMAP:22, GOVERNANCE:106 + record in a new ADR (ADR-0020) that the old phrase is retired as a trigger | S + gate G1 |
| D1.4 | `explorer/package.json` + lockfile: `learninghubstem-explorer` → `stemma-explorer` | S |
| D1.5 | `ci.yml:10` concurrency group → `ci-stemma-…` | S |
| D1.6 | "LHS" prose → "STEMMA (`lhs:` namespace)" in `scripts/ingest.py:2`, `ingest_to_proposals.py:2`, `curation_pipeline.py:2`, `docs/INGESTION.md:1`, `docs/grade12-curriculum-mapping.md:108`, explorer comments. Protocol names (`lhs-*`, `Lhs*`) stay per ADR-0019 | S |
| D1.7 | Consumer-name sweep: "STEM-TUITION/STEMTuition" → "LearningHub" across current docs (README, AGENTS, NORTHSTAR, GOVERNANCE, MASTER-VISION, GLOSSARY, CONSUMER-SEAM, EXPORT-VERSION-MIGRATION, RELATIONSHIP-MODEL note); fix `STEMMA-CONSUMER-SEAM.md:81-91` package names to `@learninghub/*` | S + gate G2 |

**Exit criteria:** `grep -ri learninghubstem` over tracked files returns hits only in
HISTORY-RENAME.md, dated ADR prose, and the "formerly known as" note; every doc cross-reference
resolves to an existing file; `verify_all` exit 0; explorer typecheck/build green.

### D2 — Truth reconciliation (fixes R4, R5, R6) — M

| Task | Detail | Size |
|------|--------|------|
| D2.1 | Licensing record: confirm the human approval moment for CC BY 4.0 + MIT; set ADR-0001 to `decided (<date>)`; rewrite spec §15/§16 rows; fix `GLOSSARY.md:25` and `STEMMA-CONSUMER-SEAM.md:101` | S + gate G3 |
| D2.2 | One status story everywhere (README, GOVERNANCE §2 table, workspace AGENTS project map): "**live foundation in early curation — contracts proven; 224 draft entities; 50 canonical assertions; review pipeline operational**" | S |
| D2.3 | Rewrite `STEMMA-ROADMAP.md`: retire the stale Phase 0–2 table; record Scopes A–C as done; adopt D-phases from this plan as the forward plan with per-phase activation gates | S |
| D2.4 | Spec §2 format rules → `content/<domain>/<subdomain>/<slug>.md` (matches implementation and README diagram) | S |
| D2.5 | `docs/README.md` map: add HISTORY-RENAME, INGESTION, SOURCES, VERSIONING, EXPORT-VERSION-MIGRATION-Q3, ARCHITECTURE-REVIEW-v0.3, grade12 mapping, curation/, metadata/, research/, integrations/ | S |
| D2.6 | Fix `REVIEW-RESPONSE.md:52` (STEMMA is a git repo with remote); date-stamp ADR-0018's entity count or state "at decision time" | S |

**Exit criteria:** no doc asserts a status or license that another doc contradicts;
`verify-docs` CI + `verify_all` green.

### D3 — Correctness & hygiene (fixes R7–R12 partially) — L

| Task | Detail | Size |
|------|--------|------|
| D3.1 | `curation_status.py:120`: compute the note from live totals (no hardcoded 397/382); regression test | S |
| D3.2 | Version literal consolidation (C.2): one authoritative source (e.g. `schema/VERSION.yaml`) read by validate/export scripts; align schema self-description (v0.2) with the export literal per ADR-0008; keep `export_version: "0.1"` until D5.1 | M |
| D3.3 | Projection sync (C.3 residual): add a generator `scripts/sync_relationships.py` that rewrites inline `relationships[]` from canonical `connections/`; run it (closes the 6-pair gap); add a validator consistency check (inline must equal the projection); rule: new/edited relationships go into `connections/` only. Deprecation of the inline field itself waits for D5.1 (consumer migration) | M |
| D3.4 | Export churn fix: drop `generated_at` from the tracked file (or replace with a deterministic value, e.g. content-hash), and add a CI step `validate && git diff --exit-code exports/` so a stale export fails the build instead of dirtying the tree | S |
| D3.5 | Windows portability decision for `connections/` + `sources/` filenames: migrate to colon-free filenames (`conn.000001.yaml`, `src.<slug>.yaml`; the `lhs:` id inside the file is untouched — not an identity change under ADR-0003/0019). Verify `check_id_immutability.py` and `verify_all` still green after `git mv` | M + gate G5 |
| D3.6 | Connection identity guard: extend the immutability check (or add a sibling) so a `lhs:conn.*` whose `source`/`relation`/`target` is reassigned across history fails CI | M |
| D3.7 | `validate.py`: load `relation-registry.yaml` once per run instead of once per connection | S |
| D3.8 | Branch hygiene: prune fully-merged local + remote branches (`chore/licensing`, `feat/math-domain-foundation`, `fix/lhs-schema-violations` — all verified 0 commits ahead of `main` on 2026-09-03); fix the workspace project map's stale "phase-B curation active on `feat/math-domain-foundation`" line (belongs with D2.2/D5.5) | S |

**Exit criteria:** all listed changes land with tests; `verify_all` exit 0; fresh
`validate.py` run produces zero working-tree diff (D3.4); a Windows-facing clone check
(D3.5) documented.

### D4 — Epistemic activation (fixes R13, R14, R15 — the core value work) — X (cadence)

The single highest-value line of work: convert an AI-drafted graph into a human-verified one,
using the tooling that already exists (`review.py`, `review_queue.py`,
`curation_priority.py`, `curation_state.py`, CURATION-PROTOCOL v0.2).

| Task | Detail | Size |
|------|--------|------|
| D4.1 | **Dependency-edge review campaign**: review all 188 `mathematically_requires`/`logically_requires` edges first (that is what LearningHub and PROFESSOR-J actually consume), in weekly batches of 25–50 composed by `curation_priority.py` (centrality → domain coverage); each batch lands as one PR with per-edge review commands and evidence per CURATION-PROTOCOL §3 | X |
| D4.2 | **Entity review pilot**: define the `draft → human_reviewed` checklist for entities (definition accurate? equation/symbol/unit correct? misconceptions valid? relationships consistent with connections?); run the first batch over `content/physics/mechanics/` (41 entities) with `provenance.reviewer` + `reviewed_at` set | M then X |
| D4.3 | **Evidence backfill**: the 599 no-evidence connections, ordered by family (causal/explanatory need real literature evidence; structural/dependency may use the documented axiomatic-evidence note); grow `sources/` from 3 records to one per actually-cited textbook (Halliday exists; add the others referenced in `provenance.source` strings) | X |
| D4.4 | **Merge/review gate (Scope C completion)**: make the human gate mechanical — ingestion proposals reach `content/`/`connections/` only via PR; CI enforces that promotion to `reviewed`/`canonical` carries `provenance.reviewed_by` + `review_history` (state machine already rejects skips); document the flow end-to-end (ingest → proposal → PR → review → canonicalize) | L |
| D4.5 | **Reviewer identity policy** (G4): choose pseudonymous role IDs (current behavior) or named humans; amend spec §8.2 + CONTRIBUTING to match whichever is chosen | S + gate |
| D4.6 | **Epistemic dashboard**: extend `epistemic_summary.py`/`curation_status.py` to also report entity review coverage and per-domain dependency-edge review %, so D4 progress is a number, not a feeling | S |

**Exit criteria (measurable trajectory, reviewable in `reports/`):**
- dependency edges (188) reviewed: 100%
- entities human_reviewed: ≥ mechanics batch (41) within the first cadence cycle
- connections without evidence: 599 → ≤ 300 by end of first cycle
- README/GOVERNANCE status line may then honestly drop "in early curation" for the covered slices.

### D5 — Consumer contract evolution & cross-repo completion (fixes R8 consumers, R16, R17; continues C-items) — L, spread

| Task | Detail | Size |
|------|--------|------|
| D5.1 | `export_version` **0.2** decision (connections/sources become a required part of the consumer contract), coordinated per `EXPORT-VERSION-MIGRATION-Q3.md` §4/§5: bump producer literals + LearningHub `SUPPORTED_EXPORT_VERSION` in the same release; ADR required | M + gate G6 |
| D5.2 | Explorer: build the graph from `connections[]` (keep `entities[].relationships` only as documented compatibility fallback); color/annotate by `review.status` (trust visualization) | M |
| D5.3 | LearningHub adapter: `getRelatedEntities` migrates from inline projection to `connections[]` (their repo, their PR — seam contract updated here first) | their repo |
| D5.4 | Refresh `STEMMA-CONSUMER-SEAM.md` to the real export shape (connection_count/source_count/connections/sources), `@learninghub/*` package names, real consumer status | S |
| D5.5 | Workspace rename completion (fixes R16): workspace `README.md`; `docs/umbrella/CONTRACTS.md` + `authority/exports-manifest.yaml` + `permission-manifest.yaml` + `capability-registry.json` + `agent-pool.yaml` paths/entries; `docs/WORKSPACE-ARCHITECTURE.md:71`; `docs/WORKSPACE-CICD.md:24` + workspace CI job key (and the workspace AGENTS "validate-steMMA" job-name mention); `docs/WORKSPACE-DEV-TASKS.md` examples | M |
| D5.6 | Skill rename + rewrite: `.agents/skills/learninghubstem-knowledge/` → `stemma-knowledge` (directory, catalog registration, and contents — its current validate command points at a nonexistent path) | S |
| D5.7 | PROFESSOR-J docs sweep: 79 refs, broken `../LearningHubSTEM` links, stale doc snippets (their repo, their PR — track here for sequencing only) | their repo |

**Exit criteria:** workspace greps find no live `LearningHubSTEM/` paths; the skill's
commands run verbatim; LearningHub + PROFESSOR-J contract tests green on the new export.

### D6 — Publication readiness (fixes R18, R19, R20) — LATER; gated by explicit activation (G7)

| Task | Detail |
|------|--------|
| D6.1 | Stable HTTPS URIs for `lhs:` IDs: replace `learninghubstem.example` `$id` placeholders and frozen schema titles in a governed minor schema change (ADR; the `lhs:` ID format itself does not change) |
| D6.2 | First release: tag + release notes (e.g. v1.1.0 content release), exercising `version_bump.py` → git tag → CI; fixes R18 |
| D6.3 | Interop emission (SEAM, derived only): optional JSON-LD/SKOS projection export (entities → `skos:Concept`/schema.org `DefinedTerm`; connections → typed properties), regenerable, never canonical — cheap given the relation registry |
| D6.4 | Entity type vocabulary decision (R20): add `phenomenon`/`model` to the entity enum (registry already references them) via ADR, or constrain the registry — one of the two, not the current drift |
| D6.5 | Coverage growth: engineering (1) and scientific-practice (2) to meaningful sets; earth-space (10) expanded; content additions follow D4.4's gated pipeline from day one |
| D6.6 | Research refresh: re-run the SOTA comparison with live web search once the harness `web_search` key is fixed (owner action), and refresh `docs/research/` + the consumer-mapping crosswalk pattern (1EdTech CASE crosswalk documented as consumer-side guidance) |

---

## 3. Sequencing

```
D1 ─┐
D2 ─┼─ (parallel, all inside STEMMA docs; one PR per phase or one combined PR)
D3 ─┘
D4 ─── starts immediately after D1 (or in parallel — review batches don't depend on doc fixes);
       this is the only X-cadence track; it continues for weeks.
D5 ─── after D3.3 (projection synced) and when D4.1 has momentum (real reviewed edges to export);
       D5.1 is the contract gate; D5.5/D5.6 can go anytime.
D6 ─── human-gated; do not start before D4 has a reviewed core and D1/D2 landed.
```

Suggested order of first PRs:
1. D1+D2 combined ("post-rename reconciliation") — one docs PR, biggest credibility win.
2. D3.1, D3.4, D3.7 (quick correctness trio).
3. D3.3 + D3.2 + D3.5/3.6 (the two decision-gated hygiene items behind G5).
4. D4.1 batch 1 (first 25–50 dependency edges) + D4.6 dashboard.
5. D5.5 + D5.6 (workspace + skill), D5.7 nudge.
6. D5.1 coordinated contract bump.
7. D6 upon activation.

**In-flight check (verified 2026-09-03):** STEMMA has no open PRs, and
`feat/math-domain-foundation`, `chore/licensing`, and `fix/lhs-schema-violations`
are all fully merged (0 commits ahead of `main`, local and remote) — nothing to
rebase against. The workspace project map's "phase-B curation active on
`feat/math-domain-foundation`" status is stale drift, corrected by D2.2/D5.5.

## 4. Explicitly out of scope (unchanged)

Full ontology, multilingual implementation, publication infrastructure, semantic-web stack as
canonical, consumer APIs, microservices, cloud, auth, payments, analytics, vector/graph
databases, recommendation engines, shared platform services, any `lhs:` renumbering/reuse,
mass auto-canonicalization, pedagogy/curriculum in canonical content.

## 5. Human decision gates (required before the marked tasks)

| Gate | Decision | Unblocks |
|------|----------|----------|
| G1 | Retire "ACTIVATE LEARNINGHUBSTEM MVP"; adopt "ACTIVATE STEMMA MVP" (ADR-0020) | D1.3 |
| G2 | Confirm consumer naming: "LearningHub" replaces STEM-TUITION in STEMMA docs | D1.7 |
| G3 | Confirm licensing approval moment; ADR-0001 status → decided | D2.1 |
| G4 | Reviewer identity policy: pseudonymous roles vs named humans | D4.5 |
| G5 | Migrate colon filenames (recommended) vs document the Windows limitation | D3.5 |
| G6 | Approve `export_version` 0.2 timing (requires LearningHub adapter co-release) | D5.1 |
| G7 | Activate publication track (URIs, first tag, interop emission) | D6 |

## 6. Risks

| Risk | Mitigation |
|------|------------|
| Review bottleneck persists (single reviewer) | D4 is cadence-based with batch PRs; dashboard makes the queue visible; protocol allows axiomatic-evidence notes where legitimate |
| Inline/connection drift grows during D4 | D3.3 gate lands first; new relationships enter via connections only |
| Rename sweeps break consumers | A9-style contract baseline before/after each sweep (pattern already proven in Scope A) |
| Publication pressure grows scope | D6 is gated (G7); OUT OF SCOPE list restated in §4 |
| Roadmap goes stale again | D2.3 folds this plan into the roadmap with per-phase activation gates |

---

*Prepared from the 2026-09-03 review evidence; all file:line references were verified against
the working tree at `main` (`verify_all` exit 0). This document is AI-drafted: it becomes
canonical only through human review and the repo's decision-record process.*
