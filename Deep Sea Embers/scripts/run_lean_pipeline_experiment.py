"""Run the experiment-only lean chapter pipeline.

This is deliberately separate from the production CLI. It translates blocks
for transport safety, then refines, checks, and formats the assembled chapter
once. Every provider call is traced when ``--trace-dir`` is supplied.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from novel_pipeline.config import load_app_config
from novel_pipeline.glossary_support import load_glossary_index, select_non_overlapping_glossary_entries
from novel_pipeline.pipeline import _format_block_with_hybrid_provider, _load_chapter_source_and_blocks
from novel_pipeline.prompts import PromptStore
from novel_pipeline.providers.base import ProviderRunner, ensure_provider_response
from novel_pipeline.stages.qa import run_qa_stage
from novel_pipeline.stages.refine import run_refine_stage
from novel_pipeline.stages.translate import run_literal_translation_stage
from novel_pipeline.types import LiteralDraft, LiteralSentencePair, RefinedDraft, TextBlock, ProviderRequest
from novel_pipeline.files import atomic_write_json


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    chapters = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        if re.fullmatch(r"\d+", item):
            item = f"ch{int(item):03d}"
        if not re.fullmatch(r"ch\d+", item):
            raise ValueError(f"Invalid chapter id: {item}")
        chapters.append(item)
    if not chapters:
        raise ValueError("At least one chapter is required.")
    return chapters


def _chapter_glossary_subset(block: TextBlock, glossary: dict[str, Any]) -> list[Any]:
    return select_non_overlapping_glossary_entries(block.source_text, glossary.values())


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
    runner = ProviderRunner(config.provider_for_stage("term_extraction"))
    prompt_store = PromptStore(config.workspace.prompts)
    if "term_harvest" not in prompt_store.available():
        prompt_store = PromptStore(ROOT / "prompts")
    prompt = prompt_store.render(
        "term_harvest",
        source_text=source_text,
        final_translation=final_text,
    )
    _context(run_id=run_id, chapter_id=chapter_id, stage="term_harvest")
    response = runner.run_with_retry(
        ProviderRequest(
            prompt=prompt,
            provider=runner.spec.name,
            stage="term_harvest",
            model=routing.model,
            timeout_seconds=routing.timeout_seconds,
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


def _trace_metrics(trace_dir: Path) -> dict[str, Any]:
    calls = 0
    failures = 0
    stage_counts: dict[str, int] = {}
    usage_totals: dict[str, float] = {}
    cost = 0.0
    cost_seen = False
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
        if response.get("failure_kind"):
            failures += 1
        usage = response.get("usage", {})
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
        "calls_by_stage": stage_counts,
        "usage_totals": usage_totals,
        "cost": cost if cost_seen else None,
        "cost_status": "measured" if cost_seen else "provider_did_not_report_cost",
    }


def run_chapter(config: Any, chapter_id: str, run_id: str, output_dir: Path, trace_dir: Path) -> dict[str, Any]:
    source, blocks = _load_chapter_source_and_blocks(config, chapter_id)
    glossary = load_glossary_index(config.workspace.glossary_dir)
    literal_pairs: list[LiteralSentencePair] = []
    block_records: list[dict[str, Any]] = []
    for block in blocks:
        _context(run_id=run_id, chapter_id=chapter_id, stage="literal_translation", block_id=block.block_id)
        runner = ProviderRunner(config.provider_for_stage("literal_translation"))
        routing = config.stage_routing_for("literal_translation")
        draft = run_literal_translation_stage(
            config=config,
            block=block,
            glossary_subset=_chapter_glossary_subset(block, glossary),
            provider_runner=runner,
            model=routing.model,
        )
        literal_pairs.extend(draft.sentence_pairs)
        block_records.append(
            {
                "block_id": block.block_id,
                "source_chars": len(block.source_text),
                "literal_chars": sum(len(pair.literal_sentence) for pair in draft.sentence_pairs),
            }
        )

    literal_text = "\n\n".join(pair.literal_sentence.strip() for pair in literal_pairs if pair.literal_sentence.strip()).strip()
    chapter_block = TextBlock(
        block_id=f"{chapter_id}-assembled",
        chapter_id=chapter_id,
        block_index=1,
        source_text=source.raw_text,
        source_language=source.source_language,
    )
    assembled_literal = LiteralDraft(
        block_id=chapter_block.block_id,
        chapter_id=chapter_id,
        sentence_pairs=tuple(literal_pairs),
        source_text=source.raw_text,
        provider="assembled_from_blocks",
    )
    _context(run_id=run_id, chapter_id=chapter_id, stage="refinement", block_id=chapter_block.block_id)
    refine_routing = config.stage_routing_for("refinement")
    refined = run_refine_stage(
        config=config,
        block=chapter_block,
        literal_draft=assembled_literal,
        glossary_subset=_chapter_glossary_subset(chapter_block, glossary),
        style_profile_key=config.default_style_profile,
        provider_runner=ProviderRunner(config.provider_for_stage("refinement")),
        model=refine_routing.model,
    )
    _context(run_id=run_id, chapter_id=chapter_id, stage="qa_judge", block_id=chapter_block.block_id)
    qa_routing = config.stage_routing_for("qa_judge")
    qa = run_qa_stage(
        config=config,
        block=chapter_block,
        literal_draft=assembled_literal,
        refined_draft=refined,
        glossary_subset=_chapter_glossary_subset(chapter_block, glossary),
        provider_runner=ProviderRunner(config.provider_for_stage("qa_judge")),
        model=qa_routing.model,
        style_profile_key=config.default_style_profile,
    )
    if not qa.passed:
        raise RuntimeError(f"Lean QA failed for {chapter_id}: {qa.feedback}")
    _context(run_id=run_id, chapter_id=chapter_id, stage="formatting", block_id=chapter_block.block_id)
    formatted, formatter_provider, formatter_meta = _format_block_with_hybrid_provider(
        config=config,
        prompt_store=PromptStore(config.workspace.prompts),
        refined_text=refined.refined_text,
    )
    chapter_output = f"# {source.title or chapter_id}\n\n{formatted.strip()}\n"
    chapter_dir = output_dir / chapter_id
    chapter_dir.mkdir(parents=True, exist_ok=True)
    (chapter_dir / f"{chapter_id}.md").write_text(chapter_output, encoding="utf-8")
    proposed = _harvest_candidates(
        config=config,
        chapter_id=chapter_id,
        source_text=source.raw_text,
        final_text=formatted,
        run_id=run_id,
        trace_dir=trace_dir,
    )
    atomic_write_json(chapter_dir / "glossary_proposed.json", proposed)
    return {
        "chapter_id": chapter_id,
        "source_chars": len(source.raw_text),
        "block_count": len(blocks),
        "block_records": block_records,
        "literal_chars": len(literal_text),
        "refined_chars": len(refined.refined_text),
        "formatted_chars": len(formatted),
        "qa_passed": qa.passed,
        "qa_feedback": qa.feedback,
        "formatter_provider": formatter_provider,
        "formatter_metadata": formatter_meta,
        "glossary_proposed_count": len(proposed),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--chapters", required=True, help="Comma-separated IDs, e.g. ch001,ch004")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--trace-dir", type=Path, required=True)
    args = parser.parse_args()
    chapters = _parse_chapters(args.chapters)
    config = load_app_config(args.config)
    output_dir = args.output_dir.resolve()
    trace_dir = args.trace_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    trace_dir.mkdir(parents=True, exist_ok=True)
    os.environ["NOVEL_PIPELINE_TRACE_DIR"] = str(trace_dir)
    results: list[dict[str, Any]] = []
    status = "complete"
    error = ""
    try:
        for chapter_id in chapters:
            results.append(run_chapter(config, chapter_id, args.run_id, output_dir, trace_dir))
    except Exception as exc:  # preserve a machine-readable stopped experiment result
        status = "blocked"
        error = f"{type(exc).__name__}: {exc}"
    report = {
        "schema": "novel.lean-experiment.v1",
        "run_id": args.run_id,
        "novel_id": config.novel_id,
        "started_at": _utc_now(),
        "status": status,
        "chapters": results,
        "metrics": _trace_metrics(trace_dir),
        "trace_dir": str(trace_dir),
        "output_dir": str(output_dir),
        "glossary_policy": "chapter-relevant context only; harvested terms remain proposed",
        "error": error,
    }
    atomic_write_json(output_dir / "lean_experiment_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
