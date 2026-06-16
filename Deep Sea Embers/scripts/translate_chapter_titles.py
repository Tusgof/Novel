from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from novel_pipeline.artifacts import chapter_dir
from novel_pipeline.config import load_app_config
from novel_pipeline.glossary_support import load_glossary_index
from novel_pipeline.prompts import PromptStore
from novel_pipeline.providers.base import ProviderRunner, ensure_provider_response
from novel_pipeline.stages.helpers import format_glossary_subset
from novel_pipeline.text_utils import parse_chapter_range, validate_text_script
from novel_pipeline.types import AppConfig, ProviderRequest


HAN_RE = re.compile(r"[\u3400-\u9fff]")
THAI_RE = re.compile(r"[\u0e00-\u0e7f]")


def main() -> int:
    parser = argparse.ArgumentParser(description="Translate chapter titles through configured title provider routes.")
    parser.add_argument("--config", type=Path, default=Path(".system/config.yaml"))
    parser.add_argument("--range", dest="chapter_range", required=True)
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()

    config = load_app_config(args.config)
    chapter_ids = parse_chapter_range(args.chapter_range)
    translate_chapter_titles(config=config, chapter_ids=chapter_ids, run_id=args.run_id)
    return 0


def translate_chapter_titles(*, config: AppConfig, chapter_ids: list[str], run_id: str = "") -> None:
    source_titles = _load_source_titles(config, chapter_ids)
    glossary_subset = _approved_entries_for_titles(
        source_titles=source_titles,
        glossary_entries=list(load_glossary_index(config.workspace.glossary).values()),
    )
    glossary_text = format_glossary_subset(glossary_subset)

    literal_titles = _run_title_provider(
        config=config,
        prompt_name="title_literal_translation",
        stage="literal_translation",
        payload={
            "titles": [
                {
                    "chapter_id": chapter_id,
                    "source_title": source_titles[chapter_id],
                    "mandatory_glossary_terms": _required_terms_for_title(source_titles[chapter_id], glossary_subset),
                }
                for chapter_id in chapter_ids
            ]
        },
        glossary_text=glossary_text,
    )

    refined_titles = _run_title_provider(
        config=config,
        prompt_name="title_refinement",
        stage="refinement",
        payload={
            "titles": [
                {
                    "chapter_id": chapter_id,
                    "source_title": source_titles[chapter_id],
                    "literal_title": literal_titles[chapter_id],
                    "mandatory_glossary_terms": _required_terms_for_title(source_titles[chapter_id], glossary_subset),
                }
                for chapter_id in chapter_ids
            ]
        },
        glossary_text=glossary_text,
    )

    created_at = datetime.now(timezone.utc).isoformat()
    literal_routing = config.stage_routing_for("literal_translation")
    refine_routing = config.stage_routing_for("refinement")
    for chapter_id in chapter_ids:
        title = refined_titles[chapter_id]
        required_terms = _required_terms_for_title(source_titles[chapter_id], glossary_subset)
        _validate_title(chapter_id, title, required_terms=required_terms)
        title_path = chapter_dir(config.workspace.work, chapter_id) / "title.json"
        title_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "source_title": source_titles[chapter_id],
            "literal_title": literal_titles[chapter_id],
            "thai_title": title,
            "approved_by": "title_provider_pipeline",
            "run_id": run_id,
            "created_at": created_at,
            "literal_provider": literal_routing.provider,
            "literal_model": literal_routing.model,
            "refine_provider": refine_routing.provider,
            "refine_model": refine_routing.model,
            "mandatory_glossary_terms": required_terms,
            "notes": "Title translated via literal_translation route and refined via refinement route before chapter assembly.",
        }
        title_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report_path = config.workspace.logs / "title_translation_last.json"
    report_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "chapter_ids": chapter_ids,
                "literal_provider": literal_routing.provider,
                "literal_model": literal_routing.model,
                "refine_provider": refine_routing.provider,
                "refine_model": refine_routing.model,
                "created_at": created_at,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Translated titles: {len(chapter_ids)}")
    print(f"Report: {report_path}")


