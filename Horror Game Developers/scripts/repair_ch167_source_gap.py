from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
EXTRACT_PATH = WORKSPACE / "04_Work" / "hgd_missing_172_180_182_novellive_extract.json"

FIRST_OLD = 167
LAST_OLD = 220


@dataclass(frozen=True)
class MissingChapter:
    local_number: int
    web_number: int
    title: str
    url: str
    raw_text: str


MISSING_LOCAL_BY_WEB = {
    172: 167,
    173: 168,
    174: 169,
    175: 170,
    176: 171,
    177: 172,
    178: 173,
    179: 174,
    180: 175,
    182: 177,
}


TITLE_MAP = {
    "Bet": "เดิมพัน",
    "Trending": "ติดเทรนด์",
    "New Mission": "ภารกิจใหม่",
    "Happy Kids Orphanage": "สถานเลี้ยงเด็กกำพร้าแฮปปี้คิดส์",
    "The boy and the crayons": "เด็กชายกับสีเทียน",
}


def chapter_id(number: int) -> str:
    return f"ch{number:03d}"


def clean_source_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\u00a0", " ").strip()
    cut_markers = [
        "\nSource:",
        "\nVisit and read more novel",
        "\n1 Common Daily Drink",
        "\nAmerican Memory Institute",
        "\nSponsored",
    ]
    end = len(text)
    for marker in cut_markers:
        pos = text.find(marker)
        if pos >= 0:
            end = min(end, pos)
    text = text[:end].strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def thai_title(source_title: str, local_number: int) -> str:
    match = re.match(r"Chapter\s+\d+:\s+(.+?)(\s+\[\d+\])?$", source_title)
    if not match:
        return f"ตอนที่ {local_number} - {source_title}"
    title = match.group(1).strip()
    suffix = match.group(2) or ""
    return f"ตอนที่ {local_number} - {TITLE_MAP.get(title, title)}{suffix}"


def load_missing() -> list[MissingChapter]:
    raw = json.loads(EXTRACT_PATH.read_text(encoding="utf-8"))
    chapters: list[MissingChapter] = []
    for item in raw:
        web_number = int(item["web_chapter"])
        if web_number not in MISSING_LOCAL_BY_WEB:
            continue
        cleaned = clean_source_text(item["raw_text"])
        if len(cleaned) < 2000:
            raise RuntimeError(f"Extracted chapter {web_number} is suspiciously short: {len(cleaned)} chars")
        chapters.append(
            MissingChapter(
                local_number=MISSING_LOCAL_BY_WEB[web_number],
                web_number=web_number,
                title=item["title"],
                url=item["url"],
                raw_text=cleaned,
            )
        )
    expected = set(MISSING_LOCAL_BY_WEB)
    found = {chapter.web_number for chapter in chapters}
    if found != expected:
        raise RuntimeError(f"Missing extracted chapters: expected {sorted(expected)}, found {sorted(found)}")
    return sorted(chapters, key=lambda chapter: chapter.local_number)


def backup_tree(name: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source = ROOT / name
    backup = ROOT / f"{name}_backup_before_ch167_gap_fix_{stamp}"
    shutil.copytree(source, backup)
    return backup


def replace_chapter_refs(path: Path, old_id: str, new_id: str, old_num: int, new_num: int) -> None:
    if path.suffix.lower() not in {".json", ".md", ".txt"}:
        return
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace(old_id, new_id)
    text = re.sub(rf"ตอนที่\s+{old_num}\b", f"ตอนที่ {new_num}", text)
    path.write_text(text, encoding="utf-8")


def rename_internal_files(directory: Path, old_num: int, new_num: int) -> None:
    old_id = chapter_id(old_num)
    new_id = chapter_id(new_num)
    for path in sorted(directory.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_file():
            replace_chapter_refs(path, old_id, new_id, old_num, new_num)
            if old_id in path.name:
                path.rename(path.with_name(path.name.replace(old_id, new_id)))


def move_chapter_dir(base: Path, old_num: int, new_num: int) -> None:
    old_dir = base / chapter_id(old_num)
    if not old_dir.exists():
        return
    new_dir = base / chapter_id(new_num)
    if new_dir.exists():
        raise RuntimeError(f"Destination already exists: {new_dir}")
    old_dir.rename(new_dir)
    rename_internal_files(new_dir, old_num, new_num)


def insert_source(chapter: MissingChapter) -> None:
    cid = chapter_id(chapter.local_number)
    target = ROOT / "03_Raw" / cid
    if target.exists():
        raise RuntimeError(f"Insert target already exists: {target}")
    target.mkdir(parents=True)
    payload = {
        "novel_id": "horror-game-developer",
        "chapter_id": cid,
        "title": chapter.title.replace(":", " -", 1),
        "source_language": "en",
        "source_path": None,
        "source_url": chapter.url,
        "metadata": {
            "source_site": "NovelLive",
            "source_gap_repair": "ch167_gap_fix",
            "web_chapter": chapter.web_number,
            "thai_title": thai_title(chapter.title, chapter.local_number),
        },
        "raw_text": chapter.raw_text,
    }
    (target / "source.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (target / "source.txt").write_text(chapter.raw_text + "\n", encoding="utf-8")


def main() -> int:
    missing = load_missing()

    sentinel = ROOT / "03_Raw" / "ch176" / "source.json"
    if sentinel.exists():
        payload = json.loads(sentinel.read_text(encoding="utf-8"))
        if payload.get("title") == "Chapter 181 - The boy and the crayons [1]":
            print("ch167 gap appears to be already repaired; no changes made.")
            return 0

    for required in ["03_Raw", "04_Work", "05_Output"]:
        if not (ROOT / required).exists():
            raise RuntimeError(f"Required directory missing: {required}")

    backups = [backup_tree(name) for name in ["03_Raw", "04_Work", "05_Output"]]

    for base_name in ["03_Raw", "04_Work", "05_Output"]:
        base = ROOT / base_name
        for number in range(LAST_OLD, 167, -1):
            move_chapter_dir(base, number, number + 10)
        move_chapter_dir(base, 167, 176)

    for chapter in missing:
        insert_source(chapter)

    report = ROOT / "07_Reports" / "hgd_ch167_gap_source_repair.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        "\n".join(
            [
                "# HGD ch167 Source Gap Repair",
                "",
                "Cause: RoliaScan manifest skipped web chapters 172-180 and 182, so local ch167 jumped from web chapter 171 to 181.",
                "",
                "Repair:",
                "- Shifted existing local ch167 to ch176.",
                "- Shifted existing local ch168-ch220 to ch178-ch230.",
                "- Inserted NovelLive source chapters 172-180 as local ch167-ch175.",
                "- Inserted NovelLive source chapter 182 as local ch177.",
                "- Historical ledger records were not rewritten; they remain append-only audit history.",
                "",
                "Backups:",
                *[f"- {path.relative_to(ROOT)}" for path in backups],
                "",
                "Inserted source chapters:",
                *[f"- ch{c.local_number:03d}: web Chapter {c.web_number} - {c.title}" for c in missing],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Inserted {len(missing)} source chapters and repaired numbering. Report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
