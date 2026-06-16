from __future__ import annotations

import re

from novel_pipeline.prompts import PromptStore
from novel_pipeline.providers.base import ProviderRunner, ensure_provider_response, ProviderOutputError
from novel_pipeline.stages.helpers import format_glossary_subset
from novel_pipeline.text_utils import split_sentences, validate_text_script
from novel_pipeline.types import AppConfig, GlossaryEntry, LiteralDraft, LiteralSentencePair, ProviderRequest, TextBlock


def run_literal_translation_stage(
    *,
    config: AppConfig,
    block: TextBlock,
    glossary_subset: list[GlossaryEntry],
    provider_runner: ProviderRunner,
    model: str = "",
) -> LiteralDraft:
    prompt_store = PromptStore(config.workspace.prompts)
    formatted_glossary = format_glossary_subset(glossary_subset)
    source_for_prompt = " ".join(line.strip() for line in block.source_text.splitlines() if line.strip())
    prompt = prompt_store.render(
        "literal_translation",
        source_block=source_for_prompt,
        glossary_subset=formatted_glossary,
        source_language=block.source_language,
        research_context=config.research_context_text(),
    )
    response = provider_runner.run_with_retry(
        ProviderRequest(
            prompt=prompt,
            provider=provider_runner.spec.name,
            stage="literal_translation",
            model=model,
        )
    )
    ensure_provider_response(response)
    pairs = parse_literal_pairs(block.source_text, response.stdout)
    if not pairs:
        preview = (response.stderr or response.stdout or "").strip().replace("\n", " ")[:300]
        raise RuntimeError(f"Literal translation provider did not return parseable Thai output. {preview}")
    # Mojibake detection
    for pair in pairs:
        try:
            validate_text_script(pair.literal_sentence, "th")
        except ValueError as exc:
            raise ProviderOutputError(
                response,
                f"Provider '{response.provider}' returned mojibake Thai output: {exc}"
            ) from exc
    return LiteralDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        sentence_pairs=pairs,
        source_text=block.source_text,
        provider=provider_runner.spec.name,
    )


def parse_literal_pairs(source_text: str, stdout: str) -> tuple[LiteralSentencePair, ...]:
    source_sentences = split_sentences(source_text)
    # LLMs sometimes output empty lines between sentences even if asked not to.
    lines = [_clean_provider_line(line) for line in stdout.splitlines()]
    lines = [line for line in lines if line]
    
    if not source_sentences:
        return ()

    if not _contains_thai(stdout):
        return ()
    if len(lines) != len(source_sentences):
        target_sentences = split_sentences(stdout)
        if len(target_sentences) == len(source_sentences):
            lines = list(target_sentences)
        else:
            # Preserve usable Thai output instead of falling back to Chinese source.
            return (
                LiteralSentencePair(
                    source_sentence=source_text,
                    literal_sentence=stdout.strip(),
                ),
            )

    pairs: list[LiteralSentencePair] = []
    for source, target in zip(source_sentences, lines):
        # Handle cases where LLM might repeat the source sentence like "Source => Translation"
        if "=>" in target:
            cleaned = target.split("=>")[-1].strip()
        elif ":" in target and not any(target.startswith(p) for p in ("http", "https")):
            parts = target.split(":", 1)
            maybe_source = parts[0].strip()
            # If the part before colon is exactly the source or a number, it's a delimiter.
            if maybe_source == source or maybe_source.isdigit() or (maybe_source.startswith("[") and maybe_source.endswith("]")):
                cleaned = parts[1].strip()
            else:
                cleaned = target
        else:
            cleaned = target
        
        pairs.append(LiteralSentencePair(source_sentence=source, literal_sentence=cleaned))
    return tuple(pairs)


def _contains_thai(text: str) -> bool:
    return bool(re.search(r"[\u0e00-\u0e7f]", text))


def _clean_provider_line(line: str) -> str:
    cleaned = line.strip()
    if not cleaned or not _contains_thai(cleaned):
        return ""
    if re.search(r"[A-Za-z]", cleaned):
        return ""
    if cleaned.startswith(("-", "*", "#", "`")):
        return ""
    if set(cleaned) <= {"-", "—", "_", " "}:
        return ""
    return cleaned
