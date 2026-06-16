# HGD V6.16.5 Title And Format Audit

Date: 2026-06-16

Scope: Horror Game Developer reader-facing `ch001-ch035`.

This is the pre-V6.17 evidence gate requested before more HGD repair work. It is audit-only except for this report and the warning-only semantic audit report generated beside it. No provider calls, pipeline runs, MoonRead regeneration, ledger edits, glossary edits, or output edits were performed.

## Questions Answered

1. Why did HGD chapter titles appear in English?
2. Is HGD formatting currently faithful to the source structure and `C:\Users\ASUS\Downloads\good format.md`?

## Files Inspected

- HGD source samples:
  - `D:\Fogust\Workspace\Novel\Horror Game Developer\03_Raw\ch001\source.json`
  - `D:\Fogust\Workspace\Novel\Horror Game Developer\03_Raw\ch014\source.json`
  - `D:\Fogust\Workspace\Novel\Horror Game Developer\03_Raw\ch022\source.json`
  - `D:\Fogust\Workspace\Novel\Horror Game Developer\03_Raw\ch035\source.json`
- HGD final output samples:
  - `D:\Fogust\Workspace\Novel\Horror Game Developer\05_Output\ch001\ch001.md`
  - `D:\Fogust\Workspace\Novel\Horror Game Developer\05_Output\ch014\ch014.md`
  - `D:\Fogust\Workspace\Novel\Horror Game Developer\05_Output\ch022\ch022.md`
  - `D:\Fogust\Workspace\Novel\Horror Game Developer\05_Output\ch035\ch035.md`
- MoonRead generated content:
  - `D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web\content\generated\books\horror-game-developer\manifest.json`
  - `D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web\content\generated\books\horror-game-developer\chapters\ch001.md`
  - `D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web\content\generated\books\horror-game-developer\chapters\ch035.md`
- MoonRead importer:
  - `D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web\scripts\generate-chapters.mjs`
- Format reference:
  - `C:\Users\ASUS\Downloads\good format.md`

## Title Evidence

Raw source titles are English:

- `ch001`: `Chapter 1 - Prologue`
- `ch014`: `Chapter 14 - Orientation Day [4]`
- `ch022`: `Chapter 22 - Developing Game [4]`
- `ch035`: `Chapter 37 - Velora Art Museum [2]`

Counts:

- raw source English-like titles: `35/35`
- final output English-like headings: `0/35`
- MoonRead generated English-like headings: `0/35`
- MoonRead manifest: `35` total, `35` available, `0` missing, `0` rejected

Current MoonRead sample titles:

- `ch001`: `ตอนที่ 1 - บทนำ`
- `ch014`: `ตอนที่ 14 - วันปฐมนิเทศ`
- `ch022`: `ตอนที่ 22 - พัฒนาเกม`
- `ch035`: `ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวลอรา`

Importer evidence:

- `reader-web/scripts/generate-chapters.mjs` defines `hgdThaiTitleMap`.
- `translateHgdTitle(title)` maps English HGD title families to Thai.
- `normalizeBookMarkdown(book, markdown)` rewrites the H1 for `horror-game-developer` before validation/import.

Finding: the title bug risk comes from raw HGD source metadata being English. Current output and MoonRead generated files are Thai because the importer/title map normalizes HGD headings. If that title map is removed, incomplete, bypassed, or stale generated content is served, HGD can fall back to English again.

## Format Evidence

`good format.md` establishes the target layout pattern:

- system/game panels are standalone bold bracketed blocks
- dialogue is usually separated into its own beat
- thoughts and sound effects are often italic standalone beats
- item/status panels use visual separation
- horror beats use frequent paragraph breaks

The HGD raw source is not a clean spacing target by itself. It often packs UI and prose tightly:

- `ch001` raw source has `107` lines, `4` lines over `250` characters, and compact UI/review sequences such as review panels and bracketed system messages attached to adjacent text.
- `ch014` raw source has `138` lines and includes a source-level quote mismatch in a thought line.
- `ch022` raw source has `102` lines and mostly clean prose/dialogue beats.
- `ch035` raw source has `119` lines and many short horror beats.

Current HGD output sample shape:

| chapter | paragraphs | paragraphs > 500 chars | max paragraph length | standalone system panels | italic-start beats | dialogue-start beats |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ch001 | 76 | 0 | 392 | 14 | 17 | 9 |
| ch014 | 110 | 0 | 255 | 3 | 10 | 0 |
| ch022 | 63 | 0 | 420 | 3 | 6 | 0 |
| ch035 | 51 | 0 | 398 | 1 | 9 | 15 |

Warning-only semantic audit:

```powershell
python scripts\audit_hgd_semantic_format.py --root "D:\Fogust\Workspace\Novel\Horror Game Developer\05_Output" --first 1 --last 35 --report "D:\Fogust\Workspace\Novel\Deep Sea Embers\07_Reports\hgd_v6_16_5_semantic_format_current.md"
```

Result:

- semantic-format findings: `0`
- report path: `D:\Fogust\Workspace\Novel\Deep Sea Embers\07_Reports\hgd_v6_16_5_semantic_format_current.md`

Residual note:

- a separate raw paragraph-length scan still found paragraphs above 500 characters in `ch003`, `ch010`, and `ch028`
- these are ordinary narration paragraphs, not current semantic warning findings
- they should be treated as optional reading-polish candidates, not proof that the HGD formatting repair failed

## Root Cause

Title root cause:

- HGD source titles are English by design because the source site is English.
- Current Thai titles depend on the HGD title normalization layer in MoonRead import plus translated H1 headings in final output.
- The previous English-title symptom was likely either stale generated content, bypassed normalization, or a missing/incomplete title-map path at that time.

Format root cause:

- The original source is compact and not always reader-friendly as-is.
- `good format.md` is a semantic layout reference, not a literal source-spacing copy target.
- The earlier broad layout repair was risky because direct AI formatting can change characters or wording.
- The current safest approach is validated projection/deterministic cleanup: use AI/layout ideas only when content preservation is proven.

## Decision

V6.16.5 is closed as an audit gate.

V6.17 should not do another broad HGD rewrite. Current HGD `ch001-ch035` is publishable by the existing semantic-format audit and MoonRead title checks. The next V6.17 work, if any, should be narrow:

1. keep the HGD title normalization map as a required guardrail
2. add or keep a title audit that fails on English HGD reader titles
3. optionally inspect `ch003`, `ch010`, and `ch028` for manual reading polish because they contain long narration paragraphs
4. do not use direct AI formatting as final output unless character preservation is enforced

## Verification

- read-only source/output/MoonRead inspection completed
- HGD semantic format audit completed with `0` findings
- no provider calls
- no pipeline run/resume/rerun-block
- no output edits
- no ledger edits
- no glossary edits
- no MoonRead regeneration
