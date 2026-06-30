from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from novel_pipeline.artifacts import (
    batch_glossary_scan_artifact_path,
    block_artifact_path,
    chapter_dir,
    glossary_scan_artifact_path,
)
from novel_pipeline.config import load_app_config
from novel_pipeline.files import atomic_write_json, atomic_write_text, read_text_if_exists
from novel_pipeline.glossary_support import (
    choose_option_interactively,
    load_glossary_index,
    write_glossary_note,
)
from novel_pipeline.ledger import ResumeState, RunLedger
from novel_pipeline.prompts import PromptStore
from novel_pipeline.providers.base import ProviderExecutionError, ProviderOutputError, ProviderRunner, ensure_provider_response
from novel_pipeline.stages.fetch import run_fetch_stage
from novel_pipeline.stages.format import cleanup_provider_formatted_text, format_block_text, _split_long_paragraphs
from novel_pipeline.stages.glossary import (
    build_glossary_scan_queue,
    build_term_suggestion,
    infer_category,
)
from novel_pipeline.stages.helpers import format_glossary_subset
from novel_pipeline.stages.qa import run_qa_stage, run_rule_checks
from novel_pipeline.stages.refine import run_refine_stage
from novel_pipeline.stages.translate import run_literal_translation_stage
from novel_pipeline.text_utils import split_blocks, split_sentences
from novel_pipeline.types import (
    AppConfig,
    ChapterSource,
    GlossaryEntry,
    LiteralDraft,
    LiteralSentencePair,
    ProviderRequest,
    QAFinding,
    QAReport,
    RefinedDraft,
    RunRecord,
    TermSuggestion,
    TextBlock,
    utc_now_iso,
)

STAGE_ORDER = [
    "fetched",
    "glossary_scanned",
    "glossary_approved",
    "translating",
    "refining",
    "qa",
    "formatting",
    "completed",
    "sentinel",
]

BLOCK_STAGE_ORDER = [
    "translating",
    "refining",
    "qa",
    "formatting",
    "completed",
]

QA_MAX_RETRIES = 2

HGD_TITLE_MAP = {
    "Velora Art Museum": "พิพิธภัณฑ์ศิลปะเวโลรา",
    "Live Stream": "ไลฟ์สตรีม",
    "The lunatic with the sunglasses": "คนบ้าแว่นกันแดด",
    "The game that makes you scream": "เกมที่ทำให้กรีดร้อง",
    "Scream": "เสียงกรีดร้อง",
    "Quest Completed": "เควสต์สำเร็จ",
    "Your account has been reinstated": "บัญชีของคุณถูกคืนสถานะแล้ว",
    "Exit": "ทางออก",
    "Orientation Day": "วันปฐมนิเทศ",
    "Return of the Jester": "การกลับมาของตัวตลก",
    "Masquerade ball": "งานเต้นรำสวมหน้ากาก",
    "The perfect piece": "ชิ้นงานสมบูรณ์แบบ",
    "The missing piece": "ชิ้นส่วนที่หายไป",
    "The world has changed": "โลกเปลี่ยนไปแล้ว",
    "Crying": "เสียงร้องไห้",
    "Little girl": "เด็กหญิงตัวน้อย",
    "Little Girl": "เด็กหญิงตัวน้อย",
    "App Update": "อัปเดตแอป",
    "Shepherd": "ผู้เลี้ยงแกะ",
    "Evolution": "วิวัฒนาการ",
    "Second Order": "ลำดับที่สอง",
    "The Conductor’s Trial": "บททดสอบของวาทยกร",
    "The Conductor's Trial": "บททดสอบของวาทยกร",
    "Guild Dinner": "มื้อค่ำของกิลด์",
    "First Trauma Patient": "ผู้ป่วยบาดแผลทางใจคนแรก",
    "Expedition": "การสำรวจ",
    "A Twisted Man": "ชายบิดเบี้ยว",
    "Expedition Squad": "หน่วยสำรวจ",
    "Silence": "ความเงียบ",
    "Butcher": "คนเชือด",
    "A Twisted Game": "เกมบิดเบี้ยว",
    "Escape": "หลบหนี",
    "Aftermath": "ผลพวง",
    "Game Developer Mode": "โหมดนักพัฒนาเกม",
    "New Project": "โปรเจกต์ใหม่",
    "Exchange": "การแลกเปลี่ยน",
    "Harmia Island": "เกาะฮาร์เมีย",
    "Photograph": "ภาพถ่าย",
    "Elderglen Junction": "ชุมทางเอลเดอร์เกลน",
    "The other side": "อีกฟากหนึ่ง",
    "Horrifying realization": "การตระหนักอันน่าสยดสยอง",
    "Horrifying Realization": "การตระหนักอันน่าสยดสยอง",
    "Return": "การกลับมา",
    "Testing new game": "ทดสอบเกมใหม่",
    "Launch of new game": "เปิดตัวเกมใหม่",
    "Multiplayer": "ระบบผู้เล่นหลายคน",
    "Multiplayer?": "เล่นหลายคน?",
    "Squad Leader": "หัวหน้ากลุ่ม",
    "Chaos": "ความโกลาหล",
    "Update": "อัปเดต",
    "Press Conference": "งานแถลงข่าว",
    "Phone": "โทรศัพท์",
    "First day as Squad Leader": "วันแรกในฐานะหัวหน้ากลุ่ม",
    "Board": "กระดาน",
    "Dinner with the Team Leader": "มื้อค่ำกับหัวหน้ากลุ่ม",
    "Setting the stage": "จัดฉาก",
    "VILE - 2013": "VILE - 2013",
    "VILE - 2013 [The Jester]": "VILE - 2013 [ตัวตลก]",
    "Bet": "เดิมพัน",
    "New Mission": "ภารกิจใหม่",
    "Happy Kids Orphanage": "สถานเลี้ยงเด็กกำพร้าแฮปปี้คิดส์",
    "The boy and the crayons": "เด็กชายกับสีเทียน",
    "Mr. Jingles": "มิสเตอร์จิงเกิลส์",
    "Mr Jingles": "มิสเตอร์จิงเกิลส์",
    "The basement": "ห้องใต้ดิน",
    "Puzzle": "ปริศนา",
    "The Origin": "จุดกำเนิด",
    "Not as it seems": "ไม่ใช่อย่างที่เห็น",
    "Inside a cartoon": "ในโลกการ์ตูน",
    "Rat": "หนู",
    "For the future": "เพื่ออนาคต",
    "Gathering Funds": "ระดมทุน",
    "Haunting": "การหลอกหลอน",
    "Freelancers": "ฟรีแลนซ์",
    "Virtual Reality": "ความเป็นจริงเสมือน",
    "Hourglass": "นาฬิกาทราย",
    "Loop": "ลูป",
    "Till my fingers fall off": "จนกว่านิ้วของผมจะหลุด",
    "Despair in perfection": "ความสิ้นหวังในความสมบูรณ์แบบ",
}

HGD_TITLE_RE = re.compile(r"^(?:Chapter|ตอนที่)\s+\d+\s+-\s+(.+?)(\s+\[\d+\])?\s*$")


class ManualActionRequired(RuntimeError):
    """Raised when execution must stop for operator action."""

BLOCK_STAGE_ALIASES = {
    "literal": "translating",
    "translate": "translating",
    "translation": "translating",
    "translating": "translating",
    "refine": "refining",
    "refinement": "refining",
    "refining": "refining",
    "qa": "qa",
    "format": "formatting",
    "formatting": "formatting",
}


@dataclass(slots=True)
class PipelineContext:
    config: AppConfig
    ledger: RunLedger
    prompt_store: PromptStore
    run_id: str
    blocks: list[TextBlock] = field(default_factory=list)
    glossary_index: dict[str, GlossaryEntry] = field(default_factory=dict)
    chapter_source: ChapterSource | None = None
    force: bool = False


@dataclass(slots=True)
class _FormattingResult:
    text: str
    provider: str
    metadata: dict[str, Any]
    output_hash: str


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _apply_glossary_rejected_variant_repairs(text: str, glossary_subset: list[GlossaryEntry]) -> tuple[str, list[dict[str, str]]]:
    repairs: list[dict[str, str]] = []
    updated = text
    for entry in glossary_subset:
        if entry.status != "approved" or not entry.thai_term:
            continue
        for variant in entry.rejected_variants:
            if not variant or variant == entry.thai_term or variant not in updated:
                continue
            updated = updated.replace(variant, entry.thai_term)
            repairs.append(
                {
                    "original_term": entry.original_term,
                    "variant": variant,
                    "thai_term": entry.thai_term,
                }
            )
    return updated, repairs


def _apply_glossary_parenthetical_leakage_repairs(text: str, glossary_subset: list[GlossaryEntry]) -> tuple[str, list[dict[str, str]]]:
    repairs: list[dict[str, str]] = []
    updated = text
    for entry in glossary_subset:
        if entry.status != "approved" or not entry.thai_term:
            continue
        source_terms = [entry.original_term, *entry.aliases]
        for source_term in source_terms:
            if not source_term or source_term == entry.thai_term:
                continue
            pattern = re.compile(
                rf"(?P<thai>{re.escape(entry.thai_term)})\s*[\(（]\s*{re.escape(source_term)}\s*[\)）]"
            )
            updated, count = pattern.subn(r"\g<thai>", updated)
            if count:
                repairs.append(
                    {
                        "original_term": entry.original_term,
                        "leaked_term": source_term,
                        "thai_term": entry.thai_term,
                        "count": str(count),
                    }
                )
    return updated, repairs


def _apply_source_footnote_marker_repairs(text: str, source_text: str) -> tuple[str, list[dict[str, str]]]:
    match = re.search(r"(?:^|\s)Footnotes:\s*\n(?P<markers>(?:\s*\[\d+\]\s*\n?)+)\s*$", source_text, re.I)
    if not match:
        return text, []
    if re.search(r"(?:^|\n)(?:Footnotes|เชิงอรรถ)\s*:", text, re.I):
        return text, []
    markers = re.findall(r"\[\d+\]", match.group("markers"))
    if not markers:
        return text, []
    footnote_text = "เชิงอรรถ:\n" + "\n".join(markers)
    return text.rstrip() + "\n\n" + footnote_text, [{"markers": ",".join(markers)}]


_FORMATTING_PROVIDER_META_MARKERS = (
    "quota",
    "rate limit",
    "429",
    "capacity",
    "provider",
    "traceback",
    "exception",
    "stderr",
    "stdout",
    "gemini",
    "claude",
    "qwen",
)
_FORMATTING_HAN_RE = re.compile(r"[\u4e00-\u9fff]")
_CHAPTER_ID_RE = re.compile(r"^ch(\d+)$")


def _format_content_signature(text: str) -> str:
    normalized = text.lower()
    normalized = re.sub(r"[\s\"'“”‘’\[\]\(\)（）*_`~.,!?;:，。！？；：…\-]+", "", normalized)
    return normalized


def validate_formatted_text(text: str, source_text: str | None = None) -> list[str]:
    issues: list[str] = []
    lowered = text.lower()
    for marker in _FORMATTING_PROVIDER_META_MARKERS:
        if marker in lowered:
            issues.append(f"provider/meta marker: {marker}")
    if _FORMATTING_HAN_RE.search(text):
        issues.append("Han Chinese characters present")
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.strip() in {'"', "“", "”"}:
            issues.append(f"quote-only line {line_number}")
    if source_text is not None:
        source_signature = _format_content_signature(source_text)
        output_signature = _format_content_signature(text)
        if source_signature and output_signature != source_signature:
            issues.append("formatted text content changed")
    return issues


def _pre_qa_guardrail_issues(text: str) -> tuple[list[str], list[str]]:
    hard: list[str] = []
    warnings: list[str] = []
    stripped = text.strip()
    if not stripped:
        return ["empty_refined_text"], warnings
    if len(stripped) < 40:
        hard.append(f"refined_text_too_short:{len(stripped)}")

    for issue in validate_formatted_text(stripped):
        if issue.startswith("provider/meta marker:") or issue == "Han Chinese characters present":
            hard.append(issue)
        elif issue.startswith("quote-only line"):
            warnings.append(issue)

    if re.search(r"(.)\1{20,}", stripped):
        hard.append("runaway_repeated_character")

    return hard, warnings


def _pre_qa_guardrail_blocks(config: AppConfig, text: str) -> tuple[bool, list[str], list[str]]:
    policy = getattr(config, "execution", None)
    hard, warnings = _pre_qa_guardrail_issues(text)
    blocks = bool(policy is not None and policy.pre_qa_blocks_runtime() and hard)
    return blocks, hard, warnings


def _artifact_cache_enabled_for_stage(config: AppConfig, stage: str) -> bool:
    policy = getattr(config, "execution", None)
    if policy is None or not policy.cache_skips_runtime():
        return False
    return stage in set(getattr(policy, "artifact_cache_stages", ()) or ())


def _literal_translation_input_hash(
    *,
    config: AppConfig,
    prompt_store: PromptStore,
    block: TextBlock,
    glossary_subset: list[GlossaryEntry],
) -> str:
    source_for_prompt = " ".join(line.strip() for line in block.source_text.splitlines() if line.strip())
    prompt = prompt_store.render(
        "literal_translation",
        source_block=source_for_prompt,
        glossary_subset=format_glossary_subset(glossary_subset),
        source_language=block.source_language,
        research_context=config.research_context_text(),
    )
    routing = config.stage_routing_for("literal_translation")
    payload = {
        "cache_version": "literal_translation:v2",
        "stage": "translating",
        "block_id": block.block_id,
        "chapter_id": block.chapter_id,
        "source_language": block.source_language,
        "source_text": block.source_text,
        "prompt_sha256": _sha256(prompt),
        "provider": routing.provider,
        "model": routing.model,
        "fallbacks": list(routing.fallbacks),
        "glossary": [
            {
                "original_term": entry.original_term,
                "thai_term": entry.thai_term,
                "category": entry.category,
                "status": entry.status,
            }
            for entry in sorted(glossary_subset, key=lambda item: item.original_term)
        ],
        "research_context_sha256": _sha256(config.research_context_text()),
    }
    return _sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def _load_literal_translation_cache(
    *,
    config: AppConfig,
    ledger: RunLedger,
    run_id: str,
    block: TextBlock,
    input_hash: str,
) -> tuple[LiteralDraft | None, dict[str, Any]]:
    if not _artifact_cache_enabled_for_stage(config, "translating"):
        return None, {"cache_status": "disabled"}

    cached = _read_block_artifact(config, block.chapter_id, block.block_id, "literal")
    if cached is None:
        return None, {"cache_status": "miss", "reason": "missing_literal_artifact"}

    draft = _reconstruct_literal_draft(cached, block.block_id, block.chapter_id)
    if not draft.sentence_pairs:
        return None, {"cache_status": "miss", "reason": "invalid_literal_artifact"}
    if draft.source_text != block.source_text:
        return None, {"cache_status": "miss", "reason": "source_text_mismatch"}

    output_hash = _sha256(str(draft.to_dict()))
    for record in reversed(tuple(ledger.iter_records(block_id=block.block_id, stage="translating", status="completed"))):
        if record.run_id == run_id:
            continue
        if record.input_hash == input_hash and record.output_hash == output_hash:
            return draft, {
                "cache_status": "hit",
                "cached_from_run_id": record.run_id,
                "cached_provider": record.provider,
                "cache_stage": "translating",
            }

    return None, {"cache_status": "miss", "reason": "no_matching_hash_record"}


def _format_block_with_hybrid_provider(
    *,
    config: AppConfig,
    prompt_store: PromptStore,
    refined_text: str,
) -> tuple[str, str, dict[str, Any]]:
    provider_attempts: list[dict[str, Any]] = []
    try:
        routing = config.stage_routing_for("formatting")
        if routing.provider and routing.provider != "local":
            candidates: list[tuple[ProviderRunner, str]] = [
                (_provider_runner_for_stage(config, "formatting"), config.stage_model_for("formatting") or "")
            ]
            candidates.extend(_fallback_provider_runners_for_stage(config, "formatting"))
            prompt = prompt_store.render("formatting.md", text=refined_text)
            for runner, model in candidates:
                try:
                    response = runner.run_with_retry(
                        ProviderRequest(
                            prompt=prompt,
                            provider=runner.spec.name,
                            stage="formatting",
                            model=model,
                            cwd=config.workspace.root,
                            timeout_seconds=routing.timeout_seconds,
                        ),
                        require_stdout=True,
                        max_attempts=routing.retry_max_attempts,
                        retry_delay_seconds=routing.retry_initial_delay_seconds,
                        retry_backoff_multiplier=routing.retry_backoff_multiplier,
                        retry_failure_kinds=routing.retry_failure_kinds,
                    )
                    ensure_provider_response(response)
                    provider_text = cleanup_provider_formatted_text(response.stdout)
                    validation_issues = validate_formatted_text(provider_text, source_text=refined_text)
                    if validation_issues:
                        provider_attempts.append({
                            "formatting_mode": "provider_failed_validation",
                            "provider": runner.spec.name,
                            "model": response.model,
                            "validation_issues": validation_issues,
                            "duration_seconds": response.duration_seconds,
                        })
                        continue
                    return provider_text, runner.spec.name, {
                        "formatting_mode": "provider",
                        "model": response.model,
                        "duration_seconds": response.duration_seconds,
                        "local_cleanup": "minimal_whitespace",
                    }
                except Exception as exc:
                    provider_error = _exception_metadata(exc)
                    provider_error["formatting_mode"] = "provider_failed"
                    provider_error["provider"] = runner.spec.name
                    provider_attempts.append(provider_error)
    except Exception as exc:
        provider_attempts.append({**_exception_metadata(exc), "formatting_mode": "provider_failed"})

    local_text = format_block_text(refined_text)
    metadata: dict[str, Any] = {"formatting_mode": "local_fallback"}
    if provider_attempts:
        metadata["provider_attempts"] = provider_attempts
    return local_text, "local", metadata


