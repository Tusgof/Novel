from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Any

from novel_pipeline.artifacts import glossary_scan_artifact_path
from novel_pipeline.files import atomic_write_json, read_text_if_exists
from novel_pipeline.glossary_support import (
    choose_option_interactively,
    load_glossary_index,
    parse_glossary_note,
    write_glossary_note,
)
from novel_pipeline.prompts import PromptStore
from novel_pipeline.providers.base import ProviderRunner, ensure_provider_response, classify_provider_response, ProviderOutputError
from novel_pipeline.text_utils import extract_candidate_terms, validate_text_script
from novel_pipeline.types import (
    AppConfig,
    GlossaryEntry,
    ProviderRequest,
    TermSuggestion,
    TextBlock,
)


@dataclass(slots=True)
class ProviderTermExtractionResult:
    terms: list[str]
    failed: bool = False
    failure_kind: str = ""


def _glossary_note_record_from_path(path: Path) -> dict[str, Any] | None:
    entry = parse_glossary_note(path)
    if entry is None:
        return None
    status = str(entry.status or "proposed").strip().lower() or "proposed"
    path_parts = {part.lower() for part in path.parts}
    return {
        "original_term": entry.original_term,
        "aliases": list(entry.aliases),
        "status": status,
        "is_quarantine": "quarantine" in path_parts,
    }


def _load_glossary_note_records(glossary_dir: Path | str) -> list[dict[str, Any]]:
    if not isinstance(glossary_dir, (str, Path, PathLike)):
        return []
    glossary_path = Path(glossary_dir)
    glossary_path.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for path in sorted(glossary_path.rglob("*.md")):
        record = _glossary_note_record_from_path(path)
        if record is not None:
            records.append(record)
    return records


def _note_bucket(note: dict[str, Any]) -> str:
    if note.get("is_quarantine"):
        return "quarantine"
    status = str(note.get("status") or "proposed").strip().lower() or "proposed"
    if status in {"approved", "rejected", "deprecated", "proposed"}:
        return status
    return "proposed"


def _blocked_exact_terms(records: list[dict[str, Any]]) -> set[str]:
    blocked: set[str] = set()
    for note in records:
        if _note_bucket(note) not in {"quarantine", "rejected", "deprecated"}:
            continue
        blocked.add(str(note.get("original_term") or "").strip())
        for alias in note.get("aliases") or []:
            blocked.add(str(alias).strip())
    return {term for term in blocked if term}


def _noise_anchor_terms(records: list[dict[str, Any]]) -> set[str]:
    anchors: set[str] = set()
    for note in records:
        if _note_bucket(note) not in {"approved", "quarantine"}:
            continue
        anchors.add(str(note.get("original_term") or "").strip())
        for alias in note.get("aliases") or []:
            anchors.add(str(alias).strip())
    return {term for term in anchors if term}


def _is_obvious_noise_candidate(candidate: str, approved_terms: set[str], quarantine_terms: set[str]) -> bool:
    candidate = candidate.strip()
    if not candidate:
        return False

    # Keep this narrow: one-character edge noise around approved terms, or one-character
    # truncations of quarantined terms, is treated as junk; nothing broader is inferred.
    noisy_edge_tokens = {"是", "的", "了", "之", "其", "这", "那"}
    for anchor in approved_terms:
        if not anchor or anchor == candidate:
            continue
        if candidate.startswith(anchor):
            suffix = candidate[len(anchor):]
            if len(suffix) == 1 and suffix in noisy_edge_tokens:
                return True
        if candidate.endswith(anchor):
            prefix = candidate[:-len(anchor)]
            if len(prefix) == 1 and prefix in noisy_edge_tokens:
                return True

    for anchor in quarantine_terms:
        if not anchor or anchor == candidate:
            continue
        if len(anchor) - len(candidate) == 1:
            if anchor.startswith(candidate) or anchor.endswith(candidate):
                return True

    return False


