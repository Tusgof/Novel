from __future__ import annotations

import re
import unicodedata
from collections import OrderedDict

from novel_pipeline.types import TextBlock

SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？!?\.])\s*")
CHINESE_BLOCK_RE = re.compile(r"[\u4e00-\u9fff]+")
LATIN_TERM_RE = re.compile(r"\b[A-Z][a-zA-Z]{2,}\b")
CHINESE_TERM_RE = re.compile(r"^[\u4e00-\u9fff]{2,4}$")

CHINESE_FRAGMENT_PREFIXES = (
    "不",
    "没",
    "无",
    "未",
    "非",
    "的",
    "在",
    "于",
    "本",
    "至",
    "仍",
    "这",
    "那",
    "此",
    "其",
    "每",
    "某",
    "几",
    "都",
    "只",
    "又",
    "还",
    "更",
    "最",
    "很",
    "太",
    "才",
    "就",
    "已",
    "再",
    "正",
    "上",
    "下",
    "前",
    "后",
    "里",
    "外",
    "中",
    "边",
    "旁",
    "对",
    "令",
    "忽然",
    "突然",
    "连忙",
    "立即",
    "缓缓",
    "慢慢",
    "轻轻",
    "悄悄",
    "隐隐",
    "默默",
    "纷纷",
    "似乎",
    "仿佛",
    "深深",
    "渐渐",
    "匆匆",
)

CHINESE_MEASURE_PREFIXES = (
    "个",
    "只",
    "条",
    "扇",
    "把",
    "张",
    "位",
    "名",
    "道",
    "片",
    "颗",
    "枚",
    "座",
    "艘",
    "辆",
    "间",
    "根",
    "支",
    "头",
    "双",
    "件",
    "块",
    "层",
    "束",
    "缕",
    "阵",
    "口",
    "门",
    "台",
    "架",
    "尊",
)

CHINESE_FRAGMENT_SUFFIXES = (
    "么",
    "呢",
    "吧",
    "吗",
    "问",
    "知",
    "道",
    "了",
    "过",
    "着",
    "来",
    "去",
    "起",
    "开",
    "到",
    "见",
    "说",
    "看",
    "听",
    "打",
    "吸",
    "做",
    "为",
    "成",
    "现",
    "是",
    "然",
    "地",
    "得",
)

CHINESE_FRAGMENT_INFIXES = (
    "什么",
    "有什",
    "不知",
    "知道",
    "过去",
    "打个",
    "吸了",
    "都要",
)

CHINESE_NOMINAL_SUFFIXES = (
    "子",
    "气",
    "记",
    "镜",
    "门",
    "船",
    "号",
    "体",
    "灯",
    "塔",
    "海",
    "城",
    "岛",
    "港",
    "馆",
    "室",
    "书",
    "像",
    "影",
    "雾",
    "潮",
    "骨",
    "血",
    "霜",
    "火",
    "人",
    "鬼",
    "神",
    "灵",
    "舰",
    "钟",
    "铃",
    "环",
    "剑",
    "炮",
    "车",
    "眼",
    "手",
    "脸",
    "石",
    "木",
    "梦",
    "屋",
    "殿",
    "域",
    "湾",
    "礁",
    "岸",
    "波",
    "声",
    "音",
    "面",
    "锁",
    "页",
    "纸",
    "线",
    "纹",
    "痕",
)

