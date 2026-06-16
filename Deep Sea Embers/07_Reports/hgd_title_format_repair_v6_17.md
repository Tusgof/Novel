# V6.17 HGD Title And Format Repair Report

Date: 2026-06-15

## Scope

Repaired Horror Game Developer reader-facing quality for the already published MoonRead range:

- target: `ch001-ch035`
- source output root: `D:\Fogust\Workspace\Novel\Horror Game Developer\05_Output`
- reader output root: `reader-web/content/generated/books/horror-game-developer`
- no provider calls
- no pipeline resume/run/rerun-block
- no ledger/source/raw mutation

## Root Cause

1. HGD MoonRead chapter titles were English because the reader importer used the Markdown H1 directly from HGD final outputs.
2. HGD final outputs had dense paragraphs because previous formatting/reflow did not reliably separate game UI panels, dialogue, thoughts, sound effects, and horror beats.
3. `good format.md` shows the target shape: standalone bold bracketed system panels, standalone italic thoughts/sounds where appropriate, divider-separated item/status panels, and frequent blank lines around UI/horror beats.

## Changes

- Added HGD title mapping in `scripts/repair_user_reported_quality_issues.py`.
- Added deterministic HGD format repair in `scripts/repair_user_reported_quality_issues.py`.
- Limited HGD repair scope to `ch001-ch035`.
- Added HGD title normalization in `reader-web/scripts/generate-chapters.mjs` so English chapter-title fallbacks do not return on regeneration.
- Repaired HGD `05_Output/ch001` through `05_Output/ch035`.
- Regenerated MoonRead content.
- Restored accidental `ch036` formatting touch from existing formatted artifact and limited the script to prevent recurrence.

## Title Results

Before:

- HGD manifest contained English titles such as `Chapter 1 - Prologue`.

After:

- English fallback titles in HGD `ch001-ch035`: `0`
- first title: `ตอนที่ 1 - บทนำ`
- last published HGD title: `ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวลอรา`

## Format Results

After deterministic repair:

- dense paragraphs over the guardrail threshold: `0`
- standalone system panels detected: `159`
- output quality guardrail: passed

Representative repaired pattern:

```markdown
# ตอนที่ 1 - บทนำ

*คลิก คลิก*

...

**[คุณต้องการออกจากเกมหรือไม่?]**

**[▶ ใช่]**

**[▷ ไม่]**
```

## Validation

Passed:

- `python scripts/check_output_quality_guardrails.py`
- `npm.cmd run generate:chapters`
- `npm.cmd run lint`
- `npm.cmd run build`
- `npm.cmd run smoke`
- `python -m compileall novel_pipeline`
- `python test_translation.py`

MoonRead generation result:

- books: `2`
- available chapters: `85`
- missing chapters: `0`
- rejected chapters: `0`
- HGD available: `35`
- HGD English titles: `0`

Smoke result:

- `ok: true`
- console errors: none
- HGD reader opens
- mobile overflow: false

## Prevention

- HGD output repair is now bounded to published chapters `ch001-ch035`.
- MoonRead importer translates known HGD English title patterns during generation.
- The output guardrail remains required before reader publishing.
- Future HGD publishing should fail review if English chapter titles or dense paragraphs return.
