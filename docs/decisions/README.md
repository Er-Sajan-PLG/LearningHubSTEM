# DECISIONS — STEMMA Foundation

Decision records for the STEMMA foundation (Phase 1 — Foundation Definition & Freeze).

Each record follows the same shape:

- Context
- Decision
- Alternatives considered
- Reason
- Consequences
- Status (`decided` or `pending` + human approval required)
- Related

| # | Record | Subject | Status |
|---|--------|---------|--------|
| 0001 | [license.md](0001-license.md) | Knowledge + code licensing | decided (2026-09-02) |
| 0002 | [canonical-representation.md](0002-canonical-representation.md) | Markdown + YAML frontmatter; canonical vs derived | decided (documented) |
| 0003 | [identity.md](0003-identity.md) | Stable ID rules and lifecycle | decided (documented) |
| 0004 | [entity-model.md](0004-entity-model.md) | Six entity types | decided (documented) |
| 0005 | [relationship-vocabulary.md](0005-relationship-vocabulary.md) | Core relationship vocabulary | decided (documented) |
| 0006 | [lifecycle-and-provenance.md](0006-lifecycle-and-provenance.md) | Lifecycle + provenance model | decided (documented) |
| 0007 | [export-contract.md](0007-export-contract.md) | Versioned export / consumer contract | decided (documented) |
| 0008 | [versioning.md](0008-versioning.md) | Schema / export / content versioning | decided (documented) |
| 0009 | [multilingual-principle.md](0009-multilingual-principle.md) | Language-independent identity | decided (documented) |
| 0010 | [0010-entity-metadata-extension.md](0010-entity-metadata-extension.md) | Optional equation/symbol/unit/common_misconceptions fields (Phase 2) | decided (documented) |
| 0011 | [0011-connection-assertion-model.md](0011-connection-assertion-model.md) | First-class connection (source–relation–target + assertion) objects | decided (documented) |
| 0012 | [0012-relation-vocabulary.md](0012-relation-vocabulary.md) | Controlled relation vocabulary + registry | decided (documented) |
| 0013 | [0013-confidence-semantics.md](0013-confidence-semantics.md) | Confidence / uncertainty semantics | decided (documented) |
| 0014 | [0014-inference-semantics.md](0014-inference-semantics.md) | Inferred vs asserted knowledge semantics | decided (documented) |
| 0015 | [0015-evidence-provenance.md](0015-evidence-provenance.md) | Evidence vs provenance separation; canonical sources | decided (Phase A) |
| 0016 | [0016-metadata-urgent-rework.md](0016-metadata-urgent-rework.md) | Urgent additive metadata v0.2 (polarity, timestamps, rights...) | decided |
| 0017 | [0017-adaptive-metadata-extensions.md](0017-adaptive-metadata-extensions.md) | Adaptive extension registry — governed open metadata seam | decided (implemented) |
| 0018 | [0018-historical-attribution.md](0018-historical-attribution.md) | Historical scientific attribution — who stated it + when (who/when/timeline) | decided (implemented) |

| 0019 | [0019-rename-and-freeze.md](0019-rename-and-freeze.md) | Rename foundation to STEMMA; freeze lhs identity + schema/export contracts | decided (implemented) |
| 0020 | [0020-connections-only-truth.md](0020-connections-only-truth.md) | Connections-only relationship truth; inline block = generated projection (plan v2 E1) | decided (implemented) |
| 0021 | [0021-registry-integrity.md](0021-registry-integrity.md) | Registry integrity: +phenomenon/model/experiment types, inverse coherence, vocabulary enforcement, honest context data (plan v2 E2/E6.2) | decided (implemented) |
| 0022 | [0022-version-source-deterministic-exports.md](0022-version-source-deterministic-exports.md) | Single version source (schema/VERSION.yaml) + deterministic content_hash exports (plan v2 E5.1/E5.2) | decided (implemented) |
| 0023 | [0023-export-contract-v1-identity-hardening.md](0023-export-contract-v1-identity-hardening.md) | Export contract **v1.0** (connections/sources required; gate G-A) + `external_ids` format checks + agent registry (plan v2 E1.5/E4.1/E4.2) | decided (implemented) |
| 0024 | [0024-math-layer.md](0024-math-layer.md) | STEM math layer: canonical LaTeX + symbol bindings + ISQ dimensions + unit entities (plan v2 E3.1) | **PROPOSED — gate G-C** |
| 0025 | [0025-activation-phrase.md](0025-activation-phrase.md) | Retire "ACTIVATE LEARNINGHUBSTEM MVP"; active phrase is "ACTIVATE STEMMA MVP" (plan v2 E0.3 / R2) | decided (implemented) |
| 0026 | [0026-claim-identity.md](0026-claim-identity.md) | Claim identity: derived `claim_signature` + duplicate-claim gate + immutable connection triples (plan v2 E4.3/E4.5, E1.6 explorer trust view) | decided (implemented) |

**Freeze rule:** a change to any subject above requires a documented decision (see specification
§17). Minor editorial improvements do not.
