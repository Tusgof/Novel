"""Abstract base class for website fetch adapters."""
from __future__ import annotations

import time
import urllib.request
from abc import ABC, abstractmethod

from novel_pipeline.types import ChapterMeta, SourceConfig


class FetchAdapter(ABC):
    """Base class for all website fetch adapters.

    Subclasses must implement:
      - build_manifest()  -> parse TOC into ordered ChapterMeta list
      - extract_content() -> given raw HTML bytes, return clean text
    """

    def __init__(self, source_config: SourceConfig) -> None:
        self.config = source_config
        self._delay = source_config.delay_seconds

    # -- abstract interface --------------------------------------------------

    @abstractmethod
    def build_manifest(self) -> list[ChapterMeta]:
        """Fetch TOC page(s) and return an ordered list of ChapterMeta."""

    @abstractmethod
    def extract_content(self, html: bytes, *, encoding: str = "") -> str:
        """Extract and clean chapter text from raw HTML bytes.

        Args:
            html: Raw response body bytes.
            encoding: Encoding hint (may be empty for auto-detect).

        Returns:
            Cleaned chapter text with paragraphs separated by newlines.
        """

    # -- shared helpers ------------------------------------------------------

    def fetch_url(self, url: str) -> bytes:
        """Fetch a URL with politeness delay.  Returns raw bytes."""
        time.sleep(self._delay)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "NovelPipeline/0.1"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()

    def fetch_chapter_text(self, meta: ChapterMeta) -> str:
        """Fetch one chapter and extract its text.

        This is the main entry point called by run_fetch_stage().
        """
        raw = self.fetch_url(meta.url)
        encoding = self.config.encoding or ""
        return self.extract_content(raw, encoding=encoding)


__all__ = ["FetchAdapter"]
