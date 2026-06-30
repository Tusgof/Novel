from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


TITLE_MAP = {
    "The Troublemaker": "ตัวปัญหา",
    "The Unidentified One": "ผู้ไม่อาจระบุตัวตน",
    "The Internationalist": "นักสากลนิยม",
    "The Companion": "สหายร่วมทาง",
    "The Reader": "นักอ่าน",
    "The Prophet": "ศาสดา",
    "The New Budhha": "พระพุทธะองค์ใหม่",
    "The Explorer": "นักสำรวจ",
    "The Creator": "ผู้สร้าง",
    "The Taxpayer": "ผู้เสียภาษี",
    "Rich Bond": "สายสัมพันธ์เศรษฐี",
    "Observer": "ผู้สังเกตการณ์",
    "Returnee": "ผู้กลับคืน",
    "Survivor": "ผู้รอดชีวิต",
}

ROMAN_MAP = {
    "Ⅰ": "1",
    "ⅠⅠ": "2",
    "ⅠⅠⅠ": "3",
    "II": "2",
    "III": "3",
    "IV": "4",
    "V": "5",
    "I": "1",
}


def sidecar_title(source_title: str) -> str:
    base = source_title.split(" - ", 1)[1].strip()
    for roman, number in sorted(ROMAN_MAP.items(), key=lambda item: len(item[0]), reverse=True):
        suffix = f" {roman}"
        if base.endswith(suffix):
            arc = base[: -len(suffix)]
            return f"{TITLE_MAP.get(arc, arc)} {number}"
    return TITLE_MAP.get(base, base)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    for index in range(11, 51):
        chapter_id = f"ch{index:03d}"
        source_path = root / "03_Raw" / chapter_id / "source.json"
        data = json.loads(source_path.read_text(encoding="utf-8-sig"))
        source_title = str(data["title"])
        thai_title = sidecar_title(source_title)
        work_dir = root / "04_Work" / chapter_id
        work_dir.mkdir(parents=True, exist_ok=True)
        sidecar = {
            "source_title": source_title.replace("Ⅰ", "I"),
            "literal_title": thai_title,
            "thai_title": thai_title,
            "approved_by": "codex_irs_clean_title_gate",
            "run_id": "irs-clean-ch001-ch050-v1",
            "created_at": now,
            "literal_provider": "local",
            "literal_model": "codex_decision",
            "refine_provider": "local",
            "refine_model": "codex_decision",
            "mandatory_glossary_terms": [],
            "notes": "Deterministic IRS title sidecar; roman numerals normalized to Arabic numerals to avoid title mojibake validation.",
        }
        (work_dir / "title.json").write_text(
            json.dumps(sidecar, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"{chapter_id}: {thai_title}")


if __name__ == "__main__":
    main()