CHINESE_SURNAME_CHARS = {
    "周",
    "王",
    "李",
    "张",
    "刘",
    "陈",
    "杨",
    "黄",
    "赵",
    "吴",
    "徐",
    "孙",
    "胡",
    "朱",
    "高",
    "林",
    "何",
    "郭",
    "马",
    "罗",
    "梁",
    "宋",
    "郑",
    "谢",
    "韩",
    "唐",
    "冯",
    "于",
    "董",
    "萧",
    "程",
    "曹",
    "袁",
    "邓",
    "许",
    "傅",
    "沈",
    "曾",
    "彭",
    "吕",
    "苏",
    "卢",
    "蒋",
    "蔡",
    "贾",
    "丁",
    "魏",
    "薛",
    "叶",
    "余",
    "潘",
    "杜",
    "戴",
    "夏",
    "钟",
    "汪",
    "田",
    "任",
    "姜",
    "范",
    "方",
    "石",
    "姚",
    "谭",
    "廖",
    "邹",
    "熊",
    "金",
    "陆",
    "郝",
    "孔",
    "白",
    "崔",
    "康",
    "毛",
    "邱",
    "秦",
    "江",
    "史",
    "顾",
    "侯",
    "邵",
    "孟",
    "龙",
    "万",
    "段",
    "雷",
    "钱",
    "汤",
    "尹",
    "黎",
    "易",
    "常",
    "武",
    "乔",
    "贺",
    "赖",
    "龚",
    "文",
    "施",
    "陶",
    "洪",
    "严",
}

CHINESE_NAME_BLOCKED_SECOND_CHARS = {
    "的",
    "是",
    "然",
    "地",
    "得",
    "在",
    "于",
    "本",
    "至",
    "仍",
    "色",
    "旧",
    "耸",
    "发",
    "传",
    "经",
    "向",
    "前",
    "后",
    "上",
    "下",
    "里",
    "外",
    "中",
    "大",
    "小",
    "高",
    "低",
    "深",
    "浅",
    "白",
    "黑",
    "红",
    "青",
    "灰",
    "蓝",
    "黄",
    "金",
    "银",
    "木",
    "石",
    "海",
    "风",
    "雾",
    "气",
    "船",
    "灯",
    "声",
    "影",
    "面",
    "心",
    "手",
    "眼",
    "骨",
    "血",
    "梦",
    "岛",
    "港",
    "城",
    "湾",
    "岸",
    "号",
    "记",
    "镜",
    "问",
}

CHINESE_PHRASE_BLACKLIST = {
    "知道",
    "不知",
    "过去",
    "有什么",
    "有什",
    "什么",
    "那扇",
    "打个",
    "吸了",
    "都要",
    "问号",
    "白色",
    "高耸",
    "曾经",
    "方向",
    "仍然",
    "精神",
    "对面",
    "上面",
    "大门",
    "令人",
}


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_source_risk_tokens(text: str) -> str:
    """Normalize provider-hostile source noise without changing normal prose.

    Some web novels encode monster sounds with heavy Unicode combining marks
    (Zalgo text). Providers can copy or amplify those marks into runaway output.
    Keep the sound-effect line, but strip only heavily marked lines and compact
    absurd repeated characters before provider prompts see them.
    """
    if sum(1 for char in text if unicodedata.category(char).startswith("M")) < 8:
        return text

    normalized_lines: list[str] = []
    for line in text.splitlines():
        mark_count = sum(1 for char in line if unicodedata.category(char).startswith("M"))
        if mark_count >= 4:
            line = "".join(char for char in line if not unicodedata.category(char).startswith("M"))
            line = re.sub(r"(.)\1{16,}", lambda match: match.group(1) * 8, line)
        normalized_lines.append(line)
    return "\n".join(normalized_lines)


def strip_empty_trailing_footnote_marker(text: str, source_language: str) -> str:
    """Remove empty trailing footnote headers from non-CJK source text.

    IRS source chapters can end with a bare ``Footnotes:`` marker. If that
    marker is sent to providers, they may invent glossary/category notes to
    fill the empty section. Keep real footnote markers such as ``[1]`` intact.
    """
    if source_language.startswith(("zh", "ja", "ko")):
        return text
    return re.sub(r"(?:\n\s*){0,2}Footnotes:\s*$", "", text, flags=re.I).rstrip()


