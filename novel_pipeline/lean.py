"""Run the chapter-aware Lean pipeline.

The production CLI delegates bounded runs here. It translates blocks
for transport safety, then refines, checks, and formats the assembled chapter
once. Every provider call is traced when ``--trace-dir`` is supplied.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from novel_pipeline.config import load_app_config
from novel_pipeline.glossary_support import load_glossary_index, select_non_overlapping_glossary_entries
from novel_pipeline.pipeline import (
    _apply_source_script_annotation_repairs,
    _load_chapter_source_and_blocks,
    _resolve_chapter_output_title,
    validate_formatted_text,
)
from novel_pipeline.prompts import PromptStore
from novel_pipeline.providers.base import ProviderExecutionError, ProviderOutputError, ProviderRunner, ensure_provider_response
from novel_pipeline.stages.qa import run_qa_stage
from novel_pipeline.stages.refine import run_refine_stage
from novel_pipeline.stages.translate import run_literal_translation_stage
from novel_pipeline.types import GlossaryEntry, LiteralDraft, LiteralSentencePair, RefinedDraft, TextBlock, ProviderRequest
from novel_pipeline.files import atomic_write_json


class ChapterQualityError(RuntimeError):
    """An unsafe chapter candidate that may be recovered without stopping others."""


def _repair_refined_source_annotations(refined: RefinedDraft, *, novel_id: str = "") -> RefinedDraft:
    """Remove copied source-script annotations before Lean's deterministic QA."""
    repaired_text, source_script_repairs = _apply_source_script_annotation_repairs(refined.refined_text)
    repaired_text, tdu_repairs = _apply_tdu_repairs(repaired_text, novel_id=novel_id)
    if not source_script_repairs and not tdu_repairs:
        return refined
    return RefinedDraft(
        block_id=refined.block_id,
        chapter_id=refined.chapter_id,
        refined_text=repaired_text,
        provider=refined.provider,
        style_profile=refined.style_profile,
        source_text=refined.source_text,
        metadata={
            **refined.metadata,
            "source_script_annotation_repairs": source_script_repairs,
            "tdu_repairs": tdu_repairs,
        },
    )


_TDU_REPAIR_RULES: tuple[tuple[str, str], ...] = (
    ("\u0e09\u0e35\u0e0b\u0e35\u0e48\u0e22", "\u0e09\u0e35\u0e40\u0e0b\u0e35\u0e48\u0e22"),
    ("\u0e09\u0e35\u0e0b\u0e35\u0e48", "\u0e09\u0e35\u0e40\u0e0b\u0e35\u0e48\u0e22"),
    ("\u0e2e\u0e27\u0e32\u0e2d\u0e35\u0e42\u0e21\u0e48", "\u0e2b\u0e32\u0e19\u0e2d\u0e35\u0e42\u0e21\u0e48"),
    ("\u0e1e\u0e27\u0e01\u0e40\u0e02\u0e48\u0e32", "\u0e1e\u0e27\u0e01\u0e40\u0e02\u0e32"),
    ("\u0e1e\u0e27\u0e01\u0e40\u0e23\u0e21\u0e35", "\u0e1e\u0e27\u0e01\u0e40\u0e23\u0e32\u0e21\u0e35"),
    ("\u0e1e\u0e27\u0e01\u0e40\u0e23\u0e08\u0e30", "\u0e1e\u0e27\u0e01\u0e40\u0e23\u0e32\u0e08\u0e30"),
    ("\u0e1e\u0e27\u0e01\u0e40\u0e23\u0e17\u0e38\u0e01\u0e04\u0e19", "\u0e1e\u0e27\u0e01\u0e40\u0e23\u0e32\u0e17\u0e38\u0e01\u0e04\u0e19"),
    ("\u0e1e\u0e27\u0e01\u0e40\u0e23\u0e01\u0e47", "\u0e1e\u0e27\u0e01\u0e40\u0e23\u0e32\u0e01\u0e47"),
    ("\u0e1e\u0e27\u0e01\u0e40\u0e02\u0e01\u0e47", "\u0e1e\u0e27\u0e01\u0e40\u0e02\u0e32\u0e01\u0e47"),
    ("\u0e21\u0e32\u0e08\u0e08\u0e19\u0e16\u0e36\u0e07", "\u0e21\u0e32\u0e08\u0e19\u0e16\u0e36\u0e07"),
    ("\u0e04\u0e27\u0e32\u0e21\u0e0b\u0e37\u0e48\u0e2d\u0e2a\u0e31\u0e22\u0e4c", "\u0e04\u0e27\u0e32\u0e21\u0e0b\u0e37\u0e48\u0e2d\u0e2a\u0e31\u0e15\u0e22\u0e4c"),
    ("\u0e04\u0e48\u0e2d\u0e19\u0e01", "\u0e04\u0e48\u0e2d\u0e19\u0e02\u0e49\u0e32\u0e07"),
    ("\u0e41\u0e48\u0e41\u0e25\u0e49\u0e27", "\u0e41\u0e22\u0e48\u0e41\u0e25\u0e49\u0e27"),
    ("\u0e40\u0e02\u0e04\u0e48\u0e2d\u0e22", "\u0e40\u0e02\u0e32\u0e04\u0e48\u0e2d\u0e22"),
    ("\u0e40\u0e18\u0e08\u0e30", "\u0e40\u0e18\u0e2d\u0e08\u0e30"),
    ("\u0e40\u0e18\u0e40\u0e0a\u0e37\u0e48\u0e2d", "\u0e40\u0e18\u0e2d\u0e40\u0e0a\u0e37\u0e48\u0e2d"),
    ("\u0e1e\u0e27\u0e01\u0e40\u0e18\u0e25\u0e2d\u0e07", "\u0e1e\u0e27\u0e01\u0e40\u0e18\u0e2d\u0e25\u0e2d\u0e07"),
    ("\u0e40\u0e18\u0e01\u0e47", "\u0e40\u0e18\u0e2d\u0e01\u0e47"),
    ("\u0e40\u0e0a\u0e37\u0e48\u0e2d\u0e40\u0e18", "\u0e40\u0e0a\u0e37\u0e48\u0e2d\u0e40\u0e18\u0e2d"),
    ("\u0e40\u0e18\u0e14\u0e39", "\u0e40\u0e18\u0e2d\u0e14\u0e39"),
    ("\u0e40\u0e2b\u0e23?", "\u0e40\u0e2b\u0e23\u0e2d?"),
    ("\u0e40\u0e02\u0e49\u0e32\u0e23\u0e39\u0e49\u0e14\u0e35\u0e27\u0e48\u0e32", "\u0e40\u0e02\u0e32\u0e23\u0e39\u0e49\u0e14\u0e35\u0e27\u0e48\u0e32"),
    ("\u0e09\u0e35\u0e40\u0e0b\u0e35\u0e48\u0e22\u0e35\u0e48\u0e15\u0e32\u0e25\u0e07", "\u0e09\u0e35\u0e40\u0e0b\u0e35\u0e48\u0e22\u0e2b\u0e23\u0e35\u0e48\u0e15\u0e32\u0e25\u0e07"),
    ("\u0e09\u0e35\u0e40\u0e0b\u0e35\u0e48\u0e22\u0e37\u0e19\u0e2d\u0e22\u0e39\u0e48", "\u0e09\u0e35\u0e40\u0e0b\u0e35\u0e48\u0e22\u0e22\u0e37\u0e19\u0e2d\u0e22\u0e39\u0e48"),
)