def _chapter_sort_key(chapter_id: str) -> tuple[int, str]:
    match = _CHAPTER_ID_RE.fullmatch(chapter_id)
    if match is not None:
        return int(match.group(1)), chapter_id
    return 10**9, chapter_id


def _split_block_id(block_id: str) -> tuple[str, int]:
    if "-block-" not in block_id:
        raise ValueError(f"Invalid block ID '{block_id}'. Expected format like ch019-block-006.")
    chapter_id, block_suffix = block_id.rsplit("-block-", 1)
    if not chapter_id or not block_suffix:
        raise ValueError(f"Invalid block ID '{block_id}'. Expected format like ch019-block-006.")
    try:
        block_index = int(block_suffix)
    except ValueError as exc:
        raise ValueError(f"Invalid block ID '{block_id}'. Block index must be numeric.") from exc
    return chapter_id, block_index


def _block_sort_key(block_id: str) -> tuple[int, int, str]:
    chapter_id, block_index = _split_block_id(block_id)
    chapter_index, _ = _chapter_sort_key(chapter_id)
    return chapter_index, block_index, block_id


def _block_chapter_id(block_id: str) -> str:
    chapter_id, _ = _split_block_id(block_id)
    return chapter_id


def _provider_runner_for_stage(config: AppConfig, stage: str) -> ProviderRunner:
    provider_spec = config.provider_for_stage(stage)
    return ProviderRunner(provider_spec)


def _fallback_provider_runner_for_stage(config: AppConfig, stage: str) -> ProviderRunner | None:
    provider_spec = config.fallback_provider_for_stage(stage)
    if provider_spec is None:
        return None
    return ProviderRunner(provider_spec)


def _fallback_provider_runners_for_stage(config: AppConfig, stage: str) -> list[tuple[ProviderRunner, str]]:
    return [(ProviderRunner(provider_spec), model) for provider_spec, model in config.fallback_routes_for_stage(stage)]


def _run_refine_with_fallback_chain(
    *,
    config: AppConfig,
    ledger: RunLedger,
    run_id: str,
    block: TextBlock,
    literal_draft: LiteralDraft,
    glossary_subset: list[GlossaryEntry],
    style_key: str,
    input_hash: str = "",
    retry_feedback: str = "",
    failure_metadata: dict[str, Any] | None = None,
    commit_failures: bool = True,
) -> tuple[RefinedDraft, str]:
    primary_runner = _provider_runner_for_stage(config, "refinement")
    primary_model = config.stage_model_for("refinement") or ""
    candidates: list[tuple[ProviderRunner, str]] = [(primary_runner, primary_model)]
    candidates.extend(_fallback_provider_runners_for_stage(config, "refinement"))
    metadata_extra = failure_metadata or {}

    for index, (runner, model) in enumerate(candidates):
        try:
            feedback = retry_feedback
            if index > 0:
                previous_provider = candidates[index - 1][0].spec.name
                note = f"Previous provider {previous_provider} failed; preserve meaning and polish Thai prose."
                feedback = f"{retry_feedback}\n\n{note}".strip() if retry_feedback else note
            draft = run_refine_stage(
                config=config,
                block=block,
                literal_draft=literal_draft,
                glossary_subset=glossary_subset,
                style_profile_key=style_key,
                provider_runner=runner,
                model=model,
                retry_feedback=feedback,
            )
            return draft, runner.spec.name
        except Exception as exc:
            next_runner = candidates[index + 1][0] if index + 1 < len(candidates) else None
            metadata = {**_exception_metadata(exc), **metadata_extra}
            if next_runner is not None:
                metadata["fallback_provider"] = next_runner.spec.name
            if commit_failures:
                _commit_stage(
                    ledger,
                    run_id,
                    block.block_id,
                    "refining",
                    "failed",
                    provider=runner.spec.name,
                    input_hash=input_hash,
                    metadata=metadata,
                )
            if next_runner is None:
                raise

    raise RuntimeError(f"Refinement did not produce a draft for {block.block_id}.")


_QA_OMISSION_MARKERS = (
    "omit",
    "omitted",
    "omission",
    "missing",
    "skipped",
    "dropped",
    "ตกหล่น",
    "หาย",
    "ขาด",
    "ละทิ้ง",
    "ไม่ได้แปล",
    "ไม่ได้ใส่",
)


def _qa_report_indicates_omission(qa_report: QAReport) -> bool:
    text_parts = [qa_report.feedback or ""]
    for finding in qa_report.findings:
        text_parts.extend((finding.code, finding.message, finding.details))
    lowered = "\n".join(text_parts).lower()
    return any(marker in lowered for marker in _QA_OMISSION_MARKERS)


def _literal_safe_refined_draft(
    *,
    block: TextBlock,
    literal_draft: LiteralDraft,
    qa_report: QAReport,
) -> RefinedDraft | None:
    literal_sentences = [
        pair.literal_sentence.strip()
        for pair in literal_draft.sentence_pairs
        if pair.literal_sentence.strip()
    ]
    literal_text = "\n\n".join(literal_sentences).strip()
    if not literal_text:
        return None
    return RefinedDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        refined_text=literal_text,
        provider="local_recovery",
        style_profile="literal_safe_omission_recovery",
        source_text=literal_draft.source_text or block.source_text,
        metadata={
            "recovery_reason": "qa_omission_literal_safe_refined_text",
            "qa_feedback": qa_report.feedback,
        },
    )


def _run_literal_with_fallback_chain(
    *,
    config: AppConfig,
    ledger: RunLedger,
    run_id: str,
    block: TextBlock,
    glossary_subset: list[GlossaryEntry],
    input_hash: str = "",
    commit_failures: bool = True,
) -> tuple[LiteralDraft, str]:
    primary_runner = _provider_runner_for_stage(config, "literal_translation")
    primary_model = config.stage_model_for("literal_translation") or ""
    candidates: list[tuple[ProviderRunner, str]] = [(primary_runner, primary_model)]
    candidates.extend(_fallback_provider_runners_for_stage(config, "literal_translation"))

    for index, (runner, model) in enumerate(candidates):
        try:
            draft = run_literal_translation_stage(
                config=config,
                block=block,
                glossary_subset=glossary_subset,
                provider_runner=runner,
                model=model,
            )
            return draft, runner.spec.name
        except Exception as exc:
            next_runner = candidates[index + 1][0] if index + 1 < len(candidates) else None
            metadata = _exception_metadata(exc)
            if next_runner is not None:
                metadata["fallback_provider"] = next_runner.spec.name
            if commit_failures:
                _commit_stage(
                    ledger,
                    run_id,
                    block.block_id,
                    "translating",
                    "failed",
                    provider=runner.spec.name,
                    input_hash=input_hash,
                    metadata=metadata,
                )
            if next_runner is None:
                raise

    raise RuntimeError(f"Literal translation did not produce a draft for {block.block_id}.")


def _load_or_create_glossary_index(config: AppConfig) -> dict[str, GlossaryEntry]:
    idx = load_glossary_index(config.workspace.glossary_dir)
    if not idx:
        config.workspace.glossary_dir.mkdir(parents=True, exist_ok=True)
    return idx


def _resolve_glossary_subset(blocks: list[TextBlock], glossary_index: dict[str, GlossaryEntry]) -> list[GlossaryEntry]:
    # Build result dict keyed by original_term to deduplicate entries
    matched: dict[str, GlossaryEntry] = {}
    
    for block in blocks:
        text = block.source_text or block.text
        if not text:
            continue
        
        # Step 1: collect candidate terms (source keys) that appear in text
        candidates: list[tuple[str, GlossaryEntry]] = []
        for key, entry in glossary_index.items():
            if entry.status == "approved" and key in text:
                candidates.append((key, entry))
        
        # Step 2: sort by term length descending, then by term for stability
        candidates.sort(key=lambda pair: (-len(pair[0]), pair[0]))
        
        # Step 3: track occupied spans (start, end) in text
        occupied: list[tuple[int, int]] = []
        
        for term, entry in candidates:
            # Find all occurrences of term in text
            occurrences: list[int] = []
            start = 0
            while True:
                pos = text.find(term, start)
                if pos == -1:
                    break
                occurrences.append(pos)
                start = pos + 1
            
            # Check if any occurrence does not overlap with any occupied span
            term_len = len(term)
            for pos in occurrences:
                end = pos + term_len
                overlap = False
                for occ_start, occ_end in occupied:
                    if pos < occ_end and end > occ_start:
                        overlap = True
                        break
                if not overlap:
                    # This occurrence is free; include the entry
                    matched[entry.original_term] = entry
                    # Mark this occurrence as occupied
                    occupied.append((pos, end))
                    break  # no need to check other occurrences
    
    return list(matched.values())


def _artifact_block_path(config: AppConfig, chapter_id: str, block_id: str, stage: str, suffix: str = "json") -> Path:
    return block_artifact_path(config.workspace.work, chapter_id, block_id, f"{stage}.{suffix}")


def _glossary_scan_path(config: AppConfig, *, chapter_id: str | None = None, run_id: str | None = None) -> Path:
    if chapter_id is not None:
        return glossary_scan_artifact_path(config.workspace.work, chapter_id)
    if run_id is not None:
        return batch_glossary_scan_artifact_path(config.workspace.work, run_id)
    raise ValueError("chapter_id or run_id is required for glossary scan artifacts.")


def _write_glossary_scan_artifact(
    config: AppConfig,
    *,
    items: list[dict[str, Any]],
    chapter_id: str | None = None,
    run_id: str | None = None,
    chapter_ids: list[str] | None = None,
) -> Path:
    path = _glossary_scan_path(config, chapter_id=chapter_id, run_id=run_id)
    payload = {
        "schema_version": 1,
        "scope": {
            "type": "batch" if run_id is not None else "chapter",
            "id": run_id if run_id is not None else chapter_id,
        },
        "chapter_ids": chapter_ids or ([chapter_id] if chapter_id is not None else []),
        "items": items,
    }
    atomic_write_json(path, payload)
    return path


def _read_glossary_scan_artifact(
    config: AppConfig,
    *,
    chapter_id: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any] | None:
    path = _glossary_scan_path(config, chapter_id=chapter_id, run_id=run_id)
    raw = read_text_if_exists(path)
    if raw is None:
        return None
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid glossary scan artifact at {path}: expected JSON object.")
    return data


def _read_glossary_scan_items(
    config: AppConfig,
    *,
    chapter_id: str | None = None,
    run_id: str | None = None,
) -> list[dict[str, Any]]:
    data = _read_glossary_scan_artifact(config, chapter_id=chapter_id, run_id=run_id)
    if not data:
        return []

    items = data.get("items")
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)]

    # Backward compatibility with older scan artifacts.
    pending_terms = data.get("pending_terms")
    if isinstance(pending_terms, list):
        fallback_items: list[dict[str, Any]] = []
        for term in pending_terms:
            if not isinstance(term, str) or not term:
                continue
            fallback_items.append(
                {
                    "original_term": term,
                    "category": infer_category(term),
                    "chapter_id": chapter_id or str(data.get("chapter_id", "")),
                    "first_seen_block": "block-001",
                    "context": "",
                    "source_language": "",
                    "novel": "",
                }
            )
        return fallback_items

    return []


