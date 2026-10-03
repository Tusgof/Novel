"""Local raw-source fetch adapter.

Uses existing 03_Raw/<chapter>/source.json files as the fetch source for
bounded runs when the upstream site is unavailable.
"""
from __future__ import annotations

import json
from pathlib import Path

from novel_pipeline.adapters.base import FetchAdapter
from novel_pipeline.types import ChapterMeta


class LocalRawAdapter(FetchAdapter):
    """Read already-fetched chapter sources from the current novel vault."""

    def _raw_root(self) -> Path:
        configured = self.config.extra.get("raw_root")
        if configured:
            return Path(str(configured)).expanduser().resolve()
        return (Path.cwd() / "03_Raw").resolve()

    def build_manifest(self) -> list[ChapterMeta]:
        raw_root = self._raw_root()
        if not raw_root.exists():
            raise ValueError(f"local_raw adapter cannot find raw root: {raw_root}")
        manifest: list[ChapterMeta] = []
        for source_path in sorted(raw_root.glob("ch*/source.json")):
            chapter_id = source_path.parent.name
            numeric = chapter_id.removeprefix("ch")
            index = int(numeric) if numeric.isdigit() else len(manifest) + 1
            data = json.loads(source_path.read_text(encoding="utf-8-sig"))
            manifest.append(
                ChapterMeta(
                    index=index,
                    chapter_id=chapter_id,
                    title=str(data.get("title", "")),
                    url=str(source_path),
                    source_id=str(data.get("metadata", {}).get("site_chapter", numeric)),
                    metadata={
                        "source_path": str(source_path),
                        "source_site": "local_raw",
                    },
                )
            )
        if not manifest:
            raise ValueError(f"local_raw adapter found no source.json files under {raw_root}")
        return manifest

    def fetch_chapter_text(self, meta: ChapterMeta) -> str:
        source_path = Path(str(meta.metadata.get("source_path") or meta.url))
        data = json.loads(source_path.read_text(encoding="utf-8-sig"))
        raw_text = str(data.get("raw_text", "")).strip()
        if not raw_text:
            raise ValueError(f"local_raw adapter found empty raw_text in {source_path}")
        return raw_text

    def extract_content(self, html: bytes, *, encoding: str = "") -> str:
        raise NotImplementedError("local_raw reads source.json directly")


__all__ = ["LocalRawAdapter"]