def _apply_tdu_repairs(text: str, *, novel_id: str) -> tuple[str, list[dict[str, str]]]:
    """Repair only observed, source-backed TDU spelling/name variants."""
    if novel_id != "ten-day-ultimatum":
        return text, []
    repaired = text
    repairs: list[dict[str, str]] = []
    for source, target in _TDU_REPAIR_RULES:
        count = repaired.count(source)
        if not count:
            continue
        repaired = repaired.replace(source, target)
        repairs.append({"source": source, "target": target, "count": str(count)})
    return repaired, repairs


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_digest(path: Path) -> str:
    if not path.exists():
        return "missing"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pipeline_prompt_digest(config: Any) -> str:
    names = ("literal_translation.md", "refinement.md", "qa_judge.md", "term_harvest.md")
    files = {name: _file_digest(ROOT / "prompts" / "lean" / name) for name in names}
    files["lean_voice.md"] = _file_digest(config.workspace.system / "lean_voice.md")
    files["providers.yaml"] = _file_digest(config.workspace.system / "providers.yaml")
    files["config.yaml"] = _file_digest(config.config_path)
    files["style_profiles.yaml"] = _file_digest(config.workspace.system / "style_profiles.yaml")
    research_path = config.workspace.root / "RESEARCH_PROFILE.yaml"
    files["RESEARCH_PROFILE.yaml"] = _file_digest(research_path)
    return _digest(files)


def _glossary_digest(glossary: dict[str, Any]) -> str:
    entries = [entry.to_dict() for entry in glossary.values()]
    return _digest(entries)


def _checkpoint_input_hash(*, stage: str, source_hash: str, glossary_hash: str, prompt_hash: str, dependencies: dict[str, str] | None = None) -> str:
    return _digest(
        {
            "stage": stage,
            "source_hash": source_hash,
            "glossary_hash": glossary_hash,
            "prompt_hash": prompt_hash,
            "dependencies": dependencies or {},
        }
    )


