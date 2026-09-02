# CONTRIBUTING — STEMMA

Thank you for contributing to STEMMA, an open, structured, reusable STEM knowledge
foundation. Every contribution should keep the foundation **curriculum-agnostic,
product-independent, and identity-stable** for consumers everywhere.

- **Governance:** `docs/GOVERNANCE.md` (this repo) overrides workspace rules inside `STEMMA`.
- **North star:** `docs/NORTHSTAR.md` — curriculum, products, and learning experiences are
  **external**. STEMMA only holds canonical STEM knowledge.
- **Specification:** `docs/STEMMA-SPECIFICATION.md`.
- **Decision record to know first:** `docs/decisions/0003-identity.md` (stable identity).

---

## 1. The three ground rules

1. **Canonical knowledge lives only in `content/`.** Everything under `exports/` is
   **derived and regenerable** — never hand-edit it. Run `python3 scripts/validate.py` to
   regenerate the export after content changes.
2. **No curriculum, grade, course, or product appears in `content/`.** A concept is described
   *independently* of any consumer's educational level, curriculum, country, or institution.
   Legitimate scientific terminology (e.g. "standard model", "trophic level", "GPA") is
   welcome; claims such as "grade-10-relevant" or "for the CBSE syllabus" are not.
3. **IDs are a stability contract (ADR-0003), not a branding choice.** See §2 below. The
   schema + CI **enforce** this by mechanism, so future contributors respect it because the
   contract is machine-checked, not merely recommended.

---

## 2. IDs & stability — the contract

Identifiers must survive renames, reordering, curriculum differences, and product differences.
**An `lhs:` identifier, once assigned to a canonical entity, can never later represent a
different entity or meaning.**

### 2.1 ID format

| Kind | Pattern | Example | Source of rule |
|------|---------|---------|----------------|
| Concept / entity | `lhs:<domain>.<slug>` | `lhs:physics.mechanics.force` | ADR-0003, `schema/entity.schema.json` |
| Connection | `lhs:conn.NNNNNN` (opaque, 6-digit) | `lhs:conn.000378` | ADR-0011 |
| Source | `lhs:src.<slug>` | `lhs:src.halliday-resnick` | ADR-0003 |

Domains come from the fixed set in `schema/` (e.g. `physics`, `math`, `chemistry`, `biology`,
`earth-space`, `engineering`, `scientific-practice`).

### 2.2 What is and is not allowed

| Action | Allowed? | How |
|--------|----------|-----|
| Add a **new** ID | ✅ | pick an unused `lhs:<domain>.<slug>` |
| Keep an existing ID with unchanged meaning | ✅ | just edit the living file |
| **Deprecate** an ID | ✅ | set `status: deprecated` + `deprecated_by`; the old ID is **reserved forever** |
| **Alias** an ID | ✅ | use `deprecated_by` / `aliases`; alias references must be valid |
| **Reassign** an ID to a different meaning | ❌ | e.g. `lhs:physics.mechanics.velocity` used for *acceleration* — **never** |
| **Delete then reuse** an ID | ❌ | deleted/deprecated IDs are reserved forever |

`scripts/check_id_immutability.py` (wired into CI) fails the build if an ID was reassigned or
reused; it passes for new/unchanged/deprecated/aliased IDs.

### 2.3 How to add a concept — worked example

1. Create `content/<domain>/<topic>/<slug>.md` with valid YAML frontmatter and an **unused** ID:

   ```yaml
   ---
   id: lhs:physics.thermodynamics.entropy
   type: concept
   name: Entropy
   domain: physics
   status: draft          # AI-drafted stays draft until human review
   definition: >-
     A thermodynamic quantity measuring the number of microscopic configurations a system
     can occupy, and hence the degree of disorder available to it.
   provenance:
     ai_drafted: true      # AI output is NOT canonical without human review
   ---
   ```

2. The ID `lhs:physics.thermodynamics.entropy` is now **permanent**. If you later decide
   "Entropy" should live under a different slug, create a **new** ID and **deprecate** this one
   (`status: deprecated`, `deprecated_by: lhs:physics.thermodynamics.entropy-change`) — never
   reassign the original.

3. Validate + regenerate the export:

   ```bash
   python3 scripts/validate.py   # exit 0 = valid; regenerates exports/knowledge.json
   python3 scripts/verify_all.py # full guard chain (generality, ID immutability, …)
   ```

4. Keep AI-drafted entities `status: draft` and set `provenance.ai_drafted: true` until a
   human reviews and promotes them.

---

## 3. Provenance & attribution

Every canonical entity records where its content came from in `provenance`:
- `provenance.source_kind` + `provenance.source` — the **record source** (standard, textbook,
  or citation the content was drawn from). This is attribution and is welcome; it does **not**
  imply a curriculum.
- `historical.stated_by` + `historical.year` — who **first** stated a scientific claim and when.

`docs/SOURCES.md` is the one-place attribution inventory. Do not invent sources; cite real ones;
keep attribution in `content/` minimal and factual.

---

## 4. Verification before opening a PR

Run the full chain and confirm it exits 0:

```bash
python3 scripts/validate.py
python3 scripts/verify_all.py
```

CI additionally runs `check_id_immutability` and the generality (`test_generality`) guards.
A PR is not ready until all pass.

---

## 5. Scope discipline

- **NOW** — only what the current milestone requires.
- **SEAM / LATER** — document intent; don't silently expand scope (full ontology, multilingual
  publication, etc.).
- **OUT OF SCOPE** — microservices, cloud, auth, payments, analytics, vector/graph databases,
  and any shared platform services.

Ask the maintainer if a change might cross the knowledge↔curriculum↔pedagogy↔product boundary.

---

*STEMMA is the foundation. Curriculum is external. Products are external. Learning experiences
are external. AI agents are consumers — never controllers.*