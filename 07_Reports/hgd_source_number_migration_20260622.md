# HGD Source Number Migration - 2026-06-22

## Summary

Horror Game Developer local chapter ids were migrated to match source chapter numbers.

Before this repair, local ids were ordinal positions from the RoliaScan manifest. When the manifest skipped chapters, local ids no longer matched source chapter numbers. This caused continuity failures such as local `ch172` pointing to source `Chapter 187` instead of source `Chapter 177`.

## Root Cause

- `RoliascanAdapter.build_manifest()` assigned `chapter_id` from manifest order (`ch001`, `ch002`, ...), not from source chapter number.
- RoliaScan skipped source chapters `29`, `30`, `54`, `55`, `91`, `172-180`, `182`, and `221` in the fetched manifest.
- Prior repair filled the `172-180/182` gap, but later a bounded run fetched through the stale manifest and overwrote local `ch172` with source `Chapter 187`.
- Existing completeness checks confirmed local file presence, but did not enforce source chapter sequence.

## Repair

- Migrated HGD raw/work/output folders so local ids now match source chapter numbers:
  - `ch001` -> source `Chapter 1`
  - ...
  - `ch236` -> source `Chapter 236`
- Inserted and translated the missing source chapters:
  - `ch029` - `Chapter 29 - Scream [3]`
  - `ch030` - `Chapter 30 - Quest Completed [1]`
  - `ch054` - `Chapter 54 - Your account has been reinstated [1]`
  - `ch055` - `Chapter 55 - Your account has been reinstated [2]`
  - `ch091` - `Chapter 91 - Guild Dinner [3]`
  - `ch221` - `Chapter 221 - Multiplayer [6]`
- Reassembled HGD final outputs so H1 headings match source chapter numbers.
- Updated MoonRead registry HGD range from `ch001-ch230` to `ch001-ch236`.
- Regenerated MoonRead generated content.

## Prevention

- Added `Deep Sea Embers/scripts/check_source_chapter_sequence.py`.
- Required check after HGD fetch/repair/publish work:

```powershell
python "Deep Sea Embers\scripts\check_source_chapter_sequence.py" --novel-dir "Horror Game Developers" --chapters ch001-ch236
```

This catches skipped, duplicated, or overwritten source chapters before publication.

## Validation

- Source sequence: passed for HGD `ch001-ch236`.
- HGD output presence: `ch001-ch236` exist.
- HGD H1 numbering: every chapter H1 matches its source-number id.
- MoonRead generation: `2 books, 386 available, 0 missing, 0 rejected`.
- MoonRead build: passed.
- MoonRead smoke: passed on retry; first attempt timed out waiting for the local server.

## Notes

- The migration created a local backup under `Horror Game Developers/99_Backups/`.
- `03_Raw`, `04_Work`, and `05_Output` remain ignored runtime/product artifact directories by repository policy. The committed product surface is MoonRead generated content plus this report and the new source-sequence guardrail.
