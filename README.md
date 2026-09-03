# STEMMA

> **An open, structured, reusable STEM knowledge foundation.** Curriculum is external.
> Products are external. Learning experiences are external. AI agents are consumers.
> (Formerly known as **LearningHubSTEM**; the `lhs:` identity namespace is unchanged.)

## Status: active canonical foundation

<!-- status-truth:start -->
## Status: live foundation in early curation

Machine-checkable live counts — `scripts/status_truth.py` (CI) fails if this
block drifts from canonical content (audit F2: status honesty is a gate):

- Entities: **224** — human-reviewed/canonical: **0**, draft: **224**
- Connections (first-class assertions): **654** — review-canonical: **50** (7.6%), unreviewed: **604**
- Canonical source records: **3**
<!-- status-truth:end -->


The architecture is proven and growing incrementally
(`docs/STEMMA-ROADMAP.md`, `docs/STEMMA-IMPLEMENTATION-PLAN-v2.md`). Per the
governance definition, *canonical* is a reviewed property, not a folder: the
corpus is draft + early curation, and consumers should filter by the review
policies documented in `docs/STEMMA-CONSUMER-SEAM.md`.

## What's here

```text
STEMMA/
├── README.md
├── schema/                     — entity, connection, source schemas + adaptive extension registry
├── content/                    — canonical Markdown + YAML-frontmatter entities (224)
│   ├── math/                   (lhs:math.*)
│   ├── physics/                (lhs:phys.*)
│   ├── chemistry/              (lhs:chem.*)
│   ├── biology/                (lhs:bio.*)
│   ├── earth-space/            (lhs:earth.*)
│   ├── engineering/            (lhs:eng.*)
│   └── scientific-practice/    (lhs:practice.*)
├── connections/                — first-class assertion objects (lhs:conn.*)
├── sources/                    — canonical source records (lhs:src.*)
├── scripts/validate.py         — validation + export generator
└── exports/knowledge.json      — DERIVED artifact (regenerable; never the source of truth)
```

Open any file with an `id: lhs:...`; filenames follow the final ID slug for convenience.

## Sources & attribution

Every entity records **where its content comes from** (`provenance.source/source_kind`) and,
for historically significant laws and discoveries, **who first stated the claim and when**
(`historical.stated_by/year/timeline`). See **`docs/SOURCES.md`** for the full visible
inventory of sources and historical attributions. Canonical source records live in `sources/`.

## Usage

```bash
# Validate all canonical content and regenerate the export
python3 scripts/validate.py          # from this directory

# Or from the workspace root
python3 STEMMA/scripts/validate.py
```

Exit code `0` = valid. Errors are printed with file and reason.

## Rules

- Canonical knowledge lives only in `content/`. Everything under `exports/` is derived.
- No curriculum, grade, course, or product appears in `content/`.
- AI-drafted content is `status: draft` until a human reviews it (see
  `docs/STEMMA-SPECIFICATION.md` §6).
- A stable ID is never reused or silently reassigned.

## Governance

The authoritative model for this repository lives in the workspace docs:

- `docs/STEMMA-SPECIFICATION.md` — canonical format, IDs, entity model,
  relationship semantics, provenance, validation, consumer contract.
- `docs/decisions/` — foundation decision records (licensing, identity, vocabulary, …).
- `docs/STEMMA-ROADMAP.md` — phased plan; each phase requires activation.
- `docs/NORTHSTAR.md`, `docs/GOVERNANCE.md` — north star and rules.

## Consumers

The first consumer proof is STEM-TUITION's shell app (the LearningHub application). The seam is
documented in `docs/STEMMA-CONSUMER-SEAM.md` (export contract, adapter, ownership boundaries,
regeneration and test commands). STEMMA stays independent: it only publishes the export;
consumers adapt it to their own curriculum and products.

## License

- **Content** (`content/`, `connections/`, `sources/`, `docs/`): **Creative Commons
  Attribution 4.0 International (CC BY 4.0)** — see `LICENSE`.
- **Code** (`scripts/`, `schema/`, tests): **MIT License** — see `LICENSE-CODE`.

See `docs/decisions/0001-license.md` and `docs/GOVERNANCE.md` for the rationale and the
distinction between the knowledge content license and the code license.