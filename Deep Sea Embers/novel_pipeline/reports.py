from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import re
import subprocess
from typing import Any

from novel_pipeline.artifacts import batch_glossary_scan_artifact_path
from novel_pipeline.files import atomic_write_text, read_text_if_exists
from novel_pipeline.glossary_support import load_glossary_index, parse_glossary_note
from novel_pipeline.ledger import RunLedger
from novel_pipeline.preflight import build_preflight_summary
from novel_pipeline.pipeline import (
    _load_chapter_source_and_blocks,
    _resolve_glossary_subset,
    inspect_block_command,
    status_run,
    validate_formatted_text,
)
from novel_pipeline.stages.glossary import (
    _blocked_exact_terms,
    _dedupe_candidates,
    _historical_rejected_terms,
    _is_obvious_noise_candidate,
    _load_glossary_note_records as _load_scan_note_records,
    _noise_anchor_terms,
    _note_bucket as _scan_note_bucket,
    _prune_substring_fragment_candidates,
    build_glossary_scan_queue,
)
from novel_pipeline.text_utils import extract_candidate_terms

_HAN_RE = re.compile(r"[\u4e00-\u9fff]")
_WRONG_GLOSSARY_VARIANTS: tuple[str, ...] = (
    "ดันแคน เอบนอร์มัล",
    "ดันแคน แอบนอร์มัล",
    "เอบนอร์มัล",
    "แอบนอร์มัล",
)


def _reports_dir(config: Any) -> Path:
    workspace = getattr(config, "workspace", None)
    root = getattr(workspace, "root", None)
    if isinstance(root, Path):
        return root / "07_Reports"
    output = getattr(workspace, "output", None)
    if isinstance(output, Path):
        return output.parent / "07_Reports"
    return Path("07_Reports")


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return slug.strip("_") or "report"


def _stable_report_path(
    *,
    config: Any,
    kind: str,
    run_id: str | None,
    chapter_ids: list[str] | None = None,
    output: Path | None = None,
) -> Path:
    if output is not None:
        return output
    reports_dir = _reports_dir(config)
    if run_id is None:
        if chapter_ids:
            chapter_slug = "-".join(chapter_ids)
            return reports_dir / f"{kind}_{_slug(chapter_slug)}.md"
        return reports_dir / f"{kind}.md"
    if chapter_ids:
        chapter_slug = "-".join(chapter_ids)
        return reports_dir / f"{kind}_{_slug(run_id)}_{_slug(chapter_slug)}.md"
    return reports_dir / f"{kind}_{_slug(run_id)}.md"


def _comma_list(values: list[str] | tuple[str, ...] | None) -> str:
    items = [value for value in (values or ()) if value]
    return ", ".join(items) if items else "none"


def _relative_report_path(path: Path, anchor: Path | None) -> str:
    if anchor is not None:
        try:
            return str(path.relative_to(anchor))
        except ValueError:
            pass
    return str(path)


