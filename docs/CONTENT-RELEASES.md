# STEMMA — Content releases

**Status:** Active · **Related:** `docs/VERSIONING.md`, `docs/MIGRATIONS.md`,
`scripts/release_manifest.py`, `docs/STEMMA-IMPLEMENTATION-PLAN-v2.md` (E5.3)

A **content release** is a named, verifiable state of the canonical knowledge —
`content/` + `connections/` + `sources/` — pinned together with the schemas and version
constants that give it meaning. Before E5.3 the only release signal was the `VERSION`
file, which a consumer could not check a checkout against (audit F5 / R18).

## What a release consists of

| Artifact | Meaning |
|----------|---------|
| Git tag `content-vX.Y.Z` | Immutable pointer to the released commit (human action). |
| `exports/release-manifest.json` | Per-file SHA-256 of every canonical + contract file, the aggregate `content_hash`, version triple, counts. Generated. |
| This changelog | What changed epistemically, in human terms. |
| `exports/knowledge.json` | The derived consumer artifact, stamping the same `content_hash`. |

The manifest's `content_hash` is computed with the *same* algorithm as the export's, so the
two can never disagree; a mismatch means a stale artifact and CI fails.

## Verifying a release

```bash
git checkout content-v2.0.0
python3 scripts/release_manifest.py --check      # tracked manifest matches this tree
python3 scripts/verify_all.py                    # full gate, exit 0
python3 -c "import json;m=json.load(open('exports/release-manifest.json'));\
e=json.load(open('exports/knowledge.json'));assert m['content_hash']==e['content_hash']"
```

## Cutting a release (human)

1. `python3 scripts/verify_all.py` → exit 0.
2. `python3 scripts/release_manifest.py --tag-command` — regenerates the manifest and prints
   the exact tag commands.
3. Add a section to the changelog below (reviewed counts, not just file counts).
4. Run the printed `git tag -a … && git push origin …`.

Tagging is deliberately **not** automated: a release asserts something about reviewed
knowledge, and only a human may make that claim (AGENTS.md ground rule 3).

## Changelog

### Unreleased

- Plan v2 wave 5: licensing record reconciled (ADR-0001 `decided`), rename leftovers cleared,
  claim signatures + duplicate-claim gate (E4.3), edit-in-place detection (E4.4),
  connection-triple immutability (E4.5), explorer graph reads `connections[]` with trust-graded
  edges (E1.6), release manifest + this changelog (E5.3), `docs/MIGRATIONS.md` (E5.5).
- No canonical content changed: 224 entities, 654 connections, 3 sources.

### 2.0.0 — export contract v1.0 (2026-09-04)

- Export contract **1.0**: `connections[]` and `sources[]` are required members (ADR-0023);
  compatibility view `exports/knowledge.compat-0.1.json` emitted during the consumer co-release.
- `external_ids` first-class and format-checked; Wikidata QIDs seeded for the 41 mechanics entities.
- `schema/agent-registry.yaml`: every provenance agent id resolves.
- Content: 224 entities (all `draft`), 654 connections, 50 canonical assertions, 3 sources.

### Earlier

Pre-1.0 states were not tagged; see `docs/MIGRATIONS.md` (M1–M6) and the ADR series for the
history of the schema and registry as they stood before the contract stabilised.
