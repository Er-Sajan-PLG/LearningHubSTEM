# STEMMA — Documentation

Governance, vision, and technical ground truth for this repository, all living inside it
so the repo is self-contained.

| Document | What it is |
|----------|-----------|
| `NORTHSTAR.md` | The one-sentence north star and the three boundaries that must never blur. |
| `MASTER-VISION.md` | The full, authoritative vision. |
| `GOVERNANCE.md` | Governance precedence and rules that apply to this repository. |
| `STEMMA-SPECIFICATION.md` | Technical specification: format, IDs, entity model, validation, consumer contract. |
| `STEMMA-ROADMAP.md` | Phased plan; each phase requires explicit activation. |
| `STEMMA-CONSUMER-SEAM.md` | The versioned export → adapter → consumer integration seam. |
| `GLOSSARY.md` | Terms that recur across the ecosystem. |
| `REVIEW-RESPONSE.md` | Architectural reconciliation record (decision trail). |
| `decisions/` | Foundation decision records (ADR-style, `00NN-*.md`). |

## Reading order

1. `NORTHSTAR.md` — what this must remain, always.
2. `STEMMA-SPECIFICATION.md` — the technical contract.
3. `GOVERNANCE.md` — the rules.
4. `decisions/README.md` — how decisions are made and recorded here.
5. `CONTRIBUTING.md` — how to contribute (open-source readiness; IDs & stability contract).

## Ground rule

Derived artifacts (`exports/`) are regenerable and never the source of truth; canonical
content lives in `content/`. Documents here describe the system; they do not replace it.