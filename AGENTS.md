# AGENTS.md — STEMMA

Operating instructions for humans and AI agents working inside this repository.
Workspace-level rules are in the workspace root (`/home/sajan/Projects/AGENTS.md` and its
`docs/`); this file governs this repository (governance Level 2).

## North star (this repo must stay)

> **STEMMA is an open, structured, reusable STEM knowledge foundation.**
> Curriculum is external. Products are external. Learning experiences are external.
> AI agents are consumers. LearningHub is one consumer — never a controller.

Read `docs/NORTHSTAR.md` for the three boundaries that must never blur.

## Ground rules

1. Canonical knowledge lives only in `content/`. Everything under `exports/` is DERIVED and
   regenerable, never the source of truth.
2. No curriculum, grade, course, or product appears in `content/`.
3. AI-drafted content stays `status: draft` until a human reviews it.
4. Stable IDs are never reused or silently reassigned.
5. Governance precedence: this repo's `docs/GOVERNANCE.md` → outer workspace rules → agent discretion.
6. Build small: verified increment + clean boundary + tests + docs, not speculative infrastructure.
7. Do not expand scope silently. Classify work NOW / SEAM / LATER / OUT OF SCOPE and state a short plan.
8. No secrets in code or docs. Leave a trail (decision records in `docs/decisions/`).

## Verification

```bash
python3 scripts/validate.py        # exit 0 = valid; regenerates exports/knowledge.json
python3 scripts/verify_all.py      # authoritative chain: validator + status-truth + reports + tests
```

Explorer (E1.6, ADR-0020/0023/0025): `npm --prefix explorer run verify` asserts the graph is
projected from `connections[]` with per-edge trust annotation; `npm --prefix explorer run dev`
(or `build`) syncs the export copy the explorer reads first (E7.4 — the validator no longer
writes into `explorer/`).

`verify_all.py` is what CI runs. It includes the cross-object gates added by ADR-0020–0025
(inline↔connections projection sync, registry coherence, context vocabularies, cycle detection,
inference/confidence rules, deterministic exports, README status-truth, export-contract schema,
agent-registry resolution, `external_ids` formats, claim signatures/duplicate-claim detection,
connection-triple immutability). Every agent id in provenance must exist in
`schema/agent-registry.yaml`; add the entry in the same PR that first uses it.

Claim identity (ADR-0026): `connections[].claim_signature` is **derived** (`sha256(source|relation|target|polarity|sorted qualifiers)`) — never hand-write it into canonical YAML;
duplicate active claims fail the gate. An assertion's `(source, relation, target)` triple is **immutable**: correcting a claim means superseding the connection
(`assertion.status: superseded` + `lifecycle.replaced_by`) and asserting the new claim under a **new** `lhs:conn.NNNNNN`. `scripts/check_id_immutability.py`
enforces this from git history (CI checks out with `fetch-depth: 0`).

Review work (E6.1): `python3 scripts/dependency_review_campaign.py` regenerates the worksheets in
`reports/e61-dependency-campaign/`; a human fills `decision:` in a `batch-NN.yaml` and applies it
with `python3 scripts/apply_review_decisions.py <sheet> --reviewer human:<id>`. AI agents never
fill decisions. If validation complains
about out-of-sync inline relationships, run `python3 scripts/sync_relationships.py` (the inline
block is a generated projection — never hand-edit it).

## Starting work

1. Read `docs/README.md` to navigate the governance set; read `docs/STEMMA-SPECIFICATION.md`.
2. Read the affected schema and a seed entity in `content/` before editing.
3. State the classification and a short plan before changing anything.
4. Run validation after changes; finish with a short summary and flag human decisions.