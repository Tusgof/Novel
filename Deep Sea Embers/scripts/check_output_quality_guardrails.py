from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
NOVEL_ROOT = REPO.parent
DSE = REPO
HGD = NOVEL_ROOT / "Horror Game Developers"
MOONREAD = Path(os.environ.get("MOONREAD_READER_ROOT", NOVEL_ROOT / "MoonRead"))
if not MOONREAD.exists():
    MOONREAD = DSE / "reader-web"
REGISTRY_PATH = NOVEL_ROOT / "00_Config" / "novel_registry.json"
REGISTRY = json.loads(REGISTRY_PATH.read_text(encoding="utf-8")) if REGISTRY_PATH.exists() else {"novels": []}
REGISTERED_NOVELS = list(REGISTRY.get("novels", []))
MAX_PARAGRAPH_CHARS = 900
MAX_HGD_PARAGRAPH_CHARS = 520
HGD_POLICY = next((novel for novel in REGISTERED_NOVELS if novel.get("slug") == "horror-game-developer"), {})
HGD_ENGLISH_TITLE_MARKERS = HGD_POLICY.get("title_policy", {}).get("forbidden_title_markers") or [
    "Horror Game Developer",
    "Chapter",
    "Prologue",
    "Jester",
    "Mission Complete",
    "Orientation Day",
    "The world has changed",
    "Developing Game",
    "The missing piece",
    "Scream",
    "Quest Completed",
    "Painting",
    "Velora Art Museum",
    "Live Stream",
    "The lunatic with the sunglasses",
    "The game that makes you scream",
    "Your account has been reinstated",
    "Return of the Jester",
    "Masquerade ball",
    "The perfect piece",
    "Crying",
    "Little girl",
    "Little Girl",
    "App Update",
    "Shepherd",
    "Evolution",
]
HGD_REQUIRED_SOURCE_BEATS = [
    {
        "chapter": "ch022",
        "source_marker": "Like that, four days passed.",
        "output_marker": "สี่วันก็ผ่านไป",
        "label": "four_day_time_skip",
    },
]
HGD_FORBIDDEN_ENGLISH_OUTPUT = [
    "Horror Developer System",
    "Developer Seth Thorne",
    "Jump Scare",
    "[Scenario]",
    "[Section Chief]",
    "(Section Chief)",
    "(Scenario)",
    "(Hidden Scenario)",
    "(Jester)",
    "(Crownfall Guild)",
    "(Twisted Man)",
    "(Anomaly)",
    "(anomaly)",
    "(Anomalies)",
    "(anomalies)",
    "(node)",
    "(Node)",
    "(Fragments)",
    "(fragments)",
    "(Order)",
    "(anchors)",
    "(Containment Department)",
    "A Twisted Game",
    "[A Twisted Game]",
    "Squad Leader",
    "Game Developer System",
    "ทวิสเต็ดแมน",
    "อโนมาลี",
    "ไคลน์",
    "โองการ",
    "บัญญัติ",
    "วาทยากร",
    "หัวหน้าหน่วย",
    "เจ้าสำนัก",
    "โซรัน",
    "กู",
    "ขกมของ",
    "ขกมและ",
    "ขกมมัลติ",
    "ขกมออก",
    "ขป็น",
    "ขขา",
    "ขรื่อง",
    "ขพื่อ",
    "ขวลา",
    "สุขาาพ",
    "*Click!*",
    "*Takakakakaka—*",
    "*Tak!*",
    "*To Tok—*",
    "[Seth's USB stick]",
]
HGD_FORBIDDEN_REGEX_OUTPUT = [
    (re.compile(r"(?<!เควสต์)คอนดักเตอร์"), "คอนดักเตอร์"),
]
HGD_SETH_PRONOUN_CHAPTERS = {
    "ch002",
    "ch004",
    "ch010",
    "ch026",
    "ch027",
    "ch028",
    "ch031",
    "ch033",
    "ch035",
}
HGD_DANGLING_ENDINGS = tuple(HGD_POLICY.get("quality", {}).get("dangling_endings") or (
    "แต่",
    "และ",
    "กับ",
    "ของ",
    "ที่",
    "ใน",
    "ก่อนจะ",
    "มือเธอ",
))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def compact_runaway_repeats(text: str, *, limit: int = 24) -> str:
    """Normalize runaway repeated non-whitespace characters for length comparisons."""
    return re.sub(r"(\S)\1{" + str(limit) + r",}", lambda match: match.group(1) * limit, text)


