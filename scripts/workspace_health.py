"""Read-only governance checks and observed state; no provider, publication or cleanup."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from datetime import datetime
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DOC_BUDGETS = {
    "AGENTS.md": (190, 18000),
    "PROJECT_BRAIN.md": (70, 5000),
    "IMPLEMENT_PLAN.md": (60, 5000),
    "ARCHITECTURE.md": (160, 15000),
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], encoding="utf-8").rstrip("\r\n")


def chapters(ranges: list[str]) -> set[str]:
    ids: set[str] = set()
    for value in ranges:
        match = re.fullmatch(r"ch(\d+)(?:-ch(\d+))?", value)
        if not match:
            raise ValueError(f"invalid chapter range: {value}")
        start = int(match[1])
        end = int(match[2] or match[1])
        if start < 1 or end < start:
            raise ValueError(f"invalid chapter range: {value}")
        ids.update(f"ch{n:03d}" for n in range(start, end + 1))
    return ids


def reader_state(root: Path, novel: dict) -> dict:
    slug = novel["slug"]
    reader = novel.get("reader", {})
    target = chapters([f"ch{reader.get('first_chapter', 1):03d}-ch{reader['last_chapter']:03d}"]) if reader.get("enabled") else set()
    manifest = root / "MoonRead/content/generated/books" / slug / "manifest.json"
    errors: list[str] = []
    available: set[str] = set()
    if manifest.is_file():
        items = load(manifest)["chapters"]
        ids = [item["id"] for item in items]
        if len(ids) != len(set(ids)):
            errors.append(f"{slug}: duplicate reader chapter IDs")
        for item in items:
            if item.get("status") == "available":
                cid = item["id"]
                available.add(cid)
                path = manifest.parent / "chapters" / f"{cid}.md"
                if not re.fullmatch(r"ch\d+", cid) or not path.is_file():
                    errors.append(f"{slug}: reader file missing/invalid: {cid}")
        if set(ids) != target or available != target:
            errors.append(f"{slug}: reader snapshot differs from registry target")
    elif target:
        errors.append(f"{slug}: reader manifest missing")
    output = root / novel["folder"] / novel.get("output_dir", "05_Output")
    local = {p.stem for p in output.glob("ch*/ch*.md") if p.parent.name == p.stem} if output.is_dir() else None
    return {
        "novel": slug,
        "reader_target_range": f"{min(target)}-{max(target)}" if target else None,
        "reader_target_count": len(target),
        "reader_snapshot_count": len(available),
        "local_output_count": len(local) if local is not None else None,
        "local_only_ids": sorted(local - target) if local is not None else None,
        "local_missing_target": sorted(target - local) if local is not None else None,
        "local_data_status": "observed-not-accepted-or-published" if local is not None else "unavailable-in-this-checkout",
        "live_publication": "not-probed",
        "errors": errors,
    }


def report_index(root: Path, query: str = "") -> dict:
    directories = [root / "07_Reports", *sorted(root.glob("*/07_Reports"))]
    groups: dict[str, list[Path]] = {}
    for directory in directories:
        for path in directory.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".json"}:
                continue
            relative = path.relative_to(root).as_posix()
            if query.casefold() not in relative.casefold():
                continue
            # Pair JSON/Markdown, then fold dated Sentinel reruns into their scope.
            scope = re.sub(r"_\d{8}_\d{6}(?:_\d+)?$", "", path.stem)
            key = f"{directory.relative_to(root).as_posix()}/{scope}"
            groups.setdefault(key, []).append(path)
    results = []
    for scope, paths in sorted(groups.items()):
        paths.sort(key=lambda p: (p.stem, p.relative_to(root).as_posix()), reverse=True)
        newest = paths[0].stem
        results.append({
            "scope": scope,
            "latest": [p.relative_to(root).as_posix() for p in paths if p.stem == newest],
            "older_files": len([p for p in paths if p.stem != newest]),
        })
    return {"matching_files": sum(len(p) for p in groups.values()), "scope_count": len(results), "scopes": results}


def quality_metrics(root: Path) -> dict:
    ledger = load(root / "00_Config/quality_incidents.json")
    cohorts: dict[str, dict] = {}
    seen_ids: set[str] = set()
    exposures: set[tuple[str, str]] = set()
    historical: set[tuple[str, str]] = set()
    for cohort in ledger["publication_cohorts"]:
        key = cohort["id"]
        if key in cohorts or not cohort.get("evidence"):
            raise ValueError(f"duplicate/unproven publication cohort: {key}")
        ids = chapters(cohort["chapters"])
        if cohort.get("kind") not in {"historical-reader-snapshot", "verified-publication"}:
            raise ValueError(f"cohort needs explicit publication provenance: {key}")
        if cohort["kind"] == "verified-publication" and not all(cohort.get(k) for k in ("verified_at", "revision", "live_url")):
            raise ValueError(f"publication needs timestamp, revision and live URL: {key}")
        if cohort["kind"] == "verified-publication":
            datetime.fromisoformat(cohort["verified_at"])
            if not cohort["live_url"].startswith("https://"):
                raise ValueError(f"publication needs an HTTPS live URL: {key}")
        if not (root / cohort["evidence"]).is_file():
            raise ValueError(f"cohort evidence missing: {key}")
        cohort = {**cohort, "ids": ids}
        cohorts[key] = cohort
        target = exposures if cohort["kind"] == "verified-publication" else historical
        target.update((cohort["novel"], cid) for cid in ids)
    reader_incidents = []
    for incident in ledger["incidents"]:
        key = incident["id"]
        if key in seen_ids:
            raise ValueError(f"duplicate incident ID: {key}")
        seen_ids.add(key)
        cohort = cohorts.get(incident["publication_cohort"])
        if not cohort or incident["novel"] != cohort["novel"] or not chapters(incident["chapters"]) <= cohort["ids"]:
            raise ValueError(f"incident outside publication cohort: {key}")
        if incident.get("detected_by") not in {"reader", "inspector", "gate"} or not incident.get("evidence"):
            raise ValueError(f"incident needs detector and evidence: {key}")
        date.fromisoformat(incident["discovered_on"])
        if not (root / incident["evidence"]).is_file():
            raise ValueError(f"incident evidence missing: {key}")
        if incident["detected_by"] == "reader":
            reader_incidents.append((key, cohort["kind"]))
    if not isinstance(ledger.get("history_complete"), bool):
        raise ValueError("history_complete must be explicit")
    count = len(exposures)
    measured = sum(kind == "verified-publication" for _, kind in reader_incidents)
    historical_count = sum(kind == "historical-reader-snapshot" for _, kind in reader_incidents)
    rate = 10 * measured / count if count else None
    return {
        "definition": ledger["definition"],
        "history_complete": ledger["history_complete"],
        "distinct_first_published_chapters": count,
        "known_reader_incidents": len(reader_incidents),
        "reader_incident_ids": [key for key, _ in reader_incidents],
        "historical_snapshot_chapters": len(historical),
        "defect_escape_rate_per_10": rate,
        "rate_scope": "recorded verified-publication cohorts only; historical snapshots excluded",
        "retrospective_snapshot_ratio_lower_bound_per_10": 10 * historical_count / len(historical) if historical else None,
        "known_published_cohort_incidence_per_10": rate,
        "interpretation": "incomplete historical ascertainment; not evidence of improving quality" if not ledger["history_complete"] else "observed incidence, not proof of semantic correctness",
    }


def check(root: Path) -> dict:
    errors: list[str] = []
    sizes = {}
    for name, (max_lines, max_chars) in DOC_BUDGETS.items():
        text = (root / name).read_text(encoding="utf-8")
        sizes[name] = {"lines": len(text.splitlines()), "chars": len(text)}
        if len(text.splitlines()) > max_lines or len(text) > max_chars:
            errors.append(f"{name}: exceeds budget {max_lines} lines/{max_chars} chars; replace current state, move history to evidence")
    registry = load(root / "00_Config/novel_registry.json")
    snapshots = [reader_state(root, novel) for novel in registry["novels"]]
    for snapshot in snapshots:
        errors.extend(snapshot["errors"])
    try:
        metrics = quality_metrics(root)
    except (KeyError, TypeError, ValueError, OSError) as exc:
        errors.append(f"quality ledger: {exc}")
        metrics = {"unverified": True}
    return {"passed": not errors, "control_sizes": sizes, "errors": errors, "quality": metrics}


def status(root: Path) -> dict:
    registry = load(root / "00_Config/novel_registry.json")
    rows = [reader_state(root, novel) for novel in registry["novels"]]
    dirty = git(root, "status", "--porcelain=v1", "--untracked-files=all").splitlines()
    categories = Counter()
    for line in dirty:
        path = line[3:].strip('"')
        category = "reader_snapshot" if path.startswith("MoonRead/content/generated/") else "machine_reports" if "sentinel_quality_" in path else "other_wip"
        categories[category] += 1
    return {
        "head": git(root, "rev-parse", "HEAD"),
        "branch": git(root, "branch", "--show-current"),
        "worktree_clean": not dirty,
        "dirty_entries": len(dirty),
        "dirty_categories": dict(categories),
        "reproducibility": "versioned code/policy/reader snapshot only; local raw/run evidence is not included",
        "novels": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "status", "reports", "quality"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--query", default="", help="Case-insensitive report path filter")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == "check":
        result = check(root)
    elif args.command == "status":
        result = status(root)
    elif args.command == "reports":
        result = report_index(root, args.query)
    else:
        result = quality_metrics(root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(args.command == "check" and not result["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
