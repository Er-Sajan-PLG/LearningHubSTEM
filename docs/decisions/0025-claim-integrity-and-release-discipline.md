# DECISION 0025 — Claim integrity (signatures, edit-in-place, triple immutability) + release discipline

- **Date:** 2026-09-05
- **Status:** decided (implemented with this change; ungated plan-v2 items only)
- **Related:** ADR-0003 (stable ids), ADR-0011 (connections), ADR-0016 (metadata rework),
  ADR-0020 (connections-only truth), ADR-0022 (version source / deterministic exports),
  ADR-0023 (export contract v1.0), `docs/STEMMA-IMPLEMENTATION-PLAN-v2.md`
  (E0.2, E0.3, E1.6, E4.3, E4.4, E4.5, E5.3, E5.5),
  `docs/ARCHITECTURE-AUDIT-v1.0.md` (F1, F5, F7, F11)

## Context

After ADR-0020–0023 the *shape* of the knowledge base is enforced, but three integrity
questions were still unmechanised, and all three are ways trust silently decays:

1. **Duplicate claims (F7).** Two connection files may assert the same triple with the same
   polarity and qualifiers. Consumers then double-count evidence, and "which one is canonical?"
   has no answer. ADR-0016 named a claim signature; nothing computed one.
2. **Edit in place (F5).** A connection or entity that a human reviewed could be edited
   afterwards with no lifecycle transition. The review then vouches for text that no longer
   exists — the most corrosive possible failure for an epistemic foundation.
3. **Triple rewriting (F11).** `check_id_immutability.py` protected entity ids only. A
   connection id could be repointed at a different source/relation/target, silently changing
   what a reviewed, exported assertion means.

Two supporting gaps: the only release signal was a `VERSION` file no one could verify a
checkout against (F5/R18), and schema changes had no migration log (F6). Separately, the
explorer still built its graph from the deprecated inline projection (F1 at the view layer),
and the licensing record still said "PENDING" while `LICENSE`/`LICENSE-CODE` were committed.

## Decision

### A. Claim signature and duplicate-claim gate (E4.3)

1. A **claim signature** is `sha256(source | relation | target | polarity | qualifiers)` with
   qualifiers normalised (stringified, deduplicated, sorted). It is **derived** — computed by
   `scripts/validate.py:claim_signature`, never stored in canonical YAML.
2. Two **active** connections may not share a claim signature. Fix by merging them, adding a
   distinguishing `context.qualifiers` entry, or superseding one via `lifecycle.replaced_by`.
3. Retracted/superseded assertions are exempt: history may legitimately repeat a triple.

### B. Content hashes and edit-in-place detection (E4.4)

4. `validate.object_content_hash` hashes an object's **substance**, excluding bookkeeping that
   legitimately changes after review (`provenance`, `updated_at`, `lifecycle`, `version`).
5. `scripts/check_content_hashes.py` maintains the tracked ledger
   `reports/content-hash-ledger.json` for every object at `reviewed`/`human_reviewed`/`canonical`.
   Substance changed **without** a new review event → CI fails. Changed **with** a new review
   event → legitimate, ledger updated. Newly reviewed → entry created.
6. The ledger is deterministic (sorted, no wall-clock), so CI's `git diff --exit-code` step
   catches a stale one exactly as it does for exports.

### C. Connection-triple immutability (E4.5)

7. `scripts/check_id_immutability.py` now also reconstructs `connections/` from git history.
   A connection id's identity is its **triple**; rewriting `source`, `relation`, or `target`
   under an existing id is a violation, as is deleting a connection outright (retract it
   instead). History reconstruction uses one `ls-tree` + `cat-file --batch` pass per commit,
   so the check stays fast.

### D. Release discipline (E5.3, E5.5)

8. `scripts/release_manifest.py` writes `exports/release-manifest.json`: per-file SHA-256 of
   every canonical + contract file, the aggregate `content_hash` (same algorithm as the export,
   so the two can never disagree), the version triple, and counts. Deterministic.
9. **Tagging remains a human action.** A release asserts something about reviewed knowledge;
   only a human may claim that. `--tag-command` prints the exact commands.
   `docs/CONTENT-RELEASES.md` documents the release contents, the verification recipe, and the
   changelog.
10. `docs/MIGRATIONS.md` logs every schema/registry/vocabulary/contract change with its
    migration script and old-vs-new validity answers; a schema PR without a row is incomplete.

### E. Explorer reads connections (E1.6) and licensing record (E0.2/E0.3)

11. The explorer's `collectEdges()` builds all edges from `connections[]`; the inline
    projection is a documented fallback for pre-v1.0 exports and is then marked `unknown` trust.
    Each edge carries `reviewStatus` and a trust-graded `opacity` (`REVIEW_OPACITY`) that
    `graph-view.ts` renders — an unreviewed assertion must not look as solid as a canonical one.
12. ADR-0001 is **decided** (CC BY 4.0 content / MIT code, matching the committed license
    files); the "LICENSE DECISION PENDING" marker is retired from the specification, glossary,
    and consumer seam. Remaining old-brand leftovers (R1) are cleared.

## Reason

Every rule above is enforced by code that ships in this change, per plan v2 §1 ("every ADR
lands with its enforcement"). None of them require a human gate: they add no canonical field,
change no contract version, and touch no canonical content — 224 entities, 654 connections,
3 sources are byte-identical before and after.

## Consequences

- New failure modes in CI, all actionable: duplicate claim, edit-in-place, rewritten triple,
  deleted connection, stale ledger, stale release manifest.
- `reports/content-hash-ledger.json` and `exports/release-manifest.json` are derived and
  tracked; regenerate with `python3 scripts/verify_all.py`.
- Adding a reviewer or a review event to an object is always allowed; rewriting a reviewed
  claim is not.
- Gated items (G-B entity types, G-C math layer, G-D reviewer identity, G-E filenames/exports
  tracking, G-F publication, G-H claim rank) are untouched and still await human decisions.
