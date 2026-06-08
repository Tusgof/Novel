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
from novel_pipeline.employees import EMPLOYEE_ROSTER, employee_provider_label
from novel_pipeline.files import atomic_write_json, atomic_write_text, read_text_if_exists
from novel_pipeline.glossary_support import parse_glossary_note, write_glossary_note
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
from novel_pipeline.providers.base import ProviderRunner, classify_provider_response
from novel_pipeline.stages.glossary import build_term_suggestion
from novel_pipeline.text_utils import parse_chapter_range
from novel_pipeline.reports import (
    build_checkpoint_report,
    build_cleanliness_report,
    build_preflight_report,
    build_recovery_drill_report,
    build_product_review_report,
    build_glossary_audit_report,
    build_glossary_conflicts_report,
    build_glossary_decisions_report,
    build_glossary_guard_report,
    build_provider_usage_report,
)
from novel_pipeline.types import AppConfig, GlossaryEntry, ProviderRequest, ResearchProfile, TermSuggestion

_OPERATOR_REPORT_KINDS: tuple[str, ...] = (
    "checkpoint",
    "cleanliness",
    "provider-usage",
    "preflight",
    "recovery-drill",
    "product-review",
    "glossary-decisions",
    "glossary-conflicts",
    "glossary-audit",
    "glossary-guard",
)

_OPERATOR_STATE_ACTIONS: tuple[str, ...] = (
    "init-novel",
    "save-research-profile",
    "glossary-decision",
    "run-batch",
    "resume",
    "rerun-block",
)


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


def _operator_command_hints(config: AppConfig, run_id: str | None, status: dict[str, Any], preflight: dict[str, Any]) -> dict[str, str]:
    config_path = str(config.config_path)
    hints: dict[str, str] = {
        "preflight": f'novel-pipeline --config "{config_path}" preflight',
        "preflight_report": f'novel-pipeline --config "{config_path}" report preflight',
        "recovery_drill": f'novel-pipeline --config "{config_path}" report recovery-drill',
        "operator": f'novel-pipeline --config "{config_path}" operator --open-browser',
    }
    if run_id:
        hints["status"] = f'novel-pipeline --config "{config_path}" status --run-id {run_id}'
        hints["product_review"] = f'novel-pipeline --config "{config_path}" report product-review --run-id {run_id}'
        next_action = str(status.get("next_effective_action") or "").strip()
        if next_action:
            hints["next_effective_action"] = next_action
        current_failed = list(status.get("current_failed_blocks") or [])
        if current_failed:
            first_failed = current_failed[0]
            hints["inspect_first_failed"] = (
                f'novel-pipeline --config "{config_path}" inspect-block --run-id {run_id} --block-id {first_failed}'
            )
        manual_actions = [
            str(item).strip()
            for item in (status.get("manual_actions") or [])
            if str(item).strip() and str(item).strip().lower() != "none"
        ]
        if manual_actions:
            hints["manual_action_summary"] = " | ".join(manual_actions)
    if preflight.get("status") != "ready":
        hints["preflight_next_safe_action"] = str(preflight.get("next_safe_action") or "Fix preflight warnings or blockers.")
    return hints


def _operator_quick_links(config: AppConfig, run_id: str | None) -> list[dict[str, str]]:
    root = config.workspace.root
    candidates = [
        ("Project Brain", root / "PROJECT_BRAIN.md"),
        ("Implement Plan", root / "IMPLEMENT_PLAN.md"),
        ("Operator Manual", root / "OPERATOR_MANUAL.md"),
        ("Research Profile", root / "RESEARCH_PROFILE.yaml"),
        ("Preflight Report", root / "07_Reports" / "preflight_report.md"),
        ("Recovery Drill", root / "07_Reports" / "recovery_drill.md"),
    ]
    if run_id:
        candidates.extend(
            [
                ("Product Review", root / "07_Reports" / f"product_review_{run_id}.md"),
                ("Checkpoint Report", root / "07_Reports" / f"checkpoint_{run_id}.md"),
            ]
        )
    links: list[dict[str, str]] = []
    for label, path in candidates:
        if path.exists():
            links.append({"label": label, "path": str(path)})
    return links


def _report_link_entry(label: str, path: Path) -> dict[str, str]:
    return {"label": label, "path": str(path)}


def _operator_report_surfaces(config: AppConfig, run_id: str | None) -> dict[str, Any]:
    reports_root = config.workspace.root / "07_Reports"
    archive_root = reports_root / "archive"

    active_reference = [
        ("Rollout Protocol", reports_root / "v3_10_repeatable_rollout_protocol.md"),
        ("Preflight Report", reports_root / "preflight_report.md"),
        ("Recovery Drill", reports_root / "recovery_drill.md"),
    ]
    active_generated: list[tuple[str, Path]] = []
    if run_id:
        active_generated.extend(
            [
                ("Product Review", reports_root / f"product_review_{run_id}.md"),
                ("Checkpoint", reports_root / f"checkpoint_{run_id}.md"),
                ("Provider Usage", reports_root / f"provider_usage_{run_id}.md"),
                ("Glossary Decisions", reports_root / f"glossary_decisions_{run_id}.md"),
                ("Glossary Conflicts", reports_root / f"glossary_conflicts_{run_id}.md"),
                ("Glossary Audit", reports_root / f"glossary_audit_{run_id}.md"),
                ("Glossary Guard", reports_root / f"glossary_guard_{run_id}.md"),
            ]
        )
        active_generated.extend(
            (
                "Cleanliness",
                path,
            )
            for path in sorted(reports_root.glob(f"cleanliness_{run_id}*.md"))
        )

    seen_paths: set[Path] = set()

    def _existing(entries: list[tuple[str, Path]]) -> list[dict[str, str]]:
        links: list[dict[str, str]] = []
        for label, path in entries:
            if path.exists() and path not in seen_paths:
                seen_paths.add(path)
                links.append(_report_link_entry(label, path))
        return links

    active = {
        "reference": _existing(active_reference),
        "generated": _existing(active_generated),
        "other_root": [],
        "count": 0,
    }
    root_files = sorted(
        [
            path
            for path in reports_root.glob("*.md")
            if path.exists() and path not in seen_paths
        ],
        key=lambda path: path.name.lower(),
    )
    active["other_root"] = [_report_link_entry(path.name, path) for path in root_files]
    active["count"] = len(active["reference"]) + len(active["generated"]) + len(active["other_root"])

    archive_groups: list[dict[str, Any]] = []
    if archive_root.exists():
        for group in sorted([path for path in archive_root.iterdir() if path.is_dir()], key=lambda path: path.name.lower()):
            count = sum(1 for _ in group.rglob("*.md"))
            archive_groups.append({"label": group.name, "count": count})
    archive_recent = sorted(
        archive_root.rglob("*.md") if archive_root.exists() else [],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )[:8]
    archive = {
        "groups": archive_groups,
        "recent": [
            {
                "label": str(path.relative_to(reports_root)).replace("\\", "/"),
                "path": str(path),
            }
            for path in archive_recent
        ],
        "count": sum(item["count"] for item in archive_groups),
    }
    return {"active": active, "archive": archive}


def _employee_stage_activity(status: dict[str, Any], stages: tuple[str, ...]) -> str:
    provider_usage = status.get("provider_usage") or {}
    counts: dict[str, int] = {}
    for stages_by_provider in provider_usage.values():
        if not isinstance(stages_by_provider, dict):
            continue
        for stage, statuses in stages_by_provider.items():
            if stage not in stages or not isinstance(statuses, dict):
                continue
            counts[stage] = counts.get(stage, 0) + sum(int(value) for value in statuses.values())
    if not counts:
        return "No run activity yet."
    return " | ".join(f"{stage}: {count}" for stage, count in sorted(counts.items()))


def _employee_status_snapshot(config: AppConfig, status: dict[str, Any], preflight: dict[str, Any]) -> list[dict[str, Any]]:
    provider_status = {
        str(item.get("provider") or ""): str(item.get("status") or "unknown")
        for item in preflight.get("providers", [])
        if isinstance(item, dict)
    }
    failed_blocks = list(status.get("current_failed_blocks") or [])
    manual_actions = [
        str(item).strip()
        for item in status.get("manual_actions", [])
        if str(item).strip().lower() != "none"
    ]
    records = int(status.get("total_records") or 0)
    employees: list[dict[str, Any]] = []
    for index, employee in enumerate(EMPLOYEE_ROSTER):
        route_stages = [stage for stage in employee["stages"] if stage in config.stage_routing]
        route_providers = [
            config.stage_routing_for(stage).provider
            for stage in route_stages
            if config.stage_routing_for(stage).provider
        ]
        if route_providers:
            route_states = [provider_status.get(provider, "unknown") for provider in route_providers]
            if any(state == "blocked" for state in route_states):
                readiness = "blocked"
            elif any(state == "unknown" for state in route_states):
                readiness = "unknown"
            else:
                readiness = "ready"
        elif preflight.get("status") == "blocked":
            readiness = "warning"
        else:
            readiness = "ready"
        if employee["code"] == "007" and failed_blocks:
            readiness = "blocked"
        elif employee["code"] in {"004", "007"} and manual_actions:
            readiness = "warning"
        latest_activity = _employee_stage_activity(status, tuple(employee["stages"]))
        if not records:
            latest_activity = "No loaded run activity."
        employees.append(
            {
                "index": index,
                "code": employee["code"],
                "name": employee["name"],
                "archetype": employee["archetype"],
                "role": employee["role"],
                "maps_to": list(employee["maps_to"]),
                "stages": list(employee["stages"]),
                "actions": list(employee["actions"]),
                "provider_model": employee_provider_label(config, employee),
                "readiness": readiness,
                "latest_activity": latest_activity,
                "asset": "employee-chibi-spritesheet.png",
            }
        )
    return employees


def run_provider_smoke_tests(config: AppConfig, *, confirm: bool) -> dict[str, Any]:
    if not confirm:
        raise ValueError("Provider smoke test requires explicit confirmation.")
    routes: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    for stage, routing in sorted(config.stage_routing.items()):
        stage_routes = [(routing.provider, routing.model)]
        stage_routes.extend((item.get("provider", ""), item.get("model", "")) for item in routing.fallbacks)
        for provider_name, model in stage_routes:
            if not provider_name or provider_name == "local":
                continue
            key = (provider_name, model)
            if key in seen:
                continue
            seen.add(key)
            routes.append((stage, provider_name, model))

    results: list[dict[str, Any]] = []
    prompt = "Reply with exactly: OK"
    for stage, provider_name, model in routes:
        spec = config.providers[provider_name]
        runner = ProviderRunner(spec)
        response = runner.run(
            ProviderRequest(
                prompt=prompt,
                provider=provider_name,
                stage=f"smoke:{stage}",
                model=model,
                cwd=config.workspace.root,
                timeout_seconds=min(spec.timeout_seconds, 30.0),
            )
        )
        failure_kind = classify_provider_response(response, require_stdout=True)
        results.append(
            {
                "stage": stage,
                "provider": provider_name,
                "model": response.model,
                "status": "ready" if not failure_kind else "blocked",
                "failure_kind": failure_kind,
                "returncode": response.returncode,
                "duration_seconds": response.duration_seconds,
                "stdout_preview": (response.stdout or "").strip()[:120],
                "stderr_preview": (response.stderr or "").strip()[:120],
            }
        )
    return {"results": results}


