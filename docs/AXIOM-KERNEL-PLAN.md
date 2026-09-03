# AXIOM — STEMMA Truth Kernel: Always-Evolving Identity & Implementation Plan

> **AXIOM** = the STEMMA truth kernel's own identity: a governed, versioned, self-validating knowledge core that **evolves on contact with new content** through a mechanised ingest→anomaly→proposal→amendment→migration→re-gate loop.  
> Not a static schema. A living kernel with a feedback loop.

---

## 1. Kernel Identity (What AXIOM *Is*)

| Layer | Artifact | Version Track | Purpose |
|-------|----------|---------------|---------|
| **Schema** | `schema/concept.schema.json`, `connection.schema.json`, `source.schema.json`, `relation-registry.yaml`, `extension-registry.yaml` | `schema_version` (0.2) | Machine-enforceable contracts |
| **Vocabulary** | 54 relations (11 families), 4 extension dimensions, controlled vocabularies (domains, regimes, subdomains) | part of schema_version | Semantic primitives |
| **Content** | 224 entities, 654 connections, 3 sources | `content_release` (independent) | Knowledge itself |
| **Export Contract** | `exports/knowledge.json` | `export_version` (0.1) | Consumer-facing derived artifact |

**Invariant**: `schema_version` and `export_version` change **only** on breaking changes. Content evolves independently.

---

## 2. Empirical Audit Findings (Live Kernel — 224 entities, 654 connections, 54 relations)

| Check | Result | Implication |
|-------|--------|-------------|
| Prerequisite cycles (`requires`, `mathematically_requires`, etc.) | **0** | Graph is acyclic on dependency edges |
| Duplicate (source, relation, target) triples | **0** | No redundant canonical connections |
| Dangling refs (connections → missing entities) | **0** | All references resolve |
| Unregistered relations in inline `relationships[]` | **0** | Inline projection is clean |
| Domain/range violations (per registry) | **0** | All connections obey registry |
| Self-loops | **0** | No reflexive assertions |
| **Unused registry relations** | **42/54** (78%) | Vocabulary vastly wider than current use — room to grow |
| **Projection drift** (inline vs canonical) | **13 entities** | Canonical connections have relations not projected inline (e.g., `bridges`, `approximates`, `analogous_to`, `mathematically_requires`) — inline is a lossy subset |
| **Registry types not in concept.type enum** | **4 types**: `experiment`, `model`, `phenomenon`, `regime` | Schema enum drift (R20): registry allows these as domain/range but concept enum lacks them |
| **Export lacks kernel_version / content_hash** | **MISSING** | Derived artifact has no provenance of which kernel produced it |

**Verdict**: Kernel is *structurally sound* (no integrity errors) but has **designed gaps** in enforcement machinery and **no evolution loop**.

---

## 3. SOTA Comparison — Mechanisms to Adopt

