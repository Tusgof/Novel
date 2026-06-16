"""Piaotia.com fetch adapter — GBK-encoded novel site."""
from __future__ import annotations

import re
import html
import unicodedata
from html.parser import HTMLParser
from urllib.parse import urljoin

from novel_pipeline.adapters.base import FetchAdapter
from novel_pipeline.text_utils import validate_text_script
from novel_pipeline.types import ChapterMeta


class _TocParser(HTMLParser):
    """Parse TOC page to extract chapter links."""

    def __init__(self, *, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.entries: list[dict[str, str]] = []
        self._seen_ids: set[str] = set()
        self._capture = False
        self._current_text = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = ""
            for name, value in attrs:
                if name == "href":
                    href = value or ""
            if href:
                match = re.search(r"(\d+)\.html$", href)
                if match:
                    self._capture = True
                    self._current_text = ""
                    self._href = href
                    self._href_numeric = match.group(1)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._capture:
            self._capture = False
            title = self._current_text.strip()
            if title and hasattr(self, "_href") and hasattr(self, "_href_numeric"):
                if self._href_numeric not in self._seen_ids:
                    self._seen_ids.add(self._href_numeric)
                    self.entries.append({"href": self._href, "title": title, "source_id": self._href_numeric})

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._current_text += data


class _ContentParser(HTMLParser):
    """Parse chapter content page to extract text.

    Strategy (in priority order):
    1. If <div id="content"> exists, use it (legacy support).
    2. Otherwise, fall back to: start capture after </h1>,
       collect text nodes separated by <br>, skip nav/ad containers,
       and stop at the ad comment marker (e.g. "翻页上AD开始").
    """

    _SKIP_TAGS = {"table", "script", "style", "ins", "iframe"}
    _NAV_CLASSES = {"toplink", "bottomlink", "mode", "status"}
    _NAV_IDS = {"Commenddiv", "feit2", "guild", "shop"}
    _STOP_COMMENT_MARKERS = ("翻页上AD开始", "标题上AD开始", "翻页下AD开始")

    # Variant content container identifiers (id exact match, class token match)
    _CONTENT_CONTAINER_IDS = {"content", "chapter-content", "chaptercontent",
                              "read-content", "readcontent", "booktext", "novel-content"}
    _CONTENT_CONTAINER_CLASSES = {"content", "chapter-content", "chaptercontent",
                                  "read-content", "readcontent", "booktext", "novel-content"}

    def __init__(self) -> None:
        super().__init__()
        self.paragraphs: list[str] = []

        # Explicit content-container path
        self._in_content_div: bool = False
        self._div_depth: int = 0
        self._content_root_tag: str = ""

        # Fallback path (after </h1>)
        self._seen_h1: bool = False
        self._capture_fallback: bool = False

        # Shared
        self._skip_depth: int = 0
        self._generic_div_depth: int = 0
        self._div_stack: list[str] = []
        self._current_paragraph: list[str] = []
        self._stopped: bool = False

    def _is_content_container(self, attrs: dict[str, str]) -> bool:
        """Return True if id or class indicates a content container."""
        id_val = attrs.get("id", "")
        if id_val in self._CONTENT_CONTAINER_IDS:
            return True
        class_val = attrs.get("class", "")
        class_tokens = set(re.split(r"\s+", class_val.strip())) if class_val.strip() else set()
        if class_tokens & self._CONTENT_CONTAINER_CLASSES:
            return True
        return False

    # -- handle_starttag -----------------------------------------------------

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._stopped:
            return

        attr_dict = {k: (v or "") for k, v in attrs}

        # -- Priority 1: explicit content-container path ---------------------
        if (
            not self._in_content_div
            and tag in ("div", "article", "section")
            and self._is_content_container(attr_dict)
        ):
            self._in_content_div = True
            self._div_depth = 1
            self._content_root_tag = tag
            return

        if self._in_content_div:
            if self._skip_depth > 0:
                if tag in self._SKIP_TAGS:
                    self._skip_depth += 1
                return
            if tag in self._SKIP_TAGS:
                self._skip_depth += 1
                return
            if tag == "br":
                self._flush_paragraph()
                return
            if tag == "p":
                self._flush_paragraph()
            self._div_depth += 1
            return

        # -- Priority 2: fallback path (after </h1>) -------------------------
        if tag == "h1":
            self._seen_h1 = True
            return

        if not self._seen_h1:
            return  # Before h1, ignore

        if not self._capture_fallback:
            return  # Waiting for </h1>

        # We are in fallback capture zone
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
            return

        if tag == "div":
            cls = attr_dict.get("class", "")
            id_val = attr_dict.get("id", "")
            # Skip known nav/ad containers by id/class
            if id_val in self._NAV_IDS or \
               any(nc in cls for nc in self._NAV_CLASSES):
                self._skip_depth += 1
                self._div_stack.append("skip")
                return
            # Generic div: track depth but DON'T skip content inside it.
            self._generic_div_depth += 1
            self._div_stack.append("generic")
            return

        if tag == "br":
            self._flush_paragraph()
        elif tag == "p":
            self._flush_paragraph()

    # -- handle_endtag -------------------------------------------------------

    def handle_endtag(self, tag: str) -> None:
        if self._stopped:
            return

        # -- explicit content-container path --------------------------------
        if self._in_content_div:
            if self._skip_depth > 0 and tag in self._SKIP_TAGS:
                self._skip_depth -= 1
                return
            if self._skip_depth > 0:
                return
            if tag == "p":
                self._flush_paragraph()
            if tag == self._content_root_tag or self._div_depth > 1:
                self._div_depth -= 1
                if self._div_depth <= 0:
                    self._in_content_div = False
                    self._content_root_tag = ""
            return

        # -- Fallback path ---------------------------------------------------
        # Activate fallback after </h1>
        if tag == "h1" and self._seen_h1 and not self._capture_fallback:
            self._capture_fallback = True
            return

        if self._capture_fallback:
            if tag == "p":
                self._flush_paragraph()
            if tag in self._SKIP_TAGS:
                if self._skip_depth > 0:
                    self._skip_depth -= 1
            elif tag == "div":
                if self._div_stack:
                    kind = self._div_stack.pop()
                    if kind == "skip":
                        if self._skip_depth > 0:
                            self._skip_depth -= 1
                    elif kind == "generic":
                        if self._generic_div_depth > 0:
                            self._generic_div_depth -= 1

    # -- handle_data ---------------------------------------------------------

    def handle_data(self, data: str) -> None:
        if self._stopped:
            return
        if (self._in_content_div or self._capture_fallback) and self._contains_stop_marker(data):
            before_marker = self._text_before_stop_marker(data)
            if before_marker:
                self._accumulate(before_marker)
            self._flush_paragraph()
            self._stopped = True
            return

        if self._in_content_div and self._skip_depth == 0:
            self._accumulate(data)
        elif self._capture_fallback and self._skip_depth == 0:
            self._accumulate(data)

    # -- handle_comment (new) ------------------------------------------------

    def handle_comment(self, data: str) -> None:
        if self._stopped:
            return
        # Only check stop markers in fallback mode (after </h1>).
        # Stop-comment markers can appear in the <head> section before
        # </h1> is ever reached (e.g. 标题上AD开始 in Piaotia page head).
        if not self._capture_fallback and not self._in_content_div:
            return
        if self._contains_stop_marker(data):
            self._flush_paragraph()
            self._stopped = True
            return

    # -- helpers -------------------------------------------------------------

    def _accumulate(self, data: str) -> None:
        cleaned = data.strip()
        if cleaned:
            self._current_paragraph.append(cleaned)

    def _flush_paragraph(self) -> None:
        if self._current_paragraph:
            text = "".join(self._current_paragraph)
            # Strip leading &nbsp; sequences (full-width and half-width)
            text = re.sub(r"^[\u00a0\u3000]+", "", text)
            text = re.sub(r"^&(nbsp|NBSP|#160|#x[Aa]0);", "", text)
            text = text.strip()
            if text and not self._is_nav_paragraph(text):
                self.paragraphs.append(text)
            self._current_paragraph = []

    def _contains_stop_marker(self, text: str) -> bool:
        return any(marker in text for marker in self._STOP_COMMENT_MARKERS)

    def _text_before_stop_marker(self, text: str) -> str:
        first_index: int | None = None
        for marker in self._STOP_COMMENT_MARKERS:
            marker_index = text.find(marker)
            if marker_index != -1 and (first_index is None or marker_index < first_index):
                first_index = marker_index
        if first_index is None:
            return text
        return text[:first_index]

    def _is_nav_paragraph(self, text: str) -> bool:
        compact = re.sub(r"\s+", "", text)
        if not compact:
            return True
        nav_tokens = ("上一章", "下一章", "返回目录", "章节目录")
        if any(token in compact for token in nav_tokens):
            non_nav = compact
            for token in nav_tokens:
                non_nav = non_nav.replace(token, "")
            non_nav = re.sub(r"[|｜·,，。:：;；\[\]（）()《》<>-]+", "", non_nav)
            return not non_nav
        return False

    def finalize(self) -> str:
        self._flush_paragraph()
        return "\n".join(self.paragraphs)


class PiaotiaAdapter(FetchAdapter):
    """Adapter for piaotia.com novel chapters."""

    def _decode_gb(self, raw: bytes) -> str:
        """Decode GB‑encoded bytes with charset detection and scoring."""
        # Detect BOM
        if raw.startswith(b'\xef\xbb\xbf'):
            encoding = 'utf-8-sig'
            raw = raw[3:]
        elif raw.startswith(b'\xff\xfe'):
            encoding = 'utf-16-le'
            raw = raw[2:]
        elif raw.startswith(b'\xfe\xff'):
            encoding = 'utf-16-be'
            raw = raw[2:]
        else:
            encoding = None
        
        # Try to extract charset from meta tag
        if encoding is None:
            meta_charset = self._extract_charset_from_meta(raw)
            if meta_charset:
                encoding = meta_charset
        
        # Candidate encodings to try (order matters)
        candidates = []
        if encoding:
            candidates.append(encoding)
        # Treat gb2312/gbk/gb18030 as gb18030
        if encoding and encoding.lower() in ('gb2312', 'gbk', 'gb18030'):
            candidates.append('gb18030')
        candidates.extend(['gb18030', 'gbk', 'utf-8'])
        # Deduplicate while preserving order
        seen = set()
        unique_candidates = []
        for enc in candidates:
            if enc not in seen:
                seen.add(enc)
                unique_candidates.append(enc)
        
        best_score = -1
        best_text = None
        for enc in unique_candidates:
            try:
                text = raw.decode(enc, errors='strict')
            except UnicodeDecodeError:
                continue
            # Score decoded HTML
            score = self._score_decoded_html(text)
            if score > best_score:
                best_score = score
                best_text = text
        
        if best_text is None:
            raise ValueError(
                f"Could not decode raw bytes with any candidate encoding: {unique_candidates}. "
                "Raw hex starts with: " + raw[:100].hex()
            )
        
        # Do not return decode-replace output as valid source
        if '\ufffd' in best_text:
            raise ValueError(
                "Decoded text contains replacement characters (�), indicating invalid encoding."
            )
        
        return best_text

    def _extract_charset_from_meta(self, raw: bytes) -> str | None:
        """Extract charset from HTML meta tag, returns normalized encoding name."""
        # Look for <meta charset="..."> or <meta http-equiv="Content-Type" content="...">
        # Decode as ascii/latin-1 to avoid decoding errors.
        try:
            sample = raw[:5000].decode('ascii', errors='ignore')
        except UnicodeDecodeError:
            # If ascii fails, try latin-1 which never fails
            sample = raw[:5000].decode('latin-1', errors='ignore')
        
        # Pattern for <meta charset="...">
        import re
        match = re.search(r'<meta\s+charset=["\']?([^"\'\s>]+)', sample, re.IGNORECASE)
        if match:
            enc = match.group(1).strip().lower()
            if enc.startswith('gb'):
                return 'gb18030'
            if enc in ('utf-8', 'utf8'):
                return 'utf-8'
            return enc
        
        # Pattern for <meta http-equiv="Content-Type" content="...">
        match = re.search(
            r'<meta\s+http-equiv=["\']?Content-Type["\']?\s+content=["\'][^"\']*charset=([^"\'\s>]+)',
            sample, re.IGNORECASE
        )
        if match:
            enc = match.group(1).strip().lower()
            if enc.startswith('gb'):
                return 'gb18030'
            if enc in ('utf-8', 'utf8'):
                return 'utf-8'
            return enc
        
        return None

    def _score_decoded_html(self, text: str) -> int:
        """Score decoded HTML: higher is better.
        Prefer high Han ratio, zero replacement chars, low Thai count, low control/other chars."""
        # Strip HTML tags, scripts, styles, comments, and decode entities
        stripped = self._strip_html_tags(text)
        
        # Count characters by category
        han_count = 0
        thai_count = 0
        latin_count = 0
        digit_count = 0
        punctuation_count = 0
        whitespace_count = 0
        control_count = 0
        other_count = 0
        replacement_count = 0
        
        for char in stripped:
            if char == '\ufffd':  # replacement character
                replacement_count += 1
                continue
            cat = unicodedata.category(char)
            if cat[0] == 'C':
                control_count += 1
            elif cat[0] == 'Z':
                whitespace_count += 1
            elif cat[0] in ('P', 'S'):
                punctuation_count += 1
            elif cat[0] == 'N':
                digit_count += 1
            elif cat[0] == 'L':
                # Script detection
                if 0x4E00 <= ord(char) <= 0x9FFF:
                    han_count += 1
                elif 0x0E00 <= ord(char) <= 0x0E7F:
                    thai_count += 1
                else:
                    latin_count += 1
            else:
                other_count += 1
        
        total_chars = len(stripped)
        if total_chars == 0:
            return -1000
        
        # Penalties and rewards
        score = 0
        # Han ratio reward (0-100)
        han_ratio = han_count / total_chars
        score += int(han_ratio * 100)
        # Penalty for replacement chars (zero tolerance)
        score -= replacement_count * 1000
        # Penalty for Thai chars (unexpected in Chinese source)
        score -= thai_count * 50
        # Penalty for control/other chars
        score -= control_count * 10
        score -= other_count * 5
        # Slight reward for Latin/digits/punctuation (acceptable)
        score += latin_count * 1
        score += digit_count * 1
        score += punctuation_count * 0
        # Penalty for high whitespace ratio (maybe noise)
        whitespace_ratio = whitespace_count / total_chars
        if whitespace_ratio > 0.5:
            score -= int((whitespace_ratio - 0.5) * 100)
        
        return score

    def _strip_html_tags(self, text: str) -> str:
        """Strip HTML tags, scripts, styles, comments, and decode entities."""
        import re
        # Remove script and style tags with content
        text = re.sub(r'<script\b[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style\b[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Remove HTML comments
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        # Remove all other tags
        text = re.sub(r'<[^>]*>', '', text)
        # Decode HTML entities
        text = html.unescape(text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def build_manifest(self) -> list[ChapterMeta]:
        toc_url = self.config.toc_url
        if not toc_url:
            raise ValueError("PiaotiaAdapter requires config.toc_url")

        raw = self.fetch_url(toc_url)
        text = self._decode_gb(raw)
        # Validate that the TOC contains Chinese characters (should be true)
        validate_text_script(text, "zh")

        base_url = self.config.base_url or toc_url.rsplit("/", 1)[0] + "/"
        if not base_url.endswith("/"):
            base_url += "/"

        parser = _TocParser(base_url=base_url)
        parser.feed(text)

        manifest: list[ChapterMeta] = []
        for idx, entry in enumerate(parser.entries, start=1):
            href = entry["href"]
            numeric_id = entry["source_id"]
            chapter_url = urljoin(base_url, href)
            chapter_id = f"ch{idx:03d}" if idx <= 999 else f"ch{idx:04d}"

            manifest.append(
                ChapterMeta(
                    index=idx,
                    chapter_id=chapter_id,
                    title=entry["title"],
                    url=chapter_url,
                    source_id=numeric_id,
                )
            )
        return manifest

    def extract_content(self, html: bytes, *, encoding: str = "") -> str:
        # encoding parameter is ignored; we always treat as GB family.
        text = self._decode_gb(html)
        # Validate stripped preview of raw HTML to catch mojibake without being misled by tags
        stripped_preview = self._strip_html_tags(text)
        validate_text_script(stripped_preview, "zh")

        parser = _ContentParser()
        parser.feed(text)
        content = parser.finalize()
        if not content or not any(0x4E00 <= ord(ch) <= 0x9FFF for ch in content):
            raise ValueError("PiaotiaAdapter could not extract chapter content")
        validate_text_script(content, "zh")
        return content