def _git_capture(workspace_root: Path, *args: str) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(workspace_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
    output = (completed.stdout or completed.stderr or "").strip()
    return completed.returncode == 0, output


def _note_record_from_path(path: Path) -> dict[str, Any] | None:
    entry = parse_glossary_note(path)
    if entry is None:
        return None
    status = str(entry.status or "proposed").strip().lower() or "proposed"
    path_parts = {part.lower() for part in path.parts}
    is_quarantine = "quarantine" in path_parts
    return {
        "original_term": entry.original_term,
        "thai_term": entry.thai_term,
        "status": status,
        "is_quarantine": is_quarantine,
        "path": path,
        "aliases": list(entry.aliases),
    }


def _load_glossary_note_records(config: Any) -> list[dict[str, Any]]:
    glossary_dir = config.workspace.glossary_dir
    records: list[dict[str, Any]] = []
    for path in sorted(glossary_dir.rglob("*.md")):
        record = _note_record_from_path(path)
        if record is not None:
            records.append(record)
    return records


def _note_bucket(note: dict[str, Any]) -> str:
    if note.get("is_quarantine"):
        return "quarantine"
    status = str(note.get("status") or "proposed")
    if status in {"approved", "rejected", "deprecated", "proposed"}:
        return status
    return "proposed"


def _render_note_lines(
    *,
    notes: list[dict[str, Any]],
    anchor: Path | None,
) -> list[str]:
    lines: list[str] = []
    for note in notes:
        aliases = note.get("aliases") or []
        alias_text = _comma_list([str(alias) for alias in aliases]) if aliases else "none"
        status = note.get("status") or "unknown"
        path_text = _relative_report_path(note["path"], anchor)
        marker_label = "bucket"
        marker_value = _note_bucket(note)
        lines.append(
            f"- {note['original_term']} | {note['thai_term'] or 'none'} | {status} | {path_text} | aliases: {alias_text} | {marker_label}: {marker_value}"
        )
    if not lines:
        lines.append("- none")
    return lines


def _scan_glossary_scan_artifact(config: Any, run_id: str | None) -> tuple[str, Path | None, list[dict[str, Any]]]:
    if run_id is None:
        return "not requested", None, []
    path = batch_glossary_scan_artifact_path(config.workspace.work, run_id)
    raw = read_text_if_exists(path)
    if raw is None:
        return "missing", path, []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return "invalid", path, []
    items = data.get("items")
    if not isinstance(items, list):
        return "invalid", path, []
    return "present", path, [item for item in items if isinstance(item, dict)]


def _render_glossary_conflicts_markdown(
    *,
    run_id: str | None,
    notes: list[dict[str, Any]],
    scan_status: str,
    scan_path: Path | None,
    approved_count: int,
    proposed_count: int,
    rejected_count: int,
    deprecated_count: int,
    quarantine_count: int,
    approved_lines: list[str],
    proposed_lines: list[str],
    rejected_lines: list[str],
    deprecated_lines: list[str],
    quarantine_lines: list[str],
    alias_collision_lines: list[str],
    source_surface_collision_lines: list[str],
    approved_overlap_lines: list[str],
    approved_nonapproved_overlap_lines: list[str],
    exact_scan_lines: list[str],
    noisy_scan_lines: list[str],
) -> str:
    lines: list[str] = [
        f"# Glossary Conflicts Report - {run_id or 'current'}",
        "",
        "## Summary",
        f"- glossary_note_count: {len(notes)}",
        f"- batch_scan_artifact: {scan_status}",
        f"- batch_scan_path: {_relative_report_path(scan_path, None) if scan_path is not None else 'none'}",
        f"- approved_terms_count: {approved_count}",
        f"- proposed_terms_count: {proposed_count}",
        f"- rejected_terms_count: {rejected_count}",
        f"- deprecated_terms_count: {deprecated_count}",
        f"- quarantine_terms_count: {quarantine_count}",
        "",
        "## Approved Terms",
        *approved_lines,
        "",
        "## Proposed Terms",
        *proposed_lines,
        "",
        "## Rejected Terms",
        *rejected_lines,
        "",
        "## Deprecated Terms",
        *deprecated_lines,
        "",
        "## Quarantine Terms",
        *quarantine_lines,
        "",
        "## Alias Collisions",
        *alias_collision_lines,
        "",
        "## Source Surface Collisions",
        *source_surface_collision_lines,
        "",
        "## Approved-vs-Approved Overlaps",
        *approved_overlap_lines,
        "",
        "## Approved-vs-Nonapproved Overlaps",
        *approved_nonapproved_overlap_lines,
        "",
        "## Scan Candidate Exact Matches",
        *exact_scan_lines,
        "",
        "## Scan Candidate Noisy Prefix/Suffix Matches",
        *noisy_scan_lines,
    ]
    return "\n".join(lines).rstrip() + "\n"


def _render_glossary_audit_markdown(*, run_id: str, chapter_results: list[dict[str, Any]]) -> str:
    lines: list[str] = [
        f"# Glossary Audit Report - {run_id}",
        "",
        "## Chapters",
    ]
    for chapter in chapter_results:
        lines.extend(
            [
                "",
                f"### {chapter['chapter_id']}",
                f"- output: {chapter['output_path']}",
                f"- exists: {'yes' if chapter['exists'] else 'no'}",
                f"- subset_terms_count: {len(chapter.get('expected_terms') or [])}",
            ]
        )
        if chapter.get("source_error"):
            lines.append(f"- source_error: {chapter['source_error']}")
        lines.append(f"- expected approved glossary terms: {_comma_list(chapter.get('expected_terms'))}")
        lines.append(f"- missing thai terms in final output: {_comma_list(chapter.get('missing_thai_terms'))}")
        lines.append(
            f"- glossary subset source terms with missing thai output: {_comma_list(chapter.get('subset_terms_not_found'))}"
        )
        lines.append(f"- suspicious wrong variants: {_comma_list(chapter.get('wrong_variants'))}")
    return "\n".join(lines).rstrip() + "\n"


def _render_glossary_guard_markdown(*, run_id: str, chapter_results: list[dict[str, Any]]) -> str:
    lines: list[str] = [
        f"# Glossary Guard Verification Report - {run_id}",
        "",
        "## Chapters",
    ]
    for chapter in chapter_results:
        lines.extend(
            [
                "",
                f"### {chapter['chapter_id']}",
                f"- raw_deterministic_candidates: {chapter['raw_count']}",
                f"- filtered_candidates: {chapter['filtered_count']}",
                f"- removed_candidates: {chapter['removed_count']}",
                f"- removed_by_blocked_exact: {_comma_list(chapter.get('removed_blocked_exact'))}",
                f"- removed_by_noisy_wrapper: {_comma_list(chapter.get('removed_noisy'))}",
                f"- removed_by_substring_prune: {_comma_list(chapter.get('removed_substring'))}",
                f"- kept_candidates: {_comma_list(chapter.get('kept_terms'))}",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_preflight_markdown(*, summary: dict[str, Any]) -> str:
    research = summary.get("research_readiness") or {}
    git_info = summary.get("git") or {}
    provider_rows: list[str] = []
    for item in summary.get("providers") or []:
        provider_rows.append(
            "| "
            + " | ".join(
                [
                    str(item.get("provider") or ""),
                    str(item.get("status") or ""),
                    str(item.get("resolved_path") or ""),
                    str(item.get("prompt_transport") or ""),
                    _comma_list(item.get("stages") or []),
                    str(item.get("working_dir") or "none"),
                ]
            )
            + " |"
        )
    if not provider_rows:
        provider_rows.append("| none | blocked | none | none | none | none |")

    lines: list[str] = [
        "# Preflight Report",
        "",
        "## Summary",
        f"- status: {summary.get('status', 'unknown')}",
        f"- workspace_root: {summary.get('workspace_root', '')}",
        f"- config_path: {summary.get('config_path', '')}",
        f"- next_safe_action: {summary.get('next_safe_action', 'none')}",
        "",
        "## Providers",
        "| provider | status | resolved_path | prompt_transport | stages | working_dir |",
        "| --- | --- | --- | --- | --- | --- |",
        *provider_rows,
        "",
        "## Research Readiness",
        f"- status: {research.get('status', 'missing')}",
        f"- readiness: {research.get('readiness', 'blocked')}",
        f"- bounded_translation_ready: {'yes' if research.get('bounded_translation_ready') else 'no'}",
        f"- translation_ready: {'yes' if research.get('translation_ready') else 'no'}",
        f"- missing_fields: {_comma_list(research.get('missing_fields') or [])}",
        f"- warnings: {_comma_list(research.get('warnings') or [])}",
        f"- blocking_reasons: {_comma_list(research.get('blocking_reasons') or [])}",
        f"- next_safe_action: {research.get('next_safe_action', 'none')}",
        "",
        "## Git Guardrails",
        f"- available: {'yes' if git_info.get('available') else 'no'}",
        f"- in_work_tree: {'yes' if git_info.get('in_work_tree') else 'no'}",
        f"- branch: {git_info.get('branch') or 'none'}",
        f"- head: {git_info.get('head') or 'none'}",
        f"- origin: {git_info.get('origin') or 'none'}",
        f"- working_tree: {'clean' if git_info.get('clean') else 'dirty'}",
        f"- git_warnings: {_comma_list(git_info.get('warnings') or [])}",
        f"- ignored_generated_changes: {_comma_list(git_info.get('ignored_generated_changes') or [])}",
        "",
        "## Workspace",
        f"- missing_directories: {_comma_list(summary.get('missing_directories') or [])}",
        f"- warnings: {_comma_list(summary.get('warnings') or [])}",
        f"- blocking_reasons: {_comma_list(summary.get('blocking_reasons') or [])}",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _render_recovery_drill_markdown(
    *,
    summary: dict[str, Any],
    checks: list[dict[str, str]],
    canonical_rows: list[dict[str, str]],
    runtime_rows: list[dict[str, str]],
) -> str:
    lines: list[str] = [
        "# Recovery Drill Report",
        "",
        "## Summary",
        f"- overall_status: {summary.get('overall_status', 'unknown')}",
        f"- workspace_root: {summary.get('workspace_root', '')}",
        f"- branch: {summary.get('branch') or 'none'}",
        f"- head: {summary.get('head') or 'none'}",
        f"- origin: {summary.get('origin') or 'none'}",
        f"- next_safe_action: {summary.get('next_safe_action', 'none')}",
        "",
        "## Acceptance Checks",
        "| check | status | detail |",
        "| --- | --- | --- |",
    ]
    for item in checks:
        lines.append(f"| {item['check']} | {item['status']} | {item['detail']} |")

    lines.extend(
        [
            "",
            "## Canonical Docs",
            "| path | tracked | restorable_from_head | detail |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in canonical_rows:
        lines.append(
            f"| {row['path']} | {row['tracked']} | {row['restorable_from_head']} | {row['detail']} |"
        )

    lines.extend(
        [
            "",
            "## Runtime Ignore Policy",
            "| path | ignored | tracked_entries | detail |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for row in runtime_rows:
        lines.append(
            f"| {row['path']} | {row['ignored']} | {row['tracked_entries']} | {row['detail']} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_checkpoint_markdown(*, run_id: str, summary: dict[str, Any]) -> str:
    lines: list[str] = [
        f"# Checkpoint Report - {run_id}",
        "",
        "## Run Summary",
        f"- total_records: {summary.get('total_records', 0)}",
        f"- completed_blocks: {_comma_list(summary.get('completed_blocks'))}",
        f"- current_failed_blocks: {_comma_list(summary.get('current_failed_blocks'))}",
        f"- historical_failed_records: {summary.get('historical_failed_records', 0)}",
        f"- next_effective_action: {summary.get('next_effective_action', 'none')}",
        "",
        "## Manual Actions",
    ]
    manual_actions = summary.get("manual_actions") or ["none"]
    for action in manual_actions:
        lines.append(f"- {action}")

    chapter_ids = list(summary.get("chapter_ids") or [])
    chapter_summary = summary.get("chapter_summary") or {}
    if chapter_ids:
        lines.extend(
            [
                "",
                "## Chapter Summary",
                "| chapter | expected blocks | complete | failed | pending | output |",
                "| --- | ---: | ---: | --- | --- | --- |",
            ]
        )
        for chapter_id in chapter_ids:
            chapter = chapter_summary.get(chapter_id, {})
            output_state = "exists" if chapter.get("output_exists") else "missing"
            lines.append(
                f"| {chapter_id} | {chapter.get('expected_blocks', 0)} | {chapter.get('completed_blocks', 0)} | "
                f"{_comma_list(chapter.get('failed_blocks'))} | {_comma_list(chapter.get('pending_blocks'))} | "
                f"{output_state} |"
            )

    block_stage_status = summary.get("block_stage_status") or {}
    if block_stage_status:
        lines.extend(
            [
                "",
                "## Block Status",
                "| block | next pending | records |",
                "| --- | --- | ---: |",
            ]
        )
        for block_id in sorted(block_stage_status):
            block = block_stage_status[block_id]
            lines.append(
                f"| {block_id} | {block.get('next_pending_stage') or 'none'} | {len(block.get('records') or [])} |"
            )

    return "\n".join(lines).rstrip() + "\n"


def _scan_cleanliness_text(text: str) -> list[str]:
    issues: list[str] = []
    for issue in validate_formatted_text(text):
        if issue.startswith("provider/meta marker:") or issue.startswith("quote-only line"):
            issues.append(issue)

    for line_number, line in enumerate(text.splitlines()[1:], start=2):
        if _HAN_RE.search(line):
            issues.append(f"Han Chinese body line {line_number}")

    for variant in _WRONG_GLOSSARY_VARIANTS:
        if variant in text:
            issues.append(f"wrong glossary variant: {variant}")

    return issues


def _load_chapter_output(config: Any, chapter_id: str) -> tuple[Path, str | None]:
    output_root = getattr(config.workspace, "output", Path("05_Output"))
    output_path = output_root / chapter_id / f"{chapter_id}.md"
    return output_path, read_text_if_exists(output_path)


def _chapter_block_ids(summary: dict[str, Any], chapter_id: str) -> list[str]:
    block_stage_status = summary.get("block_stage_status") or {}
    return [
        block_id
        for block_id in sorted(block_stage_status)
        if block_id.startswith(f"{chapter_id}-block-")
    ]


def _render_cleanliness_markdown(*, run_id: str, chapter_results: list[dict[str, Any]]) -> str:
    lines: list[str] = [
        f"# Cleanliness Report - {run_id}",
        "",
        "## Chapters",
    ]
    for chapter in chapter_results:
        lines.extend(
            [
                "",
                f"### {chapter['chapter_id']}",
                f"- output: {chapter['output_path']}",
                f"- exists: {'yes' if chapter['exists'] else 'no'}",
                f"- size_bytes: {chapter.get('size_bytes', 0)}",
                f"- line_count: {chapter.get('line_count', 0)}",
                f"- blocks_inspected: {len(chapter.get('block_ids') or [])}",
            ]
        )

        block_issues = chapter.get("block_issues") or []
        if block_issues:
            lines.append("- block issues:")
            for issue in block_issues:
                lines.append(f"  - {issue}")
        else:
            lines.append("- block issues: none")

        issues = chapter.get("issues") or []
        if issues:
            lines.append("- file issues:")
            for issue in issues:
                lines.append(f"  - {issue}")
        else:
            lines.append("- file issues: none")

    return "\n".join(lines).rstrip() + "\n"


def _render_provider_usage_markdown(*, run_id: str, summary: dict[str, Any]) -> str:
    provider_usage = summary.get("provider_usage") or {}
    lines: list[str] = [
        f"# Provider Usage Report - {run_id}",
        "",
        "## Summary",
        f"- current_failed_blocks: {_comma_list(summary.get('current_failed_blocks'))}",
        f"- historical_failed_records: {summary.get('historical_failed_records', 0)}",
        "",
        "## Provider Usage",
        "| provider | stage | status | count |",
        "| --- | --- | --- | ---: |",
    ]
    for provider, stages in sorted(provider_usage.items()):
        for stage, status_counts in sorted(stages.items()):
            for status, count in sorted(status_counts.items()):
                lines.append(f"| {provider} | {stage} | {status} | {count} |")
    return "\n".join(lines).rstrip() + "\n"


def _stage_route_rows(config: Any) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for stage, routing in sorted(getattr(config, "stage_routing", {}).items()):
        fallbacks = []
        for fallback in getattr(routing, "fallbacks", ()) or ():
            provider = str(fallback.get("provider", "")).strip()
            model = str(fallback.get("model", "")).strip()
            if provider:
                fallbacks.append(f"{provider}/{model}" if model else provider)
        rows.append(
            {
                "stage": str(stage),
                "provider": str(getattr(routing, "provider", "") or ""),
                "model": str(getattr(routing, "model", "") or ""),
                "fallbacks": ", ".join(fallbacks) if fallbacks else "none",
                "timeout": str(getattr(routing, "timeout_seconds", "") or "default"),
            }
        )
    return rows


def _provider_readiness_rows(preflight: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in preflight.get("providers") or []:
        rows.append(
            {
                "provider": str(item.get("provider") or ""),
                "status": str(item.get("status") or "unknown"),
                "stages": _comma_list(item.get("stages") or []),
                "transport": str(item.get("prompt_transport") or "unknown"),
            }
        )
    return rows


def _recent_failure_rows(config: Any, run_id: str, *, limit: int = 8) -> list[dict[str, str]]:
    records = [
        record
        for record in RunLedger(config.ledger_path).iter_records(run_id=run_id)
        if record.status in {"failed", "hard_fail"}
    ]
    rows: list[dict[str, str]] = []
    for record in records[-limit:]:
        rows.append(
            {
                "block": record.block_id,
                "stage": record.stage,
                "provider": record.provider or "unknown",
                "status": record.status,
                "message": str(record.metadata.get("message") or record.metadata.get("error_type") or ""),
            }
        )
    return rows


def _block_chapter_id_from_record(block_id: str) -> str:
    if "-block-" in block_id:
        return block_id.rsplit("-block-", 1)[0]
    return block_id


def _stage_artifact_name(stage: str) -> str:
    return {
        "translating": "literal",
        "refining": "refined",
        "qa": "qa",
        "formatting": "formatted",
    }.get(stage, "")


def _stage_artifact_exists(config: Any, block_id: str, stage: str) -> bool:
    artifact_name = _stage_artifact_name(stage)
    if not artifact_name:
        return False
    chapter_id = _block_chapter_id_from_record(block_id)
    return bool((config.workspace.work / chapter_id / f"{block_id}.{artifact_name}.json").exists())


def _cache_readiness_rows(config: Any, run_id: str) -> list[dict[str, str]]:
    tracked_stages = ("translating", "refining", "qa", "formatting")
    state = RunLedger(config.ledger_path).load_state(run_id)
    totals: dict[str, dict[str, int]] = {
        stage: {
            "completed": 0,
            "artifact_exists": 0,
            "input_hash": 0,
            "output_hash": 0,
            "cache_ready": 0,
        }
        for stage in tracked_stages
    }
    for (block_id, stage), record in state.latest_by_stage.items():
        if stage not in totals or record.status != "completed":
            continue
        artifact_exists = _stage_artifact_exists(config, block_id, stage)
        has_input_hash = bool(record.input_hash)
        has_output_hash = bool(record.output_hash)
        totals[stage]["completed"] += 1
        totals[stage]["artifact_exists"] += int(artifact_exists)
        totals[stage]["input_hash"] += int(has_input_hash)
        totals[stage]["output_hash"] += int(has_output_hash)
        totals[stage]["cache_ready"] += int(artifact_exists and has_input_hash and has_output_hash)

    return [
        {
            "stage": stage,
            "completed": str(values["completed"]),
            "artifact_exists": str(values["artifact_exists"]),
            "input_hash": str(values["input_hash"]),
            "output_hash": str(values["output_hash"]),
            "cache_ready": str(values["cache_ready"]),
        }
        for stage, values in totals.items()
    ]


def _timing_baseline_rows(config: Any, run_id: str) -> list[dict[str, str]]:
    totals: dict[tuple[str, str], dict[str, float | int]] = {}
    for record in RunLedger(config.ledger_path).iter_records(run_id=run_id):
        key = (record.stage or "unknown", record.provider or "unknown")
        row = totals.setdefault(
            key,
            {
                "records": 0,
                "completed": 0,
                "failed": 0,
                "duration_records": 0,
                "total_seconds": 0.0,
            },
        )
        row["records"] = int(row["records"]) + 1
        if record.status == "completed":
            row["completed"] = int(row["completed"]) + 1
        if record.status in {"failed", "hard_fail"}:
            row["failed"] = int(row["failed"]) + 1

        duration = record.metadata.get("duration_seconds")
        if isinstance(duration, (int, float)) and duration >= 0:
            row["duration_records"] = int(row["duration_records"]) + 1
            row["total_seconds"] = float(row["total_seconds"]) + float(duration)

    rows: list[dict[str, str]] = []
    for (stage, provider), values in sorted(totals.items()):
        duration_records = int(values["duration_records"])
        total_seconds = float(values["total_seconds"])
        average_seconds = total_seconds / duration_records if duration_records else 0.0
        rows.append(
            {
                "stage": stage,
                "provider": provider,
                "records": str(int(values["records"])),
                "completed": str(int(values["completed"])),
                "failed": str(int(values["failed"])),
                "duration_records": str(duration_records),
                "total_seconds": f"{total_seconds:.2f}",
                "average_seconds": f"{average_seconds:.2f}" if duration_records else "n/a",
            }
        )
    return rows


def _parallel_projection_rows(config: Any, run_id: str) -> list[dict[str, str]]:
    policy = getattr(config, "execution", None)
    stage_limits = getattr(policy, "stage_concurrency", {}) or {}
    if not stage_limits:
        return [
            {
                "stage": "none",
                "provider": "none",
                "records": "0",
                "configured_limit": "1",
                "sequential_seconds": "0.00",
                "projected_seconds": "0.00",
                "estimated_saved_seconds": "0.00",
                "estimated_reduction_pct": "0.0",
                "note": "no configured concurrency limits",
            }
        ]

    durations_by_key: dict[tuple[str, str], list[float]] = {}
    failed_by_key: dict[tuple[str, str], int] = {}
    for record in RunLedger(config.ledger_path).iter_records(run_id=run_id):
        stage = record.stage
        if stage not in stage_limits:
            continue
        provider = record.provider or "unknown"
        key = (stage, provider)
        durations_by_key.setdefault(key, [])
        failed_by_key.setdefault(key, 0)
        if record.status in {"failed", "hard_fail"}:
            failed_by_key[key] += 1
            continue
        if record.status != "completed":
            continue
        duration = record.metadata.get("duration_seconds")
        if isinstance(duration, (int, float)) and duration >= 0:
            durations_by_key[key].append(float(duration))

    rows: list[dict[str, str]] = []
    runtime_enabled = bool(getattr(policy, "concurrency_enabled", False))
    keys = sorted(set(durations_by_key) | set(failed_by_key))
    for stage in sorted(stage_limits):
        if not any(key_stage == stage for key_stage, _ in keys):
            keys.append((stage, "none"))
    for stage, provider in sorted(keys):
        configured_limit = max(1, int(stage_limits.get(stage, 1)))
        durations = durations_by_key.get((stage, provider), [])
        sequential = sum(durations)
        failed = failed_by_key.get((stage, provider), 0)
        if configured_limit <= 1 or len(durations) < 2 or failed:
            projected = sequential
        else:
            projected = 0.0
            for index in range(0, len(durations), configured_limit):
                projected += max(durations[index : index + configured_limit])
        saved = max(0.0, sequential - projected)
        reduction = (saved / sequential * 100.0) if sequential else 0.0
        if failed:
            note = "simulation withheld because stage/provider has failed records"
        elif configured_limit <= 1:
            note = "configured limit is sequential"
        elif len(durations) < 2:
            note = "insufficient completed timing records"
        elif runtime_enabled:
            note = "projection only; verify with approved bounded benchmark"
        else:
            note = "simulation only; runtime remains sequential"
        rows.append(
            {
                "stage": str(stage),
                "provider": str(provider),
                "records": str(len(durations)),
                "configured_limit": str(configured_limit),
                "sequential_seconds": f"{sequential:.2f}",
                "projected_seconds": f"{projected:.2f}",
                "estimated_saved_seconds": f"{saved:.2f}",
                "estimated_reduction_pct": f"{reduction:.1f}",
                "note": note,
            }
        )
    return rows


def _pre_qa_refined_text_from_artifact(path: Path) -> tuple[str | None, str | None]:
    raw = read_text_if_exists(path)
    if raw is None:
        return None, "missing_refined_artifact"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None, "invalid_refined_json"
    refined_text = data.get("refined_text")
    if not isinstance(refined_text, str):
        return None, "missing_refined_text"
    return refined_text, None


def _pre_qa_guardrail_issues(text: str) -> tuple[list[str], list[str]]:
    hard: list[str] = []
    warnings: list[str] = []
    stripped = text.strip()
    if not stripped:
        hard.append("empty_refined_text")
        return hard, warnings
    if len(stripped) < 40:
        hard.append(f"refined_text_too_short:{len(stripped)}")

    for issue in validate_formatted_text(stripped):
        if issue.startswith("provider/meta marker:") or issue == "Han Chinese characters present":
            hard.append(issue)
        elif issue.startswith("quote-only line"):
            warnings.append(issue)

    if re.search(r"(.)\1{20,}", stripped):
        hard.append("runaway_repeated_character")

    dense_paragraphs = [
        len(paragraph.strip())
        for paragraph in stripped.split("\n\n")
        if paragraph.strip() and len(paragraph.strip()) > 900
    ]
    if dense_paragraphs:
        warnings.append(f"dense_paragraph:{max(dense_paragraphs)}")

    return hard, warnings


def _pre_qa_guardrail_preview(config: Any, run_id: str, *, sample_limit: int = 8) -> dict[str, Any]:
    state = RunLedger(config.ledger_path).load_state(run_id)
    checked = 0
    artifact_missing = 0
    hard_blocks = 0
    warning_blocks = 0
    samples: list[dict[str, str]] = []

    for (block_id, stage), record in sorted(state.latest_by_stage.items()):
        if stage != "refining" or record.status != "completed":
            continue
        checked += 1
        chapter_id = _block_chapter_id_from_record(block_id)
        path = config.workspace.work / chapter_id / f"{block_id}.refined.json"
        refined_text, load_issue = _pre_qa_refined_text_from_artifact(path)
        hard: list[str] = []
        warnings: list[str] = []
        if load_issue is not None:
            hard.append(load_issue)
            if load_issue == "missing_refined_artifact":
                artifact_missing += 1
        else:
            hard, warnings = _pre_qa_guardrail_issues(refined_text or "")

        if hard:
            hard_blocks += 1
        if warnings:
            warning_blocks += 1
        if (hard or warnings) and len(samples) < sample_limit:
            samples.append(
                {
                    "block": block_id,
                    "hard": _comma_list(hard),
                    "warnings": _comma_list(warnings),
                    "artifact": str(path),
                }
            )

    return {
        "checked": checked,
        "artifact_missing": artifact_missing,
        "hard_blocks": hard_blocks,
        "warning_blocks": warning_blocks,
        "samples": samples,
    }


def _concurrency_recommendation_rows(timing_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    eligible_stages = {"translating", "refining", "formatting"}
    rows: list[dict[str, str]] = []
    for row in timing_rows:
        stage = row.get("stage", "")
        if stage not in eligible_stages:
            continue
        duration_records = int(row.get("duration_records") or "0")
        failed = int(row.get("failed") or "0")
        completed = int(row.get("completed") or "0")
        average_raw = row.get("average_seconds") or "n/a"
        average_seconds = float(average_raw) if average_raw != "n/a" else 0.0

        if failed:
            recommendation = "keep sequential until failures are reviewed"
            confidence = "low"
        elif duration_records < 10:
            recommendation = "collect more timing metadata before concurrency"
            confidence = "low"
        elif average_seconds >= 10.0 and completed >= 10:
            recommendation = "benchmark concurrency=2 on a small approved range"
            confidence = "medium"
        else:
            recommendation = "keep sequential; low timing payoff"
            confidence = "medium"

        rows.append(
            {
                "stage": stage,
                "provider": row.get("provider", "unknown"),
                "duration_records": str(duration_records),
                "average_seconds": average_raw,
                "failed": str(failed),
                "recommendation": recommendation,
                "confidence": confidence,
            }
        )
    return rows


def _execution_policy_rows(config: Any) -> list[dict[str, str]]:
    policy = getattr(config, "execution", None)
    if policy is None:
        return [
            {
                "stage": "all",
                "configured_limit": "1",
                "effective_limit": "1",
                "enabled": "false",
            }
        ]
    stage_limits = getattr(policy, "stage_concurrency", {}) or {}
    if not stage_limits:
        stage_limits = {stage: 1 for stage in ("translating", "refining", "qa", "formatting")}
    rows: list[dict[str, str]] = []
    for stage, configured_limit in sorted(stage_limits.items()):
        effective_limit = policy.limit_for_stage(stage) if hasattr(policy, "limit_for_stage") else 1
        rows.append(
            {
                "stage": str(stage),
                "configured_limit": str(configured_limit),
                "effective_limit": str(effective_limit),
                "enabled": str(bool(getattr(policy, "concurrency_enabled", False))).lower(),
            }
        )
    return rows


def _guardrail_policy_rows(config: Any) -> list[dict[str, str]]:
    policy = getattr(config, "execution", None)
    if policy is None:
        return [
            {
                "guardrail": "pre_qa",
                "mode": "report_only",
                "runtime_blocking": "false",
                "threshold": "dense paragraph warning >900 chars",
            }
        ]
    dense_limit = getattr(policy, "pre_qa_dense_paragraph_warning_chars", 900)
    blocks_runtime = policy.pre_qa_blocks_runtime() if hasattr(policy, "pre_qa_blocks_runtime") else False
    return [
        {
            "guardrail": "pre_qa",
            "mode": str(getattr(policy, "pre_qa_guardrail_mode", "report_only")),
            "runtime_blocking": str(bool(blocks_runtime)).lower(),
            "threshold": f"dense paragraph warning >{dense_limit} chars",
        }
    ]


def _cache_policy_rows(config: Any) -> list[dict[str, str]]:
    policy = getattr(config, "execution", None)
    if policy is None:
        return [
            {
                "mode": "report_only",
                "runtime_skip": "false",
                "stages": "none",
                "rule": "cache readiness is advisory only",
            }
        ]
    cache_skips = policy.cache_skips_runtime() if hasattr(policy, "cache_skips_runtime") else False
    stages = getattr(policy, "artifact_cache_stages", ()) or ()
    return [
        {
            "mode": str(getattr(policy, "artifact_cache_mode", "report_only")),
            "runtime_skip": str(bool(cache_skips)).lower(),
            "stages": _comma_list(stages),
            "rule": "skip only when stage input hash, output hash, and artifact validation match",
        }
    ]


def _speed_savings_estimate_rows(
    cache_rows: list[dict[str, str]],
    timing_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    timing_by_stage: dict[str, dict[str, str]] = {}
    for row in timing_rows:
        stage = row.get("stage", "")
        if not stage:
            continue
        duration_records = int(row.get("duration_records") or "0")
        failed = int(row.get("failed") or "0")
        average_raw = row.get("average_seconds") or "n/a"
        if failed or duration_records < 10 or average_raw == "n/a":
            continue
        current = timing_by_stage.get(stage)
        if current is None or float(average_raw) > float(current.get("average_seconds", "0")):
            timing_by_stage[stage] = row

    rows: list[dict[str, str]] = []
    for row in cache_rows:
        stage = row.get("stage", "")
        cache_ready = int(row.get("cache_ready") or "0")
        timing = timing_by_stage.get(stage)
        if timing is None:
            rows.append(
                {
                    "stage": stage,
                    "cache_ready": str(cache_ready),
                    "average_seconds": "n/a",
                    "estimated_seconds_saved": "n/a",
                    "confidence": "low",
                    "note": "insufficient clean timing baseline",
                }
            )
            continue
        average_seconds = float(timing.get("average_seconds", "0"))
        estimated = cache_ready * average_seconds
        rows.append(
            {
                "stage": stage,
                "cache_ready": str(cache_ready),
                "average_seconds": f"{average_seconds:.2f}",
                "estimated_seconds_saved": f"{estimated:.2f}",
                "confidence": "medium" if cache_ready else "low",
                "note": "read-only estimate; runtime cache skip is not enabled",
            }
        )
    return rows


def _cache_benchmark_rows(config: Any, run_id: str) -> list[dict[str, str]]:
    ledger = RunLedger(config.ledger_path)
    records = [
        record
        for record in ledger.iter_records(run_id=run_id, stage="translating", status="completed")
        if "-block-" in record.block_id
    ]
    rows: list[dict[str, str]] = []
    for record in records:
        artifact_exists = _stage_artifact_exists(config, record.block_id, "translating")
        eligible = bool(record.input_hash and record.output_hash and artifact_exists)
        reason = "ready" if eligible else "missing "
        if not eligible:
            missing: list[str] = []
            if not record.input_hash:
                missing.append("input_hash")
            if not record.output_hash:
                missing.append("output_hash")
            if not artifact_exists:
                missing.append("artifact")
            reason = ", ".join(missing)
        rows.append(
            {
                "block": record.block_id,
                "provider": record.provider or "unknown",
                "input_hash": "yes" if record.input_hash else "no",
                "output_hash": "yes" if record.output_hash else "no",
                "artifact": "yes" if artifact_exists else "no",
                "eligible": "yes" if eligible else "no",
                "reason": reason,
            }
        )
    return rows


def _cache_benchmark_summary_rows(
    cache_rows: list[dict[str, str]],
    timing_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    total = len(cache_rows)
    eligible = sum(1 for row in cache_rows if row.get("eligible") == "yes")
    blocked = total - eligible
    average_seconds = "n/a"
    estimated_saved = "n/a"
    confidence = "low"
    note = "insufficient clean translating timing baseline"
    clean_translate_timing = [
        row
        for row in timing_rows
        if row.get("stage") == "translating"
        and int(row.get("failed") or "0") == 0
        and int(row.get("duration_records") or "0") >= 10
    ]
    if clean_translate_timing:
        timing = max(clean_translate_timing, key=lambda row: float(row.get("average_seconds") or "0"))
        average = float(timing.get("average_seconds") or "0")
        average_seconds = f"{average:.2f}"
        estimated_saved = f"{eligible * average:.2f}"
        confidence = "medium" if eligible else "low"
        note = "read-only estimate; benchmark still required before enabling cache operationally"
    decision = "ready_for_small_benchmark" if eligible and confidence != "low" else "not_ready"
    return [
        {
            "stage": "translating",
            "records": str(total),
            "eligible": str(eligible),
            "blocked": str(blocked),
            "average_seconds": average_seconds,
            "estimated_saved_seconds": estimated_saved,
            "confidence": confidence,
            "decision": decision,
            "note": note,
        }
    ]


def _render_cache_benchmark_markdown(
    *,
    run_id: str,
    policy_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
    cache_rows: list[dict[str, str]],
) -> str:
    lines = [
        f"# Cache Benchmark Report - {run_id}",
        "",
        "Read-only V6.18B benchmark planning report. It does not enable cache, skip provider calls, edit ledger, or change artifacts.",
        "",
        "## Cache Policy",
        "| mode | runtime skip | stages | rule |",
        "| --- | --- | --- | --- |",
    ]
    for row in policy_rows:
        lines.append(f"| {row['mode']} | {row['runtime_skip']} | {row['stages']} | {row['rule']} |")

    lines.extend(
        [
            "",
            "## Benchmark Summary",
            "| stage | records | eligible | blocked | average seconds | estimated saved seconds | confidence | decision | note |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in summary_rows:
        lines.append(
            f"| {row['stage']} | {row['records']} | {row['eligible']} | {row['blocked']} | "
            f"{row['average_seconds']} | {row['estimated_saved_seconds']} | {row['confidence']} | "
            f"{row['decision']} | {row['note']} |"
        )

    lines.extend(
        [
            "",
            "## Translating Cache Eligibility",
            "| block | provider | input hash | output hash | artifact | eligible | reason |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    if cache_rows:
        for row in cache_rows:
            lines.append(
                f"| {row['block']} | {row['provider']} | {row['input_hash']} | {row['output_hash']} | "
                f"{row['artifact']} | {row['eligible']} | {row['reason']} |"
            )
    else:
        lines.append("| none | none | no | no | no | no | no completed translating records |")

    lines.extend(
        [
            "",
            "## Safety Notes",
            "- Only `translating` is assessed because it is the only runtime cache-skip stage currently implemented.",
            "- Refinement, QA, and formatting cache skip remain disabled.",
            "- This report is not approval to switch `.system/config.yaml` to `enabled`.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _concurrency_benchmark_summary_rows(
    recommendation_rows: list[dict[str, str]],
    projection_rows: list[dict[str, str]],
    execution_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    projection_by_key = {
        (row.get("stage", ""), row.get("provider", "unknown")): row
        for row in projection_rows
    }
    execution_by_stage = {row.get("stage", ""): row for row in execution_rows}
    rows: list[dict[str, str]] = []
    for recommendation in recommendation_rows:
        stage = recommendation.get("stage", "")
        provider = recommendation.get("provider", "unknown")
        projection = projection_by_key.get((stage, provider), {})
        execution = execution_by_stage.get(stage, {})
        recommendation_text = recommendation.get("recommendation", "")
        projected_saved = float(projection.get("estimated_saved_seconds") or "0")
        configured_limit = int(execution.get("configured_limit") or projection.get("configured_limit") or "1")
        runtime_enabled = execution.get("enabled", "false") == "true"
        if (
            "benchmark concurrency=2" in recommendation_text
            and projected_saved > 0
            and configured_limit >= 2
            and not runtime_enabled
        ):
            decision = "ready_for_small_benchmark"
            next_action = "run an explicitly approved small non-production benchmark"
        elif runtime_enabled:
            decision = "runtime_enabled_requires_review"
            next_action = "verify quality gates before any further rollout"
        else:
            decision = "not_ready"
            next_action = "collect cleaner timing data or review failed records"
        rows.append(
            {
                "stage": stage,
                "provider": recommendation.get("provider", "unknown"),
                "configured_limit": str(configured_limit),
                "duration_records": recommendation.get("duration_records", "0"),
                "failed": recommendation.get("failed", "0"),
                "projected_saved_seconds": projection.get("estimated_saved_seconds", "0.00"),
                "projected_reduction_pct": projection.get("estimated_reduction_pct", "0.0"),
                "decision": decision,
                "next_action": next_action,
            }
        )
    if not rows:
        rows.append(
            {
                "stage": "none",
                "provider": "none",
                "configured_limit": "1",
                "duration_records": "0",
                "failed": "0",
                "projected_saved_seconds": "0.00",
                "projected_reduction_pct": "0.0",
                "decision": "not_ready",
                "next_action": "collect timing data first",
            }
        )
    return rows


def _render_concurrency_benchmark_markdown(
    *,
    run_id: str,
    execution_rows: list[dict[str, str]],
    recommendation_rows: list[dict[str, str]],
    projection_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> str:
    lines = [
        f"# Concurrency Benchmark Report - {run_id}",
        "",
        "Read-only V6.18A benchmark planning report. It does not enable parallel runtime, execute providers, edit ledger, or change artifacts.",
        "",
        "## Benchmark Summary",
        "| stage | provider | configured limit | duration records | failed | projected saved seconds | projected reduction % | decision | next action |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['stage']} | {row['provider']} | {row['configured_limit']} | "
            f"{row['duration_records']} | {row['failed']} | {row['projected_saved_seconds']} | "
            f"{row['projected_reduction_pct']} | {row['decision']} | {row['next_action']} |"
        )

    lines.extend(
        [
            "",
            "## Execution Policy",
            "| stage | configured limit | effective limit | concurrency enabled |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for row in execution_rows:
        lines.append(
            f"| {row['stage']} | {row['configured_limit']} | {row['effective_limit']} | {row['enabled']} |"
        )

    lines.extend(
        [
            "",
            "## Recommendations",
            "| stage | provider | duration records | average seconds | failed | recommendation | confidence |",
            "| --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    if recommendation_rows:
        for row in recommendation_rows:
            lines.append(
                f"| {row['stage']} | {row['provider']} | {row['duration_records']} | "
                f"{row['average_seconds']} | {row['failed']} | {row['recommendation']} | {row['confidence']} |"
            )
    else:
        lines.append("| none | none | 0 | n/a | 0 | no eligible timing data | low |")

    lines.extend(
        [
            "",
            "## Simulation",
            "| stage | provider | timing records | configured limit | sequential seconds | projected seconds | estimated saved seconds | reduction % | note |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in projection_rows:
        lines.append(
            f"| {row['stage']} | {row['provider']} | {row['records']} | {row['configured_limit']} | "
            f"{row['sequential_seconds']} | {row['projected_seconds']} | "
            f"{row['estimated_saved_seconds']} | {row['estimated_reduction_pct']} | {row['note']} |"
        )

    lines.extend(
        [
            "",
            "## Safety Notes",
            "- This report is not approval to set `execution.concurrency_enabled: true`.",
            "- Glossary approval remains sequential and human-gated.",
            "- QA and AI formatting must remain enabled in any benchmark.",
            "- Stop on first hard failure, provider failure spike, command_too_long, or final-output guardrail regression.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _benchmark_scope_rows(
    summary: dict[str, Any],
    concurrency_rows: list[dict[str, str]],
    execution_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    configured_limits = {
        row.get("stage", ""): row.get("configured_limit", "1")
        for row in execution_rows
    }
    current_failed = list(summary.get("current_failed_blocks") or [])
    chapter_ids = list(summary.get("chapter_ids") or [])
    last_chapter = chapter_ids[-1] if chapter_ids else ""
    if current_failed:
        scope = f"none until failed blocks are recovered: {_comma_list(current_failed)}"
    elif last_chapter:
        scope = f"next approved 1-chapter bounded range after {last_chapter}"
    else:
        scope = "next approved 1-chapter bounded range after scan/glossary approval"

    rows: list[dict[str, str]] = []
    for row in concurrency_rows:
        recommendation = row.get("recommendation", "")
        stage = row.get("stage", "")
        if "benchmark concurrency=2" in recommendation:
            rows.append(
                {
                    "stage": stage,
                    "provider": row.get("provider", "unknown"),
                    "target_limit": configured_limits.get(stage, "2"),
                    "scope": scope,
                    "prerequisite": "user-approved scan/glossary gate and no current failed blocks",
                    "stop_condition": "first provider failure, QA hard-fail, formatting validation failure, or scope expansion",
                }
            )
    if not rows:
        rows.append(
            {
                "stage": "none",
                "provider": "none",
                "target_limit": "1",
                "scope": "no concurrency benchmark recommended from current evidence",
                "prerequisite": "collect more timing data or resolve failed records",
                "stop_condition": "n/a",
            }
        )
    return rows


def _recommended_batch_size(summary: dict[str, Any], preflight: dict[str, Any]) -> str:
    current_failed = summary.get("current_failed_blocks") or []
    blocking = preflight.get("blocking_reasons") or []
    warnings = preflight.get("warnings") or []
    if current_failed or blocking:
        return "0 until blockers are resolved"
    if warnings:
        return "1-3 chapters"
    return "3-5 chapters"


def _recommended_checkpoint(summary: dict[str, Any]) -> str:
    chapter_ids = list(summary.get("chapter_ids") or [])
    current_failed = list(summary.get("current_failed_blocks") or [])
    manual_actions = [
        str(action)
        for action in (summary.get("manual_actions") or [])
        if str(action).strip() and str(action).strip().lower() != "none"
    ]
    if current_failed:
        return f"recover failed block first: {_comma_list(current_failed)}"
    if manual_actions:
        return manual_actions[0]
    if chapter_ids:
        return f"next bounded range after {chapter_ids[-1]}"
    return "run scan-only gate for an explicit chapter range"


def _render_run_plan_markdown(
    *,
    run_id: str,
    summary: dict[str, Any],
    preflight: dict[str, Any],
    provider_rows: list[dict[str, str]],
    route_rows: list[dict[str, str]],
    failure_rows: list[dict[str, str]],
    cache_rows: list[dict[str, str]],
    cache_policy_rows: list[dict[str, str]],
    speed_savings_rows: list[dict[str, str]],
    timing_rows: list[dict[str, str]],
    execution_rows: list[dict[str, str]],
    concurrency_rows: list[dict[str, str]],
    parallel_projection_rows: list[dict[str, str]],
    benchmark_scope_rows: list[dict[str, str]],
    guardrail_policy_rows: list[dict[str, str]],
    pre_qa_preview: dict[str, Any],
    suggested_commands: list[str],
) -> str:
    current_failed = summary.get("current_failed_blocks") or []
    manual_actions = summary.get("manual_actions") or []
    lines: list[str] = [
        f"# Run Plan Report - {run_id}",
        "",
        "## Summary",
        f"- read_only: yes",
        f"- preflight_status: {preflight.get('status', 'unknown')}",
        f"- current_failed_blocks: {_comma_list(current_failed)}",
        f"- manual_actions: {_comma_list(manual_actions)}",
        f"- recommended_batch_size: {_recommended_batch_size(summary, preflight)}",
        f"- recommended_checkpoint: {_recommended_checkpoint(summary)}",
        "",
        "## Suggested Commands",
    ]
    for command in suggested_commands:
        lines.append(f"- `{command}`")

    lines.extend(
        [
            "",
            "## Provider Readiness",
            "| provider | status | stages | transport |",
            "| --- | --- | --- | --- |",
        ]
    )
    if provider_rows:
        for row in provider_rows:
            lines.append(f"| {row['provider']} | {row['status']} | {row['stages']} | {row['transport']} |")
    else:
        lines.append("| none | unknown | none | none |")

    lines.extend(
        [
            "",
            "## Routing And Fallbacks",
            "| stage | provider | model | fallbacks | timeout |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    if route_rows:
        for row in route_rows:
            lines.append(
                f"| {row['stage']} | {row['provider']} | {row['model'] or 'default'} | "
                f"{row['fallbacks']} | {row['timeout']} |"
            )
    else:
        lines.append("| none | none | none | none | none |")

    lines.extend(
        [
            "",
            "## Recent Failures",
            "| block | stage | provider | status | message |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    if failure_rows:
        for row in failure_rows:
            lines.append(
                f"| {row['block']} | {row['stage']} | {row['provider']} | {row['status']} | {row['message']} |"
            )
    else:
        lines.append("| none | none | none | none | none |")

    lines.extend(
        [
            "",
            "## Cache Readiness",
            "| stage | completed | artifact exists | input hash | output hash | hash-cache ready |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in cache_rows:
        lines.append(
            f"| {row['stage']} | {row['completed']} | {row['artifact_exists']} | {row['input_hash']} | "
            f"{row['output_hash']} | {row['cache_ready']} |"
        )

    lines.extend(
        [
            "",
            "## Cache Policy",
            "| mode | runtime skip | stages | rule |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in cache_policy_rows:
        lines.append(f"| {row['mode']} | {row['runtime_skip']} | {row['stages']} | {row['rule']} |")

    lines.extend(
        [
            "",
            "## Speed Savings Estimate",
            "| stage | cache-ready artifacts | average seconds | estimated seconds saved | confidence | note |",
            "| --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in speed_savings_rows:
        lines.append(
            f"| {row['stage']} | {row['cache_ready']} | {row['average_seconds']} | "
            f"{row['estimated_seconds_saved']} | {row['confidence']} | {row['note']} |"
        )

    lines.extend(
        [
            "",
            "## Timing Baseline",
            "| stage | provider | records | completed | failed | duration records | total seconds | average seconds |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    if timing_rows:
        for row in timing_rows:
            lines.append(
                f"| {row['stage']} | {row['provider']} | {row['records']} | {row['completed']} | "
                f"{row['failed']} | {row['duration_records']} | {row['total_seconds']} | {row['average_seconds']} |"
            )
    else:
        lines.append("| none | none | 0 | 0 | 0 | 0 | 0.00 | n/a |")

    lines.extend(
        [
            "",
            "## Concurrency Benchmark Recommendations",
            "| stage | provider | duration records | average seconds | failed | recommendation | confidence |",
            "| --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    if concurrency_rows:
        for row in concurrency_rows:
            lines.append(
                f"| {row['stage']} | {row['provider']} | {row['duration_records']} | "
                f"{row['average_seconds']} | {row['failed']} | {row['recommendation']} | {row['confidence']} |"
            )
    else:
        lines.append("| none | none | 0 | n/a | 0 | no eligible stage data | low |")

    lines.extend(
        [
            "",
            "## Concurrency Simulation",
            "| stage | provider | timing records | configured limit | sequential seconds | projected seconds | estimated saved seconds | reduction % | note |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in parallel_projection_rows:
        lines.append(
            f"| {row['stage']} | {row['provider']} | {row['records']} | {row['configured_limit']} | "
            f"{row['sequential_seconds']} | {row['projected_seconds']} | "
            f"{row['estimated_saved_seconds']} | {row['estimated_reduction_pct']} | {row['note']} |"
        )

    lines.extend(
        [
            "",
            "## Execution Policy",
            "| stage | configured limit | effective limit | concurrency enabled |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for row in execution_rows:
        lines.append(
            f"| {row['stage']} | {row['configured_limit']} | {row['effective_limit']} | {row['enabled']} |"
        )

    lines.extend(
        [
            "",
            "## Benchmark Scope Plan",
            "| stage | provider | target limit | scope | prerequisite | stop condition |",
            "| --- | --- | ---: | --- | --- | --- |",
        ]
    )
    for row in benchmark_scope_rows:
        lines.append(
            f"| {row['stage']} | {row['provider']} | {row['target_limit']} | {row['scope']} | "
            f"{row['prerequisite']} | {row['stop_condition']} |"
        )

    lines.extend(
        [
            "",
            "## Guardrail Policy",
            "| guardrail | mode | runtime blocking | threshold |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in guardrail_policy_rows:
        lines.append(
            f"| {row['guardrail']} | {row['mode']} | {row['runtime_blocking']} | {row['threshold']} |"
        )

    lines.extend(
        [
            "",
            "## Pre-QA Guardrail Preview",
            f"- report_only: yes",
            f"- refined_artifacts_checked: {pre_qa_preview.get('checked', 0)}",
            f"- missing_refined_artifacts: {pre_qa_preview.get('artifact_missing', 0)}",
            f"- hard_error_blocks: {pre_qa_preview.get('hard_blocks', 0)}",
            f"- warning_blocks: {pre_qa_preview.get('warning_blocks', 0)}",
            "",
            "| block | hard errors | warnings | artifact |",
            "| --- | --- | --- | --- |",
        ]
    )
    samples = pre_qa_preview.get("samples") or []
    if samples:
        for row in samples:
            lines.append(f"| {row['block']} | {row['hard']} | {row['warnings']} | {row['artifact']} |")
    else:
        lines.append("| none | none | none | none |")

    lines.extend(
        [
            "",
            "## Speed-Safety Notes",
            "- glossary approval remains human-gated and sequential",
            "- QA and AI formatting stay enabled; this report does not replace either gate",
            "- cache readiness is report-only; execution still uses existing ledger skip behavior",
            "- pre-QA guardrail preview is report-only; it does not block or skip AI QA yet",
            "- keep risky stages sequential until a benchmark proves stability",
            "- use bounded resume/checkpoints rather than open-ended production runs",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _render_glossary_decisions_markdown(
    *,
    run_id: str,
    block_ids: list[str],
    approval_mode: str,
    approved_rows: list[dict[str, str]],
    rejected_terms: list[str],
) -> str:
    lines: list[str] = [
        f"# Glossary Decisions Report - {run_id}",
        "",
        "## Summary",
        f"- glossary_approved_block_ids: {_comma_list(block_ids)}",
        f"- approval_mode: {approval_mode or 'unknown'}",
        f"- approved_terms_count: {len(approved_rows)}",
        f"- rejected_terms_count: {len(rejected_terms)}",
        "",
        "## Approved Terms",
        "| original_term | thai_term | category | status | glossary_note_path |",
        "| --- | --- | --- | --- | --- |",
    ]
    if approved_rows:
        for row in approved_rows:
            lines.append(
                f"| {row['original_term']} | {row['thai_term']} | {row['category']} | "
                f"{row['status']} | {row['path']} |"
            )
    else:
        lines.append("| none | none | none | none | none |")

    lines.extend(["", "## Rejected Terms"])
    if rejected_terms:
        for term in rejected_terms:
            lines.append(f"- {term}")
    else:
        lines.append("- none")

    return "\n".join(lines).rstrip() + "\n"


def _render_product_review_markdown(
    *,
    run_id: str,
    overall_status: str,
    preflight: dict[str, Any],
    summary: dict[str, Any],
    canonical_present: list[str],
    canonical_missing: list[str],
    retired_absent: list[str],
    retired_present: list[str],
    required_present: list[str],
    required_missing: list[str],
    output_rows: list[dict[str, Any]],
    accepted_checks: list[dict[str, str]],
) -> str:
    lines: list[str] = [
        f"# Product Review Report - {run_id}",
        "",
        "## Summary",
        f"- overall_status: {overall_status}",
        f"- preflight_status: {preflight.get('status', 'unknown')}",
        f"- run_records: {summary.get('total_records', 0)}",
        f"- completed_blocks_count: {len(summary.get('completed_blocks') or [])}",
        f"- current_failed_blocks: {_comma_list(summary.get('current_failed_blocks'))}",
        f"- historical_failed_records: {summary.get('historical_failed_records', 0)}",
        f"- manual_actions_needed: {_comma_list(summary.get('manual_actions'))}",
        f"- next_effective_action: {summary.get('next_effective_action', 'none')}",
        "",
        "## Acceptance Checklist",
        "| check | status | detail |",
        "| --- | --- | --- |",
    ]
    for item in accepted_checks:
        lines.append(f"| {item['check']} | {item['status']} | {item['detail']} |")

    lines.extend(
        [
            "",
            "## Preflight",
            f"- status: {preflight.get('status', 'unknown')}",
            f"- next_safe_action: {preflight.get('next_safe_action', 'none')}",
            f"- warnings: {_comma_list(preflight.get('warnings'))}",
            f"- blocking_reasons: {_comma_list(preflight.get('blocking_reasons'))}",
            "",
            "## Canonical Docs",
            f"- canonical_present: {_comma_list(canonical_present)}",
            f"- canonical_missing: {_comma_list(canonical_missing)}",
            f"- retired_absent: {_comma_list(retired_absent)}",
            f"- retired_present: {_comma_list(retired_present)}",
            "",
            "## Required Product Files",
            f"- present: {_comma_list(required_present)}",
            f"- missing: {_comma_list(required_missing)}",
            "",
            "## Final Outputs",
            "| chapter | exists | issues | path |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in output_rows:
        lines.append(
            f"| {row['chapter_id']} | {'yes' if row['exists'] else 'no'} | "
            f"{_comma_list(row['issues'])} | {row['path']} |"
        )

    return "\n".join(lines).rstrip() + "\n"


def _quiet_status_run(*, config: Any, run_id: str) -> dict[str, Any]:
    with redirect_stdout(StringIO()):
        return status_run(config=config, run_id=run_id)


def _quiet_inspect_block(*, config: Any, run_id: str, block_id: str) -> dict[str, Any]:
    with redirect_stdout(StringIO()):
        return inspect_block_command(config=config, run_id=run_id, block_id=block_id)


def build_checkpoint_report(*, config: Any, run_id: str, output: Path | None = None) -> dict[str, Any]:
    summary = _quiet_status_run(config=config, run_id=run_id)
    path = _stable_report_path(config=config, kind="checkpoint", run_id=run_id, output=output)
    text = _render_checkpoint_markdown(run_id=run_id, summary=summary)
    atomic_write_text(path, text)
    actionable_failure = bool(summary.get("current_failed_blocks")) or (
        not summary.get("chapter_ids") and not summary.get("block_stage_status")
    )
    return {
        "path": path,
        "text": text,
        "summary": summary,
        "actionable_failure": actionable_failure,
    }


def build_cleanliness_report(
    *,
    config: Any,
    run_id: str,
    chapter_ids: list[str] | None = None,
    output: Path | None = None,
) -> dict[str, Any]:
    summary = _quiet_status_run(config=config, run_id=run_id)
    resolved_chapter_ids = chapter_ids or list(summary.get("chapter_ids") or [])
    chapter_results: list[dict[str, Any]] = []
    actionable_failure = not resolved_chapter_ids

    for chapter_id in resolved_chapter_ids:
        output_path, text = _load_chapter_output(config, chapter_id)
        exists = text is not None
        issues = [] if text is None else _scan_cleanliness_text(text)
        if not exists:
            issues.append("missing final output")
            actionable_failure = True
        elif issues:
            actionable_failure = True

        block_issues: list[str] = []
        for block_id in _chapter_block_ids(summary, chapter_id):
            block_report = _quiet_inspect_block(config=config, run_id=run_id, block_id=block_id)
            block_issues.extend(block_report.get("formatted_validation_issues") or [])
        if block_issues:
            actionable_failure = True

        chapter_results.append(
            {
                "chapter_id": chapter_id,
                "output_path": str(output_path),
                "exists": exists,
                "size_bytes": len(text.encode("utf-8")) if text is not None else 0,
                "line_count": len(text.splitlines()) if text is not None else 0,
                "block_ids": _chapter_block_ids(summary, chapter_id),
                "block_issues": block_issues,
                "issues": issues,
            }
        )

    path = _stable_report_path(
        config=config,
        kind="cleanliness",
        run_id=run_id,
        chapter_ids=resolved_chapter_ids or None,
        output=output,
    )
    text = _render_cleanliness_markdown(run_id=run_id, chapter_results=chapter_results)
    atomic_write_text(path, text)
    return {
        "path": path,
        "text": text,
        "summary": summary,
        "chapter_results": chapter_results,
        "actionable_failure": actionable_failure,
    }


def build_provider_usage_report(*, config: Any, run_id: str, output: Path | None = None) -> dict[str, Any]:
    summary = _quiet_status_run(config=config, run_id=run_id)
    path = _stable_report_path(config=config, kind="provider_usage", run_id=run_id, output=output)
    text = _render_provider_usage_markdown(run_id=run_id, summary=summary)
    atomic_write_text(path, text)
    return {
        "path": path,
        "text": text,
        "summary": summary,
        "actionable_failure": bool(summary.get("current_failed_blocks")),
    }


def build_run_plan_report(*, config: Any, run_id: str, output: Path | None = None) -> dict[str, Any]:
    summary = _quiet_status_run(config=config, run_id=run_id)
    preflight = build_preflight_summary(config)
    provider_rows = _provider_readiness_rows(preflight)
    route_rows = _stage_route_rows(config)
    failure_rows = _recent_failure_rows(config, run_id)
    cache_rows = _cache_readiness_rows(config, run_id)
    cache_policy_rows = _cache_policy_rows(config)
    timing_rows = _timing_baseline_rows(config, run_id)
    speed_savings_rows = _speed_savings_estimate_rows(cache_rows, timing_rows)
    execution_rows = _execution_policy_rows(config)
    concurrency_rows = _concurrency_recommendation_rows(timing_rows)
    parallel_projection_rows = _parallel_projection_rows(config, run_id)
    benchmark_scope_rows = _benchmark_scope_rows(summary, concurrency_rows, execution_rows)
    guardrail_policy_rows = _guardrail_policy_rows(config)
    pre_qa_preview = _pre_qa_guardrail_preview(config, run_id)
    suggested_commands = [
        f"novel-pipeline --config \"{config.config_path}\" status --run-id {run_id}",
        f"novel-pipeline --config \"{config.config_path}\" report checkpoint --run-id {run_id}",
        f"novel-pipeline --config \"{config.config_path}\" report provider-usage --run-id {run_id}",
    ]
    if summary.get("current_failed_blocks"):
        first_failed = list(summary.get("current_failed_blocks") or [""])[0]
        if first_failed:
            suggested_commands.insert(
                1,
                f"novel-pipeline --config \"{config.config_path}\" inspect-block --run-id {run_id} --block-id {first_failed}",
            )
    else:
        suggested_commands.append(
            f"novel-pipeline --config \"{config.config_path}\" resume --run-id {run_id} --manual-action-mode stop"
        )

    path = _stable_report_path(config=config, kind="run_plan", run_id=run_id, output=output)
    text = _render_run_plan_markdown(
        run_id=run_id,
        summary=summary,
        preflight=preflight,
        provider_rows=provider_rows,
        route_rows=route_rows,
        failure_rows=failure_rows,
        cache_rows=cache_rows,
        cache_policy_rows=cache_policy_rows,
        speed_savings_rows=speed_savings_rows,
        timing_rows=timing_rows,
        execution_rows=execution_rows,
        concurrency_rows=concurrency_rows,
        parallel_projection_rows=parallel_projection_rows,
        benchmark_scope_rows=benchmark_scope_rows,
        guardrail_policy_rows=guardrail_policy_rows,
        pre_qa_preview=pre_qa_preview,
        suggested_commands=suggested_commands,
    )
    atomic_write_text(path, text)
    return {
        "path": path,
        "text": text,
        "summary": summary,
        "preflight": preflight,
        "provider_rows": provider_rows,
        "route_rows": route_rows,
        "failure_rows": failure_rows,
        "cache_rows": cache_rows,
        "cache_policy_rows": cache_policy_rows,
        "speed_savings_rows": speed_savings_rows,
        "timing_rows": timing_rows,
        "execution_rows": execution_rows,
        "concurrency_rows": concurrency_rows,
        "parallel_projection_rows": parallel_projection_rows,
        "benchmark_scope_rows": benchmark_scope_rows,
        "guardrail_policy_rows": guardrail_policy_rows,
        "pre_qa_preview": pre_qa_preview,
        "actionable_failure": False,
    }


def build_cache_benchmark_report(*, config: Any, run_id: str, output: Path | None = None) -> dict[str, Any]:
    cache_rows = _cache_benchmark_rows(config, run_id)
    policy_rows = _cache_policy_rows(config)
    timing_rows = _timing_baseline_rows(config, run_id)
    summary_rows = _cache_benchmark_summary_rows(cache_rows, timing_rows)
    path = _stable_report_path(config=config, kind="cache_benchmark", run_id=run_id, output=output)
    text = _render_cache_benchmark_markdown(
        run_id=run_id,
        policy_rows=policy_rows,
        summary_rows=summary_rows,
        cache_rows=cache_rows,
    )
    atomic_write_text(path, text)
    return {
        "path": path,
        "text": text,
        "cache_rows": cache_rows,
        "policy_rows": policy_rows,
        "summary_rows": summary_rows,
        "actionable_failure": False,
    }


def build_concurrency_benchmark_report(*, config: Any, run_id: str, output: Path | None = None) -> dict[str, Any]:
    timing_rows = _timing_baseline_rows(config, run_id)
    execution_rows = _execution_policy_rows(config)
    recommendation_rows = _concurrency_recommendation_rows(timing_rows)
    projection_rows = _parallel_projection_rows(config, run_id)
    summary_rows = _concurrency_benchmark_summary_rows(
        recommendation_rows,
        projection_rows,
        execution_rows,
    )
    path = _stable_report_path(config=config, kind="concurrency_benchmark", run_id=run_id, output=output)
    text = _render_concurrency_benchmark_markdown(
        run_id=run_id,
        execution_rows=execution_rows,
        recommendation_rows=recommendation_rows,
        projection_rows=projection_rows,
        summary_rows=summary_rows,
    )
    atomic_write_text(path, text)
    return {
        "path": path,
        "text": text,
        "timing_rows": timing_rows,
        "execution_rows": execution_rows,
        "recommendation_rows": recommendation_rows,
        "projection_rows": projection_rows,
        "summary_rows": summary_rows,
        "actionable_failure": False,
    }


def build_glossary_decisions_report(*, config: Any, run_id: str, output: Path | None = None) -> dict[str, Any]:
    ledger = RunLedger(config.ledger_path)
    records = list(ledger.iter_records(run_id=run_id, stage="glossary_approved", status="completed"))
    chapter_records = [record for record in records if re.fullmatch(r"ch\d+", record.block_id)]
    latest_record = chapter_records[-1] if chapter_records else None
    metadata = latest_record.metadata if latest_record is not None else {}
    approved_terms = list(metadata.get("approved_terms") or [])
    rejected_terms = list(metadata.get("rejected_terms") or [])
    approval_mode = str(metadata.get("approval_mode", ""))
    glossary_index = load_glossary_index(config.workspace.glossary_dir)

    approved_rows: list[dict[str, str]] = []
    actionable_failure = not chapter_records
    for term in approved_terms:
        entry = glossary_index.get(term)
        if entry is None:
            actionable_failure = True
            approved_rows.append(
                {
                    "original_term": term,
                    "thai_term": "missing",
                    "category": "missing",
                    "status": "missing",
                    "path": "missing",
                }
            )
            continue
        approved_rows.append(
            {
                "original_term": entry.original_term,
                "thai_term": entry.thai_term,
                "category": entry.category,
                "status": entry.status,
                "path": str(entry.metadata.get("path", "")),
            }
        )

    path = _stable_report_path(config=config, kind="glossary_decisions", run_id=run_id, output=output)
    text = _render_glossary_decisions_markdown(
        run_id=run_id,
        block_ids=[record.block_id for record in chapter_records],
        approval_mode=approval_mode,
        approved_rows=approved_rows,
        rejected_terms=rejected_terms,
    )
    atomic_write_text(path, text)
    return {
        "path": path,
        "text": text,
        "approved_rows": approved_rows,
        "rejected_terms": rejected_terms,
        "actionable_failure": actionable_failure,
    }


def build_glossary_conflicts_report(
    *,
    config: Any,
    run_id: str | None = None,
    output: Path | None = None,
) -> dict[str, Any]:
    notes = _load_glossary_note_records(config)
    anchor = getattr(config.workspace, "root", None)
    scan_status, scan_path, scan_items = _scan_glossary_scan_artifact(config, run_id)

    approved_notes = [note for note in notes if note["status"] == "approved" and not note["is_quarantine"]]
    effective_approved_notes = approved_notes
    proposed_notes = [note for note in notes if note["status"] == "proposed" and not note["is_quarantine"]]
    rejected_notes = [note for note in notes if note["status"] == "rejected" and not note["is_quarantine"]]
    deprecated_notes = [note for note in notes if note["status"] == "deprecated" and not note["is_quarantine"]]
    quarantine_notes = [note for note in notes if note["is_quarantine"]]
    nonapproved_notes = [note for note in notes if note not in effective_approved_notes]

    alias_owners: dict[str, list[str]] = {}
    for note in notes:
        for alias in note.get("aliases") or []:
            alias_owners.setdefault(str(alias), [])
            if note["original_term"] not in alias_owners[str(alias)]:
                alias_owners[str(alias)].append(note["original_term"])
    alias_collision_lines = [
        f"- {alias} -> {_comma_list(sorted(owners))}" for alias, owners in sorted(alias_owners.items()) if len(owners) > 1
    ]
    if not alias_collision_lines:
        alias_collision_lines.append("- none")

    source_surface_owners: dict[str, list[tuple[str, str, Path, str]]] = {}
    for note in effective_approved_notes:
        original = str(note["original_term"])
        thai = str(note.get("thai_term") or "")
        path = note["path"]
        source_surface_owners.setdefault(original, []).append((original, thai, path, "original"))
        for alias in note.get("aliases") or []:
            source_surface_owners.setdefault(str(alias), []).append((original, thai, path, "alias"))
    source_surface_collision_lines: list[str] = []
    for surface, owners in sorted(source_surface_owners.items()):
        thai_terms = {thai for _, thai, _, _ in owners}
        owner_terms = {original for original, _, _, _ in owners}
        if len(owners) <= 1 or len(owner_terms) <= 1 or len(thai_terms) <= 1:
            continue
        rendered = []
        for original, thai, path, role in sorted(owners, key=lambda item: (item[0], item[3])):
            rendered.append(f"{original} ({role}: {thai or 'none'} | {_relative_report_path(path, anchor)})")
        source_surface_collision_lines.append(f"- {surface} -> {'; '.join(rendered)}")
    if not source_surface_collision_lines:
        source_surface_collision_lines.append("- none")

    approved_overlap_lines: list[str] = []
    ordered_approved = sorted(effective_approved_notes, key=lambda note: (-len(note["original_term"]), note["original_term"]))
    seen_approved_pairs: set[tuple[str, str]] = set()
    for index, left in enumerate(ordered_approved):
        for right in ordered_approved[index + 1 :]:
            left_term = left["original_term"]
            right_term = right["original_term"]
            if left_term == right_term:
                continue
            if left_term in right_term or right_term in left_term:
                longer, shorter = (left_term, right_term) if len(left_term) >= len(right_term) else (right_term, left_term)
                pair = (longer, shorter)
                if pair not in seen_approved_pairs:
                    seen_approved_pairs.add(pair)
                    approved_overlap_lines.append(f"- {longer} contains {shorter}")
    if not approved_overlap_lines:
        approved_overlap_lines.append("- none")

    approved_nonapproved_overlap_lines: list[str] = []
    seen_cross_pairs: set[tuple[str, str]] = set()
    for approved in ordered_approved:
        approved_term = approved["original_term"]
        for other in sorted(nonapproved_notes, key=lambda note: (-len(note["original_term"]), note["original_term"])):
            other_term = other["original_term"]
            if approved_term == other_term:
                continue
            if approved_term in other_term or other_term in approved_term:
                pair = (approved_term, other_term)
                if pair not in seen_cross_pairs:
                    seen_cross_pairs.add(pair)
                    if approved_term == other_term:
                        relation = "matches"
                    elif approved_term in other_term:
                        relation = "inside nonapproved"
                    else:
                        relation = "contains nonapproved"
                    approved_nonapproved_overlap_lines.append(
                        f"- {approved_term} / {other_term} ({relation})"
                    )
    if not approved_nonapproved_overlap_lines:
        approved_nonapproved_overlap_lines.append("- none")

    exact_term_index: dict[str, dict[str, Any]] = {}
    for note in notes:
        if note["status"] == "rejected" or note["is_quarantine"]:
            exact_term_index.setdefault(note["original_term"], note)
            for alias in note.get("aliases") or []:
                exact_term_index.setdefault(str(alias), note)

    scan_terms: list[str] = []
    for item in scan_items:
        term = str(item.get("original_term", "")).strip()
        if term and term not in scan_terms:
            scan_terms.append(term)

    exact_scan_lines: list[str] = []
    for term in scan_terms:
        note = exact_term_index.get(term)
        if note is not None:
            bucket = _note_bucket(note)
            exact_scan_lines.append(
                f"- {term} -> {note['original_term']} ({bucket} | {_relative_report_path(note['path'], anchor)})"
            )
    if not exact_scan_lines:
        exact_scan_lines.append("- none")

    noisy_scan_lines: list[str] = []
    seen_noisy: set[tuple[str, str, str]] = set()
    for term in scan_terms:
        for approved in ordered_approved:
            approved_term = approved["original_term"]
            if term == approved_term:
                continue
            position = term.find(approved_term)
            if position == -1:
                continue
            if position == 0:
                side = "prefix"
            elif position + len(approved_term) == len(term):
                side = "suffix"
            else:
                continue
            key = (term, approved_term, side)
            if key not in seen_noisy:
                seen_noisy.add(key)
                noisy_scan_lines.append(f"- {term} -> {approved_term} ({side})")
    if not noisy_scan_lines:
        noisy_scan_lines.append("- none")

    path = _stable_report_path(config=config, kind="glossary_conflicts", run_id=run_id, output=output)
    text = _render_glossary_conflicts_markdown(
        run_id=run_id,
        notes=notes,
        scan_status=scan_status,
        scan_path=scan_path,
        approved_count=len(approved_notes),
        proposed_count=len(proposed_notes),
        rejected_count=len(rejected_notes),
        deprecated_count=len(deprecated_notes),
        quarantine_count=len(quarantine_notes),
        approved_lines=_render_note_lines(notes=approved_notes, anchor=anchor),
        proposed_lines=_render_note_lines(notes=proposed_notes, anchor=anchor),
        rejected_lines=_render_note_lines(notes=rejected_notes, anchor=anchor),
        deprecated_lines=_render_note_lines(notes=deprecated_notes, anchor=anchor),
        quarantine_lines=_render_note_lines(notes=quarantine_notes, anchor=anchor),
        alias_collision_lines=alias_collision_lines,
        source_surface_collision_lines=source_surface_collision_lines,
        approved_overlap_lines=approved_overlap_lines,
        approved_nonapproved_overlap_lines=approved_nonapproved_overlap_lines,
        exact_scan_lines=exact_scan_lines,
        noisy_scan_lines=noisy_scan_lines,
    )
    atomic_write_text(path, text)
    actionable_failure = any(
        section != ["- none"]
        for section in [
            alias_collision_lines,
            source_surface_collision_lines,
            approved_overlap_lines,
            approved_nonapproved_overlap_lines,
            exact_scan_lines,
            noisy_scan_lines,
        ]
    )
    return {
        "path": path,
        "text": text,
        "notes": notes,
        "scan_status": scan_status,
        "scan_path": scan_path,
        "actionable_failure": actionable_failure,
    }


def build_glossary_audit_report(*, config: Any, run_id: str, output: Path | None = None) -> dict[str, Any]:
    summary = _quiet_status_run(config=config, run_id=run_id)
    glossary_index = load_glossary_index(config.workspace.glossary_dir)
    chapter_ids = list(summary.get("chapter_ids") or [])
    chapter_results: list[dict[str, Any]] = []
    actionable_failure = not chapter_ids

    for chapter_id in chapter_ids:
        output_path, output_text = _load_chapter_output(config, chapter_id)
        exists = output_text is not None
        expected_terms: list[str] = []
        missing_thai_terms: list[str] = []
        subset_terms_not_found: list[str] = []
        wrong_variants: list[str] = []
        source_error = ""

        try:
            _, blocks = _load_chapter_source_and_blocks(config, chapter_id)
            subset = _resolve_glossary_subset(blocks, glossary_index)
        except Exception as exc:
            subset = []
            source_error = str(exc)
            actionable_failure = True

        expected_terms = [entry.original_term for entry in subset]

        if output_text is None:
            missing_thai_terms = [entry.thai_term for entry in subset if entry.thai_term]
            subset_terms_not_found = expected_terms[:]
            if expected_terms:
                actionable_failure = True
        else:
            for entry in subset:
                if entry.thai_term and entry.thai_term not in output_text:
                    missing_thai_terms.append(entry.thai_term)
                    subset_terms_not_found.append(entry.original_term)
                elif not entry.thai_term:
                    subset_terms_not_found.append(entry.original_term)
            for issue in _scan_cleanliness_text(output_text):
                if issue.startswith("wrong glossary variant: "):
                    variant = issue.removeprefix("wrong glossary variant: ")
                    if variant not in wrong_variants:
                        wrong_variants.append(variant)
            if missing_thai_terms or subset_terms_not_found or wrong_variants:
                actionable_failure = True

        chapter_results.append(
            {
                "chapter_id": chapter_id,
                "output_path": str(output_path),
                "exists": exists,
                "source_error": source_error,
                "expected_terms": expected_terms,
                "missing_thai_terms": missing_thai_terms,
                "subset_terms_not_found": subset_terms_not_found,
                "wrong_variants": wrong_variants,
            }
        )

    path = _stable_report_path(config=config, kind="glossary_audit", run_id=run_id, output=output)
    text = _render_glossary_audit_markdown(run_id=run_id, chapter_results=chapter_results)
    atomic_write_text(path, text)
    return {
        "path": path,
        "text": text,
        "summary": summary,
        "chapter_results": chapter_results,
        "actionable_failure": actionable_failure,
    }


def build_glossary_guard_report(*, config: Any, run_id: str, output: Path | None = None) -> dict[str, Any]:
    summary = _quiet_status_run(config=config, run_id=run_id)
    chapter_ids = list(summary.get("chapter_ids") or [])
    chapter_results: list[dict[str, Any]] = []

    note_records = _load_scan_note_records(config.workspace.glossary_dir)
    blocked_exact_terms = _blocked_exact_terms(note_records)
    blocked_exact_terms.update(_historical_rejected_terms(config))
    approved_terms = _noise_anchor_terms(note_records)
    quarantine_terms = {
        str(note.get("original_term") or "").strip()
        for note in note_records
        if _scan_note_bucket(note) == "quarantine"
    }
    quarantine_terms = {term for term in quarantine_terms if term}

    for chapter_id in chapter_ids:
        _, blocks = _load_chapter_source_and_blocks(config, chapter_id)
        raw_terms: list[str] = []
        for block in blocks:
            raw_terms.extend(extract_candidate_terms(block.source_text or block.text))
        raw_terms = _dedupe_candidates(raw_terms)

        filtered_items = build_glossary_scan_queue(config, blocks, exclude_existing=False)
        kept_terms = [str(item.get("original_term", "")).strip() for item in filtered_items if str(item.get("original_term", "")).strip()]
        kept_terms_set = set(kept_terms)

        removed_blocked_exact: list[str] = []
        removed_noisy: list[str] = []
        pre_substring_terms: list[str] = []
        for term in raw_terms:
            if term in blocked_exact_terms:
                removed_blocked_exact.append(term)
                continue
            if _is_obvious_noise_candidate(term, approved_terms, quarantine_terms):
                removed_noisy.append(term)
                continue
            pre_substring_terms.append(term)

        combined_text = "\n".join((block.source_text or block.text) for block in blocks)
        post_substring_terms = _prune_substring_fragment_candidates(combined_text, pre_substring_terms)
        post_substring_set = set(post_substring_terms)
        removed_substring = [term for term in pre_substring_terms if term not in post_substring_set]

        chapter_results.append(
            {
                "chapter_id": chapter_id,
                "raw_count": len(raw_terms),
                "filtered_count": len(kept_terms),
                "removed_count": max(0, len(raw_terms) - len(kept_terms)),
                "removed_blocked_exact": removed_blocked_exact,
                "removed_noisy": removed_noisy,
                "removed_substring": removed_substring,
                "kept_terms": kept_terms,
                "kept_terms_match_queue": kept_terms_set == post_substring_set,
            }
        )

    path = _stable_report_path(config=config, kind="glossary_guard", run_id=run_id, output=output)
    text = _render_glossary_guard_markdown(run_id=run_id, chapter_results=chapter_results)
    atomic_write_text(path, text)
    actionable_failure = any(not chapter["kept_terms_match_queue"] for chapter in chapter_results)
    return {
        "path": path,
        "text": text,
        "summary": summary,
        "chapter_results": chapter_results,
        "actionable_failure": actionable_failure,
    }


def build_preflight_report(*, config: Any, output: Path | None = None) -> dict[str, Any]:
    summary = build_preflight_summary(config)
    path = _stable_report_path(config=config, kind="preflight_report", run_id=None, output=output)
    text = _render_preflight_markdown(summary=summary)
    atomic_write_text(path, text)
    return {
        "path": path,
        "text": text,
        "summary": summary,
        "actionable_failure": summary.get("status") != "ready",
    }


def build_recovery_drill_report(*, config: Any, output: Path | None = None) -> dict[str, Any]:
    workspace_root = config.workspace.root
    git_available, inside = _git_capture(workspace_root, "rev-parse", "--is-inside-work-tree")
    branch_ok, branch = _git_capture(workspace_root, "branch", "--show-current")
    head_ok, head = _git_capture(workspace_root, "rev-parse", "--short", "HEAD")
    origin_ok, origin = _git_capture(workspace_root, "remote", "get-url", "origin")

    canonical_paths = [
        "PROJECT_BRAIN.md",
        "IMPLEMENT_PLAN.md",
        "OPERATOR_MANUAL.md",
    ]
    canonical_rows: list[dict[str, str]] = []
    canonical_fail = False
    for relative_path in canonical_paths:
        tracked_ok, tracked_output = _git_capture(workspace_root, "ls-files", "--error-unmatch", relative_path)
        restore_ok, _ = _git_capture(workspace_root, "show", f"HEAD:{relative_path}")
        detail = "tracked and restorable"
        if not tracked_ok:
            detail = tracked_output or "not tracked"
        elif not restore_ok:
            detail = "missing from HEAD"
        canonical_rows.append(
            {
                "path": relative_path,
                "tracked": "yes" if tracked_ok else "no",
                "restorable_from_head": "yes" if restore_ok else "no",
                "detail": detail,
            }
        )
        if not tracked_ok or not restore_ok:
            canonical_fail = True

    runtime_paths = ["03_Raw", "04_Work", "05_Output", "06_Logs"]
    runtime_rows: list[dict[str, str]] = []
    runtime_fail = False
    for relative_path in runtime_paths:
        ignored_ok, ignored_output = _git_capture(workspace_root, "check-ignore", relative_path)
        tracked_ok, tracked_output = _git_capture(workspace_root, "ls-files", relative_path)
        tracked_entries = [line for line in tracked_output.splitlines() if line.strip()] if tracked_ok else []
        detail = "ignored and untracked"
        if not ignored_ok:
            detail = "not ignored by git"
        elif tracked_entries:
            detail = f"tracked entries present: {_comma_list(tracked_entries)}"
        runtime_rows.append(
            {
                "path": relative_path,
                "ignored": "yes" if ignored_ok else "no",
                "tracked_entries": str(len(tracked_entries)),
                "detail": detail,
            }
        )
        if not ignored_ok or tracked_entries:
            runtime_fail = True

    checks: list[dict[str, str]] = [
        {
            "check": "git_work_tree",
            "status": "ok" if git_available and inside.strip().lower() == "true" else "fail",
            "detail": "inside git work tree" if git_available and inside.strip().lower() == "true" else "git unavailable or outside work tree",
        },
        {
            "check": "remote_origin",
            "status": "ok" if origin_ok and origin else "fail",
            "detail": origin or "origin missing",
        },
        {
            "check": "canonical_docs_restorable",
            "status": "ok" if not canonical_fail else "fail",
            "detail": "all canonical docs tracked and restorable from HEAD" if not canonical_fail else "one or more canonical docs are not safely restorable",
        },
        {
            "check": "runtime_dirs_ignored",
            "status": "ok" if not runtime_fail else "fail",
            "detail": "runtime directories are ignored and untracked" if not runtime_fail else "runtime ignore policy drift detected",
        },
    ]

    overall_status = "accepted" if all(item["status"] == "ok" for item in checks) else "failed"
    next_safe_action = (
        "Recovery baseline is ready. Use git restore for canonical docs and keep runtime state out of git."
        if overall_status == "accepted"
        else "Fix git tracking/ignore drift before relying on recovery drills."
    )
    summary = {
        "overall_status": overall_status,
        "workspace_root": str(workspace_root),
        "branch": branch if branch_ok else "",
        "head": head if head_ok else "",
        "origin": origin if origin_ok else "",
        "next_safe_action": next_safe_action,
    }
    path = _stable_report_path(config=config, kind="recovery_drill", run_id=None, output=output)
    text = _render_recovery_drill_markdown(
        summary=summary,
        checks=checks,
        canonical_rows=canonical_rows,
        runtime_rows=runtime_rows,
    )
    atomic_write_text(path, text)
    return {
        "path": path,
        "text": text,
        "summary": summary,
        "checks": checks,
        "actionable_failure": overall_status != "accepted",
    }


def build_product_review_report(*, config: Any, run_id: str, output: Path | None = None) -> dict[str, Any]:
    summary = _quiet_status_run(config=config, run_id=run_id)
    preflight = build_preflight_summary(config)
    root = config.workspace.root

    canonical_docs = [
        "PROJECT_BRAIN.md",
        "IMPLEMENT_PLAN.md",
        "OPERATOR_MANUAL.md",
    ]
    retired_docs = [
        "MASTER_PLAN.md",
        "REPORT.md",
        "SUMMARY.md",
    ]
    required_product_files = [
        "NOVEL_SETUP_PLAYBOOK.md",
        "FETCH_ADAPTER_PLAYBOOK.md",
        "RESEARCH_PROFILE_PLAYBOOK.md",
        "RESEARCH_PROFILE.yaml",
        "00_Templates/Novel-Profile.yaml",
        "00_Templates/Research-Profile.yaml",
        "00_Templates/Batch-Rollout-Checklist.md",
        "00_Templates/Worker-Bounded-Batch-Prompt.md",
        "novel_pipeline/operator_ui.py",
        "novel_pipeline/preflight.py",
        "novel_pipeline/project_setup.py",
    ]

    canonical_present = [name for name in canonical_docs if (root / name).exists()]
    canonical_missing = [name for name in canonical_docs if not (root / name).exists()]
    retired_present = [name for name in retired_docs if (root / name).exists()]
    retired_absent = [name for name in retired_docs if not (root / name).exists()]
    required_present = [name for name in required_product_files if (root / name).exists()]
    required_missing = [name for name in required_product_files if not (root / name).exists()]

    chapter_ids = list(summary.get("chapter_ids") or [])
    output_rows: list[dict[str, Any]] = []
    output_has_issues = False
    for chapter_id in chapter_ids:
        output_path, text = _load_chapter_output(config, chapter_id)
        issues: list[str] = []
        if text is None:
            issues.append("missing final output")
        else:
            issues.extend(_scan_cleanliness_text(text))
        if issues:
            output_has_issues = True
        output_rows.append(
            {
                "chapter_id": chapter_id,
                "exists": text is not None,
                "issues": issues,
                "path": str(output_path),
            }
        )

    current_failed_blocks = list(summary.get("current_failed_blocks") or [])
    raw_manual_actions = [str(item).strip() for item in (summary.get("manual_actions") or []) if str(item).strip()]
    effective_manual_actions = [item for item in raw_manual_actions if item.lower() != "none"]
    glossary_records = list(
        RunLedger(config.ledger_path).iter_records(run_id=run_id, stage="glossary_approved", status="completed")
    )
    glossary_approval_present = any(re.fullmatch(r"ch\d+", record.block_id) for record in glossary_records)
    recovery_evidence = bool(summary.get("historical_failed_records", 0)) and not current_failed_blocks

    accepted_checks: list[dict[str, str]] = [
        {
            "check": "preflight",
            "status": "ok" if not preflight.get("blocking_reasons") and not preflight.get("warnings") else ("warn" if not preflight.get("blocking_reasons") else "fail"),
            "detail": preflight.get("status", "unknown"),
        },
        {
            "check": "run_complete",
            "status": "ok" if chapter_ids and not current_failed_blocks and not effective_manual_actions else "fail",
            "detail": f"chapters={_comma_list(chapter_ids)}; failed={_comma_list(current_failed_blocks)}; manual={_comma_list(effective_manual_actions)}",
        },
        {
            "check": "final_outputs_clean",
            "status": "ok" if chapter_ids and not output_has_issues else "fail",
            "detail": "all chapter outputs present and clean" if chapter_ids and not output_has_issues else "missing output or cleanliness issue detected",
        },
        {
            "check": "glossary_approval_evidence",
            "status": "ok" if glossary_approval_present else "fail",
            "detail": f"glossary_approved records: {len(glossary_records)}",
        },
        {
            "check": "recovery_evidence",
            "status": "ok" if recovery_evidence else "warn",
            "detail": f"historical_failed_records={summary.get('historical_failed_records', 0)}; current_failed={_comma_list(current_failed_blocks)}",
        },
        {
            "check": "canonical_docs",
            "status": "ok" if not canonical_missing and not retired_present else "fail",
            "detail": f"missing={_comma_list(canonical_missing)}; retired_present={_comma_list(retired_present)}",
        },
        {
            "check": "required_product_files",
            "status": "ok" if not required_missing else "fail",
            "detail": f"missing={_comma_list(required_missing)}",
        },
    ]

    if any(item["status"] == "fail" for item in accepted_checks):
        overall_status = "failed"
    elif any(item["status"] == "warn" for item in accepted_checks):
        overall_status = "degraded"
    else:
        overall_status = "accepted"

    path = _stable_report_path(config=config, kind="product_review", run_id=run_id, output=output)
    text = _render_product_review_markdown(
        run_id=run_id,
        overall_status=overall_status,
        preflight=preflight,
        summary=summary,
        canonical_present=canonical_present,
        canonical_missing=canonical_missing,
        retired_absent=retired_absent,
        retired_present=retired_present,
        required_present=required_present,
        required_missing=required_missing,
        output_rows=output_rows,
        accepted_checks=accepted_checks,
    )
    atomic_write_text(path, text)
    return {
        "path": path,
        "text": text,
        "summary": summary,
        "preflight": preflight,
        "accepted_checks": accepted_checks,
        "overall_status": overall_status,
        "actionable_failure": overall_status != "accepted",
    }
