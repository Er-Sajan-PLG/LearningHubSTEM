import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports" / "migration-reconciliation-v0.2.json"


def test_reconciliation_exists():
    assert REPORT.exists(), "migration reconciliation report missing"


def test_all_legacy_accounted():
    data = json.loads(REPORT.read_text())
    assert data["legacy_relationship_records"] == 376
    assert data["migrated_connections"] == 376
    assert data["matched"] == 376
    assert data["orphaned_target_references"] == 0
    assert data["invalid_relation_types"] == 0
    assert data["duplicate_canonical"] == 0
    assert data["invariant_holds"] is True


def test_no_silent_loss():
    conns = list((ROOT / "connections").glob("*.yaml"))
    assert len(conns) == 377  # 376 migrated + 1 manual
    # Every legacy triple has exactly one migrated conn
    legacy = []
    for p in (ROOT / "content").rglob("*.md"):
        d = yaml.safe_load(p.read_text().split("---", 2)[1])
        for rel in d.get("relationships", []) or []:
            legacy.append((d["id"], rel["type"], rel["target"]))
    migrated = set()
    for p in (ROOT / "connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        prov = d.get("provenance", {})
        if prov.get("method", {}).get("type") == "migration":
            migrated.add((d["source"], d["relation"], d["target"]))
    for triple in legacy:
        assert triple in migrated, f"legacy {triple} not migrated"


def test_no_duplicate_migration():
    ids = [yaml.safe_load(p.read_text())["id"] for p in (ROOT / "connections").glob("*.yaml")]
    assert len(ids) == len(set(ids)), "duplicate connection IDs"
    # Idempotence: running migrate again creates 0
    import subprocess

    r = subprocess.run(["python3", str(ROOT / "scripts/migrate_relationships.py")], capture_output=True, text=True)
    assert r.returncode == 0
    assert "skipped 376" in r.stdout or "created 0" in r.stdout
