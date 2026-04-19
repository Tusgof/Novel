---
name: novel-fetch-adapters
description: Guide adapter selection and fetch expectations for novel sources. Use when Codex needs to choose or reason about the correct site-specific fetch adapter, table-of-contents traversal, pagination behavior, or content cleanup rules.
---

# Novel Fetch Adapters

Use this skill to select and reason about fetch adapters.

## Expected Commands

```
novel-pipeline run --adapter <name> --chapter-id <id>
novel-pipeline fetch --adapter <name> --chapter-id <id>
novel-pipeline fetch --adapter <name>            # build and print manifest
novel-pipeline run --input-file <path> --chapter-id <id>  # local file
```

## Adapter Contract

- `build_manifest()` → list[ChapterMeta] from TOC page
- `extract_content(html, encoding)` → clean chapter text
- `fetch_chapter_text(meta)` → fetch URL + extract content (main entry point)

## Adding a New Adapter

1. Create file in `novel_pipeline/adapters/` implementing `FetchAdapter`
2. Register in `novel_pipeline/adapters/__init__.py` via `register_adapter(name, cls)`
3. Configure in `.system/config.yaml` under `source:` section

## Manifest

- Cached at `03_Raw/manifest.json`
- Rebuilt with `--force` flag or on first run
- Contains `ChapterMeta` entries: `chapter_id`, `title`, `url`, `source_id`

## Chunking Rules

- **Chinese:** 2,500 characters per block
- **Non-Chinese:** 5,000 words per block
- Never split mid-sentence; prefer paragraph/scene breaks
- Implemented in `split_blocks()` in `text_utils.py`

## ChapterSource Contract

Fields: `novel_id`, `chapter_id`, `title`, `source_language`, `raw_text`,
`source_path`, `source_url`, `metadata`.
Source types: local file (`--input-file`), pasted text (`--text`), website adapter (`--adapter`).

## Guardrails

- Adapter implementations go in `novel_pipeline/adapters/`, not in this skill.
- No new pip dependencies — use `urllib.request` from stdlib.
- Encoding (e.g. GBK) is adapter-specific; config `encoding:` field overrides if needed.
