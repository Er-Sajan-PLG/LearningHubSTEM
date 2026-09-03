# MASTER VISION — STEMMA

You are working on a long-term ecosystem centered around **STEMMA**.

Before making architectural, data-model, API, UI, or implementation decisions, understand this vision.

---

# 1. THE FUNDAMENTAL IDEA

**STEMMA is not an education product.**

It is not LearningHub.

It is not a curriculum platform.

It is not a Nepal curriculum database.

It is not owned by one educational product.

STEMMA is intended to become an **open, structured, reusable STEM knowledge foundation**.

Its purpose is to organize STEM knowledge in a way that humans, educators, developers, researchers, AI systems, and other products can use.

Anyone should be able to build on top of it.

That includes:

* LearningHub
* other education platforms
* universities
* teachers
* researchers
* developers
* AI systems
* publishers
* games
* simulations
* future products that do not yet exist

If another person or company uses STEMMA to build something useful, that is a success.

---

# 2. THE MOST IMPORTANT ARCHITECTURAL BOUNDARY

## STEMMA ≠ Curriculum

Curriculum MUST be treated as a separate layer/system.

STEMMA should contain the underlying STEM knowledge.

A separate curriculum system can map that knowledge into:

* Nepal curriculum
* India curriculum
* CBSE
* GCSE
* A-Level
* IB
* university courses
* professional training
* private curricula
* custom curricula
* teacher-created courses
* company-created learning paths

STEMMA does NOT need to care which curriculum uses its knowledge.

Conceptually:

```text
                 STEMMA
                STEM KNOWLEDGE
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
      Curriculum A  Curriculum B  Curriculum C
          │            │            │
          ▼            ▼            ▼
      Product A     Product B     Product C
```

STEMMA provides the knowledge.

Others decide how to organize and teach it.

---

# 3. STEMMA SHOULD BE CURRICULUM-AGNOSTIC

The canonical knowledge model should not contain assumptions such as:

```text
"Force belongs to Grade 9 Nepal."
```

Instead, it should contain:

```text
Force
```

and its relationships to other STEM concepts.

For example:

```text
Force
 ├── related_to → Acceleration
 ├── related_to → Mass
 ├── related_to → Momentum
 ├── prerequisite_for → Newton's Laws
 ├── related_to → Work
 └── applied_in → Engineering Mechanics
```

A curriculum system can later say:

```text
Nepal Grade 9
     ↓
Force
```

But that mapping does NOT belong inside the canonical identity of Force.

---

# 4. CURRICULUM IS A CONSUMER

Curriculum systems should consume STEMMA.

They may reference its concepts using stable identifiers.

For example:

```text
STEMMA
    concept/force
    concept/mass
    concept/acceleration
    concept/newtons-second-law
```

A curriculum can then create:

```text
Nepal Grade 9 Physics
    ↓
Unit: Force and Motion
    ↓
concept/force
concept/mass
concept/acceleration
concept/newtons-second-law
```

Another curriculum can use exactly the same concepts differently.

```text
GCSE Physics
    ↓
Forces
    ↓
concept/force
concept/mass
concept/acceleration
concept/newtons-second-law
```

No duplication of the underlying knowledge is necessary.

---

# 5. PEOPLE ARE FREE TO BUILD ON IT

This is a core principle.

STEMMA should not dictate what people build with the knowledge.

Someone may create:

```text
STEMMA
      ↓
Nepal Curriculum
      ↓
LearningHub
```

Someone else may create:

```text
STEMMA
      ↓
IB Curriculum
      ↓
Their own learning platform
```

Someone else:

```text
STEMMA
      ↓
University Engineering Curriculum
      ↓
Engineering simulator
```

Someone else:

```text
STEMMA
      ↓
Custom curriculum
      ↓
Educational game
```

And someone else may completely ignore curriculum:

```text
STEMMA
      ↓
Research tool
```

All of these are valid.

---

# 6. LearningHub

LearningHub is ONE consumer of STEMMA.

It may have its own curriculum layer.

For example:

```text
LearningHub
│
├── Curriculum
│   ├── Nepal
│   ├── India
│   ├── International
│   └── Custom
│
├── Learning paths
├── Lessons
├── Assessments
├── Student progress
└── AI tutor
          │
          ▼
   STEMMA
```

LearningHub can decide how to organize knowledge for its users.

That organization does not become part of STEMMA.

---

# 7. STEMMA KNOWLEDGE MODEL

The knowledge layer should focus on STEM itself.

Potential entities include:

* concepts
* principles
* laws
* phenomena
* definitions
* quantities
* units
* equations
* mathematical relationships
* examples
* applications
* experiments
* problems
* misconceptions
* prerequisite relationships
* related concepts
* extensions
* evidence/references
* simulations
* models
* disciplinary relationships

The exact schema can evolve.

The key principle is:

**Represent STEM knowledge, not a particular educational system.**

---

# 8. KNOWLEDGE GRAPH

STEMMA should support meaningful relationships between knowledge entities.

