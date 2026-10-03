from __future__ import annotations

from pathlib import Path


def chapter_dir(base: Path, chapter_id: str) -> Path:
    return base / chapter_id


def block_artifact_path(base: Path, chapter_id: str, block_id: str, suffix: str) -> Path:
    return chapter_dir(base, chapter_id) / f"{block_id}.{suffix}"


def glossary_scan_artifact_path(base: Path, chapter_id: str) -> Path:
    return chapter_dir(base, chapter_id) / "glossary_scan.json"


def batch_glossary_scan_artifact_path(base: Path, run_id: str) -> Path:
    return base / "_batch" / run_id / "glossary_scan.json"
