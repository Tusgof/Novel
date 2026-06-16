from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
NOVEL_ROOT = REPO.parent
HGD_ROOT = NOVEL_ROOT / "Horror Game Developers"
HGD_OUTPUT = HGD_ROOT / "05_Output"
DEFAULT_EXPERIMENT_ROOT = REPO / "04_Work" / "_experiments" / "hgd_ai_format_sample_v6_17"
STRICT_HGD_FORMATTING_CONTRACT = """

## HGD Sample Strict Preservation Contract
- This sample is layout-only. Preserve the exact original wording and punctuation.
- Do not normalize straight quotes to curly quotes or curly quotes to straight quotes.
- Do not change sound effects, repeated syllables, tildes, dashes, ellipses, exclamation marks, or question marks.
- Do not change Thai particles, pronouns, names, item labels, bracket text, or system text.
- You may only add/remove line breaks and add Markdown emphasis markers (`*`, `**`) around text that already exists.
- If a line cannot be safely reformatted without changing characters, leave that line unchanged.
""".strip()

sys.path.insert(0, str(REPO))

from novel_pipeline.config import load_app_config  # noqa: E402
from novel_pipeline.pipeline import validate_formatted_text  # noqa: E402
from novel_pipeline.prompts import PromptStore  # noqa: E402
from novel_pipeline.providers.base import ProviderRequest, ProviderRunner, ensure_provider_response  # noqa: E402
from novel_pipeline.stages.format import cleanup_provider_formatted_text  # noqa: E402


@dataclass
class SampleResult:
    chapter: str
    status: str
    provider: str
    model: str
    duration_seconds: float
    source_path: str
    sample_path: str
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


