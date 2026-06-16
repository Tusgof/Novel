from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
NOVEL_ROOT = REPO.parent
HGD_OUTPUT = NOVEL_ROOT / "Horror Game Developers" / "05_Output"
DEFAULT_EXPERIMENT_ROOT = REPO / "04_Work" / "_experiments" / "hgd_ai_format_sample_v6_17"

sys.path.insert(0, str(REPO))

from novel_pipeline.pipeline import validate_formatted_text  # noqa: E402


MARKDOWN_ONLY_RE = re.compile(r"^[\s*_`~\-—─]+$")
SIGNATURE_DROP_RE = re.compile(r"[\s\"'“”‘’\[\]\(\)（）*_`~.,!?;:，。！？；：…\-]+")
ADJACENT_PUNCTUATION = set("\"'“”‘’[]()（）*_`~.,!?;:，。！？；：…-—")
INLINE_ITALIC_RE = re.compile(r"(\*[^*\n]{1,80}\*)")
PANEL_RE = re.compile(r"(\*\*\[[^\]]+\]\*\*)")
SENTENCE_BOUNDARY_RE = re.compile(r"(.+?[.!?…。！？](?:[\"”']?)\s+)")


@dataclass
class ProjectionResult:
    chapter: str
    status: str
    source_path: str
    ai_sample_path: str
    projected_path: str
    validation_issues: list[str]
    semantic_warning_count_before: int
    semantic_warning_count_after: int
    error: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def split_heading(markdown: str) -> tuple[str, str]:
    lines = markdown.replace("\r\n", "\n").split("\n")
    if lines and lines[0].startswith("# "):
        return lines[0].strip(), "\n".join(lines[1:]).strip()
    return "", markdown.strip()


