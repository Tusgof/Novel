from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import re
from typing import Any

from novel_pipeline.artifacts import batch_glossary_scan_artifact_path
from novel_pipeline.files import atomic_write_text, read_text_if_exists
from novel_pipeline.glossary_support import load_glossary_index, parse_glossary_note
from novel_pipeline.ledger import RunLedger
from novel_pipeline.pipeline import (
    _load_chapter_source_and_blocks,
    _resolve_glossary_subset,
    inspect_block_command,
    status_run,
    validate_formatted_text,
)

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
