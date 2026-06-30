"""WeTried TLS fetch adapter for Next.js novel chapter pages."""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser

from novel_pipeline.adapters.base import FetchAdapter
from novel_pipeline.text_utils import validate_text_script
from novel_pipeline.types import ChapterMeta


_CHAPTER_RE = re.compile(r"/chapter-(\d+)(?:\D|$)")


def _chapter_id(number: int) -> str:
    return f"ch{number:03d}" if number <= 999 else f"ch{number:04d}"


def _decode_next_payload(text: str) -> str:
    replacements = {
        r"\u003c": "<",
        r"\u003e": ">",
        r"\u0026": "&",
        r"\u0022": '"',
        r"\u0027": "'",
        r"\u003d": "=",
        r"\u002F": "/",
        r"\"": '"',
        r"\n": "\n",
        r"\t": "\t",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return html.unescape(text)


def _next_payload_segments(text: str) -> list[str]:
    segments = re.findall(r"<script>self\.__next_f\.push\(\[1,\"(.*?)\"\]\)</script>", text, flags=re.DOTALL)
    if segments:
        return [_decode_next_payload(segment) for segment in segments]
    return [_decode_next_payload(text)]


class _ParagraphParser(HTMLParser):
    _SKIP_TAGS = {"script", "style", "svg", "path", "button", "nav"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paragraphs: list[str] = []
        self._parts: list[str] = []
        self._in_p = False
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag == "p":
            self._flush()
            self._in_p = True
        elif tag == "br" and self._in_p:
            self._flush()

    def handle_endtag(self, tag: str) -> None:
        if self._skip_depth:
            if tag in self._SKIP_TAGS:
                self._skip_depth -= 1
            return
        if tag == "p":
            self._flush()
            self._in_p = False

    def handle_data(self, data: str) -> None:
        if not self._in_p or self._skip_depth:
            return
        cleaned = " ".join(data.split())
        if cleaned:
            self._parts.append(cleaned)

    def _flush(self) -> None:
        if not self._parts:
            return
        text = " ".join(self._parts).strip()
        if text:
            self.paragraphs.append(text)
        self._parts = []

    def finalize(self) -> list[str]:
        self._flush()
        return self.paragraphs


class WetriedtlsAdapter(FetchAdapter):
    """Adapter for WeTried TLS chapter pages.

    WeTried renders a loading shell in the visible HTML and streams the chapter
    body inside escaped Next.js payload strings. The adapter intentionally
    extracts only paragraph text beginning at the real chapter marker.
    """

    def _series_root(self) -> str:
        toc_url = self.config.toc_url.rstrip("/")
        if _CHAPTER_RE.search(toc_url):
            return re.sub(r"/chapter-\d+$", "", toc_url)
        return toc_url

    def _max_chapter(self) -> int:
        raw = self.config.extra.get("max_chapter") or self.config.extra.get("max_chapters") or 394
        try:
            value = int(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("WetriedtlsAdapter source.max_chapter must be an integer") from exc
        if value < 1:
            raise ValueError("WetriedtlsAdapter source.max_chapter must be >= 1")
        return value

    def build_manifest(self) -> list[ChapterMeta]:
        root = self._series_root()
        max_chapter = self._max_chapter()
        manifest: list[ChapterMeta] = []
        for number in range(1, max_chapter + 1):
            manifest.append(
                ChapterMeta(
                    index=number,
                    chapter_id=_chapter_id(number),
                    title=f"Chapter {number}",
                    url=f"{root}/chapter-{number}",
                    source_id=str(number),
                    metadata={
                        "site_chapter": str(number),
                        "source_site": "wetriedtls",
                    },
                )
            )
        return manifest

    def extract_content(self, html_bytes: bytes, *, encoding: str = "") -> str:
        decoded = html_bytes.decode(encoding or self.config.encoding or "utf-8", errors="replace")
        parser = _ParagraphParser()
        for payload in _next_payload_segments(decoded):
            parser.feed(payload)
        paragraphs = parser.finalize()

        chapter_indexes = [
            index
            for index, value in enumerate(paragraphs)
            if re.fullmatch(r"Chapter\s+\d+", value.strip(), flags=re.IGNORECASE)
        ]
        if not chapter_indexes:
            raise ValueError("WetriedtlsAdapter could not find a chapter marker in the page payload")

        start = chapter_indexes[-1]
        body = paragraphs[start:]
        stop_markers = {
            "all rights deserved. website coded by heaning.",
            "https://dsc.gg/wetried",
            "wetried translations",
            "we tried translations",
        }
        cleaned: list[str] = []
        for paragraph in body:
            text = paragraph.strip()
            if not text:
                continue
            text = re.sub(r"\s*Join our discord at https?://\S+\s*", "", text, flags=re.IGNORECASE).strip()
            if not text:
                continue
            if text.lower() in stop_markers:
                continue
            cleaned.append(text)

        content = "\n".join(cleaned).strip()
        if len(content) < 500:
            raise ValueError("WetriedtlsAdapter extracted too little chapter content")
        validate_text_script(content, "en")
        return content


__all__ = ["WetriedtlsAdapter"]
