# V6.13 Working Tree Decision - 2026-06-16

Scope: classify current untracked files so `git status` is usable without deleting evidence.

## Pre-Change Untracked Summary

| group | count | decision |
| --- | ---: | --- |
| `01_Glossary/*.md` | 46 | keep visible; needs glossary review/commit/archive decision |
| `05_Output_backup_before_ch001_ch050_v2_20260609/**` | 28 | ignore as generated local backup; do not delete without user approval |
| `07_Reports/*.md` older experiment reports | 19 | keep visible; needs evidence commit/archive decision |
| `*.base` scratch files | 2 | ignore as local scratch |

## Changes Made

- Added `.gitignore` rule: `05_Output_backup_before_*/`
- Added `.gitignore` rule: `*.base`

## Rationale

- Backup output directories are generated safety copies and should not pollute normal git status.
- `.base` files are local scratch files, not project source.
- Glossary notes are potential source-of-truth content and must not be hidden or deleted automatically.
- Reports can be audit evidence. Old untracked reports remain visible until Codex/user decides whether to commit, archive, or delete them.

## Remaining Visible Decisions

1. Review the 46 untracked glossary notes and decide whether they are approved terms, stale generated notes, or archive candidates.
2. Review the 19 untracked report files and decide whether they are useful evidence worth committing or stale experiment outputs to archive/delete.

## Safety

- No files were deleted.
- No production artifacts, ledger records, provider config, source files, or outputs were modified.
- This is a working-tree hygiene step only.
