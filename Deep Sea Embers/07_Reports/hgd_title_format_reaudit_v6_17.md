# HGD Title And Format Re-Audit (V6.17 follow-up)

Date: 2026-06-15
Scope: read-only audit of HGD ch001-ch035 output, MoonRead generated content, manifest, raw source titles, and good format sample.

## Verdict

- English title fallback: PASS for generated MoonRead/05_Output headings; no obvious English fallback titles found in ch001-ch035.
- Numbering mismatch: 7 chapters have source title numbers that differ from MoonRead sequence/file id.
- Dense paragraph/list-block risk: 1 chapter (`ch022`) still contained an over-dense numbered-list block during guardrail validation; repaired by splitting the list items into separate paragraphs without changing wording.
- Format quality: NEEDS REVIEW. Current output is cleaner than the earlier dense version, but deterministic splitting alone cannot prove it follows the source/good-format intent.

## Title Findings

- English fallback title findings: 0
  - none

### Source-title number mismatches

| file id | MoonRead sequence | title number | source title | manifest title |
| --- | ---: | ---: | --- | --- |
| ch029 | 29 | 31 | `Chapter 31 - Quest Completed [2]` | `ตอนที่ 31 - เควสต์สำเร็จ` |
| ch030 | 30 | 32 | `Chapter 32 - Painting [1]` | `ตอนที่ 32 - ภาพวาด` |
| ch031 | 31 | 33 | `Chapter 33 - Painting [2]` | `ตอนที่ 33 - ภาพวาด` |
| ch032 | 32 | 34 | `Chapter 34 - Painting [3]` | `ตอนที่ 34 - ภาพวาด` |
| ch033 | 33 | 35 | `Chapter 35 - Painting [4]` | `ตอนที่ 35 - ภาพวาด` |
| ch034 | 34 | 36 | `Chapter 36 - Velora Art Museum [1]` | `ตอนที่ 36 - พิพิธภัณฑ์ศิลปะเวลอรา` |
| ch035 | 35 | 37 | `Chapter 37 - Velora Art Museum [2]` | `ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวลอรา` |

## Format Findings

- good format sample paragraphs: 684
- HGD chapters with long paragraph/list-block risk before follow-up repair: 1 (`ch022`)
- HGD chapters with long paragraph/list-block risk after follow-up repair and guardrail rerun: 0

### Repaired during this follow-up

- `Horror Game Developer/05_Output/ch022/ch022.md`: split the "what makes a good horror game" numbered list into separate paragraphs for items 1-3.
- `Deep Sea Embers/reader-web/content/generated/books/horror-game-developer/chapters/ch022.md`: regenerated from the repaired output.
- No Thai wording was changed in the repaired list; only blank-line structure changed.

## Required Follow-up Before More HGD Publishing

1. Decide whether MoonRead should display source chapter numbers such as `ตอนที่ 31` or normalized reading sequence numbers such as `ตอนที่ 29` for HGD.
2. If normalized sequence is preferred, change the HGD title normalization/importer and regenerate MoonRead content.
3. For formatting, do not rely on local paragraph splitting as final proof. Use AI formatting for semantic decisions, then deterministic validation for leakage, paragraph density, and Markdown rendering.
4. Re-inspect representative chapters ch001, ch014, ch029, ch035 in MoonRead after any repair.

Note: the mismatch starts because local `ch029` points at Roliascan source URL `ch31-117015`. This is not an English-title fallback; it is a source numbering gap that should be made explicit in reader display or normalized intentionally.

## Files Inspected

- `Horror Game Developer/03_Raw/ch001-ch035/source.json`
- `Horror Game Developer/05_Output/ch001-ch035/chXXX.md`
- `Deep Sea Embers/reader-web/content/generated/books/horror-game-developer/manifest.json`
- `Deep Sea Embers/reader-web/content/generated/books/horror-game-developer/chapters/ch001-ch035.md`
- `C:/Users/ASUS/Downloads/good format.md`
