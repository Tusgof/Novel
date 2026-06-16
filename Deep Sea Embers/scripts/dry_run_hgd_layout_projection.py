from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
NOVEL_ROOT = REPO.parent
HGD_OUTPUT = NOVEL_ROOT / "Horror Game Developers" / "05_Output"
DEFAULT_EXPERIMENT_ROOT = REPO / "04_Work" / "_experiments" / "hgd_layout_projection_dry_run_v6_17"

sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from novel_pipeline.pipeline import validate_formatted_text  # noqa: E402

import project_hgd_ai_layout_sample as projection  # noqa: E402


@dataclass
class DryRunResult:
    chapter: str
    status: str
    source_path: str
    output_path: str
    method: str
    validation_issues: list[str]
    semantic_warning_count_before: int
    semantic_warning_count_after: int
    error: str = ""


def load_semantic_audit_module():
    path = REPO / "scripts" / "audit_hgd_semantic_format.py"
    spec = importlib.util.spec_from_file_location("audit_hgd_semantic_format_dry_run", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import semantic audit script at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_hgd_semantic_format_dry_run"] = module
    spec.loader.exec_module(module)
    return module


def semantic_warning_count(module, chapter: str, markdown: str) -> int:
    count = 0
    for index, paragraph in enumerate(module.paragraphs(markdown), start=1):
        count += len(module.audit_paragraph(chapter, index, paragraph))
    return count


def project_chapter(chapter: str, experiment_root: Path, sample_root: Path) -> DryRunResult:
    audit_module = load_semantic_audit_module()
    source_path = HGD_OUTPUT / chapter / f"{chapter}.md"
    output_path = experiment_root / chapter / f"{chapter}.md"
    before_count = 0
    method = "deterministic_fallback"

    try:
        original = projection.read(source_path)
        heading, body = projection.split_heading(original)
        before_count = semantic_warning_count(audit_module, chapter, original)
        sample_path = sample_root / f"{chapter}.sample.md"
        if sample_path.exists():
            _, ai_body = projection.split_heading(projection.read(sample_path))
            try:
                projected_body = projection.project_layout_from_original(body, ai_body)
                method = "ai_layout_projection"
            except ValueError:
                projected_body = projection.deterministic_safe_layout(body)
                method = "deterministic_fallback_after_ai_reject"
        else:
            projected_body = projection.deterministic_safe_layout(body)
        projected = f"{heading}\n\n{projected_body}\n" if heading else f"{projected_body}\n"
        validation_issues = validate_formatted_text(projected_body, source_text=body)
        after_count = semantic_warning_count(audit_module, chapter, projected)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(projected, encoding="utf-8")
        return DryRunResult(
            chapter=chapter,
            status="valid" if not validation_issues else "invalid",
            source_path=str(source_path),
            output_path=str(output_path),
            method=method,
            validation_issues=validation_issues,
            semantic_warning_count_before=before_count,
            semantic_warning_count_after=after_count,
        )
    except Exception as exc:  # noqa: BLE001 - report chapter-level failure.
        return DryRunResult(
            chapter=chapter,
            status="failed",
            source_path=str(source_path),
            output_path=str(output_path),
            method=method,
            validation_issues=[],
            semantic_warning_count_before=before_count,
            semantic_warning_count_after=before_count,
            error=str(exc)[:1000],
        )


def render_report(results: list[DryRunResult], experiment_root: Path) -> str:
    total_before = sum(result.semantic_warning_count_before for result in results)
    total_after = sum(result.semantic_warning_count_after for result in results)
    invalid = [result for result in results if result.status != "valid"]
    lines = [
        "# HGD Layout Projection Dry Run",
        "",
        "Scope: dry-run only. No final output or MoonRead generated content is modified.",
        f"Experiment root: `{experiment_root}`",
        "",
        "## Summary",
        "",
        f"- chapters: {len(results)}",
        f"- valid chapters: {len(results) - len(invalid)}",
        f"- invalid/failed chapters: {len(invalid)}",
        f"- semantic warnings before: {total_before}",
        f"- semantic warnings after: {total_after}",
        "",
        "| chapter | status | method | warnings before | warnings after | validation issues |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for result in results:
        issues = ", ".join(result.validation_issues) if result.validation_issues else "-"
        if result.error:
            issues = f"ERROR: {result.error}"
        lines.append(
            f"| {result.chapter} | {result.status} | {result.method} | "
            f"{result.semantic_warning_count_before} | {result.semantic_warning_count_after} | {issues} |"
        )
    lines.extend(
        [
            "",
            "## Safety Rule",
            "",
            "- This report does not approve publication.",
            "- Apply only after representative dry-run chapters are read and all validation issues are resolved.",
            "- The final apply step must write backups before modifying HGD `05_Output`.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run HGD layout projection across published chapters.")
    parser.add_argument("--first", type=int, default=1)
    parser.add_argument("--last", type=int, default=35)
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument(
        "--sample-root",
        type=Path,
        default=REPO / "04_Work" / "_experiments" / "hgd_ai_format_sample_v6_17",
    )
    args = parser.parse_args()

    chapters = [f"ch{number:03d}" for number in range(args.first, args.last + 1)]
    results = [project_chapter(chapter, args.experiment_root, args.sample_root) for chapter in chapters]
    args.experiment_root.mkdir(parents=True, exist_ok=True)
    (args.experiment_root / "summary.json").write_text(
        json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = render_report(results, args.experiment_root)
    report_path = args.experiment_root / "report.md"
    report_path.write_text(report, encoding="utf-8")
    print(report_path)
    if any(result.status != "valid" for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
