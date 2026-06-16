"""Roliascan fetch adapter for text novel chapters."""
from __future__ import annotations

import hashlib
import html
import json
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlencode
import urllib.request

from novel_pipeline.adapters.base import FetchAdapter
from novel_pipeline.text_utils import validate_text_script
from novel_pipeline.types import ChapterMeta


class _ReaderTextParser(HTMLParser):
    """Extract paragraphs from Roliascan's `.reader-text` container."""

    _SKIP_TAGS = {"script", "style", "iframe", "ins"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paragraphs: list[str] = []
        self._in_reader = False
        self._reader_depth = 0
        self._in_paragraph = False
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = {key: value or "" for key, value in attrs}
        class_tokens = set(attr_dict.get("class", "").split())
        if not self._in_reader and tag == "div" and "reader-text" in class_tokens:
            self._in_reader = True
            self._reader_depth = 1
            return
        if not self._in_reader:
            return
        if tag == "div":
            self._reader_depth += 1
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag == "p":
            self._flush()
            self._in_paragraph = True
        elif tag == "br":
            self._flush()
        elif tag in {"i", "em"}:
            self._parts.append("*")

    def handle_endtag(self, tag: str) -> None:
        if not self._in_reader:
            return
        if self._skip_depth:
            if tag in self._SKIP_TAGS:
                self._skip_depth -= 1
            return
        if tag in {"i", "em"}:
            self._parts.append("*")
        elif tag == "p":
            self._flush()
            self._in_paragraph = False
        elif tag == "div":
            self._reader_depth -= 1
            if self._reader_depth <= 0:
                self._flush()
                self._in_reader = False

    def handle_data(self, data: str) -> None:
        if self._in_reader and not self._skip_depth:
            cleaned = data.strip()
            if cleaned:
                if self._parts and not self._parts[-1].endswith((" ", "\n", "*")):
                    self._parts.append(" ")
                self._parts.append(cleaned)

    def _flush(self) -> None:
        if not self._parts:
            return
        text = " ".join("".join(self._parts).split()).strip()
        text = re.sub(r"\*\s+", "*", text)
        text = re.sub(r"\s+\*", "*", text)
        if text:
            self.paragraphs.append(text)
        self._parts = []

    def finalize(self) -> str:
        self._flush()
        return "\n".join(self.paragraphs)


class RoliascanAdapter(FetchAdapter):
    """Adapter for Roliascan text novel pages."""

    _CHAPTERS_ENDPOINT = "https://roliascan.com/auth/manga-chapters"

    def _fetch_json(self, url: str) -> dict[str, object]:
        time.sleep(self._delay)
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "NovelPipeline/0.1",
                "Referer": self.config.toc_url,
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _chapter_token_params(self) -> dict[str, str]:
        timestamp = int(time.time())
        hour = datetime.now(timezone.utc).strftime("%Y%m%d%H")
        token = hashlib.md5(f"{timestamp}mng_ch_{hour}".encode("utf-8")).hexdigest()[:16]
        return {"_t": token, "_ts": str(timestamp)}

    def _manga_id(self) -> str:
        configured = self.config.extra.get("manga_id")
        if configured:
            return str(configured)
        raw = self.fetch_url(self.config.toc_url)
        text = raw.decode(self.config.encoding or "utf-8", errors="replace")
        match = re.search(r'data-manga-id=["\'](\d+)["\']', text)
        if not match:
            raise ValueError("RoliascanAdapter could not find data-manga-id on TOC page")
        return match.group(1)

    def build_manifest(self) -> list[ChapterMeta]:
        if not self.config.toc_url:
            raise ValueError("RoliascanAdapter requires config.toc_url")
        manga_id = self._manga_id()
        chapters: list[dict[str, object]] = []
        offset = 0
        while True:
            params = {
                "manga_id": manga_id,
                "offset": str(offset),
                "limit": "500",
                "order": "ASC",
                **self._chapter_token_params(),
            }
            data = self._fetch_json(f"{self._CHAPTERS_ENDPOINT}?{urlencode(params)}")
            if not data.get("success"):
                raise ValueError("RoliascanAdapter chapter endpoint returned success=false")
            batch = data.get("chapters")
            if not isinstance(batch, list):
                raise ValueError("RoliascanAdapter chapter endpoint returned invalid chapters payload")
            chapters.extend(item for item in batch if isinstance(item, dict))
            if not data.get("has_more") or not batch:
                break
            offset += len(batch)

        manifest: list[ChapterMeta] = []
        seen_chapters: set[str] = set()
        for item in chapters:
            chapter_number = str(item.get("chapter", "")).strip()
            if not chapter_number or chapter_number in seen_chapters:
                continue
            seen_chapters.add(chapter_number)
            index = len(manifest) + 1
            url = str(item.get("url", "")).replace("\\/", "/")
            title = html.unescape(str(item.get("title", "")).strip())
            chapter_id = f"ch{index:03d}" if index <= 999 else f"ch{index:04d}"
            manifest.append(
                ChapterMeta(
                    index=index,
                    chapter_id=chapter_id,
                    title=f"Chapter {chapter_number} - {title}" if title else f"Chapter {chapter_number}",
                    url=url,
                    source_id=str(item.get("id", "")).strip(),
                    metadata={
                        "site_chapter": chapter_number,
                        "language": str(item.get("language", "")).strip(),
                    },
                )
            )
        if not manifest:
            raise ValueError("RoliascanAdapter found no chapters")
        return manifest

    def extract_content(self, html_bytes: bytes, *, encoding: str = "") -> str:
        text = html_bytes.decode(encoding or self.config.encoding or "utf-8", errors="replace")
        parser = _ReaderTextParser()
        parser.feed(text)
        content = html.unescape(parser.finalize())
        if not content:
            raise ValueError("RoliascanAdapter could not extract chapter content")
        validate_text_script(content, "en")
        return content


__all__ = ["RoliascanAdapter"]
