"""Novel543 fetch adapter for static Traditional Chinese chapter pages."""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from novel_pipeline.adapters.base import FetchAdapter
from novel_pipeline.text_utils import normalize_whitespace, validate_text_script
from novel_pipeline.types import ChapterMeta


_CHAPTER_HREF_RE = re.compile(
    r"/(?P<book>[^/]+)/(?P<series>\d+)_(?P<chapter>\d+)\.html$"
)
_PAGE_HREF_RE = re.compile(
    r"/(?P<book>[^/]+)/(?P<series>\d+)_(?P<chapter>\d+)"
    r"(?:_(?P<page>\d+))?\.html$"
)


def _decode_utf8(raw: bytes, *, encoding: str = "") -> str:
    selected = encoding.strip() or "utf-8-sig"
    try:
        text = raw.decode(selected, errors="strict")
    except (LookupError, UnicodeDecodeError) as exc:
        raise ValueError(f"Novel543Adapter could not decode response as {selected}") from exc
    if "\ufffd" in text:
        raise ValueError("Novel543Adapter decoded response contains replacement characters")
    return text


def _class_tokens(attrs: dict[str, str]) -> set[str]:
    return set(attrs.get("class", "").split())


class _ChapterLinkParser(HTMLParser):
    """Collect direct chapter links while ignoring continuation pages."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.entries: list[dict[str, str]] = []
        self._capture = False
        self._href = ""
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a" or self._capture:
            return
        values = {key: value or "" for key, value in attrs}
        href = values.get("href", "")
        if _CHAPTER_HREF_RE.search(urlsplit(href).path):
            self._capture = True
            self._href = href
            self._parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self._capture:
            return
        self.entries.append(
            {
                "href": self._href,
                "title": normalize_whitespace(html.unescape("".join(self._parts))),
            }
        )
        self._capture = False
        self._href = ""
        self._parts = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._parts.append(data)


class _LinkParser(HTMLParser):
    """Collect links used to discover a continuation page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        values = {key: value or "" for key, value in attrs}
        href = values.get("href", "")
        if href:
            self.hrefs.append(href)


class _ContentParser(HTMLParser):
    """Extract paragraphs from Novel543's chapter-content/content containers."""

    _SKIP_TAGS = {"iframe", "ins", "noscript", "script", "style", "svg"}
    _STOP_PREFIXES = ("\u6eab\u99a8\u63d0\u793a:", "\u6e29\u99a8\u63d0\u793a:")

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paragraphs: list[str] = []
        self.heading = ""
        self._heading_parts: list[str] = []
        self._in_heading = False
        self._content_depth = 0
        self._skip_stack: list[str] = []
        self._in_paragraph = False
        self._parts: list[str] = []
        self._stopped = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._stopped:
            return
        values = {key: value or "" for key, value in attrs}

        if self._skip_stack:
            self._skip_stack.append(tag)
            return

        if tag in self._SKIP_TAGS or (
            tag == "div"
            and ("gadBlock" in _class_tokens(values) or values.get("data-ad"))
        ):
            self._skip_stack = [tag]
            return

        if tag == "h1" and self._content_depth == 0:
            self._in_heading = True
            self._heading_parts = []
            return

        if tag == "div" and self._content_depth == 0 and "content" in _class_tokens(values):
            self._content_depth = 1
            return

        if self._content_depth == 0:
            return
        if tag == "div":
            self._content_depth += 1
        elif tag == "p":
            self._flush()
            self._in_paragraph = True
        elif tag == "br" and self._in_paragraph:
            self._flush()

    def handle_endtag(self, tag: str) -> None:
        if self._skip_stack:
            if tag == self._skip_stack[-1]:
                self._skip_stack.pop()
            return

        if tag == "h1" and self._in_heading:
            self.heading = normalize_whitespace("".join(self._heading_parts))
            self._in_heading = False
            return

        if self._content_depth == 0:
            return
        if tag == "p":
            self._flush()
            self._in_paragraph = False
        elif tag == "div":
            self._content_depth -= 1
            if self._content_depth == 0:
                self._stopped = True

    def handle_data(self, data: str) -> None:
        if self._stopped or self._skip_stack:
            return
        if self._in_heading:
            self._heading_parts.append(data)
        elif self._content_depth > 0 and self._in_paragraph:
            self._parts.append(data)

    def _flush(self) -> None:
        if not self._parts:
            return
        paragraph = normalize_whitespace(html.unescape("".join(self._parts)))
        self._parts = []
        if not paragraph:
            return
        if paragraph.startswith(self._STOP_PREFIXES):
            self._stopped = True
            return
        self.paragraphs.append(paragraph)

    def finalize(self) -> tuple[str, str]:
        self._flush()
        return self.heading, "\n".join(self.paragraphs)


def _chapter_page_info(url: str) -> tuple[str, str, int, int] | None:
    match = _PAGE_HREF_RE.search(urlsplit(url).path)
    if not match:
        return None
    page = int(match.group("page") or "1")
    return (
        match.group("book"),
        match.group("series"),
        int(match.group("chapter")),
        page,
    )


