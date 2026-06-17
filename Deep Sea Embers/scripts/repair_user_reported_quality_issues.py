from __future__ import annotations

from pathlib import Path
import re


REPO = Path(__file__).resolve().parents[1]
NOVEL_ROOT = REPO.parent
DSE = REPO
HGD = NOVEL_ROOT / "Horror Game Developers"

HGD_TITLE_MAP = {
    "Prologue": "บทนำ",
    "The Jester": "ตัวตลก",
    "Mission Complete": "ภารกิจสำเร็จ",
    "The world has changed": "โลกเปลี่ยนไปแล้ว",
    "Orientation Day": "วันปฐมนิเทศ",
    "Exit": "ทางออก",
    "Developing Game": "พัฒนาเกม",
    "The missing piece": "ชิ้นส่วนที่หายไป",
    "Scream": "เสียงกรีดร้อง",
    "Quest Completed": "เควสต์สำเร็จ",
    "Painting": "ภาพวาด",
    "Velora Art Museum": "พิพิธภัณฑ์ศิลปะเวลอรา",
    "Mr. Jingles": "มิสเตอร์จิงเกิลส์",
    "Mr Jingles": "มิสเตอร์จิงเกิลส์",
    "The basement": "ห้องใต้ดิน",
    "Puzzle": "ปริศนา",
    "The Origin": "จุดกำเนิด",
    "Not as it seems": "ไม่ใช่อย่างที่เห็น",
    "Inside a cartoon": "ในโลกการ์ตูน",
    "Rat": "หนู",
    "For the future": "เพื่ออนาคต",
    "Gathering Funds": "ระดมทุน",
    "Haunting": "การหลอกหลอน",
    "Freelancers": "ฟรีแลนซ์",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def replace_in_file(path: Path, replacements: list[tuple[str, str]]) -> bool:
    if not path.exists():
        return False
    original = read_text(path)
    updated = original
    for old, new in replacements:
        updated = updated.replace(old, new)
    if updated != original:
        write_text(path, updated)
        return True
    return False


def markdown_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(root.glob("ch*/ch*.md"))


def hgd_published_markdown_files() -> list[Path]:
    return [
        HGD / "05_Output" / f"ch{number:03d}" / f"ch{number:03d}.md"
        for number in range(1, 36)
        if (HGD / "05_Output" / f"ch{number:03d}" / f"ch{number:03d}.md").exists()
    ]


def split_long_paragraph(paragraph: str, *, soft_limit: int = 430, hard_limit: int = 620) -> list[str]:
    text = paragraph.strip()
    if len(text) <= hard_limit:
        return [text]

    parts: list[str] = []
    remaining = text
    while len(remaining) > hard_limit:
        window = remaining[:hard_limit]
        cut = -1
        for marker in [" ”", " ”", "” ", "?” ", "!” ", ". ", "... ", "… ", "— ", " "]:
            pos = window.rfind(marker, soft_limit)
            if pos > cut:
                cut = pos + len(marker.rstrip())
        if cut < soft_limit:
            cut = window.rfind(" ", soft_limit)
        if cut < soft_limit:
            break
        parts.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()

    if remaining:
        parts.append(remaining)
    return parts or [text]


def translate_hgd_title(title: str) -> str:
    match = re.match(r"^Chapter\s+(\d+)\s+-\s+(.+?)(\s+\[\d+\])?$", title.strip())
    if not match:
        return title
    number, english_title, suffix = match.groups()
    thai_title = HGD_TITLE_MAP.get(english_title.strip(), english_title.strip())
    return f"ตอนที่ {int(number)} - {thai_title}{suffix or ''}"


def repair_hgd_heading(text: str) -> str:
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines:
        return text
    if lines[0].startswith("# "):
        title = lines[0][2:].strip()
        lines[0] = f"# {translate_hgd_title(title)}"
    return "\n".join(lines)


def normalize_hgd_system_panels(text: str) -> str:
    def panel_replacement(match: re.Match[str]) -> str:
        marker = match.group(1).strip()
        return f"\n\n**{marker}**\n\n"

    # HGD uses game UI panels heavily. Standalone bold panels match the provided good-format sample
    # and keep menus/status text from being buried inside prose paragraphs.
    text = re.sub(r"(?<!\*)\s*(\[[^\]\n]{1,120}\])\s*(?!\*)", panel_replacement, text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def split_hgd_inline_beats(paragraph: str) -> list[str]:
    current = paragraph.strip()
    if not current:
        return []

    # Pull leading sound/thought beats out as their own line: *Click.* text -> *Click.* / text.
    leading_italic = re.match(r"^(\*[^*\n]{1,90}\*)\s+(.+)$", current)
    if leading_italic:
        first, rest = leading_italic.groups()
        return [first.strip(), *split_hgd_inline_beats(rest.strip())]

    # Put quoted dialogue beats on their own paragraph when they occur mid-paragraph.
    current = re.sub(r"\s+(\"[^\"]{1,180}\")", r"\n\n\1", current)
    current = re.sub(r"\s+(“[^”]{1,180}”)", r"\n\n\1", current)

    parts: list[str] = []
    for chunk in [item.strip() for item in current.split("\n\n") if item.strip()]:
        parts.extend(split_long_paragraph(chunk, soft_limit=360, hard_limit=520))
    return parts


def repair_hgd_format(path: Path) -> bool:
    original = read_text(path)
    text = repair_hgd_heading(original)
    text = normalize_hgd_system_panels(text)
    blocks = text.strip().split("\n\n")
    repaired_blocks: list[str] = []

    for block in blocks:
        stripped = block.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped == "─────" or "\n" in stripped:
            repaired_blocks.append(stripped)
            continue
        if re.fullmatch(r"\*\*\[[\s\S]{1,140}\]\*\*", stripped):
            repaired_blocks.append(stripped)
            continue
        if re.fullmatch(r"\*[^*\n]{1,140}\*", stripped):
            repaired_blocks.append(stripped)
            continue
        repaired_blocks.extend(split_hgd_inline_beats(stripped))

    updated = "\n\n".join(item.strip() for item in repaired_blocks if item.strip()).strip() + "\n"
    if updated != original:
        write_text(path, updated)
        return True
    return False


def reflow_markdown(path: Path) -> bool:
    original = read_text(path)
    blocks = original.strip().split("\n\n")
    updated_blocks: list[str] = []

    for block in blocks:
        stripped = block.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith("```") or stripped == "─────":
            updated_blocks.append(stripped)
            continue
        if "\n" in stripped:
            updated_blocks.append(stripped)
            continue
        updated_blocks.extend(split_long_paragraph(stripped))

    updated = "\n\n".join(updated_blocks).strip() + "\n"
    if updated != original:
        write_text(path, updated)
        return True
    return False


def main() -> None:
    changed: list[str] = []

    dse_replacements = {
        DSE / "05_Output/ch001/ch001.md": [
            ('แม้แต่ "ตัวเอง" ตอนนี้ก็ยังต้องตั้งเครื่องหมายคำถามอยู่เลย', 'แม้แต่ "ตัวเอง" ตอนนี้ก็ยังต้องตั้งคำถามอยู่เลย'),
            ('แม้แต่ "ตัวเอง" ก็ยังต้องตั้งเครื่องหมายคำถาม', 'แม้แต่ "ตัวเอง" ก็ยังต้องตั้งคำถาม'),
        ],
        DSE / "05_Output/ch014/ch014.md": [
            ("หีบนี้เคยเป็นที่กักขังเจ้า ข้านึกว่าเจ้าจะถือสาเสียอีก", "หีบนี้เคยเป็นที่กักขังคุณ ผมนึกว่าคุณจะถือสาเสียอีก"),
            ("แต่ดูเหมือนตอนนี้เจ้าจะขาดมันไม่ได้แล้ว", "แต่ดูเหมือนตอนนี้คุณจะขาดมันไม่ได้แล้ว"),
        ],
    }
    for path, replacements in dse_replacements.items():
        if replace_in_file(path, replacements):
            changed.append(str(path))

    for chapter in ["ch029", "ch030", "ch031"]:
        path = DSE / "05_Output" / chapter / f"{chapter}.md"
        if replace_in_file(
            path,
            [
                ("ผู้พิพากษาฟาน", "ตุลาการฟานน่า"),
                ("ผู้พิพากษา", "ตุลาการ"),
                ("อินควิสิเตอร์ฟานน่า", "ตุลาการฟานน่า"),
                ("อินควิสิเตอร์", "ตุลาการ"),
                ("วันนา", "ฟานน่า"),
                ("วานนา", "ฟานน่า"),
                ("ฟานน่ามิ", "ฟานน่ามิ"),
            ],
        ):
            changed.append(str(path))

    hgd_section_replacements = [
        ("หัวหน้าส่วนงาน", "หัวหน้าแผนก"),
        ("หัวหน้าส่วนงาน ", "หัวหน้าแผนก "),
    ]
    if replace_in_file(HGD / "01_Glossary/Section Chief.md", [("thai_term: หัวหน้าส่วนงาน", "thai_term: หัวหน้าแผนก")]):
        changed.append(str(HGD / "01_Glossary/Section Chief.md"))
    for path in hgd_published_markdown_files():
        if replace_in_file(path, hgd_section_replacements):
            changed.append(str(path))
        if repair_hgd_format(path):
            changed.append(str(path))

    for path in markdown_files(DSE / "05_Output"):
        if reflow_markdown(path):
            changed.append(str(path))
    for path in hgd_published_markdown_files():
        if reflow_markdown(path):
            changed.append(str(path))

    for path in sorted(set(changed)):
        print(path)
    print(f"changed_files={len(set(changed))}")


if __name__ == "__main__":
    main()
