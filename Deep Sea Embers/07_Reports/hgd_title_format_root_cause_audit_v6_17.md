# HGD Title And Format Root-Cause Audit (V6.17 reopened)

Date: 2026-06-15
Scope: read-only audit after user questioned HGD English titles and formatting quality.

## Verdict

- Title issue: current MoonRead generated content no longer has English fallback titles for HGD `ch001-ch035`.
- Title root cause: HGD raw source titles are English. MoonRead must translate/normalize them through the HGD title map or use already translated output headings. If that layer is absent, stale, or bypassed, English titles appear.
- Format issue: current output passes the simple density guardrail, but that is not strong enough to prove it follows `good format.md`.
- Format root cause: the current formatter/output improves spacing enough to pass max-paragraph checks, but it can still merge sound effects, beats, and narration into a paragraph where `good format.md` expects stronger visual separation.

## Title Evidence

Representative source titles and current output headings:

| file id | raw source title | current output heading |
| --- | --- | --- |
| ch001 | `Chapter 1 - Prologue` | `# ตอนที่ 1 - บทนำ` |
| ch014 | `Chapter 14 - Orientation Day [4]` | `# ตอนที่ 14 - วันปฐมนิเทศ` |
| ch022 | `Chapter 22 - Developing Game [4]` | `# ตอนที่ 22 - พัฒนาเกม` |
| ch029 | `Chapter 31 - Quest Completed [2]` | `# ตอนที่ 31 - เควสต์สำเร็จ` |
| ch035 | `Chapter 37 - Velora Art Museum [2]` | `# ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวลอรา` |

Current MoonRead manifest:

- total chapters: 35
- available: 35
- English-like title count: 0

MoonRead importer evidence:

- `reader-web/scripts/generate-chapters.mjs` has `hgdThaiTitleMap`.
- `normalizeBookMarkdown()` applies `translateHgdTitle()` to HGD H1 headings before writing generated reader Markdown.
- This is the current prevention mechanism for English title fallback.

Important numbering note:

- `ch029-ch035` are local file IDs 29-35 but their source titles are source chapter numbers 31-37.
- Example: local `ch029` uses raw title `Chapter 31 - Quest Completed [2]`, so current output displays `ตอนที่ 31 - เควสต์สำเร็จ`.
- This is not an English-title fallback. It is a source-numbering gap that must be intentionally preserved or intentionally normalized.

## Title Cause

The direct cause is not Thai translation failure in the current generated files. The durable cause is that HGD source titles are English and reader publication depends on a normalization layer.

Practical conclusion:

- Keep the HGD title map/importer guard.
- Add tests/guardrails that fail if HGD generated titles contain obvious English fallback words such as `Chapter`, `Prologue`, `Jester`, `Orientation`, `Quest`, `Painting`, or `Velora Art Museum`.
- Decide separately whether reader display should preserve source numbers (`ตอนที่ 31`) or normalize to local reading sequence (`ตอนที่ 29`).

## Format Evidence

Representative current output metrics:

| chapter | paragraphs | max paragraph chars | paragraphs > 520 | bold panel lines | italic standalone | dialogue standalone |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ch001 | 52 | 490 | 0 | 14 | 19 | 0 |
| ch014 | 112 | 255 | 0 | 3 | 13 | 47 |
| ch022 | 63 | 420 | 0 | 3 | 9 | 20 |
| ch029 | 88 | 349 | 0 | 2 | 9 | 42 |
| ch035 | 37 | 500 | 0 | 1 | 1 | 4 |

Representative source metrics:

| chapter | source title | source lines | source paragraphs | source max paragraph chars | source system lines |
| --- | --- | ---: | ---: | ---: | ---: |
| ch001 | `Chapter 1 - Prologue` | 107 | 1 | 7095 | 9 |
| ch014 | `Chapter 14 - Orientation Day [4]` | 138 | 1 | 8204 | 2 |
| ch022 | `Chapter 22 - Developing Game [4]` | 102 | 1 | 6707 | 2 |
| ch029 | `Chapter 31 - Quest Completed [2]` | 113 | 1 | 6786 | 1 |
| ch035 | `Chapter 37 - Velora Art Museum [2]` | 119 | 1 | 7466 | 0 |

Interpretation:

- Raw source is not blank-line separated, but it is line-break rich.
- Current output adds blank lines and passes density limits.
- Passing density is only a coarse readability check. It does not prove semantic layout.

## `good format.md` Evidence

