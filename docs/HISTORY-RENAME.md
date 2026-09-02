# STEMMA — Repository History & the LearningHubSTEM Rename

> **Why this file exists:** A future developer or open-source contributor will run `git log`
> and see commits that reference the names **LearningHubSTEM** / **learninghubstem** — even
> though this repository is now named **STEMMA**. This document explains that history truthfully
> so you are never confused by, and never tempted to "fix," the name mismatch in the commit
> history.

## The short version

- This repository was originally named **`LearningHubSTEM`** and was renamed to **`STEMMA`** on
  **2026-09-02**.
- The rename is recorded in **ADR-0019** (`docs/decisions/0019-rename-and-freeze.md`).
- **The git history is the immutable truth.** We deliberately **did NOT rewrite, rebase, or
  amend** the history to change old names. Old commits legitimately say `LearningHubSTEM` /
  `learninghubstem` / reference `Er-Sajan-PLG/LearningHubSTEM` because that was the repository's
  name at the time they were made.
- **The `lhs:` identity namespace, the schema, and the export contract were NOT changed by the
  rename** (see ADR-0003 and ADR-0019). `lhs:` IDs are permanent regardless of repository name.

## Timeline (verified from git history)

| Commit | What it says | What it actually is |
|--------|--------------|---------------------|
| `9071436` | "feat: add LearningHubSTEM v0.1 minimal seed..." | The original foundation seed — created under the old name. |
| `92492c9` | "docs: move LearningHubSTEM governance into this repo..." | Early governance setup under the old name. |
| `bbb28e7` | "docs: scope governance to LearningHubSTEM repository" | Governance scoping under the old name. |
| `98cf346` / `8543c99` | "ci(learninghubstem): add PROFESSOR-J level CI..." | CI setup; the `(learninghubstem)` scope was the then-current repo name. |
| `5cc37ab` | "fix(ci): ... for LearningHubSTEM" | A CI fix referencing the then-current name. |
| `67f9ba8` | "refactor: re-brand foundation LearningHubSTEM -> STEMMA (identity/path only)" | The rename implementation itself. |
| `70f9360` | "refactor: re-brand foundation LearningHubSTEM -> STEMMA + ADR-0019 (Scope A) (#17)" | The rename PR merge (documented by ADR-0019). |

(The above is a representative sample; other early commits may also reference the old name.)

## THE ONE THING YOU MUST NEVER DO: change the `lhs:` ID naming convention

> **This is the most important rule in this repository.**

- **NEVER** change `lhs:` to another prefix (e.g. `stemma:`), and **NEVER** renumber, rename,
  reassign, or reuse an existing `lhs:` ID.
- **Why (technical truth-protection):** an `lhs:` ID is a **stable contract**, not a label.
  External consumers depend on it — adapters (`lhs-adapter`), caches, cross-references in
  `connections/*.yaml`, `deprecated_by`/`aliases`, export-contract citations, and any product or
  AI system that has already persisted the ID. If `lhs:phys.example` once meant "Classical
  mechanics" and later means "Quantum mechanics," every consumer that stored the old meaning now
  silently points at a different fact. Preserving identity preserves knowledge-assignment truth;
  changing it quietly falsifies history.
- The rename of the **repository/brand** (`LearningHubSTEM` → `STEMMA`) is unrelated to the
  `lhs:` namespace. **Repo names can change; IDs cannot.** See **ADR-0003** (Stable identity) and
  ADR-0007 (export contract).
- Deprecation + `deprecated_by` + `aliases` are the only legitimate ways to evolve — never
  in-place mutation, never reuse.

---

## Why we did NOT rewrite history

Rewriting git history to rename old commits is the **wrong fix** and is explicitly avoided
here:

- **History is a factual record.** Those commits *were* made against a repo called
  `LearningHubSTEM`; rewriting them would falsify the record.
- **Rewriting shared history is destructive and anti-open-source.** It invalidates every fork and
  clone, breaks `git pull`/`cherry-pick`/`rebase` for anyone who has the old history, and is a
  cardinal sin for a project that intends to go open-source.
- **The identity that matters is the contract, not the name.** The `lhs:` namespace, schema, and
  export contract are frozen and unchanged; the repository name is incidental branding. Stable
  IDs + a documented rename are what make history navigable — not rewritten commit messages.

## What to do when you see old names in history

- **Read them as historical fact**, not as a problem. `LearningHubSTEM` and `SCIENCE
  "learninghubstem"` in commit subjects/scopes/branch-names simply reflect the repository's name
  at that point in time.
- **Do NOT** `rebase`, `filter-branch`, `filter-repo`, or `--amend` history to strip old names.
- The rename boundary is: **current code/config/branding says `STEMMA`; historical
  commits/branches may say `LearningHubSTEM`. Current identity (`lhs:`), schema, and export
  contract are unchanged.** See ADR-0019 and ADR-0003.

## Names that appear in history (past identity terms)

- Repository: **`LearningHubSTEM`** (old) → **`STEMMA`** (current)
- Git provider slug: `Er-Sajan-PLG/LearningHubSTEM` (old, auto-redirects) → `Er-Sajan-PLG/STEMMA`
- Commit footer scope: `learninghubstem` (old) — e.g. `ci(learninghubstem): ...`
- Leftover branch: `ci/learninghubstem-cicd` (historical; not part of current work)
- Schema `$id` placeholder: `https://learninghubstem.example/schema/...` — **a placeholder URI,
  not a real resolver**; to be replaced with a stable real URI when/if the project is published.
- Protocol/adapter naming: `lhs_*` / `lhs-*` — **intentional, NOT a rename target**. `lhs`
  describes the contract/protocol, not the repository brand. See ADR-0019.

## Related documentation

- `docs/decisions/0019-rename-and-freeze.md` — the rename decision + contract freeze.
- `docs/decisions/0003-rename-not-id-change.md` (referenced) — rename ≠ ID change.
- `docs/VERSIONING.md` — three-track versioning (schema / export / content).
- `README.md` — "formerly known as LearningHubSTEM" note.
- The consuming product repository was independently renamed **STEM-TUITION → LearningHub**
  (recorded separately; see the LearningHub repository's history docs).

---

*History is the truth. We preserve it. If you have questions about a commit, ask rather than
rewriting.*