def _remove_page_title_prefix(content: str, heading: str) -> str:
    if not content or not heading:
        return content
    base_heading = re.sub(r"\s+\(\d+/\d+\)\s*$", "", heading).strip()
    first, separator, remainder = content.partition("\n")
    if first.startswith(base_heading):
        first = first[len(base_heading) :].lstrip()
        content = first + (separator + remainder if separator else "")
    return content.strip()


class Novel543Adapter(FetchAdapter):
    """Fetch Novel543 chapters and join the site's continuation pages."""

    def _max_pages(self) -> int:
        raw = self.config.extra.get("max_pages", 8)
        try:
            value = int(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("Novel543Adapter source.max_pages must be an integer") from exc
        if value < 1:
            raise ValueError("Novel543Adapter source.max_pages must be >= 1")
        return value

    def _min_content_chars(self) -> int:
        raw = self.config.extra.get("min_content_chars", 80)
        try:
            value = int(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Novel543Adapter source.min_content_chars must be an integer"
            ) from exc
        if value < 1:
            raise ValueError("Novel543Adapter source.min_content_chars must be >= 1")
        return value

    def _book_path(self) -> str:
        configured = str(self.config.extra.get("book_path", "")).strip().strip("/")
        if configured:
            return configured
        path = urlsplit(self.config.toc_url).path.rstrip("/")
        match = re.search(r"/([^/]+)/dir$", path)
        if not match:
            raise ValueError(
                "Novel543Adapter source.toc_url must end with /<book-path>/dir"
            )
        return match.group(1)

    def build_manifest(self) -> list[ChapterMeta]:
        if not self.config.toc_url:
            raise ValueError("Novel543Adapter requires config.toc_url")

        raw = self.fetch_url(self.config.toc_url)
        text = _decode_utf8(raw, encoding=self.config.encoding)

        parser = _ChapterLinkParser()
        parser.feed(text)
        validate_text_script("\n".join(entry["title"] for entry in parser.entries), "zh")
        book_path = self._book_path()
        configured_series = str(self.config.extra.get("series_id", "")).strip()
        entries: dict[int, dict[str, str]] = {}
        series_id = configured_series
        for entry in parser.entries:
            info = _chapter_page_info(urljoin(self.config.toc_url, entry["href"]))
            if info is None or info[0] != book_path:
                continue
            if series_id and info[1] != series_id:
                continue
            series_id = series_id or info[1]
            entries.setdefault(info[2], entry)

        if not entries:
            raise ValueError("Novel543Adapter found no chapter links in the TOC")

        base_url = self.config.base_url.strip() or (
            f"{urlsplit(self.config.toc_url).scheme}://{urlsplit(self.config.toc_url).netloc}"
        )
        manifest: list[ChapterMeta] = []
        for ordinal, chapter_number in enumerate(sorted(entries), start=1):
            entry = entries[chapter_number]
            url = urljoin(self.config.toc_url, entry["href"])
            manifest.append(
                ChapterMeta(
                    index=ordinal,
                    chapter_id=f"ch{chapter_number:03d}" if chapter_number <= 999 else f"ch{chapter_number:04d}",
                    title=entry["title"],
                    url=url,
                    source_id=f"{series_id}_{chapter_number}",
                    metadata={
                        "site_chapter": chapter_number,
                        "source_site": "novel543",
                        "book_path": book_path,
                        "series_id": series_id,
                        "base_url": base_url,
                    },
                )
            )
        return manifest

    def _next_page_url(self, raw: bytes, current_url: str) -> str | None:
        current = _chapter_page_info(current_url)
        if current is None:
            return None
        text = _decode_utf8(raw, encoding=self.config.encoding)
        parser = _LinkParser()
        parser.feed(text)
        candidates: list[tuple[int, str]] = []
        for href in parser.hrefs:
            absolute = urljoin(current_url, href)
            info = _chapter_page_info(absolute)
            if info is None or info[:3] != current[:3]:
                continue
            if info[3] > current[3]:
                candidates.append((info[3], absolute))
        if not candidates:
            return None
        return min(candidates)[1]

    def extract_content(self, html_bytes: bytes, *, encoding: str = "") -> str:
        text = _decode_utf8(html_bytes, encoding=encoding or self.config.encoding)
        parser = _ContentParser()
        parser.feed(text)
        heading, content = parser.finalize()
        content = _remove_page_title_prefix(content, heading)
        if len(content) < self._min_content_chars():
            raise ValueError(
                "Novel543Adapter extracted too little chapter content: "
                f"{len(content)} chars"
            )
        validate_text_script(content, "zh")
        return content

    def fetch_chapter_text(self, meta: ChapterMeta) -> str:
        pages: list[str] = []
        visited: set[str] = set()
        url = meta.url
        for _ in range(self._max_pages()):
            if url in visited:
                raise ValueError(f"Novel543Adapter continuation loop at {url}")
            visited.add(url)
            raw = self.fetch_url(url)
            pages.append(self.extract_content(raw))
            next_url = self._next_page_url(raw, url)
            if not next_url:
                return "\n\n".join(page for page in pages if page).strip()
            url = next_url
        raise ValueError(
            f"Novel543Adapter exceeded max_pages={self._max_pages()} for {meta.chapter_id}"
        )


__all__ = ["Novel543Adapter"]
