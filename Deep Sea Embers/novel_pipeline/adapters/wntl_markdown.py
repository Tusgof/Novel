"""WNTL public Markdown adapter for chapter manifests and raw text."""
from __future__ import annotations

import json
import re
import urllib.request

from novel_pipeline.adapters.base import FetchAdapter
from novel_pipeline.text_utils import validate_text_script
from novel_pipeline.types import ChapterMeta


class WntlMarkdownAdapter(FetchAdapter):
    """Fetch WNTL's published chapter metadata and Markdown bodies."""

    def _series_id(self) -> str:
        value = self.config.extra.get("series_id")
        if not value:
            raise ValueError("WntlMarkdownAdapter requires source.series_id")
        return str(value).strip()

    def _fetch_json(self, url: str) -> dict[str, object]:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "NovelPipeline/0.1", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("WNTL returned a non-object JSON payload")
        return payload

    def build_manifest(self) -> list[ChapterMeta]:
        series_id = self._series_id()
        api_root = str(self.config.extra.get("api_root", "https://wntl.net")).rstrip("/")
        payload = self._fetch_json(f"{api_root}/api/chapters/{series_id}")
        rows = payload.get("chapters")
        if not isinstance(rows, list):
            raise ValueError("WNTL chapter API returned no chapters list")

        manifest: list[ChapterMeta] = []
        seen: set[int] = set()
        for row in rows:
            if not isinstance(row, dict) or str(row.get("status", "published")) != "published":
                continue
            try:
                number = int(row["number"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"WNTL chapter row has invalid number: {row!r}") from exc
            if number < 1 or number in seen:
                continue
            seen.add(number)
            title = str(row.get("title") or f"Chapter {number}").strip()
            manifest.append(
                ChapterMeta(
                    index=len(manifest) + 1,
                    chapter_id=f"ch{number:03d}",
                    title=title,
                    url=f"{api_root}/content/{series_id}/{number}.md",
                    source_id=str(row.get("id", number)),
                    metadata={
                        "site_chapter": str(number),
                        "source_site": "wntl",
                        "series_id": series_id,
                    },
                )
            )
        manifest.sort(key=lambda item: int(item.metadata["site_chapter"]))
        for index, item in enumerate(manifest, start=1):
            item.index = index
        if not manifest:
            raise ValueError("WNTL returned no published chapters")
        return manifest

    def extract_content(self, html: bytes, *, encoding: str = "") -> str:
        text = html.decode(encoding or "utf-8", errors="replace")
        text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        if len(text) < 500:
            raise ValueError("WNTL returned too little chapter content")
        validate_text_script(text, "en")
        return text


__all__ = ["WntlMarkdownAdapter"]
