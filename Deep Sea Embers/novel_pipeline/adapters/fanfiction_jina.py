"""FanFiction.Net adapter using Jina's public Markdown reader."""
from __future__ import annotations

import re
from urllib.parse import urlsplit

from novel_pipeline.adapters.base import FetchAdapter
from novel_pipeline.text_utils import validate_text_script
from novel_pipeline.types import ChapterMeta


_MARKDOWN_MARKER = "Markdown Content:"
_NOT_FOUND_MARKER = "FanFiction.Net Message Type 1"


def _strip_markdown_emphasis(value: str) -> str:
    text = value.strip()
    while len(text) >= 4 and (
        (text.startswith("**") and text.endswith("**"))
        or (text.startswith("__") and text.endswith("__"))
    ):
        text = text[2:-2].strip()
    return text


class FanfictionJinaAdapter(FetchAdapter):
    """Fetch a known FanFiction.Net story range through r.jina.ai."""

    def __init__(self, source_config) -> None:
        super().__init__(source_config)
        self._payload_cache: dict[str, bytes] = {}

    def _story_parts(self) -> tuple[str, str, int]:
        path_parts = [part for part in urlsplit(self.config.toc_url).path.split("/") if part]
        try:
            story_index = path_parts.index("s")
            story_id = path_parts[story_index + 1]
            slug = path_parts[story_index + 3]
        except (ValueError, IndexError) as exc:
            raise ValueError(
                "FanfictionJinaAdapter requires a FanFiction.Net chapter URL"
            ) from exc
        if not story_id.isdigit() or not slug:
            raise ValueError("FanfictionJinaAdapter found an invalid story id or slug")
        max_chapter = int(self.config.extra.get("max_chapter", 0))
        if max_chapter < 1:
            raise ValueError("FanfictionJinaAdapter requires source.max_chapter >= 1")
        return story_id, slug, max_chapter

    @staticmethod
    def _jina_url(story_id: str, chapter: int, slug: str) -> str:
        source_url = f"http://www.fanfiction.net/s/{story_id}/{chapter}/{slug}"
        return f"https://r.jina.ai/{source_url}"

    @staticmethod
    def _decode(payload: bytes, encoding: str = "") -> str:
        return payload.decode(encoding or "utf-8", errors="strict")

    @classmethod
    def _markdown_body(cls, payload: bytes, encoding: str = "") -> str:
        text = cls._decode(payload, encoding)
        if _NOT_FOUND_MARKER in text or "Chapter not found." in text:
            raise ValueError("FanFiction.Net chapter does not exist")
        if _MARKDOWN_MARKER not in text:
            raise ValueError("Jina response is missing the Markdown Content marker")
        return text.split(_MARKDOWN_MARKER, 1)[1].strip()

    @classmethod
    def _chapter_title(cls, payload: bytes, chapter: int, encoding: str = "") -> str:
        body = cls._markdown_body(payload, encoding)
        for line in body.splitlines():
            candidate = _strip_markdown_emphasis(line)
            if candidate:
                match = re.match(rf"Chapter\s+{chapter}\s*:\s*(.+)", candidate, re.IGNORECASE)
                if match:
                    return f"Chapter {chapter}: {match.group(1).strip()}"
                break
        return f"Chapter {chapter}"

    def build_manifest(self) -> list[ChapterMeta]:
        if not self.config.toc_url:
            raise ValueError("FanfictionJinaAdapter requires config.toc_url")
        story_id, slug, max_chapter = self._story_parts()
        manifest: list[ChapterMeta] = []
        for chapter in range(1, max_chapter + 1):
            url = self._jina_url(story_id, chapter, slug)
            payload = self.fetch_url(url)
            self._payload_cache[url] = payload
            title = self._chapter_title(payload, chapter, self.config.encoding)
            chapter_id = f"ch{chapter:03d}" if chapter <= 999 else f"ch{chapter:04d}"
            manifest.append(
                ChapterMeta(
                    index=chapter,
                    chapter_id=chapter_id,
                    title=title,
                    url=url,
                    source_id=str(chapter),
                    metadata={
                        "site_chapter": chapter,
                        "story_id": story_id,
                        "source_site": "fanfiction.net-via-jina",
                    },
                )
            )
        return manifest

    def fetch_chapter_text(self, meta: ChapterMeta) -> str:
        payload = self._payload_cache.pop(meta.url, None)
        if payload is None:
            payload = self.fetch_url(meta.url)
        return self.extract_content(payload, encoding=self.config.encoding)

    def extract_content(self, payload: bytes, *, encoding: str = "") -> str:
        body = self._markdown_body(payload, encoding or self.config.encoding)
        lines = body.splitlines()
        first_content = next((index for index, line in enumerate(lines) if line.strip()), None)
        if first_content is not None:
            title = _strip_markdown_emphasis(lines[first_content])
            if re.match(r"Chapter\s+\d+\s*:", title, re.IGNORECASE):
                del lines[first_content]
        content = "\n".join(lines).strip()
        if not content:
            raise ValueError("FanfictionJinaAdapter extracted empty chapter content")
        validate_text_script(content, "en")
        return content


__all__ = ["FanfictionJinaAdapter"]