def normalize_chapter_id(value: str) -> str:
    value = value.strip()
    if not value:
        return value
    if value.startswith("ch"):
        return value
    if value.isdigit():
        return f"ch{int(value):03d}"
    return value


def parse_requested_chapters(argv: list[str]) -> set[str] | None:
    if "--chapters" not in argv:
        return None
    index = argv.index("--chapters")
    if index + 1 >= len(argv):
        return set()

    chapters: set[str] = set()
    for token in argv[index + 1].split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            start_raw, end_raw = token.split("-", 1)
            start = normalize_chapter_id(start_raw)
            end = normalize_chapter_id(end_raw)
            if start.startswith("ch") and end.startswith("ch") and start[2:].isdigit() and end[2:].isdigit():
                for number in range(int(start[2:]), int(end[2:]) + 1):
                    chapters.add(f"ch{number:03d}")
                continue
        chapters.add(normalize_chapter_id(token))
    return chapters


def in_scope(chapter: str, scoped_chapters: set[str] | None) -> bool:
    return scoped_chapters is None or chapter in scoped_chapters


def is_chapter_id(value: str) -> bool:
    return bool(re.fullmatch(r"ch\d+", value))


def requested_novel_slug(argv: list[str]) -> str | None:
    if "--novel" in argv:
        index = argv.index("--novel")
        if index + 1 < len(argv):
            return argv[index + 1].strip() or None

    for index, arg in enumerate(argv):
        if arg != "--config" or index + 1 >= len(argv):
            continue
        config_path = Path(argv[index + 1]).resolve()
        parts = {part.lower() for part in config_path.parts}
        if "horror game developers" in parts:
            return "horror-game-developer"
        if "deep sea embers" in parts:
            return "deep-sea-embers"
        if "infinite regressor stories" in parts:
            return "infinite-regressor-stories"
    return None


def novel_root(novel: dict) -> Path:
    return NOVEL_ROOT / str(novel.get("folder", ""))


def novel_raw_root(novel: dict) -> Path:
    return novel_root(novel) / str(novel.get("raw_dir", "03_Raw"))


def novel_output_root(novel: dict) -> Path:
    return novel_root(novel) / str(novel.get("output_dir", "05_Output"))


def novel_reader_manifest_path(novel: dict) -> Path:
    return MOONREAD / "content/generated/books" / str(novel.get("slug", "")) / "manifest.json"


def check_absent(path: Path, terms: list[str], issues: list[str]) -> None:
    if not path.exists():
        issues.append(f"missing file: {path}")
        return
    text = read(path)
    for term in terms:
        if term in text:
            issues.append(f"{path}: forbidden variant remains: {term}")


def check_absent_patterns(path: Path, patterns: list[tuple[re.Pattern[str], str]], issues: list[str]) -> None:
    if not path.exists():
        issues.append(f"missing file: {path}")
        return
    text = read(path)
    for pattern, label in patterns:
        if pattern.search(text):
            issues.append(f"{path}: forbidden variant remains: {label}")


def source_allows_question_placeholder(novel: dict, chapter: str) -> bool:
    source_path = novel_raw_root(novel) / chapter / "source.json"
    if not source_path.exists():
        return False
    try:
        payload = json.loads(read(source_path))
    except (OSError, json.JSONDecodeError):
        return False
    source_text = "\n".join(
        str(payload.get(key, ""))
        for key in ("title", "raw_title", "raw_text", "source_text", "text")
    )
    return "?????" in source_text


def check_unapproved_question_placeholders(
    path: Path,
    novel: dict,
    chapter: str,
    issues: list[str],
) -> None:
    """Reject generated placeholders unless the source intentionally contains them."""
    if not path.exists():
        issues.append(f"missing file: {path}")
        return
    text = read(path)
    if "?????" in text and not source_allows_question_placeholder(novel, chapter):
        issues.append(f"{path}: repeated question-mark placeholder remains but source has no matching placeholder")


