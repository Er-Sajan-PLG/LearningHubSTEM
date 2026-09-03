# NORTHSTAR — STEMMA

**Status:** The governing north star for the entire STEM Ecosystem workspace.
**Scope:** Everything under `/Projects`.
**Source of truth:** The full vision is preserved verbatim in
`docs/MASTER-VISION.md`. This file is the distilled, actionable version.

---

## The one-sentence north star

> **STEMMA is an open, structured, reusable STEM knowledge foundation.**
> Anyone — humans, educators, developers, researchers, AI systems, and other products —
> should be able to build on top of it.
> **Curriculum is external. Products are external. Learning experiences are external.
> AI agents are consumers.**

---

## The fundamental idea

STEMMA is **not** an education product. It is not LearningHub. It is not a
curriculum platform. It is not a Nepal curriculum database, and it is not owned by any single
product.

It exists so that the underlying STEM knowledge (concepts, laws, quantities, equations,
relationships, misconceptions, applications, simulations) is organized in a reusable way that:

- anyone can build on,
- any curriculum can map into its own sequence,
- any product can consume,
- any AI system can retrieve from.

If another person or company uses STEMMA to build something useful, **that is a success.**

---

## The three boundaries you must never blur

1. **Knowledge ≠ Curriculum.**
   STEMMA owns the STEM knowledge and its relationships (`requires`, `related_to`,
   `applied_in`, `derived_from`, …). It does not care which curriculum — Nepal, CBSE, GCSE,
   A-Level, IB, university, custom — uses it. Curriculum systems are **consumers**.

2. **Knowledge order ≠ Curriculum order.**
   The knowledge layer says `A requires B`. A curriculum decides when to teach each. STEMMA
   provides the relationship; the curriculum decides sequence.

3. **Products are external.**
   LearningHub, STEM-GAME, STEM Lab, JARVIS are all consumers. STEMMA must remain useful
   even if every one of those products disappears. Never couple the foundation to a product.

---

## Architecture rule (the test)

When deciding whether something belongs in STEMMA, ask:

> **"Is this intrinsic to the STEM knowledge itself, or is it a way of organizing, teaching,
> presenting, or consuming that knowledge?"**

- Intrinsic to the knowledge → potentially STEMMA.
- Curriculum, grade, lesson sequence, student progress, UI, monetization, subscription, product
  experience → belongs OUTSIDE STEMMA.

---

## Canonical vs derived

- **Canonical** STEMMA content is version-controlled, structured, human-readable,
  machine-readable, modular, reusable, open to contribution, and independent of any application.
- **Derived** systems (embeddings, vector/graph databases, search indexes, APIs, caches,
  recommendations, AI retrieval indexes) must always be **regenerable** from canonical content.
  They are never the source of truth.

---

## AI and authority

AI may propose concepts, relationships, drafts, examples, questions, and duplicate/inconsistency
detection — but **AI output is not authoritative knowledge**. It becomes canonical only through a
validation/review workflow:

```
AI suggestion → validation/review → canonical knowledge → derived indexes
```

---

## Current implementation principle

> **Simple now. Extensible later.**

Do not build the entire future ecosystem now. Implement the smallest correct version of the current
requirement, but avoid decisions that would unnecessarily prevent future independent consumers.

---

## Design for unexpected users

Assume future consumers we cannot imagine: robotics education, engineering simulation, AI training
environments, scientific visualization, research tools. Therefore avoid unnecessary assumptions
about presentation, curriculum, pedagogy, or product design in the core knowledge layer.

---

*The full authoritative text, section by section, is in `docs/MASTER-VISION.md`.*