def normalize_embedded_cjk_glosses(text: str, source_language: str) -> str:
    """Replace embedded CJK phrases with nearby English glosses in non-CJK source.

    English-source novels sometimes include a Chinese/Japanese/Korean quote followed
    by its English translation, e.g. ``有朋自遠方來 ("friends come from afar")``.
    Passing both to providers has repeatedly leaked CJK into Thai output. Use the
    existing English gloss as the source phrase for translation.
    """
    if source_language.startswith(("zh", "ja", "ko")):
        return text
    cjk = r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af]+"
    pattern = re.compile(
        rf"{cjk}(?:\s*{cjk})*\s*\(\s*[\"“]?([A-Za-z][^)]*?)[\"”]?\s*\)"
    )
    return pattern.sub(lambda match: match.group(1).strip(), text)


def normalize_quoted_cjk_meaning_terms(text: str, source_language: str) -> str:
    """Replace quoted source-script terms when an English meaning follows.

    IRS source can say ``is '군주 (君主),' meaning a ruler...``. The meaning is
    already present in English, so keeping the Korean/Hanja term only increases
    leakage risk in Thai output.
    """
    if source_language.startswith(("zh", "ja", "ko")):
        return text

    source_script = r"\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af"
    pattern = re.compile(
        rf"([\"'“‘])(?:[{source_script}\s·・]+)(?:\s*\([{source_script}\s·・,，、;；:：'\-]+\))?\s*,?([\"'”’])\s*,?\s*meaning\s+",
        flags=re.I,
    )
    return pattern.sub("a term meaning ", text)


def strip_parenthetical_cjk_annotations(text: str, source_language: str) -> str:
    """Remove source-script annotations in parentheses from non-CJK source.

    English-source chapters can include already-explained Hanja/Han annotations,
    such as ``Cheon Yo-hwa of the hundred tales (千謠話)``. Providers have
    repeatedly copied those annotations into Thai output. Remove only parentheses
    whose content is source-script annotation, while preserving normal prose
    parentheses such as ``(skill)`` or ``(Chapter 1)``.
    """
    if source_language.startswith(("zh", "ja", "ko")):
        return text

    source_script = r"\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af"
    annotation_re = re.compile(rf"\s*\(([{source_script}\s·・,，、;；:：'\-]+)\)")

    def replacement(match: re.Match[str]) -> str:
        content = match.group(1)
        if re.search(rf"[{source_script}]", content):
            return ""
        return match.group(0)

    return annotation_re.sub(replacement, text)


def split_sentences(text: str) -> list[str]:
    text = normalize_whitespace(text)
    if not text:
        return []
    parts = SENTENCE_SPLIT_RE.split(text)
    return [part.strip() for part in parts if part.strip()]


def word_count(text: str) -> int:
    return len([token for token in re.split(r"\s+", text.strip()) if token])


def split_blocks(
    chapter_id: str,
    text: str,
    source_language: str,
    *,
    zh_limit: int = 2500,
    non_zh_limit: int = 5000,
) -> list[TextBlock]:
    text = normalize_whitespace(text)
    text = normalize_embedded_cjk_glosses(text, source_language)
    text = normalize_quoted_cjk_meaning_terms(text, source_language)
    text = strip_parenthetical_cjk_annotations(text, source_language)
    text = normalize_source_risk_tokens(text)
    text = strip_empty_trailing_footnote_marker(text, source_language)
    if not text:
        return []

    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    blocks: list[TextBlock] = []
    current: list[str] = []
    current_metric = 0
    limit = zh_limit if source_language.startswith("zh") else non_zh_limit
    use_chars = source_language.startswith("zh")

    expanded_paragraphs: list[str] = []
    for paragraph in paragraphs:
        metric = len(paragraph) if use_chars else word_count(paragraph)
        if metric > limit:
            expanded_paragraphs.extend(_split_oversized_paragraph(paragraph, limit=limit, use_chars=use_chars))
        else:
            expanded_paragraphs.append(paragraph)

    for paragraph in expanded_paragraphs:
        metric = len(paragraph) if use_chars else word_count(paragraph)
        if current and current_metric + metric > limit:
            blocks.append(_make_block(chapter_id, len(blocks), "\n\n".join(current), source_language))
            current = [paragraph]
            current_metric = metric
        else:
            current.append(paragraph)
            current_metric += metric

    if current:
        blocks.append(_make_block(chapter_id, len(blocks), "\n\n".join(current), source_language))
    return blocks