def check_paragraph_density(
    root: Path,
    issues: list[str],
    *,
    max_chars: int = MAX_PARAGRAPH_CHARS,
    scoped_chapters: set[str] | None = None,
) -> None:
    if not root.exists():
        return
    for path in sorted(root.glob("ch*/ch*.md")):
        if not in_scope(path.parent.name, scoped_chapters):
            continue
        text = read(path)
        for index, paragraph in enumerate(text.split("\n\n"), start=1):
            stripped = paragraph.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if len(stripped) > max_chars:
                issues.append(f"{path}: paragraph {index} too dense ({len(stripped)} chars)")


def check_malformed_markdown_artifacts(
    root: Path,
    issues: list[str],
    *,
    scoped_chapters: set[str] | None = None,
) -> None:
    """Catch formatter marker residue that renders badly in MoonRead."""
    if not root.exists():
        return
    paths = sorted(root.glob("ch*/ch*.md"))
    if not paths:
        paths = sorted(root.glob("ch*.md"))
    for path in paths:
        chapter = path.parent.name if path.parent.name.startswith("ch") else path.stem
        if not in_scope(chapter, scoped_chapters):
            continue
        for line_number, line in enumerate(read(path).splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            if re.match(r"^\[[^\]\n]+\]\*\*$", stripped):
                issues.append(f"{path}:{line_number}: malformed markdown missing opening bold marker")
            elif stripped.endswith("***") and stripped != "***" and not stripped.startswith("***"):
                issues.append(f"{path}:{line_number}: malformed markdown has trailing extra emphasis markers")
            elif re.match(r"^::?\*", stripped):
                issues.append(f"{path}:{line_number}: malformed markdown has stray colon before emphasis")
            elif stripped in {"*", "* *"}:
                issues.append(f"{path}:{line_number}: malformed markdown empty emphasis marker")
            elif re.match(r"^\*\s+.+\s+\*$", stripped):
                issues.append(f"{path}:{line_number}: malformed markdown has spaced emphasis wrapper")
            elif re.match(r"^\).+\]\*\*$", stripped) or re.match(r"^\(.+\)\]\*\*$", stripped):
                issues.append(f"{path}:{line_number}: malformed markdown has broken UI bracket wrapper")


def check_translation_metadata_leakage(
    root: Path,
    issues: list[str],
    *,
    scoped_chapters: set[str] | None = None,
) -> None:
    """Reject leaked glossary/category labels that are not reader-facing prose."""
    if not root.exists():
        return
    paths = sorted(root.glob("ch*/ch*.md"))
    if not paths:
        paths = sorted(root.glob("ch*.md"))
    metadata_pattern = re.compile(r"\((?:character|entity|rank|system|term)\)")
    for path in paths:
        chapter = path.parent.name if path.parent.name.startswith("ch") else path.stem
        if not in_scope(chapter, scoped_chapters):
            continue
        for line_number, line in enumerate(read(path).splitlines(), start=1):
            if metadata_pattern.search(line):
                issues.append(f"{path}:{line_number}: leaked translation metadata label")


def check_registry_forbidden_output_patterns(
    issues: list[str],
    *,
    scoped_chapters: set[str] | None = None,
    requested_novel: str | None = None,
) -> None:
    for novel in REGISTERED_NOVELS:
        slug = str(novel.get("slug", ""))
        if requested_novel is not None and slug != requested_novel:
            continue

        pattern_specs = (novel.get("quality", {}) or {}).get("forbidden_output_patterns") or []
        compiled: list[tuple[re.Pattern[str], str]] = []
        for spec in pattern_specs:
            if not isinstance(spec, dict):
                continue
            pattern_text = str(spec.get("pattern", ""))
            if not pattern_text:
                continue
            label = str(spec.get("label") or pattern_text)
            compiled.append((re.compile(pattern_text), label))
        if not compiled:
            continue

        roots = [novel_output_root(novel)]
        reader_root = MOONREAD / "content/generated/books" / slug / "chapters"
        if reader_root.exists():
            roots.append(reader_root)

        for root in roots:
            if not root.exists():
                continue
            paths = sorted(root.glob("ch*/ch*.md"))
            if not paths:
                paths = sorted(root.glob("ch*.md"))
            for path in paths:
                chapter = path.parent.name if is_chapter_id(path.parent.name) else path.stem
                if not in_scope(chapter, scoped_chapters):
                    continue
                text = read(path)
                for pattern, label in compiled:
                    match = pattern.search(text)
                    if match:
                        issues.append(f"{path}: {slug} forbidden output pattern remains: {label} ({match.group(0)!r})")


def _parse_simple_frontmatter(path: Path) -> dict[str, str]:
    text = read(path).lstrip("\ufeff")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def _parse_inline_aliases(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw.startswith("[") or not raw.endswith("]"):
        return []
    return [part.strip().strip("'\"") for part in raw[1:-1].split(",") if part.strip()]


def _approved_hgd_glossary_terms(issues: list[str]) -> list[tuple[str, str, Path]]:
    terms: list[tuple[str, str, Path]] = []
    glossary_root = HGD / "01_Glossary"
    if not glossary_root.exists():
        return terms
    for path in sorted(glossary_root.glob("*.md")):
        meta = _parse_simple_frontmatter(path)
        if meta.get("status") != "approved":
            continue
        thai = meta.get("thai_term", "").strip()
        if not thai or "?" in thai:
            issues.append(f"{path}: approved glossary term has unusable thai_term")
            continue
        originals = [meta.get("original_term", "").strip(), *_parse_inline_aliases(meta.get("aliases", ""))]
        for original in originals:
            if original and original != thai and re.search(r"[A-Za-z]", original):
                terms.append((original, thai, path))
    terms.sort(key=lambda item: len(item[0]), reverse=True)
    return terms


def check_hgd_approved_glossary_leakage(
    root: Path,
    issues: list[str],
    *,
    scoped_chapters: set[str] | None = None,
) -> None:
    """Approved HGD glossary terms should not remain as English parentheticals/UI labels."""
    if not root.exists():
        return
    terms = _approved_hgd_glossary_terms(issues)
    paths = sorted(root.glob("ch*/ch*.md"))
    if not paths:
        paths = sorted(root.glob("ch*.md"))
    for path in paths:
        chapter = path.parent.name if path.parent.name.startswith("ch") else path.stem
        if not in_scope(chapter, scoped_chapters):
            continue
        text = read(path)
        for original, thai, source in terms:
            escaped = re.escape(original)
            patterns = [
                rf"\({escaped}\)",
                rf"\({escaped}\]",
                rf"\[{escaped}\]",
                rf"\*\*\[{escaped}\]\*\*",
            ]
            if any(re.search(pattern, text) for pattern in patterns):
                issues.append(
                    f"{path}: approved glossary English remains: {original} -> {thai} ({source.name})"
                )


def check_duplicate_title_paragraphs(
    root: Path,
    issues: list[str],
    *,
    scoped_chapters: set[str] | None = None,
) -> None:
    """Reject plain title paragraphs repeated immediately below the H1 heading."""
    if not root.exists():
        return
    paths = sorted(root.glob("ch*/ch*.md"))
    if not paths:
        paths = sorted(root.glob("ch*.md"))
    title_line_re = re.compile(r"^(ตอนที่|บทที่)\s+\d+")
    for path in paths:
        chapter = path.parent.name if path.parent.name.startswith("ch") else path.stem
        if not in_scope(chapter, scoped_chapters):
            continue
        lines = read(path).splitlines()
        if len(lines) >= 3 and lines[0].startswith("# ") and not lines[1].strip():
            candidate = lines[2].strip()
            if title_line_re.match(candidate):
                issues.append(f"{path}: duplicate plain title paragraph under H1: {candidate}")


def check_hgd_title_fallbacks(issues: list[str]) -> None:
    for output_dir in sorted((HGD / "05_Output").glob("ch*")):
        if not output_dir.is_dir():
            continue
        try:
            number = int(output_dir.name[2:])
        except ValueError:
            continue
        chapter = f"ch{number:03d}"
        path = HGD / "05_Output" / chapter / f"{chapter}.md"
        if not path.exists():
            continue
        heading = read(path).split("\n", 1)[0].strip()
        for marker in HGD_ENGLISH_TITLE_MARKERS:
            if marker in heading:
                issues.append(f"{path}: HGD heading still contains English fallback title marker: {marker}")

    manifest_path = MOONREAD / "content/generated/books/horror-game-developer/manifest.json"
    if not manifest_path.exists():
        return
    manifest = json.loads(read(manifest_path))
    novel_title = str(manifest.get("novel", {}).get("title", ""))
    if novel_title == "Horror Game Developer":
        issues.append(f"{manifest_path}: reader book title still uses English fallback: {novel_title}")
    for chapter in manifest.get("chapters", []):
        title = str(chapter.get("title", ""))
        for marker in HGD_ENGLISH_TITLE_MARKERS:
            if marker in title:
                issues.append(f"{manifest_path}: {chapter.get('id')}: reader title contains English fallback marker: {marker}")


def has_named_chinese_chapter_title(title: str) -> bool:
    match = re.search(r"第[零〇一二两三四五六七八九十百千\d]+章\s*(.+)$", title or "")
    return bool(match and re.search(r"[\u3400-\u9fff]", match.group(1).strip()))


def check_dse_generic_title_fallbacks(issues: list[str]) -> None:
    for source_path in sorted((DSE / "03_Raw").glob("ch*/source.json")):
        chapter = source_path.parent.name
        output_path = DSE / "05_Output" / chapter / f"{chapter}.md"
        if not output_path.exists():
            continue

        source_payload = json.loads(read(source_path))
        source_title = str(source_payload.get("title", "")).strip()
        if not has_named_chinese_chapter_title(source_title):
            continue

        heading = read(output_path).split("\n", 1)[0].strip()
        number = int(chapter[2:])
        if heading == f"# บทที่ {number}":
            issues.append(
                f"{output_path}: DSE heading uses generic fallback despite named source title: {source_title}"
            )

    manifest_path = MOONREAD / "content/generated/books/deep-sea-embers/manifest.json"
    if not manifest_path.exists():
        return
    manifest = json.loads(read(manifest_path))
    for chapter in manifest.get("chapters", []):
        chapter_id = str(chapter.get("id", ""))
        source_path = DSE / "03_Raw" / chapter_id / "source.json"
        if not source_path.exists():
            continue
        source_payload = json.loads(read(source_path))
        source_title = str(source_payload.get("title", "")).strip()
        if not has_named_chinese_chapter_title(source_title):
            continue
        try:
            number = int(chapter_id[2:])
        except ValueError:
            continue
        if str(chapter.get("title", "")) == f"บทที่ {number}":
            issues.append(
                f"{manifest_path}: {chapter_id}: reader title uses generic fallback despite named source title: {source_title}"
            )


def check_registry_title_policies(
    issues: list[str],
    *,
    scoped_chapters: set[str] | None = None,
    requested_novel: str | None = None,
) -> None:
    for novel in REGISTERED_NOVELS:
        slug = str(novel.get("slug", ""))
        if requested_novel is not None and slug != requested_novel:
            continue
        title_policy = novel.get("title_policy", {}) or {}
        reader = novel.get("reader", {}) or {}
        output_root = novel_output_root(novel)
        raw_root = novel_raw_root(novel)

        forbidden_markers = list(title_policy.get("forbidden_title_markers") or [])
        if forbidden_markers:
            for output_dir in sorted(output_root.glob("ch*")):
                if not output_dir.is_dir():
                    continue
                chapter = output_dir.name
                if not in_scope(chapter, scoped_chapters):
                    continue
                path = output_root / chapter / f"{chapter}.md"
                if not path.exists():
                    continue
                heading = read(path).split("\n", 1)[0].strip()
                for marker in forbidden_markers:
                    if marker in heading:
                        issues.append(f"{path}: {slug} heading contains forbidden title marker: {marker}")

        if title_policy.get("named_chinese_source_titles_require_sidecar"):
            for source_path in sorted(raw_root.glob("ch*/source.json")):
                chapter = source_path.parent.name
                if not in_scope(chapter, scoped_chapters):
                    continue
                output_path = output_root / chapter / f"{chapter}.md"
                if not output_path.exists():
                    continue

                source_payload = json.loads(read(source_path))
                source_title = str(source_payload.get("title", "")).strip()
                if not has_named_chinese_chapter_title(source_title):
                    continue

                heading = read(output_path).split("\n", 1)[0].strip()
                try:
                    number = int(chapter[2:])
                except ValueError:
                    continue
                if heading == f"# บทที่ {number}":
                    issues.append(
                        f"{output_path}: {slug} heading uses generic fallback despite named source title: {source_title}"
                    )

        manifest_path = novel_reader_manifest_path(novel)
        if not manifest_path.exists():
            continue
        manifest = json.loads(read(manifest_path))
        expected_reader_title = str(reader.get("title", "")).strip()
        if title_policy.get("english_source_titles_require_thai_output") and expected_reader_title:
            novel_title = str(manifest.get("novel", {}).get("title", "")).strip()
            if novel_title != expected_reader_title:
                issues.append(
                    f"{manifest_path}: reader book title should be {expected_reader_title!r}; got {novel_title!r}"
                )

        for chapter in manifest.get("chapters", []):
            chapter_id = str(chapter.get("id", ""))
            if not in_scope(chapter_id, scoped_chapters):
                continue
            title = str(chapter.get("title", ""))
            for marker in forbidden_markers:
                if marker in title:
                    issues.append(f"{manifest_path}: {chapter_id}: reader title contains forbidden marker: {marker}")

            if title_policy.get("named_chinese_source_titles_require_sidecar"):
                source_path = raw_root / chapter_id / "source.json"
                if not source_path.exists():
                    continue
                source_payload = json.loads(read(source_path))
                source_title = str(source_payload.get("title", "")).strip()
                if not has_named_chinese_chapter_title(source_title):
                    continue
                try:
                    number = int(chapter_id[2:])
                except ValueError:
                    continue
                if title == f"บทที่ {number}":
                    issues.append(
                        f"{manifest_path}: {chapter_id}: reader title uses generic fallback despite named source title: {source_title}"
                    )


def check_hgd_truncation_against_source(issues: list[str]) -> None:
    for source_path in sorted((HGD / "03_Raw").glob("ch*/source.json")):
        chapter = source_path.parent.name
        output_path = HGD / "05_Output" / chapter / f"{chapter}.md"
        if not output_path.exists():
            continue

        source_payload = json.loads(read(source_path))
        source_text = str(source_payload.get("raw_text", ""))
        output_text = read(output_path)
        output_body = "\n".join(output_text.split("\n")[1:]).strip()
        if len(source_text) < 3000:
            continue

        comparable_source = compact_runaway_repeats(source_text)
        comparable_output = compact_runaway_repeats(output_body)
        ratio = len(comparable_output) / max(1, len(comparable_source))
        if ratio < 0.45:
            issues.append(
                f"{output_path}: output appears truncated versus source "
                f"(source chars={len(comparable_source)}, output chars={len(comparable_output)}, ratio={ratio:.2f})"
            )

        tail = output_body.rstrip()
        if any(tail.endswith(ending) for ending in HGD_DANGLING_ENDINGS):
            issues.append(f"{output_path}: output appears to end mid-sentence: {tail[-80:]}")


def check_registry_truncation_against_source(
    issues: list[str],
    scoped_chapters: set[str] | None = None,
    requested_novel: str | None = None,
) -> None:
    for novel in REGISTERED_NOVELS:
        slug = str(novel.get("slug", ""))
        if requested_novel is not None and slug != requested_novel:
            continue
        quality = novel.get("quality", {}) or {}
        min_source_chars = int(quality.get("truncation_min_source_chars") or 0)
        min_ratio = float(quality.get("truncation_min_ratio") or 0)
        if min_source_chars <= 0 or min_ratio <= 0:
            continue

        raw_root = novel_raw_root(novel)
        output_root = novel_output_root(novel)
        dangling_endings = tuple(quality.get("dangling_endings") or ())
        for source_path in sorted(raw_root.glob("ch*/source.json")):
            chapter = source_path.parent.name
            if not in_scope(chapter, scoped_chapters):
                continue
            output_path = output_root / chapter / f"{chapter}.md"
            if not output_path.exists():
                continue

            source_payload = json.loads(read(source_path))
            source_text = str(source_payload.get("raw_text", ""))
            output_text = read(output_path)
            output_body = "\n".join(output_text.split("\n")[1:]).strip()
            if len(source_text) < min_source_chars:
                continue

            comparable_source = compact_runaway_repeats(source_text)
            comparable_output = compact_runaway_repeats(output_body)
            ratio = len(comparable_output) / max(1, len(comparable_source))
            if ratio < min_ratio:
                issues.append(
                    f"{output_path}: {slug} output appears truncated versus source "
                    f"(source chars={len(comparable_source)}, output chars={len(comparable_output)}, ratio={ratio:.2f})"
                )

            tail = output_body.rstrip()
            if dangling_endings and any(tail.endswith(ending) for ending in dangling_endings):
                issues.append(f"{output_path}: {slug} output appears to end mid-sentence: {tail[-80:]}")


def check_hgd_required_source_beats(
    issues: list[str],
    scoped_chapters: set[str] | None = None,
) -> None:
    for rule in HGD_REQUIRED_SOURCE_BEATS:
        chapter = rule["chapter"]
        if not in_scope(chapter, scoped_chapters):
            continue
        source_path = HGD / "03_Raw" / chapter / "source.json"
        output_path = HGD / "05_Output" / chapter / f"{chapter}.md"
        if not source_path.exists() or not output_path.exists():
            continue

        source_payload = json.loads(read(source_path))
        source_text = str(source_payload.get("raw_text", ""))
        output_text = read(output_path)
        if rule["source_marker"] in source_text and rule["output_marker"] not in output_text:
            issues.append(
                f"{output_path}: HGD required source beat missing: {rule['label']} "
                f"(source marker: {rule['source_marker']})"
            )


def check_hgd_pronoun_policy(
    issues: list[str],
    scoped_chapters: set[str] | None = None,
) -> None:
    for chapter in sorted(HGD_SETH_PRONOUN_CHAPTERS):
        if not in_scope(chapter, scoped_chapters):
            continue
        path = HGD / "05_Output" / chapter / f"{chapter}.md"
        if not path.exists():
            continue
        text = read(path)
        if "ฉัน" in text:
            issues.append(f"{path}: Seth-dominant HGD chapter still contains first-person drift marker: ฉัน")

    ch033_path = HGD / "05_Output/ch033/ch033.md"
    if in_scope("ch033", scoped_chapters) and ch033_path.exists():
        text = read(ch033_path)
        for phrase in ["เธอเห็นอะไร", "เธอไม่ผิดหรอก", "ฉันว่าเธอพูดถูก", "ผมว่าเธอพูดถูก"]:
            if phrase in text:
                issues.append(f"{ch033_path}: Kyle/Seth peer-address drift remains: {phrase}")


def main() -> int:
    issues: list[str] = []
    scoped_chapters = parse_requested_chapters(sys.argv)
    requested_novel = requested_novel_slug(sys.argv)
    include_dse = requested_novel in (None, "deep-sea-embers")
    include_hgd = requested_novel in (None, "horror-game-developer")

    if include_dse and in_scope("ch001", scoped_chapters):
        check_absent(DSE / "05_Output/ch001/ch001.md", ["ตั้งเครื่องหมายคำถาม"], issues)
    if include_dse and in_scope("ch014", scoped_chapters):
        check_absent(
            DSE / "05_Output/ch014/ch014.md",
            ["กักขังเจ้า", "ข้านึกว่าเจ้าจะ", "ตอนนี้เจ้าจะ"],
            issues,
        )
    for chapter in ["ch029", "ch030", "ch031"]:
        if include_dse and in_scope(chapter, scoped_chapters):
            check_absent(
                DSE / "05_Output" / chapter / f"{chapter}.md",
                ["อินควิสิเตอร์", "ผู้พิพากษา", "วันนา", "วานนา"],
                issues,
            )
    for number in range(140, 161):
        chapter = f"ch{number:03d}"
        if include_dse and in_scope(chapter, scoped_chapters):
            check_absent(
                DSE / "05_Output" / chapter / f"{chapter}.md",
                ["อินควิสิเตอร์", "ผู้พิพากษา", "(Prominence)"],
                issues,
            )

    if include_hgd and scoped_chapters is None:
        check_absent(HGD / "01_Glossary/Section Chief.md", ["thai_term: หัวหน้าส่วนงาน"], issues)
    if include_hgd:
        for output_dir in sorted((HGD / "05_Output").glob("ch*")):
            if not output_dir.is_dir():
                continue
            chapter = output_dir.name
            if not in_scope(chapter, scoped_chapters):
                continue
            path = output_dir / f"{chapter}.md"
            if not path.exists():
                continue
            check_absent(path, ["หัวหน้าส่วนงาน"], issues)
            check_absent(path, HGD_FORBIDDEN_ENGLISH_OUTPUT, issues)
            check_absent_patterns(path, HGD_FORBIDDEN_REGEX_OUTPUT, issues)
            check_unapproved_question_placeholders(path, HGD_POLICY, chapter, issues)

            generated_path = MOONREAD / "content/generated/books/horror-game-developer/chapters" / f"{chapter}.md"
            if generated_path.exists():
                check_absent(generated_path, HGD_FORBIDDEN_ENGLISH_OUTPUT, issues)
                check_absent_patterns(generated_path, HGD_FORBIDDEN_REGEX_OUTPUT, issues)
                check_unapproved_question_placeholders(generated_path, HGD_POLICY, chapter, issues)
    check_registry_title_policies(
        issues,
        scoped_chapters=scoped_chapters,
        requested_novel=requested_novel,
    )
    if include_hgd:
        check_hgd_required_source_beats(issues, scoped_chapters=scoped_chapters)
        check_hgd_pronoun_policy(issues, scoped_chapters=scoped_chapters)
    check_registry_truncation_against_source(
        issues,
        scoped_chapters=scoped_chapters,
        requested_novel=requested_novel,
    )
    check_registry_forbidden_output_patterns(
        issues,
        scoped_chapters=scoped_chapters,
        requested_novel=requested_novel,
    )

    if include_dse:
        check_paragraph_density(DSE / "05_Output", issues, scoped_chapters=scoped_chapters)
        check_duplicate_title_paragraphs(DSE / "05_Output", issues, scoped_chapters=scoped_chapters)
        check_translation_metadata_leakage(DSE / "05_Output", issues, scoped_chapters=scoped_chapters)
        check_duplicate_title_paragraphs(
            MOONREAD / "content/generated/books/deep-sea-embers/chapters",
            issues,
            scoped_chapters=scoped_chapters,
        )
        check_translation_metadata_leakage(
            MOONREAD / "content/generated/books/deep-sea-embers/chapters",
            issues,
            scoped_chapters=scoped_chapters,
        )
    if include_hgd:
        check_paragraph_density(
            HGD / "05_Output",
            issues,
            max_chars=MAX_HGD_PARAGRAPH_CHARS,
            scoped_chapters=scoped_chapters,
        )
        check_malformed_markdown_artifacts(HGD / "05_Output", issues, scoped_chapters=scoped_chapters)
        check_translation_metadata_leakage(HGD / "05_Output", issues, scoped_chapters=scoped_chapters)
        check_hgd_approved_glossary_leakage(HGD / "05_Output", issues, scoped_chapters=scoped_chapters)
        check_malformed_markdown_artifacts(
            MOONREAD / "content/generated/books/horror-game-developer/chapters",
            issues,
            scoped_chapters=scoped_chapters,
        )
        check_translation_metadata_leakage(
            MOONREAD / "content/generated/books/horror-game-developer/chapters",
            issues,
            scoped_chapters=scoped_chapters,
        )
        check_hgd_approved_glossary_leakage(
            MOONREAD / "content/generated/books/horror-game-developer/chapters",
            issues,
            scoped_chapters=scoped_chapters,
        )

    if issues:
        for issue in issues:
            print(issue)
        return 1
    print("output_quality_guardrails: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
