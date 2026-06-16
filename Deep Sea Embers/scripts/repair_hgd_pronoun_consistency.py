from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
NOVEL_ROOT = REPO.parent
HGD = NOVEL_ROOT / "Horror Game Developers"
OUTPUT_ROOT = HGD / "05_Output"
REPORT_ROOT = HGD / "07_Reports"


SETH_DOMINANT_CHAPTERS = {
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

TARGETED_REPLACEMENTS = {
    "ch007": {
        "ฉัน... เพิ่งกินยาไปเองนะ": "ผม... เพิ่งกินยาไปเองนะ",
        "ฉันยืนไหว": "ผมยืนไหว",
        "ฉัน... รอดแล้ว": "ผม... รอดแล้ว",
        "ฉันไม่อยากฟัง": "ผมไม่อยากฟัง",
        "ปล่อยฉันไป": "ปล่อยผมไป",
        "ใช่ ฉันแน่ใจ": "ใช่ ผมแน่ใจ",
        "ทำไมฉันต้องอยาก": "ทำไมผมต้องอยาก",
        "รักษาโรคของฉัน": "รักษาโรคของผม",
        "พรากชีวิตฉัน": "พรากชีวิตผม",
    },
    "ch017": {
        "ฉัน... จะสลบตอนนี้ไม่ได้": "ผม... จะสลบตอนนี้ไม่ได้",
        "ฉัน... ทำสำเร็จไหม": "ผม... ทำสำเร็จไหม",
    },
}

PEER_ADDRESS_REPLACEMENTS = {
    "ch033": {
        "คุณ": "นาย",
        "เธอเห็นอะไร": "นายเห็นอะไร",
        "เธอไม่ผิดหรอก": "นายไม่ผิดหรอก",
        "ฉันว่าเธอพูดถูก": "ผมว่านายพูดถูก",
        "ผมว่าเธอพูดถูก": "ผมว่านายพูดถูก",
        "เชื่อฉันเถอะ": "เชื่อผมเถอะ",
    },
}


@dataclass
class RepairResult:
    chapter: str
    changed: bool
    before_counts: dict[str, int]
    after_counts: dict[str, int]
    replacements: list[str]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def count_pronouns(text: str) -> dict[str, int]:
    return {
        "ผม": text.count("ผม"),
        "ฉัน": text.count("ฉัน"),
        "คุณ": text.count("คุณ"),
        "นาย": text.count("นาย"),
        "เธอ": text.count("เธอ"),
    }


def chapter_path(chapter: str) -> Path:
    return OUTPUT_ROOT / chapter / f"{chapter}.md"


def backup_outputs() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = HGD / f"05_Output_backup_before_pronoun_repair_{stamp}"
    shutil.copytree(OUTPUT_ROOT, backup_root)
    return backup_root


def apply_replacements(chapter: str, text: str) -> tuple[str, list[str]]:
    replacements: list[str] = []

    if chapter in SETH_DOMINANT_CHAPTERS:
        changed = text.replace("ฉัน", "ผม")
        if changed != text:
            replacements.append("Seth-dominant chapter: ฉัน -> ผม")
            text = changed

    for source, target in TARGETED_REPLACEMENTS.get(chapter, {}).items():
        if source in text:
            text = text.replace(source, target)
            replacements.append(f"{source} -> {target}")

    for source, target in PEER_ADDRESS_REPLACEMENTS.get(chapter, {}).items():
        if source in text:
            text = text.replace(source, target)
            replacements.append(f"{source} -> {target}")

    return text, replacements


def repair_chapter(chapter: str) -> RepairResult:
    path = chapter_path(chapter)
    original = read(path)
    before = count_pronouns(original)
    repaired, replacements = apply_replacements(chapter, original)
    after = count_pronouns(repaired)
    changed = repaired != original
    if changed:
        write(path, repaired)
    return RepairResult(
        chapter=chapter,
        changed=changed,
        before_counts=before,
        after_counts=after,
        replacements=replacements,
    )


def build_report(results: list[RepairResult], backup_root: Path) -> str:
    changed = [result for result in results if result.changed]
    lines = [
        "# HGD Pronoun Consistency Repair",
        "",
        f"Created at: {datetime.now().isoformat(timespec='seconds')}",
        f"Backup path: `{backup_root}`",
        "",
        "## Root Cause",
        "",
        "- HGD had no Obsidian vault or durable pronoun policy note.",
        "- The HGD horror style profile and prompts preserved tone, UI, and glossary, but did not pin Seth Thorne's Thai first-person voice.",
        "- QA checked meaning and tone, but did not explicitly reject ผม/ฉัน drift or Kyle/Seth address drift.",
        "",
        "## Prevention Added",
        "",
        "- Added HGD Obsidian vault files and `02_Database_Views/HGD Pronoun Policy.md`.",
        "- Added pronoun policy to `RESEARCH_PROFILE.yaml`, `.system/style_profiles.yaml`, refinement prompt, and QA prompt.",
        "- Added deterministic guardrail coverage in the main repo for known high-risk published HGD chapters.",
        "",
        "## Repair Scope",
        "",
        "- Published MoonRead scope only: HGD `ch001-ch035`.",
        "- High-risk Seth-dominant chapters were repaired from `ฉัน` to `ผม`.",
        "- Mixed chapters received targeted repairs only.",
        "",
        "## Changed Chapters",
        "",
    ]
    if not changed:
        lines.append("No chapter text changed.")
    for result in changed:
        lines.append(f"### {result.chapter}")
        lines.append("")
        lines.append(f"- before: `{json.dumps(result.before_counts, ensure_ascii=False)}`")
        lines.append(f"- after: `{json.dumps(result.after_counts, ensure_ascii=False)}`")
        for replacement in result.replacements:
            lines.append(f"- {replacement}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    if not OUTPUT_ROOT.exists():
        raise SystemExit(f"Missing HGD output root: {OUTPUT_ROOT}")

    backup_root = backup_outputs()
    chapters = [f"ch{number:03d}" for number in range(1, 36)]
    results = [repair_chapter(chapter) for chapter in chapters if chapter_path(chapter).exists()]

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    report = build_report(results, backup_root)
    report_path = REPORT_ROOT / "hgd_pronoun_consistency_repair_20260616.md"
    write(report_path, report)
    print(f"backup={backup_root}")
    print(f"report={report_path}")
    print(f"changed={sum(1 for result in results if result.changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
