# AGENTS.md — LearningHubSTEM

Operating instructions for humans and AI agents working inside this repository.
Workspace-level rules are in the workspace root (`/home/sajan/Projects/AGENTS.md` and its
`docs/`); this file governs this repository (governance Level 2).

## North star (this repo must stay)

> **LearningHubSTEM is an open, structured, reusable STEM knowledge foundation.**
> Curriculum is external. Products are external. Learning experiences are external.
> AI agents are consumers. STEM-TUITION is one consumer — never a controller.

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
```

These are derived-output commands; `scripts/validate.py` is the only required check today.

## Starting work

1. Read `docs/README.md` to navigate the governance set; read `docs/LEARNINGHUBSTEM-SPECIFICATION.md`.
2. Read the affected schema and a seed entity in `content/` before editing.
3. State the classification and a short plan before changing anything.
4. Run validation after changes; finish with a short summary and flag human decisions.