def _read_matching_checkpoint(path: Path, expected_input_hash: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None
    if payload.get("input_hash") != expected_input_hash:
        return None
    return payload


def _context(*, run_id: str, chapter_id: str, stage: str, block_id: str = "") -> None:
    os.environ["NOVEL_PIPELINE_TRACE_CONTEXT"] = json.dumps(
        {
            "run_id": run_id,
            "chapter_id": chapter_id,
            "stage": stage,
            "block_id": block_id,
            "experiment_arm": "lean",
        },
        ensure_ascii=False,
    )


def _parse_chapters(value: str) -> list[str]:
    chapters: list[str] = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        range_match = re.fullmatch(r"(?:ch)?(\d+)\s*-\s*(?:ch)?(\d+)", item, re.IGNORECASE)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if start > end:
                raise ValueError(f"Invalid descending chapter range: {item}")
            chapters.extend(f"ch{number:03d}" for number in range(start, end + 1))
            continue
        if re.fullmatch(r"\d+", item):
            item = f"ch{int(item):03d}"
        if not re.fullmatch(r"ch\d+", item):
            raise ValueError(f"Invalid chapter id: {item}")
        chapters.append(item)
    if not chapters:
        raise ValueError("At least one chapter is required.")
    return list(dict.fromkeys(chapters))


def _chapter_glossary_subset(block: TextBlock, glossary: dict[str, Any]) -> list[Any]:
    return select_non_overlapping_glossary_entries(block.source_text, glossary.values())


def _run_qa_with_configured_fallbacks(
    *,
    config: Any,
    block: TextBlock,
    literal_draft: LiteralDraft,
    refined_draft: RefinedDraft,
    glossary_subset: list[Any],
    style_profile_key: str,
) -> Any:
    """Run experiment QA through the configured route, including fallbacks."""
    routing = config.stage_routing_for("qa_judge")
    routes = [(config.provider_for_stage("qa_judge"), routing.model)]
    routes.extend(config.fallback_routes_for_stage("qa_judge"))
    failures: list[str] = []
    previous_judge_feedback = ""
    for index, (provider_spec, model) in enumerate(routes):
        try:
            report = run_qa_stage(
                config=config,
                block=block,
                literal_draft=literal_draft,
                refined_draft=refined_draft,
                glossary_subset=glossary_subset,
                provider_runner=ProviderRunner(provider_spec),
                model=model,
                style_profile_key=style_profile_key,
                retry_feedback=(
                    "Review only the previous judge's alleged issue(s), and decide whether each is supported by the supplied source and refined text. "
                    f"Previous judge feedback: {previous_judge_feedback}"
                    if previous_judge_feedback
                    else ""
                ),
                prompt_store=PromptStore(ROOT / "prompts" / "lean"),
            )
            report.metadata["qa_route_index"] = index
            report.metadata["qa_fallback_used"] = index > 0
            if failures:
                report.metadata["qa_primary_failures"] = failures
            # A valid AI FAIL is evidence to adjudicate, not a provider crash.
            # Give the configured fallback an independent chance to verify it;
            # deterministic rule failures still return immediately above.
            if not report.passed and report.judge_provider != "rules" and index < len(routes) - 1:
                previous_judge_feedback = report.feedback
                failures.append(f"{provider_spec.name}: QA rejected draft: {report.feedback}")
                continue
            if previous_judge_feedback and report.passed and not _has_verbatim_adjudication_evidence(
                report.feedback,
                source_text=block.source_text,
                refined_text=refined_draft.refined_text,
            ):
                report.passed = False
                report.feedback = (
                    "QA disagreement unresolved: the fallback PASS did not quote a source passage "
                    "and its corresponding Thai passage verbatim."
                )
                report.metadata["qa_disagreement_unresolved"] = True
            if failures:
                report.metadata["qa_adjudication_failures"] = failures
            return report
        except ProviderOutputError as exc:
            failures.append(f"{provider_spec.name}: {exc}")
            if index == len(routes) - 1:
                raise
    raise RuntimeError("QA route list was empty.")


def _has_verbatim_adjudication_evidence(feedback: str, *, source_text: str, refined_text: str) -> bool:
    """Require a disagreeing PASS to cite both sides of the alleged issue."""
    fragments = re.findall(r"(?:`([^`]{2,120})`|[\"“']([^\"”']{2,120})[\"”'])", feedback)
    quoted = [next((part.strip() for part in pair if part.strip()), "") for pair in fragments]
    source_hits = [fragment for fragment in quoted if fragment in source_text]
    refined_hits = [fragment for fragment in quoted if fragment in refined_text]
    return bool(source_hits and refined_hits)


def _run_refinement_with_configured_fallbacks(
    *,
    config: Any,
    block: TextBlock,
    literal_draft: LiteralDraft,
    glossary_subset: list[Any],
    style_profile_key: str,
) -> Any:
    """Run refinement through the configured primary and fallback routes."""
    routing = config.stage_routing_for("refinement")
    routes = [(config.provider_for_stage("refinement"), routing.model)]
    routes.extend(config.fallback_routes_for_stage("refinement"))
    failures: list[str] = []
    for index, (provider_spec, model) in enumerate(routes):
        try:
            draft = run_refine_stage(
                config=config,
                block=block,
                literal_draft=literal_draft,
                glossary_subset=glossary_subset,
                style_profile_key=style_profile_key,
                provider_runner=ProviderRunner(provider_spec),
                model=model,
                retry_feedback=(
                    f"Previous refinement route failed: {failures[-1]}. Preserve every source passage."
                    if failures
                    else ""
                ),
                prompt_store=PromptStore(ROOT / "prompts" / "lean"),
                style_instructions=(config.workspace.system / "lean_voice.md").read_text(encoding="utf-8"),
            )
            if "[...]" in draft.refined_text or "[…]" in draft.refined_text:
                raise ChapterQualityError("Refinement returned an omission placeholder.")
            draft.metadata["refinement_route_index"] = index
            draft.metadata["refinement_fallback_used"] = index > 0
            if failures:
                draft.metadata["refinement_primary_failures"] = failures
            return draft
        except Exception as exc:
            failures.append(f"{provider_spec.name}: {exc}")
            if index == len(routes) - 1:
                raise
    raise RuntimeError("Refinement route list was empty.")


def _source_term_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term)
    if re.search(r"[A-Za-z]", term):
        return re.compile(rf"(?<![A-Za-z]){escaped}(?![A-Za-z])")
    return re.compile(escaped)


def _run_literal_with_configured_fallbacks(config: Any, block: TextBlock) -> LiteralDraft:
    routing = config.stage_routing_for("literal_translation")
    routes = [(config.provider_for_stage("literal_translation"), routing.model)]
    routes.extend(config.fallback_routes_for_stage("literal_translation"))
    failures: list[str] = []
    for index, (spec, model) in enumerate(routes):
        try:
            draft = run_literal_translation_stage(
                config=config, block=block, glossary_subset=[],
                provider_runner=ProviderRunner(spec), model=model,
                prompt_store=PromptStore(ROOT / "prompts" / "lean"),
            )
            draft.metadata["literal_route_index"] = index
            draft.metadata["literal_primary_failures"] = failures
            return draft
        except (ProviderExecutionError, RuntimeError) as exc:
            failures.append(f"{spec.name}: {exc}")
            if index == len(routes) - 1:
                raise
    raise RuntimeError("Literal translation route list was empty.")


def project_glossary_terms(
    source_text: str,
    entries: list[GlossaryEntry],
) -> tuple[str, list[dict[str, str]]]:
    """Project approved glossary terms into a source copy for the literal call."""
    projected = source_text
    replacements: list[dict[str, str]] = []
    terms: list[tuple[int, str, str]] = []
    for entry in entries:
        if entry.status.strip().lower() != "approved" or not entry.thai_term:
            continue
        for source_term in {entry.original_term, *entry.aliases}:
            source_term = source_term.strip()
            if source_term:
                terms.append((len(source_term), source_term, entry.thai_term))

    for _length, source_term, thai_term in sorted(set(terms), reverse=True):
        projected, count = _source_term_pattern(source_term).subn(thai_term, projected)
        if count:
            replacements.append(
                {
                    "source_term": source_term,
                    "thai_term": thai_term,
                    "occurrences": str(count),
                }
            )
    return projected, replacements