| Standard | Mechanism | AXIOM Adoption |
|----------|-----------|----------------|
| **W3C SHACL** | `sh:ValidationReport` with `sh:conforms`, `sh:result[]` carrying `sh:resultSeverity` (`sh:Violation`/`sh:Warning`/`sh:Info`), `sh:focusNode`, `sh:resultPath`, `sh:sourceConstraintComponent`, `sh:resultMessage` | Adopt this *exact report structure* for kernel validation output — machine-readable, severity-graded, actionable |
| **LinkML** | `linkml-validate` (runtime validator), generators (JSON Schema, Python, SQL, etc.), `linkml-map` for data migration, schema versioning in YAML header | Adopt: validator as library, migration scripts as first-class, generators for consumer adapters |
| **OBO Foundry** | ID stability policy (P1–P16), term obsoletion with `owl:deprecated` + `IAO:0100001 replaced_by` + `consider`, MIREOT term import | Adopt: explicit deprecation lifecycle, `consider` for soft redirects, import protocol for external terms |
| **ROBOT** | CLI pipeline: `extract` → `merge` → `reason` → `annotate` → `diff` → `report` → `init` | Adopt: same pipeline stages for kernel release |
| **SKOS** | `exactMatch`/`closeMatch`/`broadMatch`/`narrowMatch`/`relatedMatch` for concept mapping | Adopt: mapping vocabulary for cross-foundation alignment |
| **Wikidata** | Property proposal process (proposal → discussion → closure), constraint types (single-value, subject-type, etc.) with severity (mandatory/suggestion), data-quality dashboards | Adopt: proposal→review→ratification governance, constraint severity, public quality dashboard |
| **PROV-O** | `prov:Entity`/`Activity`/`Agent`, qualified patterns (`prov:qualifiedAttribution`), derivation/attribution | Already in `connection.provenance` — extend to full PROV-O export |
| **FAIR** | 15 principles (F1–F4, A1–A2, I1–I3, R1) | Adopt as release gate checklist |
| **Schema.org** | `pending.schema.org` lifecycle, `attic` for retired terms | Adopt: staging area for candidate relations, attic for deprecated |
| **LLM Extraction (2024–26)** | JSON-Schema-constrained outputs (OpenAI structured outputs, Outlines, Instructor), extraction→validation loops, human-in-the-loop curation | Adopt: LLM Draft seam with schema-constrained output + validation gate |
| **Confluent Schema Registry** | Compatibility modes: BACKWARD/FORWARD/FULL/TRANSITIVE | Adopt: explicit compatibility policy per schema track |

---

## 4. The Always-Evolving Loop (Core of AXIOM)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AXIOM EVOLUTION LOOP                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────┐    ┌─────────────┐    ┌───────────┐    ┌────────────────┐   │
│   │ INGEST   │───▶│ ANOMALY     │───▶│ PROPOSAL  │───▶│ GOVERNANCE     │   │
│   │ (PDF,    │    │ DETECTION   │    │ STAGING   │    │ GATE           │   │
│   │  text,   │    │ (new rels,  │    │ (proposals/│    │ (human +       │   │
│   │  LLM)    │    │  vocab gaps,│    │  staged)  │    │  automated)    │   │
│   └──────────┘    │  violations)│    └───────────┘    └───────┬────────┘   │
│                   └─────────────┘                              │          │
│                          ▲                                     │          │
│                          │                                     ▼          │
│                   ┌─────────────┐    ┌─────────────┐    ┌──────────────┐  │
│                   │ RE-GATE     │◀───│ MIGRATION   │◀───│ AMENDMENT    │  │
│                   │ (validate   │    │ (apply      │    │ (registry    │  │
│                   │  + export)  │    │  patches,   │    │  edits,      │  │
│                   └─────────────┘    │  ID remap)  │    │  deprecation)│  │
│                                      └─────────────┘    └──────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Stage 1: INGEST (Already Exists)
- `scripts/ingest.py` — deterministic extraction (pdftotext + tesseract)
- `scripts/ingest_to_proposals.py` — stages `CurationRequest` under `proposals/`
- **Gap**: LLM Draft seam needs JSON-Schema-constrained output (Outlines/Instructor)

### Stage 2: ANOMALY DETECTION (Partial — `integrity_anomalies.py`)
**Current**: duplicate claims, contradictions, confidence/basis mismatch, isolated entities, conflicting reviews
**Add**:
- **New relation candidates**: relations used in inline but not in registry (currently 0, but future-proof)
- **Vocabulary gaps**: entities with `type` not in concept enum but in registry domain/range (`phenomenon`, `model`, `experiment`, `regime`)
- **Constraint violations**: SHACL-style severity grading (ERROR/WARNING/INFO)
- **Projection drift detector**: inline `relationships[]` vs canonical `connections/` diff
- **Kernel version drift**: export missing `kernel_version` + `content_hash`

### Stage 3: PROPOSAL STAGING (Exists — `proposals/*.proposal.yaml`)
- Human-readable dossiers with extraction preview, source candidate, proposal artifact, gate decisions
- **Add**: machine-readable proposal index (`proposals/index.json`) for automation

