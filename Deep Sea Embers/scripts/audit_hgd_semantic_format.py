from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
NOVEL_ROOT = REPO.parent
HGD_OUTPUT = NOVEL_ROOT / "Horror Game Developers" / "05_Output"
DEFAULT_REPORT = REPO / "07_Reports" / "hgd_semantic_format_audit_v6_17.md"

INLINE_ITALIC = re.compile(r"(?<!^)\*[^*\n]{1,80}\*(?!$)")
QUOTE_MARK = re.compile(r"[\"“”]")
PANEL = re.compile(r"\*\*\[[^\]]+\]\*\*")
SENTENCE_END = re.compile(r"[.!?…。！？]|[”\"]")


@dataclass(frozen=True)
class Finding:
    chapter: str
    paragraph: int
    kind: str
    length: int
    excerpt: str


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def paragraphs(markdown: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", markdown) if part.strip()]


def excerpt(text: str, limit: int = 160) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def audit_paragraph(chapter: str, index: int, paragraph: str) -> list[Finding]:
    if paragraph.startswith("#"):
        return []

    findings: list[Finding] = []
    length = len(paragraph)
    line_count = paragraph.count("\n") + 1
    sentence_count = len(SENTENCE_END.findall(paragraph))
    quote_count = len(QUOTE_MARK.findall(paragraph))

    if length > 280 and INLINE_ITALIC.search(paragraph):
        findings.append(Finding(chapter, index, "inline_italic_in_long_paragraph", length, excerpt(paragraph)))

    if length > 260 and quote_count >= 2 and not (paragraph.startswith(("“", '"')) and paragraph.endswith(("”", '"'))):
        findings.append(Finding(chapter, index, "dialogue_or_quote_embedded_in_long_paragraph", length, excerpt(paragraph)))

    if length > 280 and sentence_count >= 5:
        findings.append(Finding(chapter, index, "many_beats_in_one_paragraph", length, excerpt(paragraph)))

    if PANEL.search(paragraph) and line_count > 1:
        findings.append(Finding(chapter, index, "system_panel_not_standalone", length, excerpt(paragraph)))

    return findings


def audit_outputs(root: Path = HGD_OUTPUT, *, first: int = 1, last: int = 35) -> list[Finding]:
    findings: list[Finding] = []
    for number in range(first, last + 1):
        chapter = f"ch{number:03d}"
        path = root / chapter / f"{chapter}.md"
        if not path.exists():
            findings.append(Finding(chapter, 0, "missing_output", 0, str(path)))
            continue
        for index, paragraph in enumerate(paragraphs(read(path)), start=1):
            findings.extend(audit_paragraph(chapter, index, paragraph))
    return findings


def render_report(findings: list[Finding], *, first: int, last: int) -> str:
    lines = [
        "# HGD Semantic Format Audit",
        "",
        "Scope: Horror Game Developer output formatting warnings.",
        f"Range: ch{first:03d}-ch{last:03d}",
        "",
        "This is a warning-only audit. It does not prove content is wrong and does not modify output.",
        "",
        "## Summary",
        "",
        f"- findings: {len(findings)}",
    ]

    by_kind: dict[str, int] = {}
    by_chapter: dict[str, int] = {}
    for finding in findings:
        by_kind[finding.kind] = by_kind.get(finding.kind, 0) + 1
        by_chapter[finding.chapter] = by_chapter.get(finding.chapter, 0) + 1

    lines.extend(["", "## Findings By Kind", ""])
    if by_kind:
        for kind, count in sorted(by_kind.items()):
            lines.append(f"- {kind}: {count}")
    else:
        lines.append("- none")

    lines.extend(["", "## Findings By Chapter", ""])
    if by_chapter:
        for chapter, count in sorted(by_chapter.items()):
            lines.append(f"- {chapter}: {count}")
    else:
        lines.append("- none")

    lines.extend(["", "## Detail", ""])
    if findings:
        lines.append("| chapter | paragraph | kind | length | excerpt |")
        lines.append("| --- | ---: | --- | ---: | --- |")
        for finding in findings:
            safe_excerpt = finding.excerpt.replace("|", "\\|")
            lines.append(
                f"| {finding.chapter} | {finding.paragraph} | {finding.kind} | {finding.length} | {safe_excerpt} |"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `inline_italic_in_long_paragraph`: a thought/sound marker may need its own beat.",
            "- `dialogue_or_quote_embedded_in_long_paragraph`: direct speech or quoted sound may be merged into narration.",
            "- `many_beats_in_one_paragraph`: paragraph may be readable but still too rhythmically dense for `good format.md`.",
            "- `system_panel_not_standalone`: game/system panel is not isolated as its own block.",
            "",
            "Use these findings to choose AI-format sample chapters. Do not apply mechanical splitting blindly.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit HGD semantic formatting warnings.")
    parser.add_argument("--root", type=Path, default=HGD_OUTPUT)
    parser.add_argument("--first", type=int, default=1)
    parser.add_argument("--last", type=int, default=35)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    findings = audit_outputs(root=args.root, first=args.first, last=args.last)
    report = render_report(findings, first=args.first, last=args.last)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print(f"hgd_semantic_format_audit: {len(findings)} findings")
    print(args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
