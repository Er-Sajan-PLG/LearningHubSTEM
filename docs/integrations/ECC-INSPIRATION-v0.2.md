# ECC Inspiration for STEMMA — v0.2

**Source:** https://github.com/affaan-m/ECC — agent harness performance optimization system (`plan -> test -> implement -> review -> verify -> remember -> improve`), 68 agents, 286 skills, hooks/memory/AgentShield.

**Intent:** Integrate ECC *workflow and quality* inspiration into LHS without adopting ECC as canonical truth, RDF/GraphDB, or full harness. LHS remains Markdown/YAML canonical, human-governed.

## 1. Mapping ECC → LHS

| ECC | LHS Interpretation |
|-----|-------------------|
| `plan` | ADR-011..015 + CURATION-PROTOCOL-v0.2 before code; `docs/curation/` as plan artifact |
| `test` | `scripts/validate.py` + `tests/phase-b/` + `tests/curation/` — schema + semantic + provenance + boundary tests; TDD for scripts |
| `implement` | Small deterministic increments: `migrate_relationships.py`, `create_curated_b3_b6.py`, `graph_analysis.py` — idempotent, no bulk canonicalization |
| `review` | `scripts/review_queue.py` + `scripts/graph_policy.py` + human review gate (D17); no `canonical` without `reviewed_by` human |
| `verify` | `validate.py` + `epistemic_summary.py` + `integrity_anomalies.py` + `graph_analysis` determinism check; CI-equivalent via `verify` script |
| `remember` | `reports/*.md/*.json` + `exports/knowledge*.json` + `provenance.review_history` as durable memory; epistemic summary as snapshot |
| `improve` | Curation pilot retrospective (`reports/curation-pilot-v0.2.md`), `phase-b-validation`, continuous reclassification queue |

## 2. Concrete Integrations (Implemented / To Apply)

### Implemented (Phase A–C)
- **Hooks/memory analogue:** `scripts/validate.py` as pre-commit gate (schema/domain/range, bridge scope-aware, cycle detection); `reports/` as memory.
- **Skills analogue:** Deterministic helpers — `reconcile_migration.py` (audit), `classify_related_to.py` (candidate generation, never auto-canonicalize), `review_queue.py` (prioritization), `graph_policy.should_include_connection` (single inclusion policy).
- **AgentShield analogue:** `integrity_anomalies.py` (ERROR/WARNING/INFO) as security/integrity scan; provenance origin preservation as anti-fabrication guard.
- **Rules analogue:** `schema/relation-registry.yaml` as selective, always-loaded standards; `schema/vocabularies/` as controlled terms.

### To Integrate Before Phase D Continuation (D2/D3/D13/D15)
1. **TDD for curation state machine:** `scripts/curation_state.py` with `pytest`-style tests in `tests/curation/` — valid/invalid transitions, reviewer-required, origin-preserved.
2. **Review interface as skill:** `scripts/review.py` CLI — `review --list`, `--show <id>`, `--accept`, `--reject`, `--edit`, `--canonicalize` — reads derived analytics, writes only approved canonical metadata; shows source/target descriptions without manual file opening.
3. **Verify hook chain:** `make verify` or `scripts/verify_all.py` → `validate.py` → `epistemic_summary.py` → `integrity_anomalies.py` → `graph_analysis.py` → `tests/curation/` → determinism/idempotence check (single command, like ECC hooks).
4. **Remember/improve loop:** After each pilot batch, update `reports/curation-status-v0.2.json/.md` and `reports/curation-pilot-v0.2.md` with effort/ambiguity/false-positive/schema friction; feed back into `relation-registry` or `CURATION-PROTOCOL` only via ADR.
5. **Security/provenance scan:** Extend `integrity_anomalies` to flag LLM→canonical without human, missing evidence per family, and confidence without basis — analogous to AgentShield prompt/secret scanning.

## 3. What LHS Will NOT Take From ECC (Governance Freeze)
- No RDF/OWL/GraphDB/Neo4j/vector DB as canonical (ECC supports many harnesses; LHS stays lightweight).
- No mass auto-canonicalization (ECC's 68 agents ≠ automatic promotion; LHS requires human `reviewed_by`).
- No `PageRank` as truth (ECC centrality is analytics only).
- No full harness install (`/plugin`, hooks-runtime) — LHS uses repository-local scripts and `graph_policy` as the single inclusion decision point.

## 4. Immediate Application to Phase D
- D2 review interface will follow ECC `/code-review` pattern: fresh context, check against registry, evidence, provenance, then human verdict.
- D3 state machine will be tested first (ECC `test -> implement`), then review UI built on it.
- D13 exports will use `graph_policy` (`all`/`reviewed`/`canonical`/`trusted`) — one module, like ECC's selective rules.
- D15 tests will mirror ECC's 997-test discipline: state machine, review integrity, evidence, provenance, export, idempotence, determinism.

## 5. Next Step
Proceed with D2/D3 (state machine + review CLI) using TDD, then resume pilot canonicalization (D16) with the verify→remember loop after each batch.

Reference: ECC workflow `plan -> test -> implement -> review -> verify -> remember -> improve` (README).
