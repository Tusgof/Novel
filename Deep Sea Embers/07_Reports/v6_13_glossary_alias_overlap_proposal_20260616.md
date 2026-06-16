# V6.13 Glossary Alias Overlap Proposal - 2026-06-16

Purpose: resolve the one known glossary overlap before deciding whether to commit the visible untracked glossary queue.

No provider calls were made. No glossary notes, ledger records, source files, output files, MoonRead files, provider config, or runtime artifacts were modified.

## Scope

Reviewed terms:

| term | status | thai_term | file state | note |
| --- | --- | --- | --- | --- |
| `实太阳神` | approved | `สุริยเทพที่แท้จริง` | tracked | canonical approved title from V3.9 |
| `真实的太阳神` | approved | `สุริยเทพที่แท้จริง` | untracked | described as a variant of `实太阳神` |

Files inspected:

- `01_Glossary/实太阳神.md`
- `01_Glossary/真实的太阳神.md`
- `07_Reports/v6_13_glossary_queue_review_20260616.md`
- glossary parsing/indexing code in `novel_pipeline/glossary_support.py`
- glossary queue handling in `novel_pipeline/stages/glossary.py`

## Finding

`真实的太阳神` and `实太阳神` intentionally share the same Thai rendering, `สุริยเทพที่แท้จริง`.

The untracked `真实的太阳神.md` already says:

- `approval_notes: Approved during deep-sea-embers-retranslate-ch021-ch023-v1; variant of 实太阳神.`

This is not a translation conflict. It is an ownership/modeling question: should the variant be represented as a separate glossary note or as an alias of the canonical term?

## Schema Support

The glossary schema supports aliases:

- `GlossaryEntry.aliases` exists.
- `parse_glossary_note()` reads `aliases`.
- `load_glossary_index()` indexes both `original_term` and each alias to the same entry.
- glossary scan filtering checks aliases when excluding existing terms.

Therefore, the system can represent `真实的太阳神` as an alias of `实太阳神` without needing a second approved note.

## Recommendation

Recommended decision:

1. Keep `实太阳神` as the canonical glossary note.
2. Add `真实的太阳神` to `实太阳神.md` as an alias in a dedicated glossary cleanup commit.
3. Do not commit `01_Glossary/真实的太阳神.md` as a separate note unless there is later evidence that the two source terms require different Thai handling.
4. After alias migration is explicitly approved, remove the untracked `01_Glossary/真实的太阳神.md` from the visible queue in the same dedicated glossary cleanup commit.

Recommended canonical note shape:

```yaml
original_term: 实太阳神
thai_term: สุริยเทพที่แท้จริง
category: title
status: approved
aliases:
  - 真实的太阳神
```

## Why This Is Lower Risk

- It preserves the user-approved Thai rendering.
- It avoids duplicate glossary notes with the same Thai term.
- It lets the scanner suppress future `真实的太阳神` candidates through the existing alias index.
- It keeps prompts shorter and avoids two glossary rows for one title concept.
- It does not require runtime changes.

## Stop Rule

This report is a proposal only. Do not modify, delete, stage, or commit the untracked glossary queue until the user/Codex explicitly approves a dedicated glossary cleanup step.
