---
name: novel-glossary-review
description: Review and present new glossary terms for human approval during the novel translation workflow. Use when Codex needs to show context, category, rationale, and 3 translation options for a source term before the runtime continues.
---

# Novel Glossary Review

Use this skill when the pipeline discovers terms that are not yet approved.

## Expected Commands

Glossary scan and approval are integrated into the `run` and `resume` commands.
Use `novel-pipeline status --run-id <id>` to check pending terms.

## Data Flow

1. `scan_terms_for_blocks()` → candidate terms from chapter blocks
2. New terms get `GlossaryEntry(status="proposed")` → `write_glossary_note()` to disk
3. `build_term_suggestion()` → `TermSuggestion` with 3 options
4. `choose_option_interactively()` → user picks an option
5. Entry updated: `status="approved"`, `thai_term` set
6. `write_glossary_note()` again with approved entry (idempotent)

## Required Presentation

Reference `TermSuggestion` fields: `original_term`, `source_language`, `category`,
`context` (tuple), `rationale`, `options` (list of 3 Thai translations).

## Runtime Artifacts

- `00_Templates/Term-Template.md` — entry template
- `01_Glossary/*.md` — glossary notes (frontmatter + body)
- `06_Logs/run_ledger.jsonl` — run ledger

## Guardrails

- Approved terms are never re-asked in the same or subsequent runs.
- Keep output concise and decision-oriented.
- Do not write glossary files directly from this skill; runtime code does that.
