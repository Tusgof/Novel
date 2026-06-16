from __future__ import annotations

from novel_pipeline.prompts import PromptStore
from novel_pipeline.providers.base import ProviderRunner, ensure_provider_response, ProviderOutputError
from novel_pipeline.text_utils import validate_text_script
from novel_pipeline.stages.helpers import format_glossary_subset
from novel_pipeline.types import AppConfig, GlossaryEntry, LiteralDraft, ProviderRequest, RefinedDraft, TextBlock


def run_refine_stage(
    *,
    config: AppConfig,
    block: TextBlock,
    literal_draft: LiteralDraft,
    glossary_subset: list[GlossaryEntry],
    style_profile_key: str,
    provider_runner: ProviderRunner,
    model: str = "",
    retry_feedback: str = "",
) -> RefinedDraft:
    prompt_store = PromptStore(config.workspace.prompts)
    style_profile = config.style_profile_for_name(style_profile_key)
    
    formatted_glossary = format_glossary_subset(glossary_subset)
    formatted_literal = "\n\n".join(pair.literal_sentence for pair in literal_draft.sentence_pairs)
    
    prompt = prompt_store.render(
        "refinement",
        literal_draft=formatted_literal,
        source_block=block.source_text,
        glossary_subset=formatted_glossary,
        style_instructions=style_profile.instruction_text(),
        retry_feedback=retry_feedback or "none",
        research_context=config.research_context_text(),
    )
    response = provider_runner.run_with_retry(
        ProviderRequest(
            prompt=prompt,
            provider=provider_runner.spec.name,
            stage="refinement",
            model=model,
        )
    )
    ensure_provider_response(response)
    fallback = "\n".join(pair.literal_sentence for pair in literal_draft.sentence_pairs)
    # Validate fallback (should already be Thai, but ensure no mojibake)
    try:
        validate_text_script(fallback, "th")
    except ValueError as exc:
        raise ProviderOutputError(
            response,
            f"Fallback literal draft contains mojibake: {exc}"
        ) from exc
    refined_text = _clean_refined_output(response.stdout) or fallback
    # Validate refined text
    try:
        validate_text_script(refined_text, "th")
    except ValueError as exc:
        raise ProviderOutputError(
            response,
            f"Provider '{response.provider}' returned mojibake Thai output: {exc}"
        ) from exc
    if _too_short_to_trust(refined_text, fallback):
        refined_text = fallback
    return RefinedDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        refined_text=refined_text,
        provider=provider_runner.spec.name,
        style_profile=style_profile.key,
        source_text=block.source_text,
    )


def _clean_refined_output(stdout: str) -> str:
    text = stdout.strip()
    if not text:
        return ""
    for marker in ("\n---", "\n**Craft notes", "\nCraft notes", "\nหมายเหตุ"):
        marker_index = text.find(marker)
        if marker_index != -1:
            text = text[:marker_index].strip()
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if stripped.startswith(("-", "*", "#", "`")):
            continue
        if "Craft notes" in stripped:
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _too_short_to_trust(refined_text: str, literal_text: str) -> bool:
    refined_len = _thai_character_count(refined_text)
    literal_len = _thai_character_count(literal_text)
    if literal_len < 200:
        return False
    return refined_len < int(literal_len * 0.65)


def _thai_character_count(text: str) -> int:
    return sum("\u0e00" <= char <= "\u0e7f" for char in text)