def _operator_dashboard_guardrails() -> dict[str, Any]:
    return {
        "allowed_state_actions": list(_OPERATOR_STATE_ACTIONS),
        "visible_report_kinds": list(_OPERATOR_REPORT_KINDS),
        "run_batch_requires_run_id": True,
        "run_batch_requires_chapter_range": True,
        "run_batch_allowed_modes": ["bounded", "glossary-scan"],
        "resume_requires_boundary": True,
        "resume_manual_action_mode": "stop",
        "rerun_requires_block_and_stage": True,
        "glossary_current_queue_only": True,
        "research_readiness_gate": "bounded",
        "inspect_prefill_only": True,
        "broad_unbounded_actions_exposed": False,
        "employee_aliases_display_only": True,
        "provider_smoke_requires_explicit_action": True,
    }


def generate_operator_report(
    *,
    config: AppConfig,
    run_id: str | None,
    kind: str,
    chapter_ids: list[str] | None = None,
) -> dict[str, Any]:
    if kind == "checkpoint":
        if not run_id:
            raise ValueError("checkpoint report requires run_id.")
        return build_checkpoint_report(config=config, run_id=run_id)
    if kind == "cleanliness":
        if not run_id:
            raise ValueError("cleanliness report requires run_id.")
        return build_cleanliness_report(config=config, run_id=run_id, chapter_ids=chapter_ids or None)
    if kind == "provider-usage":
        if not run_id:
            raise ValueError("provider-usage report requires run_id.")
        return build_provider_usage_report(config=config, run_id=run_id)
    if kind == "glossary-decisions":
        if not run_id:
            raise ValueError("glossary-decisions report requires run_id.")
        return build_glossary_decisions_report(config=config, run_id=run_id)
    if kind == "glossary-conflicts":
        return build_glossary_conflicts_report(config=config, run_id=run_id)
    if kind == "glossary-audit":
        if not run_id:
            raise ValueError("glossary-audit report requires run_id.")
        return build_glossary_audit_report(config=config, run_id=run_id)
    if kind == "glossary-guard":
        if not run_id:
            raise ValueError("glossary-guard report requires run_id.")
        return build_glossary_guard_report(config=config, run_id=run_id)
    if kind == "preflight":
        return build_preflight_report(config=config)
    if kind == "recovery-drill":
        return build_recovery_drill_report(config=config)
    if kind == "product-review":
        if not run_id:
            raise ValueError("product-review report requires run_id.")
        return build_product_review_report(config=config, run_id=run_id)
    raise ValueError(f"Unsupported report kind: {kind}")


def build_operator_snapshot(config: AppConfig, run_id: str | None = None) -> dict[str, Any]:
    resolved_run_id = run_id or _latest_run_id(config)
    status = _quiet_status_run(config, resolved_run_id) if resolved_run_id else {"runs": []}
    preflight = build_preflight_summary(config)
    return {
        "run_id": resolved_run_id,
        "available_run_ids": _list_run_ids(config),
        "status": status,
        "research_profile_path": str(config.workspace.root / "RESEARCH_PROFILE.yaml"),
        "research_profile": _research_profile_snapshot(config),
        "research_readiness": config.research_readiness_summary(),
        "preflight": preflight,
        "dashboard_guardrails": _operator_dashboard_guardrails(),
        "employee_status": _employee_status_snapshot(config, status, preflight),
        "command_hints": _operator_command_hints(config, resolved_run_id, status, preflight),
        "quick_links": _operator_quick_links(config, resolved_run_id),
        "report_surfaces": _operator_report_surfaces(config, resolved_run_id),
    }


