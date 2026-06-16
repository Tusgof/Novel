---
name: novel-pipeline-orchestrator
description: Orchestrate the local novel translation pipeline through high-level user commands. Use when Codex needs to map a user request such as running a batch, resuming a run, or stepping through the pipeline into the correct Python command flow, config resolution, and human touchpoints.
---

# Novel Pipeline Orchestrator

Use this skill to control the runtime pipeline, not to implement runtime logic in the skill itself.

## Expected Commands

```
novel-pipeline run --chapter-id <id> [--input-file <path> | --text <str>] [--title <str>] [--style-profile <key>] [--run-id <id>] [--force]
novel-pipeline run --range <range>  # batch mode: "ch001-ch010" or "ch001,ch003"
novel-pipeline resume [--run-id <id>] [--force]
novel-pipeline status [--run-id <id>]
```

Global flags: `--config <path>` (default `.system/config.yaml`), `--novel <id>`

## Stage Flow

- **Chapter-level:** fetched, glossary_scanned, glossary_approved
- **Block-level:** translating, refining, qa, formatting, completed

## Key Types

`AppConfig`, `PipelineContext`, `ChapterSource`, `TextBlock`, `GlossaryEntry`,
`LiteralDraft`, `RefinedDraft`, `QAReport`, `RunRecord`

## Human Gates

- **Glossary approval** — interactive terminal input for each pending term
- **QA hard-fail escalation** — force-accept / skip / inspect-and-retry
- **Batch chapter failure** — continue to next chapter / stop entire batch

## Runtime Artifacts

- `03_Raw/<chapter_id>/source.json` — fetched source
- `01_Glossary/<original_term>.md` — glossary entries (proposed → approved)
- `04_Work/<chapter_id>/<block_id>/<stage>.json` — block artifacts (literal, refined, formatted, qa)
- `05_Output/<chapter_id>/<chapter_id>.md` — final chapter markdown
- `06_Logs/run_ledger.jsonl` — append-only run ledger

## Guardrails

- Do not embed prompt bodies here; use files under `prompts/`.
- Do not implement retry, state persistence, or provider subprocess logic here.
- Treat `PROJECT_BRAIN.md` as the source of truth.
