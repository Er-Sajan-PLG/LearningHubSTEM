# DECISION 0003 — Stable identity

- **Date:** 2026-08-12
- **Status:** decided (documented)
- **Related:** specification §3

## Context

Identifiers must survive renames, reordering, curriculum differences, and product differences.

## Alternatives considered

- Numeric/database IDs (rejected: not stable across systems)
- Path-dependent IDs (rejected: files move)
- Namespaced `lhs:<domain>.<slug>` ← **chosen**

## Decision

IDs are `lhs:<domain>.<slug>`, globally unique, stable, never reassigned, never reused,
machine- and human-readable, independent of files/curriculum/products. Rename ≠ ID change.
Split/merge/replace handled by deprecation + `deprecated_by` + `aliases` (never in-place mutation).

## Reason

Namespaced, ASCII, regex-validated IDs give uniqueness and readability without infrastructure.

## Consequences

- Deprecated IDs remain reserved forever; alias handling is explicit.
- Validator enforces ID format, uniqueness, and alias validity.

## Status

**decided (documented).**
