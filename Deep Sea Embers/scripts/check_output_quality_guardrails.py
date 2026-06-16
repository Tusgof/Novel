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
MAX_PARAGRAPH_CHARS = 900
MAX_HGD_PARAGRAPH_CHARS = 520
HGD_ENGLISH_TITLE_MARKERS = [
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
    "*Click!*",
    "*Takakakakaka—*",
    "*Tak!*",
    "*To Tok—*",
    "[Seth's USB stick]",
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
HGD_DANGLING_ENDINGS = (
    "แต่",
    "และ",
    "กับ",
    "ของ",
    "ที่",
    "ใน",
    "ก่อนจะ",
    "มือเธอ",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def check_absent(path: Path, terms: list[str], issues: list[str]) -> None:
    if not path.exists():
        issues.append(f"missing file: {path}")
        return
    text = read(path)
    for term in terms:
        if term in text:
            issues.append(f"{path}: forbidden variant remains: {term}")


def check_paragraph_density(root: Path, issues: list[str], *, max_chars: int = MAX_PARAGRAPH_CHARS) -> None:
    if not root.exists():
        return
    for path in sorted(root.glob("ch*/ch*.md")):
        text = read(path)
        for index, paragraph in enumerate(text.split("\n\n"), start=1):
            stripped = paragraph.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if len(stripped) > max_chars:
                issues.append(f"{path}: paragraph {index} too dense ({len(stripped)} chars)")


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

        ratio = len(output_body) / max(1, len(source_text))
        if ratio < 0.45:
            issues.append(
                f"{output_path}: output appears truncated versus source "
                f"(source chars={len(source_text)}, output chars={len(output_body)}, ratio={ratio:.2f})"
            )

        tail = output_body.rstrip()
        if any(tail.endswith(ending) for ending in HGD_DANGLING_ENDINGS):
            issues.append(f"{output_path}: output appears to end mid-sentence: {tail[-80:]}")


def check_hgd_required_source_beats(issues: list[str]) -> None:
    for rule in HGD_REQUIRED_SOURCE_BEATS:
        chapter = rule["chapter"]
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


def check_hgd_pronoun_policy(issues: list[str]) -> None:
    for chapter in sorted(HGD_SETH_PRONOUN_CHAPTERS):
        path = HGD / "05_Output" / chapter / f"{chapter}.md"
        if not path.exists():
            continue
        text = read(path)
        if "ฉัน" in text:
            issues.append(f"{path}: Seth-dominant HGD chapter still contains first-person drift marker: ฉัน")

    ch033_path = HGD / "05_Output/ch033/ch033.md"
    if ch033_path.exists():
        text = read(ch033_path)
        for phrase in ["เธอเห็นอะไร", "เธอไม่ผิดหรอก", "ฉันว่าเธอพูดถูก", "ผมว่าเธอพูดถูก"]:
            if phrase in text:
                issues.append(f"{ch033_path}: Kyle/Seth peer-address drift remains: {phrase}")


def main() -> int:
    issues: list[str] = []

    check_absent(DSE / "05_Output/ch001/ch001.md", ["ตั้งเครื่องหมายคำถาม"], issues)
    check_absent(
        DSE / "05_Output/ch014/ch014.md",
        ["กักขังเจ้า", "ข้านึกว่าเจ้าจะ", "ตอนนี้เจ้าจะ"],
        issues,
    )
    for chapter in ["ch029", "ch030", "ch031"]:
        check_absent(
            DSE / "05_Output" / chapter / f"{chapter}.md",
            ["อินควิสิเตอร์", "ผู้พิพากษา", "วันนา", "วานนา"],
            issues,
        )

    check_absent(HGD / "01_Glossary/Section Chief.md", ["thai_term: หัวหน้าส่วนงาน"], issues)
    for number in range(1, 36):
        chapter = f"ch{number:03d}"
        path = HGD / "05_Output" / chapter / f"{chapter}.md"
        if not path.exists():
            continue
        check_absent(path, ["หัวหน้าส่วนงาน"], issues)
        check_absent(path, HGD_FORBIDDEN_ENGLISH_OUTPUT, issues)

        generated_path = MOONREAD / "content/generated/books/horror-game-developer/chapters" / f"{chapter}.md"
        if generated_path.exists():
            check_absent(generated_path, HGD_FORBIDDEN_ENGLISH_OUTPUT, issues)
    check_hgd_title_fallbacks(issues)
    check_dse_generic_title_fallbacks(issues)
    check_hgd_required_source_beats(issues)
    check_hgd_pronoun_policy(issues)
    check_hgd_truncation_against_source(issues)

    check_paragraph_density(DSE / "05_Output", issues)
    for number in range(1, 36):
        chapter = f"ch{number:03d}"
        check_paragraph_density(HGD / "05_Output" / chapter, issues, max_chars=MAX_HGD_PARAGRAPH_CHARS)

    if issues:
        for issue in issues:
            print(issue)
        return 1
    print("output_quality_guardrails: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
