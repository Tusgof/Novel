# V6.17.1 HGD Title And Format Re-Audit

Generated at: 2026-06-16

## Scope

- Novel: Horror Game Developer
- Published MoonRead range: `ch001-ch035`
- Trigger: user reported HGD titles still looked English and HGD formatting did not match the source rhythm / `C:\Users\ASUS\Downloads\good format.md`.

## Title Findings

- `05_Output/ch001-ch035` H1 titles are Thai.
- `04_Work/ch001-ch035/title.json` sidecars exist and match the final Markdown H1 titles.
- MoonRead generated chapter titles for HGD are Thai.
- Root cause of visible English title text: MoonRead book metadata used `novel.title: "Horror Game Developer"` and the home/smoke checks were also tied to that English display title.

## Title Fix Applied

- `reader-web/scripts/generate-chapters.mjs` now emits the HGD book title as `นักพัฒนาเกมสยองขวัญ`.
- `reader-web/app/page.js` now displays the generated HGD book title instead of a hard-coded English label.
- `reader-web/scripts/smoke-reader.mjs` now checks for `นักพัฒนาเกมสยองขวัญ`.
- `scripts/check_output_quality_guardrails.py` now fails if the generated HGD MoonRead manifest falls back to `Horror Game Developer` as the book title.

## Format Findings

The HGD output still has paragraph-density problems even after earlier repairs.

Measured against `Horror Game Developer/05_Output/ch001-ch035`:

- chapters checked: 35
- lines over 260 characters: 115
- lines over 320 characters: 56
- maximum line length: 513
- densest sampled chapters: `ch003`, `ch028`, `ch010`, `ch013`, `ch008`, `ch024`, `ch016`, `ch025`, `ch026`, `ch005`

Representative examples:

- `ch001`: 6 lines over 320 characters, max 392
- `ch022`: 2 lines over 320 characters, max 420
- `ch035`: 3 lines over 320 characters, max 398

## `good format.md` Finding

`C:\Users\ASUS\Downloads\good format.md` is not safe to use as a direct formatting authority yet.

- UTF-8 read produced 106 replacement characters.
- Thai text contains suspicious character substitutions such as `ยิน๸ี๹้อนรับ` and `๦้อ๨วาม`, which are not clean modern Thai output.
- Attempting the same Windows-874 repair heuristic used by MoonRead made the score worse, not better.

Conclusion: do not bulk-reformat HGD from this file until the reference is replaced or decoded cleanly.

## English Body And Sound Leakage Findings

The user also reported English text remaining in the first chapter and English sound effects in later chapters.

Confirmed leakage in published HGD output:

- `ch001`: `Jump Scare`, `Horror Developer System`, `Developer Seth Thorne`
- `ch007`: `Horror Developer System`
- `ch015`: `[Scenario]`, `[Section Chief]`
- `ch021`: `(Section Chief)`
- `ch022`: `*Click!*`, `*Takakakakaka—*`, `*Tak!*`, `*To Tok—*`
- `ch027`: `Jump Scare`, `[Seth's USB stick]`

Applied bounded repairs:

- `Jump Scare` -> `ฉากสะดุ้ง`
- `Horror Developer System` -> `ระบบนักพัฒนาเกมสยองขวัญ`
- `Developer Seth Thorne` -> `นักพัฒนาเซธ ธอร์น`
- `[Scenario]` -> `[ฉาก]`
- `[Section Chief]` / `(Section Chief)` -> `หัวหน้าแผนก`
- `*Click!*` -> `*คลิก!*`
- `*Takakakakaka—*` -> `*ตักตักตักตักตัก—*`
- `*Tak!*` -> `*ตั๊ก!*`
- `*To Tok—*` -> `*ก๊อก ก๊อก—*`
- `[Seth's USB stick]` -> `[แฟลชไดรฟ์ USB ของเซธ]`

Prevention added:

- `scripts/check_output_quality_guardrails.py` now rejects these known English leakage terms in both HGD `05_Output/ch001-ch035` and MoonRead generated HGD chapters.
- Proper nouns such as `U-Engine`, `Nightmare Forge Studios`, `Menxylanis`, and character names were intentionally left unchanged.

## Recommended Next Step

Do not claim HGD formatting complete yet.

Create a bounded V6.17.2 repair milestone:

1. Get or produce a clean formatting reference.
2. Select 3 representative HGD chapters: one early, one `ch022`, and one dense later chapter.
3. Run AI formatting only on those chapters with deterministic validation.
4. Compare source beats, paragraph spacing, dialogue, thoughts, system messages, sound effects, and MoonRead rendering.
5. If the pilot passes, expand to `ch001-ch035`.

## Stop Conditions For Repair

- source meaning changes
- source beat disappears
- Thai text corruption appears
- provider/meta text appears
- title sidecar and final H1 diverge
- MoonRead build/smoke fails