def paragraphs(markdown: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", markdown) if part.strip()]


def signature(text: str) -> str:
    return SIGNATURE_DROP_RE.sub("", text.lower())


def build_signature_map(text: str) -> tuple[str, list[int]]:
    chars: list[str] = []
    mapping: list[int] = []
    for index, char in enumerate(text):
        normalized = signature(char)
        if not normalized:
            continue
        for normalized_char in normalized:
            chars.append(normalized_char)
            mapping.append(index)
    return "".join(chars), mapping


def load_semantic_audit_module():
    path = REPO / "scripts" / "audit_hgd_semantic_format.py"
    spec = importlib.util.spec_from_file_location("audit_hgd_semantic_format_projector", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import semantic audit script at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_hgd_semantic_format_projector"] = module
    spec.loader.exec_module(module)
    return module


def semantic_warning_count(module, chapter: str, markdown: str) -> int:
    count = 0
    for index, paragraph in enumerate(module.paragraphs(markdown), start=1):
        count += len(module.audit_paragraph(chapter, index, paragraph))
    return count


def project_layout_from_original(original_body: str, ai_body: str) -> str:
    original_sig, original_map = build_signature_map(original_body)
    if not original_sig:
        return original_body.strip()

    cursor = 0
    previous_end = 0
    chunks: list[str] = []
    for ai_paragraph in paragraphs(ai_body):
        if MARKDOWN_ONLY_RE.match(ai_paragraph):
            continue
        para_sig = signature(ai_paragraph)
        if not para_sig:
            continue
        position = original_sig.find(para_sig, cursor)
        if position < 0:
            raise ValueError(f"Cannot project paragraph near: {ai_paragraph[:120]}")
        if position != cursor:
            raise ValueError(f"AI proposal skipped original content near: {ai_paragraph[:120]}")
        start = original_map[position]
        while start > previous_end and original_body[start - 1] in ADJACENT_PUNCTUATION:
            start -= 1
        next_position = position + len(para_sig)
        end = original_map[next_position - 1] + 1
        while end < len(original_body) and original_body[end] in ADJACENT_PUNCTUATION:
            end += 1
        chunk = original_body[start:end].strip()
        if chunk:
            chunks.append(chunk)
        cursor = next_position
        previous_end = end

    projected = "\n\n".join(chunks).strip()
    if signature(projected) != original_sig:
        raise ValueError("Projected layout did not preserve all original content")
    return projected


def split_leading_quote(paragraph: str) -> tuple[str, str] | None:
    if not paragraph.startswith(('"', "“")):
        return None
    close = '"' if paragraph.startswith('"') else "”"
    end = paragraph.find(close, 1)
    if end < 0 or end + 1 >= len(paragraph) or not paragraph[end + 1].isspace():
        return None
    return paragraph[: end + 1], paragraph[end + 1 :].strip()


def deterministic_safe_layout(original_body: str) -> str:
    chunks: list[str] = []
    for paragraph in paragraphs(original_body):
        quote_split = split_leading_quote(paragraph)
        if quote_split and len(paragraph) > 180:
            chunks.append(quote_split[0])
            paragraph = quote_split[1]
        candidate_parts = [paragraph]
        if len(paragraph) > 260 and " —" in paragraph:
            candidate_parts = [part.strip() for part in re.split(r"\s+(?=—)", paragraph) if part.strip()]
        expanded_parts: list[str] = []
        for part in candidate_parts:
            if len(part) > 260 and (' "' in part or " “" in part):
                expanded_parts.extend(split.strip() for split in re.split(r"\s+(?=[\"“])", part) if split.strip())
            else:
                expanded_parts.append(part)
        candidate_parts = expanded_parts
        expanded_parts = []
        for part in candidate_parts:
            if PANEL_RE.search(part) and not part.strip().startswith("**["):
                expanded_parts.extend(split.strip() for split in PANEL_RE.split(part) if split.strip())
            elif len(PANEL_RE.findall(part)) > 1:
                expanded_parts.extend(split.strip() for split in PANEL_RE.split(part) if split.strip())
            else:
                expanded_parts.append(part)
        candidate_parts = expanded_parts
        for part in candidate_parts:
            if part == "─────":
                chunks.append(part)
                continue
            italic_parts = split_inline_italic_safely(part)
            if len(part) > 220 and len(italic_parts) > 1:
                chunks.extend(italic_parts)
            elif len(part) > 320:
                chunks.extend(split_long_sentence_beats(part))
            else:
                chunks.append(part)

    projected = "\n\n".join(chunks).strip()
    if signature(projected) != signature(original_body):
        raise ValueError("Deterministic fallback did not preserve all original content")
    return projected


def split_inline_italic_safely(paragraph: str) -> list[str]:
    if "**" in paragraph or not INLINE_ITALIC_RE.search(paragraph):
        return [paragraph]
    return [part.strip() for part in INLINE_ITALIC_RE.split(paragraph) if part.strip()]


def split_long_sentence_beats(paragraph: str) -> list[str]:
    if len(paragraph) <= 320:
        return [paragraph]
    pieces: list[str] = []
    cursor = 0
    for match in SENTENCE_BOUNDARY_RE.finditer(paragraph):
        pieces.append(match.group(1).strip())
        cursor = match.end()
    tail = paragraph[cursor:].strip()
    if tail:
        pieces.append(tail)
    if len(pieces) < 2:
        return [paragraph]

    chunks: list[str] = []
    current = ""
    for piece in pieces:
        if current and len(current) + 1 + len(piece) > 260:
            chunks.append(current.strip())
            current = piece
        else:
            current = f"{current} {piece}".strip() if current else piece
    if current:
        chunks.append(current.strip())
    return chunks if len(chunks) > 1 else [paragraph]


def project_chapter(chapter: str, experiment_root: Path) -> ProjectionResult:
    audit_module = load_semantic_audit_module()
    source_path = HGD_OUTPUT / chapter / f"{chapter}.md"
    ai_sample_path = experiment_root / f"{chapter}.sample.md"
    projected_path = experiment_root / f"{chapter}.projected.md"
    before_count = 0

    try:
        original = read(source_path)
        ai_sample = read(ai_sample_path)
        heading, body = split_heading(original)
        _, ai_body = split_heading(ai_sample)
        before_count = semantic_warning_count(audit_module, chapter, original)
        fallback_note = ""
        try:
            projected_body = project_layout_from_original(body, ai_body)
            status_prefix = "valid"
        except ValueError as projection_error:
            projected_body = deterministic_safe_layout(body)
            fallback_note = f"AI projection failed; deterministic fallback used: {projection_error}"
            status_prefix = "fallback_valid"
        projected_body = deterministic_safe_layout(projected_body)
        projected = f"{heading}\n\n{projected_body}\n" if heading else f"{projected_body}\n"
        validation_issues = validate_formatted_text(projected_body, source_text=body)
        after_count = semantic_warning_count(audit_module, chapter, projected)
        projected_path.write_text(projected, encoding="utf-8")
        return ProjectionResult(
            chapter=chapter,
            status=status_prefix if not validation_issues else "invalid",
            source_path=str(source_path),
            ai_sample_path=str(ai_sample_path),
            projected_path=str(projected_path),
            validation_issues=validation_issues,
            semantic_warning_count_before=before_count,
            semantic_warning_count_after=after_count,
            error=fallback_note,
        )
    except Exception as exc:  # noqa: BLE001 - projection report should record per-chapter failures.
        return ProjectionResult(
            chapter=chapter,
            status="failed",
            source_path=str(source_path),
            ai_sample_path=str(ai_sample_path),
            projected_path=str(projected_path),
            validation_issues=[],
            semantic_warning_count_before=before_count,
            semantic_warning_count_after=before_count,
            error=str(exc)[:1000],
        )


def render_report(results: list[ProjectionResult], experiment_root: Path) -> str:
    lines = [
        "# HGD AI Layout Projection Report",
        "",
        "Scope: sample-only projection. AI sample layout is used as a proposal; projected text is reconstructed from original chapter characters.",
        "No final output or MoonRead generated content is modified.",
        f"Experiment root: `{experiment_root}`",
        "",
        "## Summary",
        "",
        "| chapter | status | warnings before | warnings after | validation issues |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for result in results:
        issues = ", ".join(result.validation_issues) if result.validation_issues else "-"
        if result.error and result.status == "failed":
            issues = f"ERROR: {result.error}"
        elif result.error:
            issues = f"{issues}; note: {result.error}" if issues != "-" else f"note: {result.error}"
        lines.append(
            f"| {result.chapter} | {result.status} | {result.semantic_warning_count_before} | "
            f"{result.semantic_warning_count_after} | {issues} |"
        )

    lines.extend(
        [
            "",
            "## Status Meaning",
            "",
            "- `valid`: AI layout projected cleanly onto original text and validation passed.",
            "- `fallback_valid`: AI layout was rejected, but deterministic original-text fallback validation passed.",
            "- `invalid`: projected/fallback text was produced but validation found issues.",
            "- `failed`: neither AI projection nor deterministic fallback produced usable text.",
            "",
            "## Safety Rule",
            "",
            "- Apply only projected files that validate against the original body.",
            "- Do not apply a chapter when status is `invalid` or `failed`.",
            "- This report does not approve broad HGD repair by itself; representative projected files still need review.",
            "",
            "## Files",
            "",
        ]
    )
    for result in results:
        lines.append(f"- {result.chapter}: `{result.projected_path}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Project HGD AI layout samples onto original chapter text.")
    parser.add_argument("--chapters", nargs="+", default=["ch001", "ch014", "ch022", "ch035"])
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    args = parser.parse_args()

    args.experiment_root.mkdir(parents=True, exist_ok=True)
    results = [project_chapter(chapter, args.experiment_root) for chapter in args.chapters]
    (args.experiment_root / "projection_summary.json").write_text(
        json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = render_report(results, args.experiment_root)
    report_path = args.experiment_root / "projection_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(report_path)
    if any(result.status in {"failed", "invalid"} for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