def _queue_item_index(queue_items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for item in queue_items:
        term = str(item.get("original_term", "")).strip()
        if term and term not in index:
            index[term] = item
    return index


def _revalidate_glossary_queue_items(
    config: AppConfig,
    blocks: list[TextBlock],
    queue_items: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Remove stale/noisy queue terms using the current deterministic scan guard.

    Approval may shrink an older queue artifact, but it must not silently add new terms
    that were absent from that artifact.
    """
    allowed_items = build_glossary_scan_queue(config, blocks, exclude_existing=False)
    allowed_terms = {
        str(item.get("original_term", "")).strip()
        for item in allowed_items
        if str(item.get("original_term", "")).strip()
    }
    filtered_items: list[dict[str, Any]] = []
    removed_terms: list[str] = []
    seen: set[str] = set()
    for item in queue_items:
        term = str(item.get("original_term", "")).strip()
        if not term or term in seen:
            continue
        seen.add(term)
        if term in allowed_terms:
            filtered_items.append(item)
        else:
            removed_terms.append(term)
    return filtered_items, removed_terms


def _load_glossary_index_from_queue(
    config: AppConfig,
    queue_items: list[dict[str, Any]],
) -> dict[str, GlossaryEntry]:
    glossary_index = _load_or_create_glossary_index(config)
    for item in queue_items:
        term = str(item.get("original_term", "")).strip()
        if not term:
            continue
        entry = GlossaryEntry(
            original_term=term,
            thai_term=str(item.get("thai_term", "")),
            category=str(item.get("category", "")) or infer_category(term),
            status=str(item.get("status", "proposed")) or "proposed",
            source_language=str(item.get("source_language", config.source_language)),
            novel=str(item.get("novel", config.novel_id)),
            metadata={
                "chapter_id": item.get("chapter_id", ""),
                "first_seen_block": item.get("first_seen_block", ""),
                "context": item.get("context", ""),
            },
        )
        existing = glossary_index.get(term)
        if existing is not None and existing.status == "approved":
            continue
        glossary_index[term] = entry
    return glossary_index


def _pending_terms_from_queue(
    glossary_index: dict[str, GlossaryEntry],
    queue_items: list[dict[str, Any]],
) -> list[str]:
    pending: list[str] = []
    seen: set[str] = set()
    for item in queue_items:
        term = str(item.get("original_term", "")).strip()
        if not term or term in seen:
            continue
        seen.add(term)
        entry = glossary_index.get(term)
        if entry is None or entry.status != "approved":
            pending.append(term)
    return pending


def _commit_stage(
    ledger: RunLedger,
    run_id: str,
    block_id: str,
    stage: str,
    status: str,
    provider: str = "",
    input_hash: str = "",
    output_hash: str = "",
    metadata: dict[str, Any] | None = None,
) -> None:
    ledger.append_stage(
        run_id=run_id,
        block_id=block_id,
        stage=stage,
        status=status,
        provider=provider,
        input_hash=input_hash,
        output_hash=output_hash,
        metadata=metadata,
    )


def _exception_metadata(exc: Exception) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "error_type": type(exc).__name__,
        "message": str(exc),
    }
    if isinstance(exc, ProviderExecutionError):
        response = exc.response
        metadata.update(
            {
                "provider": response.provider,
                "model": response.model,
                "returncode": response.returncode,
                "stderr_preview": (response.stderr or "").strip()[:500],
                "stdout_preview": (response.stdout or "").strip()[:500],
                "duration_seconds": response.duration_seconds,
            }
        )
    return metadata


def _normalize_block_stage(stage: str) -> str:
    key = stage.strip().lower().replace("_", "-")
    key = key.replace("-", "")
    aliases = {name.replace("-", ""): value for name, value in BLOCK_STAGE_ALIASES.items()}
    try:
        return aliases[key]
    except KeyError as exc:
        allowed = ", ".join(sorted(BLOCK_STAGE_ALIASES))
        raise ValueError(f"Unsupported block stage '{stage}'. Use one of: {allowed}") from exc


def _should_force_block_stage(stage: str, *, force: bool, force_from_stage: str | None) -> bool:
    if force:
        return True
    if force_from_stage is None:
        return False
    normalized = _normalize_block_stage(force_from_stage)
    return BLOCK_STAGE_ORDER.index(stage) >= BLOCK_STAGE_ORDER.index(normalized)


def _write_block_artifact(config: AppConfig, chapter_id: str, block_id: str, stage: str, data: Any) -> Path:
    path = _artifact_block_path(config, chapter_id, block_id, stage)
    atomic_write_json(path, data)
    return path


def _read_block_artifact(config: AppConfig, chapter_id: str, block_id: str, stage: str) -> Any | None:
    path = _artifact_block_path(config, chapter_id, block_id, stage)
    raw = read_text_if_exists(path)
    if raw is None:
        return None
    return json.loads(raw)


def _load_chapter_source_and_blocks(config: AppConfig, chapter_id: str) -> tuple[ChapterSource, list[TextBlock]]:
    source_path = config.workspace.raw / chapter_id / "source.json"
    raw_text = read_text_if_exists(source_path)
    if raw_text is None:
        raise ValueError(f"No fetched source found at {source_path}. Run fetch or run first.")
    raw_source = json.loads(raw_text)
    chapter_source = ChapterSource(
        novel_id=raw_source.get("novel_id", config.novel_id),
        chapter_id=raw_source.get("chapter_id", chapter_id),
        title=raw_source.get("title", ""),
        source_language=raw_source.get("source_language", config.source_language),
        raw_text=raw_source.get("raw_text", ""),
    )
    blocks = split_blocks(
        chapter_id=chapter_id,
        text=chapter_source.raw_text,
        source_language=config.source_language,
        zh_limit=config.chunking.chinese_character_limit,
        non_zh_limit=config.chunking.non_chinese_word_limit,
    )
    return chapter_source, blocks


def _find_block(blocks: list[TextBlock], block_id: str) -> TextBlock:
    block = next((item for item in blocks if item.block_id == block_id), None)
    if block is None:
        raise ValueError(f"Block '{block_id}' was not found.")
    return block


def _output_chapter_path(config: AppConfig, chapter_id: str) -> Path:
    return chapter_dir(config.workspace.output, chapter_id)


def run_pipeline(
    *,
    config: AppConfig | None = None,
    chapter_id: str,
    title: str = "",
    input_file: Path | None = None,
    text: str | None = None,
    style_profile: str | None = None,
    run_id: str | None = None,
    force: bool = False,
    adapter_name: str = "",
    manual_action_mode: str = "interactive",
) -> PipelineContext:
    if config is None:
        config = load_app_config()
    if run_id is None:
        import uuid
        run_id = f"run-{uuid.uuid4().hex[:8]}"

    ledger = RunLedger(config.ledger_path)
    config.workspace.logs_dir.mkdir(parents=True, exist_ok=True)

    prompt_store = PromptStore(config.workspace.prompts)
    style_key = style_profile or config.default_style_profile

    ctx = PipelineContext(
        config=config,
        ledger=ledger,
        prompt_store=prompt_store,
        run_id=run_id,
        force=force,
    )

    # Resolve adapter if configured
    adapter = None
    chapter_meta = None
    if adapter_name:
        config.source.adapter = adapter_name
    if not input_file and not text and config.source.adapter:
        from novel_pipeline.adapters import get_adapter
        from novel_pipeline.stages.fetch import load_or_build_manifest, resolve_chapter_meta
        adapter = get_adapter(config.source)
        manifest = load_or_build_manifest(config=config, adapter=adapter, force=force)
        chapter_meta = resolve_chapter_meta(manifest, chapter_id)

    # Stage 1: Fetch
    print(f"[{run_id}] Stage: fetch")
    if not ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="fetched"):
        chapter_source = run_fetch_stage(
            config=config,
            chapter_id=chapter_id,
            title=title,
            input_file=input_file,
            text=text,
            adapter=adapter,
            chapter_meta=chapter_meta,
        )
        ctx.chapter_source = chapter_source
        ih = _sha256(chapter_source.raw_text)
        _commit_stage(ledger, run_id, chapter_id, "fetched", "completed", provider="local", input_hash=ih)
        print(f"[{run_id}]   fetched: {len(chapter_source.raw_text)} chars")
    else:
        print(f"[{run_id}]   fetch already committed, skipping.")

    # Split into blocks
    blocks = split_blocks(
        chapter_id=chapter_id,
        text=ctx.chapter_source.raw_text if ctx.chapter_source else (text or ""),
        source_language=config.source_language,
        zh_limit=config.chunking.chinese_character_limit,
        non_zh_limit=config.chunking.non_chinese_word_limit,
    )
    ctx.blocks = blocks
    if not blocks:
        raise ValueError("No blocks produced from chapter text.")

    # Stage 2: Glossary Pre-Scan
    print(f"[{run_id}] Stage: glossary pre-scan")
    glossary_index = _load_or_create_glossary_index(config)
    ctx.glossary_index = glossary_index

    if not ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="glossary_scanned"):
        queue_items = build_glossary_scan_queue(config, blocks)
        print(f"[{run_id}]   {len(queue_items)} new candidate terms found.")
        _write_glossary_scan_artifact(config, chapter_id=chapter_id, items=queue_items)
        glossary_index = _load_glossary_index_from_queue(config, queue_items)
        ctx.glossary_index = glossary_index
        _commit_stage(ledger, run_id, chapter_id, "glossary_scanned", "completed", provider="local")
        print(f"[{run_id}]   glossary scan committed.")
    else:
        print(f"[{run_id}]   glossary scan already committed, skipping.")

    # Stage 3: Glossary Approval (interactive gate)
    print(f"[{run_id}] Stage: glossary approval")
    if not ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="glossary_approved"):
        queue_artifact = _read_glossary_scan_artifact(config, chapter_id=chapter_id)
        if queue_artifact is None:
            queue_items = build_glossary_scan_queue(config, blocks)
            _write_glossary_scan_artifact(config, chapter_id=chapter_id, items=queue_items)
        else:
            queue_items = _read_glossary_scan_items(config, chapter_id=chapter_id)
        queue_items, removed_terms = _revalidate_glossary_queue_items(config, blocks, queue_items)
        if removed_terms:
            _write_glossary_scan_artifact(config, chapter_id=chapter_id, items=queue_items)
            print(f"[{run_id}]   glossary approval revalidated queue; removed {len(removed_terms)} stale/noisy terms.")
        glossary_index = _load_glossary_index_from_queue(config, queue_items)
        ctx.glossary_index = glossary_index

        template_text = read_text_if_exists(config.workspace.templates_dir / "Term-Template.md")
        if template_text is None:
            template_text = _default_term_template()

        pending_terms = _pending_terms_from_queue(glossary_index, queue_items)
        if pending_terms:
            print(f"[{run_id}]   {len(pending_terms)} terms pending approval.")
            provider_runner = _provider_runner_for_stage(config, "term_suggestion")
            queue_by_term = _queue_item_index(queue_items)
            for term_key in pending_terms:
                entry = glossary_index.get(term_key)
                if entry is None or entry.status == "approved":
                    continue
                queue_item = queue_by_term.get(term_key, {})
                context_text = str(queue_item.get("context", ""))
                suggestion = build_term_suggestion(
                    config=config,
                    provider_runner=provider_runner,
                    prompt_store=ctx.prompt_store,
                    term=term_key,
                    context=context_text,
                )
                thai_term = choose_option_interactively(suggestion)
                entry.thai_term = thai_term
                entry.status = "approved"
                entry.description = suggestion.rationale
                entry.source_language = config.source_language
                entry.novel = config.novel_id
                write_glossary_note(
                    template_text=template_text,
                    glossary_dir=config.workspace.glossary_dir,
                    entry=entry,
                    first_seen_chapter=chapter_id,
                    first_seen_block=str(queue_item.get("first_seen_block", "block-001")),
                )
                glossary_index[term_key] = entry
            ctx.glossary_index = glossary_index

        _commit_stage(ledger, run_id, chapter_id, "glossary_approved", "completed", provider="local")
        print(f"[{run_id}]   glossary approval committed.")
    else:
        print(f"[{run_id}]   glossary approval already committed, skipping.")

    # Process each block through translate -> refine -> QA -> format
    formatted_blocks: list[str] = []
    for block in blocks:
        print(f"[{run_id}] Block: {block.block_id}")
        formatted_text = _process_block(
            ctx,
            block,
            style_key,
            force=force,
            manual_action_mode=manual_action_mode,
        )
        if formatted_text is not None:
            formatted_blocks.append(formatted_text)

    # Write final chapter output
    if formatted_blocks:
        _write_chapter_output_with_sentinel_gate(config, ledger, run_id, chapter_id, formatted_blocks, ctx.chapter_source)

    print(f"[{run_id}] Pipeline completed for chapter {chapter_id}.")
    return ctx


def _process_block(
    ctx: PipelineContext,
    block: TextBlock,
    style_key: str,
    force: bool = False,
    force_from_stage: str | None = None,
    manual_action_mode: str = "interactive",
) -> str | None:
    config = ctx.config
    ledger = ctx.ledger
    run_id = ctx.run_id
    block_id = block.block_id
    glossary_subset = _resolve_glossary_subset([block], ctx.glossary_index)

    # Stage 4: Literal Translation
    print(f"[{run_id}]   Stage: translate")
    literal_draft: LiteralDraft | None = None
    force_translate = _should_force_block_stage("translating", force=force, force_from_stage=force_from_stage)
    if not ledger.has_committed(run_id=run_id, block_id=block_id, stage="translating") or force_translate:
        ih = _literal_translation_input_hash(
            config=config,
            prompt_store=ctx.prompt_store,
            block=block,
            glossary_subset=glossary_subset,
        )
        cache_metadata: dict[str, Any] = {}
        if not force_translate:
            literal_draft, cache_metadata = _load_literal_translation_cache(
                config=config,
                ledger=ledger,
                run_id=run_id,
                block=block,
                input_hash=ih,
            )
        if literal_draft is not None:
            oh = _sha256(str(literal_draft.to_dict()))
            _commit_stage(
                ledger,
                run_id,
                block_id,
                "translating",
                "completed",
                provider="cache",
                input_hash=ih,
                output_hash=oh,
                metadata=cache_metadata,
            )
        else:
            literal_draft, literal_provider_name = _run_literal_with_fallback_chain(
                config=config,
                ledger=ledger,
                run_id=run_id,
                block=block,
                glossary_subset=glossary_subset,
                input_hash=ih,
            )
            oh = _sha256(str(literal_draft.to_dict()))
            _write_block_artifact(config, block.chapter_id, block_id, "literal", literal_draft.to_dict())
            _commit_stage(
                ledger,
                run_id,
                block_id,
                "translating",
                "completed",
                provider=literal_provider_name,
                input_hash=ih,
                output_hash=oh,
                metadata=cache_metadata if cache_metadata.get("cache_status") == "miss" else None,
            )
    else:
        print(f"[{run_id}]     translate already committed, skipping.")
        cached = _read_block_artifact(config, block.chapter_id, block_id, "literal")
        if cached is not None:
            literal_draft = _reconstruct_literal_draft(cached, block_id, block.chapter_id)

    if literal_draft is None:
        raise RuntimeError(
            f"Missing literal artifact for {block_id}. Run with --force or use rerun-block --from-stage literal."
        )

    # Stage 5: Refine
    print(f"[{run_id}]   Stage: refine")
    refined_draft: RefinedDraft | None = None
    force_refine = _should_force_block_stage("refining", force=force, force_from_stage=force_from_stage)
    if not ledger.has_committed(run_id=run_id, block_id=block_id, stage="refining") or force_refine:
        ih = _sha256(str(literal_draft.to_dict()))
        refined_draft, refine_provider_name = _run_refine_with_fallback_chain(
            config=config,
            ledger=ledger,
            run_id=run_id,
            block=block,
            literal_draft=literal_draft,
            glossary_subset=glossary_subset,
            style_key=style_key,
            input_hash=ih,
        )
        if refined_draft is None:
            error = RuntimeError(f"Refinement did not produce a draft for {block_id}.")
            _commit_stage(
                ledger,
                run_id,
                block_id,
                "refining",
                "failed",
                provider=refine_provider_name,
                input_hash=ih,
                metadata=_exception_metadata(error),
            )
            raise error
        repaired_text, glossary_repairs = _apply_glossary_rejected_variant_repairs(
            refined_draft.refined_text,
            glossary_subset,
        )
        repaired_text, footnote_repairs = _apply_source_footnote_marker_repairs(
            repaired_text,
            block.source_text,
        )
        if glossary_repairs or footnote_repairs:
            refined_draft = RefinedDraft(
                block_id=refined_draft.block_id,
                chapter_id=refined_draft.chapter_id,
                refined_text=repaired_text,
                provider=refined_draft.provider,
                style_profile=refined_draft.style_profile,
                source_text=refined_draft.source_text,
                metadata={
                    **refined_draft.metadata,
                    "glossary_rejected_variant_repairs": glossary_repairs,
                    "source_footnote_marker_repairs": footnote_repairs,
                },
            )
        oh = _sha256(refined_draft.refined_text)
        _write_block_artifact(config, block.chapter_id, block_id, "refined", refined_draft.to_dict())
        _commit_stage(ledger, run_id, block_id, "refining", "completed",
                      provider=refine_provider_name, input_hash=ih, output_hash=oh)
    else:
        print(f"[{run_id}]     refine already committed, skipping.")
        cached = _read_block_artifact(config, block.chapter_id, block_id, "refined")
        if cached is not None:
            refined_draft = _reconstruct_refined_draft(cached, block_id, block.chapter_id)

    if refined_draft is None:
        raise RuntimeError(
            f"Missing refined artifact for {block_id}. Run with --force or use rerun-block --from-stage refine."
        )

    # Stage 6: QA
    print(f"[{run_id}]   Stage: QA")
    qa_passed: bool = False
    qa_already_done = (
        ledger.has_committed(run_id=run_id, block_id=block_id, stage="qa")
        or ledger.has_committed(run_id=run_id, block_id=block_id, stage="qa", status="force_accepted")
        or ledger.has_committed(run_id=run_id, block_id=block_id, stage="qa", status="skipped")
    )

    force_qa = _should_force_block_stage("qa", force=force, force_from_stage=force_from_stage)
    if not qa_already_done or force_qa:
        pre_qa_blocks, pre_qa_hard, pre_qa_warnings = _pre_qa_guardrail_blocks(config, refined_draft.refined_text)
        if pre_qa_blocks:
            _commit_stage(
                ledger,
                run_id,
                block_id,
                "qa",
                "failed",
                provider="local",
                input_hash=_sha256(refined_draft.refined_text),
                metadata={
                    "guardrail": "pre_qa",
                    "mode": config.execution.pre_qa_guardrail_mode,
                    "hard_errors": pre_qa_hard,
                    "warnings": pre_qa_warnings,
                },
            )
            raise ValueError(
                f"Pre-QA guardrail blocked {block_id}: {'; '.join(pre_qa_hard)}"
            )
        try:
            qa_passed = _run_qa_with_retries(
                ctx=ctx,
                block=block,
                literal_draft=literal_draft,
                refined_draft=refined_draft,
                glossary_subset=glossary_subset,
                style_key=style_key,
                manual_action_mode=manual_action_mode,
            )
        except ManualActionRequired:
            _commit_stage(
                ledger,
                run_id,
                block_id,
                "qa",
                "hard_fail",
                provider="local",
            )
            raise
        except Exception as exc:
            provider_name = config.stage_provider_name("qa_judge")
            _commit_stage(
                ledger,
                run_id,
                block_id,
                "qa",
                "failed",
                provider=provider_name,
                metadata=_exception_metadata(exc),
            )
            raise

        if not qa_passed:
            print(f"[{run_id}]   Block {block_id} QA hard-failed. Marking as failed.")
            ledger.append_stage(
                run_id=run_id, block_id=block_id, stage="qa", status="hard_fail", provider="local"
            )
            return
    else:
        print(f"[{run_id}]     QA already committed, skipping.")
        qa_passed = True

    latest_refined = _read_block_artifact(config, block.chapter_id, block_id, "refined")
    if latest_refined is not None:
        refined_draft = _reconstruct_refined_draft(latest_refined, block_id, block.chapter_id)

    # Stage 7: Format
    print(f"[{run_id}]   Stage: format")
    formatted_text: str | None = None
    force_format = _should_force_block_stage("formatting", force=force, force_from_stage=force_from_stage)
    if not ledger.has_committed(run_id=run_id, block_id=block_id, stage="formatting") or force_format:
        formatted_text, formatter_provider, formatter_metadata = _format_block_with_hybrid_provider(
            config=config,
            prompt_store=ctx.prompt_store,
            refined_text=refined_draft.refined_text,
        )
        formatted_text, parenthetical_repairs = _apply_glossary_parenthetical_leakage_repairs(
            formatted_text,
            glossary_subset,
        )
        if parenthetical_repairs:
            formatter_metadata = {
                **formatter_metadata,
                "glossary_parenthetical_leakage_repairs": parenthetical_repairs,
            }
        validation_source_text, _ = _apply_glossary_parenthetical_leakage_repairs(
            refined_draft.refined_text,
            glossary_subset,
        )
        validation_issues = validate_formatted_text(formatted_text, source_text=validation_source_text)
        if validation_issues:
            _commit_stage(
                ledger,
                run_id,
                block_id,
                "formatting",
                "failed",
                provider=formatter_provider,
                metadata={**formatter_metadata, "validation_issues": validation_issues},
            )
            raise ValueError(
                f"Formatted text validation failed for {block_id}: {'; '.join(validation_issues)}"
            )
        oh = _sha256(formatted_text)
        _write_block_artifact(config, block.chapter_id, block_id, "formatted", {"text": formatted_text})
        _commit_stage(ledger, run_id, block_id, "formatting", "completed",
                      provider=formatter_provider, output_hash=oh, metadata=formatter_metadata)
    else:
        print(f"[{run_id}]     format already committed, skipping.")
        cached = _read_block_artifact(config, block.chapter_id, block_id, "formatted")
        if cached is not None:
            formatted_text = cached.get("text", refined_draft.refined_text)
        validation_issues = validate_formatted_text(formatted_text or "", source_text=refined_draft.refined_text)
        if validation_issues:
            print(f"[{run_id}]     cached formatted text is stale; rerunning format.")
            formatted_text, formatter_provider, formatter_metadata = _format_block_with_hybrid_provider(
                config=config,
                prompt_store=ctx.prompt_store,
                refined_text=refined_draft.refined_text,
            )
            formatted_text, parenthetical_repairs = _apply_glossary_parenthetical_leakage_repairs(
                formatted_text,
                glossary_subset,
            )
            if parenthetical_repairs:
                formatter_metadata = {
                    **formatter_metadata,
                    "glossary_parenthetical_leakage_repairs": parenthetical_repairs,
                }
            validation_source_text, _ = _apply_glossary_parenthetical_leakage_repairs(
                refined_draft.refined_text,
                glossary_subset,
            )
            validation_issues = validate_formatted_text(formatted_text, source_text=validation_source_text)
            if validation_issues:
                _commit_stage(
                    ledger,
                    run_id,
                    block_id,
                    "formatting",
                    "failed",
                    provider=formatter_provider,
                    metadata={**formatter_metadata, "validation_issues": validation_issues, "stale_cache_reformatted": True},
                )
                raise ValueError(
                    f"Formatted text validation failed for {block_id}: {'; '.join(validation_issues)}"
                )
            oh = _sha256(formatted_text)
            _write_block_artifact(config, block.chapter_id, block_id, "formatted", {"text": formatted_text})
            _commit_stage(
                ledger,
                run_id,
                block_id,
                "formatting",
                "completed",
                provider=formatter_provider,
                output_hash=oh,
                metadata={**formatter_metadata, "stale_cache_reformatted": True},
            )

    # Mark block completed
    if not ledger.has_committed(run_id=run_id, block_id=block_id, stage="completed") or force or force_from_stage:
        ledger.append_stage(
            run_id=run_id, block_id=block_id, stage="completed", status="completed", provider="local"
        )

    return formatted_text


def _formatting_parallel_limit(config: AppConfig) -> int:
    policy = getattr(config, "execution", None)
    limit_for_stage = getattr(policy, "limit_for_stage", None)
    if not callable(limit_for_stage):
        return 1
    try:
        return max(1, int(limit_for_stage("formatting")))
    except (TypeError, ValueError):
        return 1


def _load_refined_for_formatting(config: AppConfig, block: TextBlock) -> RefinedDraft:
    cached = _read_block_artifact(config, block.chapter_id, block.block_id, "refined")
    if cached is None:
        raise RuntimeError(f"Missing refined artifact for {block.block_id}.")
    return _reconstruct_refined_draft(cached, block.block_id, block.chapter_id)


def _format_ready_blocks_parallel(
    ctx: PipelineContext,
    blocks: list[TextBlock],
) -> dict[str, str]:
    """Format already-QA-approved blocks concurrently, then commit in block order."""
    config = ctx.config
    ledger = ctx.ledger
    run_id = ctx.run_id
    limit = _formatting_parallel_limit(config)
    if limit <= 1 or len(blocks) <= 1:
        return {}

    refined_by_block: dict[str, RefinedDraft] = {}
    for block in blocks:
        qa_done = (
            ledger.has_committed(run_id=run_id, block_id=block.block_id, stage="qa")
            or ledger.has_committed(run_id=run_id, block_id=block.block_id, stage="qa", status="force_accepted")
            or ledger.has_committed(run_id=run_id, block_id=block.block_id, stage="qa", status="skipped")
        )
        if not qa_done:
            raise RuntimeError(f"Cannot parallel-format {block.block_id}: QA is not committed.")
        refined_by_block[block.block_id] = _load_refined_for_formatting(config, block)

    def format_one(block: TextBlock) -> _FormattingResult:
        refined = refined_by_block[block.block_id]
        glossary_index = ctx.glossary_index if isinstance(ctx.glossary_index, dict) else {}
        glossary_subset = _resolve_glossary_subset([block], glossary_index)
        text, provider, metadata = _format_block_with_hybrid_provider(
            config=config,
            prompt_store=ctx.prompt_store,
            refined_text=refined.refined_text,
        )
        text, parenthetical_repairs = _apply_glossary_parenthetical_leakage_repairs(text, glossary_subset)
        if parenthetical_repairs:
            metadata = {
                **metadata,
                "glossary_parenthetical_leakage_repairs": parenthetical_repairs,
            }
        validation_source_text, _ = _apply_glossary_parenthetical_leakage_repairs(
            refined.refined_text,
            glossary_subset,
        )
        validation_issues = validate_formatted_text(text, source_text=validation_source_text)
        if validation_issues:
            raise ValueError(
                f"Formatted text validation failed for {block.block_id}: {'; '.join(validation_issues)}"
            )
        return _FormattingResult(
            text=text,
            provider=provider,
            metadata=metadata,
            output_hash=_sha256(text),
        )

    results: dict[str, _FormattingResult] = {}
    max_workers = min(limit, len(blocks))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(format_one, block): block for block in blocks}
        for future in as_completed(futures):
            block = futures[future]
            try:
                results[block.block_id] = future.result()
            except Exception as exc:
                _commit_stage(
                    ledger,
                    run_id,
                    block.block_id,
                    "formatting",
                    "failed",
                    provider=config.stage_provider_name("formatting"),
                    metadata=_exception_metadata(exc),
                )
                raise

    formatted_text_by_block: dict[str, str] = {}
    for block in blocks:
        result = results[block.block_id]
        _write_block_artifact(config, block.chapter_id, block.block_id, "formatted", {"text": result.text})
        _commit_stage(
            ledger,
            run_id,
            block.block_id,
            "formatting",
            "completed",
            provider=result.provider,
            output_hash=result.output_hash,
            metadata={**result.metadata, "parallel_formatting": True, "parallel_limit": max_workers},
        )
        if not ledger.has_committed(run_id=run_id, block_id=block.block_id, stage="completed"):
            ledger.append_stage(
                run_id=run_id,
                block_id=block.block_id,
                stage="completed",
                status="completed",
                provider="local",
            )
        formatted_text_by_block[block.block_id] = result.text
    return formatted_text_by_block


def _run_qa_with_retries(
    *,
    ctx: PipelineContext,
    block: TextBlock,
    literal_draft: LiteralDraft,
    refined_draft: RefinedDraft,
    glossary_subset: list[GlossaryEntry],
    style_key: str,
    manual_action_mode: str = "interactive",
    auto_refine: bool = True,
) -> bool:
    config = ctx.config
    ledger = ctx.ledger
    run_id = ctx.run_id
    block_id = block.block_id

    retry_count = 0
    current_refined = refined_draft
    literal_safe_recovery_attempted = False

    while retry_count <= QA_MAX_RETRIES:
        primary_runner = _provider_runner_for_stage(config, "qa_judge")
        primary_model = config.stage_model_for("qa_judge") or ""
        candidates: list[tuple[ProviderRunner, str]] = [(primary_runner, primary_model)]
        candidates.extend(_fallback_provider_runners_for_stage(config, "qa_judge"))
        qa_report = None
        used_runner: ProviderRunner | None = None
        used_model = ""
        used_route_index = 0
        last_output_error: ProviderOutputError | None = None
        for route_index, (runner, model) in enumerate(candidates):
            try:
                qa_report = run_qa_stage(
                    config=config,
                    block=block,
                    literal_draft=literal_draft,
                    refined_draft=current_refined,
                    glossary_subset=glossary_subset,
                    provider_runner=runner,
                    model=model,
                    retry_count=retry_count,
                    style_profile_key=style_key,
                )
                used_runner = runner
                used_model = model or runner.spec.default_model
                used_route_index = route_index
                break
            except ProviderOutputError as exc:
                last_output_error = exc
                continue
        if qa_report is None or used_runner is None:
            if last_output_error is not None:
                raise last_output_error
            raise RuntimeError(f"QA did not produce a report for {block_id}.")
        provider_runner = used_runner
        _write_block_artifact(config, block.chapter_id, block_id, "qa", qa_report.to_dict())

        if qa_report.passed:
            ledger.append_stage(
                run_id=run_id, block_id=block_id, stage="qa", status="completed",
                provider=provider_runner.spec.name,
                metadata={"model": used_model, "route_index": used_route_index},
            )
            print(f"[{run_id}]     QA passed (retry {retry_count}).")
            return True

        if not auto_refine:
            print(f"[{run_id}]     QA failed; auto re-refine disabled.")
            return False

        retry_count += 1
        if retry_count > QA_MAX_RETRIES:
            if not literal_safe_recovery_attempted and _qa_report_indicates_omission(qa_report):
                recovered_refined = _literal_safe_refined_draft(
                    block=block,
                    literal_draft=literal_draft,
                    qa_report=qa_report,
                )
                literal_safe_recovery_attempted = True
                if recovered_refined is not None:
                    current_refined = recovered_refined
                    repaired_text, glossary_repairs = _apply_glossary_rejected_variant_repairs(
                        current_refined.refined_text,
                        glossary_subset,
                    )
                    repaired_text, footnote_repairs = _apply_source_footnote_marker_repairs(
                        repaired_text,
                        block.source_text,
                    )
                    if glossary_repairs or footnote_repairs:
                        current_refined = RefinedDraft(
                            block_id=current_refined.block_id,
                            chapter_id=current_refined.chapter_id,
                            refined_text=repaired_text,
                            provider=current_refined.provider,
                            style_profile=current_refined.style_profile,
                            source_text=current_refined.source_text,
                            metadata={
                                **current_refined.metadata,
                                "glossary_rejected_variant_repairs": glossary_repairs,
                                "source_footnote_marker_repairs": footnote_repairs,
                            },
                        )
                    _write_block_artifact(config, block.chapter_id, block_id, "refined", current_refined.to_dict())
                    _commit_stage(
                        ledger,
                        run_id,
                        block_id,
                        "refining",
                        "completed",
                        provider=current_refined.provider,
                        output_hash=_sha256(current_refined.refined_text),
                        metadata={
                            "recovery": "qa_omission_literal_safe_refined_text",
                            "retry_from_qa": retry_count,
                            "qa_feedback": qa_report.feedback,
                            "glossary_rejected_variant_repairs": glossary_repairs,
                            "source_footnote_marker_repairs": footnote_repairs,
                        },
                    )
                    retry_count = QA_MAX_RETRIES
                    print(f"[{run_id}]     QA omission hard-fail; restored literal-safe refined text for one final QA pass.")
                    continue

            # Hard fail - offer escalation
            print(f"[{run_id}]     QA hard-fail after {QA_MAX_RETRIES} retries.")
            choice = _qa_escalation_prompt(
                qa_report,
                block_id=block_id,
                stage="qa",
                manual_action_mode=manual_action_mode,
            )
            if choice == "force-accept":
                ledger.append_stage(
                    run_id=run_id, block_id=block_id, stage="qa", status="force_accepted",
                    provider="manual", metadata={"escalation": "force-accept"},
                )
                return True
            elif choice == "skip":
                ledger.append_stage(
                    run_id=run_id, block_id=block_id, stage="qa", status="skipped",
                    provider="manual", metadata={"escalation": "skip"},
                )
                return True
            elif choice == "inspect-and-retry":
                # One more manual retry beyond the limit
                retry_count -= 1
                continue
            else:
                return False

        # Re-refine with feedback
        print(f"[{run_id}]     QA failed, re-refining with feedback (retry {retry_count}).")
        current_refined, refine_provider_name = _run_refine_with_fallback_chain(
            config=config,
            ledger=ledger,
            run_id=run_id,
            block=block,
            literal_draft=literal_draft,
            glossary_subset=glossary_subset,
            style_key=style_key,
            input_hash=_sha256(str(literal_draft.to_dict())),
            retry_feedback=qa_report.feedback,
            failure_metadata={"retry_from_qa": retry_count},
        )
        repaired_text, glossary_repairs = _apply_glossary_rejected_variant_repairs(
            current_refined.refined_text,
            glossary_subset,
        )
        repaired_text, footnote_repairs = _apply_source_footnote_marker_repairs(
            repaired_text,
            block.source_text,
        )
        if glossary_repairs or footnote_repairs:
            current_refined = RefinedDraft(
                block_id=current_refined.block_id,
                chapter_id=current_refined.chapter_id,
                refined_text=repaired_text,
                provider=current_refined.provider,
                style_profile=current_refined.style_profile,
                source_text=current_refined.source_text,
                metadata={
                    **current_refined.metadata,
                    "glossary_rejected_variant_repairs": glossary_repairs,
                    "source_footnote_marker_repairs": footnote_repairs,
                },
            )
        _write_block_artifact(config, block.chapter_id, block_id, "refined", current_refined.to_dict())
        _commit_stage(
            ledger,
            run_id,
            block_id,
            "refining",
            "completed",
            provider=refine_provider_name,
            output_hash=_sha256(current_refined.refined_text),
            metadata={
                "retry_from_qa": retry_count,
                "glossary_rejected_variant_repairs": glossary_repairs,
                "source_footnote_marker_repairs": footnote_repairs,
            },
        )

    return False


def _qa_escalation_prompt(
    qa_report: QAReport,
    *,
    block_id: str | None = None,
    stage: str = "qa",
    manual_action_mode: str = "interactive",
) -> str:
    print()
    print("  === QA Hard Fail Escalation ===")
    print(f"  Findings: {len(qa_report.findings)}")
    for f in qa_report.findings:
        print(f"    - [{f.severity}] {f.code}: {f.message}")
    if manual_action_mode == "stop":
        scope = f"block {block_id}" if block_id else "the current block"
        raise ManualActionRequired(f"Manual action required for {scope} at stage '{stage}'.")
    print()
    print("  Options:")
    print("  1. force-accept  (accept the current refined text)")
    print("  2. skip          (skip this block entirely)")
    print("  3. inspect-and-retry  (one more manual retry)")
    while True:
        choice = input("  Choose [1-3]: ").strip()
        if choice == "1":
            return "force-accept"
        elif choice == "2":
            return "skip"
        elif choice == "3":
            return "inspect-and-retry"
        print("  Invalid choice. Please enter 1, 2, or 3.")


def _effective_resume_stop_chapter(until_chapter: str | None, until_block: str | None) -> str | None:
    candidates = [chapter for chapter in (until_chapter, _block_chapter_id(until_block) if until_block else None) if chapter]
    if not candidates:
        return None
    return min(candidates, key=_chapter_sort_key)


def resume_pipeline(
    *,
    config: AppConfig | None = None,
    run_id: str,
    force: bool = False,
    manual_action_mode: str = "interactive",
    until_chapter: str | None = None,
    until_block: str | None = None,
) -> PipelineContext:
    if config is None:
        config = load_app_config()
    ledger = RunLedger(config.ledger_path)
    state = ledger.load_state(run_id)

    if not state.records:
        raise ValueError(f"No records found for run_id={run_id}.")

    print(f"[{run_id}] Resuming from ledger state...")
    ctx = PipelineContext(
        config=config,
        ledger=ledger,
        prompt_store=PromptStore(config.workspace.prompts),
        run_id=run_id,
        force=force,
    )

    completed_blocks = state.completed_blocks()
    failed_blocks = state.failed_blocks()
    print(f"[{run_id}] Completed blocks: {len(completed_blocks)}, Failed blocks: {len(failed_blocks)}")

    # Determine chapter(s) to resume
    batch_chapter_ids = _get_batch_chapter_ids(config, run_id)
    if batch_chapter_ids is not None:
        # Batch resume
        glossary_index = _load_or_create_glossary_index(config)
        stop_chapter = _effective_resume_stop_chapter(until_chapter, until_block)
        until_block_chapter = _block_chapter_id(until_block) if until_block else None
        for chapter_id in batch_chapter_ids:
            if stop_chapter is not None and _chapter_sort_key(chapter_id) > _chapter_sort_key(stop_chapter):
                print(f"[{run_id}] Bounded resume stopping before chapter {chapter_id}; limit is {stop_chapter}.")
                break
            chapter_until_block = until_block if until_block_chapter == chapter_id else None
            stopped_early = _resume_chapter(
                config=config,
                ledger=ledger,
                run_id=run_id,
                chapter_id=chapter_id,
                glossary_index=glossary_index,
                state=state,
                force=force,
                manual_action_mode=manual_action_mode,
                until_block=chapter_until_block,
            )
            if stopped_early:
                break
            if stop_chapter is not None and chapter_id == stop_chapter:
                print(f"[{run_id}] Bounded resume stopped after chapter {chapter_id}.")
                break
        # Return a dummy context (last chapter's context would be lost, but fine)
        return PipelineContext(
            config=config,
            ledger=ledger,
            prompt_store=PromptStore(config.workspace.prompts),
            run_id=run_id,
            force=force,
        )

    # Single-chapter resume (original logic)
    chapter_id = _extract_chapter_id(state)
    if until_chapter is not None and until_chapter != chapter_id:
        raise ValueError(
            f"Single-chapter resume for chapter '{chapter_id}' cannot use --until-chapter '{until_chapter}'."
        )
    if until_block is not None and _block_chapter_id(until_block) != chapter_id:
        raise ValueError(
            f"Single-chapter resume for chapter '{chapter_id}' cannot use --until-block '{until_block}'."
        )
    source_path = config.workspace.raw / chapter_id / "source.json"
    raw_text = read_text_if_exists(source_path)
    if raw_text is None:
        raise ValueError(f"No fetched source found at {source_path} for run={run_id}.")
    raw_source = json.loads(raw_text)
    ctx.chapter_source = ChapterSource(
        novel_id=raw_source.get("novel_id", config.novel_id),
        chapter_id=raw_source.get("chapter_id", chapter_id),
        title=raw_source.get("title", ""),
        source_language=raw_source.get("source_language", config.source_language),
        raw_text=raw_source.get("raw_text", ""),
    )

    blocks = split_blocks(
        chapter_id=chapter_id,
        text=ctx.chapter_source.raw_text,
        source_language=config.source_language,
        zh_limit=config.chunking.chinese_character_limit,
        non_zh_limit=config.chunking.non_chinese_word_limit,
    )
    ctx.blocks = blocks

    # Reload glossary index
    ctx.glossary_index = _load_or_create_glossary_index(config)
    stop_block_key = _block_sort_key(until_block) if until_block else None

    # Resume chapter-level stages if not yet committed
    if not ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="glossary_scanned"):
        print(f"[{run_id}] Resuming: glossary pre-scan")
        queue_items = build_glossary_scan_queue(config, blocks)
        _write_glossary_scan_artifact(config, chapter_id=chapter_id, items=queue_items)
        ctx.glossary_index = _load_glossary_index_from_queue(config, queue_items)
        _commit_stage(ledger, run_id, chapter_id, "glossary_scanned", "completed", provider="local")

    if not ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="glossary_approved"):
        print(f"[{run_id}] Resuming: glossary approval")
        queue_artifact = _read_glossary_scan_artifact(config, chapter_id=chapter_id)
        if queue_artifact is None:
            queue_items = build_glossary_scan_queue(config, blocks)
            _write_glossary_scan_artifact(config, chapter_id=chapter_id, items=queue_items)
        else:
            queue_items = _read_glossary_scan_items(config, chapter_id=chapter_id)
        queue_items, removed_terms = _revalidate_glossary_queue_items(config, blocks, queue_items)
        if removed_terms:
            _write_glossary_scan_artifact(config, chapter_id=chapter_id, items=queue_items)
            print(f"[{run_id}]   glossary approval revalidated queue; removed {len(removed_terms)} stale/noisy terms.")
        ctx.glossary_index = _load_glossary_index_from_queue(config, queue_items)

        template_text = read_text_if_exists(config.workspace.templates_dir / "Term-Template.md")
        if template_text is None:
            template_text = _default_term_template()
        pending_terms = _pending_terms_from_queue(ctx.glossary_index, queue_items)
        if pending_terms:
            print(f"[{run_id}]   {len(pending_terms)} terms pending approval.")
            provider_runner = _provider_runner_for_stage(config, "term_suggestion")
            queue_by_term = _queue_item_index(queue_items)
            for term_key in pending_terms:
                entry = ctx.glossary_index.get(term_key)
                if entry is None or entry.status == "approved":
                    continue
                queue_item = queue_by_term.get(term_key, {})
                context_text = str(queue_item.get("context", ""))
                suggestion = build_term_suggestion(
                    config=config,
                    provider_runner=provider_runner,
                    prompt_store=ctx.prompt_store,
                    term=term_key,
                    context=context_text,
                )
                thai_term = choose_option_interactively(suggestion)
                entry.thai_term = thai_term
                entry.status = "approved"
                entry.description = suggestion.rationale
                entry.source_language = config.source_language
                entry.novel = config.novel_id
                write_glossary_note(
                    template_text=template_text,
                    glossary_dir=config.workspace.glossary_dir,
                    entry=entry,
                    first_seen_chapter=chapter_id,
                    first_seen_block=str(queue_item.get("first_seen_block", "block-001")),
                )
                ctx.glossary_index[term_key] = entry
        _commit_stage(ledger, run_id, chapter_id, "glossary_approved", "completed", provider="local")

    formatted_blocks: list[str] = []
    stopped_early = False
    found_stop_block = False
    for block in blocks:
        if stop_block_key is not None and _block_sort_key(block.block_id) > stop_block_key:
            print(f"[{run_id}] Bounded resume stopping before block {block.block_id}; limit is {until_block}.")
            stopped_early = True
            break
        is_bound_block = until_block is not None and block.block_id == until_block
        next_stage = state.next_pending_stage(block.block_id, BLOCK_STAGE_ORDER)
        if force:
            print(f"[{run_id}] Block {block.block_id}: force rerun requested.")
            formatted_text = _process_block(
                ctx,
                block,
                config.default_style_profile,
                force=True,
                manual_action_mode=manual_action_mode,
            )
            if formatted_text is not None:
                formatted_blocks.append(formatted_text)
            if is_bound_block:
                print(f"[{run_id}] Bounded resume stopped after block {until_block}.")
                stopped_early = True
                found_stop_block = True
                break
            continue
        if next_stage is None:
            print(f"[{run_id}] Block {block.block_id}: all stages completed, loading cached output.")
            cached = _read_block_artifact(config, chapter_id, block.block_id, "formatted")
            if cached is not None:
                formatted_blocks.append(cached.get("text", ""))
            if is_bound_block:
                print(f"[{run_id}] Bounded resume stopped after block {until_block}.")
                stopped_early = True
                found_stop_block = True
                break
            continue

        print(f"[{run_id}] Block {block.block_id}: resuming from stage '{next_stage}'.")
        formatted_text = _process_block(
            ctx,
            block,
            config.default_style_profile,
            force=force,
            manual_action_mode=manual_action_mode,
        )
        if formatted_text is not None:
            formatted_blocks.append(formatted_text)
        if is_bound_block:
            print(f"[{run_id}] Bounded resume stopped after block {until_block}.")
            stopped_early = True
            found_stop_block = True
            break

    if until_block is not None and not found_stop_block:
        raise ValueError(f"Bounded block '{until_block}' was not found in chapter '{chapter_id}'.")

    if formatted_blocks:
        _write_chapter_output_with_sentinel_gate(config, ledger, run_id, chapter_id, formatted_blocks, ctx.chapter_source)

    print(f"[{run_id}] Resume completed.")
    return ctx


def rerun_block_pipeline(
    *,
    config: AppConfig | None = None,
    run_id: str,
    block_id: str,
    from_stage: str,
    style_profile: str | None = None,
) -> PipelineContext:
    """Rerun one block from a selected block stage and reuse cached upstream artifacts."""
    if config is None:
        config = load_app_config()
    ledger = RunLedger(config.ledger_path)
    state = ledger.load_state(run_id)
    if not state.records:
        raise ValueError(f"No records found for run_id={run_id}.")

    normalized_stage = _normalize_block_stage(from_stage)
    chapter_id = block_id.rsplit("-block-", 1)[0] if "-block-" in block_id else _extract_chapter_id(state)
    source_path = config.workspace.raw / chapter_id / "source.json"
    raw_text = read_text_if_exists(source_path)
    if raw_text is None:
        raise ValueError(f"No fetched source found at {source_path} for run={run_id}.")
    raw_source = json.loads(raw_text)
    chapter_source = ChapterSource(
        novel_id=raw_source.get("novel_id", config.novel_id),
        chapter_id=raw_source.get("chapter_id", chapter_id),
        title=raw_source.get("title", ""),
        source_language=raw_source.get("source_language", config.source_language),
        raw_text=raw_source.get("raw_text", ""),
    )
    blocks = split_blocks(
        chapter_id=chapter_id,
        text=chapter_source.raw_text,
        source_language=config.source_language,
        zh_limit=config.chunking.chinese_character_limit,
        non_zh_limit=config.chunking.non_chinese_word_limit,
    )
    target_block = next((block for block in blocks if block.block_id == block_id), None)
    if target_block is None:
        raise ValueError(f"Block '{block_id}' was not found in chapter '{chapter_id}'.")

    ctx = PipelineContext(
        config=config,
        ledger=ledger,
        prompt_store=PromptStore(config.workspace.prompts),
        run_id=run_id,
        blocks=blocks,
        glossary_index=_load_or_create_glossary_index(config),
        chapter_source=chapter_source,
        force=False,
    )

    print(f"[{run_id}] Rerunning {block_id} from stage '{normalized_stage}'.")
    formatted_text = _process_block(
        ctx,
        target_block,
        style_profile or config.default_style_profile,
        force_from_stage=normalized_stage,
    )

    if formatted_text is not None:
        formatted_blocks: list[str] = []
        missing: list[str] = []
        for block in blocks:
            cached = _read_block_artifact(config, chapter_id, block.block_id, "formatted")
            if cached is None:
                missing.append(block.block_id)
                continue
            formatted_blocks.append(str(cached.get("text", "")))
        if missing:
            print(f"[{run_id}] Rerun complete. Final chapter output not rewritten; missing formatted blocks: {', '.join(missing)}")
        else:
            _write_chapter_output_with_sentinel_gate(config, ledger, run_id, chapter_id, formatted_blocks, chapter_source)
            print(f"[{run_id}] Rerun complete. Final chapter output rewritten.")
    return ctx


def scan_terms_command(
    *,
    config: AppConfig,
    chapter_id: str,
    run_id: str | None = None,
    force: bool = False,
) -> Path:
    chapter_source, blocks = _load_chapter_source_and_blocks(config, chapter_id)
    ledger = RunLedger(config.ledger_path)
    if run_id and ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="glossary_scanned") and not force:
        print(f"[{run_id}] glossary scan already committed, skipping. Use --force to rescan.")
        return _glossary_scan_path(config, chapter_id=chapter_id)
    queue_items = build_glossary_scan_queue(config, blocks)
    path = _write_glossary_scan_artifact(config, chapter_id=chapter_id, items=queue_items)
    if run_id:
        _commit_stage(ledger, run_id, chapter_id, "glossary_scanned", "completed", provider="local")
    print(f"[scan-terms] {chapter_source.chapter_id}: {len(queue_items)} candidate terms -> {path}")
    return path


def approve_terms_command(
    *,
    config: AppConfig,
    chapter_id: str | None,
    run_id: str | None = None,
    force: bool = False,
    batch: bool = False,
    decision_report: str = "",
) -> int:
    ledger = RunLedger(config.ledger_path)
    if batch:
        if not run_id:
            raise ValueError("--run-id is required for batch glossary approval.")
        artifact = _read_glossary_scan_artifact(config, run_id=run_id)
        if artifact is None:
            raise ValueError(f"Missing batch glossary scan artifact for run_id={run_id}.")
        chapter_ids = artifact.get("chapter_ids")
        if not isinstance(chapter_ids, list) or not all(isinstance(item, str) for item in chapter_ids):
            raise ValueError(f"Batch glossary scan artifact for {run_id} is missing chapter_ids.")
        committed = 0
        for batch_chapter_id in chapter_ids:
            if ledger.has_committed(run_id=run_id, block_id=batch_chapter_id, stage="glossary_approved") and not force:
                continue
            _commit_stage(
                ledger,
                run_id,
                batch_chapter_id,
                "glossary_approved",
                "completed",
                provider="local",
                metadata={
                    "approval_mode": "reviewed_batch_gate",
                    "decision_report": decision_report,
                },
            )
            committed += 1
        print(f"[approve-terms] {run_id}: committed glossary_approved for {committed}/{len(chapter_ids)} batch chapters.")
        return committed

    if not chapter_id:
        raise ValueError("--chapter-id is required unless --batch is used.")
    if run_id and ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="glossary_approved") and not force:
        print(f"[{run_id}] glossary approval already committed, skipping. Use --force to re-check queue.")
        return 0
    queue_items = _read_glossary_scan_items(config, chapter_id=chapter_id)
    if not queue_items:
        _, blocks = _load_chapter_source_and_blocks(config, chapter_id)
        queue_items = build_glossary_scan_queue(config, blocks)
        _write_glossary_scan_artifact(config, chapter_id=chapter_id, items=queue_items)
    else:
        _, blocks = _load_chapter_source_and_blocks(config, chapter_id)
    queue_items, removed_terms = _revalidate_glossary_queue_items(config, blocks, queue_items)
    if removed_terms:
        _write_glossary_scan_artifact(config, chapter_id=chapter_id, items=queue_items)
        print(f"[{run_id}] glossary approval revalidated queue; removed {len(removed_terms)} stale/noisy terms.")
    glossary_index = _load_glossary_index_from_queue(config, queue_items)
    pending_terms = _pending_terms_from_queue(glossary_index, queue_items)
    template_text = read_text_if_exists(config.workspace.templates_dir / "Term-Template.md") or _default_term_template()
    provider_runner = _provider_runner_for_stage(config, "term_suggestion")
    queue_by_term = _queue_item_index(queue_items)
    for term_key in pending_terms:
        entry = glossary_index.get(term_key)
        if entry is None or entry.status == "approved":
            continue
        queue_item = queue_by_term.get(term_key, {})
        suggestion = build_term_suggestion(
            config=config,
            provider_runner=provider_runner,
            prompt_store=PromptStore(config.workspace.prompts),
            term=term_key,
            context=str(queue_item.get("context", "")),
        )
        thai_term = choose_option_interactively(suggestion)
        entry.thai_term = thai_term
        entry.status = "approved"
        entry.description = suggestion.rationale
        entry.source_language = config.source_language
        entry.novel = config.novel_id
        write_glossary_note(
            template_text=template_text,
            glossary_dir=config.workspace.glossary_dir,
            entry=entry,
            first_seen_chapter=chapter_id,
            first_seen_block=str(queue_item.get("first_seen_block", "block-001")),
        )
        glossary_index[term_key] = entry
    if run_id:
        _commit_stage(ledger, run_id, chapter_id, "glossary_approved", "completed", provider="local")
    print(f"[approve-terms] {chapter_id}: approved gate complete ({len(pending_terms)} pending terms checked).")
    return len(pending_terms)


def translate_literal_command(
    *,
    config: AppConfig,
    chapter_id: str,
    block_id: str,
    run_id: str | None = None,
    force: bool = False,
) -> Path:
    _, blocks = _load_chapter_source_and_blocks(config, chapter_id)
    block = _find_block(blocks, block_id)
    ledger = RunLedger(config.ledger_path)
    if run_id and ledger.has_committed(run_id=run_id, block_id=block_id, stage="translating") and not force:
        print(f"[{run_id}] {block_id} translating already committed, skipping. Use --force to rerun.")
        return _artifact_block_path(config, chapter_id, block_id, "literal")
    glossary_subset = _resolve_glossary_subset([block], _load_or_create_glossary_index(config))
    draft, provider_name = _run_literal_with_fallback_chain(
        config=config,
        ledger=ledger,
        run_id=run_id or "",
        block=block,
        glossary_subset=glossary_subset,
        input_hash=_sha256(block.source_text),
        commit_failures=bool(run_id),
    )
    path = _write_block_artifact(config, chapter_id, block_id, "literal", draft.to_dict())
    if run_id:
        _commit_stage(ledger, run_id, block_id, "translating", "completed", provider=provider_name, output_hash=_sha256(str(draft.to_dict())))
    print(f"[translate-literal] {block_id}: {path}")
    return path


def refine_command(
    *,
    config: AppConfig,
    chapter_id: str,
    block_id: str,
    run_id: str | None = None,
    style_profile: str | None = None,
    force: bool = False,
) -> Path:
    _, blocks = _load_chapter_source_and_blocks(config, chapter_id)
    block = _find_block(blocks, block_id)
    cached = _read_block_artifact(config, chapter_id, block_id, "literal")
    if cached is None:
        raise ValueError(f"Missing literal artifact for {block_id}. Run translate-literal first.")
    literal_draft = _reconstruct_literal_draft(cached, block_id, chapter_id)
    ledger = RunLedger(config.ledger_path)
    if run_id and ledger.has_committed(run_id=run_id, block_id=block_id, stage="refining") and not force:
        print(f"[{run_id}] {block_id} refining already committed, skipping. Use --force to rerun.")
        return _artifact_block_path(config, chapter_id, block_id, "refined")
    glossary_subset = _resolve_glossary_subset([block], _load_or_create_glossary_index(config))
    draft, refine_provider_name = _run_refine_with_fallback_chain(
        config=config,
        ledger=ledger,
        run_id=run_id or f"manual-{chapter_id}",
        block=block,
        literal_draft=literal_draft,
        glossary_subset=glossary_subset,
        style_key=style_profile or config.default_style_profile,
        input_hash=_sha256(str(literal_draft.to_dict())),
        commit_failures=bool(run_id),
    )
    path = _write_block_artifact(config, chapter_id, block_id, "refined", draft.to_dict())
    if run_id:
        _commit_stage(ledger, run_id, block_id, "refining", "completed", provider=refine_provider_name, output_hash=_sha256(draft.refined_text))
    print(f"[refine] {block_id}: {path}")
    return path


def qa_command(
    *,
    config: AppConfig,
    chapter_id: str,
    block_id: str,
    run_id: str | None = None,
    style_profile: str | None = None,
    auto_refine: bool = True,
    force_accept_current: bool = False,
    force_accept_reason: str = "",
) -> Path:
    chapter_source, blocks = _load_chapter_source_and_blocks(config, chapter_id)
    block = _find_block(blocks, block_id)
    literal_cached = _read_block_artifact(config, chapter_id, block_id, "literal")
    refined_cached = _read_block_artifact(config, chapter_id, block_id, "refined")
    if literal_cached is None or refined_cached is None:
        raise ValueError(f"Missing literal/refined artifacts for {block_id}.")
    ctx = PipelineContext(
        config=config,
        ledger=RunLedger(config.ledger_path),
        prompt_store=PromptStore(config.workspace.prompts),
        run_id=run_id or f"manual-{chapter_id}",
        blocks=blocks,
        glossary_index=_load_or_create_glossary_index(config),
        chapter_source=chapter_source,
    )
    literal_draft = _reconstruct_literal_draft(literal_cached, block_id, chapter_id)
    refined_draft = _reconstruct_refined_draft(refined_cached, block_id, chapter_id)
    glossary_subset = _resolve_glossary_subset([block], ctx.glossary_index)
    if force_accept_current:
        if not force_accept_reason.strip():
            raise ValueError("--reason is required with --force-accept-current.")
        ctx.ledger.append_stage(
            run_id=ctx.run_id,
            block_id=block_id,
            stage="qa",
            status="force_accepted",
            provider="manual",
            metadata={
                "escalation": "force-accept-current",
                "reason": force_accept_reason.strip(),
                "refined_hash": _sha256(refined_draft.refined_text),
            },
        )
        path = _artifact_block_path(config, chapter_id, block_id, "qa")
        print(f"[qa] {block_id}: force_accepted current refined artifact -> {path}")
        return path
    passed = _run_qa_with_retries(
        ctx=ctx,
        block=block,
        literal_draft=literal_draft,
        refined_draft=refined_draft,
        glossary_subset=glossary_subset,
        style_key=style_profile or config.default_style_profile,
        auto_refine=auto_refine,
    )
    if not passed:
        raise RuntimeError(f"QA failed for {block_id}.")
    path = _artifact_block_path(config, chapter_id, block_id, "qa")
    print(f"[qa] {block_id}: {path}")
    return path


def format_command(
    *,
    config: AppConfig,
    chapter_id: str,
    block_id: str,
    run_id: str | None = None,
    force: bool = False,
) -> Path:
    refined_cached = _read_block_artifact(config, chapter_id, block_id, "refined")
    if refined_cached is None:
        raise ValueError(f"Missing refined artifact for {block_id}. Run refine first.")
    ledger = RunLedger(config.ledger_path)
    if run_id and ledger.has_committed(run_id=run_id, block_id=block_id, stage="formatting") and not force:
        cached = _read_block_artifact(config, chapter_id, block_id, "formatted")
        if cached is None:
            raise ValueError(f"Missing formatted artifact for {block_id}.")
        cached_text = str(cached.get("text", ""))
        validation_issues = validate_formatted_text(cached_text)
        if validation_issues:
            _commit_stage(
                ledger,
                run_id,
                block_id,
                "formatting",
                "failed",
                provider="local",
                metadata={"validation_issues": validation_issues},
            )
            raise ValueError(f"Formatted text validation failed for {block_id}: {'; '.join(validation_issues)}")
        print(f"[{run_id}] {block_id} formatting already committed, skipping. Use --force to rerun.")
        return _artifact_block_path(config, chapter_id, block_id, "formatted")
    refined_draft = _reconstruct_refined_draft(refined_cached, block_id, chapter_id)
    formatted_text, formatter_provider, formatter_metadata = _format_block_with_hybrid_provider(
        config=config,
        prompt_store=PromptStore(config.workspace.prompts),
        refined_text=refined_draft.refined_text,
    )
    validation_issues = validate_formatted_text(formatted_text, source_text=refined_draft.refined_text)
    if validation_issues:
        if run_id:
            _commit_stage(
                ledger,
                run_id,
                block_id,
                "formatting",
                "failed",
                provider=formatter_provider,
                metadata={**formatter_metadata, "validation_issues": validation_issues},
            )
        raise ValueError(f"Formatted text validation failed for {block_id}: {'; '.join(validation_issues)}")
    path = _write_block_artifact(config, chapter_id, block_id, "formatted", {"text": formatted_text})
    if run_id:
        _commit_stage(
            ledger,
            run_id,
            block_id,
            "formatting",
            "completed",
            provider=formatter_provider,
            output_hash=_sha256(formatted_text),
            metadata=formatter_metadata,
        )
        _commit_stage(ledger, run_id, block_id, "completed", "completed", provider="local")
    print(f"[format] {block_id}: {path}")
    return path


def status_run(
    *,
    config: AppConfig | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    if config is None:
        config = load_app_config()
    ledger = RunLedger(config.ledger_path)

    if not ledger.path.exists():
        print("No ledger found. No runs recorded.")
        return {"runs": []}

    if run_id is not None:
        state = ledger.load_state(run_id)
        block_stage_status = {}
        for block_id in sorted(key for key in state.records_by_block if "-block-" in key):
            block_stage_status[block_id] = {
                "next_pending_stage": state.next_pending_stage(block_id, BLOCK_STAGE_ORDER),
                "records": [record.to_dict() for record in state.records_for_block(block_id)],
            }

        # Determine chapter IDs
        batch_chapter_ids = _get_batch_chapter_ids(config, run_id)
        if batch_chapter_ids is not None:
            chapter_ids = batch_chapter_ids
        else:
            # Infer from block IDs, including chapter-level records (e.g., "ch004")
            chapter_candidates = set()
            for block_id in state.records_by_block:
                if "-block-" in block_id:
                    chapter_candidates.add(block_id.split("-block-")[0])
                elif re.match(r"^ch\d+$", block_id):
                    chapter_candidates.add(block_id)
            chapter_ids = sorted(chapter_candidates)
        # Determine if we have any block-level records
        has_block_records = any("-block-" in block_id for block_id in state.records_by_block)

        # Determine if we are in fetched-only pre-batch-artifact state
        # This includes runs that have only fetched, or fetched + glossary_scanned but not glossary_approved
        is_fetched_only_pre_batch = (
            batch_chapter_ids is None
            and not has_block_records
            and chapter_ids
        )

        completed_block_set = set(state.completed_blocks())
        failed_block_set = set(state.failed_blocks())

        chapter_summary = {}
        all_expected_block_ids = set()
        for chapter_id in chapter_ids:
            source_available = False
            expected_block_ids = []
            warning = None
            try:
                _, blocks = _load_chapter_source_and_blocks(config, chapter_id)
                source_available = True
                expected_block_ids = [block.block_id for block in blocks]
                expected_blocks = len(blocks)
            except Exception:
                # Fallback: count block IDs for this chapter in ledger
                expected_blocks = sum(
                    1 for block_id in state.records_by_block
                    if block_id.startswith(chapter_id + "-block-")
                )
                warning = "source.json missing; expected blocks inferred from ledger only"
                source_available = False

            ledger_block_ids = [
                bid for bid in state.records_by_block
                if bid.startswith(chapter_id + "-block-")
            ]
            all_block_ids = sorted(set(expected_block_ids + ledger_block_ids))
            all_expected_block_ids.update(expected_block_ids)

            completed = [bid for bid in all_block_ids if bid in completed_block_set]
            failed = [bid for bid in all_block_ids if bid in failed_block_set]
            pending = [
                bid for bid in all_block_ids
                if bid not in completed_block_set and bid not in failed_block_set
            ]
            pending_stages = {}
            for bid in pending:
                stage = state.next_pending_stage(bid, BLOCK_STAGE_ORDER)
                pending_stages[bid] = stage if stage is not None else "unknown"
            # If fetched-only pre-batch, clear block-level pending and set batch pending stage
            if is_fetched_only_pre_batch:
                pending = []
                pending_stages = {}
                # Check if glossary_scanned is committed but glossary_approved is not
                has_glossary_scanned = state.committed(chapter_id, "glossary_scanned", "completed")
                has_glossary_approved = state.committed(chapter_id, "glossary_approved", "completed")
                
                if has_glossary_scanned and not has_glossary_approved:
                    # Run was stopped after glossary scan, manual approval required
                    batch_pending_stage = "glossary_approval"
                    manual_action_required = True
                else:
                    # Only fetched, glossary scan not yet done
                    batch_pending_stage = "glossary_scanned"
                    manual_action_required = False

            # Output path
            output_path = _output_chapter_path(config, chapter_id) / f"{chapter_id}.md"
            output_exists = output_path.exists()
            chapter_data = {
                "expected_blocks": expected_blocks,
                "expected_block_ids": expected_block_ids,
                "source_available": source_available,
                "warning": warning,
                "completed_blocks": len(completed),
                "failed_blocks": failed,
                "pending_blocks": pending,
                "pending_stages": pending_stages,
                "output_path": str(output_path),
                "output_exists": output_exists,
            }
            if is_fetched_only_pre_batch:
                chapter_data["batch_pending_stage"] = batch_pending_stage
                chapter_data["manual_action_required"] = manual_action_required
                # Add batch glossary artifact path if manual action required
                if manual_action_required:
                    batch_artifact_path = batch_glossary_scan_artifact_path(config.workspace.work, run_id)
                    chapter_data["batch_glossary_artifact"] = str(batch_artifact_path)
                    chapter_data["batch_glossary_artifact_exists"] = batch_artifact_path.exists()
            chapter_summary[chapter_id] = chapter_data

        # Add missing expected blocks to block_stage_status (skip if fetched-only pre-batch)
        if not is_fetched_only_pre_batch:
            for block_id in all_expected_block_ids:
                if block_id not in block_stage_status:
                    next_stage = state.next_pending_stage(block_id, BLOCK_STAGE_ORDER)
                    block_stage_status[block_id] = {
                        "next_pending_stage": next_stage,
                        "records": [],
                    }

        # Provider usage
        provider_usage = {}
        for record in state.records:
            provider = record.provider or "local"
            stage = record.stage
            status = record.status
            provider_usage.setdefault(provider, {}).setdefault(stage, {}).setdefault(status, 0)
            provider_usage[provider][stage][status] += 1

        # Manual actions needed
        manual_actions = []
        if state.failed_blocks():
            manual_actions.append("inspect failed blocks and rerun from the appropriate stage.")
        pending_blocks = [
            bid for bid, details in block_stage_status.items()
            if details["next_pending_stage"] is not None
        ]
        if pending_blocks:
            manual_actions.append(f"resume --run-id {run_id}.")
        # If no batch artifact and no block records, suggest run --range
        if batch_chapter_ids is None and not has_block_records and chapter_ids:
            first = chapter_ids[0]
            last = chapter_ids[-1]
            manual_actions.append(f"run --range {first}-{last} --run-id {run_id} --stop-after glossary-scan")
        # Check missing outputs
        for chapter_id, summary in chapter_summary.items():
            if (
                not is_fetched_only_pre_batch
                and summary["expected_blocks"] > 0
                and summary["completed_blocks"] == summary["expected_blocks"]
                and not summary["output_exists"]
            ):
                manual_actions.append(f"rerun formatting/final assembly for {chapter_id}.")
        if not manual_actions:
            manual_actions.append("none")

        historical_failed_records = sum(1 for record in state.records if record.status in {"failed", "hard_fail"})
        current_failed_blocks = state.failed_blocks()
        next_effective_action = "none" if manual_actions == ["none"] else manual_actions[0]

        result = {
            "run_id": run_id,
            "total_records": len(state.records),
            "completed_blocks": state.completed_blocks(),
            "failed_blocks": current_failed_blocks,
            "current_failed_blocks": current_failed_blocks,
            "historical_failed_records": historical_failed_records,
            "next_effective_action": next_effective_action,
            "block_stage_status": block_stage_status,
            "latest_by_block": {
                bid: rec.to_dict() for bid, rec in state.latest_by_block.items()
            },
            "chapter_ids": chapter_ids,
            "chapter_summary": chapter_summary,
            "provider_usage": provider_usage,
            "manual_actions": manual_actions,
        }
        print(f"Run {run_id}:")
        print(f"  Records: {len(state.records)}")
        print(f"  Completed blocks: {', '.join(state.completed_blocks()) or 'none'}")
        print(f"  Current failed blocks: {', '.join(current_failed_blocks) or 'none'}")
        print(f"  Failed blocks: {', '.join(current_failed_blocks) or 'none'}")
        print(f"  Historical failed records: {historical_failed_records}")
        print(f"  Next effective action: {next_effective_action}")

        # Chapter summary
        if chapter_ids:
            print("  Chapter summary:")
            for chapter_id in chapter_ids:
                summary = chapter_summary[chapter_id]
                print(f"    Chapter {chapter_id}:")
                print(f"      Blocks: {summary['completed_blocks']}/{summary['expected_blocks']} complete")
                if summary.get('warning'):
                    print(f"      Warning: {summary['warning']}")
                if 'batch_pending_stage' in summary:
                    print(f"      Pending batch stage: {summary['batch_pending_stage']}")
                    if summary.get('manual_action_required'):
                        print(f"      Manual action required: Yes")
                    if summary.get('batch_glossary_artifact'):
                        artifact_exists = summary.get('batch_glossary_artifact_exists', False)
                        print(f"      Batch glossary artifact: {summary['batch_glossary_artifact']} ({'exists' if artifact_exists else 'missing'})")
                elif summary['pending_blocks']:
                    pending_str = ', '.join(
                        f"{bid} ({summary['pending_stages'].get(bid, '?')})"
                        for bid in summary['pending_blocks']
                    )
                    print(f"      Pending: {pending_str}")
                if summary['failed_blocks']:
                    print(f"      Failed: {', '.join(summary['failed_blocks'])}")
                output_exists = summary['output_exists']
                print(f"      Output: {summary['output_path']} {'exists' if output_exists else 'missing'}")

        # Provider usage
        print("  Provider usage:")
        for provider, stages in sorted(provider_usage.items()):
            print(f"    {provider}:")
            for stage, status_counts in sorted(stages.items()):
                counts_str = ', '.join(f"{status}: {count}" for status, count in sorted(status_counts.items()))
                print(f"      {stage}: {counts_str}")
        print("  Note: provider usage is historical ledger data and may include retries or records from older routing policy.")

        # Manual actions needed
        print(f"  Manual actions needed: {'; '.join(manual_actions)}")

        for block_id, details in block_stage_status.items():
            next_stage = details["next_pending_stage"]
            print(f"  {block_id}: {'complete' if next_stage is None else 'pending ' + next_stage}")
        return result

    # Show all runs
    all_runs: dict[str, list[RunRecord]] = {}
    for record in ledger.iter_records():
        all_runs.setdefault(record.run_id, []).append(record)

    result = {"runs": []}
    for rid, records in all_runs.items():
        run_status = {
            "run_id": rid,
            "record_count": len(records),
            "blocks": list(set(r.block_id for r in records)),
        }
        result["runs"].append(run_status)
        print(f"Run {rid}: {len(records)} records, {len(run_status['blocks'])} blocks")

    return result


def inspect_block_command(
    *,
    config: AppConfig,
    run_id: str,
    block_id: str,
) -> dict[str, Any]:
    ledger = RunLedger(config.ledger_path)
    state = ledger.load_state(run_id)
    chapter_id = _block_chapter_id(block_id)
    records = [record.to_dict() for record in state.records_for_block(block_id)]
    latest_by_stage = {
        stage: record.to_dict()
        for (record_block_id, stage), record in state.latest_by_stage.items()
        if record_block_id == block_id
    }
    source_path = str(config.workspace.raw / chapter_id / "source.json")
    artifact_paths = {"source": source_path}
    artifact_paths.update(
        {
            stage: str(_artifact_block_path(config, chapter_id, block_id, stage))
            for stage in ("literal", "refined", "qa", "formatted")
        }
    )
    artifact_exists = {stage: Path(path).exists() for stage, path in artifact_paths.items()}

    formatted_validation_issues: list[str] = []
    if artifact_exists["formatted"]:
        formatted_raw = read_text_if_exists(Path(artifact_paths["formatted"]))
        if formatted_raw is None:
            formatted_validation_issues.append("formatted artifact exists but could not be read")
        else:
            try:
                formatted_data = json.loads(formatted_raw)
            except json.JSONDecodeError as exc:
                formatted_validation_issues.append(f"formatted artifact JSON decode error: {exc}")
            else:
                if isinstance(formatted_data, dict):
                    formatted_text = formatted_data.get("text", "")
                    if isinstance(formatted_text, str):
                        formatted_validation_issues.extend(validate_formatted_text(formatted_text))
                    else:
                        formatted_validation_issues.append("formatted artifact missing text field")
                else:
                    formatted_validation_issues.append("formatted artifact is not a JSON object")

    next_pending_stage = state.next_pending_stage(block_id, BLOCK_STAGE_ORDER)
    result = {
        "run_id": run_id,
        "block_id": block_id,
        "chapter_id": chapter_id,
        "artifact_paths": artifact_paths,
        "artifact_exists": artifact_exists,
        "records": records,
        "latest_by_stage": latest_by_stage,
        "next_pending_stage": next_pending_stage,
        "formatted_validation_issues": formatted_validation_issues,
    }

    print(f"Inspect block {block_id} in run {run_id}:")
    print(f"  Chapter: {chapter_id}")
    for stage in ("source", "literal", "refined", "qa", "formatted"):
        exists = "exists" if artifact_exists[stage] else "missing"
        print(f"  {stage}: {artifact_paths[stage]} ({exists})")
    print(f"  Next pending stage: {next_pending_stage or 'none'}")
    if formatted_validation_issues:
        print(f"  Formatted validation issues: {'; '.join(formatted_validation_issues)}")
    else:
        print("  Formatted validation issues: none")
    print(f"  Ledger records: {len(records)}")
    return result


def run_batch_pipeline(
    *,
    config: AppConfig,
    chapter_ids: list[str],
    title_prefix: str = "",
    input_dir: Path | None = None,
    style_profile: str | None = None,
    run_id: str | None = None,
    force: bool = False,
    stop_after: str | None = None,
    manual_action_mode: str = "interactive",
) -> list[PipelineContext]:
    """Run the pipeline across multiple chapters with batch glossary approval. If stop_after is 'glossary-scan', stops after glossary pre-scan and returns empty list."""
    if run_id is None:
        import uuid
        run_id = f"run-{uuid.uuid4().hex[:8]}"

    ledger = RunLedger(config.ledger_path)
    config.workspace.logs_dir.mkdir(parents=True, exist_ok=True)
    prompt_store = PromptStore(config.workspace.prompts)
    style_key = style_profile or config.default_style_profile

    # Phase 1: Fetch all chapters
    print(f"[{run_id}] Batch: Phase 1 — fetch")
    all_blocks: list[TextBlock] = []
    chapter_blocks: dict[str, list[TextBlock]] = {}
    chapter_sources: dict[str, ChapterSource] = {}

    # Resolve adapter if configured
    adapter = None
    manifest = None
    if config.source.adapter and not input_dir:
        from novel_pipeline.adapters import get_adapter
        from novel_pipeline.stages.fetch import load_or_build_manifest, resolve_chapter_meta
        adapter = get_adapter(config.source)
        manifest = load_or_build_manifest(config=config, adapter=adapter, force=force)

    for chapter_id in chapter_ids:
        print(f"[{run_id}]   Chapter: {chapter_id}")
        chapter_meta = None
        if adapter is not None and manifest is not None:
            from novel_pipeline.stages.fetch import resolve_chapter_meta
            chapter_meta = resolve_chapter_meta(manifest, chapter_id)

        if not ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="fetched"):
            input_file = (input_dir / f"{chapter_id}.txt") if input_dir else None
            chapter_source = run_fetch_stage(
                config=config,
                chapter_id=chapter_id,
                title="",
                input_file=input_file,
                text=None,
                adapter=adapter,
                chapter_meta=chapter_meta,
            )
            chapter_sources[chapter_id] = chapter_source
            ih = _sha256(chapter_source.raw_text)
            _commit_stage(ledger, run_id, chapter_id, "fetched", "completed", provider="local", input_hash=ih)
        else:
            print(f"[{run_id}]     already fetched, loading.")
            source_path = config.workspace.raw / chapter_id / "source.json"
            raw_text = read_text_if_exists(source_path)
            if raw_text is None:
                raise ValueError(f"No fetched source for {chapter_id}")
            raw_source = json.loads(raw_text)
            chapter_sources[chapter_id] = ChapterSource(
                novel_id=raw_source.get("novel_id", config.novel_id),
                chapter_id=raw_source.get("chapter_id", chapter_id),
                title=raw_source.get("title", ""),
                source_language=raw_source.get("source_language", config.source_language),
                raw_text=raw_source.get("raw_text", ""),
            )

        blocks = split_blocks(
            chapter_id=chapter_id,
            text=chapter_sources[chapter_id].raw_text,
            source_language=config.source_language,
            zh_limit=config.chunking.chinese_character_limit,
            non_zh_limit=config.chunking.non_chinese_word_limit,
        )
        chapter_blocks[chapter_id] = blocks
        all_blocks.extend(blocks)

    # Phase 2: Batch glossary scan
    print(f"[{run_id}] Batch: Phase 2 — glossary pre-scan")
    queue_items = build_glossary_scan_queue(config, all_blocks)
    print(f"[{run_id}]   {len(queue_items)} new candidate terms found.")
    _write_glossary_scan_artifact(
        config,
        run_id=run_id,
        items=queue_items,
        chapter_ids=chapter_ids,
    )
    glossary_index = _load_glossary_index_from_queue(config, queue_items)

    # Commit glossary_scanned for EACH chapter
    for chapter_id in chapter_ids:
        if not ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="glossary_scanned"):
            _commit_stage(ledger, run_id, chapter_id, "glossary_scanned", "completed", provider="local")

    # Stop after glossary scan if requested
    if stop_after == "glossary-scan":
        print(f"[{run_id}] Stop requested after glossary scan. Review batch glossary artifact before approval.")
        return []

    # Phase 3: Single glossary approval
    print(f"[{run_id}] Batch: Phase 3 — glossary approval")
    queue_artifact = _read_glossary_scan_artifact(config, run_id=run_id)
    if queue_artifact is None:
        queue_items = build_glossary_scan_queue(config, all_blocks)
        _write_glossary_scan_artifact(
            config,
            run_id=run_id,
            items=queue_items,
            chapter_ids=chapter_ids,
        )
    else:
        queue_items = _read_glossary_scan_items(config, run_id=run_id)
    queue_items, removed_terms = _revalidate_glossary_queue_items(config, all_blocks, queue_items)
    if removed_terms:
        _write_glossary_scan_artifact(
            config,
            run_id=run_id,
            items=queue_items,
            chapter_ids=chapter_ids,
        )
        print(f"[{run_id}]   glossary approval revalidated queue; removed {len(removed_terms)} stale/noisy terms.")
    glossary_index = _load_glossary_index_from_queue(config, queue_items)

    template_text = read_text_if_exists(config.workspace.templates_dir / "Term-Template.md")
    if template_text is None:
        template_text = _default_term_template()

    pending_terms = _pending_terms_from_queue(glossary_index, queue_items)
    if pending_terms:
        print(f"[{run_id}]   {len(pending_terms)} terms pending approval.")
        provider_runner = _provider_runner_for_stage(config, "term_suggestion")
        queue_by_term = _queue_item_index(queue_items)
        for term_key in pending_terms:
            entry = glossary_index.get(term_key)
            if entry is None or entry.status == "approved":
                continue
            queue_item = queue_by_term.get(term_key, {})
            context_text = str(queue_item.get("context", ""))
            suggestion = build_term_suggestion(
                config=config,
                provider_runner=provider_runner,
                prompt_store=prompt_store,
                term=term_key,
                context=context_text,
            )
            thai_term = choose_option_interactively(suggestion)
            entry.thai_term = thai_term
            entry.status = "approved"
            entry.description = suggestion.rationale
            entry.source_language = config.source_language
            entry.novel = config.novel_id
            write_glossary_note(
                template_text=template_text,
                glossary_dir=config.workspace.glossary_dir,
                entry=entry,
                first_seen_chapter=str(queue_item.get("chapter_id", chapter_ids[0])),
                first_seen_block=str(queue_item.get("first_seen_block", "block-001")),
            )
            glossary_index[term_key] = entry

    # Commit glossary_approved for EACH chapter
    for chapter_id in chapter_ids:
        if not ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="glossary_approved"):
            _commit_stage(ledger, run_id, chapter_id, "glossary_approved", "completed", provider="local")

    # Phase 4: Sequential chapter processing
    results: list[PipelineContext] = []
    for chapter_id in chapter_ids:
        print(f"[{run_id}] Chapter: {chapter_id}")
        blocks = chapter_blocks[chapter_id]
        if not blocks:
            print(f"[{run_id}]   No blocks, skipping.")
            continue

        ctx = PipelineContext(
            config=config,
            ledger=ledger,
            prompt_store=prompt_store,
            run_id=run_id,
            blocks=blocks,
            glossary_index=glossary_index,
            chapter_source=chapter_sources.get(chapter_id),
            force=force,
        )

        formatted_blocks: list[str] = []
        chapter_failed = False
        for block in blocks:
            print(f"[{run_id}]   Block: {block.block_id}")
            formatted_text = _process_block(
                ctx,
                block,
                style_key,
                force=force,
                manual_action_mode=manual_action_mode,
            )
            if formatted_text is not None:
                formatted_blocks.append(formatted_text)
            else:
                # Block failed (hard_fail + no skip/force)
                chapter_failed = True
                break

        if formatted_blocks:
            _write_chapter_output_with_sentinel_gate(config, ledger, run_id, chapter_id, formatted_blocks, ctx.chapter_source)

        if chapter_failed:
            print(f"[{run_id}]   Chapter {chapter_id} had a block failure.")
            if manual_action_mode == "stop":
                raise ManualActionRequired(
                    f"Manual action required for chapter {chapter_id} during batch processing."
                )
            choice = _batch_chapter_failure_prompt(chapter_id, manual_action_mode=manual_action_mode)
            if choice == "stop":
                print(f"[{run_id}] Batch stopped by user at chapter {chapter_id}.")
                break
            # "continue" — proceed to next chapter
        else:
            print(f"[{run_id}]   Chapter {chapter_id} completed.")

        results.append(ctx)

    print(f"[{run_id}] Batch pipeline completed for {len(results)} chapters.")
    return results


def _batch_chapter_failure_prompt(chapter_id: str, *, manual_action_mode: str = "interactive") -> str:
    if manual_action_mode == "stop":
        raise ManualActionRequired(f"Manual action required for chapter {chapter_id} during batch processing.")
    print()
    print(f"  === Chapter {chapter_id} Failed ===")
    print("  Options:")
    print("  1. continue  (skip this chapter, continue to next)")
    print("  2. stop      (stop the entire batch run)")
    while True:
        choice = input("  Choose [1-2]: ").strip()
        if choice == "1":
            return "continue"
        elif choice == "2":
            return "stop"
        print("  Invalid choice. Please enter 1 or 2.")


# -- Helpers --

def _write_chapter_output(
    config: AppConfig,
    chapter_id: str,
    formatted_blocks: list[str],
    chapter_source: ChapterSource | None,
) -> Path:
    """Write the final chapter markdown output to 05_Output."""
    output_dir = chapter_dir(config.workspace.output, chapter_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    title = _resolve_chapter_output_title(config, chapter_id, chapter_source)
    header = f"# {title}\n\n" if title else ""
    body = _remove_duplicate_title_paragraph("\n\n".join(formatted_blocks), has_header=bool(header))
    body = _split_long_paragraphs(body, max_len=850)

    content = f"{header}{body}\n"
    output_path = output_dir / f"{chapter_id}.md"
    atomic_write_text(output_path, content)
    return output_path


def _remove_duplicate_title_paragraph(body: str, *, has_header: bool) -> str:
    """Drop title-like first paragraphs that duplicate the assembled H1."""
    if not has_header:
        return body
    paragraphs = re.split(r"\n\s*\n", body.strip())
    if not paragraphs:
        return body
    first = paragraphs[0].strip()
    if re.match(r"^(ตอนที่|บทที่)\s+\d+(?:\s|:|：|-|$)", first):
        return "\n\n".join(paragraphs[1:]).strip()
    return body


def _run_sentinel_gate_for_chapter(
    *,
    config: AppConfig,
    ledger: RunLedger,
    run_id: str,
    chapter_id: str,
) -> None:
    mode = getattr(config.execution, "sentinel_mode", "report_only")
    if mode != "blocking":
        return

    env_override: dict[str, str] = {}
    workspace_root = config.workspace.root.resolve()
    if "_experiments" in workspace_root.parts:
        registry_path = workspace_root / "00_Config" / "novel_registry.json"
        if registry_path.exists():
            env_override = {
                "NOVEL_SENTINEL_WORKSPACE_ROOT": str(workspace_root),
                "NOVEL_SENTINEL_REGISTRY_PATH": str(registry_path),
                "NOVEL_SENTINEL_MOONREAD_ROOT": str(workspace_root / "MoonRead"),
                "NOVEL_SENTINEL_REPORT_ROOT": str(workspace_root / "07_Reports"),
                "NOVEL_SENTINEL_SKIP_EXISTING_GUARDRAILS": "1",
            }
    previous_env = {key: os.environ.get(key) for key in env_override}
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "sentinel_quality_report.py"
    try:
        for key, value in env_override.items():
            os.environ[key] = value
        spec = importlib.util.spec_from_file_location("sentinel_quality_report_runtime", script_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load Sentinel gate script: {script_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules["sentinel_quality_report_runtime"] = module
        spec.loader.exec_module(module)

        fail_on = getattr(config.execution, "sentinel_fail_on", "major")
        result = module.generate_sentinel_report(
            scope=f"{run_id}_{chapter_id}_sentinel",
            novel=config.novel_id,
            chapters=chapter_id,
            fail_on=fail_on,
            skip_advisory_english=True,
        )
    finally:
        for key, previous in previous_env.items():
            if previous is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = previous
    counts = result["counts"]
    metadata = {
        "mode": mode,
        "fail_on": fail_on,
        "report": str(result["md_path"]),
        "json_report": str(result["json_path"]),
        "blocker": counts.get("blocker", 0),
        "major": counts.get("major", 0),
        "minor": counts.get("minor", 0),
        "info": counts.get("info", 0),
    }
    if result["failed"]:
        ledger.append_stage(
            run_id=run_id,
            block_id=chapter_id,
            stage="sentinel",
            status="failed",
            provider="local",
            metadata=metadata,
        )
        raise RuntimeError(
            f"Sentinel gate blocked {chapter_id}: "
            f"blocker/major/minor/info {metadata['blocker']}/{metadata['major']}/{metadata['minor']}/{metadata['info']}. "
            f"Report: {metadata['report']}"
        )

    ledger.append_stage(
        run_id=run_id,
        block_id=chapter_id,
        stage="sentinel",
        status="completed",
        provider="local",
        metadata=metadata,
    )


def _write_chapter_output_with_sentinel_gate(
    config: AppConfig,
    ledger: RunLedger,
    run_id: str,
    chapter_id: str,
    formatted_blocks: list[str],
    chapter_source: ChapterSource | None,
) -> Path:
    output_path = _write_chapter_output(config, chapter_id, formatted_blocks, chapter_source)
    _run_sentinel_gate_for_chapter(config=config, ledger=ledger, run_id=run_id, chapter_id=chapter_id)
    return output_path


def _resolve_chapter_output_title(
    config: AppConfig,
    chapter_id: str,
    chapter_source: ChapterSource | None,
) -> str:
    source_title = chapter_source.title if chapter_source else ""
    sidecar_path = chapter_dir(config.workspace.work, chapter_id) / "title.json"
    if sidecar_path.exists():
        try:
            data = json.loads(sidecar_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError:
            data = {}
        thai_title = data.get("thai_title") if isinstance(data, dict) else None
        if isinstance(thai_title, str) and thai_title.strip():
            resolved_title = thai_title.strip()
            _validate_chapter_output_title_glossary(config, chapter_id, source_title, resolved_title)
            return resolved_title

    if getattr(config, "novel_id", "") == "horror-game-developer" and source_title:
        normalized_title = _normalize_hgd_chapter_title(chapter_id, source_title)
        if normalized_title:
            _validate_chapter_output_title_glossary(config, chapter_id, source_title, normalized_title)
            _write_hgd_title_sidecar(config, chapter_id, normalized_title)
            return normalized_title
        if _looks_like_hgd_english_title(source_title):
            raise RuntimeError(
                f"Missing HGD Thai title mapping for {chapter_id}: {source_title}. "
                "Update HGD_TITLE_MAP before final assembly."
            )

    if getattr(config, "novel_id", "") == "infinite-regressor-stories" and _looks_like_irs_english_title(source_title):
        raise RuntimeError(
            f"Missing IRS Thai title sidecar for {chapter_id}: {source_title}. "
            "Create 04_Work/<chapter>/title.json before final assembly."
        )

    if source_title and not _contains_han(source_title):
        _validate_chapter_output_title_glossary(config, chapter_id, source_title, source_title)
        return source_title

    if source_title and _contains_han(source_title) and _has_named_chinese_chapter_title(source_title):
        raise RuntimeError(
            f"Missing translated chapter title sidecar for {chapter_id}. "
            "Run scripts/translate_chapter_titles.py for this range before final assembly."
        )

    chapter_number = _chapter_number_from_title(source_title) or _chapter_number_from_id(chapter_id)
    if chapter_number is not None:
        return f"บทที่ {chapter_number}"
    return chapter_id


def _validate_chapter_output_title_glossary(
    config: AppConfig,
    chapter_id: str,
    source_title: str,
    resolved_title: str,
) -> None:
    """Block title/H1 drift when a source title contains an approved glossary term."""
    if not source_title or not resolved_title:
        return
    glossary_dir = getattr(getattr(config, "workspace", None), "glossary_dir", None)
    if not glossary_dir:
        return
    glossary_path = Path(glossary_dir)
    if not glossary_path.exists():
        return
    glossary_index = load_glossary_index(glossary_path)
    checked: set[tuple[str, str]] = set()
    missing: list[str] = []
    for entry in glossary_index.values():
        if entry.status != "approved" or not entry.thai_term:
            continue
        marker = (entry.original_term, entry.thai_term)
        if marker in checked:
            continue
        checked.add(marker)
        source_keys = [entry.original_term, *entry.aliases]
        if not any(_source_title_contains_term(source_title, key) for key in source_keys):
            continue
        if entry.thai_term not in resolved_title:
            missing.append(f"{entry.original_term} -> {entry.thai_term}")
    if missing:
        details = "; ".join(missing)
        raise RuntimeError(
            f"Chapter title violates approved glossary for {chapter_id}: {details}; got {resolved_title!r}"
        )


def _source_title_contains_term(source_title: str, term: str) -> bool:
    if not term:
        return False
    if re.search(r"[A-Za-z]", term):
        return bool(re.search(rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])", source_title))
    return term in source_title


def _normalize_hgd_chapter_title(chapter_id: str, source_title: str) -> str | None:
    match = HGD_TITLE_RE.match(source_title.strip().lstrip("\ufeff#").strip())
    if not match:
        return None
    raw_title = match.group(1).strip()
    suffix = match.group(2) or ""
    thai_title = HGD_TITLE_MAP.get(raw_title)
    if not thai_title:
        return None
    chapter_number = _chapter_number_from_id(chapter_id)
    if chapter_number is None:
        return None
    return f"ตอนที่ {chapter_number} - {thai_title}{suffix}"


def _looks_like_hgd_english_title(source_title: str) -> bool:
    return bool(HGD_TITLE_RE.match(source_title.strip().lstrip("\ufeff#").strip()))


def _looks_like_irs_english_title(source_title: str) -> bool:
    return bool(re.match(r"^Chapter\s+\d+\s+-\s+\S+", source_title.strip().lstrip("\ufeff#").strip(), flags=re.IGNORECASE))


def _write_hgd_title_sidecar(config: AppConfig, chapter_id: str, thai_title: str) -> None:
    sidecar_path = chapter_dir(config.workspace.work, chapter_id) / "title.json"
    atomic_write_json(
        sidecar_path,
        {
            "chapter_id": chapter_id,
            "thai_title": thai_title,
            "source": "pipeline_hgd_title_normalization",
        },
    )


def _contains_han(text: str) -> bool:
    return bool(re.search(r"[\u3400-\u9fff]", text))


def _has_named_chinese_chapter_title(title: str) -> bool:
    match = re.search(r"第[零〇一二两三四五六七八九十百千\d]+章\s*(.+)$", title or "")
    if not match:
        return False
    remainder = match.group(1).strip()
    return bool(re.search(r"[\u3400-\u9fff]", remainder))


def _chapter_number_from_id(chapter_id: str) -> int | None:
    match = re.fullmatch(r"ch(\d+)", chapter_id)
    if not match:
        return None
    return int(match.group(1))


def _chapter_number_from_title(title: str) -> int | None:
    match = re.search(r"第([零〇一二两三四五六七八九十百千\d]+)章", title or "")
    if not match:
        return None
    raw = match.group(1)
    if raw.isdigit():
        return int(raw)
    return _parse_chinese_integer(raw)


def _parse_chinese_integer(raw: str) -> int | None:
    digits = {
        "零": 0,
        "〇": 0,
        "一": 1,
        "二": 2,
        "两": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
    }
    if raw in digits:
        return digits[raw]
    if "百" in raw:
        left, _, right = raw.partition("百")
        hundreds = digits.get(left, 1 if left == "" else None)
        if hundreds is None:
            return None
        tail = _parse_chinese_integer(right) if right else 0
        return hundreds * 100 + (tail or 0)
    if "十" in raw:
        left, _, right = raw.partition("十")
        tens = digits.get(left, 1 if left == "" else None)
        ones = digits.get(right, 0 if right == "" else None)
        if tens is None or ones is None:
            return None
        return tens * 10 + ones
    total = 0
    for char in raw:
        if char not in digits:
            return None
        total = total * 10 + digits[char]
    return total


def _extract_chapter_id(state: ResumeState) -> str:
    for record in state.records:
        if "-" not in record.block_id or record.block_id == record.run_id:
            continue
        # Heuristic: chapter_id is the part before "-block-"
        if "-block-" in record.block_id:
            return record.block_id.rsplit("-block-", 1)[0]
    # Fallback: use first block_id
    if state.latest_by_block:
        first_block = next(iter(state.latest_by_block))
        if "-block-" in first_block:
            return first_block.rsplit("-block-", 1)[0]
        return first_block
    raise ValueError("Cannot determine chapter_id from ledger state.")

def _get_batch_chapter_ids(config: AppConfig, run_id: str) -> list[str] | None:
    """Return chapter_ids from batch glossary scan artifact, or None if not a batch."""
    path = batch_glossary_scan_artifact_path(config.workspace.work, run_id)
    raw = read_text_if_exists(path)
    if raw is None:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    chapter_ids = data.get("chapter_ids")
    if isinstance(chapter_ids, list) and chapter_ids:
        return chapter_ids
    return None


def _resume_chapter(
    *,
    config: AppConfig,
    ledger: RunLedger,
    run_id: str,
    chapter_id: str,
    glossary_index: dict[str, GlossaryEntry],
    state: ResumeState,
    force: bool = False,
    manual_action_mode: str = "interactive",
    until_block: str | None = None,
) -> bool:
    """Resume processing for a single chapter within a batch."""
    if until_block is not None and _block_chapter_id(until_block) != chapter_id:
        raise ValueError(f"Bounded block '{until_block}' does not belong to chapter '{chapter_id}'.")
    print(f"[{run_id}] Chapter: {chapter_id}")
    # Load source and blocks
    source_path = config.workspace.raw / chapter_id / "source.json"
    raw_text = read_text_if_exists(source_path)
    if raw_text is None:
        raise ValueError(f"No fetched source found at {source_path} for run={run_id}.")
    raw_source = json.loads(raw_text)
    chapter_source = ChapterSource(
        novel_id=raw_source.get("novel_id", config.novel_id),
        chapter_id=raw_source.get("chapter_id", chapter_id),
        title=raw_source.get("title", ""),
        source_language=raw_source.get("source_language", config.source_language),
        raw_text=raw_source.get("raw_text", ""),
    )
    blocks = split_blocks(
        chapter_id=chapter_id,
        text=chapter_source.raw_text,
        source_language=config.source_language,
        zh_limit=config.chunking.chinese_character_limit,
        non_zh_limit=config.chunking.non_chinese_word_limit,
    )
    # Create context for this chapter
    ctx = PipelineContext(
        config=config,
        ledger=ledger,
        prompt_store=PromptStore(config.workspace.prompts),
        run_id=run_id,
        blocks=blocks,
        glossary_index=glossary_index,
        chapter_source=chapter_source,
        force=force,
    )
    # Resume chapter-level stages if not yet committed
    if not ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="glossary_scanned"):
        print(f"[{run_id}] Resuming: glossary pre-scan")
        queue_items = build_glossary_scan_queue(config, blocks)
        _write_glossary_scan_artifact(config, chapter_id=chapter_id, items=queue_items)
        ctx.glossary_index = _load_glossary_index_from_queue(config, queue_items)
        _commit_stage(ledger, run_id, chapter_id, "glossary_scanned", "completed", provider="local")
    if not ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="glossary_approved"):
        print(f"[{run_id}] Resuming: glossary approval")
        queue_artifact = _read_glossary_scan_artifact(config, chapter_id=chapter_id)
        if queue_artifact is None:
            queue_items = build_glossary_scan_queue(config, blocks)
            _write_glossary_scan_artifact(config, chapter_id=chapter_id, items=queue_items)
        else:
            queue_items = _read_glossary_scan_items(config, chapter_id=chapter_id)
        queue_items, removed_terms = _revalidate_glossary_queue_items(config, blocks, queue_items)
        if removed_terms:
            _write_glossary_scan_artifact(config, chapter_id=chapter_id, items=queue_items)
            print(f"[{run_id}]   glossary approval revalidated queue; removed {len(removed_terms)} stale/noisy terms.")
        ctx.glossary_index = _load_glossary_index_from_queue(config, queue_items)
        template_text = read_text_if_exists(config.workspace.templates_dir / "Term-Template.md")
        if template_text is None:
            template_text = _default_term_template()
        pending_terms = _pending_terms_from_queue(ctx.glossary_index, queue_items)
        if pending_terms:
            print(f"[{run_id}]   {len(pending_terms)} terms pending approval.")
            provider_runner = _provider_runner_for_stage(config, "term_suggestion")
            queue_by_term = _queue_item_index(queue_items)
            for term_key in pending_terms:
                entry = ctx.glossary_index.get(term_key)
                if entry is None or entry.status == "approved":
                    continue
                queue_item = queue_by_term.get(term_key, {})
                context_text = str(queue_item.get("context", ""))
                suggestion = build_term_suggestion(
                    config=config,
                    provider_runner=provider_runner,
                    prompt_store=ctx.prompt_store,
                    term=term_key,
                    context=context_text,
                )
                thai_term = choose_option_interactively(suggestion)
                entry.thai_term = thai_term
                entry.status = "approved"
                entry.description = suggestion.rationale
                entry.source_language = config.source_language
                entry.novel = config.novel_id
                write_glossary_note(
                    template_text=template_text,
                    glossary_dir=config.workspace.glossary_dir,
                    entry=entry,
                    first_seen_chapter=chapter_id,
                    first_seen_block=str(queue_item.get("first_seen_block", "block-001")),
                )
                ctx.glossary_index[term_key] = entry
        _commit_stage(ledger, run_id, chapter_id, "glossary_approved", "completed", provider="local")
    # Process blocks
    formatted_blocks: list[str] = []
    stop_block_key = _block_sort_key(until_block) if until_block else None
    stopped_early = False
    found_bound_block = False
    index = 0
    while index < len(blocks):
        block = blocks[index]
        if stop_block_key is not None and _block_sort_key(block.block_id) > stop_block_key:
            print(f"[{run_id}] Bounded resume stopping before block {block.block_id}; limit is {until_block}.")
            stopped_early = True
            break
        is_bound_block = until_block is not None and block.block_id == until_block
        next_stage = state.next_pending_stage(block.block_id, BLOCK_STAGE_ORDER)
        if force:
            print(f"[{run_id}] Block {block.block_id}: force rerun requested.")
            formatted_text = _process_block(
                ctx,
                block,
                config.default_style_profile,
                force=True,
                manual_action_mode=manual_action_mode,
            )
            if formatted_text is not None:
                formatted_blocks.append(formatted_text)
            if is_bound_block:
                print(f"[{run_id}] Bounded resume stopped after block {until_block}.")
                found_bound_block = True
                stopped_early = True
                break
            index += 1
            continue
        if next_stage is None:
            print(f"[{run_id}] Block {block.block_id}: all stages completed, loading cached output.")
            cached = _read_block_artifact(config, chapter_id, block.block_id, "formatted")
            if cached is not None:
                formatted_blocks.append(cached.get("text", ""))
            if is_bound_block:
                print(f"[{run_id}] Bounded resume stopped after block {until_block}.")
                found_bound_block = True
                stopped_early = True
                break
            index += 1
            continue
        print(f"[{run_id}] Block {block.block_id}: resuming from stage '{next_stage}'.")
        if next_stage == "formatting" and _formatting_parallel_limit(config) > 1:
            ready_blocks: list[TextBlock] = []
            scan_index = index
            while scan_index < len(blocks):
                candidate = blocks[scan_index]
                if stop_block_key is not None and _block_sort_key(candidate.block_id) > stop_block_key:
                    break
                if state.next_pending_stage(candidate.block_id, BLOCK_STAGE_ORDER) != "formatting":
                    break
                ready_blocks.append(candidate)
                if until_block is not None and candidate.block_id == until_block:
                    break
                scan_index += 1
            if len(ready_blocks) > 1:
                print(f"[{run_id}] Formatting {len(ready_blocks)} ready blocks with limited parallelism.")
                formatted_by_block = _format_ready_blocks_parallel(ctx, ready_blocks)
                for ready_block in ready_blocks:
                    if ready_block.block_id in formatted_by_block:
                        formatted_blocks.append(formatted_by_block[ready_block.block_id])
                    if until_block is not None and ready_block.block_id == until_block:
                        print(f"[{run_id}] Bounded resume stopped after block {until_block}.")
                        found_bound_block = True
                        stopped_early = True
                        break
                index += len(ready_blocks)
                if stopped_early:
                    break
                continue
        formatted_text = _process_block(
            ctx,
            block,
            config.default_style_profile,
            force=force,
            manual_action_mode=manual_action_mode,
        )
        if formatted_text is not None:
            formatted_blocks.append(formatted_text)
        if is_bound_block:
            print(f"[{run_id}] Bounded resume stopped after block {until_block}.")
            found_bound_block = True
            stopped_early = True
            break
        index += 1
    if until_block is not None and not found_bound_block:
        raise ValueError(f"Bounded block '{until_block}' was not found in chapter '{chapter_id}'.")
    if formatted_blocks:
        _write_chapter_output_with_sentinel_gate(config, ledger, run_id, chapter_id, formatted_blocks, ctx.chapter_source)
    return stopped_early



def _reconstruct_literal_draft(data: dict[str, Any], block_id: str, chapter_id: str) -> LiteralDraft:
    pairs_data = data.get("sentence_pairs", [])
    pairs = tuple(
        LiteralSentencePair(
            source_sentence=p.get("source_sentence", ""),
            literal_sentence=p.get("literal_sentence", ""),
        )
        for p in pairs_data
    ) if pairs_data else ()
    return LiteralDraft(
        block_id=data.get("block_id", block_id),
        chapter_id=data.get("chapter_id", chapter_id),
        sentence_pairs=pairs,
        source_text=data.get("source_text", ""),
        provider=data.get("provider", ""),
    )


def _reconstruct_refined_draft(data: dict[str, Any], block_id: str, chapter_id: str) -> RefinedDraft:
    return RefinedDraft(
        block_id=data.get("block_id", block_id),
        chapter_id=data.get("chapter_id", chapter_id),
        refined_text=data.get("refined_text", ""),
        provider=data.get("provider", ""),
        style_profile=data.get("style_profile", ""),
        source_text=data.get("source_text", ""),
    )


def _default_term_template() -> str:
    return """---
type: glossary-term
original_term:
thai_term:
status: proposed
aliases: []
source_language:
category:
novel:
first_seen_chapter:
first_seen_block:
description:
related: []
approved_by:
approval_notes:
created_at:
updated_at:
---

## Summary

## Context Examples

## Translation Notes

## Related Terms

Use `[[linked terms]]` in the body when the note needs to point at another approved glossary entry.

## Runtime Contract

- `status = proposed` means the term still needs human approval.
- `status = approved` means the runtime can treat the term as canonical.
- `status = deprecated` means the term should stay searchable but should not be used for new translations.
- `aliases` should list source spellings or variant forms that the scanner may match.
- `first_seen_chapter` and `first_seen_block` record where the term was first discovered in the source text.
"""


__all__ = [
    "BLOCK_STAGE_ORDER",
    "QA_MAX_RETRIES",
    "STAGE_ORDER",
    "ManualActionRequired",
    "inspect_block_command",
    "PipelineContext",
    "validate_formatted_text",
    "resume_pipeline",
    "run_batch_pipeline",
    "run_pipeline",
    "status_run",
]