### Stage 4: GOVERNANCE GATE (Partial)
- `curation_pipeline.py` has `GateResult` (pass/fail/block) with findings
- `graph_policy.py` has review policies (`all`, `reviewed`, `canonical`, `trusted`)
- **Add**: 
  - **Automated gates**: schema conformance, ID immutability, domain/range, projection drift
  - **Human gate**: semantic review, deprecation approval
  - **Decision record**: every gate produces an ADR-style decision log entry

### Stage 5: AMENDMENT (Manual Today — Needs Tooling)
- `register_extension.py` — adds extension dimensions (ADR-0017)
- **Missing**: 
  - `register_relation.py` — adds relation to registry with domain/range/inverse/transitive
  - `deprecate_relation.py` — marks relation deprecated + `replaced_by` + `consider`
  - `deprecate_entity.py` — marks entity deprecated + `deprecated_by` + `aliases`
  - `add_concept_type.py` — adds `phenomenon`/`model`/`experiment`/`regime` to concept enum + migration

### Stage 6: MIGRATION (Partial — `migrate_relationships.py`, `reconcile_migration.py`)
- **Add**: 
  - Automated patch generator from amendment decisions
  - Dry-run mode with diff report
  - Rollback capability

### Stage 7: RE-GATE (Exists — `validate.py` + `integrity_anomalies.py`)
- Full validation + anomaly report
- Export regeneration with `kernel_version` + `content_hash`
- **Add**: 
  - Release artifact signing (checksums)
  - Consumer notification (webhook/feed)

---

## 5. Implementation Phases

### Phase 0 — Foundation Hardening (NOW, 1–2 weeks)
| Task | File | Description |
|------|------|-------------|
| Add `kernel_version` + `content_hash` to export | `validate.py` | Export carries `kernel_version` (semver from VERSION) + SHA-256 of canonical content |
| SHACL-style validation report | `validate.py` | Replace flat error list with `ValidationReport` structure: `conforms`, `results[]` with `severity`, `focusNode`, `resultPath`, `sourceConstraintComponent`, `message` |
| Projection drift detector | new `scripts/check_projection_drift.py` | Compare inline `relationships[]` vs canonical `connections/`; emit WARNING for drift |
| Registry type enum sync | `concept.schema.json` | Add `phenomenon`, `model`, `experiment`, `regime` to `type` enum (additive) |
| Unused relation report | `integrity_anomalies.py` | Flag registry relations with 0 canonical connections as INFO |

### Phase 1 — Anomaly Detection Expansion (SEAM, 2–3 weeks)
| Task | File | Description |
|------|------|-------------|
| New relation candidate detector | `integrity_anomalies.py` | Scan inline `relationships[]` for types not in registry → propose registration |
| Vocabulary gap detector | `integrity_anomalies.py` | Entities whose optimal type is `phenomenon`/`model`/etc. but forced into `concept` |
| SHACL severity on all checks | `validate.py`, `integrity_anomalies.py` | Every finding gets `ERROR`/`WARNING`/`INFO` |
| Proposal index | `proposals/index.json` | Machine-readable list of staged proposals |

### Phase 2 — Governance Gate Automation (NOW → SEAM, 3–4 weeks)
| Task | File | Description |
|------|------|-------------|
| Automated gate runner | new `scripts/run_gates.py` | Runs: schema validation, ID immutability, domain/range, drift, anomalies → `GateResult` |
| Decision log | `docs/decisions/` | Every gate pass/fail produces an ADR-style entry |
| Human gate UI | `review.py` enhancement | CLI to approve/reject proposals with reasoning |

### Phase 3 — Amendment Tooling (SEAM, 3–4 weeks)
| Task | File | Description |
|------|------|-------------|
| `register_relation.py` | new | Register relation with family, inverse, transitive, domain, range, description |
| `deprecate_relation.py` | new | Mark deprecated + `replaced_by` + `consider` (OBO style) |
| `deprecate_entity.py` | new | Mark deprecated + `deprecated_by` + `aliases` |
| `add_concept_type.py` | new | Add type to enum + auto-migrate affected entities |

