# HGD Title And Format Checkpoint

Date: 2026-06-16

Scope: Horror Game Developer `ch001-ch035` reader-facing publication state.

This is a read-only checkpoint created before any further V6.17 repair work. No provider calls, pipeline runs, output edits, glossary edits, or MoonRead regeneration were performed for this checkpoint.

## Questions

1. Why did HGD chapter titles appear in English?
2. Is HGD formatting currently faithful to the source and to `C:\Users\ASUS\Downloads\good format.md`?

## Title Evidence

- Source path checked: `D:\Fogust\Workspace\Novel\Horror Game Developer\03_Raw\ch001\source.json`
- Source `ch001` title: `Chapter 1 - Prologue`
- Source titles for `ch001-ch035`: 35/35 are English-like source titles.
- Output headings for `ch001-ch035`: 35/35 start with Thai `# ตอนที่`.
- MoonRead manifest path: `D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web\content\generated\books\horror-game-developer\manifest.json`
- MoonRead manifest summary: 35 total, 35 available, 0 missing, 0 rejected.
- MoonRead manifest English-like title count: 0.

Finding: the English-title risk comes from raw source metadata. Current output and MoonRead generated content no longer show obvious English fallback titles, but the title normalization/import layer must remain active because the source titles are still English.

## Format Evidence

Reference file checked: `C:\Users\ASUS\Downloads\good format.md`

Observed target style from the reference:

- system/game panels are standalone bold bracketed blocks
- dialogue usually gets its own beat
- thoughts and sound effects are often italic standalone beats
- dividers separate item/status panels
- spacing is frequent and reader-oriented, especially around horror beats

Current sample checks:

- `ch001` now separates early sound effects, system panels, choices, and some thoughts, but review text still contains awkward markdown artifacts such as `* *` and some dense review/narration flow.
- `ch022` is much cleaner after the earlier projection repair and has good standalone numbered points.
- `ch035` still has at least one long paragraph where dialogue remains embedded in narration.

Audit command run:

```powershell
python scripts\audit_hgd_semantic_format.py --root "D:\Fogust\Workspace\Novel\Horror Game Developer\05_Output" --first 1 --last 35 --report "D:\Fogust\Workspace\Novel\Deep Sea Embers\07_Reports\hgd_semantic_format_audit_20260616_checkpoint.md"
```

Audit result:

- total semantic-format warnings: 9
- `dialogue_or_quote_embedded_in_long_paragraph`: 3
- `inline_italic_in_long_paragraph`: 1
- `many_beats_in_one_paragraph`: 5
- affected chapters: `ch003`, `ch005`, `ch025`, `ch031`, `ch035`

Finding: the prior projection repair improved HGD formatting substantially, but it is not perfect. The remaining issues are targeted layout warnings, not a full-book failure. The next repair should target the 9 warning sites and any obvious markdown artifact such as `* *`, while preserving wording exactly.

## Root Cause

Title root cause:

- HGD raw source titles are English.
- If title normalization/import metadata is missing or stale generated content is used, MoonRead can fall back to those English titles.
- Current generated content is corrected, but the underlying risk remains.

Format root cause:

- Basic paragraph-density checks are too weak for HGD.
- HGD needs semantic layout checks because dialogue, thoughts, sound effects, review snippets, and system panels can be technically short enough while still rhythmically wrong.
- Direct AI formatting is unsafe as final output unless character/content preservation is enforced; previous samples showed wording drift.

## Next Safe Repair

1. Do not reformat all HGD blindly.
2. Repair only the 9 warning sites from `hgd_semantic_format_audit_20260616_checkpoint.md` plus obvious markdown artifacts such as isolated `* *`.
3. Preserve wording and punctuation unless the punctuation is strictly markdown wrapper cleanup.
4. Regenerate MoonRead after output repair.
5. Run:
   - `python scripts\check_output_quality_guardrails.py`
   - `npm.cmd run generate:chapters`
   - `npm.cmd run lint`
   - `npm.cmd run build`
   - `npm.cmd run smoke`

## Decision

V6.17 can continue as a targeted HGD format cleanup, not a full rewrite. V6.18 speed work should not be used to justify skipping this reader-quality cleanup.
