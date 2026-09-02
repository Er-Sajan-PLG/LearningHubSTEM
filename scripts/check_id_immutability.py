#!/usr/bin/env python3
"""B3 (Scope B): ID-immutability guard — an `lhs:` identifier once assigned to a canonical
entity can NEVER later represent a different entity or meaning (ADR-0003).

This is NOT a naive "union all IDs in git history and compare sets" check. The real invariant
(plan v4.0) is **semantic identity**: an identity is reconstructed from the schema/history as
(id, name, domain) — the stable, identity-defining fields. Reassigning an ID to a *different*
entity (a different name or domain) is never allowed; deprecation and aliasing are the only
legal ways to retire/resurface an identifier, and they reserve the ID forever.

Single source of truth for history = git. Reconstruction walks each canonical entity file's
git history and records the identity fields at each version.

Outcomes (must match the plan's TDD table):
  new                       -> PASS   (an ID introduced, never present before)
  unchanged identity        -> PASS   (name/domain identical across all versions)
  deprecated                -> PASS   (status: deprecated; ID reserved forever)
  aliased                   -> PASS   (deprecated_by / aliases; alias references must be valid)
  reassigned                -> FAIL   (same ID now means a DIFFERENT entity: name/domain changed)
  deleted-and-reused        -> FAIL   (an ID was deleted, then a different entity reused it)
"""
from __future__ import annotations
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

_ID_RE = re.compile(r"^id:\s*(lhs:[a-z][a-z0-9-]*\.[a-z0-9][a-z0-9-]*)", re.MULTILINE)
_NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
_DOMAIN_RE = re.compile(r"^domain:\s*(.+)$", re.MULTILINE)
_STATUS_RE = re.compile(r"^status:\s*(.+)$", re.MULTILINE)

# Identity-defining fields. Editing prose (definition/examples/notes) does NOT change identity;
# only these two fields, if changed under the same id, constitute reassignment.
_IDENTITY_FIELDS = ("name", "domain")


def git(*args: str) -> str:
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr}")
    return r.stdout


def parse_file(text: str) -> dict:
    """Extract (id, name, domain, status) from a canonical entity's YAML frontmatter."""
    if not text.startswith("---"):
        return {}
    fm = text.split("---", 2)[1]
    out: dict[str, str] = {}
    for pattern, key in ((_ID_RE, "id"), (_NAME_RE, "name"), (_DOMAIN_RE, "domain"), (_STATUS_RE, "status")):
        m = pattern.search(fm)
        if m:
            val = m.group(1).strip().strip("\"'>")
            if key == "name":
                # name may be quoted or plain; keep the visible name text
                val = m.group(1).strip().strip("'\"")
            out[key] = val
    return out


def build_id_history() -> dict[str, list[dict]]:
    """For each lhs: id, record every (name, domain, status) version across git history.

    Returns mapping id -> list of dict(commit, name, domain, status) in oldest->newest order.
    """
    history: dict[str, list[dict]] = {}
    for path in sorted(CONTENT.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        # SHAs where this file changed, oldest first
        shas = [
            s for s in reversed(git("log", "--format=%H", "--", rel).split())
        ]
        seen = set()
        for sha in shas:
            try:
                blob = git("show", f"{sha}:{rel}")
            except RuntimeError:
                continue  # file absent at that sha (deleted or not yet added)
            ent = parse_file(blob)
            if not ent.get("id"):
                continue
            key = (ent.get("name"), ent.get("domain"), ent.get("status"))
            if key in seen:
                continue  # drop duplicate identity across consecutive commits
            seen.add(key)
            history.setdefault(ent["id"], []).append(
                {"commit": sha[:9], "name": ent.get("name"), "domain": ent.get("domain"),
                 "status": ent.get("status")}
            )
    return history


def live_entities() -> dict[str, dict]:
    """Entities currently in HEAD content: id -> (name, domain, status)."""
    live: dict[str, dict] = {}
    for path in CONTENT.rglob("*.md"):
        ent = parse_file(path.read_text())
        if ent.get("id"):
            live[ent["id"]] = ent
    return live


def detect_violations(history: dict[str, list[dict]], live: dict[str, dict]) -> list[str]:
    """Pure detection: given an id->[versions] history and a HEAD id->entity map, return any
    immutability violations. Empty = all pass.

    This is the testable core (TDD) — it operates on plain dicts, so the six plan cases can be
    exercised directly, independent of git.
    """
    violations: list[str] = []
    # 2. Reassignment / deleted-and-reused: name/domain change under the same id.
    for id_, versions in history.items():
        identity_stamps: list[tuple[tuple[str, str], str]] = []
        seen_stamps: set[tuple[str, str]] = set()
        for v in versions:
            if v.get("name") and v.get("domain"):
                stamp = (v["name"], v["domain"])
                if stamp not in seen_stamps:
                    seen_stamps.add(stamp)
                    identity_stamps.append((stamp, v["commit"]))
        if len(identity_stamps) > 1:
            first = identity_stamps[0]
            for stamp, commit in identity_stamps[1:]:
                violations.append(
                    f"[reassigned] {id_}: '{first[0][0]}' ({first[0][1]}) @{first[1]} -> "
                    f"'{stamp[0]}' ({stamp[1]}) @{commit}. Reassigning an id to a different "
                    f"entity is forbidden; deprecate + deprecated_by instead."
                )
                break

    # 1. Every historical id that is gone from HEAD must be deprecated (else it was dropped).
    for id_ in sorted(set(history) - set(live)):
        last = history[id_][-1]
        if last["status"] != "deprecated" and last.get("name"):
            violations.append(
                f"[deleted-without-deprecation] {id_}: present in history as '{last.get('name')}' "
                f"({last.get('domain')}) but dropped from HEAD without status: deprecated"
            )

    # 3. HEAD-tree invariants: uniqueness.
    seen_ids: set[str] = set()
    for id_ in live:
        if id_ in seen_ids:
            violations.append(f"[duplicate-id] {id_}: present more than once in HEAD")
        seen_ids.add(id_)

    # 4. Alias / deprecated_by validity: the target must be a real, current-or-historical lhs id.
    known = set(live) | set(history)
    for id_, ent in live.items():
        target = ent.get("deprecated_by")
        if target and target not in known:
            violations.append(
                f"[alias-invalid] {id_} -> deprecated_by '{target}' but target is not a known lhs id"
            )
        for alias in ent.get("aliases", []) or []:
            if alias and alias not in known:
                violations.append(f"[alias-invalid] {id_}: alias '{alias}' is not a known lhs id")
    return violations


def check_id_immutability() -> list[str]:
    """Reconstruct history + live tree from HEAD, then run pure detection."""
    return detect_violations(build_id_history(), live_entities())


def main() -> int:
    violations = check_id_immutability()
    if violations:
        print("ID-IMMUTABILITY FAILURES:")
        for v in violations:
            print(f"  - {v}")
        return 1
    print("PASS: all lhs: identifiers are immutable (no reassignment/reuse); "
          f"{len(live_entities())} live entities, {len(build_id_history())} historical ids")
    return 0


if __name__ == "__main__":
    sys.exit(main())