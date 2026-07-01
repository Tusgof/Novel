"""Verify that an experiment vault uses the same raw source as its novel vault.

This is intentionally read-only. It compares chapter source files by title,
source_url, and raw_text hash so a treatment/OOS experiment cannot silently run
against stale copied raw files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _load_source(path: Path) -> dict:
    if not path.exists():
        return {"__missing__": True}
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def _raw_hash(data: dict) -> str:
    raw_text = data.get("raw_text")
    if not isinstance(raw_text, str):
        raw_text = ""
    return hashlib.sha256(raw_text.encode("utf-8")).hexdigest()


def _chapter_ids(value: str) -> list[str]:
    chapters = [item.strip() for item in value.split(",") if item.strip()]
    if not chapters:
        raise argparse.ArgumentTypeError("at least one chapter id is required")
    return chapters


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--novel-root", required=True, type=Path)
    parser.add_argument("--experiment-root", required=True, type=Path)
    parser.add_argument("--chapters", required=True, type=_chapter_ids)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    findings: list[dict] = []
    for chapter_id in args.chapters:
        rel = Path("03_Raw") / chapter_id / "source.json"
        novel_path = args.novel_root / rel
        experiment_path = args.experiment_root / rel
        novel = _load_source(novel_path)
        experiment = _load_source(experiment_path)

        chapter_findings: list[str] = []
        if novel.get("__missing__"):
            chapter_findings.append("novel_source_missing")
        if experiment.get("__missing__"):
            chapter_findings.append("experiment_source_missing")
        if not chapter_findings:
            if novel.get("title") != experiment.get("title"):
                chapter_findings.append("title_mismatch")
            if novel.get("source_url") != experiment.get("source_url"):
                chapter_findings.append("source_url_mismatch")
            if _raw_hash(novel) != _raw_hash(experiment):
                chapter_findings.append("raw_text_hash_mismatch")

        if chapter_findings:
            findings.append(
                {
                    "chapter_id": chapter_id,
                    "findings": chapter_findings,
                    "novel_title": novel.get("title"),
                    "experiment_title": experiment.get("title"),
                    "novel_source_url": novel.get("source_url"),
                    "experiment_source_url": experiment.get("source_url"),
                }
            )

    result = {
        "novel_root": str(args.novel_root),
        "experiment_root": str(args.experiment_root),
        "chapters_checked": args.chapters,
        "mismatch_count": len(findings),
        "findings": findings,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Checked {len(args.chapters)} chapters")
        print(f"Mismatches: {len(findings)}")
        for finding in findings:
            print(
                f"- {finding['chapter_id']}: {', '.join(finding['findings'])}; "
                f"novel={finding.get('novel_title')!r}; "
                f"experiment={finding.get('experiment_title')!r}"
            )
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