def _split_oversized_paragraph(paragraph: str, *, limit: int, use_chars: bool) -> list[str]:
    sentences = split_sentences(paragraph)
    if len(sentences) <= 1:
        return _hard_split_text(paragraph, limit=limit, use_chars=use_chars)

    chunks: list[str] = []
    current: list[str] = []
    current_metric = 0
    for sentence in sentences:
        metric = len(sentence) if use_chars else word_count(sentence)
        if metric > limit:
            if current:
                chunks.append("".join(current) if use_chars else " ".join(current))
                current = []
                current_metric = 0
            chunks.extend(_hard_split_text(sentence, limit=limit, use_chars=use_chars))
            continue
        if current and current_metric + metric > limit:
            chunks.append("".join(current) if use_chars else " ".join(current))
            current = [sentence]
            current_metric = metric
        else:
            current.append(sentence)
            current_metric += metric
    if current:
        chunks.append("".join(current) if use_chars else " ".join(current))
    return chunks


def _hard_split_text(text: str, *, limit: int, use_chars: bool) -> list[str]:
    if use_chars:
        return [text[index : index + limit] for index in range(0, len(text), limit) if text[index : index + limit]]
    words = text.split()
    return [" ".join(words[index : index + limit]) for index in range(0, len(words), limit)]


def parse_chapter_range(range_str: str) -> list[str]:
    """Parse chapter range string into a list of chapter IDs."""
    if not range_str or not range_str.strip():
        raise ValueError(f"Empty chapter range: {range_str!r}")

    range_str = range_str.strip()

    if "," in range_str:
        parts = [p.strip() for p in range_str.split(",") if p.strip()]
        if not parts:
            raise ValueError(f"No valid chapter IDs in range: {range_str!r}")
        return parts

    if "-" in range_str:
        match = re.match(r"^([a-zA-Z]*)(\d+)-([a-zA-Z]*)(\d+)$", range_str)
        if match:
            prefix_start, num_start_str, prefix_end, num_end_str = match.groups()
            prefix = prefix_start if prefix_start else prefix_end
            num_start = int(num_start_str)
            num_end = int(num_end_str)
            if num_start > num_end:
                raise ValueError(f"Invalid range: start > end in {range_str!r}")
            width = max(len(num_start_str), len(num_end_str))
            return [f"{prefix}{n:0{width}d}" for n in range(num_start, num_end + 1)]

        match = re.match(r"^([a-zA-Z]*)(\d+)-(\d+)$", range_str)
        if match:
            prefix, num_start_str, num_end_str = match.groups()
            num_start = int(num_start_str)
            num_end = int(num_end_str)
            if num_start > num_end:
                raise ValueError(f"Invalid range: start > end in {range_str!r}")
            width = len(num_start_str)
            return [f"{prefix}{n:0{width}d}" for n in range(num_start, num_end + 1)]

        raise ValueError(f"Unparseable chapter range: {range_str!r}")

    if re.match(r"^[a-zA-Z]*\d+$", range_str):
        return [range_str]

    raise ValueError(f"Unparseable chapter range: {range_str!r}")


