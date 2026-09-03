# STEMMA — Documentation

Governance, vision, and technical ground truth for this repository, all living inside it
so the repo is self-contained.

| Document | What it is |
|----------|-----------|
| `NORTHSTAR.md` | The one-sentence north star and the three boundaries that must never blur. |
| `MASTER-VISION.md` | The full, authoritative vision. |
| `GOVERNANCE.md` | Governance precedence and rules that apply to this repository. |
| `STEMMA-SPECIFICATION.md` | Technical specification: format, IDs, entity model, validation, consumer contract. |
| **`ARCHITECTURE-AUDIT-v1.0.md`** | **The latest architecture audit (2026-09-03) — supersedes `ARCHITECTURE-REVIEW-v0.3.md` (kept for history).** |
| **`STEMMA-IMPLEMENTATION-PLAN-v2.md`** | **The forward implementation plan (E-series), derived from audit v1.0 — supersedes `STEMMA-IMPLEMENTATION-PLAN.md` (Scope D).** |
| `ARCHITECTURE-REVIEW-v0.3.md` | Prior internal review (superseded; findings C.1–C.10 traceable). |
| `STEMMA-IMPLEMENTATION-PLAN.md` | Prior Scope D plan (superseded; R-number findings register still referenced). |
| `STEMMA-ROADMAP.md` | Phased plan; each phase requires explicit activation. |
| `STEMMA-CONSUMER-SEAM.md` | The versioned export → adapter → consumer integration seam. |
| `EXPORT-VERSION-MIGRATION-Q3.md` | The consumer export-version migration plan (compat window, co-release). |
| `RELATIONSHIP-MODEL-ADR-0011-note.md` | Note on the connection-assertion model and its consumer migration. |
| `VERSIONING.md` | Three-track versioning (schema / export / content release). |
| `HISTORY-RENAME.md` | Why git history still says LearningHubSTEM; the rename boundary. |
| `SOURCES.md` | Visible inventory of sources and historical attributions. |
| `INGESTION.md` | Document → review-ready proposal ingestion pipeline. |
| `AXIOM-KERNEL-PLAN.md` | Axiom-kernel plan (FAIR principles, release gates). |
| `grade12-curriculum-mapping.md` | Consumer-owned grade-12 curriculum mapping (never canonical). |
| `GLOSSARY.md` | Terms that recur across the ecosystem. |
| `REVIEW-RESPONSE.md` | Architectural reconciliation record (decision trail). |
| `CONTRIBUTING.md` | Contribution rules; IDs & stability contract. |
| `decisions/` | Foundation decision records (ADR-style, `00NN-*.md`; index in `decisions/README.md`). |
| `curation/` | Review protocol (`CURATION-PROTOCOL-v0.2.md`). |
| `metadata/` | Metadata audit / design / gap-matrix records. |
| `research/` | Research notes (e.g. physics grade-10 research). |
| `integrations/` | Integration inspiration notes (e.g. ECC). |
| `../schema/agent-registry.yaml` | Every provenance agent id (human/process/llm/unknown) — validator-resolved (ADR-0023). |
| `../schema/export.schema.json` | Export contract v1.0 shape (ADR-0023). |
| `../reports/e61-dependency-campaign/` | E6.1 dependency-edge review worksheets + dashboard (generated; decisions are human). |

## Reading order

1. `NORTHSTAR.md` — what this must remain, always.
2. `STEMMA-SPECIFICATION.md` — the technical contract.
3. `GOVERNANCE.md` — the rules.
4. `decisions/README.md` — how decisions are made and recorded here.
5. `CONTRIBUTING.md` — how to contribute (open-source readiness; IDs & stability contract).

## Ground rule

Derived artifacts (`exports/`) are regenerable and never the source of truth; canonical
content lives in `content/`. Documents here describe the system; they do not replace it.