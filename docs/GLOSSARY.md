# GLOSSARY — STEM Ecosystem Workspace

Only terms that recur across the workspace. See the authoritative definitions in
`docs/GOVERNANCE.md` and `docs/STEMMA-SPECIFICATION.md`.

| Term | Meaning |
|------|---------|
| **STEMMA** | The open, structured, reusable STEM knowledge foundation; independent of any product. |
| **canonical knowledge** | The source-of-truth STEM knowledge in `STEMMA/content/` (Markdown + YAML frontmatter), version-controlled. |
| **derived artifact** | Output regenerable from canonical content (JSON export, search indexes, embeddings, APIs); never the source of truth. |
| **knowledge entity** | One canonical node: a Concept, Quantity, Unit, Law, Equation, or Misconception with a stable ID. |
| **stable ID** | Identifier `lhs:<domain>.<slug>` that is never reassigned and is independent of files, curriculum, and products. |
| **consumer** | Anything that builds on STEMMA: a curriculum, a product, a research tool, an AI system. |
| **product** | An application that presents or uses knowledge (STEM-TUITION, JARVIS, STEM-GAME, STEM Lab, 3D-Ludo). |
| **curriculum** | How a particular educational system organizes knowledge (Nepal, CBSE, GCSE, A-Level, IB…); a consumer. |
| **curriculum mapping** | The consumer-owned act of connecting canonical IDs to a course/grade/unit. |
| **provenance** | Record of how content came to be (AI-drafted? source/citation? named reviewer). |
| **source_kind** | Controlled vocabulary for the class of a provenance source (textbook, academic, institutional, standards, AI-assisted…). |
| **review status** | Lifecycle state: draft → machine_validated → human_reviewed → canonical → deprecated/superseded. |
| **decision record** | A concise record of a foundational decision (context, decision, alternatives, reason, consequences, status) in `docs/decisions/`. |
| **freeze** | A rule meaning foundational changes require a documented governance decision — not "never change". |
| **schema version** | Version of `schema/concept.schema.json`; separate from export version and content release. |
| **export version** | Version of the `exports/knowledge.json` contract; separate from schema version and content release. |
| **content release** | The knowledge set itself (entities added/updated/deprecated); not a contract change. |
| **LICENSE DECISION PENDING** | Marker used until a license is chosen; no license claim is made without human approval. |
| **pedagogy** | How knowledge is taught/learned; pedagogical relationships are not canonical in v0.1. |
| **ecosystem invariant** | A Level-1 rule that project governance may not redefine (STEMMA independence, curriculum external, products as consumers…). |
| **NOW** | Work required by the current milestone; implement. |
| **SEAM** | Small interface/adapter/contract protecting a known future change; implement only when inexpensive. |
| **LATER** | Described by the architecture but not required now; document, do not implement. |
| **OUT OF SCOPE** | Not relevant now; do not implement. |