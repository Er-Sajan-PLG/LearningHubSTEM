# LEARNINGHUBSTEM — ROADMAP

**Status:** Phasing for the foundation. **The roadmap is not authorization to implement future
phases.** Each phase requires an explicit human activation decision.

Related: `docs/LEARNINGHUBSTEM-SPECIFICATION.md`, `docs/GOVERNANCE.md`, `docs/decisions/`.

---

## Phases

| Phase | Name | Content | Status |
|-------|------|---------|--------|
| 0 | Governance + specification + seed proof | `AGENTS.md`, governance, northstar, spec, glossary; schema + 5 seed entities + validator + export | ✅ DONE (proof only) |
| 1 | **Foundation Definition & Freeze** | licenses (pending), canonical representation, entity model, stable identity, lifecycle, provenance, relationship vocabulary, knowledge≠curriculum, knowledge≠pedagogy, export/consumer contract, versioning, multilingual principle, decision records, freeze rule | ✅ DONE (definition & freeze docs); license decisions **PENDING human approval** |
| 2 | First independent consumer adapter + end-to-end consumption proof | one consumer maps canonical IDs to its own curriculum without touching canonical content | ✅ DONE — STEM-TUITION shell consumes `exports/knowledge.json` via `apps/shell/src/lib/lhs-adapter.ts`; vertical slice (Newton's Second Law) live in `#lhs-demo`. See `docs/LEARNINGHUBSTEM-CONSUMER-SEAM.md` |
| 3+ | Governance enforcement (CI-level checks), ontology expansion, multilingual implementation | — | 🔵 LATER |

Phases 0–1 are implemented **as a foundation and proof** (per specification §1). They do not
activate the MVP. The full MVP stays inactive until a human explicitly says:

> **ACTIVATE LEARNINGHUBSTEM MVP**

---

## Human decisions gating Phase 1 completion

- Knowledge/content license (CC BY 4.0 vs CC0)
- Code/tooling license (MIT vs Apache-2.0)
- Initial domain scope
- **Activation of the Phase 1 foundation freeze**
- Final canonical format, entity vocabulary, relationship vocabulary, multilingual policy approvals

Full list: specification §16.

---

## Scope guardrails

Always classify work against `docs/GOVERNANCE.md` §3:

- **NOW** — current phase only.
- **SEAM** — small contracts (versioned export, consumer mapping example, validation boundary).
- **LATER** — full ontology, broad coverage, multilingual, publication infrastructure,
  semantic-web stack, consumer APIs, CI policy system.
- **OUT OF SCOPE** — microservices, cloud, auth, payments, analytics, vector/graph databases,
  recommendation engines, shared platform services.