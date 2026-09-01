# Epistemic Summary — v0.2

Deterministic report over all `connections/*.yaml` (explicit fields only).

- Total connection records (canonical objects): **397**
- Canonical scientific assertions (`review.status == canonical`): **50**
- Proposed: 396, Asserted: 1, Inferred: 0
- Review: unreviewed 347, reviewed-only 0, canonical 50 (total reviewed including canonical: 50)
- Status: active 397, deprecated 0, rejected 0
- Origin: migrated 384, human-authored 13, llm-authored 0
- With confidence: 1, without: 396
- Human reviewed_by present: 50

> Canonical object (file exists in `connections/`) != canonical scientific assertion.
> Canonical is terminal reviewed state (reviewed-only 0, canonical 15). `review.status==canonical` implies reviewed.
> A migrated connection is a canonical object with `review.status=unreviewed` until human review.

## By assertion type
{'proposed': 396, 'asserted': 1}

## By review
{'canonical': 50, 'unreviewed': 347}

## By origin
{'migrated': 384, 'human-authored': 13}

## By method
{'migration': 384, 'manual': 13}

Machine-readable: `reports/epistemic-summary-v0.2.json`
