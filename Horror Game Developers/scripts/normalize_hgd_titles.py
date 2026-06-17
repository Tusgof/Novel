from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TITLE_MAP = {
    "Velora Art Museum": "พิพิธภัณฑ์ศิลปะเวลอรา",
    "Live Stream": "ไลฟ์สตรีม",
    "The lunatic with the sunglasses": "คนบ้าแว่นกันแดด",
    "The game that makes you scream": "เกมที่ทำให้กรีดร้อง",
    "Your account has been reinstated": "บัญชีของคุณถูกคืนสถานะแล้ว",
    "Return of the Jester": "การกลับมาของตัวตลก",
    "Masquerade ball": "งานเต้นรำสวมหน้ากาก",
    "The perfect piece": "ชิ้นงานสมบูรณ์แบบ",
    "Crying": "เสียงร้องไห้",
    "Little girl": "เด็กหญิงตัวน้อย",
    "Little Girl": "เด็กหญิงตัวน้อย",
    "App Update": "อัปเดตแอป",
    "Shepherd": "ผู้เลี้ยงแกะ",
    "Evolution": "วิวัฒนาการ",
    "Second Order": "ลำดับที่สอง",
    "The Conductor’s Trial": "บททดสอบของวาทยกร",
    "The Conductor's Trial": "บททดสอบของวาทยกร",
    "Guild Dinner": "มื้อค่ำของกิลด์",
    "First Trauma Patient": "ผู้ป่วยบาดแผลทางใจคนแรก",
    "Expedition": "การสำรวจ",
    "A Twisted Man": "ชายบิดเบี้ยว",
    "Expedition Squad": "หน่วยสำรวจ",
    "Silence": "ความเงียบ",
    "Butcher": "คนเชือด",
    "A Twisted Game": "เกมบิดเบี้ยว",
    "Escape": "หลบหนี",
    "Aftermath": "ผลพวง",
    "Game Developer Mode": "โหมดนักพัฒนาเกม",
    "New Project": "โปรเจกต์ใหม่",
}

HEADING_RE = re.compile(r"^\ufeff?#\s*(?:Chapter|ตอนที่)\s+\d+\s+-\s+(.+?)(\s+\[\d+\])?\s*$")


def normalize_heading(chapter_id: str, heading: str) -> str | None:
    match = HEADING_RE.match(heading.strip())
    if not match:
        return None
    raw_title = match.group(1).strip()
    suffix = match.group(2) or ""
    thai_title = TITLE_MAP.get(raw_title)
    if not thai_title:
        return None
    number = int(chapter_id[2:])
    return f"# ตอนที่ {number} - {thai_title}{suffix}"


def main() -> int:
    changed: list[str] = []
    missing_map: dict[str, str] = {}

    for number in range(36, 121):
        chapter_id = f"ch{number:03d}"
        output_path = ROOT / "05_Output" / chapter_id / f"{chapter_id}.md"
        if not output_path.exists():
            continue

        text = output_path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        lines = text.split("\n")
        new_heading = normalize_heading(chapter_id, lines[0])
        if not new_heading:
            if re.search(r"[A-Za-z]", lines[0]):
                missing_map[chapter_id] = lines[0]
            continue

        if lines[0] != new_heading:
            lines[0] = new_heading
            output_path.write_text("\n".join(lines), encoding="utf-8")
            changed.append(str(output_path.relative_to(ROOT)))

        title_path = ROOT / "04_Work" / chapter_id / "title.json"
        title_path.parent.mkdir(parents=True, exist_ok=True)
        title_payload = {
            "chapter_id": chapter_id,
            "thai_title": new_heading.replace("# ", "", 1),
            "source": "hgd_title_normalization_ch036_ch090",
        }
        title_path.write_text(json.dumps(title_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if missing_map:
        print("Missing title mappings:")
        for chapter_id, heading in missing_map.items():
            print(f"- {chapter_id}: {heading}")
        return 1

    print(f"normalized_hgd_titles: {len(changed)} output headings checked/updated; title sidecars written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
