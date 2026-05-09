from __future__ import annotations

import contextlib
import io
import json
import re
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlparse

from novel_pipeline.config import load_yaml_mapping
from novel_pipeline.files import atomic_write_json, atomic_write_text, read_text_if_exists
from novel_pipeline.glossary_support import write_glossary_note
from novel_pipeline.ledger import RunLedger
from novel_pipeline.pipeline import (
    ManualActionRequired,
    _commit_stage,
    _default_term_template,
    _load_chapter_source_and_blocks,
    _read_glossary_scan_artifact,
    _read_glossary_scan_items,
    _revalidate_glossary_queue_items,
    inspect_block_command,
    rerun_block_pipeline,
    run_batch_pipeline,
    resume_pipeline,
    status_run,
)
from novel_pipeline.preflight import build_preflight_summary
from novel_pipeline.prompts import PromptStore
from novel_pipeline.project_setup import initialize_novel_project, render_research_profile_yaml
from novel_pipeline.stages.glossary import build_term_suggestion
from novel_pipeline.text_utils import parse_chapter_range
from novel_pipeline.reports import (
    build_checkpoint_report,
    build_cleanliness_report,
    build_product_review_report,
    build_glossary_audit_report,
    build_glossary_conflicts_report,
    build_glossary_decisions_report,
    build_glossary_guard_report,
    build_provider_usage_report,
)
from novel_pipeline.types import AppConfig, GlossaryEntry, ResearchProfile, TermSuggestion


def _latest_run_id(config: AppConfig) -> str | None:
    ledger = RunLedger(config.ledger_path)
    last_run_id: str | None = None
    for record in ledger.iter_records():
        last_run_id = record.run_id
    return last_run_id


def _list_run_ids(config: AppConfig) -> list[str]:
    ledger = RunLedger(config.ledger_path)
    run_ids: list[str] = []
    seen: set[str] = set()
    for record in ledger.iter_records():
        if record.run_id not in seen:
            seen.add(record.run_id)
            run_ids.append(record.run_id)
    return run_ids


def _quiet_status_run(config: AppConfig, run_id: str | None) -> dict[str, Any]:
    with contextlib.redirect_stdout(io.StringIO()):
        return status_run(config=config, run_id=run_id)


def _quiet_inspect_block(config: AppConfig, run_id: str, block_id: str) -> dict[str, Any]:
    with contextlib.redirect_stdout(io.StringIO()):
        return inspect_block_command(config=config, run_id=run_id, block_id=block_id)


