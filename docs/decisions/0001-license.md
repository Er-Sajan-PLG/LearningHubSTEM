# DECISION 0001 — Licensing

- **Date:** 2026-08-12
- **Status:** decided (human approval recorded 2026-09-03; LICENSE + LICENSE-CODE present in the repository)
- **Related:** specification §15

## Context

"Open" needs legal grounding. No LICENSE file exists anywhere in the workspace. Two tracks:
knowledge/content and code/tooling. This decision must remain a human call.

## Alternatives considered

| Track | Candidate | Implication |
|-------|-----------|-------------|
| Knowledge/content | **CC BY 4.0** | attribution required; reusable/remixable/commercial with credit; interoperable; attribution preserved |
| Knowledge/content | **CC0** | public-domain dedication; maximal openness; attribution not required; irrevocable |
| Code/tooling | **MIT** | permissive, minimal, widely understood; no patent grant |
| Code/tooling | **Apache-2.0** | permissive + explicit patent grant + contribution terms |

## Decision

Recommendation (NOT finalized):

- Knowledge/content → **CC BY 4.0** (preserves attribution for an open knowledge foundation while
  enabling reuse).
- Code/tooling → **MIT** (simplest fit for the small validator/scripts; Apache-2.0 if external
  contributors or patent clarity become important).

**Approved by the owner (2026-09-03)** as recommended:

- Knowledge/content → **CC BY 4.0** — `LICENSE` (covers `content/`, `connections/`, `sources/`, `docs/`).
- Code/tooling → **MIT** — `LICENSE-CODE` (covers `scripts/`, `schema/`, `tests/`, `explorer/`).

Both license files are committed; `README.md` §License states the split. The former
**LICENSE DECISION PENDING** marker is retired repository-wide (plan v2 E0.2).

## Reason

CC BY 4.0 balances the "anyone can build on it" goal with durable attribution, which supports the
foundation's provenance principle. MIT keeps tooling friction low.

## Consequences

- `LICENSE` (CC BY 4.0) and `LICENSE-CODE` (MIT) are the authoritative license statements.
- Specification §15, `GLOSSARY.md`, and `STEMMA-CONSUMER-SEAM.md` no longer say "pending";
  human-decision items 1 and 2 are closed.
- Re-licensing content is a new decision record, never an edit to this one.

## Status

**decided** — items 1 and 2 of the human-decision list are closed (2026-09-03).
