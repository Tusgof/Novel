"""ToonNovel adapter for the novel index and server-rendered chapter pages."""
from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from novel_pipeline.adapters.base import FetchAdapter
from novel_pipeline.text_utils import normalize_whitespace, validate_text_script
from novel_pipeline.types import ChapterMeta


_CHAPTER_HREF_RE = re.compile(r"/novel/(?P<slug>[^/]+)/chapter/(?P<chapter>\d+)/?$")
_TITLE_RE = re.compile(r"^Chapter\s+(?P<number>\d+)\s*[:.\-\u2013\u2014]\s*(?P<title>\S.*)$")


def _chapter_id(number: int) -> str:
    return f"ch{number:03d}" if number <= 999 else f"ch{number:04d}"


def normalize_title(text: str, number: int) -> str:
    """Render a site heading as 'Chapter N - Title', keeping a bare number generic."""
    match = _TITLE_RE.match(normalize_whitespace(text))
    if match and match.group("title").strip():
        return f"Chapter {number} - {match.group('title').strip()}"
    return normalize_whitespace(text) or f"Chapter {number}"


class _CatalogParser(HTMLParser):
    # The server-rendered chapter list lives inside <noscript>, so only markup
    # that can never hold anchors is skipped here.
    _SKIP_TAGS = {"script", "style"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.entries: list[tuple[str, str]] = []
        self._href: str | None = None
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._skip_depth:
            if tag in self._SKIP_TAGS:
                self._skip_depth += 1
            return
        if tag in self._SKIP_TAGS:
            self._skip_depth = 1
            return
        if tag != "a":
            return
        values = {key: value or "" for key, value in attrs}
        href = values.get("href", "")
        if _CHAPTER_HREF_RE.search(urlsplit(href).path):
            self._href = href
            self._parts = []

    def handle_endtag(self, tag: str) -> None:
        if self._skip_depth:
            if tag in self._SKIP_TAGS:
                self._skip_depth -= 1
            return
        if tag != "a" or self._href is None:
            return
        self.entries.append((self._href, normalize_whitespace("".join(self._parts))))
        self._href = None
        self._parts = []

    def handle_data(self, data: str) -> None:
        if self._href is not None and not self._skip_depth:
            self._parts.append(data)


class _ContentParser(HTMLParser):
    """Collect <p> text inside the chapter body only.

    Every paragraph carries a comments button; skipping buttons, svg icons and
    scripts keeps that UI out of the source text.
    """

    _SKIP_TAGS = {"button", "svg", "script", "style", "noscript", "iframe"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paragraphs: list[str] = []
        self._content_depth = 0
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if self._skip_depth:
            if tag in self._SKIP_TAGS:
                self._skip_depth += 1
            return
        if tag in self._SKIP_TAGS:
            self._skip_depth = 1
            return
        if tag == "div" and values.get("id") == "content":
            self._content_depth = 1
            return
        if not self._content_depth:
            return
        if tag == "div":
            self._content_depth += 1
        elif tag == "p":
            self._flush()
        elif tag == "br":
            self._parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if self._skip_depth:
            if tag in self._SKIP_TAGS:
                self._skip_depth -= 1
            return
        if not self._content_depth:
            return
        if tag == "p":
            self._flush()
        elif tag == "div":
            self._content_depth -= 1
            if not self._content_depth:
                self._flush()

    def handle_data(self, data: str) -> None:
        if self._content_depth and not self._skip_depth:
            self._parts.append(data)

    def _flush(self) -> None:
        text = normalize_whitespace("".join(self._parts).replace("\u200b", ""))
        self._parts = []
        if text:
            self.paragraphs.append(text)


class ToonnovelAdapter(FetchAdapter):
    """Fetch ToonNovel chapter listings and chapter bodies."""

    def _base_url(self) -> str:
        if self.config.base_url:
            return self.config.base_url.rstrip("/")
        parts = urlsplit(self.config.toc_url)
        return f"{parts.scheme}://{parts.netloc}"

    def _series_slug(self) -> str:
        segments = [part for part in urlsplit(self.config.toc_url).path.split("/") if part]
        if len(segments) >= 2 and segments[0] == "novel":
            return segments[1]
        return ""

    def build_manifest(self) -> list[ChapterMeta]:
        if not self.config.toc_url:
            raise ValueError("ToonnovelAdapter requires source.toc_url")
        encoding = self.config.encoding or "utf-8"
        parser = _CatalogParser()
        parser.feed(self.fetch_url(self.config.toc_url).decode(encoding, errors="strict"))

        slug = self._series_slug()
        entries: dict[int, tuple[str, str]] = {}
        for href, text in parser.entries:
            match = _CHAPTER_HREF_RE.search(urlsplit(href).path)
            if not match:
                continue
            if slug and match.group("slug") != slug:
                continue
            entries.setdefault(int(match.group("chapter")), (href, text))
        if not entries:
            raise ValueError("ToonnovelAdapter found no chapter links in the catalog")

        base_url = self._base_url()
        manifest: list[ChapterMeta] = []
        for index, number in enumerate(sorted(entries), start=1):
            href, text = entries[number]
            manifest.append(ChapterMeta(
                index=index,
                chapter_id=_chapter_id(number),
                title=normalize_title(text, number),
                url=urljoin(base_url + "/", href),
                source_id=str(number),
                metadata={
                    "site_chapter": number,
                    "source_site": "toonnovel",
                    "language": "en",
                },
            ))
        validate_text_script("\n".join(item.title for item in manifest), "en")
        return manifest

    def extract_content(self, html_bytes: bytes, *, encoding: str = "") -> str:
        parser = _ContentParser()
        parser.feed(html_bytes.decode(encoding or self.config.encoding or "utf-8", errors="strict"))
        content = "\n".join(parser.paragraphs).strip()
        if not content:
            raise ValueError("ToonnovelAdapter found no chapter body in the page")
        if len(content) < 500:
            raise ValueError("ToonnovelAdapter extracted too little chapter content")
        validate_text_script(content, "en")
        return content


__all__ = ["ToonnovelAdapter", "normalize_title"]
