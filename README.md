# LearningHubSTEM

> **An open, structured, reusable STEM knowledge foundation.** Curriculum is external.
> Products are external. Learning experiences are external. AI agents are consumers.

## Status: SEED ONLY

This repository currently contains a **minimal proof** that the architecture works — five seed
entities, a schema, a validator, and a regenerable JSON export. It is **not** an activated MVP.
Do not expand it beyond the minimal seed without an explicit human decision
(`docs/LEARNINGHUBSTEM-ROADMAP.md`).

## What's here

```text
LearningHubSTEM/
├── README.md
├── schema/concept.schema.json    — canonical entity schema (JSON Schema)
├── content/                      — canonical Markdown + YAML-frontmatter entities
│   ├── force.md                  (lhs:phys.force)
│   ├── mass.md                   (lhs:phys.mass)
│   ├── acceleration.md           (lhs:phys.acceleration)
│   ├── newtons-second-law.md     (lhs:phys.newtons-second-law)
│   └── momentum.md               (lhs:phys.momentum)
├── scripts/validate.py           — lightweight validation + export generator
└── exports/knowledge.json        — DERIVED artifact (regenerable; never the source of truth)
```

Open the files with `id: lhs:phys.force` and so on. Relabeling a file to a different name
without changing its `id` is expected; filenames follow the final ID slug for convenience.

## Usage

```bash
# Validate all canonical content and regenerate the export
python3 scripts/validate.py          # from this directory

# Or from the workspace root
python3 LearningHubSTEM/scripts/validate.py
```

Exit code `0` = valid. Errors are printed with file and reason.

## Rules

- Canonical knowledge lives only in `content/`. Everything under `exports/` is derived.
- No curriculum, grade, course, or product appears in `content/`.
- AI-drafted content is `status: draft` until a human reviews it (see
  `../docs/LEARNINGHUBSTEM-SPECIFICATION.md` §6).
- A stable ID is never reused or silently reassigned.

## Governance

The authoritative model for this repository lives in the workspace docs:

- `../docs/LEARNINGHUBSTEM-SPECIFICATION.md` — canonical format, IDs, entity model,
  relationship semantics, provenance, validation, consumer contract.
- `../docs/LEARNINGHUBSTEM-ROADMAP.md` — phased plan; each phase requires activation.
- `../docs/NORTHSTAR.md`, `../docs/GOVERNANCE.md` — north star and rules.

## License

No license has been chosen yet — a human decision is pending (`../docs/GOVERNANCE.md`).