def _safe_workspace_path(config: AppConfig, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = (config.workspace.root / raw_path).resolve()
    else:
        candidate = candidate.resolve()
    workspace_root = config.workspace.root.resolve()
    try:
        candidate.relative_to(workspace_root)
    except ValueError as exc:
        raise ValueError("Path is outside the workspace root.") from exc
    if candidate.suffix.lower() not in {".md", ".json", ".txt", ".yaml", ".yml"}:
        raise ValueError("Unsupported file type for operator viewer.")
    if not candidate.exists():
        raise ValueError("Requested file does not exist.")
    return candidate


def _parse_init_novel_aliases(raw_aliases: Any) -> list[str]:
    if raw_aliases is None:
        return []
    if isinstance(raw_aliases, (list, tuple)):
        raw_items = raw_aliases
    else:
        raw_items = re.split(r"[,\n]+", str(raw_aliases))
    aliases: list[str] = []
    for item in raw_items:
        alias = str(item).strip()
        if alias:
            aliases.append(alias)
    return aliases


def _parse_text_list(raw_items: Any) -> list[str]:
    if raw_items is None:
        return []
    if isinstance(raw_items, (list, tuple)):
        values = raw_items
    else:
        values = re.split(r"[,\n]+", str(raw_items))
    items: list[str] = []
    for item in values:
        text = str(item).strip()
        if text:
            items.append(text)
    return items


def _research_profile_path(config: AppConfig) -> Path:
    return config.workspace.root / "RESEARCH_PROFILE.yaml"


def _load_research_profile_mapping(config: AppConfig) -> dict[str, Any] | None:
    path = _research_profile_path(config)
    if not path.exists():
        return None
    return load_yaml_mapping(path)


def _research_profile_snapshot(config: AppConfig) -> dict[str, Any]:
    profile = config.research_profile
    if profile is None:
        payload = _load_research_profile_mapping(config)
        if payload is not None:
            profile = ResearchProfile.from_mapping(payload)
    if profile is None:
        profile = ResearchProfile(
            title="",
            source_url=config.source.toc_url.strip(),
            status="pending",
        )
    return {
        "title": profile.title,
        "aliases": list(profile.aliases),
        "source_url": profile.source_url,
        "status": profile.status,
        "synopsis": profile.synopsis,
        "tags": list(profile.tags),
        "style_notes": profile.style_notes,
        "reader_expectations": profile.reader_expectations,
        "review_summary": profile.review_summary,
        "last_reviewed_at": profile.last_reviewed_at,
        "reviewed_by": profile.reviewed_by,
        "terminology": list(profile.terminology),
        "reference_links": list(profile.reference_links),
        "notes": profile.notes,
    }


def generate_operator_report(
    *,
    config: AppConfig,
    run_id: str,
    kind: str,
    chapter_ids: list[str] | None = None,
) -> dict[str, Any]:
    if kind == "checkpoint":
        return build_checkpoint_report(config=config, run_id=run_id)
    if kind == "cleanliness":
        return build_cleanliness_report(config=config, run_id=run_id, chapter_ids=chapter_ids or None)
    if kind == "provider-usage":
        return build_provider_usage_report(config=config, run_id=run_id)
    if kind == "glossary-decisions":
        return build_glossary_decisions_report(config=config, run_id=run_id)
    if kind == "glossary-conflicts":
        return build_glossary_conflicts_report(config=config, run_id=run_id)
    if kind == "glossary-audit":
        return build_glossary_audit_report(config=config, run_id=run_id)
    if kind == "glossary-guard":
        return build_glossary_guard_report(config=config, run_id=run_id)
    if kind == "product-review":
        return build_product_review_report(config=config, run_id=run_id)
    raise ValueError(f"Unsupported report kind: {kind}")


def build_operator_snapshot(config: AppConfig, run_id: str | None = None) -> dict[str, Any]:
    resolved_run_id = run_id or _latest_run_id(config)
    status = _quiet_status_run(config, resolved_run_id) if resolved_run_id else {"runs": []}
    return {
        "run_id": resolved_run_id,
        "available_run_ids": _list_run_ids(config),
        "status": status,
        "research_profile_path": str(config.workspace.root / "RESEARCH_PROFILE.yaml"),
        "research_profile": _research_profile_snapshot(config),
        "research_readiness": config.research_readiness_summary(),
        "preflight": build_preflight_summary(config),
    }


def build_glossary_queue_snapshot(config: AppConfig, run_id: str) -> dict[str, Any]:
    artifact = _read_glossary_scan_artifact(config, run_id=run_id)
    chapter_ids = list(artifact.get("chapter_ids", [])) if isinstance(artifact, dict) else []
    queue_items = _read_glossary_scan_items(config, run_id=run_id)
    if not queue_items:
        return {
            "run_id": run_id,
            "chapter_ids": chapter_ids,
            "items": [],
            "removed_terms": [],
        }

    blocks = []
    for chapter_id in chapter_ids:
        _, chapter_blocks = _load_chapter_source_and_blocks(config, chapter_id)
        blocks.extend(chapter_blocks)
    filtered_items, removed_terms = _revalidate_glossary_queue_items(config, blocks, queue_items)
    return {
        "run_id": run_id,
        "chapter_ids": chapter_ids,
        "items": filtered_items,
        "removed_terms": removed_terms,
    }


def _read_batch_glossary_artifact(config: AppConfig, run_id: str) -> dict[str, Any]:
    artifact = _read_glossary_scan_artifact(config, run_id=run_id)
    if artifact is None:
        raise ValueError(f"No batch glossary scan artifact found for run {run_id}.")
    return artifact


def _write_batch_glossary_artifact(config: AppConfig, run_id: str, payload: dict[str, Any]) -> None:
    path = config.workspace.work / "_batch" / run_id / "glossary_scan.json"
    atomic_write_json(path, payload)


def _artifact_decisions(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    decisions = artifact.get("decisions")
    if not isinstance(decisions, list):
        return []
    return [item for item in decisions if isinstance(item, dict)]


def build_glossary_suggestion_snapshot(config: AppConfig, run_id: str, term: str) -> dict[str, Any]:
    queue_snapshot = build_glossary_queue_snapshot(config, run_id)
    queue_item = next((item for item in queue_snapshot["items"] if item.get("original_term") == term), None)
    if queue_item is None:
        raise ValueError(f"Term '{term}' is not in the current glossary queue.")
    prompt_store = PromptStore(config.workspace.prompts)
    provider_runner = config.provider_for_stage("term_suggestion")
    from novel_pipeline.providers.base import ProviderRunner
    suggestion = build_term_suggestion(
        config=config,
        provider_runner=ProviderRunner(provider_runner),
        prompt_store=prompt_store,
        term=term,
        context=str(queue_item.get("context", "")),
    )
    return {
        "run_id": run_id,
        "term": term,
        "chapter_id": queue_item.get("chapter_id", ""),
        "first_seen_block": queue_item.get("first_seen_block", ""),
        "category": suggestion.category,
        "context": list(suggestion.context),
        "options": list(suggestion.options),
        "rationales": list(suggestion.rationales),
        "rationale": suggestion.rationale,
        "provider": suggestion.provider,
    }


def _load_term_template(config: AppConfig) -> str:
    template_path = config.workspace.templates_dir / "Term-Template.md"
    template_text = read_text_if_exists(template_path)
    if template_text is None:
        return _default_term_template()
    return template_text


def _decision_metadata(artifact: dict[str, Any]) -> tuple[list[str], list[str]]:
    approved_terms: list[str] = []
    rejected_terms: list[str] = []
    for item in _artifact_decisions(artifact):
        term = str(item.get("original_term") or "").strip()
        decision = str(item.get("decision") or "").strip().lower()
        if not term:
            continue
        if decision == "approve":
            approved_terms.append(term)
        elif decision == "reject":
            rejected_terms.append(term)
    return approved_terms, rejected_terms


def execute_glossary_decision(
    *,
    config: AppConfig,
    run_id: str,
    term: str,
    decision: str,
    thai_term: str = "",
    note: str = "",
) -> dict[str, Any]:
    artifact = _read_batch_glossary_artifact(config, run_id)
    chapter_ids = list(artifact.get("chapter_ids", []))
    queue_snapshot = build_glossary_queue_snapshot(config, run_id)
    queue_item = next((item for item in queue_snapshot["items"] if item.get("original_term") == term), None)
    if queue_item is None:
        raise ValueError(f"Term '{term}' is not in the current glossary queue.")

    normalized_decision = decision.strip().lower()
    if normalized_decision not in {"approve", "reject"}:
        raise ValueError("decision must be 'approve' or 'reject'.")
    if normalized_decision == "approve" and not thai_term.strip():
        raise ValueError("approve requires a selected thai_term.")

    entry = GlossaryEntry(
        original_term=term,
        thai_term=thai_term.strip(),
        category=str(queue_item.get("category", "")) or "term",
        status="approved" if normalized_decision == "approve" else "rejected",
        source_language=str(queue_item.get("source_language", config.source_language)),
        novel=str(queue_item.get("novel", config.novel_id)),
        description=note.strip(),
    )
    write_glossary_note(
        template_text=_load_term_template(config),
        glossary_dir=config.workspace.glossary_dir,
        entry=entry,
        first_seen_chapter=str(queue_item.get("chapter_id", "")),
        first_seen_block=str(queue_item.get("first_seen_block", "block-001")),
    )

    decisions = [item for item in _artifact_decisions(artifact) if str(item.get("original_term") or "").strip() != term]
    decisions.append(
        {
            "original_term": term,
            "decision": normalized_decision,
            "thai_term": entry.thai_term,
            "category": entry.category,
            "chapter_id": str(queue_item.get("chapter_id", "")),
            "first_seen_block": str(queue_item.get("first_seen_block", "")),
            "note": note.strip(),
        }
    )
    refreshed_queue = build_glossary_queue_snapshot(config, run_id)
    filtered_items = [item for item in refreshed_queue["items"] if item.get("original_term") != term]
    # Re-run revalidation against current note state to remove rejected terms and preserve ordering.
    blocks = []
    for chapter_id in chapter_ids:
        _, chapter_blocks = _load_chapter_source_and_blocks(config, chapter_id)
        blocks.extend(chapter_blocks)
    filtered_items, removed_terms = _revalidate_glossary_queue_items(config, blocks, filtered_items)
    updated_artifact = {
        "schema_version": artifact.get("schema_version", 1),
        "scope": artifact.get("scope", {"type": "batch", "id": run_id}),
        "chapter_ids": chapter_ids,
        "items": filtered_items,
        "decisions": decisions,
    }
    _write_batch_glossary_artifact(config, run_id, updated_artifact)

    committed = False
    if not filtered_items:
        ledger = RunLedger(config.ledger_path)
        approved_terms, rejected_terms = _decision_metadata(updated_artifact)
        metadata = {
            "approval_mode": "operator_ui",
            "approved_terms_count": len(approved_terms),
            "rejected_terms_count": len(rejected_terms),
            "approved_terms": approved_terms,
            "rejected_terms": rejected_terms,
        }
        for chapter_id in chapter_ids:
            if not ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="glossary_approved"):
                _commit_stage(
                    ledger,
                    run_id,
                    chapter_id,
                    "glossary_approved",
                    "completed",
                    provider="local",
                    metadata=metadata,
                )
        committed = True

    return {
        "run_id": run_id,
        "term": term,
        "decision": normalized_decision,
        "queue": build_glossary_queue_snapshot(config, run_id),
        "snapshot": build_operator_snapshot(config, run_id=run_id),
        "removed_terms": removed_terms,
        "committed": committed,
    }


def execute_operator_action(
    *,
    config: AppConfig,
    action: str,
    run_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    if action in {"resume", "rerun-block"}:
        config.ensure_translation_ready(bounded=True)
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        init_novel_paths: dict[str, str] | None = None
        if action == "run-batch":
            chapter_range = str(payload.get("chapter_range") or "").strip()
            stop_after = str(payload.get("stop_after") or "").strip()
            if not run_id or not chapter_range:
                raise ValueError("run-batch requires run_id and chapter_range.")
            if stop_after not in {"", "glossary-scan"}:
                raise ValueError("run-batch only supports stop_after='' or 'glossary-scan'.")
            chapter_ids = parse_chapter_range(chapter_range)
            if not chapter_ids:
                raise ValueError("run-batch requires a non-empty chapter range.")
            if stop_after == "":
                config.ensure_translation_ready(bounded=True)
                stop_after_arg = None
            else:
                stop_after_arg = "glossary-scan"
            run_batch_pipeline(
                config=config,
                chapter_ids=chapter_ids,
                run_id=run_id,
                force=False,
                stop_after=stop_after_arg,
                manual_action_mode="stop",
            )
        elif action == "resume":
            until_chapter = str(payload.get("until_chapter") or "").strip() or None
            until_block = str(payload.get("until_block") or "").strip() or None
            if not until_chapter and not until_block:
                raise ValueError("resume requires until_chapter or until_block.")
            resume_pipeline(
                config=config,
                run_id=run_id,
                force=False,
                manual_action_mode="stop",
                until_chapter=until_chapter,
                until_block=until_block,
            )
        elif action == "rerun-block":
            block_id = str(payload.get("block_id") or "").strip()
            from_stage = str(payload.get("from_stage") or "").strip()
            if not block_id or not from_stage:
                raise ValueError("rerun-block requires block_id and from_stage.")
            rerun_block_pipeline(
                config=config,
                run_id=run_id,
                block_id=block_id,
                from_stage=from_stage,
            )
        elif action == "init-novel":
            project_root = str(payload.get("project_root") or "").strip()
            title = str(payload.get("title") or "").strip()
            source_url = str(payload.get("source_url") or "").strip()
            if not project_root or not title or not source_url:
                raise ValueError("init-novel requires project_root, title, and source_url.")
            result = initialize_novel_project(
                template_config=config,
                project_root=Path(project_root),
                title=title,
                source_url=source_url,
                novel_id=str(payload.get("novel_id") or "").strip() or None,
                aliases=_parse_init_novel_aliases(payload.get("aliases")),
                source_language=str(payload.get("source_language") or "").strip(),
                target_language=str(payload.get("target_language") or "").strip(),
                genre=str(payload.get("genre") or "").strip(),
                adapter=str(payload.get("adapter") or "").strip(),
                style_profile=str(payload.get("style_profile") or "").strip(),
            )
            init_novel_paths = {key: str(value) for key, value in result.items()}
        elif action == "save-research-profile":
            profile_path = _research_profile_path(config)
            current_payload = _load_research_profile_mapping(config)
            if current_payload is None and config.research_profile is not None:
                current_payload = config.research_profile.to_dict()
            merged_payload = dict(current_payload or {})
            merged_payload.setdefault("source_url", config.source.toc_url.strip())
            merged_payload.setdefault("status", "pending")
            for field_name in (
                "title",
                "source_url",
                "status",
                "synopsis",
                "style_notes",
                "reader_expectations",
                "review_summary",
                "last_reviewed_at",
                "reviewed_by",
                "notes",
            ):
                if field_name in payload:
                    merged_payload[field_name] = str(payload.get(field_name) or "").strip()
            if "aliases" in payload:
                merged_payload["aliases"] = _parse_text_list(payload.get("aliases"))
            if "tags" in payload:
                merged_payload["tags"] = _parse_text_list(payload.get("tags"))
            if "terminology" in payload:
                merged_payload["terminology"] = _parse_text_list(payload.get("terminology"))
            if "reference_links" in payload:
                merged_payload["reference_links"] = _parse_text_list(payload.get("reference_links"))
            profile = ResearchProfile.from_mapping(merged_payload)
            atomic_write_text(profile_path, render_research_profile_yaml(profile))
            config.research_profile = profile
            print(f"Saved research profile to {profile_path}")
        else:
            raise ValueError(f"Unsupported operator action: {action}")

    snapshot = build_operator_snapshot(config, run_id=run_id or None)
    if init_novel_paths is not None:
        snapshot["init_novel_paths"] = init_novel_paths
    return {
        "action": action,
        "run_id": run_id,
        "output": buffer.getvalue(),
        "paths": init_novel_paths,
        "snapshot": snapshot,
    }


def _render_operator_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Novel Operator</title>
  <style>
    :root {
      --bg: #f4f5f7;
      --surface: #ffffff;
      --surface-alt: #eef1f5;
      --text: #16181d;
      --muted: #5f6673;
      --border: #d9dee8;
      --accent: #0f62fe;
      --danger: #c0362c;
      --ok: #1f8f50;
      --shadow: 0 1px 2px rgba(16,24,40,.04), 0 8px 24px rgba(16,24,40,.06);
      --radius: 8px;
      font-family: "Segoe UI", Tahoma, sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--text); }
    .shell {
      min-height: 100svh;
      display: grid;
      grid-template-columns: 280px minmax(0, 1fr);
    }
    .nav {
      background: #111827;
      color: #f9fafb;
      padding: 20px 18px;
      border-right: 1px solid rgba(255,255,255,.08);
    }
    .nav h1 {
      margin: 0 0 6px;
      font-size: 18px;
      font-weight: 700;
    }
    .nav p {
      margin: 0 0 18px;
      color: #c7ced9;
      font-size: 13px;
      line-height: 1.4;
    }
    .nav section { margin-bottom: 20px; }
    .nav label, .panel label {
      display: block;
      margin-bottom: 6px;
      font-size: 12px;
      font-weight: 600;
      color: inherit;
    }
    .nav input, .panel input, .panel select, .nav textarea, .panel textarea {
      width: 100%;
      height: 38px;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 0 10px;
      background: white;
      color: var(--text);
    }
    .nav textarea, .panel textarea {
      height: auto;
      min-height: 86px;
      padding: 8px 10px;
      resize: vertical;
    }
    .nav input { background: rgba(255,255,255,.98); }
    .btn-row, .grid-btns {
      display: grid;
      gap: 8px;
    }
    .grid-btns { grid-template-columns: 1fr 1fr; }
    button {
      height: 36px;
      border: 1px solid transparent;
      border-radius: 6px;
      padding: 0 12px;
      font-weight: 600;
      cursor: pointer;
      background: var(--surface-alt);
      color: var(--text);
    }
    button.primary {
      background: var(--accent);
      color: white;
    }
    button.ghost-dark {
      background: rgba(255,255,255,.08);
      color: #f9fafb;
      border-color: rgba(255,255,255,.12);
    }
    .main {
      padding: 20px;
      display: grid;
      gap: 18px;
      align-content: start;
    }
    .topbar {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 12px;
    }
    .topbar h2 {
      margin: 0;
      font-size: 24px;
    }
    .topbar p {
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 13px;
    }
    .metrics {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }
    .metric, .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }
    .metric {
      padding: 14px 16px;
      min-height: 94px;
    }
    .metric .label {
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 8px;
    }
    .metric .value {
      font-size: 24px;
      font-weight: 700;
    }
    .metric .sub {
      margin-top: 6px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
      word-break: break-word;
    }
    .layout {
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(320px, .7fr);
      gap: 18px;
    }
    .panel {
      padding: 16px;
    }
    .panel h3 {
      margin: 0 0 6px;
      font-size: 16px;
    }
    .panel p.meta {
      margin: 0 0 14px;
      font-size: 12px;
      color: var(--muted);
    }
    .table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    .table th, .table td {
      text-align: left;
      padding: 10px 8px;
      border-top: 1px solid var(--border);
      vertical-align: top;
    }
    .table th {
      color: var(--muted);
      font-size: 12px;
      font-weight: 600;
    }
    .stack { display: grid; gap: 14px; }
    .pill {
      display: inline-block;
      border-radius: 999px;
      padding: 4px 8px;
      font-size: 11px;
      font-weight: 700;
      background: var(--surface-alt);
      color: var(--text);
    }
    .pill.ok { background: #e7f7ee; color: var(--ok); }
    .pill.danger { background: #fdeceb; color: var(--danger); }
    .mono {
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      font-size: 12px;
    }
    .actions-list, .artifact-list, .issues-list {
      display: grid;
      gap: 8px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .artifact-list a, .report-link {
      color: var(--accent);
      text-decoration: none;
      word-break: break-all;
    }
    .report-link:hover, .artifact-list a:hover { text-decoration: underline; }
    .inspect-grid {
      display: grid;
      grid-template-columns: 1fr 1fr auto;
      gap: 8px;
      margin-bottom: 12px;
    }
    .empty {
      color: var(--muted);
      font-size: 13px;
    }
    .footer-note {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
    }
    @media (max-width: 1080px) {
      .shell { grid-template-columns: 1fr; }
      .metrics, .layout { grid-template-columns: 1fr; }
      .inspect-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="nav">
      <h1>Novel Operator</h1>
      <p>Local control surface for status, inspection, reports, and bounded batch actions.</p>

      <section>
        <label for="runIdInput">Run ID</label>
        <input id="runIdInput" placeholder="batch-ch019-ch023-v1">
        <div class="btn-row" style="margin-top: 10px;">
          <button class="primary" id="loadRunBtn">Load Run</button>
          <button class="ghost-dark" id="refreshBtn">Refresh</button>
        </div>
      </section>

          <section>
            <label>Reports</label>
            <div class="grid-btns">
          <button class="ghost-dark" data-report="checkpoint">Checkpoint</button>
          <button class="ghost-dark" data-report="cleanliness">Cleanliness</button>
          <button class="ghost-dark" data-report="provider-usage">Provider</button>
          <button class="ghost-dark" data-report="product-review">Product Review</button>
          <button class="ghost-dark" data-report="glossary-decisions">Decisions</button>
          <button class="ghost-dark" data-report="glossary-conflicts">Conflicts</button>
          <button class="ghost-dark" data-report="glossary-audit">Audit</button>
          <button class="ghost-dark" data-report="glossary-guard">Guard</button>
        </div>
      </section>

      <section>
        <div class="footer-note">
          This slice surfaces status, inspection, reports, and bounded state-changing actions.
        </div>
      </section>
    </aside>

    <main class="main">
      <div class="topbar">
        <div>
          <h2 id="runTitle">No run loaded</h2>
          <p id="runSubtitle">Load a run to inspect current status, blocker, and artifacts.</p>
        </div>
      </div>

      <section class="metrics" id="metrics"></section>

      <div class="layout">
        <section class="panel">
          <h3>Chapter Status</h3>
          <p class="meta">Current chapter progress and next pending stages.</p>
          <div id="chapterTableWrap" class="empty">No run loaded.</div>
        </section>

        <div class="stack">
          <section class="panel">
            <h3>Safe Next Action</h3>
            <p class="meta">Directly from the current verified run state.</p>
            <div id="nextAction" class="mono empty">No run loaded.</div>
          </section>

          <section class="panel">
            <h3>Research Readiness</h3>
            <p class="meta">Readiness contract for bounded translation versus normal production.</p>
            <div id="researchReadiness" class="empty">No research profile loaded.</div>
          </section>

          <section class="panel">
            <h3>Research Profile</h3>
            <p class="meta">Edit the current workspace research profile fields used for readiness.</p>
            <div class="stack">
              <input id="researchProfileTitle" placeholder="Title">
              <textarea id="researchProfileAliases" placeholder="Aliases, one per line or comma-separated"></textarea>
              <input id="researchProfileSourceUrl" placeholder="Source URL">
              <div class="inspect-grid">
                <select id="researchProfileStatus">
                  <option value="pending">pending</option>
                  <option value="drafted">drafted</option>
                  <option value="active">active</option>
                </select>
                <input id="researchProfileLastReviewedAt" placeholder="Last reviewed at">
              </div>
              <input id="researchProfileReviewedBy" placeholder="Reviewed by">
              <textarea id="researchProfileSynopsis" placeholder="Synopsis"></textarea>
              <textarea id="researchProfileTags" placeholder="Tags, one per line or comma-separated"></textarea>
              <textarea id="researchProfileStyleNotes" placeholder="Style notes"></textarea>
              <textarea id="researchProfileReaderExpectations" placeholder="Reader expectations"></textarea>
              <textarea id="researchProfileReviewSummary" placeholder="Review summary"></textarea>
              <textarea id="researchProfileTerminology" placeholder="Terminology, one per line or comma-separated"></textarea>
              <textarea id="researchProfileReferenceLinks" placeholder="Reference links, one per line or comma-separated"></textarea>
              <textarea id="researchProfileNotes" placeholder="Notes"></textarea>
            </div>
            <button class="primary" id="saveResearchProfileBtn">Save Research Profile</button>
          </section>

          <section class="panel">
            <h3>Preflight</h3>
            <p class="meta">Environment, provider, and git guardrail checks.</p>
            <div id="preflightSummary" class="empty">No preflight summary loaded.</div>
          </section>

          <section class="panel">
            <h3>Manual Actions</h3>
            <p class="meta">Outstanding operator actions from `status`.</p>
            <ul id="manualActions" class="actions-list"></ul>
          </section>

          <section class="panel">
            <h3>Recent Report Output</h3>
            <p class="meta">Generated by the existing CLI report layer.</p>
            <div id="reportResult" class="empty">No report generated yet.</div>
          </section>
        </div>
      </div>

      <section class="panel">
        <h3>Block Inspection</h3>
        <p class="meta">Read-only artifact and validation view for one block.</p>
        <div class="inspect-grid">
          <input id="inspectRunId" placeholder="Run ID">
          <input id="inspectBlockId" placeholder="Block ID e.g. ch019-block-002">
          <button class="primary" id="inspectBtn">Inspect</button>
        </div>
        <div id="inspectResult" class="empty">No block inspected.</div>
      </section>

      <div class="layout">
      <section class="panel">
        <h3>Glossary Candidate Queue</h3>
        <p class="meta">Current effective queue after glossary revalidation.</p>
        <div id="glossaryQueue" class="empty">No queue loaded.</div>
      </section>

        <div class="stack">
          <section class="panel">
            <h3>Glossary Decision</h3>
            <p class="meta">Load 2-3 Thai options for one term, then approve or reject it.</p>
            <div id="glossaryDecision" class="empty">No term selected.</div>
          </section>

          <section class="panel">
            <h3>Safe Actions</h3>
            <p class="meta">State-changing controls stay bounded and always stop on manual action.</p>
            <div class="stack">
              <div>
                <label for="initProjectRoot">Init Novel Project</label>
                <div class="stack">
                  <div class="inspect-grid">
                    <input id="initProjectRoot" placeholder="Project root">
                    <input id="initTitle" placeholder="Title">
                  </div>
                  <input id="initSourceUrl" placeholder="Source URL">
                  <div class="inspect-grid">
                    <input id="initNovelId" placeholder="Novel ID (optional)">
                    <input id="initSourceLanguage" placeholder="Source language">
                    <input id="initTargetLanguage" placeholder="Target language">
                  </div>
                  <div class="inspect-grid">
                    <input id="initGenre" placeholder="Genre">
                    <input id="initAdapter" placeholder="Adapter">
                    <input id="initStyleProfile" placeholder="Style profile">
                  </div>
                  <textarea id="initAliases" placeholder="Aliases, one per line or comma-separated"></textarea>
                </div>
                <button class="primary" id="initNovelBtn">Init Novel Project</button>
              </div>
              <div>
                <label for="batchRunId">Run Batch Range</label>
                <div class="inspect-grid">
                  <input id="batchRunId" placeholder="Run ID">
                  <input id="batchChapterRange" placeholder="Chapter range e.g. ch004-ch008">
                  <select id="batchMode">
                    <option value="scan-only">Scan-only gate</option>
                    <option value="bounded">Bounded batch run</option>
                  </select>
                </div>
                <button class="primary" id="batchBtn">Run Batch</button>
              </div>
              <div>
                <label for="resumeRunId">Resume Run</label>
                <div class="inspect-grid">
                  <input id="resumeRunId" placeholder="Run ID">
                  <input id="resumeUntilChapter" placeholder="Until chapter e.g. ch022">
                  <input id="resumeUntilBlock" placeholder="Or until block e.g. ch022-block-004">
                </div>
                <button class="primary" id="resumeBtn">Run Bounded Resume</button>
              </div>
              <div>
                <label for="rerunRunId">Rerun Block</label>
                <div class="inspect-grid">
                  <input id="rerunRunId" placeholder="Run ID">
                  <input id="rerunBlockId" placeholder="Block ID">
                  <select id="rerunStage">
                    <option value="qa">qa</option>
                    <option value="refining">refining</option>
                    <option value="translating">translating</option>
                    <option value="formatting">formatting</option>
                  </select>
                </div>
                <button class="primary" id="rerunBtn">Run Rerun-Block</button>
              </div>
            </div>
          </section>

          <section class="panel">
            <h3>Action Result</h3>
            <p class="meta">Captured local pipeline output for the last state-changing action.</p>
            <div id="actionResult" class="empty">No action executed yet.</div>
          </section>
        </div>
      </div>
    </main>
  </div>

  <script>
    const state = {
      runId: "",
      snapshot: null,
    };

    const runIdInput = document.getElementById("runIdInput");
    const inspectRunId = document.getElementById("inspectRunId");
    const inspectBlockId = document.getElementById("inspectBlockId");
    const batchRunId = document.getElementById("batchRunId");
    const batchChapterRange = document.getElementById("batchChapterRange");
    const batchMode = document.getElementById("batchMode");
    const initProjectRoot = document.getElementById("initProjectRoot");
    const initTitle = document.getElementById("initTitle");
    const initSourceUrl = document.getElementById("initSourceUrl");
    const initNovelId = document.getElementById("initNovelId");
    const initAliases = document.getElementById("initAliases");
    const initSourceLanguage = document.getElementById("initSourceLanguage");
    const initTargetLanguage = document.getElementById("initTargetLanguage");
    const initGenre = document.getElementById("initGenre");
    const initAdapter = document.getElementById("initAdapter");
    const initStyleProfile = document.getElementById("initStyleProfile");
    const researchProfileTitle = document.getElementById("researchProfileTitle");
    const researchProfileAliases = document.getElementById("researchProfileAliases");
    const researchProfileSourceUrl = document.getElementById("researchProfileSourceUrl");
    const researchProfileStatus = document.getElementById("researchProfileStatus");
    const researchProfileSynopsis = document.getElementById("researchProfileSynopsis");
    const researchProfileTags = document.getElementById("researchProfileTags");
    const researchProfileStyleNotes = document.getElementById("researchProfileStyleNotes");
    const researchProfileReaderExpectations = document.getElementById("researchProfileReaderExpectations");
    const researchProfileReviewSummary = document.getElementById("researchProfileReviewSummary");
    const researchProfileLastReviewedAt = document.getElementById("researchProfileLastReviewedAt");
    const researchProfileReviewedBy = document.getElementById("researchProfileReviewedBy");
    const researchProfileTerminology = document.getElementById("researchProfileTerminology");
    const researchProfileReferenceLinks = document.getElementById("researchProfileReferenceLinks");
    const researchProfileNotes = document.getElementById("researchProfileNotes");
    const resumeRunId = document.getElementById("resumeRunId");
    const resumeUntilChapter = document.getElementById("resumeUntilChapter");
    const resumeUntilBlock = document.getElementById("resumeUntilBlock");
    const rerunRunId = document.getElementById("rerunRunId");
    const rerunBlockId = document.getElementById("rerunBlockId");
    const rerunStage = document.getElementById("rerunStage");
    let currentGlossarySuggestion = null;

    function setRunId(runId) {
      state.runId = runId || "";
      runIdInput.value = state.runId;
      if (!batchRunId.value) {
        batchRunId.value = state.runId;
      }
      if (!inspectRunId.value) {
        inspectRunId.value = state.runId;
      }
      if (!resumeRunId.value) {
        resumeRunId.value = state.runId;
      }
      if (!rerunRunId.value) {
        rerunRunId.value = state.runId;
      }
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }

    function fileLink(path, label) {
      const href = "/api/file?path=" + encodeURIComponent(path);
      return `<a class="report-link" href="${href}" target="_blank" rel="noreferrer">${escapeHtml(label || path)}</a>`;
    }

    function maybeWorkspaceFileLink(path, label) {
      const workspaceRoot = state.snapshot?.preflight?.workspace_root || "";
      if (workspaceRoot && path && String(path).startsWith(workspaceRoot)) {
        return fileLink(path, label);
      }
      return escapeHtml(label || path || "");
    }

    function splitListField(raw) {
      return String(raw || "")
        .split(/[\n,]+/)
        .map((item) => item.trim())
        .filter(Boolean);
    }

    function renderPathList(paths) {
      const projectRoot = paths?.project_root || "";
      const configPath = paths?.config_path || "";
      const profilePath = paths?.profile_path || "";
      const researchProfilePath = paths?.research_profile_path || "";
      const items = [
        `<li class="mono">project_root: ${escapeHtml(projectRoot || "missing")}</li>`,
        `<li class="mono">config_path: ${configPath ? maybeWorkspaceFileLink(configPath, configPath) : "missing"}</li>`,
        `<li class="mono">profile_path: ${profilePath ? maybeWorkspaceFileLink(profilePath, profilePath) : "missing"}</li>`,
        `<li class="mono">research_profile_path: ${researchProfilePath ? maybeWorkspaceFileLink(researchProfilePath, researchProfilePath) : "missing"}</li>`,
      ];
      return `<div><strong>Created Paths</strong><ul class="artifact-list">${items.join("")}</ul></div>`;
    }

    function renderMetrics(snapshot) {
      const metrics = document.getElementById("metrics");
      const status = snapshot?.status || {};
      const completedCount = Array.isArray(status.completed_blocks) ? status.completed_blocks.length : 0;
      const failedCount = Array.isArray(status.current_failed_blocks) ? status.current_failed_blocks.length : 0;
      const records = status.total_records ?? 0;
      const chapterCount = Array.isArray(status.chapter_ids) ? status.chapter_ids.length : 0;
      metrics.innerHTML = `
        <div class="metric">
          <div class="label">Completed Blocks</div>
          <div class="value">${completedCount}</div>
          <div class="sub">${chapterCount} chapters in run scope</div>
        </div>
        <div class="metric">
          <div class="label">Current Failed Blocks</div>
          <div class="value">${failedCount}</div>
          <div class="sub">${status.historical_failed_records ?? 0} historical failed records</div>
        </div>
        <div class="metric">
          <div class="label">Ledger Records</div>
          <div class="value">${records}</div>
          <div class="sub">${escapeHtml(status.run_id || "no run")}</div>
        </div>
        <div class="metric">
          <div class="label">Next Effective Action</div>
          <div class="value" style="font-size:16px; line-height:1.35;">${escapeHtml(status.next_effective_action || "none")}</div>
          <div class="sub">Manual actions needed: ${(status.manual_actions || []).length}</div>
        </div>
      `;
    }

    function renderChapterTable(snapshot) {
      const wrap = document.getElementById("chapterTableWrap");
      const summary = snapshot?.status?.chapter_summary || {};
      const chapterIds = snapshot?.status?.chapter_ids || [];
      if (!chapterIds.length) {
        wrap.className = "empty";
        wrap.textContent = "No chapter summary available.";
        return;
      }
      const rows = chapterIds.map((chapterId) => {
        const item = summary[chapterId] || {};
        const pending = (item.pending_blocks || []).map((blockId) => `${blockId} (${item.pending_stages?.[blockId] || "?"})`).join(", ") || "none";
        const failed = (item.failed_blocks || []).join(", ") || "none";
        const output = item.output_exists ? fileLink(item.output_path, "open output") : "missing";
        return `
          <tr>
            <td class="mono">${escapeHtml(chapterId)}</td>
            <td>${item.completed_blocks ?? 0}/${item.expected_blocks ?? 0}</td>
            <td>${escapeHtml(pending)}</td>
            <td>${escapeHtml(failed)}</td>
            <td>${output}</td>
          </tr>
        `;
      }).join("");
      wrap.className = "";
      wrap.innerHTML = `
        <table class="table">
          <thead>
            <tr>
              <th>Chapter</th>
              <th>Progress</th>
              <th>Pending</th>
              <th>Failed</th>
              <th>Output</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    }

    function renderManualActions(snapshot) {
      const list = document.getElementById("manualActions");
      const actions = snapshot?.status?.manual_actions || [];
      list.innerHTML = "";
      if (!actions.length) {
        list.innerHTML = `<li class="empty">No manual actions.</li>`;
        return;
      }
      for (const action of actions) {
        const li = document.createElement("li");
        li.className = "mono";
        li.textContent = action;
        list.appendChild(li);
      }
    }

    function renderResearchReadiness(snapshot) {
      const wrap = document.getElementById("researchReadiness");
      const readiness = snapshot?.research_readiness || {};
      const profilePath = snapshot?.research_profile_path || readiness.path || "";
      const warnings = readiness.warnings || [];
      const blocking = readiness.blocking_reasons || [];
      const missing = readiness.missing_fields || [];
      const pillClass = readiness.readiness === "ready"
        ? "ok"
        : readiness.readiness === "degraded"
          ? ""
          : "danger";
      wrap.className = "";
      wrap.innerHTML = `
        <div class="stack">
          <div><span class="pill ${pillClass}">${escapeHtml(readiness.readiness || "blocked")}</span></div>
          <div class="mono">status: ${escapeHtml(readiness.status || "missing")}</div>
          <div class="mono">path: ${profilePath ? fileLink(profilePath, profilePath) : "missing"}</div>
          <div class="mono">bounded translation: ${readiness.bounded_translation_ready ? "allowed" : "blocked"}</div>
          <div class="mono">normal production: ${readiness.translation_ready ? "allowed" : "blocked"}</div>
          <div class="mono">missing fields: ${escapeHtml(missing.length ? missing.join(", ") : "none")}</div>
          <div class="mono">warnings: ${escapeHtml(warnings.length ? warnings.join(" | ") : "none")}</div>
          <div class="mono">blocking: ${escapeHtml(blocking.length ? blocking.join(" | ") : "none")}</div>
          <div class="mono">next safe action: ${escapeHtml(readiness.next_safe_action || "none")}</div>
        </div>
      `;
    }

    function renderResearchProfileEditor(snapshot) {
      const profile = snapshot?.research_profile || {};
      researchProfileTitle.value = profile.title || "";
      researchProfileAliases.value = Array.isArray(profile.aliases) ? profile.aliases.join("\n") : "";
      researchProfileSourceUrl.value = profile.source_url || "";
      researchProfileStatus.value = profile.status || "pending";
      researchProfileSynopsis.value = profile.synopsis || "";
      researchProfileTags.value = Array.isArray(profile.tags) ? profile.tags.join("\n") : "";
      researchProfileStyleNotes.value = profile.style_notes || "";
      researchProfileReaderExpectations.value = profile.reader_expectations || "";
      researchProfileReviewSummary.value = profile.review_summary || "";
      researchProfileLastReviewedAt.value = profile.last_reviewed_at || "";
      researchProfileReviewedBy.value = profile.reviewed_by || "";
      researchProfileTerminology.value = Array.isArray(profile.terminology) ? profile.terminology.join("\n") : "";
      researchProfileReferenceLinks.value = Array.isArray(profile.reference_links) ? profile.reference_links.join("\n") : "";
      researchProfileNotes.value = profile.notes || "";
    }

    function renderPreflight(snapshot) {
      const wrap = document.getElementById("preflightSummary");
      const preflight = snapshot?.preflight || {};
      const warnings = preflight.warnings || [];
      const blocking = preflight.blocking_reasons || [];
      const git = preflight.git || {};
      const providerItems = preflight.providers || [];
      const pillClass = preflight.status === "ready"
        ? "ok"
        : preflight.status === "degraded"
          ? ""
          : "danger";
      const providerLines = providerItems.length
        ? providerItems.map((item) => `${item.provider}: ${item.found ? "ready" : "missing"} [${(item.stages || []).join(", ")}]`).join(" | ")
        : "none";
      wrap.className = "";
      wrap.innerHTML = `
        <div class="stack">
          <div><span class="pill ${pillClass}">${escapeHtml(preflight.status || "blocked")}</span></div>
          <div class="mono">providers: ${escapeHtml(providerLines)}</div>
          <div class="mono">git: ${git.available ? (git.in_work_tree ? `${git.branch || "(detached)"} / ${git.clean ? "clean" : "dirty"}` : "not a work tree") : "unavailable"}</div>
          <div class="mono">warnings: ${escapeHtml(warnings.length ? warnings.join(" | ") : "none")}</div>
          <div class="mono">blocking: ${escapeHtml(blocking.length ? blocking.join(" | ") : "none")}</div>
          <div class="mono">next safe action: ${escapeHtml(preflight.next_safe_action || "none")}</div>
        </div>
      `;
    }

    function renderSnapshot(snapshot) {
      state.snapshot = snapshot;
      const runId = snapshot?.run_id || "";
      setRunId(runId);
      document.getElementById("runTitle").textContent = runId || "No run loaded";
      document.getElementById("runSubtitle").textContent = snapshot?.available_run_ids?.length
        ? `${snapshot.available_run_ids.length} known run IDs in ledger.`
        : "No runs recorded.";
      document.getElementById("nextAction").textContent = snapshot?.status?.next_effective_action || "none";
      renderMetrics(snapshot);
      renderChapterTable(snapshot);
      renderResearchReadiness(snapshot);
      renderResearchProfileEditor(snapshot);
      renderPreflight(snapshot);
      renderManualActions(snapshot);
    }

    async function loadSnapshot(runId = "") {
      const query = runId ? `?run_id=${encodeURIComponent(runId)}` : "";
      const response = await fetch(`/api/bootstrap${query}`);
      const data = await response.json();
      renderSnapshot(data);
      if (data.run_id) {
        await loadGlossaryQueue(data.run_id);
      }
    }

    async function loadGlossaryQueue(runId) {
      const response = await fetch(`/api/glossary-queue?run_id=${encodeURIComponent(runId)}`);
      const data = await response.json();
      const wrap = document.getElementById("glossaryQueue");
      if (!response.ok) {
        wrap.className = "empty";
        wrap.textContent = data.error || "Failed to load glossary queue.";
        return;
      }
      const items = data.items || [];
      if (!items.length) {
        wrap.className = "empty";
        wrap.textContent = "No pending glossary candidates in the effective queue.";
        return;
      }
      const rows = items.map((item) => `
        <tr>
          <td class="mono">${escapeHtml(item.original_term || "")}</td>
          <td>${escapeHtml(item.category || "")}</td>
          <td>${escapeHtml(item.chapter_id || "")}</td>
          <td class="mono">${escapeHtml(item.first_seen_block || "")}</td>
          <td><button data-term="${escapeHtml(item.original_term || "")}" class="load-suggestion-btn">Load options</button></td>
        </tr>
      `).join("");
      const removed = (data.removed_terms || []).length
        ? `<div class="footer-note" style="margin-top:10px;">Removed by current guard: ${escapeHtml((data.removed_terms || []).join(", "))}</div>`
        : "";
      wrap.className = "";
      wrap.innerHTML = `
        <table class="table">
          <thead>
            <tr>
              <th>Term</th>
              <th>Category</th>
              <th>Chapter</th>
              <th>First Seen</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
        ${removed}
      `;
      wrap.querySelectorAll(".load-suggestion-btn").forEach((button) => {
        button.addEventListener("click", () => loadGlossarySuggestion(button.dataset.term || ""));
      });
    }

    async function loadGlossarySuggestion(term) {
      const runId = state.runId || runIdInput.value.trim();
      if (!runId || !term) {
        document.getElementById("glossaryDecision").innerHTML = `<div class="empty">Run ID and term are required.</div>`;
        return;
      }
      const response = await fetch(`/api/glossary-suggestion?run_id=${encodeURIComponent(runId)}&term=${encodeURIComponent(term)}`);
      const data = await response.json();
      const wrap = document.getElementById("glossaryDecision");
      if (!response.ok) {
        wrap.innerHTML = `<div class="empty">${escapeHtml(data.error || "Failed to load suggestions.")}</div>`;
        return;
      }
      currentGlossarySuggestion = data;
      const optionRows = (data.options || []).map((option, index) => {
        const rationale = (data.rationales || [])[index] || "";
        return `<option value="${escapeHtml(option)}">${escapeHtml(option)}${rationale ? " — " + escapeHtml(rationale) : ""}</option>`;
      }).join("");
      const contextPreview = (data.context || []).join("\n\n");
      wrap.className = "";
      wrap.innerHTML = `
        <div class="stack">
          <div class="mono">term: ${escapeHtml(data.term)}</div>
          <div class="mono">category: ${escapeHtml(data.category || "")}</div>
          <div class="mono">provider: ${escapeHtml(data.provider || "")}</div>
          <label for="glossaryOptionSelect">Thai option</label>
          <select id="glossaryOptionSelect">${optionRows}</select>
          <label for="glossaryDecisionNote">Decision note</label>
          <input id="glossaryDecisionNote" placeholder="Optional note">
          <div class="mono" style="white-space:pre-wrap;">${escapeHtml(contextPreview)}</div>
          <div class="btn-row">
            <button class="primary" id="approveTermBtn">Approve Selected Option</button>
            <button id="rejectTermBtn">Reject Term</button>
          </div>
        </div>
      `;
      document.getElementById("approveTermBtn").addEventListener("click", () => submitGlossaryDecision("approve"));
      document.getElementById("rejectTermBtn").addEventListener("click", () => submitGlossaryDecision("reject"));
    }

    async function submitGlossaryDecision(decision) {
      if (!currentGlossarySuggestion) {
        document.getElementById("actionResult").innerHTML = `<div class="empty">No glossary suggestion loaded.</div>`;
        return;
      }
      const selectedOption = document.getElementById("glossaryOptionSelect")?.value || "";
      const note = document.getElementById("glossaryDecisionNote")?.value || "";
      const payload = {
        action: "glossary-decision",
        run_id: currentGlossarySuggestion.run_id,
        term: currentGlossarySuggestion.term,
        decision,
        thai_term: decision === "approve" ? selectedOption : "",
        note,
      };
      const response = await fetch("/api/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        document.getElementById("actionResult").innerHTML = `<div class="empty">${escapeHtml(data.error || "Glossary decision failed.")}</div>`;
        return;
      }
      const decisionWrap = document.getElementById("glossaryDecision");
      decisionWrap.className = "empty";
      decisionWrap.textContent = data.committed
        ? "Decision saved. Glossary approval committed for this run."
        : "Decision saved.";
      currentGlossarySuggestion = null;
      document.getElementById("actionResult").innerHTML = `
        <div class="stack">
          <div><span class="pill ok">${escapeHtml(data.decision)}</span></div>
          <div class="mono">${escapeHtml(data.term)}</div>
          <div class="mono">${data.committed ? "glossary_approved committed" : "queue updated"}</div>
        </div>
      `;
      if (data.snapshot) {
        renderSnapshot(data.snapshot);
      }
      await loadGlossaryQueue(data.run_id || state.runId);
    }

    async function inspectBlock() {
      const runId = inspectRunId.value.trim() || state.runId;
      const blockId = inspectBlockId.value.trim();
      if (!runId || !blockId) {
        document.getElementById("inspectResult").innerHTML = `<div class="empty">Run ID and block ID are required.</div>`;
        return;
      }
      const response = await fetch(`/api/inspect-block?run_id=${encodeURIComponent(runId)}&block_id=${encodeURIComponent(blockId)}`);
      const data = await response.json();
      if (!response.ok) {
        document.getElementById("inspectResult").innerHTML = `<div class="empty">${escapeHtml(data.error || "Inspect failed.")}</div>`;
        return;
      }
      const artifactEntries = Object.entries(data.artifact_paths || {}).map(([stage, path]) => {
        const exists = data.artifact_exists?.[stage];
        const label = `${stage} (${exists ? "exists" : "missing"})`;
        return `<li>${exists ? fileLink(path, label) : escapeHtml(label + ": " + path)}</li>`;
      }).join("");
      const issues = (data.formatted_validation_issues || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
      document.getElementById("inspectResult").innerHTML = `
        <div class="stack">
          <div><span class="pill ${data.next_pending_stage ? "danger" : "ok"}">${data.next_pending_stage ? "pending " + escapeHtml(data.next_pending_stage) : "complete"}</span></div>
          <div class="mono">chapter: ${escapeHtml(data.chapter_id)}</div>
          <div>
            <strong>Artifacts</strong>
            <ul class="artifact-list">${artifactEntries}</ul>
          </div>
          <div>
            <strong>Formatted validation issues</strong>
            ${issues ? `<ul class="issues-list">${issues}</ul>` : `<div class="empty">none</div>`}
          </div>
          <div class="mono">ledger records: ${(data.records || []).length}</div>
        </div>
      `;
    }

    async function generateReport(kind) {
      const runId = state.runId || runIdInput.value.trim();
      if (!runId) {
        document.getElementById("reportResult").innerHTML = `<div class="empty">Run ID is required.</div>`;
        return;
      }
      const response = await fetch("/api/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: runId, kind }),
      });
      const data = await response.json();
      if (!response.ok) {
        document.getElementById("reportResult").innerHTML = `<div class="empty">${escapeHtml(data.error || "Report generation failed.")}</div>`;
        return;
      }
      document.getElementById("reportResult").innerHTML = `
        <div class="stack">
          <div><span class="pill ${data.actionable_failure ? "danger" : "ok"}">${data.actionable_failure ? "actionable" : "ok"}</span></div>
          <div>${fileLink(data.path, data.path)}</div>
        </div>
      `;
    }

    async function runAction(action, payload) {
      const response = await fetch("/api/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      const target = document.getElementById("actionResult");
      if (!response.ok) {
        target.innerHTML = `<div class="empty">${escapeHtml(data.error || "Action failed.")}</div>`;
        return;
      }
      const initPaths = data.paths || data.snapshot?.init_novel_paths || null;
      target.innerHTML = `
        <div class="stack">
          <div><span class="pill ok">${escapeHtml(data.action)}</span></div>
          <pre class="mono" style="margin:0; white-space:pre-wrap;">${escapeHtml(data.output || "(no output)")}</pre>
          ${initPaths ? renderPathList(initPaths) : ""}
        </div>
      `;
      if (data.snapshot) {
        renderSnapshot(data.snapshot);
        if (data.snapshot.run_id) {
          await loadGlossaryQueue(data.snapshot.run_id);
        }
      }
    }

    document.getElementById("loadRunBtn").addEventListener("click", () => loadSnapshot(runIdInput.value.trim()));
    document.getElementById("refreshBtn").addEventListener("click", () => loadSnapshot(state.runId || runIdInput.value.trim()));
    document.getElementById("inspectBtn").addEventListener("click", inspectBlock);
    document.getElementById("initNovelBtn").addEventListener("click", () => {
      const projectRoot = initProjectRoot.value.trim();
      const title = initTitle.value.trim();
      const sourceUrl = initSourceUrl.value.trim();
      if (!projectRoot || !title || !sourceUrl) {
        document.getElementById("actionResult").innerHTML = `<div class="empty">Init Novel Project requires project root, title, and source URL.</div>`;
        return;
      }
      runAction("init-novel", {
        action: "init-novel",
        run_id: state.runId || "",
        project_root: projectRoot,
        title,
        source_url: sourceUrl,
        novel_id: initNovelId.value.trim(),
        aliases: initAliases.value,
        source_language: initSourceLanguage.value.trim(),
        target_language: initTargetLanguage.value.trim(),
        genre: initGenre.value.trim(),
        adapter: initAdapter.value.trim(),
        style_profile: initStyleProfile.value.trim(),
      });
    });
    document.getElementById("saveResearchProfileBtn").addEventListener("click", () => {
      runAction("save-research-profile", {
        action: "save-research-profile",
        run_id: state.runId || "",
        title: researchProfileTitle.value.trim(),
        aliases: splitListField(researchProfileAliases.value),
        source_url: researchProfileSourceUrl.value.trim(),
        status: researchProfileStatus.value,
        synopsis: researchProfileSynopsis.value.trim(),
        tags: splitListField(researchProfileTags.value),
        style_notes: researchProfileStyleNotes.value.trim(),
        reader_expectations: researchProfileReaderExpectations.value.trim(),
        review_summary: researchProfileReviewSummary.value.trim(),
        last_reviewed_at: researchProfileLastReviewedAt.value.trim(),
        reviewed_by: researchProfileReviewedBy.value.trim(),
        terminology: splitListField(researchProfileTerminology.value),
        reference_links: splitListField(researchProfileReferenceLinks.value),
        notes: researchProfileNotes.value.trim(),
      });
    });
    document.getElementById("batchBtn").addEventListener("click", () => {
      const runId = batchRunId.value.trim() || state.runId;
      const chapterRange = batchChapterRange.value.trim();
      const stopAfter = batchMode.value === "scan-only" ? "glossary-scan" : "";
      if (!runId || !chapterRange) {
        document.getElementById("actionResult").innerHTML = `<div class="empty">Run-batch requires run ID and chapter range.</div>`;
        return;
      }
      runAction("run-batch", {
        action: "run-batch",
        run_id: runId,
        chapter_range: chapterRange,
        stop_after: stopAfter,
      });
    });
    document.getElementById("resumeBtn").addEventListener("click", () => {
      const runId = resumeRunId.value.trim() || state.runId;
      const untilChapter = resumeUntilChapter.value.trim();
      const untilBlock = resumeUntilBlock.value.trim();
      if (!runId || (!untilChapter && !untilBlock)) {
        document.getElementById("actionResult").innerHTML = `<div class="empty">Resume requires run ID and a bounded chapter or block.</div>`;
        return;
      }
      runAction("resume", {
        action: "resume",
        run_id: runId,
        until_chapter: untilChapter,
        until_block: untilBlock,
      });
    });
    document.getElementById("rerunBtn").addEventListener("click", () => {
      const runId = rerunRunId.value.trim() || state.runId;
      const blockId = rerunBlockId.value.trim();
      const fromStage = rerunStage.value;
      if (!runId || !blockId || !fromStage) {
        document.getElementById("actionResult").innerHTML = `<div class="empty">Rerun-block requires run ID, block ID, and stage.</div>`;
        return;
      }
      runAction("rerun-block", {
        action: "rerun-block",
        run_id: runId,
        block_id: blockId,
        from_stage: fromStage,
      });
    });
    document.querySelectorAll("[data-report]").forEach((button) => {
      button.addEventListener("click", () => generateReport(button.dataset.report));
    });

    loadSnapshot("");
  </script>
</body>
</html>
"""


class _OperatorHandler(BaseHTTPRequestHandler):
    config: AppConfig
    default_run_id: str | None

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _send_json(self, payload: dict[str, Any], *, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, *, content_type: str = "text/plain; charset=utf-8", status: int = 200) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if parsed.path == "/":
            self._send_text(_render_operator_html(), content_type="text/html; charset=utf-8")
            return
        if parsed.path == "/api/bootstrap":
            run_id = (params.get("run_id") or [self.default_run_id or ""])[0] or None
            try:
                payload = build_operator_snapshot(self.config, run_id=run_id)
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
            return
        if parsed.path == "/api/glossary-queue":
            run_id = (params.get("run_id") or [self.default_run_id or ""])[0] or None
            if not run_id:
                self._send_json({"error": "run_id is required."}, status=400)
                return
            try:
                payload = build_glossary_queue_snapshot(self.config, run_id)
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
            return
        if parsed.path == "/api/glossary-suggestion":
            run_id = (params.get("run_id") or [self.default_run_id or ""])[0] or None
            term = (params.get("term") or [""])[0]
            if not run_id or not term:
                self._send_json({"error": "run_id and term are required."}, status=400)
                return
            try:
                payload = build_glossary_suggestion_snapshot(self.config, run_id, term)
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
            return
        if parsed.path == "/api/inspect-block":
            run_id = (params.get("run_id") or [""])[0]
            block_id = (params.get("block_id") or [""])[0]
            if not run_id or not block_id:
                self._send_json({"error": "run_id and block_id are required."}, status=400)
                return
            try:
                payload = _quiet_inspect_block(self.config, run_id, block_id)
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
            return
        if parsed.path == "/api/file":
            raw_path = (params.get("path") or [""])[0]
            if not raw_path:
                self._send_text("Missing path.", status=400)
                return
            try:
                safe_path = _safe_workspace_path(self.config, unquote(raw_path))
                text = safe_path.read_text(encoding="utf-8")
                title = quote(str(safe_path))
                html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{safe_path.name}</title>
                <style>body{{margin:0;background:#f5f6f8;color:#111827;font-family:Segoe UI,Tahoma,sans-serif}}
                header{{padding:14px 18px;border-bottom:1px solid #d7dce5;background:#fff}}
                main{{padding:18px}} pre{{white-space:pre-wrap;word-break:break-word;background:#fff;border:1px solid #d7dce5;border-radius:8px;padding:16px}}</style>
                </head><body><header><strong>{safe_path}</strong></header><main><pre>{text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</pre></main></body></html>"""
                self._send_text(html, content_type="text/html; charset=utf-8")
            except Exception as exc:
                self._send_text(str(exc), status=400)
            return
        self._send_json({"error": "Not found."}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path not in {"/api/report", "/api/action"}:
            self._send_json({"error": "Not found."}, status=404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            payload = json.loads(raw)
            if parsed.path == "/api/report":
                run_id = str(payload.get("run_id") or "").strip()
                kind = str(payload.get("kind") or "").strip()
                chapter_ids = payload.get("chapter_ids")
                if not run_id or not kind:
                    self._send_json({"error": "run_id and kind are required."}, status=400)
                    return
                result = generate_operator_report(
                    config=self.config,
                    run_id=run_id,
                    kind=kind,
                    chapter_ids=chapter_ids if isinstance(chapter_ids, list) else None,
                )
                self._send_json(
                    {
                        "path": str(result["path"]),
                        "actionable_failure": bool(result.get("actionable_failure")),
                    }
                )
                return
            run_id = str(payload.get("run_id") or "").strip()
            action = str(payload.get("action") or "").strip()
            if not action or (not run_id and action not in {"init-novel", "save-research-profile"}):
                self._send_json({"error": "action is required; run_id is required for run-scoped actions."}, status=400)
                return
            if action == "glossary-decision":
                term = str(payload.get("term") or "").strip()
                decision = str(payload.get("decision") or "").strip()
                thai_term = str(payload.get("thai_term") or "").strip()
                note = str(payload.get("note") or "").strip()
                result = execute_glossary_decision(
                    config=self.config,
                    run_id=run_id,
                    term=term,
                    decision=decision,
                    thai_term=thai_term,
                    note=note,
                )
                self._send_json(result)
                return
            result = execute_operator_action(
                config=self.config,
                action=action,
                run_id=run_id,
                payload=payload,
            )
            self._send_json(result)
        except ManualActionRequired as exc:
            self._send_json({"error": str(exc), "manual_action_required": True}, status=409)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)


def serve_operator_ui(
    *,
    config: AppConfig,
    host: str = "127.0.0.1",
    port: int = 8765,
    run_id: str | None = None,
    open_browser: bool = False,
) -> ThreadingHTTPServer:
    handler = type(
        "OperatorHandler",
        (_OperatorHandler,),
        {"config": config, "default_run_id": run_id},
    )
    server = ThreadingHTTPServer((host, port), handler)
    if open_browser:
        url = f"http://{host}:{port}/"
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()
    return server


__all__ = [
    "build_operator_snapshot",
    "build_glossary_queue_snapshot",
    "execute_operator_action",
    "generate_operator_report",
    "serve_operator_ui",
]