def load_semantic_audit_module():
    path = REPO / "scripts" / "audit_hgd_semantic_format.py"
    spec = importlib.util.spec_from_file_location("audit_hgd_semantic_format_runtime", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import semantic audit script at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_hgd_semantic_format_runtime"] = module
    spec.loader.exec_module(module)
    return module


def semantic_warning_count(module, chapter: str, markdown: str) -> int:
    count = 0
    for index, paragraph in enumerate(module.paragraphs(markdown), start=1):
        count += len(module.audit_paragraph(chapter, index, paragraph))
    return count


def strict_layout_signature(text: str) -> str:
    """Ignore only whitespace and Markdown emphasis markers added for layout."""
    return "".join(char for char in text if not char.isspace() and char not in "*_`")


def strict_layout_preservation_issues(formatted_text: str, source_text: str) -> list[str]:
    if strict_layout_signature(formatted_text) != strict_layout_signature(source_text):
        return ["strict layout preservation changed punctuation, wording, or sound effects"]
    return []


def format_sample_chapter(*, chapter: str, experiment_root: Path, timeout_seconds: int) -> SampleResult:
    config = load_app_config(REPO / ".system" / "config.yaml")
    routing = config.stage_routing_for("formatting")
    provider = config.provider_for_stage("formatting")
    model = routing.model or config.stage_model_for("formatting") or provider.default_model
    prompt_store = PromptStore(HGD_ROOT / "prompts")
    audit_module = load_semantic_audit_module()

    source_path = HGD_OUTPUT / chapter / f"{chapter}.md"
    sample_path = experiment_root / f"{chapter}.sample.md"
    experiment_root.mkdir(parents=True, exist_ok=True)

    original = read(source_path)
    heading, body = split_heading(original)
    prompt = prompt_store.render("formatting.md", text=body) + "\n\n" + STRICT_HGD_FORMATTING_CONTRACT + "\n"
    before_count = semantic_warning_count(audit_module, chapter, original)
    started = time.perf_counter()

    try:
        response = ProviderRunner(provider).run_with_retry(
            ProviderRequest(
                prompt=prompt,
                provider=provider.name,
                stage="formatting_sample",
                model=model,
                cwd=REPO,
                timeout_seconds=timeout_seconds or routing.timeout_seconds,
            ),
            require_stdout=True,
            max_attempts=1,
        )
        ensure_provider_response(response)
        formatted_body = cleanup_provider_formatted_text(response.stdout)
        sample = f"{heading}\n\n{formatted_body.strip()}\n" if heading else f"{formatted_body.strip()}\n"
        validation_issues = validate_formatted_text(formatted_body, source_text=body)
        validation_issues.extend(strict_layout_preservation_issues(formatted_body, body))
        after_count = semantic_warning_count(audit_module, chapter, sample)
        sample_path.write_text(sample, encoding="utf-8")
        status = "valid" if not validation_issues else "invalid"
        return SampleResult(
            chapter=chapter,
            status=status,
            provider=provider.name,
            model=model or "",
            duration_seconds=response.duration_seconds,
            source_path=str(source_path),
            sample_path=str(sample_path),
            validation_issues=validation_issues,
            semantic_warning_count_before=before_count,
            semantic_warning_count_after=after_count,
        )
    except Exception as exc:  # noqa: BLE001 - sample report must record provider/runtime failures.
        return SampleResult(
            chapter=chapter,
            status="failed",
            provider=provider.name,
            model=model or "",
            duration_seconds=time.perf_counter() - started,
            source_path=str(source_path),
            sample_path=str(sample_path),
            validation_issues=[],
            semantic_warning_count_before=before_count,
            semantic_warning_count_after=before_count,
            error=str(exc)[:1000],
        )


def render_report(results: list[SampleResult], experiment_root: Path) -> str:
    lines = [
        "# HGD AI Format Sample Repair Report",
        "",
        "Scope: sample-only AI formatting for V6.17. No final output or MoonRead generated content is modified.",
        f"Experiment root: `{experiment_root}`",
        "",
        "## Summary",
        "",
        "| chapter | status | provider | model | warnings before | warnings after | validation issues |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for result in results:
        issues = ", ".join(result.validation_issues) if result.validation_issues else "-"
        if result.error:
            issues = f"ERROR: {result.error}"
        lines.append(
            "| "
            f"{result.chapter} | {result.status} | {result.provider} | {result.model} | "
            f"{result.semantic_warning_count_before} | {result.semantic_warning_count_after} | {issues} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `valid` means the AI sample passed deterministic no-content-change validation and strict layout-preservation validation.",
            "- `invalid` means the provider returned text, but validation found content drift, punctuation drift, wording drift, sound-effect drift, or leakage.",
            "- `failed` means the provider/sample runtime failed before a usable sample was produced.",
            "- Even valid samples still require human/Codex reading before applying to all HGD chapters.",
            "",
            "## Safety Conclusion",
            "",
        ]
    )
    invalid = [result for result in results if result.status != "valid"]
    if invalid:
        invalid_chapters = ", ".join(result.chapter for result in invalid)
        lines.extend(
            [
                f"- Direct AI formatting is not safe for broad apply yet; invalid sample chapters: {invalid_chapters}.",
                "- The next implementation should treat AI output as a layout proposal only, then reconstruct the final text from the original chapter characters so wording, punctuation, and sound effects cannot drift.",
            ]
        )
    else:
        lines.append("- All samples passed validation, but broad apply still requires source/output review before publication.")
    lines.extend(
        [
            "",
            "## Files",
            "",
        ]
    )
    for result in results:
        lines.append(f"- {result.chapter}: `{result.sample_path}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create sample-only HGD AI formatting repairs.")
    parser.add_argument("--chapters", nargs="+", default=["ch001", "ch014", "ch022", "ch035"])
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()

    results = [
        format_sample_chapter(chapter=chapter, experiment_root=args.experiment_root, timeout_seconds=args.timeout_seconds)
        for chapter in args.chapters
    ]
    args.experiment_root.mkdir(parents=True, exist_ok=True)
    (args.experiment_root / "summary.json").write_text(
        json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = render_report(results, args.experiment_root)
    report_path = args.experiment_root / "report.md"
    report_path.write_text(report, encoding="utf-8")
    print(report_path)

    if any(result.status == "failed" for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