The reference file at `C:\Users\ASUS\Downloads\good format.md` is a layout reference. It has:

- 1,368 lines
- 684 blank-line-separated paragraphs
- max paragraph length about 311 characters
- many standalone dialogue lines
- many standalone italic lines for thoughts/sounds
- many escaped markdown panel patterns such as bold bracketed system messages
- divider lines for item/status panels

Technical note:

- The file contains many escaped markdown markers such as `\*` and `\[`.
- It should be used as a layout/rhythm reference, not copied literally with escape characters.

## Format Cause

The current HGD output is not "all wrong", but it is under-specified for the user's desired reading style.

Example problem pattern:

- HGD `ch001` current output starts with a standalone sound effect `*คลิก คลิก*`, which is good.
- The next paragraph then merges office narration, light description, another sound effect, footsteps, movement, and hunting beat into one paragraph.
- `good format.md` suggests a stronger rhythm: sound effects, system panels, inner thoughts, and horror beats should often stand alone when they are separate source beats.

This means the root cause is not only paragraph length. The formatter needs a semantic layout rule:

- separate standalone sound effects
- separate sudden horror beats
- separate system panels
- separate direct speech and radio/voice fragments
- keep continuous narration together only when it is truly one continuous beat

## Repair Recommendation

Do not run a broad blind repair yet.

Recommended next V6.17 step:

1. Create an HGD format audit/repair script that reports likely merged beats:
   - italic sound effect inside a long narrative paragraph
   - quoted speech embedded in long narration
   - multiple sentence beats plus sound effect in one paragraph
   - system/status panel not standing alone
2. Apply AI formatting only to a small sample first: `ch001`, `ch014`, `ch022`, `ch035`.
3. Use `good format.md` as the prompt style reference, but instruct the model not to copy escaped markdown.
4. Validate:
   - no wording loss
   - no provider/meta leakage
   - no source-language leakage
   - Markdown panels render as real `**[ ... ]**`, not escaped text
   - max paragraph density stays low
   - representative chapters look better in MoonRead
5. Only then apply to HGD `ch001-ch035`.

## Prevention Mechanisms

Low-effort, medium/high-impact prevention:

- Keep HGD English-title guardrail in `scripts/check_output_quality_guardrails.py`.
- Add/keep MoonRead title normalization for HGD in `generate-chapters.mjs`.
- Add an HGD format audit that checks semantic layout patterns, not only paragraph length.
- Keep AI formatting primary for HGD because local formatting cannot reliably identify dialogue, thoughts, sound effects, or system panels.
- Use deterministic validation after AI formatting to catch escaped markdown, provider leakage, source-language remnants, and over-dense paragraphs.

## Files Inspected

- `D:\Fogust\Workspace\Novel\Horror Game Developer\03_Raw\ch001\source.json`
- `D:\Fogust\Workspace\Novel\Horror Game Developer\03_Raw\ch014\source.json`
- `D:\Fogust\Workspace\Novel\Horror Game Developer\03_Raw\ch022\source.json`
- `D:\Fogust\Workspace\Novel\Horror Game Developer\03_Raw\ch029\source.json`
- `D:\Fogust\Workspace\Novel\Horror Game Developer\03_Raw\ch035\source.json`
- `D:\Fogust\Workspace\Novel\Horror Game Developer\05_Output\ch001\ch001.md`
- `D:\Fogust\Workspace\Novel\Horror Game Developer\05_Output\ch014\ch014.md`
- `D:\Fogust\Workspace\Novel\Horror Game Developer\05_Output\ch022\ch022.md`
- `D:\Fogust\Workspace\Novel\Horror Game Developer\05_Output\ch029\ch029.md`
- `D:\Fogust\Workspace\Novel\Horror Game Developer\05_Output\ch035\ch035.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web\content\generated\books\horror-game-developer\manifest.json`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web\content\generated\books\horror-game-developer\chapters\ch001.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web\content\generated\books\horror-game-developer\chapters\ch014.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web\content\generated\books\horror-game-developer\chapters\ch022.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web\content\generated\books\horror-game-developer\chapters\ch029.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web\content\generated\books\horror-game-developer\chapters\ch035.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web\scripts\generate-chapters.mjs`
- `C:\Users\ASUS\Downloads\good format.md`

## No State-Changing Runtime Actions

- No provider calls.
- No pipeline run/resume/rerun.
- No MoonRead regeneration.
- No translation artifacts modified.
- This report is evidence for the next repair step, not the repair itself.