For example:

```text
Newton's Second Law
       │
       ├── requires → Force
       ├── requires → Mass
       ├── requires → Acceleration
       ├── related_to → Momentum
       ├── extends → Newton's First Law
       └── applied_in → Engineering Mechanics
```

Possible relationship types include:

```text
requires
teaches
extends
equivalent_to
related
misconception_of
depends_on
part_of
derived_from
applied_in
```

These relationships describe the knowledge itself.

They should not be confused with curriculum sequencing.

---

# 9. KNOWLEDGE ORDER ≠ CURRICULUM ORDER

This distinction is extremely important.

A knowledge graph may say:

```text
A requires B.
```

A curriculum may decide:

```text
Teach B in Grade 8.
Teach A in Grade 9.
```

Another curriculum may decide:

```text
Teach B and A in Grade 10.
```

STEMMA should provide the relationship.

The curriculum decides the instructional sequence.

---

# 10. CANONICAL CONTENT

The canonical STEMMA repository should be:

* version controlled
* structured
* human readable
* machine readable
* modular
* reusable
* open to contribution
* independent from any single application

Canonical files should be the source of truth.

Derived systems may include:

* embeddings
* vector databases
* search indexes
* graph databases
* APIs
* caches
* recommendation systems
* AI retrieval indexes

But these are derived representations.

They must be regenerable from canonical content.

---

# 11. AI

AI can assist in developing STEMMA.

It may:

* propose concepts
* suggest relationships
* generate drafts
* detect duplicates
* find inconsistencies
* generate examples
* create questions
* classify content
* identify possible misconceptions

But AI output should not automatically become authoritative canonical knowledge.

Use a workflow such as:

```text
AI suggestion
      ↓
validation/review
      ↓
canonical knowledge
      ↓
derived indexes
```

---

# 12. PRODUCTS SHOULD NOT BE TIGHTLY COUPLED

STEMMA should not depend on:

* LearningHub
* STEM Game
* STEM Lab
* JARVIS
* one specific frontend
* one specific database
* one specific curriculum
* one specific company product

Instead:

```text
                    STEMMA
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
     LearningHub      STEM Game        STEM Lab
          │                │                │
          └────────────────┼────────────────┘
                           │
                         JARVIS
```

These systems consume and interact with the knowledge layer through defined interfaces.

STEMMA must remain useful even if every one of those products disappears.

---

# 13. JARVIS

JARVIS is an AI agent/interface.

It may consume STEMMA, but STEMMA must not become dependent on JARVIS.

JARVIS may eventually use:

```text
STEMMA
Web
Research papers
User data
Tools
Code
Simulations
External APIs
```

STEMMA is one knowledge source in the larger JARVIS ecosystem.

---

# 14. THE COMPANY

The eventual company may create products and services around STEMMA.

For example:

```text
Company
│
├── LearningHub
├── STEM Game
├── STEM Lab
├── AI services
└── other future products
```

But the existence of commercial products must not dictate the fundamental structure of STEMMA.

The open knowledge foundation should remain independently useful.

---

# 15. DESIGN FOR UNEXPECTED USERS

Do not assume we know all future consumers.

A future developer might use STEMMA for something completely different.

For example:

```text
STEMMA
       ↓
robotics education
```

or:

```text
STEMMA
       ↓
engineering simulation
```

or:

```text
STEMMA
       ↓
AI training environment
```

or:

```text
STEMMA
       ↓
scientific visualization
```

Therefore avoid unnecessary assumptions about presentation, curriculum, pedagogy, or product design in the core knowledge layer.

---

# 16. ARCHITECTURAL RULE

When deciding whether something belongs in STEMMA, ask:

> "Is this intrinsic to the STEM knowledge itself, or is it a particular way of organizing, teaching, presenting, or consuming that knowledge?"

If it is intrinsic to the knowledge:

**Potentially STEMMA.**

If it is about:

* curriculum
* grade
* lesson sequence
* student progression
* UI
* monetization
* subscription
* product experience
* classroom structure
* specific educational system

then it probably belongs outside STEMMA.

---

# 17. CURRENT IMPLEMENTATION PRINCIPLE

Do not build the entire future ecosystem now.

Implement the smallest correct version of the current requirement.

However, avoid architectural decisions that unnecessarily prevent future independent consumers.

In other words:

> **Simple now. Extensible later.**

Do not introduce unnecessary complexity merely because the vision is large.

---

# 18. THE NORTH STAR

Remember this above everything else:

> **STEMMA is an open STEM knowledge foundation.**

> **It should organize STEM knowledge so that anyone can build upon it.**

> **Curriculum is external.**

> **Products are external.**

> **Learning experiences are external.**

> **AI agents are consumers.**

> **LearningHub is one consumer.**

> **If other people use STEMMA to build things we never imagined, that is a success—not a failure of product control.**

The objective is not to own every use of the knowledge.

The objective is to build a **high-quality, reusable foundation that makes many uses possible.**

Always preserve this boundary when making architectural decisions.
