from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
NOVEL_ROOT = REPO.parent
HGD_ROOT = NOVEL_ROOT / "Horror Game Developers"
HGD_OUTPUT = HGD_ROOT / "05_Output"
DEFAULT_DRY_RUN_ROOT = REPO / "04_Work" / "_experiments" / "hgd_layout_projection_dry_run_v6_17"


@dataclass
class ApplyResult:
    chapter: str
    source_path: Path
    projected_path: Path
    backup_path: Path
    destination_path: Path


def load_validated_dry_run(dry_run_root: Path, *, first: int, last: int) -> list[dict]:
    summary_path = dry_run_root / "summary.json"
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    expected = {f"ch{number:03d}" for number in range(first, last + 1)}
    by_chapter = {item["chapter"]: item for item in data}
    missing = sorted(expected - set(by_chapter))
    if missing:
        raise RuntimeError(f"Dry-run summary missing chapters: {', '.join(missing)}")
    invalid = [chapter for chapter in sorted(expected) if by_chapter[chapter]["status"] != "valid"]
    if invalid:
        raise RuntimeError(f"Dry-run summary has non-valid chapters: {', '.join(invalid)}")
    return [by_chapter[f"ch{number:03d}"] for number in range(first, last + 1)]


def apply_projection(*, dry_run_root: Path, first: int, last: int, backup_root: Path) -> list[ApplyResult]:
    dry_run_rows = load_validated_dry_run(dry_run_root, first=first, last=last)
    results: list[ApplyResult] = []
    for row in dry_run_rows:
        chapter = row["chapter"]
        source_path = HGD_OUTPUT / chapter / f"{chapter}.md"
        projected_path = dry_run_root / chapter / f"{chapter}.md"
        backup_path = backup_root / chapter / f"{chapter}.md"
        destination_path = source_path
        if not source_path.exists():
            raise RuntimeError(f"Missing HGD output: {source_path}")
        if not projected_path.exists():
            raise RuntimeError(f"Missing projected output: {projected_path}")
        results.append(
            ApplyResult(
                chapter=chapter,
                source_path=source_path,
                projected_path=projected_path,
                backup_path=backup_path,
                destination_path=destination_path,
            )
        )

    for result in results:
        result.backup_path.parent.mkdir(parents=True, exist_ok=True)
        result.destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(result.source_path, result.backup_path)
        shutil.copy2(result.projected_path, result.destination_path)
    return results


def render_report(results: list[ApplyResult], backup_root: Path, dry_run_root: Path) -> str:
    lines = [
        "# HGD Layout Projection Apply Report",
        "",
        "Scope: applies validated dry-run projected Markdown to Horror Game Developer output.",
        f"Dry-run root: `{dry_run_root}`",
        f"Backup root: `{backup_root}`",
        "",
        "## Summary",
        "",
        f"- chapters applied: {len(results)}",
        "- source output was backed up before overwrite",
        "",
        "| chapter | backup | destination |",
        "| --- | --- | --- |",
    ]
    for result in results:
        lines.append(f"| {result.chapter} | `{result.backup_path}` | `{result.destination_path}` |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply validated HGD layout projection dry-run outputs.")
    parser.add_argument("--first", type=int, default=1)
    parser.add_argument("--last", type=int, default=35)
    parser.add_argument("--dry-run-root", type=Path, default=DEFAULT_DRY_RUN_ROOT)
    parser.add_argument("--backup-root", type=Path)
    args = parser.parse_args()

    backup_root = args.backup_root
    if backup_root is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_root = HGD_ROOT / f"05_Output_backup_before_v6_17_layout_projection_{stamp}"
    results = apply_projection(
        dry_run_root=args.dry_run_root,
        first=args.first,
        last=args.last,
        backup_root=backup_root,
    )
    report = render_report(results, backup_root, args.dry_run_root)
    report_path = REPO / "07_Reports" / "hgd_layout_projection_apply_v6_17.md"
    report_path.write_text(report, encoding="utf-8")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