### Phase 4 — Migration & Release (LATER, 2–3 weeks)
| Task | File | Description |
|------|------|-------------|
| Migration patch generator | new `scripts/generate_migration.py` | From amendment decisions → YAML patches for content/connections/sources |
| Dry-run + diff report | `migrate_relationships.py` enhancement | Show exact changes before apply |
| Release pipeline | new `scripts/release.py` | Tag, sign export, publish checksums, notify consumers |
| Compatibility policy | `docs/COMPATIBILITY.md` | BACKWARD/FORWARD/FULL per Schema Registry model |

### Phase 5 — LLM Draft Seam Hardening (SEAM, ongoing)
| Task | File | Description |
|------|------|-------------|
| JSON-Schema-constrained LLM output | `curation_pipeline.py` | Use Outlines/Instructor for structured extraction |
| Extraction→validation loop | `curation_pipeline.py` | Auto-retry on validation failure (max 3) |
| Human-in-the-loop curation UI | `review.py` | Side-by-side diff: LLM draft vs canonical |

---

## 6. AXIOM Release Contract

Every kernel release produces:

```
exports/
├── knowledge.json              # Main export (consumers)
├── knowledge.json.sha256       # Checksum
├── kernel_version              # e.g. "0.3.0" (from VERSION + schema_version)
├── content_hash                # SHA-256 of all canonical content/
├── validation-report.json      # SHACL-style report
├── anomalies-report.json       # integrity_anomalies output
├── proposals-index.json        # Staged proposals
└── decisions/                  # ADR-style decision log for this release
```

**Consumer contract**: "I consume `export_version` X, `kernel_version` Y, verified by `content_hash` Z."

---

## 7. Decision Points Requiring Human Input

| Decision | Options | Recommendation |
|----------|---------|----------------|
| **Add `phenomenon`/`model`/`experiment`/`regime` to concept.type enum** | Yes (additive) / No / Defer | **Yes** — registry already uses them; additive, backward-compatible |
| **Deprecate `related_to` as catch-all** | Keep / Deprecate with `replaced_by` specific relations | **Deprecate** — 205/654 connections are `related_to` (weak signal); require specific relation |
| **Compatibility mode for schema_version** | BACKWARD / FORWARD / FULL | **BACKWARD** — new schema accepts old data; consumers on old schema read new export |
| **LLM Draft seam: mandatory or optional** | Mandatory for all proposals / Optional fallback | **Optional** — deterministic seam always works; LLM is accelerator |
| **Release cadence** | Continuous (on every merge) / Weekly / On-demand | **On-demand** — kernel releases are governance events |

---

## 8. Next Immediate Actions (This Week)

1. **Apply Phase 0 fixes** — export provenance, SHACL report, projection drift checker, enum sync
2. **Run full validation** — confirm 0 regressions
3. **Create `feat/axiom-kernel` branch** — commit Phase 0
4. **Open PR** — with audit findings + plan as description
5. **Human review** — decide on Decision Points above

---

## Appendix: KO板 Operational Takeaways

1. **SHACL ValidationReport** — adopt exact structure (`sh:conforms`, `sh:result[]` with severity, focusNode, resultPath, sourceConstraintComponent, message) for all kernel validation
2. **LinkML migration tooling** — `linkml-map` pattern for data migration scripts; make migration first-class, not ad-hoc
3. **OBO obsoletion** — use `owl:deprecated` + `IAO:0100001 replaced_by` + `consider` for every deprecated term/relation
4. **ROBOT pipeline** — model kernel release as `extract → merge → reason → annotate → diff → report → init`
5. **Wikidata proposal process** — formal proposal→discussion→closure with constraint severity (mandatory/suggestion) and public dashboard
6. **Confluent compatibility modes** — declare BACKWARD/FORWARD/FULL per track; never collapse tracks
