# reports/ — generated operational artifacts

Everything here is **derived** from canonical content by the scripts in the
verify chain and is regenerated on every run (CI enforces freshness via
`git diff --exit-code`).

- `validation-report.json` — gate result + content hash (`scripts/validate.py`)
- `epistemic-summary.*` — review-coverage epistemics (`scripts/epistemic_summary.py`)
- `integrity-anomalies.*` — standing anomaly reporter (target: 0)
- `curation-status.*`, `curation-pilot.md` — review workflow state
- `dependency-review-campaign/` — **human review worksheets.** The `batch-NN.yaml`
  files are the one writable exception: a human fills `decision:` and applies it
  with `scripts/apply_review_decisions.py` (recorded as the human, never a process).
  Regeneration rebuilds worksheets from canonical review state: applied decisions
  already live in `connections/` (as review status + history), and only *unfilled*
  pending decisions would be lost by regenerating before they are applied.

Do not hand-edit anything else here; fix the generator or the canonical data
instead.