def extract_candidate_terms(text: str) -> list[str]:
    """Extract glossary candidates with a conservative noun/name gate."""
    counts: dict[str, int] = {}

    for match in LATIN_TERM_RE.findall(text):
        term = match.strip()
        if term:
            counts[term] = counts.get(term, 0) + 1

    for block in CHINESE_BLOCK_RE.findall(text):
        for window_size in range(2, 5):
            for i in range(len(block) - window_size + 1):
                term = block[i : i + window_size]
                if _is_plausible_chinese_slice(term):
                    counts[term] = counts.get(term, 0) + 1

    results: list[str] = []
    for term, count in counts.items():
        if LATIN_TERM_RE.fullmatch(term):
            results.append(term)
            continue
        if not CHINESE_TERM_RE.fullmatch(term):
            continue
        if _is_likely_chinese_name(term) and count >= 3:
            results.append(term)
            continue
        if _is_likely_noun_term(term) and count >= 3:
            results.append(term)

    results.sort(key=lambda term: (_term_rank(term), len(term), term), reverse=True)
    return list(OrderedDict.fromkeys(results).keys())


def _contains_any(text: str, fragments: tuple[str, ...]) -> bool:
    return any(fragment in text for fragment in fragments)


def _starts_with_any(text: str, prefixes: tuple[str, ...]) -> bool:
    return any(text.startswith(prefix) for prefix in prefixes)


def _ends_with_any(text: str, suffixes: tuple[str, ...]) -> bool:
    return any(text.endswith(suffix) for suffix in suffixes)


def _is_plausible_chinese_slice(term: str) -> bool:
    if not CHINESE_TERM_RE.fullmatch(term):
        return False
    if term in CHINESE_PHRASE_BLACKLIST:
        return False
    if _contains_any(term, CHINESE_FRAGMENT_INFIXES):
        return False
    if _starts_with_any(term, CHINESE_MEASURE_PREFIXES):
        return False
    if _starts_with_any(term, CHINESE_FRAGMENT_PREFIXES):
        return False
    if _ends_with_any(term, CHINESE_FRAGMENT_SUFFIXES):
        return False
    if any(char in term for char in "什么哪谁何了过着"):
        return False
    if len(term) > 2 and term[0] == term[1]:
        return False
    return True


def _is_likely_chinese_name(term: str) -> bool:
    if len(term) != 2:
        return False
    if term[0] not in CHINESE_SURNAME_CHARS:
        return False
    if term[1] in CHINESE_NAME_BLOCKED_SECOND_CHARS:
        return False
    return _is_plausible_chinese_slice(term)


def _is_likely_noun_term(term: str) -> bool:
    if not _is_plausible_chinese_slice(term):
        return False
    return _ends_with_any(term, CHINESE_NOMINAL_SUFFIXES)


def _term_rank(term: str) -> int:
    if LATIN_TERM_RE.fullmatch(term):
        return 4
    if _is_likely_chinese_name(term):
        return 3
    if _is_likely_noun_term(term):
        return 2
    return 1


def _make_block(chapter_id: str, index: int, text: str, source_language: str) -> TextBlock:
    normalized = normalize_whitespace(text)
    return TextBlock(
        block_id=f"{chapter_id}-block-{index + 1:03d}",
        chapter_id=chapter_id,
        block_index=index,
        source_text=normalized,
        source_language=source_language,
        start_offset=0,
        end_offset=len(normalized),
    )