def _harvest_candidates(
    *,
    config: Any,
    chapter_id: str,
    source_text: str,
    final_text: str,
    run_id: str,
    trace_dir: Path,
) -> list[dict[str, Any]]:
    routing = config.stage_routing_for("term_extraction")
    prompt_store = PromptStore(ROOT / "prompts" / "lean")
    prompt = prompt_store.render(
        "term_harvest",
        source_text=source_text,
        final_translation=final_text,
    )
    _context(run_id=run_id, chapter_id=chapter_id, stage="term_harvest")
    routes = [(config.provider_for_stage("term_extraction"), routing.model)]
    routes.extend(config.fallback_routes_for_stage("term_extraction"))
    for index, (spec, model) in enumerate(routes):
        try:
            runner = ProviderRunner(spec)
            response = runner.run_with_retry(
                ProviderRequest(
                    prompt=prompt, provider=spec.name, stage="term_harvest",
                    model=model, timeout_seconds=routing.timeout_seconds,
                ),
                max_attempts=routing.retry_max_attempts,
                retry_delay_seconds=routing.retry_initial_delay_seconds,
                retry_backoff_multiplier=routing.retry_backoff_multiplier,
                retry_failure_kinds=routing.retry_failure_kinds,
            )
            ensure_provider_response(response)
            text = response.stdout.strip()
            fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.I | re.S)
            if fenced:
                text = fenced.group(1).strip()
            payload = json.loads(text)
            if not isinstance(payload, list):
                raise ValueError("term_harvest must return a JSON array")
            break
        except (ProviderExecutionError, ValueError):
            if index == len(routes) - 1:
                raise
    candidates: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        original = str(item.get("original_term", "")).strip()
        thai = str(item.get("observed_thai", "")).strip()
        if not original or not thai or original not in source_text or thai not in final_text:
            continue
        candidates.append(
            {
                "original_term": original,
                "observed_thai": thai,
                "category": str(item.get("category", "term")).strip() or "term",
                "evidence": str(item.get("evidence", "")).strip(),
                "confidence": str(item.get("confidence", "unknown")).strip(),
                "status": "proposed",
                "chapter_id": chapter_id,
            }
        )
    return candidates


def _review_proposed_candidates(
    *,
    candidates: list[dict[str, Any]],
    source_text: str,
    final_text: str,
) -> dict[str, Any]:
    """Run a cheap evidence review before candidates enter the proposal queue."""
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    for candidate in candidates:
        original = str(candidate.get("original_term", "")).strip()
        thai = str(candidate.get("observed_thai", "")).strip()
        reason = ""
        if len(original) < 2 or "\n" in original or "\n" in thai:
            reason = "invalid_term_shape"
        elif original not in source_text:
            reason = "source_evidence_missing"
        elif thai not in final_text:
            reason = "final_thai_evidence_missing"
        elif original.lower() in {"chapter", "author", "note", "system", "level"}:
            reason = "generic_noise"
        elif original == thai or original in thai:
            reason = "unchanged_source_term"
        elif original in seen and seen[original] != thai:
            reason = "conflicting_candidate_mapping"
        if reason:
            rejected.append({**candidate, "review_status": "rejected", "review_reason": reason})
        else:
            accepted.append({**candidate, "review_status": "accepted_for_proposal"})
            seen[original] = thai
    return {
        "review": "deterministic_source_and_final_evidence",
        "accepted": accepted,
        "rejected": rejected,
        "promoted_to_glossary": 0,
    }


def _promote_reviewed_candidates(
    *,
    review: dict[str, Any],
    glossary: dict[str, GlossaryEntry],
) -> tuple[list[GlossaryEntry], list[dict[str, Any]]]:
    """Promote only high-confidence, non-conflicting terms into experiment memory."""
    promoted: list[GlossaryEntry] = []
    decisions: list[dict[str, Any]] = []
    candidates = review.get("accepted", [])
    grouped: dict[str, set[str]] = {}
    for candidate in candidates:
        grouped.setdefault(str(candidate.get("original_term", "")).strip(), set()).add(
            str(candidate.get("observed_thai", "")).strip()
        )
    for candidate in candidates:
        original = str(candidate.get("original_term", "")).strip()
        thai = str(candidate.get("observed_thai", "")).strip()
        reason = ""
        existing = glossary.get(original)
        if str(candidate.get("confidence", "")).strip().lower() != "high":
            reason = "confidence_not_high"
        elif len(grouped.get(original, set())) != 1:
            reason = "conflicting_candidate_mapping"
        elif existing and existing.thai_term != thai:
            reason = "conflicts_with_existing_glossary"
        elif existing:
            reason = "already_in_experiment_glossary"
        if reason:
            decisions.append({**candidate, "promotion_status": "not_promoted", "promotion_reason": reason})
            continue
        entry = GlossaryEntry(
            original_term=original,
            thai_term=thai,
            category=str(candidate.get("category", "term")) or "term",
            status="approved",
            source_language="en",
            notes="Experiment-only approval from source/final evidence review.",
            metadata={"experiment_only": True, "first_seen_chapter": candidate.get("chapter_id", "")},
        )
        glossary[original] = entry
        promoted.append(entry)
        decisions.append({**candidate, "promotion_status": "promoted_experiment_only"})
    return promoted, decisions


def _literal_from_dict(payload: dict[str, Any]) -> LiteralDraft:
    return LiteralDraft(
        block_id=str(payload.get("block_id", "")),
        chapter_id=str(payload.get("chapter_id", "")),
        sentence_pairs=tuple(LiteralSentencePair(**pair) for pair in payload.get("sentence_pairs", [])),
        source_text=str(payload.get("source_text", "")),
        provider=str(payload.get("provider", "")),
        metadata=dict(payload.get("metadata", {})),
    )


def _refined_from_dict(payload: dict[str, Any]) -> RefinedDraft:
    return RefinedDraft(
        block_id=str(payload.get("block_id", "")),
        chapter_id=str(payload.get("chapter_id", "")),
        refined_text=str(payload.get("refined_text", "")),
        provider=str(payload.get("provider", "")),
        style_profile=str(payload.get("style_profile", "")),
        source_text=str(payload.get("source_text", "")),
        metadata=dict(payload.get("metadata", {})),
    )


