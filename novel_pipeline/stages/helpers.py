from __future__ import annotations

from novel_pipeline.types import GlossaryEntry, LiteralDraft


def format_glossary_subset(entries: list[GlossaryEntry]) -> str:
    if not entries:
        return "none"
    pairs = []
    for entry in sorted(entries, key=lambda e: e.original_term):
        category = f" ({entry.category})" if entry.category else ""
        pairs.append(f"{entry.original_term}={entry.thai_term}{category}")
    return "; ".join(pairs)


def format_literal_draft(draft: LiteralDraft) -> str:
    if not draft.sentence_pairs:
        return draft.source_text
    lines = []
    for i, pair in enumerate(draft.sentence_pairs, start=1):
        lines.append(f"[{i}] SOURCE: {pair.source_sentence}")
        lines.append(f"[{i}] LITERAL: {pair.literal_sentence}")
        lines.append("")
    return "\n".join(lines).strip()
