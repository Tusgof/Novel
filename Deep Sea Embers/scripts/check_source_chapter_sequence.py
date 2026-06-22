#!/usr/bin/env python
"""Check local chapter ids against source chapter numbers.

This guard catches cases where a local chapter was overwritten by a stale
source manifest and now points to the wrong source chapter.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


CHAPTER_RE = re.compile(r"\bChapter\s+(\d+)\b", re.IGNORECASE)
RANGE_RE = re.compile(r"^ch(\d{3})-ch(\d{3})$")


def parse_chapter_range(value: str) -> tuple[int, int]:
    match = RANGE_RE.match(value)
    if not match:
        raise argparse.ArgumentTypeError("range must look like ch001-ch220")
    start = int(match.group(1))
    end = int(match.group(2))
    if start > end:
        raise argparse.ArgumentTypeError("range start must be <= end")
    return start, end


def source_number(source: dict, path: Path) -> int:
    metadata = source.get("metadata") or {}
    web_number = metadata.get("web_chapter") or metadata.get("source_chapter")
    if isinstance(web_number, int):
        return web_number
    if isinstance(web_number, str) and web_number.isdigit():
        return int(web_number)

    title = str(source.get("title") or "")
    match = CHAPTER_RE.search(title)
    if match:
        return int(match.group(1))

    raise ValueError(f"cannot find source chapter number in {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--novel-dir", required=True, type=Path)
    parser.add_argument("--chapters", required=True, type=parse_chapter_range)
    parser.add_argument(
        "--allow-gap",
        action="append",
        default=[],
        help="Allowed transition, e.g. ch120:121->123 for intentional source gaps.",
    )
    args = parser.parse_args()

    novel_dir = args.novel_dir
    start, end = args.chapters
    allowed = set(args.allow_gap)

    rows: list[tuple[str, int, str]] = []
    errors: list[str] = []

    for index in range(start, end + 1):
        chapter_id = f"ch{index:03d}"
        path = novel_dir / "03_Raw" / chapter_id / "source.json"
        if not path.exists():
            errors.append(f"{chapter_id}: missing {path}")
            continue
        try:
            source = json.loads(path.read_text(encoding="utf-8-sig"))
            number = source_number(source, path)
        except Exception as exc:  # noqa: BLE001 - report malformed source files.
            errors.append(f"{chapter_id}: {exc}")
            continue
        rows.append((chapter_id, number, str(source.get("title") or "")))

    for previous, current in zip(rows, rows[1:]):
        prev_id, prev_number, _ = previous
        current_id, current_number, current_title = current
        transition = f"{prev_id}:{prev_number}->{current_number}"
        if current_number == prev_number + 1 or transition in allowed:
            continue
        errors.append(
            f"{current_id}: source chapter jumped from {prev_number} to "
            f"{current_number} ({current_title})"
        )

    if errors:
        print("source_chapter_sequence: failed")
        for error in errors:
            print(f"- {error}")
        return 1

    if rows:
        print(
            "source_chapter_sequence: passed "
            f"({rows[0][0]} source {rows[0][1]} -> {rows[-1][0]} source {rows[-1][1]})"
        )
    else:
        print("source_chapter_sequence: passed (empty range)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
