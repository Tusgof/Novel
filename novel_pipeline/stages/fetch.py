from __future__ import annotations

import json
from pathlib import Path

from novel_pipeline.adapters.base import FetchAdapter
from novel_pipeline.artifacts import chapter_dir
from novel_pipeline.files import atomic_write_json
from novel_pipeline.text_utils import normalize_whitespace
from novel_pipeline.types import AppConfig, ChapterMeta, ChapterSource


def _derive_title_from_body_if_generic(title: str, raw_text: str) -> str:
    """Use early body subtitle when the adapter only knows a generic Chapter N."""
    cleaned_title = title.strip()
    if not cleaned_title:
        return title
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if len(lines) < 3:
        return title
    if not lines[0].lower().startswith("chapter "):
        return title
    if lines[0] != cleaned_title:
        return title
    separator_chars = set("─-—_=*")
    if not lines[1] or any(ch not in separator_chars for ch in lines[1]):
        return title
    subtitle = lines[2].strip()
    if not subtitle or subtitle.lower().startswith("chapter "):
        return title
    return f"{cleaned_title} - {subtitle}"


def load_or_build_manifest(
    *,
    config: AppConfig,
    adapter: FetchAdapter,
    force: bool = False,
) -> list[ChapterMeta]:
    """Load cached manifest or build from TOC and cache it."""
    manifest_path = config.workspace.raw / "manifest.json"
    if not force and manifest_path.exists():
        raw = manifest_path.read_text(encoding="utf-8")
        entries = json.loads(raw)
        return [ChapterMeta(**e) for e in entries]
    manifest = adapter.build_manifest()
    atomic_write_json(manifest_path, manifest)
    return manifest


def resolve_chapter_meta(
    manifest: list[ChapterMeta],
    chapter_id: str,
) -> ChapterMeta:
    """Find a ChapterMeta by chapter_id. Raises ValueError if not found.

    Some source adapters keep local chapter IDs by TOC position while also
    storing the real website chapter number in metadata.site_chapter. When a
    caller asks for ch237, prefer a real site_chapter=237 entry over a TOC
    ordinal ch237 entry so local output numbering follows the source chapter.
    """
    numeric_id = chapter_id.removeprefix("ch")
    if numeric_id.isdigit():
        target_number = int(numeric_id)
        for meta in manifest:
            site_chapter = meta.metadata.get("site_chapter")
            if isinstance(site_chapter, int) and site_chapter == target_number:
                return meta
            if isinstance(site_chapter, str) and site_chapter.isdigit():
                if int(site_chapter) == target_number:
                    return meta

    for meta in manifest:
        if meta.chapter_id == chapter_id:
            return meta
    available = [m.chapter_id for m in manifest[:5]]
    raise ValueError(
        f"Chapter '{chapter_id}' not found in manifest. "
        f"First entries: {available}..."
    )


def run_fetch_stage(
    *,
    config: AppConfig,
    chapter_id: str,
    title: str,
    input_file: Path | None = None,
    text: str | None = None,
    adapter: FetchAdapter | None = None,
    chapter_meta: ChapterMeta | None = None,
) -> ChapterSource:
    source_path: Path | None = None
    source_url: str = ""

    if adapter is not None and chapter_meta is not None:
        # Web fetch path
        raw_text = adapter.fetch_chapter_text(chapter_meta)
        source_url = chapter_meta.url
        if not title:
            title = chapter_meta.title
    elif input_file is not None:
        # Existing file path (unchanged)
        raw_text = input_file.read_text(encoding="utf-8")
        source_path = input_file.resolve()
        source_url = ""
    elif text:
        # Existing paste path (unchanged)
        raw_text = text
        source_path = None
        source_url = ""
    else:
        raise ValueError("Provide adapter+chapter_meta, input_file, or text.")

    raw_text = normalize_whitespace(raw_text)
    title = _derive_title_from_body_if_generic(title, raw_text)
    chapter = ChapterSource(
        novel_id=config.novel_id,
        chapter_id=chapter_id,
        title=title,
        source_language=config.source_language,
        source_path=source_path,
        source_url=source_url,
        raw_text=raw_text,
    )
    target_dir = chapter_dir(config.workspace.raw, chapter_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(target_dir / "source.json", chapter)
    return chapter


__all__ = [
    "load_or_build_manifest",
    "resolve_chapter_meta",
    "run_fetch_stage",
]