def detect_mojibake(text: str, expected_language: str) -> bool:
    """
    Detect obvious mojibake in text based on expected language.
    Returns True if mojibake detected.
    """
    if not text:
        return False
    import unicodedata

    # Helper functions
    def is_cjk(char: str) -> bool:
        code = ord(char)
        return 0x4E00 <= code <= 0x9FFF

    def is_thai(char: str) -> bool:
        code = ord(char)
        return 0x0E00 <= code <= 0x0E7F

    def is_latin(char: str) -> bool:
        cat = unicodedata.category(char)
        return cat[0] == 'L' and char.isascii()

    def is_digit(char: str) -> bool:
        return unicodedata.category(char) == 'Nd' or char.isdigit()

    def is_punctuation(char: str) -> bool:
        return unicodedata.category(char)[0] in ('P', 'S')

    def is_whitespace(char: str) -> bool:
        return unicodedata.category(char)[0] == 'Z' or char in '\t\n\r'

    def is_mark(char: str) -> bool:
        return unicodedata.category(char)[0] == 'M'

    # Count script categories
    cjk_count = 0
    thai_count = 0
    latin_count = 0
    digit_count = 0
    punctuation_count = 0
    whitespace_count = 0
    mark_count = 0
    other_count = 0

    for char in text:
        if is_cjk(char):
            cjk_count += 1
        elif is_thai(char):
            thai_count += 1
        elif is_latin(char):
            latin_count += 1
        elif is_digit(char):
            digit_count += 1
        elif is_punctuation(char):
            punctuation_count += 1
        elif is_whitespace(char):
            whitespace_count += 1
        elif is_mark(char):
            mark_count += 1
        else:
            other_count += 1

    total_chars = len(text)
    meaningful_chars = total_chars - whitespace_count - punctuation_count

    if expected_language.startswith("zh"):
        # For Chinese source: require meaningful CJK presence, reject Thai-heavy text
        # Allow Latin, digits, punctuation, whitespace as neutral
        if total_chars == 0:
            return False
        
        # Thai-heavy text must fail zh
        if thai_count >= 2 or (meaningful_chars > 0 and thai_count / meaningful_chars > 0.05):
            return True
        
        # Other-script-heavy text must fail zh
        if other_count > max(1, meaningful_chars * 0.05):
            return True
        
        # Latin/digit/punctuation/whitespace-only text should not be classified as mojibake
        if cjk_count == 0 and thai_count == 0 and other_count == 0:
            return False
        
        # Chinese source must have meaningful CJK
        if meaningful_chars >= 10:
            if cjk_count < max(2, meaningful_chars * 0.20):
                return True
        else:
            # Short text: must have at least one CJK character if there are meaningful chars
            if meaningful_chars > 0 and cjk_count == 0:
                return True
        
        return False

    elif expected_language.startswith("th"):
        # For Thai translation: require meaningful Thai presence, allow small CJK for proper names
        # Allow whitespace, Latin, digits, punctuation, marks
        if total_chars == 0:
            return False
        
        # Thai text should pass if it has enough Thai script
        if meaningful_chars >= 10:
            if thai_count < max(3, meaningful_chars * 0.30):
                return True
        else:
            # Short text: must have at least one Thai character if there are meaningful chars
            if meaningful_chars > 0 and thai_count == 0:
                return True
        
        # CJK proper names are allowed in Thai output
        if cjk_count > max(4, meaningful_chars * 0.20):
            return True
        
        # Other scripts must be limited
        if other_count > max(1, meaningful_chars * 0.05):
            return True
        
        return False

    else:
        # Unknown language: only basic validation - allow common categories
        allowed_categories = {"P", "Z", "M", "N", "L", "S"}
        unexpected = 0
        for char in text:
            if unicodedata.category(char)[0] not in allowed_categories:
                unexpected += 1
        if unexpected > max(3, total_chars * 0.1):
            return True
        return False


def validate_text_script(text: str, expected_language: str) -> None:
    """
    Raise ValueError if text appears to be mojibake.
    """
    if detect_mojibake(text, expected_language):
        raise ValueError(
            f"Text appears to be mojibake (unexpected characters) for language {expected_language}"
        )


__all__ = [
    "CHINESE_NOMINAL_SUFFIXES",
    "CHINESE_NAME_BLOCKED_SECOND_CHARS",
    "CHINESE_SURNAME_CHARS",
    "extract_candidate_terms",
    "normalize_quoted_cjk_meaning_terms",
    "normalize_whitespace",
    "parse_chapter_range",
    "strip_parenthetical_cjk_annotations",
    "split_blocks",
    "split_sentences",
    "word_count",
    "_is_likely_chinese_name",
    "_is_likely_noun_term",
    "detect_mojibake",
    "validate_text_script",
]
