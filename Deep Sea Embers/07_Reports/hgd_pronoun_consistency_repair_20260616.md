# HGD Pronoun Consistency Repair

Created at: 2026-06-16

## Scope

- Novel: Horror Game Developer
- Published MoonRead scope: `ch001-ch035`
- Project folder after migration: `D:\Fogust\Workspace\Novel\Horror Game Developers`
- Backup folders created before repair:
  - `D:\Fogust\Workspace\Novel\Horror Game Developers\05_Output_backup_before_pronoun_repair_20260616_145913`
  - `D:\Fogust\Workspace\Novel\Horror Game Developers\05_Output_backup_before_pronoun_repair_20260616_150339`
  - `D:\Fogust\Workspace\Novel\Horror Game Developers\05_Output_backup_before_pronoun_repair_20260616_150518`

## Root Cause

- HGD did not have a durable Obsidian-side pronoun policy before this repair.
- The HGD horror style profile and prompts preserved horror tone, system UI, and glossary, but did not pin Seth Thorne's Thai first-person voice.
- QA checked meaning and tone, but did not explicitly reject Seth `ผม`/`ฉัน` drift or Kyle/Seth address drift.
- MoonRead imported final Markdown faithfully, so inconsistent pronouns in HGD output became reader-facing.

## Prevention Added

- Migrated HGD project data into the user-created Obsidian vault folder: `D:\Fogust\Workspace\Novel\Horror Game Developers`.
- Added durable policy note: `Horror Game Developers/02_Database_Views/HGD Pronoun Policy.md`.
- Added pronoun rules to HGD `RESEARCH_PROFILE.yaml`, `.system/style_profiles.yaml`, `prompts/refinement.md`, and `prompts/qa_judge.md`.
- Updated active HGD path references in MoonRead import and repair/audit scripts from `Horror Game Developer` to `Horror Game Developers`.
- Added deterministic guardrail coverage in `scripts/check_output_quality_guardrails.py` for known high-risk Seth-dominant published chapters.
- Added `test_hgd_pronoun_policy_guardrail_flags_seth_drift` to `test_translation.py`.

## Repair Rules

- Seth Thorne narration, internal monologue, and self-reference should use `ผม/ของผม/ตัวผม`.
- Do not bulk-replace every `ฉัน` across all HGD output; female speakers and child voices can legitimately use other forms.
- Kyle/Seth casual peer dialogue should usually use `นาย`; `คุณ` remains valid for system, strangers, or formal contexts.

## Repaired Chapters

High-risk Seth-dominant chapters repaired from `ฉัน` to `ผม`:

- `ch002`
- `ch004`
- `ch010`
- `ch026`
- `ch027`
- `ch028`
- `ch031`
- `ch033`
- `ch035`

Targeted mixed-chapter repairs:

- `ch007`: fixed Seth self-reference in the medicine/survival/system acceptance scene.
- `ch017`: fixed Seth self-reference in two local phrases.
- `ch033`: fixed Kyle/Seth peer address including `เธอเห็นอะไร`, `เธอไม่ผิดหรอก`, and `ผมว่าเธอพูดถูก`.

## Pronoun Count Result

Published range `ch001-ch035` after repair:

- `ผม`: 1882
- `ฉัน`: 167
- `คุณ`: 141
- `นาย`: 175
- `เธอ`: 162

The remaining `ฉัน/เธอ` occurrences are not removed mechanically because several chapters contain female speakers, child voices, or third-person references.

## MoonRead Publication

MoonRead was regenerated after repair. HGD generated reader content now imports from:

```text
../../Horror Game Developers/05_Output
```

Updated generated chapters include:

- `ch002`, `ch004`, `ch007`, `ch010`, `ch017`, `ch026`, `ch027`, `ch028`, `ch031`, `ch033`, `ch035`

## Validation

- `python -m compileall novel_pipeline test_translation.py`: passed
- `$env:PYTHONIOENCODING='utf-8'; python test_translation.py`: passed
- `python scripts\check_output_quality_guardrails.py`: passed
- `npm.cmd run generate:chapters`: passed
- `npm.cmd run lint`: passed
- `npm.cmd run build`: passed
- `npm.cmd run smoke`: passed on rerun; one earlier smoke attempt timed out waiting for local server startup, then passed without code changes
- `git diff --check`: passed
