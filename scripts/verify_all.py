#!/usr/bin/env python3
"""Verify hook chain — ECC verify analogue."""
import subprocess
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
steps = [
    ["python3", str(ROOT / "scripts/validate.py")],
    ["python3", str(ROOT / "scripts/epistemic_summary.py")],
    ["python3", str(ROOT / "scripts/integrity_anomalies.py")],
    ["python3", str(ROOT / "scripts/graph_analysis.py")],
    ["python3", str(ROOT / "scripts/export_review_aware.py")],
    ["python3", str(ROOT / "scripts/curation_status.py")],
    ["python3", str(ROOT / "tests/phase-b/test_phase_b.py")],
    ["python3", str(ROOT / "tests/phase-b/test_boundary.py")],
    ["python3", str(ROOT / "tests/curation/test_curation.py")],
]
for cmd in steps:
    print(f"RUN: {' '.join(cmd)}")
    r = subprocess.run(cmd)
    if r.returncode != 0:
        print(f"FAIL: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(1)
print("OK: all verify steps pass")
