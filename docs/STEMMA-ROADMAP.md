# STEMMA — ROADMAP

**Status:** live foundation in early curation — **224 draft entities; 50 canonical assertions
(7.6%); zero human-reviewed entities** (machine-checked by `scripts/status_truth.py`). The
roadmap is **not authorization to implement future phases**: each phase requires an explicit
human activation decision, and the forward plan is now
**[`STEMMA-IMPLEMENTATION-PLAN-v2.md`](STEMMA-IMPLEMENTATION-PLAN-v2.md)** (E-series), derived
from [`ARCHITECTURE-AUDIT-v1.0.md`](ARCHITECTURE-AUDIT-v1.0.md).

Related: `docs/STEMMA-SPECIFICATION.md`, `docs/GOVERNANCE.md`, `docs/decisions/`.

---

## Where the work actually happened

The original Phase 0–3 table below is retained as history. In practice the repository advanced
through three rename/hardening scopes (A–C, see `docs/HISTORY-RENAME.md` and ADR-0019) and four
post-audit waves (plan v2 E-series; ADRs 0020–0025). **The forward work is plan v2 E0–E8**, and
each E-task carries its own activation/gate status.

| Phase | Name | Content | Status |
|-------|------|---------|--------|
| 0 | Governance + specification + seed proof | `AGENTS.md`, governance, northstar, spec, glossary; schema + seed entities + validator + export | ✅ DONE (proof only) |
| 1 | **Foundation Definition & Freeze** | licensing, canonical representation, entity model, stable identity, lifecycle, provenance, relationship vocabulary, knowledge≠curriculum, knowledge≠pedagogy, export/consumer contract, versioning, multilingual principle, decision records, freeze rule | ✅ DONE — license **decided 2026-09-02** (ADR-0001: CC BY 4.0 content / MIT code) |
| 2 | First independent consumer adapter + end-to-end consumption proof | one consumer maps canonical IDs to its own curriculum without touching canonical content | ✅ DONE — LearningHub (formerly STEM-TUITION) shell consumes `exports/knowledge.json` via `apps/shell/src/lib/lhs-adapter.ts`; vertical slice (Newton's Second Law) live in `#lhs-demo`. See `docs/STEMMA-CONSUMER-SEAM.md` |
| 3+ | Governance enforcement (CI-level checks), ontology expansion, multilingual implementation | — | 🔵 LATER — superseded by plan v2 E-series (E1–E8), which is the forward plan |

The foundation is **implemented as a foundation and proof** (per specification §1). It does not
activate the MVP. The full MVP stays inactive until a human explicitly says:

> **ACTIVATE STEMMA MVP**

(The previous trigger phrase `"ACTIVATE LEARNINGHUBSTEM MVP"` is retired — see ADR-0025.)

---

## Human decisions gating Phase 1 completion

- Knowledge/content license (CC BY 4.0 vs CC0) — **decided 2026-09-02: CC BY 4.0**
- Code/tooling license (MIT vs Apache-2.0) — **decided 2026-09-02: MIT**
- Initial domain scope
- **Activation of the Phase 1 foundation freeze**
- Final canonical format, entity vocabulary, relationship vocabulary, multilingual policy approvals

Full list: specification §16. Forward-plan gates (G-A … G-H): plan v2 §6.

---

## Scope guardrails

Always classify work against `docs/GOVERNANCE.md` §3:

- **NOW** — current phase only.
- **SEAM** — small contracts (versioned export, consumer mapping example, validation boundary).
- **LATER** — full ontology, broad coverage, multilingual, publication infrastructure,
  semantic-web stack, consumer APIs, CI policy system.
- **OUT OF SCOPE** — microservices, cloud, auth, payments, analytics, vector/graph databases,
  recommendation engines, shared platform services.
