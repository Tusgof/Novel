from __future__ import annotations

import re
from pathlib import Path

import yaml

from novel_pipeline.files import atomic_write_text
from novel_pipeline.types import GlossaryEntry, TermSuggestion

FRONTMATTER_FIELDS = {
    "type": "glossary-term",
    "status": "proposed",
    "aliases": [],
    "related": [],
    "source_language": "",
    "description": "",
    "notes": "",
}


def slugify_term(term: str) -> str:
    sanitized = re.sub(r'[\\/:*?"<>|]', "_", term.strip())
    return sanitized or "untitled-term"


def load_glossary_index(glossary_dir: Path) -> dict[str, GlossaryEntry]:
    glossary_dir.mkdir(parents=True, exist_ok=True)
    index: dict[str, GlossaryEntry] = {}
    for path in sorted(glossary_dir.glob("*.md")):
        entry = parse_glossary_note(path)
        if entry is None:
            continue
        index[entry.original_term] = entry
        for alias in entry.aliases:
            index[alias] = entry
    return index


def parse_glossary_note(path: Path) -> GlossaryEntry | None:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        return None
    _, frontmatter_text, body = raw.split("---", 2)
    frontmatter = yaml.safe_load(frontmatter_text) or {}
    original_term = str(frontmatter.get("original_term", "")).strip()
    if not original_term:
        return None
    return GlossaryEntry(
        original_term=original_term,
        thai_term=str(frontmatter.get("thai_term", "")).strip(),
        category=str(frontmatter.get("category", "")).strip() or "term",
        status=str(frontmatter.get("status", "proposed")).strip(),
        aliases=tuple(str(item) for item in frontmatter.get("aliases", []) or []),
        rejected_variants=tuple(str(item) for item in frontmatter.get("rejected_variants", []) or []),
        description=str(frontmatter.get("description", "")).strip(),
        related=tuple(str(item) for item in frontmatter.get("related", []) or []),
        source_language=str(frontmatter.get("source_language", "")).strip(),
        notes=body.strip(),
        metadata={"path": str(path.resolve())},
    )


def write_glossary_note(
    *,
    template_text: str,
    glossary_dir: Path,
    entry: GlossaryEntry,
    first_seen_chapter: str,
    first_seen_block: str,
) -> Path:
    body = template_text
    replacements = {
        "type: glossary-term": "type: glossary-term",
        "original_term:": f"original_term: {entry.original_term}",
        "thai_term:": f"thai_term: {entry.thai_term}",
        "status: proposed": f"status: {entry.status}",
        "aliases: []": f"aliases: {list(entry.aliases)}",
        "rejected_variants: []": f"rejected_variants: {list(entry.rejected_variants)}",
        "source_language:": f"source_language: {entry.source_language}",
        "category:": f"category: {entry.category}",
        "description:": f"description: {entry.description}",
        "related: []": f"related: {list(entry.related)}",
        "first_seen_chapter:": f"first_seen_chapter: {first_seen_chapter}",
        "first_seen_block:": f"first_seen_block: {first_seen_block}",
        "approval_notes:": f"approval_notes: {entry.description}",
    }
    for original, replacement in replacements.items():
        body = body.replace(original, replacement, 1)
    path = glossary_dir / f"{slugify_term(entry.original_term)}.md"
    atomic_write_text(path, body)
    return path


def choose_option_interactively(suggestion: TermSuggestion) -> str:
    print()
    print(f"New term: {suggestion.original_term}")
    print(f"Category: {suggestion.category}")
    if suggestion.context:
        print(f"Context: {suggestion.context[0]}")
    if suggestion.rationale:
        print(f"Summary: {suggestion.rationale}")
    
    for index, option in enumerate(suggestion.options, start=1):
        rationale = suggestion.rationales[index - 1] if index - 1 < len(suggestion.rationales) else ""
        print(f"{index}. {option}")
        if rationale:
            print(f"   Note: {rationale}")
    
    while True:
        choice = input("Choose translation [1-3]: ").strip()
        if choice in {"1", "2", "3"}:
            return suggestion.options[int(choice) - 1]
        print("Invalid choice. Please enter 1, 2, or 3.")
