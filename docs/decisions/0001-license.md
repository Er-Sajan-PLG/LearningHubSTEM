# DECISION 0001 — Licensing

- **Date:** 2026-08-12
- **Status:** PENDING human approval
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

Marked **LICENSE DECISION PENDING**. No LICENSE file is created until the human decides.

## Reason

CC BY 4.0 balances the "anyone can build on it" goal with durable attribution, which supports the
foundation's provenance principle. MIT keeps tooling friction low.

## Consequences

- No license claim is made anywhere until approval.
- Once decided: add the chosen license files and update the specification §15.

## Status

**PENDING human approval** (items 1 and 2 of the human-decision list).