def _qa_from_dict(payload: dict[str, Any]) -> Any:
    from novel_pipeline.types import QAFinding, QAReport

    return QAReport(
        block_id=str(payload.get("block_id", "")),
        chapter_id=str(payload.get("chapter_id", "")),
        passed=bool(payload.get("passed", False)),
        findings=tuple(QAFinding(**finding) for finding in payload.get("findings", [])),
        feedback=str(payload.get("feedback", "")),
        retry_count=int(payload.get("retry_count", 0)),
        judge_provider=str(payload.get("judge_provider", "")),
        metadata=dict(payload.get("metadata", {})),
    )


def _trace_metrics(trace_dir: Path) -> dict[str, Any]:
    calls = 0
    failures = 0
    stage_counts: dict[str, int] = {}
    usage_totals: dict[str, float] = {}
    cost = 0.0
    cost_seen = False
    provider_seconds = 0.0
    for path in sorted(trace_dir.glob("*.json")):
        try:
            event = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if event.get("schema") != "novel.provider-trace.v1":
            continue
        calls += 1
        stage = str(event.get("stage", "unknown"))
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
        response = event.get("response", {})
        provider_seconds += float(response.get("duration_seconds") or 0)
        if response.get("failure_kind"):
            failures += 1
        usage = response.get("usage", {})
        if isinstance(usage, dict) and isinstance(usage.get("usage"), dict):
            usage = usage["usage"]
        if isinstance(usage, dict):
            for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
                value = usage.get(key)
                if isinstance(value, (int, float)):
                    usage_totals[key] = usage_totals.get(key, 0.0) + float(value)
            value = usage.get("cost")
            if isinstance(value, (int, float)):
                cost += float(value)
                cost_seen = True
    return {
        "provider_calls": calls,
        "provider_failures": failures,
        "provider_seconds": round(provider_seconds, 3),
        "calls_by_stage": stage_counts,
        "usage_totals": usage_totals,
        "cost": cost if cost_seen else None,
        "cost_status": "measured" if cost_seen else "provider_did_not_report_cost",
    }