def build_glossary_queue_snapshot(config: AppConfig, run_id: str) -> dict[str, Any]:
    artifact = _read_glossary_scan_artifact(config, run_id=run_id)
    chapter_ids = list(artifact.get("chapter_ids", [])) if isinstance(artifact, dict) else []
    queue_items = _read_glossary_scan_items(config, run_id=run_id)
    note_records = _load_operator_glossary_note_records(config)
    if not queue_items:
        return {
            "run_id": run_id,
            "chapter_ids": chapter_ids,
            "items": [],
            "removed_terms": [],
            "progress": _glossary_progress_snapshot(artifact or {}, {"items": [], "removed_terms": []}),
        }

    blocks = []
    for chapter_id in chapter_ids:
        _, chapter_blocks = _load_chapter_source_and_blocks(config, chapter_id)
        blocks.extend(chapter_blocks)
    filtered_items, removed_terms = _revalidate_glossary_queue_items(config, blocks, queue_items)
    items_with_context: list[dict[str, Any]] = []
    for item in filtered_items:
        enriched = dict(item)
        enriched["intersections"] = _glossary_intersections(note_records, str(item.get("original_term") or ""))
        items_with_context.append(enriched)
    snapshot = {
        "items": items_with_context,
        "removed_terms": removed_terms,
    }
    return {
        "run_id": run_id,
        "chapter_ids": chapter_ids,
        "items": items_with_context,
        "removed_terms": removed_terms,
        "progress": _glossary_progress_snapshot(artifact, snapshot),
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


def _load_operator_glossary_note_records(config: AppConfig) -> list[dict[str, Any]]:
    glossary_dir = config.workspace.glossary_dir
    if not isinstance(glossary_dir, (str, Path)):
        return []
    glossary_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for path in sorted(glossary_dir.rglob("*.md")):
        entry = parse_glossary_note(path)
        if entry is None:
            continue
        path_parts = {part.lower() for part in path.parts}
        records.append(
            {
                "original_term": entry.original_term,
                "thai_term": entry.thai_term,
                "status": str(entry.status or "proposed").strip().lower() or "proposed",
                "category": entry.category,
                "aliases": list(entry.aliases),
                "path": str(path.resolve()),
                "is_quarantine": "quarantine" in path_parts,
            }
        )
    return records


def _glossary_note_bucket(note: dict[str, Any]) -> str:
    if note.get("is_quarantine"):
        return "quarantine"
    status = str(note.get("status") or "proposed").strip().lower() or "proposed"
    if status in {"approved", "rejected", "deprecated", "proposed"}:
        return status
    return "proposed"


def _glossary_intersections(records: list[dict[str, Any]], term: str) -> dict[str, list[dict[str, Any]]]:
    normalized = term.strip()
    exact: list[dict[str, Any]] = []
    overlap: list[dict[str, Any]] = []
    for note in records:
        note_term = str(note.get("original_term") or "").strip()
        aliases = [str(item).strip() for item in (note.get("aliases") or []) if str(item).strip()]
        keys = [note_term, *aliases]
        if normalized in keys:
            exact.append(
                {
                    "term": note_term,
                    "thai_term": str(note.get("thai_term") or "").strip(),
                    "status": _glossary_note_bucket(note),
                    "path": str(note.get("path") or ""),
                    "match_type": "exact",
                }
            )
            continue
        if any(normalized and key and (normalized in key or key in normalized) for key in keys):
            overlap.append(
                {
                    "term": note_term,
                    "thai_term": str(note.get("thai_term") or "").strip(),
                    "status": _glossary_note_bucket(note),
                    "path": str(note.get("path") or ""),
                    "match_type": "overlap",
                }
            )
    return {"exact": exact, "overlap": overlap}


def _glossary_progress_snapshot(artifact: dict[str, Any], queue_snapshot: dict[str, Any]) -> dict[str, Any]:
    decisions = _artifact_decisions(artifact)
    approved_terms, rejected_terms = _decision_metadata(artifact)
    chapter_ids = list(artifact.get("chapter_ids", []))
    pending_items = list(queue_snapshot.get("items") or [])
    total_candidates = len(pending_items) + len(decisions)
    return {
        "chapter_ids": chapter_ids,
        "total_candidates": total_candidates,
        "pending_count": len(pending_items),
        "decided_count": len(decisions),
        "approved_count": len(approved_terms),
        "rejected_count": len(rejected_terms),
        "removed_terms_count": len(queue_snapshot.get("removed_terms") or []),
        "completion_ready": not pending_items,
    }


def build_glossary_suggestion_snapshot(config: AppConfig, run_id: str, term: str) -> dict[str, Any]:
    queue_snapshot = build_glossary_queue_snapshot(config, run_id)
    queue_item = next((item for item in queue_snapshot["items"] if item.get("original_term") == term), None)
    if queue_item is None:
        raise ValueError(f"Term '{term}' is not in the current glossary queue.")
    note_records = _load_operator_glossary_note_records(config)
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
    try:
        artifact = _read_batch_glossary_artifact(config, run_id)
    except Exception:
        artifact = {"chapter_ids": list(queue_snapshot.get("chapter_ids", []))}
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
        "intersections": _glossary_intersections(note_records, term),
        "progress": _glossary_progress_snapshot(artifact, queue_snapshot),
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
        "thai_term": entry.thai_term,
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
      --bg: #f6f7f9;
      --surface: #ffffff;
      --surface-alt: #f0f3f6;
      --surface-soft: #f8fafb;
      --text: #111827;
      --muted: #5b6472;
      --border: #d8dee7;
      --accent: #1769ff;
      --danger: #b42318;
      --warning: #a15c07;
      --ok: #16834b;
      --shadow: 0 1px 2px rgba(16,24,40,.04), 0 10px 30px rgba(16,24,40,.06);
      --radius: 8px;
      font-family: "Segoe UI", Tahoma, sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--text); }
    .shell {
      min-height: 100svh;
      display: grid;
      grid-template-columns: 288px minmax(0, 1fr);
    }
    .nav {
      position: sticky;
      top: 0;
      height: 100svh;
      background: #101828;
      color: #f9fafb;
      padding: 20px 18px;
      border-right: 1px solid rgba(255,255,255,.08);
      overflow-y: auto;
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
    .side-caption {
      color: #98a2b3;
      font-size: 12px;
      line-height: 1.5;
      margin-top: 10px;
    }
    .nav section { margin-bottom: 20px; }
    .focus-nav {
      display: grid;
      grid-template-columns: 1fr;
      gap: 8px;
    }
    .focus-btn {
      height: 38px;
      font-size: 13px;
      text-align: left;
      justify-content: flex-start;
    }
    .focus-btn.active {
      background: #f9fafb;
      color: #111827;
      border-color: rgba(255,255,255,.22);
    }
    .sidebar-run-stack {
      display: grid;
      gap: 8px;
    }
    .nav label, .panel label {
      display: block;
      margin-bottom: 6px;
      font-size: 12px;
      font-weight: 600;
      color: inherit;
    }
    .nav input, .nav select, .panel input, .panel select, .nav textarea, .panel textarea {
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
    .nav input, .nav select { background: rgba(255,255,255,.98); }
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
      transition: background .15s ease, border-color .15s ease, transform .12s ease;
    }
    button:hover { transform: translateY(-1px); }
    button:active { transform: translateY(0); }
    button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible {
      outline: 3px solid rgba(23, 105, 255, .2);
      outline-offset: 1px;
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
      padding: 20px 24px 28px;
      display: grid;
      gap: 16px;
      align-content: start;
    }
    .topbar {
      display: flex;
      align-items: flex-start;
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
    .topbar-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
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
      box-shadow: 0 1px 2px rgba(16,24,40,.04);
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
      grid-template-columns: minmax(0, 1fr) 360px;
      gap: 16px;
    }
    .column-stack {
      display: grid;
      gap: 18px;
      align-content: start;
    }
    .focus-strip {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: -4px;
    }
    .focus-chip {
      border: 1px solid var(--border);
      border-radius: 999px;
      background: var(--surface);
      color: var(--muted);
      padding: 7px 12px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
    }
    .focus-chip.active {
      background: #111827;
      color: #f9fafb;
      border-color: #111827;
    }
    .status-strip {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }
    .overview-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }
    .status-card, .chapter-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 14px;
    }
    .overview-card {
      background: var(--surface-soft);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 14px;
    }
    .overview-card .label {
      font-size: 11px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .04em;
      margin-bottom: 6px;
    }
    .overview-card .value {
      font-size: 14px;
      font-weight: 700;
      color: var(--text);
      margin-bottom: 4px;
    }
    .overview-card .sub {
      font-size: 12px;
      color: var(--muted);
      line-height: 1.45;
      word-break: break-word;
    }
    .command-center {
      border-left: 4px solid var(--accent);
      box-shadow: var(--shadow);
    }
    .command-head {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      margin-bottom: 14px;
    }
    .command-head h3 {
      font-size: 18px;
    }
    .task-label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .04em;
    }
    .detail-panel summary {
      cursor: pointer;
      font-weight: 700;
      list-style: none;
    }
    .detail-panel summary::-webkit-details-marker { display: none; }
    .detail-panel summary::after {
      content: "+";
      float: right;
      color: var(--muted);
    }
    .detail-panel[open] summary::after { content: "-"; }
    .detail-body {
      display: grid;
      gap: 12px;
      margin-top: 14px;
    }
    .status-card .label, .chapter-card .label {
      font-size: 11px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .04em;
      margin-bottom: 6px;
    }
    .status-card .value, .chapter-card .value {
      font-size: 15px;
      font-weight: 700;
      color: var(--text);
      margin-bottom: 4px;
    }
    .status-card .sub, .chapter-card .sub {
      font-size: 12px;
      color: var(--muted);
      line-height: 1.45;
    }
    .chapter-matrix {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 12px;
      margin-bottom: 14px;
    }
    .run-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(180px, 240px);
      gap: 10px;
      align-items: end;
    }
    .panel {
      padding: 16px;
    }
    .panel[data-focus-group][hidden] {
      display: none !important;
    }
    .is-hidden {
      display: none !important;
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
    .action-stack { display: grid; gap: 12px; }
    .dual-stack {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .action-card {
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      background: var(--surface-soft);
    }
    .action-card .meta {
      margin: 0 0 10px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }
    .preview-box {
      margin-top: 10px;
      border: 1px dashed var(--border);
      border-radius: 8px;
      background: var(--surface);
      padding: 10px 12px;
    }
    .preview-box .label {
      font-size: 11px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .04em;
      margin-bottom: 6px;
    }
    .artifact-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
    }
    .artifact-card {
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      background: var(--surface-alt);
    }
    .artifact-card .label {
      font-size: 11px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .04em;
      margin-bottom: 6px;
    }
    .artifact-card .value {
      font-size: 13px;
      font-weight: 700;
      margin-bottom: 6px;
    }
    .employee-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 8px;
    }
    .employee-card {
      display: grid;
      grid-template-columns: 52px minmax(0, 1fr);
      gap: 10px;
      align-items: start;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--surface);
      padding: 10px;
    }
    .employee-avatar {
      width: 48px;
      height: 48px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background-image: url("/api/dashboard-asset?name=employee-chibi-spritesheet.png");
      background-size: 400% 200%;
      background-repeat: no-repeat;
      background-color: #f8fafc;
    }
    .employee-card .employee-title {
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
      margin-bottom: 4px;
    }
    .employee-card .employee-name {
      font-weight: 800;
      font-size: 14px;
    }
    .employee-card .employee-role {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }
    .employee-lines {
      display: grid;
      gap: 3px;
      margin-top: 6px;
    }
    .loading-status {
      margin-top: 12px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #ecfdf5;
      color: #064e3b;
      padding: 10px 12px;
      font-size: 13px;
      display: none;
    }
    .loading-status.active {
      display: block;
    }
    .glossary-progress {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }
    .glossary-progress .overview-card {
      padding: 10px 12px;
    }
    .context-stack {
      display: grid;
      gap: 6px;
    }
    .context-chip {
      display: inline-block;
      border-radius: 999px;
      padding: 4px 8px;
      font-size: 11px;
      font-weight: 700;
      background: var(--surface-alt);
      color: var(--text);
      margin-right: 6px;
      margin-bottom: 6px;
    }
    .context-chip.approved { background: #e7f7ee; color: var(--ok); }
    .context-chip.rejected,
    .context-chip.quarantine,
    .context-chip.deprecated { background: #fdeceb; color: var(--danger); }
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
    .pill.warn { background: #fff4df; color: var(--warning); }
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
    .surface-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
    }
    .surface-card {
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      background: var(--surface-alt);
    }
    .surface-card h4 {
      margin: 0 0 8px;
      font-size: 13px;
    }
    .report-toolbar {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 8px;
      margin-bottom: 14px;
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
    .hero-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.1fr) minmax(260px, .9fr);
      gap: 12px;
      align-items: stretch;
    }
    .active-action-bar {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
      align-items: center;
      border-top: 1px solid var(--border);
      padding-top: 12px;
      margin-top: 12px;
    }
    .decision-copy {
      display: grid;
      gap: 5px;
      min-width: 0;
    }
    .decision-copy .value {
      color: var(--text);
      font-weight: 800;
      line-height: 1.35;
      word-break: break-word;
    }
    .decision-copy .sub {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
      word-break: break-word;
    }
    .blocker-summary {
      display: grid;
      gap: 8px;
      align-content: start;
      min-width: 0;
    }
    .blocker-summary .detail {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
      word-break: break-word;
    }
    .right-rail {
      display: grid;
      gap: 12px;
      align-content: start;
    }
    .task-surface {
      display: grid;
      gap: 12px;
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
      .nav { position: static; height: auto; }
      .metrics, .layout, .hero-grid { grid-template-columns: 1fr; }
      .dual-stack { grid-template-columns: 1fr; }
      .status-strip, .overview-grid, .glossary-progress, .run-row { grid-template-columns: 1fr; }
      .inspect-grid { grid-template-columns: 1fr; }
      .focus-nav { grid-template-columns: 1fr 1fr 1fr; }
      .command-head { display: block; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="nav">
      <h1>Novel Operator</h1>
      <p class="side-caption">Local dashboard for bounded translation work.</p>

      <section>
        <label for="runIdInput">Run ID</label>
        <div class="sidebar-run-stack">
          <input id="runIdInput" placeholder="batch-ch019-ch023-v1">
          <select id="runSelector">
            <option value="">Select known run</option>
          </select>
        </div>
        <div class="btn-row" style="margin-top: 10px;">
          <button class="primary" id="loadRunBtn" data-action-role="read-only">Load Run</button>
          <button class="ghost-dark" id="refreshBtn" data-action-role="read-only">Refresh</button>
        </div>
      </section>

      <section>
        <label>Workspace</label>
        <div class="focus-nav">
          <button class="ghost-dark focus-btn active" data-focus-target="operate" data-task-role="navigation">Continue Translation</button>
          <button class="ghost-dark focus-btn" data-focus-target="glossary" data-task-role="navigation">Review Glossary</button>
          <button class="ghost-dark focus-btn" data-focus-target="recovery" data-task-role="navigation">Recover Block</button>
          <button class="ghost-dark focus-btn" data-focus-target="reports" data-task-role="navigation">Generate Reports</button>
          <button class="ghost-dark focus-btn" data-focus-target="setup" data-task-role="navigation">Project Setup</button>
          <button class="ghost-dark focus-btn" data-focus-target="all" data-task-role="navigation">All Surfaces</button>
        </div>
        <p class="side-caption">Pick one job. State-changing buttons still show scope before execution.</p>
      </section>
    </aside>

    <main class="main">
      <div class="topbar">
        <div>
          <h2 id="runTitle">No run loaded</h2>
          <p id="runSubtitle">Load a run to inspect current status, blocker, and artifacts.</p>
        </div>
        <div class="topbar-actions">
          <button id="providerSmokeBtn" data-action-role="provider-smoke">Smoke Test Providers</button>
        </div>
      </div>

      <section class="panel command-center" id="dailyHome">
        <div class="command-head">
          <div>
            <div class="task-label">Current decision</div>
            <h3 id="taskGuideTitle">Continue Translation</h3>
          </div>
          <div class="mono" id="nextAction">No run loaded.</div>
        </div>
        <div class="hero-grid">
          <div id="runOverview" class="empty">No run loaded.</div>
          <div id="currentBlocker" class="empty">No blocker loaded.</div>
        </div>
        <div class="active-action-bar">
          <div id="taskGuide" class="empty">No run loaded.</div>
          <div class="focus-strip">
            <button class="focus-chip active" data-focus-target="operate" data-task-role="navigation">Continue</button>
            <button class="focus-chip" data-focus-target="glossary" data-task-role="navigation">Glossary</button>
            <button class="focus-chip" data-focus-target="recovery" data-task-role="navigation">Recover</button>
            <button class="focus-chip" data-focus-target="reports" data-task-role="navigation">Reports</button>
            <button class="focus-chip" data-focus-target="setup" data-task-role="navigation">Setup</button>
          </div>
        </div>
        <div id="loadingStatus" class="loading-status" data-loading-state="idle"></div>
      </section>

      <div class="layout">
        <div class="column-stack task-surface">
          <section class="panel" id="batchControlsPanel" data-focus-group="operate,all">
            <h3>Continue Translation</h3>
            <div class="dual-stack">
              <div class="action-card">
                <label for="batchRunId">Start A Bounded Batch</label>
                <div class="inspect-grid">
                  <input id="batchRunId" placeholder="Run ID">
                  <input id="batchChapterRange" placeholder="Chapter range e.g. ch004-ch008">
                  <select id="batchMode">
                    <option value="scan-only">Scan Terms</option>
                    <option value="bounded">Translate Batch</option>
                  </select>
                </div>
                <button class="primary" id="batchBtn" data-action-role="state-changing">Start Batch</button>
                <div id="batchPreview" class="preview-box empty">No batch scope prepared.</div>
              </div>
              <div class="action-card">
                <label for="resumeRunId">Continue To Boundary</label>
                <div class="inspect-grid">
                  <input id="resumeRunId" placeholder="Run ID">
                  <input id="resumeUntilChapter" placeholder="Until chapter e.g. ch022">
                  <input id="resumeUntilBlock" placeholder="Or until block e.g. ch022-block-004">
                </div>
                <button class="primary" id="resumeBtn" data-action-role="state-changing">Continue</button>
                <div id="resumePreview" class="preview-box empty">No bounded resume scope prepared.</div>
              </div>
            </div>
          </section>

          <section class="panel" id="chapterDashboardPanel" data-focus-group="operate,recovery,all">
            <h3>Chapter Progress</h3>
            <div id="chapterMatrix" class="empty">No run loaded.</div>
            <details class="detail-panel" style="margin-top:12px;">
              <summary>Chapter table</summary>
              <div id="chapterTableWrap" class="empty detail-body">No run loaded.</div>
            </details>
          </section>

          <section class="panel" id="glossaryWorkbenchPanel" data-focus-group="glossary,all">
            <h3>Glossary Review</h3>
            <div id="glossaryProgress" class="empty">No glossary progress loaded.</div>
            <div id="glossaryQueue" class="empty">No queue loaded.</div>
          </section>

          <section class="panel" data-focus-group="glossary,all">
            <h3>Glossary Decision</h3>
            <div id="glossaryDecisionPreview" class="preview-box">Provider-assisted suggestions require an explicit click.</div>
            <div id="glossaryDecision" class="empty">No term selected.</div>
          </section>

          <section class="panel" id="blockInspectionPanel" data-focus-group="recovery,all">
            <h3>Block Inspection</h3>
            <div class="inspect-grid">
              <input id="inspectRunId" placeholder="Run ID">
              <input id="inspectBlockId" placeholder="Block ID e.g. ch019-block-002">
              <button class="primary" id="inspectBtn" data-action-role="read-only">Inspect</button>
            </div>
            <div id="inspectResult" class="empty">No block inspected.</div>
          </section>

          <section class="panel" id="recoveryControlsPanel" data-focus-group="recovery,all">
            <h3>Recover Block</h3>
            <div id="recoveryEmptyState" class="empty">No current failures.</div>
            <div class="action-card" id="rerunActionCard">
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
              <button class="primary" id="rerunBtn" data-action-role="state-changing">Run Rerun-Block</button>
              <div id="rerunPreview" class="preview-box empty">No rerun-block scope prepared.</div>
            </div>
            <div id="actionResult" class="preview-box empty">No action executed yet.</div>
          </section>

          <section class="panel" data-focus-group="setup,all">
            <h3>Project Setup</h3>
            <div class="action-stack">
              <div class="action-card">
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
                <button class="primary" id="initNovelBtn" data-action-role="setup-action">Init Novel Project</button>
              </div>
              <div class="action-card">
                <label>Research Profile</label>
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
                <button class="primary" id="saveResearchProfileBtn" data-action-role="setup-action">Save Research Profile</button>
              </div>
            </div>
          </section>
        </div>

        <div class="right-rail">
          <section class="panel" id="employeeStatusPanel" data-focus-group="operate,glossary,recovery,reports,setup,all">
            <div class="command-head">
              <div>
                <h3>Employees</h3>
              </div>
            </div>
            <div id="employeeStatus" class="employee-grid"></div>
            <div id="providerSmokeResult" class="empty" style="margin-top:12px;">Provider smoke test has not run.</div>
          </section>

          <section class="panel" data-focus-group="operate,recovery,all">
            <h3>Manual Actions</h3>
            <ul id="manualActions" class="actions-list"></ul>
          </section>

          <section class="panel" id="reportControlsPanel" data-focus-group="reports,all">
            <h3>Reports</h3>
            <div class="report-toolbar">
              <button class="primary" data-report="preflight" data-action-role="report-action">System Ready?</button>
              <button data-report="checkpoint" data-action-role="report-action">Run Complete?</button>
              <button data-report="cleanliness" data-action-role="report-action">Output Clean?</button>
              <button data-report="provider-usage" data-action-role="report-action">Provider Issue?</button>
              <button data-report="glossary-guard" data-action-role="report-action">Glossary Safe?</button>
              <button data-report="product-review" data-action-role="report-action">Product Gate</button>
              <button data-report="glossary-decisions" data-action-role="report-action">Decisions</button>
              <button data-report="glossary-conflicts" data-action-role="report-action">Conflicts</button>
              <button data-report="glossary-audit" data-action-role="report-action">Audit</button>
              <button data-report="recovery-drill" data-action-role="report-action">Recovery Drill</button>
            </div>
            <div id="reportResult" class="empty">No report generated yet.</div>
          </section>

          <section class="panel" data-focus-group="reports,all">
            <h3>Report Workspace</h3>
            <div id="reportWorkspace" class="empty">No report workspace loaded.</div>
          </section>

          <section class="panel" data-focus-group="setup,reports,all">
            <h3>Research Readiness</h3>
            <div id="researchReadiness" class="empty">No research profile loaded.</div>
          </section>

          <details class="panel detail-panel" data-focus-group="operate,recovery,reports,setup,all">
            <summary>Technical Details</summary>
            <div class="detail-body">
              <section class="metrics" id="metrics"></section>
              <section id="statusStrip" class="status-strip"></section>
              <div>
                <h3>Recovery Hints</h3>
                <div id="commandHints" class="empty">No command hints loaded.</div>
                <div id="quickLinks" class="empty" style="margin-top:12px;">No quick links loaded.</div>
              </div>
              <div>
                <h3>Guardrails</h3>
                <div id="dashboardGuardrails" class="empty">No guardrails loaded.</div>
              </div>
              <div>
                <h3>Preflight</h3>
                <div id="preflightSummary" class="empty">No preflight summary loaded.</div>
              </div>
            </div>
          </details>

          <section class="panel" data-focus-group="operate,recovery,reports,setup,all">
            <h3>Activity</h3>
            <ul id="activityLog" class="actions-list"></ul>
          </section>
        </div>
      </div>
    </main>
  </div>

  <script>
    const state = {
      runId: "",
      snapshot: null,
      activityLog: [],
      focus: "operate",
      loadingStartedAt: null,
      loadingTimer: null,
    };

    const runIdInput = document.getElementById("runIdInput");
    const runSelector = document.getElementById("runSelector");
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

    function setDashboardFocus(focus) {
      state.focus = focus || "operate";
      document.querySelectorAll("[data-focus-target]").forEach((button) => {
        button.classList.toggle("active", button.dataset.focusTarget === state.focus);
      });
      document.querySelectorAll("[data-focus-group]").forEach((element) => {
        const groups = String(element.dataset.focusGroup || "").split(",").map((item) => item.trim()).filter(Boolean);
        const visible = state.focus === "all" || groups.includes(state.focus);
        element.hidden = !visible;
      });
      renderTaskGuide(state.snapshot);
    }

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
        .split(/[\\n,]+/)
        .map((item) => item.trim())
        .filter(Boolean);
    }

    function commandPrefix() {
      const configPath = state.snapshot?.preflight?.config_path || ".system/config.yaml";
      return `novel-pipeline --config "${configPath}"`;
    }

    function renderActionPreview(targetId, title, command, scopeLines) {
      const wrap = document.getElementById(targetId);
      if (!command) {
        wrap.className = "preview-box empty";
        wrap.textContent = "Incomplete action scope.";
        return;
      }
      wrap.className = "preview-box";
      wrap.innerHTML = `
        <div class="label">${escapeHtml(title)}</div>
        <div class="mono">${escapeHtml(command)}</div>
        <ul class="actions-list" style="margin-top:10px;">
          ${scopeLines.map((line) => `<li class="mono">${escapeHtml(line)}</li>`).join("")}
        </ul>
      `;
    }

    function renderActionPreviews() {
      const prefix = commandPrefix();

      const batchRun = batchRunId.value.trim() || state.runId;
      const batchRange = batchChapterRange.value.trim();
      const batchScanOnly = batchMode.value === "scan-only";
      const batchCommand = batchRun && batchRange
        ? `${prefix} run --range ${batchRange} --run-id ${batchRun}${batchScanOnly ? " --stop-after glossary-scan" : ""}`
        : "";
      renderActionPreview(
        "batchPreview",
        batchScanOnly ? "Scan-only gate" : "Bounded batch run",
        batchCommand,
        [
          `run_id=${batchRun || "missing"} | range=${batchRange || "missing"}`,
          batchScanOnly ? "scope: fetch + glossary scan only" : "scope: bounded production run across explicit chapter range",
          batchScanOnly ? "translation readiness: not required" : "translation readiness: bounded path enforced",
        ],
      );

      const resumeRun = resumeRunId.value.trim() || state.runId;
      const untilChapter = resumeUntilChapter.value.trim();
      const untilBlock = resumeUntilBlock.value.trim();
      const resumeBound = untilChapter
        ? `--until-chapter ${untilChapter}`
        : (untilBlock ? `--until-block ${untilBlock}` : "");
      const resumeCommand = resumeRun && resumeBound
        ? `${prefix} resume --run-id ${resumeRun} ${resumeBound} --manual-action-mode stop`
        : "";
      renderActionPreview(
        "resumePreview",
        "Bounded resume",
        resumeCommand,
        [
          `run_id=${resumeRun || "missing"} | boundary=${untilChapter || untilBlock || "missing"}`,
          untilChapter ? "scope: resume through explicit chapter boundary" : "scope: resume through explicit block boundary",
          "guardrail: manual actions force stop, never continue silently",
        ],
      );

      const rerunRun = rerunRunId.value.trim() || state.runId;
      const blockId = rerunBlockId.value.trim();
      const stage = rerunStage.value.trim();
      const rerunCommand = rerunRun && blockId && stage
        ? `${prefix} rerun-block --run-id ${rerunRun} --block-id ${blockId} --from-stage ${stage}`
        : "";
      renderActionPreview(
        "rerunPreview",
        "Rerun block",
        rerunCommand,
        [
          `run_id=${rerunRun || "missing"} | block_id=${blockId || "missing"}`,
          `scope: rerun one block from ${stage || "missing"} only`,
          "guardrail: upstream artifacts reused; no broad resume implied",
        ],
      );
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

    function renderRunSelector(snapshot) {
      const runIds = snapshot?.available_run_ids || [];
      const selected = snapshot?.run_id || "";
      const options = ['<option value="">Select known run</option>']
        .concat(runIds.map((runId) => `<option value="${escapeHtml(runId)}"${runId === selected ? " selected" : ""}>${escapeHtml(runId)}</option>`));
      runSelector.innerHTML = options.join("");
    }

    function resolveCurrentBlocker(snapshot) {
      const status = snapshot?.status || {};
      const preflight = snapshot?.preflight || {};
      const failed = status.current_failed_blocks || [];
      const manualActions = (status.manual_actions || []).filter((item) => String(item || "").trim().toLowerCase() !== "none");
      const blocking = preflight.blocking_reasons || [];
      const warnings = preflight.warnings || [];

      let pillClass = "ok";
      let title = "No active blocker";
      let detail = "Normal bounded operation is allowed.";

      if (blocking.length) {
        pillClass = "danger";
        title = "Preflight blocking";
        detail = blocking.join(" | ");
      } else if (failed.length) {
        pillClass = "danger";
        title = "Failed blocks present";
        detail = failed.join(", ");
      } else if (manualActions.length) {
        pillClass = "danger";
        title = "Manual action required";
        detail = manualActions.join(" | ");
      } else if (preflight.status === "degraded" || warnings.length) {
        pillClass = "";
        title = "Bounded-only caution";
        detail = warnings.join(" | ") || preflight.next_safe_action || "Use bounded controls only.";
      }

      return { pillClass, title, detail };
    }

    function renderTaskGuide(snapshot) {
      const title = document.getElementById("taskGuideTitle");
      const wrap = document.getElementById("taskGuide");
      if (!title || !wrap) {
        return;
      }
      const status = snapshot?.status || {};
      const blocker = resolveCurrentBlocker(snapshot);
      const manualActions = (status.manual_actions || []).filter((item) => String(item || "").trim().toLowerCase() !== "none");
      const failedBlocks = status.current_failed_blocks || [];
      const nextAction = status.next_effective_action || "none";
      const taskMap = {
        operate: {
          title: "Continue Translation",
          detail: snapshot?.run_id
            ? `${blocker.title}.`
            : "Load a run first.",
          action: failedBlocks.length
            ? "Switch to Recover Block before continuing translation."
            : nextAction === "none"
              ? "This run has no pending action. Start a new scan range when source is ready."
              : nextAction,
        },
        glossary: {
          title: "Glossary Review",
          detail: snapshot?.run_id
            ? "Review pending terms one at a time."
            : "Load the scan-only run before reviewing glossary candidates.",
          action: "Load options only when provider-assisted suggestions are acceptable.",
        },
        recovery: {
          title: "Recover Block",
          detail: failedBlocks.length
            ? `Current failed blocks: ${failedBlocks.join(", ")}.`
            : "No current failed blocks.",
          action: failedBlocks.length
            ? "Inspect the failed block, then recover one stage."
            : "No recovery action is needed.",
        },
        reports: {
          title: "Reports",
          detail: "Generate evidence by question.",
          action: "Reports refresh markdown artifacts; they do not translate chapters.",
        },
        setup: {
          title: "Project Setup",
          detail: "Use for a new novel or research profile update.",
          action: "Normal Deep Sea Embers continuation does not require setup.",
        },
        all: {
          title: "All Controls",
          detail: "All surfaces are visible.",
          action: "For normal work, pick one task.",
        },
      };
      const guide = taskMap[state.focus] || taskMap.operate;
      title.textContent = guide.title;
      wrap.className = "decision-copy";
      wrap.innerHTML = `
        <div class="task-label">Task State</div>
        <div class="value">${escapeHtml(guide.detail)}</div>
        <div class="sub">${escapeHtml(guide.action)}</div>
      `;
    }

    function renderStatusStrip(snapshot) {
      const wrap = document.getElementById("statusStrip");
      const preflight = snapshot?.preflight || {};
      const research = snapshot?.research_readiness || {};
      const status = snapshot?.status || {};
      const providers = preflight.providers || [];
      const readyProviders = providers.filter((item) => item.status === "ready").length;
      const blockedProviders = providers.filter((item) => item.status !== "ready").length;
      const failedCount = Array.isArray(status.current_failed_blocks) ? status.current_failed_blocks.length : 0;
      const manualCount = (status.manual_actions || []).filter((item) => String(item || "").trim().toLowerCase() !== "none").length;
      wrap.innerHTML = `
        <div class="status-card">
          <div class="label">Preflight</div>
          <div class="value">${escapeHtml(preflight.status || "unknown")}</div>
          <div class="sub">${escapeHtml(preflight.next_safe_action || "none")}</div>
        </div>
        <div class="status-card">
          <div class="label">Research</div>
          <div class="value">${escapeHtml(research.status || "missing")} / ${escapeHtml(research.readiness || "blocked")}</div>
          <div class="sub">bounded=${research.bounded_translation_ready ? "yes" : "no"} | production=${research.translation_ready ? "yes" : "no"}</div>
        </div>
        <div class="status-card">
          <div class="label">Providers</div>
          <div class="value">${readyProviders} ready / ${blockedProviders} blocked</div>
          <div class="sub">${providers.length} provider routes in current workspace</div>
        </div>
        <div class="status-card">
          <div class="label">Run Pressure</div>
          <div class="value">${failedCount} failed / ${manualCount} manual</div>
          <div class="sub">${escapeHtml(status.run_id || "no run")}</div>
        </div>
      `;
    }

    function renderRunOverview(snapshot) {
      const wrap = document.getElementById("runOverview");
      const status = snapshot?.status || {};
      const chapterIds = status.chapter_ids || [];
      if (!chapterIds.length && !snapshot?.run_id) {
        wrap.className = "empty";
        wrap.textContent = "No run overview available.";
        return;
      }
      const summary = status.chapter_summary || {};
      const blocker = resolveCurrentBlocker(snapshot);
      const manualActions = (status.manual_actions || []).filter((item) => String(item || "").trim().toLowerCase() !== "none");
      const failedChapterCount = chapterIds.filter((chapterId) => (summary[chapterId]?.failed_blocks || []).length > 0).length;
      const pendingChapterCount = chapterIds.filter((chapterId) => (summary[chapterId]?.pending_blocks || []).length > 0).length;
      const outputReadyCount = chapterIds.filter((chapterId) => summary[chapterId]?.output_exists).length;
      const pendingBlockCount = chapterIds.reduce((total, chapterId) => total + ((summary[chapterId]?.pending_blocks || []).length), 0);
      wrap.className = "overview-grid";
      wrap.innerHTML = `
        <div class="overview-card">
          <div class="label">Run Scope</div>
          <div class="value">${escapeHtml(status.run_id || snapshot.run_id || "workspace")}</div>
          <div class="sub">${chapterIds.length} chapters | ${outputReadyCount}/${chapterIds.length} outputs ready</div>
        </div>
        <div class="overview-card">
          <div class="label">Current Blocker</div>
          <div class="value"><span class="pill ${blocker.pillClass}">${escapeHtml(blocker.title)}</span></div>
          <div class="sub">${escapeHtml(blocker.detail)}</div>
        </div>
        <div class="overview-card">
          <div class="label">Next Safe Action</div>
          <div class="value">${escapeHtml(status.next_effective_action || "none")}</div>
          <div class="sub">${manualActions.length} manual actions</div>
        </div>
        <div class="overview-card">
          <div class="label">Chapter Pressure</div>
          <div class="value">${failedChapterCount} failed | ${pendingChapterCount} pending</div>
          <div class="sub">${pendingBlockCount} pending blocks</div>
        </div>
      `;
    }

    function renderGlossaryProgress(data) {
      const wrap = document.getElementById("glossaryProgress");
      const progress = data?.progress || null;
      if (!progress) {
        wrap.className = "empty";
        wrap.textContent = "No glossary progress loaded.";
        return;
      }
      wrap.className = "glossary-progress";
      wrap.innerHTML = `
        <div class="overview-card">
          <div class="label">Candidates</div>
          <div class="value">${progress.total_candidates ?? 0}</div>
          <div class="sub">${(progress.chapter_ids || []).length} chapters in glossary scope</div>
        </div>
        <div class="overview-card">
          <div class="label">Pending</div>
          <div class="value">${progress.pending_count ?? 0}</div>
          <div class="sub">remaining queue items</div>
        </div>
        <div class="overview-card">
          <div class="label">Approved</div>
          <div class="value">${progress.approved_count ?? 0}</div>
          <div class="sub">decisions in current artifact</div>
        </div>
        <div class="overview-card">
          <div class="label">Rejected</div>
          <div class="value">${progress.rejected_count ?? 0}</div>
          <div class="sub">decisions in current artifact</div>
        </div>
        <div class="overview-card">
          <div class="label">Closure</div>
          <div class="value">${progress.completion_ready ? "ready" : "open"}</div>
          <div class="sub">${progress.removed_terms_count ?? 0} removed by guard</div>
        </div>
      `;
    }

    function renderGlossaryIntersectionSummary(intersections) {
      const exact = intersections?.exact || [];
      const overlap = intersections?.overlap || [];
      const all = exact.concat(overlap);
      if (!all.length) {
        return `<span class="context-chip">clean</span>`;
      }
      return all.map((item) => {
        const status = String(item.status || "proposed").trim();
        return `<span class="context-chip ${escapeHtml(status)}">${escapeHtml(status)}:${escapeHtml(item.term || "")}</span>`;
      }).join("");
    }

    function renderChapterMatrix(snapshot) {
      const wrap = document.getElementById("chapterMatrix");
      const summary = snapshot?.status?.chapter_summary || {};
      const chapterIds = snapshot?.status?.chapter_ids || [];
      if (!chapterIds.length) {
        wrap.className = "empty";
        wrap.textContent = "No chapter matrix available.";
        return;
      }
      const sortedChapterIds = [...chapterIds].sort((leftId, rightId) => {
        const left = summary[leftId] || {};
        const right = summary[rightId] || {};
        const leftFailed = (left.failed_blocks || []).length;
        const rightFailed = (right.failed_blocks || []).length;
        if (leftFailed !== rightFailed) {
          return rightFailed - leftFailed;
        }
        const leftPending = (left.pending_blocks || []).length;
        const rightPending = (right.pending_blocks || []).length;
        if (leftPending !== rightPending) {
          return rightPending - leftPending;
        }
        const leftOutputPenalty = left.output_exists ? 0 : 1;
        const rightOutputPenalty = right.output_exists ? 0 : 1;
        if (leftOutputPenalty !== rightOutputPenalty) {
          return rightOutputPenalty - leftOutputPenalty;
        }
        return leftId.localeCompare(rightId);
      });
      const cards = sortedChapterIds.map((chapterId) => {
        const item = summary[chapterId] || {};
        const failed = item.failed_blocks || [];
        const pending = item.pending_blocks || [];
        const nextPendingBlock = pending[0] || "";
        const nextPendingStage = nextPendingBlock ? (item.pending_stages?.[nextPendingBlock] || "?") : "";
        return `
          <div class="chapter-card">
            <div class="label">${escapeHtml(chapterId)}</div>
            <div class="value">${item.completed_blocks ?? 0}/${item.expected_blocks ?? 0} complete</div>
            <div class="sub">failed: ${failed.length ? escapeHtml(failed.join(", ")) : "none"}</div>
            <div class="sub">pending: ${pending.length ? escapeHtml(pending.join(", ")) : "none"}</div>
            <div class="sub">next: ${nextPendingBlock ? `${escapeHtml(nextPendingBlock)} (${escapeHtml(nextPendingStage)})` : "none"}</div>
            <div class="sub">output: ${item.output_exists ? "exists" : "missing"}</div>
          </div>
        `;
      }).join("");
      wrap.className = "chapter-matrix";
      wrap.innerHTML = cards;
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

    function renderCurrentBlocker(snapshot) {
      const wrap = document.getElementById("currentBlocker");
      if (!wrap) {
        return;
      }
      const blocker = resolveCurrentBlocker(snapshot);

      wrap.className = "blocker-summary";
      wrap.innerHTML = `
        <div><span class="pill ${blocker.pillClass}">${escapeHtml(blocker.title)}</span></div>
        <div class="detail">${escapeHtml(blocker.detail)}</div>
      `;
    }

    function renderRecoveryVisibility(snapshot) {
      const failedBlocks = snapshot?.status?.current_failed_blocks || [];
      const manualActions = (snapshot?.status?.manual_actions || []).filter((item) => String(item || "").trim().toLowerCase() !== "none");
      const emptyState = document.getElementById("recoveryEmptyState");
      const rerunCard = document.getElementById("rerunActionCard");
      const shouldShowExecution = failedBlocks.length > 0 || manualActions.length > 0;
      if (emptyState) {
        emptyState.classList.toggle("is-hidden", shouldShowExecution);
        emptyState.textContent = shouldShowExecution
          ? ""
          : "No current failures. Inspect a block only if you need to review artifacts.";
      }
      if (rerunCard) {
        rerunCard.classList.toggle("is-hidden", !shouldShowExecution);
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
      researchProfileAliases.value = Array.isArray(profile.aliases) ? profile.aliases.join("\\n") : "";
      researchProfileSourceUrl.value = profile.source_url || "";
      researchProfileStatus.value = profile.status || "pending";
      researchProfileSynopsis.value = profile.synopsis || "";
      researchProfileTags.value = Array.isArray(profile.tags) ? profile.tags.join("\\n") : "";
      researchProfileStyleNotes.value = profile.style_notes || "";
      researchProfileReaderExpectations.value = profile.reader_expectations || "";
      researchProfileReviewSummary.value = profile.review_summary || "";
      researchProfileLastReviewedAt.value = profile.last_reviewed_at || "";
      researchProfileReviewedBy.value = profile.reviewed_by || "";
      researchProfileTerminology.value = Array.isArray(profile.terminology) ? profile.terminology.join("\\n") : "";
      researchProfileReferenceLinks.value = Array.isArray(profile.reference_links) ? profile.reference_links.join("\\n") : "";
      researchProfileNotes.value = profile.notes || "";
    }

    function renderPreflight(snapshot) {
      const wrap = document.getElementById("preflightSummary");
      const preflight = snapshot?.preflight || {};
      const warnings = preflight.warnings || [];
      const blocking = preflight.blocking_reasons || [];
      const git = preflight.git || {};
      const providerItems = preflight.providers || [];
      const research = preflight.research_readiness || {};
      const pillClass = preflight.status === "ready"
        ? "ok"
        : preflight.status === "degraded"
          ? ""
          : "danger";
      const providerLines = providerItems.length ? providerItems.map((item) => {
        const resolvedPath = item.resolved_path || item.command?.[0] || "none";
        return `<li>${escapeHtml(item.provider)}: ${escapeHtml(item.status || (item.found ? "ready" : "blocked"))} | ${escapeHtml((item.stages || []).join(", ") || "none")} | ${escapeHtml(item.prompt_transport || "none")} | ${escapeHtml(resolvedPath)}</li>`;
      }).join("") : "<li>none</li>";
      const gitLines = [
        `branch: ${git.available ? (git.branch || "(detached)") : "unavailable"}`,
        `head: ${git.head || "none"}`,
        `origin: ${git.origin || "none"}`,
        `working tree: ${git.available ? (git.in_work_tree ? (git.clean ? "clean" : "dirty") : "not a work tree") : "unavailable"}`,
      ].map((line) => `<li>${escapeHtml(line)}</li>`).join("");
      wrap.className = "";
      wrap.innerHTML = `
        <div class="stack">
          <div><span class="pill ${pillClass}">${escapeHtml(preflight.status || "blocked")}</span></div>
          <div class="mono">workspace: ${escapeHtml(preflight.workspace_root || "unknown")}</div>
          <div class="mono">config: ${escapeHtml(preflight.config_path || "unknown")}</div>
          <div class="mono">research: ${escapeHtml(research.status || "missing")} / ${escapeHtml(research.readiness || "blocked")} / bounded=${research.bounded_translation_ready ? "yes" : "no"} / production=${research.translation_ready ? "yes" : "no"}</div>
          <div>
            <strong>Providers</strong>
            <ul class="issues-list">${providerLines}</ul>
          </div>
          <div>
            <strong>Git guardrails</strong>
            <ul class="issues-list">${gitLines}</ul>
          </div>
          <div class="mono">warnings: ${escapeHtml(warnings.length ? warnings.join(" | ") : "none")}</div>
          <div class="mono">blocking: ${escapeHtml(blocking.length ? blocking.join(" | ") : "none")}</div>
          <div class="mono">next safe action: ${escapeHtml(preflight.next_safe_action || "none")}</div>
        </div>
      `;
    }

    function renderCommandHints(snapshot) {
      const wrap = document.getElementById("commandHints");
      const hints = snapshot?.command_hints || {};
      const rows = Object.entries(hints).map(([label, command]) => {
        return `<li><strong>${escapeHtml(label)}</strong><pre class="mono" style="margin:6px 0 0; white-space:pre-wrap;">${escapeHtml(command)}</pre></li>`;
      }).join("");
      if (!rows) {
        wrap.className = "empty";
        wrap.textContent = "No command hints loaded.";
        return;
      }
      wrap.className = "";
      wrap.innerHTML = `<ul class="issues-list">${rows}</ul>`;
    }

    function renderQuickLinks(snapshot) {
      const wrap = document.getElementById("quickLinks");
      const links = snapshot?.quick_links || [];
      if (!links.length) {
        wrap.className = "empty";
        wrap.textContent = "No quick links loaded.";
        return;
      }
      const rows = links.map((item) => `<li>${fileLink(item.path, item.label)}</li>`).join("");
      wrap.className = "";
      wrap.innerHTML = `<ul class="artifact-list">${rows}</ul>`;
    }

    function renderReportWorkspace(snapshot) {
      const wrap = document.getElementById("reportWorkspace");
      const reportSurfaces = snapshot?.report_surfaces || {};
      const active = reportSurfaces.active || {};
      const archive = reportSurfaces.archive || {};
      const renderLinks = (items) => {
        if (!items || !items.length) {
          return '<div class="empty">none</div>';
        }
        return `<ul class="artifact-list">${items.map((item) => `<li>${fileLink(item.path, item.label)}</li>`).join("")}</ul>`;
      };
      const archiveGroups = (archive.groups || []).length
        ? `<ul class="issues-list">${archive.groups.map((item) => `<li><strong>${escapeHtml(item.label)}</strong> <span class="mono">${escapeHtml(String(item.count))} files</span></li>`).join("")}</ul>`
        : '<div class="empty">none</div>';
      wrap.className = "";
      wrap.innerHTML = `
        <div class="surface-grid">
          <div class="surface-card">
            <h4>Active operational reports</h4>
            <div class="mono" style="margin-bottom:8px;">${escapeHtml(String(active.count || 0))} files at 07_Reports root</div>
            <div class="footer-note" style="margin-bottom:8px;">Reference baselines and current generated reports used in daily operation.</div>
            ${renderLinks(active.reference)}
          </div>
          <div class="surface-card">
            <h4>Current generated run reports</h4>
            <div class="footer-note" style="margin-bottom:8px;">Run-scoped outputs that should be regenerated or reviewed from the dashboard.</div>
            ${renderLinks(active.generated)}
          </div>
          <div class="surface-card">
            <h4>Archive</h4>
            <div class="mono" style="margin-bottom:8px;">${escapeHtml(String(archive.count || 0))} files under 07_Reports/archive</div>
            <div class="footer-note" style="margin-bottom:8px;">Historical run evidence and old benchmarks kept for reference, not daily operation.</div>
            ${archiveGroups}
          </div>
          <div class="surface-card">
            <h4>Recent archive files</h4>
            ${renderLinks(archive.recent)}
          </div>
        </div>
        ${active.other_root && active.other_root.length ? `
          <div class="footer-note" style="margin-top:12px;">
            Root reports needing reclassification:
          </div>
          ${renderLinks(active.other_root)}
        ` : ""}
      `;
    }

    function renderDashboardGuardrails(snapshot) {
      const wrap = document.getElementById("dashboardGuardrails");
      const guardrails = snapshot?.dashboard_guardrails || {};
      if (!Object.keys(guardrails).length) {
        wrap.className = "empty";
        wrap.textContent = "No guardrails loaded.";
        return;
      }
      const actions = (guardrails.allowed_state_actions || []).map((item) => `<span class="pill ok">${escapeHtml(item)}</span>`).join(" ");
      const reports = (guardrails.visible_report_kinds || []).map((item) => `<span class="pill">${escapeHtml(item)}</span>`).join(" ");
      wrap.className = "";
      wrap.innerHTML = `
        <div class="stack">
          <div><strong>Allowed state-changing actions</strong></div>
          <div>${actions || '<span class="empty">none</span>'}</div>
          <ul class="issues-list">
            <li>run-batch requires explicit run ID and chapter range; allowed modes: ${escapeHtml((guardrails.run_batch_allowed_modes || []).join(", ") || "none")}</li>
            <li>resume requires an explicit boundary and always uses manual-action-mode=${escapeHtml(guardrails.resume_manual_action_mode || "unknown")}</li>
            <li>rerun-block requires exactly one block ID plus one stage</li>
            <li>research readiness gate for translation actions: ${escapeHtml(guardrails.research_readiness_gate || "unknown")}</li>
            <li>glossary decisions stay limited to current queue terms; inspect only prefills recovery targets</li>
            <li>broad unbounded actions exposed: ${guardrails.broad_unbounded_actions_exposed ? "yes" : "no"}</li>
          </ul>
          <div><strong>Visible report kinds</strong></div>
          <div>${reports || '<span class="empty">none</span>'}</div>
        </div>
      `;
    }

    function logActivity(kind, title, detail, status = "ok") {
      const stamp = new Date().toLocaleTimeString();
      state.activityLog.unshift({ kind, title, detail, status, stamp });
      state.activityLog = state.activityLog.slice(0, 10);
      renderActivityLog();
    }

    function renderActivityLog() {
      const wrap = document.getElementById("activityLog");
      if (!state.activityLog.length) {
        wrap.innerHTML = `<li class="empty">No activity yet.</li>`;
        return;
      }
      wrap.innerHTML = state.activityLog.map((item) => `
        <li>
          <div><span class="pill ${item.status === "error" ? "danger" : item.status === "warn" ? "" : "ok"}">${escapeHtml(item.kind)}</span></div>
          <div class="mono" style="margin-top:6px;">${escapeHtml(item.stamp)} — ${escapeHtml(item.title)}</div>
          <div class="mono" style="margin-top:4px;">${escapeHtml(item.detail || "none")}</div>
        </li>
      `).join("");
    }

    function employeeByCode(code) {
      return (state.snapshot?.employee_status || []).find((employee) => employee.code === code) || null;
    }

    function employeeForAction(action) {
      const actionMap = {
        "bootstrap": "000",
        "run-batch": "000",
        "glossary-queue": "001",
        "glossary-suggestion": "001",
        "glossary-decision": "001",
        "resume": "002",
        "rerun-block": "007",
        "inspect-block": "007",
        "report": "006",
        "provider-smoke": "004",
        "init-novel": "000",
        "save-research-profile": "000",
      };
      return employeeByCode(actionMap[action] || "006");
    }

    function setLoadingStatus(action, detail = "") {
      const employee = employeeForAction(action);
      const wrap = document.getElementById("loadingStatus");
      state.loadingStartedAt = Date.now();
      if (state.loadingTimer) {
        clearInterval(state.loadingTimer);
      }
      const render = () => {
        const elapsed = state.loadingStartedAt ? Math.max(0, Math.round((Date.now() - state.loadingStartedAt) / 1000)) : 0;
        wrap.className = "loading-status active";
        wrap.dataset.loadingState = "active";
        wrap.innerHTML = `
          <strong>${escapeHtml(employee ? `${employee.code} ${employee.name}` : "Worker")}</strong>
          <span class="mono"> action=${escapeHtml(action)} | provider=${escapeHtml(employee?.provider_model || "local")} | elapsed=${elapsed}s</span>
          <div class="mono" style="margin-top:4px;">${escapeHtml(detail || "Waiting for response...")}</div>
        `;
      };
      render();
      state.loadingTimer = setInterval(render, 1000);
    }

    function clearLoadingStatus(message = "") {
      const wrap = document.getElementById("loadingStatus");
      if (state.loadingTimer) {
        clearInterval(state.loadingTimer);
        state.loadingTimer = null;
      }
      if (message) {
        wrap.className = "loading-status active";
        wrap.dataset.loadingState = "done";
        wrap.innerHTML = `<strong>Done</strong><span class="mono"> ${escapeHtml(message)}</span>`;
      } else {
        wrap.className = "loading-status";
        wrap.dataset.loadingState = "idle";
        wrap.textContent = "";
      }
      state.loadingStartedAt = null;
    }

    function spritePosition(index) {
      const col = index % 4;
      const row = Math.floor(index / 4);
      return `${col * 33.3333}% ${row * 100}%`;
    }

    function renderEmployeeStatus(snapshot) {
      const wrap = document.getElementById("employeeStatus");
      const employees = snapshot?.employee_status || [];
      if (!employees.length) {
        wrap.className = "empty";
        wrap.textContent = "No employee status available.";
        return;
      }
      wrap.className = "employee-grid";
      wrap.innerHTML = employees.map((employee) => {
        const readinessClass = employee.readiness === "ready" ? "ok" : employee.readiness === "blocked" ? "danger" : "";
        const mapped = (employee.maps_to || []).join(", ");
        return `
          <article class="employee-card" data-employee-code="${escapeHtml(employee.code)}">
            <div class="employee-avatar" role="img" aria-label="${escapeHtml(employee.name)} chibi" style="background-position:${spritePosition(employee.index || 0)};"></div>
            <div>
              <div class="employee-title">
                <span class="pill">${escapeHtml(employee.code)}</span>
                <span class="employee-name">${escapeHtml(employee.name)}</span>
                <span class="pill ${readinessClass}">${escapeHtml(employee.readiness || "unknown")}</span>
              </div>
              <div class="employee-role">${escapeHtml(employee.role || employee.archetype || "")}</div>
              <div class="employee-lines">
                <div class="mono">work: ${escapeHtml(mapped)}</div>
                <div class="mono">route: ${escapeHtml(employee.provider_model || "local")}</div>
              </div>
              <div class="employee-role" style="margin-top:6px;">${escapeHtml(employee.latest_activity || "No recent activity.")}</div>
            </div>
          </article>
        `;
      }).join("");
    }

    function renderSnapshot(snapshot) {
      state.snapshot = snapshot;
      const runId = snapshot?.run_id || "";
      setRunId(runId);
      renderRunSelector(snapshot);
      const status = snapshot?.status || {};
      const chapterIds = status.chapter_ids || [];
      const summary = status.chapter_summary || {};
      const outputReadyCount = chapterIds.filter((chapterId) => summary[chapterId]?.output_exists).length;
      const failedCount = Array.isArray(status.current_failed_blocks) ? status.current_failed_blocks.length : 0;
      document.getElementById("runTitle").textContent = runId || "No run loaded";
      document.getElementById("runSubtitle").textContent = runId
        ? `${chapterIds.length} chapters | ${outputReadyCount}/${chapterIds.length} outputs ready | ${failedCount} current failed blocks`
        : (snapshot?.available_run_ids?.length
          ? `${snapshot.available_run_ids.length} known run IDs in ledger.`
          : "No runs recorded.");
      document.getElementById("nextAction").textContent = snapshot?.status?.next_effective_action || "none";
      renderMetrics(snapshot);
      renderStatusStrip(snapshot);
      renderRunOverview(snapshot);
      renderEmployeeStatus(snapshot);
      renderChapterMatrix(snapshot);
      renderChapterTable(snapshot);
      renderCurrentBlocker(snapshot);
      renderResearchReadiness(snapshot);
      renderResearchProfileEditor(snapshot);
      renderPreflight(snapshot);
      renderCommandHints(snapshot);
      renderQuickLinks(snapshot);
      renderReportWorkspace(snapshot);
      renderDashboardGuardrails(snapshot);
      renderManualActions(snapshot);
      renderRecoveryVisibility(snapshot);
      renderActionPreviews();
      setDashboardFocus(state.focus);
    }

    async function loadSnapshot(runId = "") {
      setLoadingStatus("bootstrap", "Loading read-only status snapshot.");
      try {
        const query = runId ? `?run_id=${encodeURIComponent(runId)}` : "";
        const response = await fetch(`/api/bootstrap${query}`);
        const data = await response.json();
        renderSnapshot(data);
        logActivity("snapshot", runId || data.run_id || "latest", response.ok ? "Snapshot loaded." : (data.error || "Snapshot failed."), response.ok ? "ok" : "error");
        if (data.run_id) {
          await loadGlossaryQueue(data.run_id);
        }
        clearLoadingStatus("Snapshot loaded.");
      } catch (error) {
        clearLoadingStatus("Snapshot failed.");
        logActivity("snapshot", runId || "latest", String(error), "error");
      }
    }

    async function loadGlossaryQueue(runId) {
      setLoadingStatus("glossary-queue", "Loading glossary queue without provider calls.");
      const response = await fetch(`/api/glossary-queue?run_id=${encodeURIComponent(runId)}`);
      const data = await response.json();
      const wrap = document.getElementById("glossaryQueue");
      renderGlossaryProgress(data);
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
          <td>${renderGlossaryIntersectionSummary(item.intersections)}</td>
          <td>${escapeHtml(item.chapter_id || "")}</td>
          <td class="mono">${escapeHtml(item.first_seen_block || "")}</td>
          <td><button data-term="${escapeHtml(item.original_term || "")}" class="load-suggestion-btn" data-action-role="provider-assisted">Load options</button></td>
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
              <th>History Context</th>
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
      clearLoadingStatus("Glossary queue loaded.");
    }

    async function loadGlossarySuggestion(term) {
      const runId = state.runId || runIdInput.value.trim();
      if (!runId || !term) {
        document.getElementById("glossaryDecision").innerHTML = `<div class="empty">Run ID and term are required.</div>`;
        return;
      }
      setLoadingStatus("glossary-suggestion", `Loading provider-assisted options for ${term}.`);
      const response = await fetch(`/api/glossary-suggestion?run_id=${encodeURIComponent(runId)}&term=${encodeURIComponent(term)}`);
      const data = await response.json();
      const wrap = document.getElementById("glossaryDecision");
      if (!response.ok) {
        wrap.innerHTML = `<div class="empty">${escapeHtml(data.error || "Failed to load suggestions.")}</div>`;
        logActivity("glossary", term, data.error || "Failed to load suggestions.", "error");
        clearLoadingStatus("Glossary suggestion failed.");
        return;
      }
      logActivity("glossary", data.term || term, "Loaded Thai suggestion options.");
      currentGlossarySuggestion = data;
      const optionRows = (data.options || []).map((option, index) => {
        const rationale = (data.rationales || [])[index] || "";
        return `<option value="${escapeHtml(option)}">${escapeHtml(option)}${rationale ? " — " + escapeHtml(rationale) : ""}</option>`;
      }).join("");
      const contextPreview = (data.context || []).join("\\n\\n");
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
            <button class="primary" id="approveTermBtn" data-action-role="state-changing">Approve Selected Option</button>
            <button id="rejectTermBtn" data-action-role="state-changing">Reject Term</button>
          </div>
        </div>
      `;
      document.getElementById("approveTermBtn").addEventListener("click", () => submitGlossaryDecision("approve"));
      document.getElementById("rejectTermBtn").addEventListener("click", () => submitGlossaryDecision("reject"));
      clearLoadingStatus("Glossary options loaded.");
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
      setLoadingStatus("glossary-decision", `${decision} ${currentGlossarySuggestion.term}.`);
      const response = await fetch("/api/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        document.getElementById("actionResult").innerHTML = `<div class="empty">${escapeHtml(data.error || "Glossary decision failed.")}</div>`;
        logActivity("glossary", currentGlossarySuggestion.term, data.error || "Glossary decision failed.", "error");
        clearLoadingStatus("Glossary decision failed.");
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
          ${data.thai_term ? `<div class="mono">${escapeHtml(data.thai_term)}</div>` : ""}
          <div class="mono">${data.committed ? "glossary_approved committed" : "queue updated"}</div>
        </div>
      `;
      if (data.snapshot) {
        renderSnapshot(data.snapshot);
      }
      logActivity("glossary", data.term, data.committed ? "Decision saved and glossary approval committed." : "Decision saved and queue updated.");
      await loadGlossaryQueue(data.run_id || state.runId);
      clearLoadingStatus("Glossary decision saved.");
    }

    async function inspectBlock() {
      const runId = inspectRunId.value.trim() || state.runId;
      const blockId = inspectBlockId.value.trim();
      if (!runId || !blockId) {
        document.getElementById("inspectResult").innerHTML = `<div class="empty">Run ID and block ID are required.</div>`;
        return;
      }
      setLoadingStatus("inspect-block", `Inspecting ${blockId}.`);
      const response = await fetch(`/api/inspect-block?run_id=${encodeURIComponent(runId)}&block_id=${encodeURIComponent(blockId)}`);
      const data = await response.json();
      if (!response.ok) {
        document.getElementById("inspectResult").innerHTML = `<div class="empty">${escapeHtml(data.error || "Inspect failed.")}</div>`;
        logActivity("inspect", blockId, data.error || "Inspect failed.", "error");
        clearLoadingStatus("Inspect failed.");
        return;
      }
      const artifactEntries = Object.entries(data.artifact_paths || {}).map(([stage, path]) => {
        const exists = data.artifact_exists?.[stage];
        const label = `${stage} (${exists ? "exists" : "missing"})`;
        return `
          <div class="artifact-card">
            <div class="label">${escapeHtml(stage)}</div>
            <div class="value">${exists ? "exists" : "missing"}</div>
            <div class="mono">${exists ? fileLink(path, label) : escapeHtml(path)}</div>
          </div>
        `;
      }).join("");
      const issues = (data.formatted_validation_issues || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
      const latestStages = Object.entries(data.latest_by_stage || {}).map(([stage, record]) => `
        <li class="mono">${escapeHtml(stage)}: ${escapeHtml(record.status || "unknown")} / ${escapeHtml(record.provider || "unknown")}</li>
      `).join("");
      const rerunStage = data.next_pending_stage || "qa";
      document.getElementById("inspectResult").innerHTML = `
        <div class="stack">
          <div><span class="pill ${data.next_pending_stage ? "danger" : "ok"}">${data.next_pending_stage ? "pending " + escapeHtml(data.next_pending_stage) : "complete"}</span></div>
          <div class="mono">chapter: ${escapeHtml(data.chapter_id)}</div>
          <div>
            <strong>Artifacts</strong>
            <div class="artifact-grid">${artifactEntries}</div>
          </div>
          <div>
            <strong>Latest Stage State</strong>
            ${latestStages ? `<ul class="issues-list">${latestStages}</ul>` : `<div class="empty">none</div>`}
          </div>
          <div>
            <strong>Formatted validation issues</strong>
            ${issues ? `<ul class="issues-list">${issues}</ul>` : `<div class="empty">none</div>`}
          </div>
          <div class="preview-box">
            <div class="label">Recovery target</div>
            <div class="mono">recommended rerun stage: ${escapeHtml(rerunStage)}</div>
            <div class="btn-row" style="margin-top:10px;">
              <button class="primary" id="inspectUsePendingStageBtn" data-action-role="read-only">Use Pending Stage</button>
              <button id="inspectUseQaStageBtn" data-action-role="read-only">Use QA Stage</button>
            </div>
          </div>
          <div class="mono">ledger records: ${(data.records || []).length}</div>
        </div>
      `;
      document.getElementById("inspectUsePendingStageBtn").addEventListener("click", () => setRerunTargetFromInspect(runId, blockId, rerunStage));
      document.getElementById("inspectUseQaStageBtn").addEventListener("click", () => setRerunTargetFromInspect(runId, blockId, "qa"));
      logActivity("inspect", blockId, data.next_pending_stage ? `Pending ${data.next_pending_stage}.` : "Block complete.");
      clearLoadingStatus("Block inspected.");
    }

    function setRerunTargetFromInspect(runId, blockId, stage) {
      rerunRunId.value = runId || state.runId || "";
      rerunBlockId.value = blockId || "";
      rerunStage.value = stage || "qa";
      renderActionPreviews();
      logActivity("rerun-target", blockId || "none", `Prepared rerun-block from ${stage || "qa"}.`);
    }

    async function generateReport(kind) {
      const runId = state.runId || runIdInput.value.trim();
      if (kind !== "preflight" && !runId) {
        document.getElementById("reportResult").innerHTML = `<div class="empty">Run ID is required.</div>`;
        return;
      }
      setLoadingStatus("report", `Generating ${kind} report.`);
      const response = await fetch("/api/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: runId, kind }),
      });
      const data = await response.json();
      if (!response.ok) {
        document.getElementById("reportResult").innerHTML = `<div class="empty">${escapeHtml(data.error || "Report generation failed.")}</div>`;
        logActivity("report", kind, data.error || "Report generation failed.", "error");
        clearLoadingStatus("Report generation failed.");
        return;
      }
      document.getElementById("reportResult").innerHTML = `
        <div class="stack">
          <div><span class="pill ${data.actionable_failure ? "danger" : "ok"}">${data.actionable_failure ? "actionable" : "ok"}</span></div>
          <div>${fileLink(data.path, data.path)}</div>
        </div>
      `;
      logActivity("report", kind, data.path, data.actionable_failure ? "warn" : "ok");
      clearLoadingStatus("Report generated.");
    }

    async function runAction(action, payload) {
      setLoadingStatus(action, `Executing ${action}; waiting for backend result.`);
      const response = await fetch("/api/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      const target = document.getElementById("actionResult");
      if (!response.ok) {
        target.innerHTML = `<div class="empty">${escapeHtml(data.error || "Action failed.")}</div>`;
        logActivity(action, payload.run_id || state.runId || "none", data.error || "Action failed.", "error");
        clearLoadingStatus(`${action} failed.`);
        return;
      }
      const initPaths = data.paths || data.snapshot?.init_novel_paths || null;
      const commandPreview = action === "run-batch"
        ? document.getElementById("batchPreview")?.querySelector(".mono")?.textContent
        : action === "resume"
          ? document.getElementById("resumePreview")?.querySelector(".mono")?.textContent
          : action === "rerun-block"
            ? document.getElementById("rerunPreview")?.querySelector(".mono")?.textContent
            : "";
      target.innerHTML = `
        <div class="stack">
          <div><span class="pill ok">${escapeHtml(data.action)}</span></div>
          ${commandPreview ? `<div class="mono">${escapeHtml(commandPreview)}</div>` : ""}
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
      logActivity(action, payload.run_id || state.runId || "workspace", data.output || "Action completed.");
      clearLoadingStatus(`${action} completed.`);
    }

    async function runProviderSmoke() {
      const confirmed = window.confirm("Provider smoke test will call configured AI provider CLIs with tiny prompts. Continue?");
      if (!confirmed) {
        return;
      }
      setLoadingStatus("provider-smoke", "Running explicit provider smoke checks.");
      const response = await fetch("/api/provider-smoke", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ confirm: true }),
      });
      const data = await response.json();
      const wrap = document.getElementById("providerSmokeResult");
      if (!response.ok) {
        wrap.className = "empty";
        wrap.textContent = data.error || "Provider smoke failed.";
        logActivity("provider-smoke", "failed", data.error || "Provider smoke failed.", "error");
        clearLoadingStatus("Provider smoke failed.");
        return;
      }
      const rows = (data.results || []).map((item) => `
        <li class="mono">
          ${escapeHtml(item.provider)}/${escapeHtml(item.model || "default")}:
          ${escapeHtml(item.status)} ${item.failure_kind ? `(${escapeHtml(item.failure_kind)})` : ""}
        </li>
      `).join("");
      wrap.className = "";
      wrap.innerHTML = `<ul class="actions-list">${rows || '<li class="empty">No provider routes tested.</li>'}</ul>`;
      logActivity("provider-smoke", "complete", `${(data.results || []).length} routes tested.`);
      clearLoadingStatus("Provider smoke complete.");
    }

    document.getElementById("loadRunBtn").addEventListener("click", () => loadSnapshot(runIdInput.value.trim() || runSelector.value.trim()));
    document.getElementById("refreshBtn").addEventListener("click", () => loadSnapshot(state.runId || runIdInput.value.trim()));
    document.getElementById("providerSmokeBtn").addEventListener("click", runProviderSmoke);
    runSelector.addEventListener("change", () => {
      const runId = runSelector.value.trim();
      runIdInput.value = runId;
      if (runId) {
        loadSnapshot(runId);
      }
    });
    [batchRunId, batchChapterRange, batchMode, resumeRunId, resumeUntilChapter, resumeUntilBlock, rerunRunId, rerunBlockId, rerunStage]
      .forEach((element) => {
        element.addEventListener("input", renderActionPreviews);
        element.addEventListener("change", renderActionPreviews);
      });
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
    document.querySelectorAll("[data-focus-target]").forEach((button) => {
      button.addEventListener("click", () => setDashboardFocus(button.dataset.focusTarget || "operate"));
    });

    setDashboardFocus(state.focus);
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
        if parsed.path == "/api/dashboard-asset":
            name = Path((params.get("name") or [""])[0]).name
            if name not in {"employee-chibi-spritesheet.png", "employee-chibi-spritesheet-source.png"}:
                self._send_text("Unsupported dashboard asset.", status=400)
                return
            asset_path = self.config.workspace.root / "assets" / "dashboard" / name
            if not asset_path.exists():
                self._send_text("Dashboard asset not found.", status=404)
                return
            body = asset_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self._send_json({"error": "Not found."}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path not in {"/api/report", "/api/action", "/api/provider-smoke"}:
            self._send_json({"error": "Not found."}, status=404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            payload = json.loads(raw)
            if parsed.path == "/api/provider-smoke":
                result = run_provider_smoke_tests(self.config, confirm=bool(payload.get("confirm")))
                self._send_json(result)
                return
            if parsed.path == "/api/report":
                run_id = str(payload.get("run_id") or "").strip()
                kind = str(payload.get("kind") or "").strip()
                chapter_ids = payload.get("chapter_ids")
                if not kind:
                    self._send_json({"error": "kind is required."}, status=400)
                    return
                if kind not in {"preflight", "recovery-drill"} and not run_id:
                    self._send_json({"error": "run_id and kind are required."}, status=400)
                    return
                result = generate_operator_report(
                    config=self.config,
                    run_id=run_id or None,
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