def _all_occurrences(text: str, term: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    start = 0
    while True:
        pos = text.find(term, start)
        if pos == -1:
            break
        spans.append((pos, pos + len(term)))
        start = pos + 1
    return spans


def _is_covered_by_any(span: tuple[int, int], covering_spans: list[tuple[int, int]]) -> bool:
    start, end = span
    for cover_start, cover_end in covering_spans:
        if start >= cover_start and end <= cover_end:
            return True
    return False


def _prune_substring_fragment_candidates(text: str, candidates: list[str]) -> list[str]:
    kept: list[str] = []
    for term in candidates:
        longer_terms = [other for other in candidates if len(other) > len(term) and term in other]
        if not longer_terms:
            kept.append(term)
            continue
        term_spans = _all_occurrences(text, term)
        if not term_spans:
            kept.append(term)
            continue
        covering_spans: list[tuple[int, int]] = []
        for longer_term in longer_terms:
            covering_spans.extend(_all_occurrences(text, longer_term))
        if term_spans and all(_is_covered_by_any(span, covering_spans) for span in term_spans):
            continue
        kept.append(term)
    return kept


def scan_terms_for_blocks(config: AppConfig, blocks: list[TextBlock], exclude_existing: bool = True) -> list[str]:
    """Extract candidate terms from blocks."""
    return [item["original_term"] for item in build_glossary_scan_queue(config, blocks, exclude_existing=exclude_existing)]


def build_glossary_scan_queue(
    config: AppConfig,
    blocks: list[TextBlock],
    *,
    exclude_existing: bool = True,
) -> list[dict[str, Any]]:
    """Build a deterministic glossary scan queue for the current chapter/run."""
    glossary_index = load_glossary_index(config.workspace.glossary_dir) if exclude_existing else {}
    note_records = _load_glossary_note_records(config.workspace.glossary_dir)
    blocked_exact_terms = _blocked_exact_terms(note_records)
    approved_terms = _noise_anchor_terms(note_records)
    quarantine_terms = {
        str(note.get("original_term") or "").strip()
        for note in note_records
        if _note_bucket(note) == "quarantine"
    }
    quarantine_terms = {term for term in quarantine_terms if term}
    ordered: OrderedDict[str, dict[str, Any]] = OrderedDict()

    # Validate source text is not mojibake before any extraction
    for block in blocks:
        text = block.source_text or block.text
        validate_text_script(text, config.source_language)

    # Circuit breaker for optional provider term extraction
    provider_enabled = True
    provider_calls = 0
    provider_failures = 0
    # Get routing for term_extraction, if configured
    try:
        routing = config.stage_routing_for("term_extraction")
    except KeyError:
        routing = None
    # Safely extract scan budget fields (may be missing in mocks or old configs)
    max_calls = None
    max_failures = None
    if routing:
        # Mock objects may return Mock for missing attributes; we need to check type
        maybe_calls = getattr(routing, "max_calls_per_scan", None)
        maybe_failures = getattr(routing, "max_failures_per_scan", None)
        if isinstance(maybe_calls, int):
            max_calls = maybe_calls
        if isinstance(maybe_failures, int):
            max_failures = maybe_failures
    # Default for term_extraction: at most one failure allowed if not specified
    if routing and max_failures is None:
        max_failures = 1

    for block in blocks:
        text = block.source_text or block.text
        context = text[:500]
        candidates = list(extract_candidate_terms(text))
        
        # Optional provider supplement (if enabled and routing exists)
        provider_terms = []
        if provider_enabled and routing:
            # Check call limit
            if max_calls is not None and provider_calls >= max_calls:
                provider_enabled = False
            # Check failure limit (already disabled if failures reached)
            if provider_enabled and max_failures is not None and provider_failures >= max_failures:
                provider_enabled = False
        
        if provider_enabled and routing:
            result = _extract_provider_candidate_terms_with_status(config, text)
            provider_calls += 1
            if result.failed:
                provider_failures += 1
                if max_failures is not None and provider_failures >= max_failures:
                    provider_enabled = False
            provider_terms = result.terms
            # Safety: never include provider meta/quota text as candidate term
            # parse_candidate_terms already filters non-Chinese, but we double-check
            provider_terms = [t for t in provider_terms if _looks_like_source_candidate(t)]
        
        candidates.extend(provider_terms)
        
        filtered_candidates: list[str] = []
        for term in _dedupe_candidates(candidates):
            if term in blocked_exact_terms:
                continue
            if exclude_existing and term in glossary_index:
                continue
            if _is_obvious_noise_candidate(term, approved_terms, quarantine_terms):
                continue
            filtered_candidates.append(term)

        for term in _prune_substring_fragment_candidates(text, filtered_candidates):
            if term in ordered:
                continue
            ordered[term] = {
                "original_term": term,
                "category": infer_category(term),
                "chapter_id": block.chapter_id,
                "first_seen_block": block.block_id,
                "context": context,
                "source_language": config.source_language,
                "novel": config.novel_id,
            }

    return list(ordered.values())


def _extract_provider_candidate_terms_with_status(config: AppConfig, text: str) -> ProviderTermExtractionResult:
    """Internal helper that returns terms and failure state."""
    if "term_extraction" not in config.stage_routing:
        return ProviderTermExtractionResult(terms=[])
    try:
        prompt_store = PromptStore(config.workspace.prompts)
        prompt_text = prompt_store.render(
            "term_extraction",
            source_block=text[:2500],
        )
        routing = config.stage_routing_for("term_extraction")
        provider_runner = ProviderRunner(config.provider_for_stage("term_extraction"))
        # Build request with stage-level timeout override
        request = ProviderRequest(
            prompt=prompt_text,
            provider=provider_runner.spec.name,
            stage="term_extraction",
            model=routing.model,
            timeout_seconds=routing.timeout_seconds,
        )
        # Pass retry overrides from routing
        response = provider_runner.run_with_retry(
            request,
            max_attempts=routing.retry_max_attempts,
            retry_delay_seconds=routing.retry_initial_delay_seconds,
            retry_backoff_multiplier=routing.retry_backoff_multiplier,
            retry_failure_kinds=routing.retry_failure_kinds,
        )
        ensure_provider_response(response)
        terms = parse_candidate_terms(response.stdout)
        return ProviderTermExtractionResult(terms=terms, failed=False, failure_kind="")
    except ProviderOutputError as e:
        # Provider returned unusable output (quota, timeout, empty stdout, etc.)
        failure_kind = classify_provider_response(e.response)
        return ProviderTermExtractionResult(terms=[], failed=True, failure_kind=failure_kind)
    except Exception:
        # Any other exception (network, parsing, etc.)
        return ProviderTermExtractionResult(terms=[], failed=True, failure_kind="exception")


def _extract_provider_candidate_terms(config: AppConfig, text: str) -> list[str]:
    """Use the configured term_extraction provider as an optional candidate supplement."""
    result = _extract_provider_candidate_terms_with_status(config, text)
    return result.terms


def _dedupe_candidates(candidates: list[str]) -> list[str]:
    ordered: OrderedDict[str, None] = OrderedDict()
    for candidate in candidates:
        term = candidate.strip()
        if term:
            ordered.setdefault(term, None)
    return list(ordered)


def parse_candidate_terms(stdout: str) -> list[str]:
    """Parse source-language candidate terms from provider output."""
    candidates: list[str] = []
    seen: set[str] = set()
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[\-\*\d\.\)\(]+[\s]*", "", line).strip()
        line = re.sub(r"[\*_`]+", "", line).strip()
        if "|" in line:
            line = line.split("|", 1)[0].strip()
        if "：" in line:
            line = line.split("：", 1)[0].strip()
        if ":" in line:
            line = line.split(":", 1)[0].strip()
        if not _looks_like_source_candidate(line):
            continue
        if line in seen:
            continue
        seen.add(line)
        candidates.append(line)
    return candidates


def _looks_like_source_candidate(value: str) -> bool:
    value = value.strip()
    if not value or len(value) > 20:
        return False
    if re.search(r"[\u0e00-\u0e7f]", value):
        return False
    if re.search(r"[。！？!?，,；;]", value):
        return False
    return bool(re.search(r"[\u4e00-\u9fff]", value) or re.match(r"^[A-Z][A-Za-z\-']{2,}$", value))


def run_glossary_stage(
    *,
    config: AppConfig,
    chapter_id: str,
    blocks: list[TextBlock],
    provider_runner: ProviderRunner,
) -> dict[str, GlossaryEntry]:
    """Scan terms, deduplicate against existing glossary, and manage approvals.

    Returns a dict of term -> GlossaryEntry for newly approved terms.
    """
    glossary_index = load_glossary_index(config.workspace.glossary_dir)
    template_text = read_text_if_exists(config.workspace.templates_dir / "Term-Template.md")
    if template_text is None:
        template_text = _default_term_template()

    prompt_store = PromptStore(config.workspace.prompts)
    queue_items = build_glossary_scan_queue(config, blocks)
    resolved: dict[str, GlossaryEntry] = {}

    atomic_write_json(
        glossary_scan_artifact_path(config.workspace.work, chapter_id),
        {
            "schema_version": 1,
            "scope": {"type": "chapter", "id": chapter_id},
            "chapter_ids": [chapter_id],
            "items": queue_items,
        },
    )

    for item in queue_items:
        term = item["original_term"]
        if term in glossary_index:
            existing = glossary_index[term]
            if existing.status == "approved":
                continue

        context_text = str(item.get("context", ""))

        suggestion = build_term_suggestion(
            config=config,
            provider_runner=provider_runner,
            prompt_store=prompt_store,
            term=term,
            context=context_text,
        )

        thai_term = choose_option_interactively(suggestion)

        entry = GlossaryEntry(
            original_term=term,
            thai_term=thai_term,
            status="approved",
            category=suggestion.category,
            description=suggestion.rationale,
            aliases=tuple(suggestion.options) if suggestion.options else (),
            related=(),
            source_language=config.source_language,
            novel=config.novel_id,
        )

        write_glossary_note(
            template_text=template_text,
            glossary_dir=config.workspace.glossary_dir,
            entry=entry,
            first_seen_chapter=chapter_id,
            first_seen_block=blocks[0].block_id if blocks else "block-001",
        )

        glossary_index[term] = entry
        for alias in entry.aliases:
            glossary_index[alias] = entry
        resolved[term] = entry

    return resolved


def build_term_suggestion(
    *,
    config: AppConfig,
    provider_runner: ProviderRunner,
    prompt_store: PromptStore,
    term: str,
    context: str,
) -> TermSuggestion:
    """Build 3 translation options for a term, using provider or deterministic fallback."""
    category = infer_category(term)
    curated_options = _curated_fallback_options(term)
    if curated_options:
        return TermSuggestion(
            original_term=term,
            category=category,
            context=(context,),
            rationale="Curated local fallback for known Deep Sea Embers terms.",
            options=tuple(curated_options),
            rationales=(
                f"Curated option 1 for {term}",
                f"Curated option 2 for {term}",
                f"Curated option 3 for {term}",
            ),
            provider="curated",
        )

    try:
        prompt_text = prompt_store.render(
            "term_suggestion",
            {
                "original_term": term,
                "category": category,
                "context": context,
                "source_language": config.source_language,
            },
        )
        response = provider_runner.run_with_retry(
            ProviderRequest(
                prompt=prompt_text,
                provider=provider_runner.spec.name,
                stage="term_suggestion",
            )
        )
        ensure_provider_response(response)
        results = parse_suggestion_options(response.stdout)
        if len(results) >= 3:
            options = [r[0] for r in results[:3]]
            rationales = [r[1] or f"Option {i+1} for {term}" for i, r in enumerate(results[:3])]
            return TermSuggestion(
                original_term=term,
                category=category,
                context=(context,),
                rationale="Provider-generated options based on local context.",
                options=tuple(options),
                rationales=tuple(rationales),
                provider=provider_runner.spec.name,
            )
    except Exception:
        pass

    # Deterministic fallback
    fallback_options = _deterministic_fallback_options(term, category)
    return TermSuggestion(
        original_term=term,
        category=category,
        context=(context,),
        rationale="Fallback options because provider output was unavailable or unparseable.",
        options=tuple(fallback_options),
        rationales=(
            f"Literal transliteration of {term}",
            f"Descriptive form with common suffix",
            f"Formal variant with honorific suffix",
        ),
        provider="fallback",
    )


def parse_suggestion_options(stdout: str) -> list[tuple[str, str]]:
    """Parse numbered or bulleted list of options from provider stdout.
    
    Expected format: "Term | Rationale" or just "Term".
    """
    lines = stdout.splitlines()
    results: list[tuple[str, str]] = []
    seen: set[str] = set()

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        # Strip numbering/bullets: "1. ", "- ", "* ", etc.
        cleaned = re.sub(r"^[\-\*\d\.\)\(]+[\s]*", "", line).strip()
        # Strip markdown bold/italic
        cleaned = re.sub(r"[\*_]{1,2}", "", cleaned).strip()
        if not cleaned or len(cleaned) < 1:
            continue
        
        if "|" in cleaned:
            term, rationale = cleaned.split("|", 1)
            term = term.strip()
            rationale = rationale.strip()
        else:
            term = cleaned
            rationale = ""

        if not _looks_like_thai_option(term):
            continue
        if term in seen:
            continue
        seen.add(term)
        results.append((term, rationale))

    return results


def _looks_like_thai_option(value: str) -> bool:
    """Keep provider output constrained to actual Thai glossary options."""
    value = value.strip()
    if not value or len(value) > 40:
        return False
    if re.search(r"[\u4e00-\u9fff]", value):
        return False
    if re.search(r"[A-Za-z]", value):
        return False
    return bool(re.search(r"[\u0e00-\u0e7f]", value))


def infer_category(term: str) -> str:
    """Infer a rough category for a term based on heuristics for Deep Sea Embers."""
    # Chinese characters:
    if re.match(r"^[\u4e00-\u9fff]{2}$", term):
        # 2 chars are often just words unless they appear extremely frequently
        # but here we just infer category. Let's default to 'term' for 2 chars
        # unless it's a known name pattern (which we don't have yet)
        return "term"
        
    if re.match(r"^[\u4e00-\u9fff]{3}$", term):
        # 3 chars could be names, but still risky
        return "term"

    # 4 chars might be names or titles/locations
    if re.match(r"^[\u4e00-\u9fff]{4}$", term):
        if any(x in term for x in ("号", "之")):
            return "vessel"
        if any(x in term for x in ("都", "市", "岛", "海")):
            return "location"
        return "title"
        
    # Longer Chinese phrases in this novel are often entities or phenomena
    if re.match(r"^[\u4e00-\u9fff]{5,7}$", term):
        if any(x in term for x in ("雾", "光", "声")):
            return "phenomenon"
        return "entity"
        
    # Latin capitalized words are likely names or titles
    if re.match(r"^[A-Z][a-zA-Z]+$", term):
        # If all caps and short, maybe an acronym/term
        if term.isupper() and len(term) <= 4:
            return "term"
        return "character"
        
    return "term"


def _deterministic_fallback_options(term: str, category: str) -> list[str]:
    """Produce 3 deterministic fallback translation options when provider is unavailable."""
    curated = _curated_fallback_options(term)
    if curated:
        return curated
    if category == "character":
        return [
            term,  # Keep original
            f"{term} (ตัวละคร)",  # Add descriptor
            f"คุณ{term}",  # Honorific prefix (Deep Sea Embers uses more modern/western-ish honorifics)
        ]
    if category == "vessel":
        return [
            term,
            f"เรือ{term}",
            f"เรือเดินสมุทร{term}",
        ]
    if category == "location":
        return [
            term,
            f"นคร{term}",
            f"เกาะ{term}",
        ]
    if category == "entity":
        return [
            term,
            f"ตัวตน{term}",
            f"สิ่งที่เรียกว่า{term}",
        ]
    if category == "phenomenon":
        return [
            term,
            f"ปรากฏการณ์{term}",
            f"ความผิดปกติ{term}",
        ]
    return [
        term,
        f"{term}แห่ง",
        f"เกี่ยวกับ{term}",
    ]


def _curated_fallback_options(term: str) -> list[str]:
    curated = {
        "周铭": ["โจวหมิง", "โจว หมิง", "คุณโจวหมิง"],
        "浓雾": ["หมอกหนาทึบ", "ม่านหมอกหนา", "หมอกเข้มข้น"],
        "雾气": ["ไอหมอก", "ละอองหมอก", "หมอกบาง"],
        "日记": ["บันทึกประจำวัน", "สมุดบันทึก", "ไดอารี"],
        "镜子": ["กระจก", "บานกระจก", "คันฉ่อง"],
    }
    return curated.get(term, [])


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
    "build_term_suggestion",
    "build_glossary_scan_queue",
    "infer_category",
    "parse_candidate_terms",
    "run_glossary_stage",
    "scan_terms_for_blocks",
]