def _load_source_titles(config: AppConfig, chapter_ids: list[str]) -> dict[str, str]:
    titles: dict[str, str] = {}
    for chapter_id in chapter_ids:
        source_path = chapter_dir(config.workspace.raw, chapter_id) / "source.json"
        data = json.loads(source_path.read_text(encoding="utf-8-sig"))
        title = str(data.get("title", "")).strip()
        if not title:
            raise ValueError(f"Missing source title for {chapter_id}: {source_path}")
        titles[chapter_id] = title
    return titles


def _run_title_provider(
    *,
    config: AppConfig,
    prompt_name: str,
    stage: str,
    payload: dict[str, Any],
    glossary_text: str,
) -> dict[str, str]:
    prompt_store = PromptStore(config.workspace.prompts)
    rendered = prompt_store.render(
        prompt_name,
        title_payload=json.dumps(payload, ensure_ascii=False, indent=2),
        glossary_subset=glossary_text,
    )
    provider = config.provider_for_stage(stage)
    routing = config.stage_routing_for(stage)
    response = ProviderRunner(provider).run_with_retry(
        ProviderRequest(
            prompt=rendered,
            provider=provider.name,
            stage=stage,
            model=routing.model,
            timeout_seconds=routing.timeout_seconds,
        )
    )
    ensure_provider_response(response)
    data = _parse_json_object(response.stdout)
    items = data.get("titles")
    if not isinstance(items, list):
        raise ValueError(f"Provider output for {prompt_name} missing titles list.")
    result: dict[str, str] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        chapter_id = str(item.get("chapter_id", "")).strip()
        thai_title = str(item.get("thai_title", "")).strip()
        if chapter_id and thai_title:
            required_terms: list[dict[str, str]] = []
            for payload_item in payload["titles"]:
                if str(payload_item.get("chapter_id", "")).strip() == chapter_id:
                    required_terms = list(payload_item.get("mandatory_glossary_terms", []) or [])
                    break
            _validate_title(chapter_id, thai_title, required_terms=required_terms)
            result[chapter_id] = thai_title
    expected = {str(item["chapter_id"]) for item in payload["titles"]}
    missing = sorted(expected.difference(result))
    if missing:
        raise ValueError(f"Provider output for {prompt_name} missing titles for: {', '.join(missing)}")
    return result


def _parse_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped, flags=re.I).strip()
        stripped = re.sub(r"```$", "", stripped).strip()
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, flags=re.S)
        if not match:
            raise
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("Provider output JSON root must be an object.")
    return data


def _approved_entries_for_titles(*, source_titles: dict[str, str], glossary_entries: list[Any]) -> list[Any]:
    combined_titles = "\n".join(source_titles.values())
    selected: list[Any] = []
    seen: set[str] = set()
    for entry in sorted(glossary_entries, key=lambda item: len(item.original_term), reverse=True):
        if entry.status.strip().lower() != "approved":
            continue
        if not entry.original_term or entry.original_term in seen:
            continue
        if entry.original_term in combined_titles:
            selected.append(entry)
            seen.add(entry.original_term)
    return selected


def _required_terms_for_title(source_title: str, glossary_entries: list[Any]) -> list[dict[str, str]]:
    required: list[dict[str, str]] = []
    for entry in sorted(glossary_entries, key=lambda item: len(item.original_term), reverse=True):
        if entry.status.strip().lower() != "approved":
            continue
        if entry.original_term and entry.original_term in source_title:
            required.append(
                {
                    "original_term": entry.original_term,
                    "thai_term": entry.thai_term,
                    "category": entry.category,
                }
            )
    return required


def _validate_title(
    chapter_id: str,
    title: str,
    *,
    required_terms: list[dict[str, str]] | None = None,
) -> None:
    if HAN_RE.search(title):
        raise ValueError(f"Title for {chapter_id} contains source Chinese: {title}")
    if not THAI_RE.search(title):
        raise ValueError(f"Title for {chapter_id} contains no Thai text: {title}")
    for term in required_terms or []:
        source_term = str(term.get("original_term", "")).strip()
        thai_term = str(term.get("thai_term", "")).strip()
        if thai_term and thai_term not in title:
            raise ValueError(
                f"Title for {chapter_id} violates glossary: {source_term} must be {thai_term!r}; got {title!r}"
            )
    validate_text_script(title, "th")


if __name__ == "__main__":
    raise SystemExit(main())
