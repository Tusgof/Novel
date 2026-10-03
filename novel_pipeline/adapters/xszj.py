"""XSZJ (小说之家) adapter for Chinese novel chapter pages."""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from novel_pipeline.adapters.base import FetchAdapter
from novel_pipeline.text_utils import normalize_whitespace, validate_text_script
from novel_pipeline.types import ChapterMeta


_CHAPTER_RE = re.compile(r"/b/(?P<book>[^/]+)/c/(?P<chapter>\d+)$")
_NUMBER_RE = re.compile(r"第\s*(\d+)\s*章")


class _CatalogParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.entries: list[tuple[str, str]] = []
        self.next_pages: list[str] = []
        self._anchor: tuple[str, str] | None = None
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        values = {key: value or "" for key, value in attrs}
        href = values.get("href", "")
        title = values.get("title", "")
        if "/c/" in href and "rel" in values and values["rel"] == "chapter":
            self._anchor = (href, title)
            self._parts = []
        elif "/cs/" in href and (
            "index-container-btn" in values.get("class", "") or "下一页" in title
        ):
            self.next_pages.append(href)
        elif values.get("rel") == "prev" and "page=" in href:
            self.next_pages.append(href)

    def handle_data(self, data: str) -> None:
        if self._anchor is not None:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._anchor is None:
            return
        href, title = self._anchor
        self.entries.append((href, normalize_whitespace(title or "".join(self._parts))))
        self._anchor = None
        self._parts = []


class _ContentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paragraphs: list[str] = []
        self._content_depth = 0
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if self._skip_depth:
            if tag in {"script", "style", "iframe", "noscript"}:
                self._skip_depth += 1
            return
        if tag in {"script", "style", "iframe", "noscript"}:
            self._skip_depth = 1
            return
        if tag == "div" and values.get("id") == "content":
            self._content_depth = 1
            return
        if self._content_depth and tag == "div":
            self._content_depth += 1
        elif self._content_depth and tag == "p":
            self._flush()

    def handle_endtag(self, tag: str) -> None:
        if self._skip_depth:
            if tag in {"script", "style", "iframe", "noscript"}:
                self._skip_depth -= 1
            return
        if not self._content_depth:
            return
        if tag == "p":
            self._flush()
        elif tag == "div":
            self._content_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._content_depth and not self._skip_depth:
            self._parts.append(data)

    def _flush(self) -> None:
        text = normalize_whitespace(html.unescape("".join(self._parts)))
        self._parts = []
        if text:
            self.paragraphs.append(text)


class XszjAdapter(FetchAdapter):
    """Fetch XSZJ catalog pages and multi-page chapter bodies."""

    def _catalog_pages(self) -> int:
        value = int(self.config.extra.get("max_catalog_pages", 20))
        if value < 1:
            raise ValueError("XszjAdapter max_catalog_pages must be >= 1")
        return value

    def build_manifest(self) -> list[ChapterMeta]:
        if not self.config.toc_url:
            raise ValueError("XszjAdapter requires source.toc_url")
        entries: dict[int, tuple[str, str]] = {}
        url = self.config.toc_url
        visited: set[str] = set()
        for _ in range(self._catalog_pages()):
            if url in visited:
                break
            visited.add(url)
            parser = _CatalogParser()
            parser.feed(self.fetch_url(url).decode(self.config.encoding or "utf-8", errors="strict"))
            for href, title in parser.entries:
                match = _CHAPTER_RE.search(urlsplit(href).path)
                number = _NUMBER_RE.search(title)
                if match and number:
                    entries.setdefault(int(number.group(1)), (href, title))
            next_url = next(
                (
                    candidate
                    for href in parser.next_pages
                    for candidate in (urljoin(url, href),)
                    if candidate not in visited
                ),
                None,
            )
            if not next_url:
                break
            url = next_url
        if not entries:
            raise ValueError("XszjAdapter found no chapter links in the catalog")
        validate_text_script("\n".join(title for _, title in entries.values()), "zh")
        base_url = self.config.base_url or f"{urlsplit(self.config.toc_url).scheme}://{urlsplit(self.config.toc_url).netloc}"
        manifest: list[ChapterMeta] = []
        for index, chapter_number in enumerate(sorted(entries), start=1):
            href, title = entries[chapter_number]
            manifest.append(ChapterMeta(
                index=index,
                chapter_id=f"ch{chapter_number:03d}",
                title=title,
                url=urljoin(base_url, href),
                source_id=str(chapter_number),
                metadata={"site_chapter": chapter_number, "source_site": "xszj", "book_id": urlsplit(self.config.toc_url).path.split("/")[2]},
            ))
        return manifest

    def extract_content(self, html_bytes: bytes, *, encoding: str = "") -> str:
        parser = _ContentParser()
        parser.feed(html_bytes.decode(encoding or self.config.encoding or "utf-8", errors="strict"))
        content = "\n\n".join(parser.paragraphs).strip()
        if not content:
            raise ValueError("XszjAdapter found empty chapter content")
        validate_text_script(content, "zh")
        return content

    def fetch_chapter_text(self, meta: ChapterMeta) -> str:
        pages: list[str] = []
        url = meta.url
        visited: set[str] = set()
        for _ in range(20):
            if url in visited:
                raise ValueError(f"XszjAdapter continuation loop at {url}")
            visited.add(url)
            raw = self.fetch_url(url)
            pages.append(self.extract_content(raw))
            text = raw.decode(self.config.encoding or "utf-8", errors="strict")
            parser = _CatalogParser()
            parser.feed(text)
            next_page = next((href for href in parser.next_pages if urljoin(url, href) not in visited), None)
            if not next_page:
                return "\n\n".join(pages).strip()
            url = urljoin(url, next_page)
        raise ValueError(f"XszjAdapter exceeded continuation limit for {meta.chapter_id}")


__all__ = ["XszjAdapter"]