def _run_production_sentinel(config: Any, *, run_id: str, chapters: str, staged_output_root: Path) -> dict[str, Any]:
    """Run the shared Sentinel against only this novel and chapter range."""
    workspace_root = config.workspace.root.parent.resolve()
    sentinel_path = workspace_root / "scripts" / "sentinel_quality_report.py"
    if not sentinel_path.exists():
        raise RuntimeError(f"Shared Sentinel is missing: {sentinel_path}")
    env_keys = (
        "NOVEL_SENTINEL_WORKSPACE_ROOT",
        "NOVEL_SENTINEL_REGISTRY_PATH",
        "NOVEL_SENTINEL_REPORT_ROOT",
        "NOVEL_SENTINEL_NOVEL",
        "NOVEL_SENTINEL_OUTPUT_ROOT",
        "NOVEL_SENTINEL_STAGE_ONLY",
        "NOVEL_SENTINEL_SKIP_EXISTING_GUARDRAILS",
    )
    previous_env = {key: os.environ.get(key) for key in env_keys}
    os.environ["NOVEL_SENTINEL_WORKSPACE_ROOT"] = str(workspace_root)
    os.environ["NOVEL_SENTINEL_REGISTRY_PATH"] = str(workspace_root / "00_Config" / "novel_registry.json")
    os.environ["NOVEL_SENTINEL_REPORT_ROOT"] = str(workspace_root / "07_Reports")
    os.environ["NOVEL_SENTINEL_NOVEL"] = config.novel_id
    os.environ["NOVEL_SENTINEL_OUTPUT_ROOT"] = str(staged_output_root)
    os.environ["NOVEL_SENTINEL_STAGE_ONLY"] = "1"
    os.environ.pop("NOVEL_SENTINEL_SKIP_EXISTING_GUARDRAILS", None)
    spec = importlib.util.spec_from_file_location("novel_shared_sentinel", sentinel_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load shared Sentinel: {sentinel_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        result = module.generate_sentinel_report(
            scope=f"lean-{run_id}-{chapters}",
            novel=config.novel_id,
            chapters=chapters,
            fail_on="major",
            skip_advisory_english=True,
        )
    finally:
        for key, value in previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        sys.modules.pop(spec.name, None)
    return {
        "counts": result["counts"],
        "failed": bool(result["failed"]),
        "json_path": str(result["json_path"]),
        "md_path": str(result["md_path"]),
    }


def run_chapter(
    config: Any,
    chapter_id: str,
    run_id: str,
    output_dir: Path,
    trace_dir: Path,
    *,
    resume: bool = False,
    glossary: dict[str, Any] | None = None,
    checkpoint_root: Path | None = None,
) -> dict[str, Any]:
    source, blocks = _load_chapter_source_and_blocks(config, chapter_id)
    output_title = _resolve_chapter_output_title(config, chapter_id, source)
    glossary = glossary if glossary is not None else load_glossary_index(config.workspace.glossary_dir)
    source_hash = _digest({"chapter_id": chapter_id, "title": source.title, "source": source.raw_text})
    glossary_hash = _glossary_digest(glossary)
    prompt_hash = _pipeline_prompt_digest(config)
    state_dir = (checkpoint_root or output_dir) / chapter_id
    state_dir.mkdir(parents=True, exist_ok=True)
    literal_checkpoint = state_dir / "literal_checkpoint.json"
    refined_checkpoint = state_dir / "refined_checkpoint.json"
    qa_checkpoint = state_dir / "qa_checkpoint.json"
    formatted_checkpoint = state_dir / "formatted_checkpoint.json"
    harvest_checkpoint = state_dir / "glossary_review.json"
    literal_pairs: list[LiteralSentencePair] = []
    block_records: list[dict[str, Any]] = []
    projection_records: list[dict[str, Any]] = []
    reused_stages: list[str] = []
    literal_input_hash = _checkpoint_input_hash(
        stage="literal_translation",
        source_hash=source_hash,
        glossary_hash=glossary_hash,
        prompt_hash=prompt_hash,
    )
    literal_checkpoint_data = _read_matching_checkpoint(literal_checkpoint, literal_input_hash) if resume else None
    if literal_checkpoint_data is not None:
        checkpoint = literal_checkpoint_data
        literal_draft = _literal_from_dict(checkpoint["draft"])
        literal_pairs.extend(literal_draft.sentence_pairs)
        block_records = checkpoint.get("block_records", [])
        projection_records = checkpoint.get("projection_records", [])
        reused_stages.append("literal_translation")
    else:
        for block in blocks:
            glossary_subset = _chapter_glossary_subset(block, glossary)
            projected_source, replacements = project_glossary_terms(block.source_text, glossary_subset)
            projected_block = TextBlock(
                block_id=block.block_id,
                chapter_id=block.chapter_id,
                block_index=block.block_index,
                source_text=projected_source,
                source_language=block.source_language,
                start_offset=block.start_offset,
                end_offset=block.end_offset,
                metadata=dict(block.metadata),
            )
            _context(run_id=run_id, chapter_id=chapter_id, stage="literal_translation", block_id=block.block_id)
            draft = _run_literal_with_configured_fallbacks(config, projected_block)
            literal_pairs.extend(draft.sentence_pairs)
            block_records.append(
                {
                    "block_id": block.block_id,
                    "source_chars": len(block.source_text),
                    "projected_source_chars": len(projected_source),
                    "literal_chars": sum(len(pair.literal_sentence) for pair in draft.sentence_pairs),
                }
            )
            projection_records.append(
                {
                    "block_id": block.block_id,
                    "replacement_count": len(replacements),
                    "replacements": replacements,
                }
            )
        literal_draft = LiteralDraft(
            block_id=f"{chapter_id}-assembled",
            chapter_id=chapter_id,
            sentence_pairs=tuple(literal_pairs),
            source_text=source.raw_text,
            provider="assembled_from_blocks",
        )
        atomic_write_json(
            literal_checkpoint,
            {
                "stage": "literal_translation",
                "input_hash": literal_input_hash,
                "draft": literal_draft.to_dict(),
                "block_records": block_records,
                "projection_records": projection_records,
            },
        )

    literal_text = "\n\n".join(pair.literal_sentence.strip() for pair in literal_pairs if pair.literal_sentence.strip()).strip()
    chapter_block = TextBlock(
        block_id=f"{chapter_id}-assembled",
        chapter_id=chapter_id,
        block_index=1,
        source_text=source.raw_text,
        source_language=source.source_language,
    )
    assembled_literal = literal_draft
    literal_hash = _digest(literal_draft.to_dict())
    refinement_input_hash = _checkpoint_input_hash(
        stage="refinement",
        source_hash=source_hash,
        glossary_hash=glossary_hash,
        prompt_hash=prompt_hash,
        dependencies={"literal_hash": literal_hash},
    )
    refined_checkpoint_data = _read_matching_checkpoint(refined_checkpoint, refinement_input_hash) if resume else None
    if refined_checkpoint_data is not None:
        refined = _refined_from_dict(refined_checkpoint_data["draft"])
        reused_stages.append("refinement")
    else:
        _context(run_id=run_id, chapter_id=chapter_id, stage="refinement", block_id=chapter_block.block_id)
        refined = _run_refinement_with_configured_fallbacks(
            config=config,
            block=chapter_block,
            literal_draft=assembled_literal,
            glossary_subset=_chapter_glossary_subset(chapter_block, glossary),
            style_profile_key=config.default_style_profile,
        )
        atomic_write_json(
            refined_checkpoint,
            {"stage": "refinement", "input_hash": refinement_input_hash, "draft": refined.to_dict()},
        )
    repaired_refined = _repair_refined_source_annotations(refined, novel_id=config.novel_id)
    if repaired_refined is not refined:
        refined = repaired_refined
        atomic_write_json(
            refined_checkpoint,
            {"stage": "refinement", "input_hash": refinement_input_hash, "draft": refined.to_dict()},
        )
    qa = None
    refined_hash = _digest(refined.to_dict())
    qa_input_hash = _checkpoint_input_hash(
        stage="qa_judge",
        source_hash=source_hash,
        glossary_hash=glossary_hash,
        prompt_hash=prompt_hash,
        dependencies={"literal_hash": literal_hash, "refined_hash": refined_hash},
    )
    qa_checkpoint_data = _read_matching_checkpoint(qa_checkpoint, qa_input_hash) if resume else None
    if qa_checkpoint_data is not None:
        cached_qa = _qa_from_dict(qa_checkpoint_data["report"])
        # A failed QA checkpoint is evidence of where the run stopped, not a
        # successful stage. Reuse the refined artifact but adjudicate QA again.
        if cached_qa.passed:
            qa = cached_qa
            reused_stages.append("qa_judge")
    if qa is None:
        _context(run_id=run_id, chapter_id=chapter_id, stage="qa_judge", block_id=chapter_block.block_id)
        qa = _run_qa_with_configured_fallbacks(
            config=config,
            block=chapter_block,
            literal_draft=assembled_literal,
            refined_draft=refined,
            glossary_subset=_chapter_glossary_subset(chapter_block, glossary),
            style_profile_key=config.default_style_profile,
        )
        atomic_write_json(qa_checkpoint, {"stage": "qa_judge", "input_hash": qa_input_hash, "report": qa.to_dict()})
    if not qa.passed:
        raise ChapterQualityError(f"Lean QA failed for {chapter_id}: {qa.feedback}")
    formatting_input_hash = _checkpoint_input_hash(
        stage="formatting",
        source_hash=source_hash,
        glossary_hash=glossary_hash,
        prompt_hash=prompt_hash,
        dependencies={"refined_hash": refined_hash},
    )
    formatted_checkpoint_data = _read_matching_checkpoint(formatted_checkpoint, formatting_input_hash) if resume else None
    if formatted_checkpoint_data is not None:
        formatted_data = formatted_checkpoint_data
        formatted = str(formatted_data["formatted"])
        formatter_provider = str(formatted_data["formatter_provider"])
        formatter_meta = dict(formatted_data.get("formatter_metadata", {}))
        reused_stages.append("formatting")
    else:
        _context(run_id=run_id, chapter_id=chapter_id, stage="formatting", block_id=chapter_block.block_id)
        # Formatting does not infer speakers or rewrite story content.
        formatted = re.sub(r"\n{3,}", "\n\n", refined.refined_text.replace("\r\n", "\n")).strip()
        formatter_provider = "local"
        formatter_meta = {"policy": "preserve_content_and_markdown_normalize_spacing"}
        atomic_write_json(
            formatted_checkpoint,
            {
                "stage": "formatting",
                "input_hash": formatting_input_hash,
                "formatted": formatted,
                "formatter_provider": formatter_provider,
                "formatter_metadata": formatter_meta,
            },
        )
    validation_issues = validate_formatted_text(formatted, source_text=refined.refined_text)
    if validation_issues:
        raise ChapterQualityError(
            f"Lean formatting validation failed for {chapter_id}: "
            + "; ".join(validation_issues)
        )
    chapter_output = f"# {output_title}\n\n{formatted.strip()}\n"
    output_chapter_dir = output_dir / chapter_id
    output_chapter_dir.mkdir(parents=True, exist_ok=True)
    (output_chapter_dir / f"{chapter_id}.md").write_text(chapter_output, encoding="utf-8")
    harvest_input_hash = _checkpoint_input_hash(
        stage="term_harvest",
        source_hash=source_hash,
        glossary_hash=glossary_hash,
        prompt_hash=prompt_hash,
        dependencies={"formatted_hash": _digest(formatted)},
    )
    harvest_checkpoint_data = _read_matching_checkpoint(harvest_checkpoint, harvest_input_hash) if resume else None
    if harvest_checkpoint_data is not None:
        review = harvest_checkpoint_data
        reused_stages.append("term_harvest")
    else:
        proposed = _harvest_candidates(
            config=config,
            chapter_id=chapter_id,
            source_text=source.raw_text,
            final_text=formatted,
            run_id=run_id,
            trace_dir=trace_dir,
        )
        review = _review_proposed_candidates(candidates=proposed, source_text=source.raw_text, final_text=formatted)
        review["input_hash"] = harvest_input_hash
        atomic_write_json(harvest_checkpoint, review)
    proposed = review.get("accepted", [])
    atomic_write_json(state_dir / "glossary_proposed.json", proposed)
    return {
        "chapter_id": chapter_id,
        "source_chars": len(source.raw_text),
        "block_count": len(blocks),
        "block_records": block_records,
        "glossary_projection": projection_records,
        "literal_chars": len(literal_text),
        "refined_chars": len(refined.refined_text),
        "formatted_chars": len(formatted),
        "qa_passed": qa.passed,
        "qa_feedback": qa.feedback,
        "qa_metadata": qa.metadata,
        "refinement_metadata": refined.metadata,
        "formatter_provider": formatter_provider,
        "formatter_metadata": formatter_meta,
        "glossary_proposed_count": len(proposed),
        "glossary_review_rejected_count": len(review.get("rejected", [])),
        "glossary_candidates": review.get("accepted", []),
        "reused_stages": reused_stages,
        "resumed_from_checkpoints": bool(reused_stages),
        "staged_output": str(output_chapter_dir / f"{chapter_id}.md"),
    }


def _promote_staged_outputs(config: Any, results: list[dict[str, Any]], *, promoted: list[str] | None = None) -> list[str]:
    """Copy only Sentinel-approved staged Markdown into the selected novel."""
    promoted = promoted if promoted is not None else []
    for result in results:
        if not Path(str(result["staged_output"])).is_file():
            raise RuntimeError(f"Missing staged output for {result['chapter_id']}")
    for result in results:
        staged = Path(str(result["staged_output"])).resolve()
        if not staged.is_file():
            raise RuntimeError(f"Missing staged output for {result['chapter_id']}: {staged}")
        chapter_id = str(result["chapter_id"])
        destination = (config.workspace.output / chapter_id / f"{chapter_id}.md").resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(f".{destination.name}.lean-promotion.tmp")
        try:
            shutil.copyfile(staged, temporary)
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
        promoted.append(str(destination))
    return promoted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--chapters", required=True, help="Comma-separated IDs, e.g. ch001,ch004")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--trace-dir", type=Path, default=None)
    parser.add_argument("--checkpoint-dir", type=Path, default=None)
    parser.add_argument("--mode", choices=("production", "experiment"), default="production")
    parser.add_argument("--dry-run", action="store_true", help="Validate novel context and raw source without provider calls.")
    parser.add_argument("--resume", action="store_true", help="Reuse completed per-stage checkpoints in each chapter output directory.")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", args.run_id):
        parser.error("--run-id must be a single safe directory name")
    chapters = _parse_chapters(args.chapters)
    config = load_app_config(args.config)
    if args.dry_run:
        for chapter_id in chapters:
            source, blocks = _load_chapter_source_and_blocks(config, chapter_id)
            print(f"[DRY-RUN] {config.novel_id} {chapter_id}: {len(source.raw_text)} source chars, {len(blocks)} blocks")
        print(f"[DRY-RUN] workspace: {config.workspace.root}")
        print("[DRY-RUN] provider helpers resolved from the selected novel or shared workspace scripts")
        return 0
    if args.mode == "production":
        if args.output_dir is not None:
            parser.error("production output is selected by the novel config, not --output-dir")
        checkpoint_dir = (args.checkpoint_dir or config.workspace.work / "_lean_runs" / args.run_id).resolve()
        output_dir = checkpoint_dir / "_staged_output"
        trace_dir = (args.trace_dir or checkpoint_dir / "trace").resolve()
        run_root = (config.workspace.work / "_lean_runs").resolve()
        for path in (checkpoint_dir, trace_dir):
            if not path.is_relative_to(run_root) or path == run_root:
                parser.error("production checkpoint/trace paths must stay under the selected novel's 04_Work/_lean_runs")
    else:
        if args.output_dir is None or args.trace_dir is None:
            parser.error("experiment mode requires --output-dir and --trace-dir")
        output_dir = args.output_dir.resolve()
        checkpoint_dir = (args.checkpoint_dir or output_dir).resolve()
        trace_dir = args.trace_dir.resolve()
        work_root = config.workspace.work.resolve()
        for path in (output_dir, checkpoint_dir, trace_dir):
            if not path.is_relative_to(work_root) or path == work_root:
                parser.error("experiment paths must stay under the selected novel's 04_Work, outside product output")
    output_dir.mkdir(parents=True, exist_ok=True)
    trace_dir.mkdir(parents=True, exist_ok=True)
    os.environ["NOVEL_PIPELINE_TRACE_DIR"] = str(trace_dir)
    prior_report_path = checkpoint_dir / "lean_run_report.json"
    if args.mode == "experiment":
        prior_report_path = output_dir / "lean_experiment_report.json"
    prior_report: dict[str, Any] = {}
    if args.resume and prior_report_path.exists():
        try:
            prior_report = json.loads(prior_report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prior_report = {}
    if prior_report and (
        prior_report.get("novel_id") != config.novel_id
        or prior_report.get("run_id") != args.run_id
        or _parse_chapters(str(prior_report.get("chapters_requested", ""))) != chapters
    ):
        parser.error("resume must keep the original novel, run ID and chapter scope")
    started_at = str(prior_report.get("started_at", "")) or _utc_now()
    glossary = load_glossary_index(config.workspace.glossary_dir)
    results: list[dict[str, Any]] = []
    promoted_terms: list[GlossaryEntry] = []
    status = "complete"
    error = ""
    for chapter_id in chapters:
        print(f"[{args.run_id}] START {chapter_id}", flush=True)
        try:
            result = run_chapter(
                config,
                chapter_id,
                args.run_id,
                output_dir,
                trace_dir,
                resume=args.resume,
                glossary=glossary,
                checkpoint_root=checkpoint_dir,
            )
            if args.mode == "experiment":
                promoted, promotion_decisions = _promote_reviewed_candidates(
                    review={"accepted": result.pop("glossary_candidates", [])},
                    glossary=glossary,
                )
                promoted_terms.extend(promoted)
                result["glossary_promoted_experiment_only"] = [entry.original_term for entry in promoted]
                result["glossary_promotion_decisions"] = promotion_decisions
            result["status"] = "staged"
            results.append(result)
            atomic_write_json(checkpoint_dir / chapter_id / "chapter_result.json", result)
            if args.mode == "experiment":
                atomic_write_json(
                    output_dir / "experiment_glossary_approved.json",
                    [entry.to_dict() for entry in glossary.values() if entry.metadata.get("experiment_only")],
                )
            print(f"[{args.run_id}] COMPLETE {chapter_id}", flush=True)
        except ChapterQualityError as exc:
            if args.mode != "production":
                status = "blocked"
                error = f"{type(exc).__name__}: {exc}"
                break
            # A chapter-local defect is quarantined so later chapters can keep
            # moving. The quarantined chapter remains unpublished and resumable.
            result = {
                "chapter_id": chapter_id,
                "status": "quarantined",
                "error": f"{type(exc).__name__}: {exc}",
                "staged_output": "",
            }
            results.append(result)
            atomic_write_json(checkpoint_dir / chapter_id / "chapter_result.json", result)
            print(f"[{args.run_id}] QUARANTINED {chapter_id}: {result['error']}", flush=True)
        except Exception as exc:
            status = "blocked"
            error = f"{type(exc).__name__}: {exc}"
            break
    sentinel = None
    sentinel_runs: list[dict[str, Any]] = []
    promoted_outputs: list[str] = []
    if args.mode == "production":
        for result in results:
            if result.get("status") != "staged":
                continue
            chapter_id = str(result["chapter_id"])
            try:
                chapter_sentinel = _run_production_sentinel(
                    config,
                    run_id=args.run_id,
                    chapters=chapter_id,
                    staged_output_root=output_dir,
                )
                sentinel_runs.append({"chapter_id": chapter_id, **chapter_sentinel})
                result["sentinel"] = chapter_sentinel
                if chapter_sentinel["failed"]:
                    result["status"] = "quarantined"
                    result["error"] = "Production Sentinel reported blocker/major findings."
                    atomic_write_json(checkpoint_dir / chapter_id / "chapter_result.json", result)
                    continue
                _promote_staged_outputs(config, [result], promoted=promoted_outputs)
                result["status"] = "promoted"
                atomic_write_json(checkpoint_dir / chapter_id / "chapter_result.json", result)
            except Exception as exc:
                status = "blocked"
                error = f"ProductionGateError: {exc}"
                break
        sentinel = {
            "failed": any(item.get("failed") for item in sentinel_runs),
            "runs": sentinel_runs,
        }
    quarantined = [result for result in results if result.get("status") == "quarantined"]
    if quarantined and status != "blocked":
        status = "partial"
        error = f"{len(quarantined)} chapter(s) quarantined for recovery."
    report = {
        "schema": "novel.lean-run.v1",
        "mode": args.mode,
        "run_id": args.run_id,
        "novel_id": config.novel_id,
        "chapters_requested": args.chapters,
        "started_at": started_at,
        "finished_at": _utc_now(),
        "status": status,
        "chapters": results,
        "metrics": _trace_metrics(trace_dir),
        "trace_dir": str(trace_dir),
        "output_dir": str(config.workspace.output if args.mode == "production" else output_dir),
        "staged_output_dir": str(output_dir) if args.mode == "production" else "",
        "promoted_outputs": promoted_outputs,
        "quarantined_chapters": [
            {"chapter_id": result["chapter_id"], "error": result.get("error", "")}
            for result in quarantined
        ],
        "checkpoint_dir": str(checkpoint_dir),
        "glossary_policy": "production-approved terms are projected into source copies; harvested terms remain proposed until separately reviewed",
        "experiment_glossary_promoted_count": len(promoted_terms),
        "experiment_glossary_promoted_terms": [entry.original_term for entry in promoted_terms],
        "checkpoint_policy": "reuse requires matching source, glossary, prompt, and upstream artifact hashes",
        "error": error,
        "sentinel": sentinel,
    }
    atomic_write_json(checkpoint_dir / "lean_run_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # Workers inspect partial reports for recovery rather than treating a
    # nonzero quality result as an instruction to stop their entire work order.
    return 0 if status in {"complete", "partial"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
