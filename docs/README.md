# LearningHubSTEM — Documentation

Governance, vision, and technical ground truth for this repository, all living inside it
so the repo is self-contained.

| Document | What it is |
|----------|-----------|
| `NORTHSTAR.md` | The one-sentence north star and the three boundaries that must never blur. |
| `MASTER-VISION-LearningHubSTEM.md` | The full, authoritative vision. |
| `GOVERNANCE.md` | Governance precedence and rules that apply to this repository. |
| `LEARNINGHUBSTEM-SPECIFICATION.md` | Technical specification: format, IDs, entity model, validation, consumer contract. |
| `LEARNINGHUBSTEM-ROADMAP.md` | Phased plan; each phase requires explicit activation. |
| `LEARNINGHUBSTEM-CONSUMER-SEAM.md` | The versioned export → adapter → consumer integration seam. |
| `GLOSSARY.md` | Terms that recur across the ecosystem. |
| `REVIEW-RESPONSE.md` | Architectural reconciliation record (decision trail). |
| `decisions/` | Foundation decision records (ADR-style, `00NN-*.md`). |

## Reading order

1. `NORTHSTAR.md` — what this must remain, always.
2. `LEARNINGHUBSTEM-SPECIFICATION.md` — the technical contract.
3. `GOVERNANCE.md` — the rules.
4. `decisions/README.md` — how decisions are made and recorded here.

## Ground rule

Derived artifacts (`exports/`) are regenerable and never the source of truth; canonical
content lives in `content/`. Documents here describe the system; they do not replace it.